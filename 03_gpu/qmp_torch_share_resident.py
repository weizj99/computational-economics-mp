"""Experimental resident FP64 correction for the existing mixed share solver.

The FP32 predictor, FP64 initialization, final independent residual and full
economic pipeline are the incumbent implementations. Only the FP64 correction
loop moves into one Triton launch. Each market freezes at its own first strict
stop; a program may finish when all of its markets have frozen.

Importing this module changes no solver globals. Use ``resident_backend`` in
an isolated worker, and validate against the current mixed implementation
before accepting timings. The optional observer is for correctness runs only;
the normal path performs no observer copies, reductions or device-host reads.
"""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
import math

import torch
import triton
import triton.language as tl
from triton.language.extra.cuda import libdevice

import qmp_torch as Q
import qmp_torch_current as C
import qmp_torch_precision as P
from qmp_torch_share_fused import (
    DEFAULT_FP_FUSION,
    DEFAULT_MARKETS_PER_PROGRAM,
    DEFAULT_NUM_WARPS,
    _parameter_batch_stride,
)


MAX_PHASE_STEPS = 1000
_OBSERVER = ContextVar('qmp_resident_share_observer', default=None)


@triton.jit
def _resident_kernel(
    S, MU, ITERS, DONE, RESIDUAL, ACT, ZPOW, THETA, ETA, EXPO,
    S_OUT, MU_OUT, ITERS_OUT, DONE_OUT, RESIDUAL_OUT,
    B, M: tl.constexpr, J: tl.constexpr,
    S_B: tl.constexpr, S_M: tl.constexpr, S_J: tl.constexpr,
    MU_B: tl.constexpr, MU_M: tl.constexpr, MU_J: tl.constexpr,
    IT_B: tl.constexpr, IT_J: tl.constexpr,
    DN_B: tl.constexpr, DN_J: tl.constexpr,
    RS_B: tl.constexpr, RS_J: tl.constexpr,
    AC_B: tl.constexpr, AC_M: tl.constexpr, AC_J: tl.constexpr,
    ZP_B: tl.constexpr, ZP_M: tl.constexpr, ZP_J: tl.constexpr,
    TH_B: tl.constexpr, ET_B: tl.constexpr, EX_B: tl.constexpr,
    DAMPING: tl.constexpr, OLD_WEIGHT: tl.constexpr, TOL: tl.constexpr,
    PHASE_STEPS: tl.constexpr, XBLOCK: tl.constexpr, RBLOCK: tl.constexpr,
):
    # This is the incumbent fused [market, padded firms], axis=1 layout.
    flat_market = tl.program_id(0) * XBLOCK + tl.arange(0, XBLOCK)
    valid_market = flat_market < B * J
    batch = flat_market // J
    market = flat_market % J
    firm = tl.arange(0, RBLOCK)
    valid_cell = valid_market[:, None] & (firm[None, :] < M)

    s = tl.load(S + batch[:, None] * S_B + firm[None, :] * S_M
                + market[:, None] * S_J, valid_cell, other=0.0)
    previous_mu = tl.load(MU + batch[:, None] * MU_B + firm[None, :] * MU_M
                          + market[:, None] * MU_J, valid_cell, other=0.0)
    active = tl.load(ACT + batch[:, None] * AC_B + firm[None, :] * AC_M
                     + market[:, None] * AC_J, valid_cell, other=0).to(tl.int1)
    zpow = tl.load(ZPOW + batch[:, None] * ZP_B + firm[None, :] * ZP_M
                   + market[:, None] * ZP_J, valid_cell, other=0.0)
    theta = tl.load(THETA + batch * TH_B, valid_market, other=1.0)[:, None]
    eta = tl.load(ETA + batch * ET_B, valid_market, other=1.0)[:, None]
    exponent = tl.load(EXPO + batch * EX_B, valid_market, other=1.0)[:, None]
    old_iters = tl.load(ITERS + batch * IT_B + market * IT_J,
                        valid_market, other=0)
    old_done = tl.load(DONE + batch * DN_B + market * DN_J,
                       valid_market, other=1).to(tl.int1)
    old_residual = tl.load(RESIDUAL + batch * RS_B + market * RS_J,
                           valid_market, other=0.0)

    one = tl.full((1, 1), 1.0, tl.float64)
    zero = tl.full((1, 1), 0.0, tl.float64)
    damping = tl.full((1, 1), DAMPING, tl.float64)
    old_weight = tl.full((1, 1), OLD_WEIGHT, tl.float64)
    tolerance = tl.full((1,), TOL, tl.float64)
    one_market = tl.full((1,), 1.0, tl.float64)
    zero_market = tl.full((1,), 0.0, tl.float64)

    phase_step = 0
    # Only this tile's termination is combined. Each market's five-state
    # freeze below remains independent of all other markets in the tile.
    while (phase_step < PHASE_STEPS) & (
            tl.sum((valid_market & ~old_done).to(tl.int32), axis=0) > 0):
        # Keep the exact arithmetic of _share_step_kernel, including FP64 /
        # and libdevice pow/sqrt. There is no approximate-power substitute.
        elasticity_denominator = (s / theta) + ((one - s) / eta)
        elasticity = one / elasticity_denominator
        markup = tl.where(active, elasticity / (elasticity - one), zero)
        safe_base = tl.where(active, markup * zpow, one)
        weight = tl.where(active, libdevice.pow(safe_base, exponent), zero)

        total_weight = tl.sum(tl.where(valid_cell, weight, zero), axis=1)[:, None]
        proposed = weight / tl.where(total_weight > zero, total_weight, one)
        relaxed = damping * proposed + old_weight * s
        total_relaxed = tl.sum(tl.where(valid_cell, relaxed, zero), axis=1)[:, None]
        difference = proposed - s
        distance_squared = tl.sum(
            tl.where(valid_cell, difference * difference, zero), axis=1)
        previous_squared = tl.sum(tl.where(valid_cell, s * s, zero), axis=1)
        numerator = libdevice.sqrt(distance_squared)
        denominator = libdevice.sqrt(previous_squared)
        distance = numerator / tl.where(denominator > zero_market, denominator, one_market)

        working = ~old_done
        stopped_now = working & (distance < tolerance)
        normalized = relaxed / tl.where(total_relaxed > zero, total_relaxed, one)
        next_s = tl.where(working[:, None], normalized, s)
        # mu is from pre-damping s at the first stopping step; returned s is
        # the post-damping, normalized value from that same step.
        next_mu = tl.where(stopped_now[:, None], markup, previous_mu)
        next_iters = old_iters + working.to(tl.int64)
        next_done = old_done | stopped_now
        next_residual = tl.where(working, distance, old_residual)
        s, previous_mu = next_s, next_mu
        old_iters, old_done, old_residual = next_iters, next_done, next_residual
        phase_step += 1

    cell_out = batch[:, None] * (M * J) + firm[None, :] * J + market[:, None]
    tl.store(S_OUT + cell_out, s, valid_cell)
    tl.store(MU_OUT + cell_out, previous_mu, valid_cell)
    tl.store(ITERS_OUT + flat_market, old_iters, valid_market)
    tl.store(DONE_OUT + flat_market, old_done, valid_market)
    tl.store(RESIDUAL_OUT + flat_market, old_residual, valid_market)


