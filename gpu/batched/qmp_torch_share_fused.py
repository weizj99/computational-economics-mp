"""Experimental one-iteration fusion of the current strict share step.

This is a local kernel replacement for qmp_torch_current._share_step. It does
not replace the model, share loop, stopping gates, grouped batch driver, input
draws, root or exit code. The incumbent compiled step remains the reference.

The expressions and four firm reductions follow the three kernels (K0, K1, K2)
that torch.compile generated for M = 13. One Triton program retains the weight
and markup while performing the four reductions, rather than passing complete
arrays between three kernels. General FP64 pow remains one evaluation in the
firm update; inactive lanes receive the same safe base one as in the incumbent.

There is deliberately no autotuning or timing/validation at import or launch.
A launch option is not evidence of accuracy: require the same first stopping
iteration and all existing full-equilibrium gates before accepting this
experimental backend.
"""
from __future__ import annotations

from functools import partial
import math

import torch
import triton
import triton.language as tl
from triton.language.extra.cuda import libdevice


DEFAULT_MARKETS_PER_PROGRAM = 16
DEFAULT_NUM_WARPS = 4
# Match the incumbent's saved Triton3.3.1 CUDA compile metadata. FP64 FMA
# contraction is not a lower-precision/fast-math mode. First-stop and complete
# equilibrium comparisons remain mandatory despite matching this option.
DEFAULT_FP_FUSION = True


@triton.jit
def _share_step_kernel(
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
    XBLOCK: tl.constexpr, RBLOCK: tl.constexpr,
):
    # Preserve the generated reduction's [market, padded firms], axis=1 form.
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

    # FP64 '/' is the incumbent generated operation. In the installed Triton
    # generation tl.div_rn is FP32-only, so it must not be called on these data.
    elasticity_denominator = (s / theta) + ((one - s) / eta)
    elasticity = one / elasticity_denominator
    markup = tl.where(active, elasticity / (elasticity - one), zero)
    safe_base = tl.where(active, markup * zpow, one)
    weight = tl.where(active, libdevice.pow(safe_base, exponent), zero)

    # Mask padded firms before every reduction, just as the generated K1 does.
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
    one_market = tl.full((1,), 1.0, tl.float64)
    zero_market = tl.full((1,), 0.0, tl.float64)
    distance = numerator / tl.where(denominator > zero_market, denominator, one_market)

    working = ~old_done
    stopped_now = working & (distance < tolerance)
    normalized = relaxed / tl.where(total_relaxed > zero, total_relaxed, one)
    next_s = tl.where(working[:, None], normalized, s)
    # Incumbent GPU captures mu only at the first strict stopping step. It is
    # the markup from pre-damping s, not a recomputation from returned next_s.
    next_mu = tl.where(stopped_now[:, None], markup, previous_mu)
    next_iters = old_iters + working.to(tl.int64)
    next_done = old_done | stopped_now
    next_residual = tl.where(working, distance, old_residual)

    cell_out = batch[:, None] * (M * J) + firm[None, :] * J + market[:, None]
    tl.store(S_OUT + cell_out, next_s, valid_cell)
    tl.store(MU_OUT + cell_out, next_mu, valid_cell)
    tl.store(ITERS_OUT + flat_market, next_iters, valid_market)
    tl.store(DONE_OUT + flat_market, next_done, valid_market)
    tl.store(RESIDUAL_OUT + flat_market, next_residual, valid_market)


def _parameter_batch_stride(value, name, batch):
    """Parameters must broadcast as one value per economy, as in current03."""
    if value.numel() == 1:
        return 0
    if value.ndim == 3 and tuple(value.shape) == (batch, 1, 1):
        return value.stride(0)
    raise ValueError(f'{name} must be scalar or have shape (B,1,1)')


def _launch(
    s, mu_out, iters, done, residual, act, zpow, th, et, expo, damping, tol,
    *, markets_per_program, num_warps, enable_fp_fusion,
):
    tensors = (s, mu_out, iters, done, residual, act, zpow, th, et, expo)
    if any(not isinstance(value, torch.Tensor) for value in tensors):
        raise TypeError('fused share inputs must be torch tensors')
    if s.ndim != 3 or min(s.shape) < 1:
        raise ValueError('shares must have nonempty shape (B,M,J)')
    B, M, J = s.shape
    device = s.device
    if device.type != 'cuda' or any(value.device != device for value in tensors):
        raise ValueError('all fused share inputs must be on the same CUDA device')
    for name, value in (('s', s), ('mu_out', mu_out), ('zpow', zpow)):
        if tuple(value.shape) != (B, M, J) or value.dtype != torch.float64:
            raise ValueError(f'{name} must have shape (B,M,J) and dtype float64')
    if tuple(act.shape) != (B, M, J) or act.dtype != torch.bool:
        raise ValueError('act must have shape (B,M,J) and dtype bool')
    for name, value, dtype in (('iters', iters, torch.int64), ('done', done, torch.bool),
                               ('residual', residual, torch.float64)):
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

    # Only outputs are allocated. No complete weight or market temporary leaves
    # the kernel, and no input/returned earlier iteration is mutated.
    next_s = torch.empty((B, M, J), dtype=torch.float64, device=device)
    next_mu = torch.empty((B, M, J), dtype=torch.float64, device=device)
    next_iters = torch.empty((B, J), dtype=torch.int64, device=device)
    next_done = torch.empty((B, J), dtype=torch.bool, device=device)
    next_residual = torch.empty((B, J), dtype=torch.float64, device=device)
    with torch.cuda.device(device):
        _share_step_kernel[(triton.cdiv(B * J, markets_per_program),)](
            s, mu_out, iters, done, residual, act, zpow, th, et, expo,
            next_s, next_mu, next_iters, next_done, next_residual,
            B, M, J, *s.stride(), *mu_out.stride(), *iters.stride(),
            *done.stride(), *residual.stride(), *act.stride(), *zpow.stride(),
            *parameter_strides, damping, 1.0 - damping, tol,
            markets_per_program, triton.next_power_of_2(M),
            num_warps=num_warps, num_stages=1,
            enable_fp_fusion=enable_fp_fusion,
        )
    return next_s, next_mu, next_iters, next_done, next_residual


def share_step_fused(s, mu_out, iters, done, residual, act, zpow, th, et, expo, damping, tol):
    """One fused current-contract share update; no convergence loop is added."""
    return _launch(
        s, mu_out, iters, done, residual, act, zpow, th, et, expo, damping, tol,
        markets_per_program=DEFAULT_MARKETS_PER_PROGRAM,
        num_warps=DEFAULT_NUM_WARPS, enable_fp_fusion=DEFAULT_FP_FUSION,
    )


def make_share_step_fused(*, markets_per_program=16, num_warps=4, enable_fp_fusion=True):
    """Explicit experiment configuration; never picks a setting by timing it.

    The caller must record these options and validate that the selected FMA
    contraction policy matches the incumbent first-stop/full-result contract.
    Both options remain FP64 and use no fast math or approximate pow.
    """
    if not isinstance(markets_per_program, int) or markets_per_program < 1 \
            or markets_per_program & (markets_per_program - 1):
        raise ValueError('markets_per_program must be a positive power of two')
    if not isinstance(num_warps, int) or num_warps not in (1, 2, 4, 8, 16, 32):
        raise ValueError('num_warps must be a supported power of two')
    if not isinstance(enable_fp_fusion, bool):
        raise ValueError('enable_fp_fusion must be explicit bool')
    return partial(_launch, markets_per_program=markets_per_program,
                   num_warps=num_warps, enable_fp_fusion=enable_fp_fusion)
