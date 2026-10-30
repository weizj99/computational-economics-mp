"""Isolated mixed-precision experiment on the existing current GPU mainline.

Only the share fixed-point predictor is FP32. Its output is normalized and
corrected in FP64 with the incumbent strict share gates. Prices, the root,
fixed costs, exits and the three moments remain the existing FP64 code.
Importing this module does not patch or run the model. Use a fresh worker
process and ``precision_backend`` for an explicitly scoped experiment.

The predictor changes numerical iterates and therefore is not a bitwise or
first-stopping-iteration replica. Full arrays and discrete economic outcomes
must be checked against the current FP64 solver before accepting timings.
"""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar

import torch

import qmp_torch as Q
import qmp_torch_current as C
from qmp_torch_share_fused import share_step_fused


PREDICTOR_STEPS = 16
PREDICTOR_TOL = 3e-6
_INCUMBENT_STEP = C._share_step
_INCUMBENT_SOLVER = C.solve_shares_current
_TRACKER = ContextVar('qmp_precision_experiment', default=None)


def _fp32_predict(z, act, th, et, ga, numerics, steps):
    """Run at most the predeclared FP32 budget; never relax final FP64 gates."""
    values = tuple(value.to(torch.float32) for value in (z, th, et, ga))
    zz, tt, ee, gg = values
    zp, expo, s, mu, iters, done, stopping = C._share_start(
        *Q.free_b(zz, act, tt, ee, gg))
    # A fixed outer budget avoids a device synchronization at every predictor
    # step. The incumbent per-market freeze still stops each completed column.
    for _ in range(steps):
        s, mu, iters, done, stopping = _INCUMBENT_STEP(
            *Q.free_b(s, mu, iters, done, stopping, act, zp, tt, ee, expo),
            numerics.share_damping, PREDICTOR_TOL)
    return s, mu, iters, done, stopping


def solve_shares_mixed(z, act, th, et, ga, numerics, check_every=4):
    """FP32 predictor followed by the original FP64 residual contract.

    Counts include the actual predictor updates for each nontrivial market.
    A fixed predictor budget is deducted from the available global loop cap;
    no market receives more than ``share_max_iter`` total updates.
    """
    if z.dtype != torch.float64 or z.device.type != 'cuda':
        raise ValueError('mixed shares require original CUDA float64 inputs')
    if not isinstance(check_every, int) or check_every < 1:
        raise ValueError('check_every must be a positive integer')
    budget = min(PREDICTOR_STEPS, max(0, numerics.share_max_iter - 1))
    zp, expo, initial, mu, iters, done, stopping = C._share_start(
        *Q.free_b(z, act, th, et, ga))
    if budget:
        predicted, _, predictor_iters, _, _ = _fp32_predict(
            z, act, th, et, ga, numerics, budget)
        candidate = predicted.to(torch.float64)
        total = candidate.sum(1, keepdim=True)
        usable = (torch.isfinite(candidate).all(1)
                  & torch.isfinite(total[:, 0, :]) & (total[:, 0, :] > 0))
        candidate = candidate / torch.where(total > 0, total, 1.0)
        # Empty/monopoly markets use the exact original FP64 initialization.
        # A bad predictor is only a failed warm start, never an economic zero.
        use = usable & ~done
        s = torch.where(use[:, None, :], candidate, initial)
        iters = torch.where(~done, predictor_iters, iters)
    else:
        s = initial
    refinement_loop_steps = 0
    for iteration in range(1, numerics.share_max_iter - budget + 1):
        if (iteration == 1 or iteration % check_every == 0) and bool(done.all()):
            break
        s, mu, iters, done, stopping = share_step_fused(
            s, mu, iters, done, stopping, act, zp, th, et, expo,
            numerics.share_damping, numerics.share_tol)
        refinement_loop_steps += 1
    returned = C._share_residual(*Q.free_b(s, act, zp, th, et, expo))
    valid = (done.all(1) & torch.isfinite(s).all((1, 2))
             & torch.isfinite(mu).all((1, 2))
             & (returned.amax(1) <= numerics.share_tol)
             & (stopping.amax(1) <= numerics.share_tol)
             & (iters.amax(1) <= numerics.share_max_iter))
    tracker = _TRACKER.get()
    if tracker is not None:
        tracker['share_calls'].append({
            'batch': int(z.shape[0]), 'firms': int(z.shape[1]),
            'markets': int(z.shape[2]), 'predictor_loop_steps': budget,
            'FP64_refinement_loop_steps': refinement_loop_steps,
        })
    return s, mu, iters, stopping.amax(1), returned.amax(1), valid