def resident_updates(
    s, mu, iters, done, stopping, act, zpow, th, et, expo,
    damping, tol, max_phase_steps,
):
    """Return up to ``max_phase_steps`` strict FP64 updates in one launch.

    The input states are never modified. The phase budget is additional to
    the incoming per-market counters; it is not a target total iteration
    count. It must be an explicit Python integer in [0, 1000]. No launch
    option, autotuning or silent budget expansion is applied.
    """
    if type(max_phase_steps) is not int or not 0 <= max_phase_steps <= MAX_PHASE_STEPS:
        raise ValueError('max_phase_steps must be an integer from 0 through 1000')
    tensors = (s, mu, iters, done, stopping, act, zpow, th, et, expo)
    if any(not isinstance(value, torch.Tensor) for value in tensors):
        raise TypeError('resident share inputs must be torch tensors')
    if s.ndim != 3 or min(s.shape) < 1:
        raise ValueError('shares must have nonempty shape (B,M,J)')
    B, M, J = s.shape
    device = s.device
    if device.type != 'cuda' or any(value.device != device for value in tensors):
        raise ValueError('all resident share inputs must be on the same CUDA device')
    for name, value in (('s', s), ('mu', mu), ('zpow', zpow)):
        if tuple(value.shape) != (B, M, J) or value.dtype != torch.float64:
            raise ValueError(f'{name} must have shape (B,M,J) and dtype float64')
    if tuple(act.shape) != (B, M, J) or act.dtype != torch.bool:
        raise ValueError('act must have shape (B,M,J) and dtype bool')
    for name, value, dtype in (('iters', iters, torch.int64), ('done', done, torch.bool),
                               ('stopping', stopping, torch.float64)):
        if tuple(value.shape) != (B, J) or value.dtype != dtype:
            raise ValueError(f'{name} has an incompatible market shape or dtype')
    if any(value.dtype != torch.float64 for value in (th, et, expo)):
        raise ValueError('theta, eta and exponent must have dtype float64')
    parameter_strides = tuple(_parameter_batch_stride(value, name, B)
                              for value, name in ((th, 'theta'), (et, 'eta'), (expo, 'expo')))
    damping, tol = float(damping), float(tol)
    if not (math.isfinite(damping) and 0.0 < damping <= 1.0
            and math.isfinite(tol) and 0.0 < tol < 1.0):
        raise ValueError('invalid damping or share tolerance')
    if max_phase_steps == 0:
        return tuple(value.clone() for value in (s, mu, iters, done, stopping))

    next_s = torch.empty((B, M, J), dtype=torch.float64, device=device)
    next_mu = torch.empty((B, M, J), dtype=torch.float64, device=device)
    next_iters = torch.empty((B, J), dtype=torch.int64, device=device)
    next_done = torch.empty((B, J), dtype=torch.bool, device=device)
    next_stopping = torch.empty((B, J), dtype=torch.float64, device=device)
    with torch.cuda.device(device):
        _resident_kernel[(triton.cdiv(B * J, DEFAULT_MARKETS_PER_PROGRAM),)](
            s, mu, iters, done, stopping, act, zpow, th, et, expo,
            next_s, next_mu, next_iters, next_done, next_stopping,
            B, M, J, *s.stride(), *mu.stride(), *iters.stride(),
            *done.stride(), *stopping.stride(), *act.stride(), *zpow.stride(),
            *parameter_strides, damping, 1.0 - damping, tol, max_phase_steps,
            DEFAULT_MARKETS_PER_PROGRAM, triton.next_power_of_2(M),
            num_warps=DEFAULT_NUM_WARPS, num_stages=1,
            enable_fp_fusion=DEFAULT_FP_FUSION,
        )
    return next_s, next_mu, next_iters, next_done, next_stopping


def solve_shares_resident_mixed(z, act, th, et, ga, numerics, check_every=4):
    """The current mixed path with only its FP64 correction loop replaced.

    ``check_every`` remains accepted and validated for call compatibility.
    Resident termination uses device-local market states, so it does not
    perform the incumbent's periodic host all-done synchronization.
    """
    if z.dtype != torch.float64 or z.device.type != 'cuda':
        raise ValueError('mixed shares require original CUDA float64 inputs')
    if not isinstance(check_every, int) or check_every < 1:
        raise ValueError('check_every must be a positive integer')
    if type(numerics.share_max_iter) is not int or not 0 <= numerics.share_max_iter <= MAX_PHASE_STEPS:
        raise ValueError('resident mixed share_max_iter must be an integer from 0 through 1000')
    budget = min(P.PREDICTOR_STEPS, max(0, numerics.share_max_iter - 1))
    zp, expo, initial, mu, iters, done, stopping = C._share_start(
        *Q.free_b(z, act, th, et, ga))
    predictor_iters = None
    if budget:
        predicted, _, predictor_iters, _, _ = P._fp32_predict(
            z, act, th, et, ga, numerics, budget)
        candidate = predicted.to(torch.float64)
        total = candidate.sum(1, keepdim=True)
        usable = (torch.isfinite(candidate).all(1)
                  & torch.isfinite(total[:, 0, :]) & (total[:, 0, :] > 0))
        candidate = candidate / torch.where(total > 0, total, 1.0)
        # Exactly the incumbent warm-start fallback and iteration accounting.
        # Predictor done/mu/stopping are deliberately not inherited.
        use = usable & ~done
        s = torch.where(use[:, None, :], candidate, initial)
        iters = torch.where(~done, predictor_iters, iters)
    else:
        s = initial
    phase_budget = numerics.share_max_iter - budget
    observer = _OBSERVER.get()
    initial_state = (s, mu, iters, done, stopping) if observer is not None else None
    s, mu, iters, done, stopping = resident_updates(
        s, mu, iters, done, stopping, act, zp, th, et, expo,
        numerics.share_damping, numerics.share_tol, phase_budget)
    returned = C._share_residual(*Q.free_b(s, act, zp, th, et, expo))
    valid = (done.all(1) & torch.isfinite(s).all((1, 2))
             & torch.isfinite(mu).all((1, 2))
             & (returned.amax(1) <= numerics.share_tol)
             & (stopping.amax(1) <= numerics.share_tol)
             & (iters.amax(1) <= numerics.share_max_iter))
    if observer is not None:
        observer({
            'shape': tuple(z.shape), 'budget': budget, 'predictor_budget': budget,
            'max_phase_steps': phase_budget, 'predictor_iters': predictor_iters,
            'initial_state': initial_state,
            'final_state': (s, mu, iters, done, stopping),
        })
    return s, mu, iters, stopping.amax(1), returned.amax(1), valid