@contextmanager
def precision_backend(mode='mixed'):
    """Temporarily replace one existing solver global in an isolated worker.

    Modes: ``fused_fp64`` is the previously validated fused baseline;
    ``mixed`` is the FP32-predictor/FP64-correction experiment. The yielded
    dictionary contains only Python scalars and lists and is JSON serializable.
    """
    if mode not in ('fused_fp64', 'mixed'):
        raise ValueError('precision mode must be fused_fp64 or mixed')
    old_solver, old_step = C.solve_shares_current, C._share_step
    tracker = {
        'mode': mode, 'final_dtype': 'float64',
        'predictor_dtype': 'float32' if mode == 'mixed' else None,
        'predictor_tolerance': PREDICTOR_TOL if mode == 'mixed' else None,
        'predictor_max_steps': PREDICTOR_STEPS if mode == 'mixed' else 0,
        'strict_final_gates_unchanged': True,
        'prices_root_exit_moments_dtype': 'float64', 'share_calls': [],
        'same_first_stopping_iteration_claimed': False,
    }
    token = _TRACKER.set(tracker)
    C._share_step = share_step_fused
    C.solve_shares_current = solve_shares_mixed if mode == 'mixed' else _INCUMBENT_SOLVER
    try:
        yield tracker
    finally:
        C.solve_shares_current, C._share_step = old_solver, old_step
        _TRACKER.reset(token)


def solve_batch_precision(*args, precision_mode='mixed', **kwargs):
    """The original full batch solve with a scoped share implementation."""
    with precision_backend(precision_mode) as metadata:
        result = C.solve_batch_current(*args, **kwargs)
    result['precision_meta'] = metadata
    for diagnostic in result.get('diagnostics', []):
        diagnostic['precision_experiment'] = {
            key: value for key, value in metadata.items() if key != 'share_calls'}
    return result


def fp32_share_pilot(z, act, th, et, ga, numerics, *, steps=64):
    """Component diagnostic, *not* an all-FP32 full economic solve.

    The returned FP32 fixed point is independently evaluated using original
    FP64 productivity, parameters, powers and arithmetic. Passing an FP32
    self-residual cannot establish the original FP64 contract.
    """
    if z.dtype != torch.float64 or z.device.type != 'cuda':
        raise ValueError('pilot requires the unrounded CUDA float64 reference input')
    if not isinstance(steps, int) or steps < 1:
        raise ValueError('pilot steps must be a positive integer')
    # This pilot keeps iterating below predictor tolerance to expose the FP32
    # rounding floor, rather than declaring success at the coarse warm start.
    zz, tt, ee, gg = tuple(value.to(torch.float32) for value in (z, th, et, ga))
    zp, expo, s, mu, iters, done, stopping = C._share_start(*Q.free_b(zz, act, tt, ee, gg))
    for _ in range(steps):
        s, mu, iters, done, stopping = _INCUMBENT_STEP(
            *Q.free_b(s, mu, iters, done, stopping, act, zp, tt, ee, expo),
            numerics.share_damping, numerics.share_tol)
    self_residual = C._share_residual(*Q.free_b(s, act, zp, tt, ee, expo))
    zp64, expo64, *_ = C._share_start(*Q.free_b(z, act, th, et, ga))
    s64 = s.to(torch.float64)
    true_residual = C._share_residual(*Q.free_b(s64, act, zp64, th, et, expo64))
    count = act.sum(1)
    normalization = torch.where(count > 0, (s64.sum(1) - 1.0).abs(), s64.abs().sum(1))
    finite = torch.isfinite(s64).all((1, 2)) & torch.isfinite(true_residual).all(1)
    strict = (finite & (true_residual.amax(1) <= numerics.share_tol)
              & (normalization.amax(1) <= numerics.share_tol))
    return {'shares': s, 'FP32_self_residual': self_residual,
            'FP64_independent_residual': true_residual,
            'FP64_normalization_error': normalization,
            'strict_reference_gate_passed': strict, 'finite': finite,
            'iterations': iters, 'scope': 'shares_only_not_full_economy',
            'steps': steps}