@contextmanager
def observe_shares(callback):
    """Enable an explicit correctness observer; it owns any copies or I/O.

    Each completed share call sends references to its initial/final five
    states and predictor counters. The callback must not mutate tensors.
    No hook runs and no observation work is done outside this context.
    """
    if not callable(callback):
        raise TypeError('share observer must be callable')
    token = _OBSERVER.set(callback)
    try:
        yield
    finally:
        _OBSERVER.reset(token)


@contextmanager
def resident_backend(*, observer=None):
    """Temporarily select resident mixed shares in an isolated worker.

    Only C.solve_shares_current is patched. The FP32 predictor still calls
    the original compiled single-step function captured in the incumbent
    precision module. This context never installs a multi-step kernel into
    C._share_step and never changes the production default on import.
    """
    if observer is not None and not callable(observer):
        raise TypeError('share observer must be callable or None')
    old_solver = C.solve_shares_current
    token = _OBSERVER.set(observer) if observer is not None else None
    C.solve_shares_current = solve_shares_resident_mixed
    metadata = {
        'mode': 'mixed_resident_fp64_correction', 'final_dtype': 'float64',
        'predictor_dtype': 'float32', 'predictor_max_steps': P.PREDICTOR_STEPS,
        'predictor_tolerance': P.PREDICTOR_TOL,
        'strict_final_gates_unchanged': True,
        'prices_root_exit_moments_dtype': 'float64',
        'markets_per_program': DEFAULT_MARKETS_PER_PROGRAM,
        'num_warps': DEFAULT_NUM_WARPS, 'enable_fp_fusion': DEFAULT_FP_FUSION,
        'iteration_count_source': 'returned per-market counters; no host-loop count',
        'first_stop_equivalence_requires_validation': True,
    }
    try:
        yield metadata
    finally:
        C.solve_shares_current = old_solver
        if token is not None:
            _OBSERVER.reset(token)
