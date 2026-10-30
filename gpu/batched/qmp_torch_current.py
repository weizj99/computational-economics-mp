"""Current qmp contract connected to the existing compiled GPU batch engine.

This adapter reuses qmp_torch's compiled price, profit and exit kernels, its
dynamic-B convention and captured-economy compaction. Strict share diagnostics
and a bracketed log-output root replace the historical stopping contracts.
No complete economic array is moved to a CPU equilibrium solver.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict
import math
import numpy as np
import torch

import qmp_torch as Q
from qmp.draws import build_productivity
from qmp.equilibrium import ModelConfig, Numerics, _validate
from qmp.estimation import diagnostic_quality

MOMENT_NAMES = ('employment_reallocation_rate', 'markup_sales_weighted', 'sga_cost_share_sales_weighted')
ROOT_RTOL = 4.0 * np.finfo(np.float64).eps
TRACE_KEYS = ('iteration', 'active_firms', 'active_markets', 'loss_firms', 'proposed_drop',
              'root_relative_residual', 'root_iterations', 'labor_relative_residual',
              'max_share_stopping_residual', 'max_share_residual', 'max_share_iterations',
              'actual_production_labor', 'overhead_labor')
INTEGER_KEYS = {'iteration', 'active_firms', 'active_markets', 'loss_firms', 'proposed_drop',
                'root_iterations', 'max_share_iterations'}
ERROR_NAMES = {1: 'no active market', 2: 'share iteration or residual failed',
               3: 'invalid fixed labor phi', 4: 'invalid price system',
               5: 'upper-positive-output root failed', 6: 'independent labor check failed',
               7: 'entry iteration limit', 8: 'nonfinite final quantities'}


@torch.compile(fullgraph=True)
def _share_start(z, act, th, et, ga):
    zpow = Q.spow(z, -1.0 / ga, act)
    expo = ga * (1.0 - et) / (ga - ga * et + et)
    totals = z.sum(1, keepdim=True)
    s = z / torch.where(totals > 0, totals, 1.0)
    count = act.sum(1)
    monopoly = count == 1
    done = (count == 0) | monopoly
    mu = torch.where(monopoly[:, None, :], act.to(z.dtype) * th / (th - 1.0), 0.0)
    iters = monopoly.to(torch.int64)
    residual = torch.zeros_like(totals[:, 0, :])
    return zpow, expo, s, mu, iters, done, residual


@torch.compile(fullgraph=True)
def _share_step(s, mu_out, iters, done, residual, act, zpow, th, et, expo, damping, tol):
    eps = 1.0 / (s / th + (1.0 - s) / et)
    mu = torch.where(act, eps / (eps - 1.0), 0.0)
    weight = Q.spow(mu * zpow, expo, act)
    totals = weight.sum(1, keepdim=True)
    proposed = weight / torch.where(totals > 0, totals, 1.0)
    denominator = torch.sqrt((s * s).sum(1))
    distance = torch.sqrt(((proposed - s) ** 2).sum(1)) / torch.where(denominator > 0, denominator, 1.0)
    relaxed = damping * proposed + (1.0 - damping) * s
    total_relaxed = relaxed.sum(1, keepdim=True)
    relaxed = relaxed / torch.where(total_relaxed > 0, total_relaxed, 1.0)
    working = ~done
    stop = working & (distance < tol)
    return (torch.where(working[:, None, :], relaxed, s),
            torch.where(stop[:, None, :], mu, mu_out),
            iters + working.to(iters.dtype), done | stop,
            torch.where(working, distance, residual))


@torch.compile(fullgraph=True)
def _share_residual(s, act, zpow, th, et, expo):
    eps = 1.0 / (s / th + (1.0 - s) / et)
    mu = torch.where(act, eps / (eps - 1.0), 0.0)
    weight = Q.spow(mu * zpow, expo, act)
    totals = weight.sum(1, keepdim=True)
    proposed = weight / torch.where(totals > 0, totals, 1.0)
    denominator = torch.sqrt((s * s).sum(1))
    return torch.sqrt(((proposed - s) ** 2).sum(1)) / torch.where(denominator > 0, denominator, 1.0)


def solve_shares_current(z, act, th, et, ga, numerics, check_every=4):
    """The original compiled per-market-freezing structure, with strict gates."""
    zp, expo, s, mu, iters, done, stopping = _share_start(*Q.free_b(z, act, th, et, ga))
    for iteration in range(1, numerics.share_max_iter + 1):
        if (iteration == 1 or iteration % check_every == 0) and bool(done.all()):
            break
        s, mu, iters, done, stopping = _share_step(
            *Q.free_b(s, mu, iters, done, stopping, act, zp, th, et, expo),
            numerics.share_damping, numerics.share_tol)
    returned = _share_residual(*Q.free_b(s, act, zp, th, et, expo))
    valid = (done.all(1) & torch.isfinite(s).all((1, 2)) & torch.isfinite(mu).all((1, 2))
             & (returned.amax(1) <= numerics.share_tol) & (stopping.amax(1) <= numerics.share_tol))
    return s, mu, iters, stopping.amax(1), returned.amax(1), valid


@torch.compile(fullgraph=True)
def _root_coefficients(WC, Jt, sum_part, overhead, ga, ac, varphibar, varphi, psi_cogs, rate):
    ak = ga - ac
    k1 = varphibar * WC ** (varphi / ac)
    k2 = (1.0 / (WC ** (ak / ac) * Jt)) ** (1.0 / ga) * psi_cogs * (rate * ac / ak) ** (ak / ga) * sum_part
    a, b = varphi * (ga - 1.0) / ac, (1.0 - ak) / ac
    valid = (torch.isfinite(k1) & torch.isfinite(k2) & torch.isfinite(overhead)
             & (k1 > 0) & (k2 > 0) & (overhead >= 0) & (Jt > 0))
    lk1, lk2 = torch.log(torch.where(k1 > 0, k1, 1.0)), torch.log(torch.where(k2 > 0, k2, 1.0))
    upper = (lk1 - lk2) / (b - a)
    lower_peak = (torch.log(torch.where(a > 0, a / b, 1.0)) + lk1 - lk2) / (b - a)
    lower = torch.where(a > 0, lower_peak, upper - 2.0)
    return lk1, lk2, a, b, lower, upper, valid


def _residual(log_y, lk1, lk2, a, b, overhead):
    return 1.0 - torch.exp(lk2 - lk1 + (b - a) * log_y) - overhead * torch.exp(-lk1 - a * log_y)


@torch.compile(fullgraph=True)
def _root_step(lower, upper, point, done, iterations, lk1, lk2, a, b, overhead, force_bisection):
    residual = _residual(point, lk1, lk2, a, b, overhead)
    lower = torch.where(~done & (residual > 0), point, lower)
    upper = torch.where(~done & (residual <= 0), point, upper)
    middle = lower + 0.5 * (upper - lower)
    width_ok = (upper - lower).abs() <= 5e-15 + ROOT_RTOL * middle.abs()
    first = torch.exp(lk2 - lk1 + (b - a) * point)
    second = overhead * torch.exp(-lk1 - a * point)
    derivative = -(b - a) * first + a * second
    newton = point - residual / torch.where(derivative != 0, derivative, 1.0)
    safe = torch.isfinite(newton) & (derivative != 0) & (newton > lower) & (newton < upper)
    if force_bisection:
        proposal = middle
    else:
        proposal = torch.where(safe, newton, middle)
    return lower, upper, torch.where(done, point, proposal), done | width_ok, iterations + (~done).to(iterations.dtype)


def solve_output_current(WC, Jt, sum_part, overhead, ga, ac, config, numerics, check_every=4):
    """Batched safeguarded Newton in the same upper log-output bracket as qmp.

    Alternate bisection steps guarantee bracket shrinkage. A narrow log bracket
    retains the reference's Brent position precision; the normalized residual
    remains a separate mandatory gate. No CPU per-economy root is called.
    """
    lk1, lk2, a, b, lower, upper, valid = _root_coefficients(
        *Q.free_b(WC, Jt, sum_part, overhead, ga, ac), config.varphibar, config.varphi, config.psi_cogs, config.r)
    zero = overhead == 0
    rlow = _residual(lower, lk1, lk2, a, b, overhead)
    nonpositive_a = (a <= 0) & ~zero & valid
    if bool(nonpositive_a.any()):
        for iteration in range(numerics.root_max_iter):
            extend = nonpositive_a & (rlow <= 0)
            if iteration % check_every == 0 and not bool(extend.any()):
                break
            lower = torch.where(extend, lower - 2.0, lower)
            rlow = _residual(lower, lk1, lk2, a, b, overhead)
    valid = valid & (zero | (torch.isfinite(rlow) & (rlow > 0)))
    done = ~valid | zero
    iterations = torch.zeros_like(Jt, dtype=torch.int64)
    point = lower + 0.5 * (upper - lower)
    for iteration in range(1, numerics.root_max_iter + 1):
        if (iteration == 1 or iteration % check_every == 0) and bool(done.all()):
            break
        lower, upper, point, done, iterations = _root_step(
            *Q.free_b(lower, upper, point, done, iterations, lk1, lk2, a, b, overhead), iteration % 2 == 0)
    solution = torch.where(zero, upper, lower + 0.5 * (upper - lower))
    residual = _residual(solution, lk1, lk2, a, b, overhead).abs()
    output = torch.exp(solution)
    valid = valid & done & torch.isfinite(output) & (output > 0) & torch.isfinite(residual) & (residual <= numerics.root_tol)
    output = torch.where(valid, output, float('nan'))
    return output, residual, iterations, valid


def _empty_cap(z):
    B, _, J = z.shape
    cap = {key: torch.full_like(z, float('nan')) for key in ('z', 'u', 's', 'mu', 'p', 'y', 'n', 'phi_ij')}
    cap.update({key: torch.full((B,), float('nan'), dtype=z.dtype, device=z.device) for key in ('W', 'Y', 'Ns', 'Nprod')})
    cap['Njt'] = torch.full((B, J), -1, dtype=torch.int64, device=z.device)
    cap['share_iterations'] = torch.full((B, J), -1, dtype=torch.int64, device=z.device)
    cap['err'] = torch.full((B, 3), float('nan'), dtype=z.dtype, device=z.device)
    cap['rounds'] = torch.zeros(B, dtype=torch.int64, device=z.device)
    return cap


def _period(z0, u0, pp, config, numerics, phi0, prior_valid, check_every):
    B, M, J = z0.shape
    z, u = z0, u0
    th, et, ga, ac = (pp[key] for key in ('th', 'et', 'ga', 'aC'))
    rows = torch.arange(B, device=z.device)
    captured = ~prior_valid.clone()
    valid_out = torch.zeros(B, dtype=torch.bool, device=z.device)
    errors = torch.zeros(B, dtype=torch.int64, device=z.device)
    cap = _empty_cap(z)
    phi_all = torch.full((B,), float('nan'), dtype=z.dtype, device=z.device) if phi0 is None else phi0.clone()
    phi = phi_all
    trace = []
    if bool(captured.all()):
        return cap, phi_all, valid_out, errors, trace
    for iteration in range(1, numerics.entry_max_iter + 1):
        Bw = z.shape[0]
        act = z > 0
        counts = act.sum(1)
        Jt = (counts > 0).sum(1).to(z.dtype)
        s, mu, share_iters, stop_resid, share_resid, share_ok = solve_shares_current(z, act, th, et, ga, numerics, check_every)
        WC, p, demand, sum_part = Q._prices(*Q.free_b(z, act, s, mu, counts.to(z.dtype), Jt, th, et, ga, ac), config.p, config.r)
        price_ok = torch.isfinite(WC) & (WC > 0) & torch.isfinite(p).all((1, 2)) & torch.isfinite(demand).all((1, 2))
        if phi0 is None and iteration == 1:
            dpow = Q.spow(demand, 1.0 / ga, act)
            numerator = (mu - ga) * config.varphibar * WC[:, None, None] ** (config.varphi / ac) * dpow
            denominator = (ac * config.psi_cogs * u * Q.spow(z, 1.0 / ga, act) / config.psi_sga * sum_part[:, None, None]
                           + (mu - ga) * dpow * u.sum(1).sum(1)[:, None, None])
            gammas = torch.where(act, numerator / torch.where(act, denominator, 1.0), float('nan'))
            sorted_gamma = gammas.reshape(Bw, M * J).sort(1).values
            phi = torch.where(pp['zeta'] < 1, sorted_gamma.gather(1, pp['cdf_index'][:, None])[:, 0], sorted_gamma[:, -1] * pp['zeta'])
            phi = torch.where(pp['cdf_supported'], phi, float('nan'))
            phi_all[rows] = phi
        phi_ok = torch.isfinite(phi) & (phi >= 0)
        fixed = phi[:, None, None] * u
        overhead = fixed.sum(1).sum(1)
        Y, root_resid, root_iters, root_ok = solve_output_current(WC, Jt, sum_part, overhead, ga[:, 0, 0], ac[:, 0, 0], config, numerics, check_every)
        W, y, labor, loss_pi, n_loss = Q._profits(*Q.free_b(z, act, u, p, demand, WC, Y, Jt, phi, ga, ac), config.r, config.psi_cogs, config.psi_sga)
        supply = config.varphibar * W ** config.varphi
        production = labor.sum(1).sum(1)
        labor_resid = (production + overhead - supply) / supply
        # This is integer division, preserving the current CPU's zero-based rank.
        k = torch.div(n_loss, 3, rounding_mode='floor').long().clamp(max=M * J - 1)
        selected = torch.topk(loss_pi.reshape(Bw, -1), int(k.max().item()) + 1, dim=1, largest=False).values
        cutoff = torch.where(n_loss > 0, selected.gather(1, k[:, None])[:, 0], 0.0)
        z_new, u_new, dropped = Q._apply_exit(*Q.free_b(loss_pi, cutoff, z, u, captured))
        below = dropped < numerics.entry_drop_stop
        finite = (torch.isfinite(W) & torch.isfinite(Y) & torch.isfinite(supply)
                  & torch.isfinite(y).all((1, 2)) & torch.isfinite(labor).all((1, 2)))
        labor_ok = torch.isfinite(labor_resid) & (labor_resid.abs() <= 1e-10)
        code = torch.zeros(Bw, dtype=torch.int64, device=z.device)
        for condition, number in ((~finite, 8), (~labor_ok, 6), (~root_ok, 5), (~price_ok, 4), (~phi_ok, 3), (~share_ok, 2), (Jt == 0, 1)):
            code = torch.where(condition, number, code)
        if iteration == numerics.entry_max_iter:
            code = torch.where((code == 0) & ~below, 7, code)
        failed = (code != 0) & ~captured
        stop = below & (code == 0) & ~captured
        working = ~captured
        metric = torch.stack((torch.full_like(Jt, float(iteration)), act.sum((1, 2)).to(z.dtype), Jt,
                              n_loss.to(z.dtype), dropped.to(z.dtype), root_resid, root_iters.to(z.dtype),
                              labor_resid, stop_resid, share_resid, share_iters.amax(1).to(z.dtype), production, overhead), dim=1)
        trace.append(torch.cat((rows[working, None].to(z.dtype), metric[working]), dim=1))
        if bool(stop.any()):
            destinations = rows[stop]
            for key, value in zip(('z', 'u', 's', 'mu', 'p', 'y', 'n', 'phi_ij'), (z, u, s, mu, p, y, labor, fixed)):
                cap[key][destinations] = value[stop]
            for key, value in (('W', W), ('Y', Y), ('Ns', supply), ('Nprod', supply - overhead), ('Njt', counts), ('share_iterations', share_iters)):
                cap[key][destinations] = value[stop]
            cap['err'][destinations] = torch.stack(((share_iters[stop] >= numerics.share_max_iter).to(z.dtype).mean(1), share_iters[stop].to(z.dtype).mean(1), z[stop].mean((1, 2))), dim=1)
            cap['rounds'][destinations] = iteration
            valid_out[destinations] = True
        errors[rows[failed]] = code[failed]
        cap['rounds'][rows[failed]] = iteration
        captured = captured | stop | failed
        n_left = int((~captured).sum().item())
        if n_left == 0:
            break
        z, u = z_new, u_new
        # Retain the historical dynamic-B compaction, including its singleton tail.
        if 2 <= n_left < Bw:
            keep = ~captured
            z, u, th, et, ga, ac, phi, rows, captured = [value[keep] for value in (z, u, th, et, ga, ac, phi, rows, captured)]
    return cap, phi_all, valid_out, errors, trace


@torch.compile(fullgraph=True)
def _three_moments(n0, f0, p0, y0, mu0, W0, n1, f1, gamma, alpha_cogs, psi_cogs, psi_sga):
    on0, on1 = n0 > 0, n1 > 0
    e0, e1 = torch.where(on0, n0 + f0, 0.0), torch.where(on1, n1 + f1, 0.0)
    reallocation = (e1 - e0).abs().sum(1).sum(1) / (0.5 * (e0.sum(1).sum(1) + e1.sum(1).sum(1)))
    # Preserve the current moment definition and logical Fortran firm order.
    active = on0.transpose(1, 2).reshape(n0.shape[0], -1)
    revenue = (p0 * y0).transpose(1, 2).reshape(n0.shape[0], -1)
    revenue = torch.where(active, revenue, 0.0)
    weights = revenue / revenue.sum(1, keepdim=True)
    markups = torch.where(active, mu0.transpose(1, 2).reshape(n0.shape[0], -1), 0.0)
    fixed = f0.transpose(1, 2).reshape(n0.shape[0], -1)
    production = n0.transpose(1, 2).reshape(n0.shape[0], -1)
    sga = W0[:, None] * fixed / psi_sga
    costs = gamma / alpha_cogs * W0[:, None] * production / psi_cogs + sga
    shares = torch.where(active, sga / torch.where(active, costs, 1.0), 0.0)
    return torch.stack((reallocation, (weights * markups).sum(1), (weights * shares).sum(1)), dim=1)


def _traces_to_host(trace, errors, valid, config, numerics, draw_sources):
    B = valid.shape[0]
    records = [[] for _ in range(B)]
    if trace:
        packed = torch.cat(trace, dim=0).detach().cpu().numpy()
        for row in packed:
            item = {}
            for key, value in zip(TRACE_KEYS, row[1:]):
                item[key] = int(value) if key in INTEGER_KEYS else float(value) if math.isfinite(float(value)) else None
            records[int(row[0])].append(item)
    return records


def solve_batch_current(x, config=None, numerics=None, draws=None, device='cuda', dtype=torch.float64,
                        return_equilibrium=False, prepared_inputs=None, check_every=4):
    """Solve current-qmp economies together on the existing compiled batch engine.

    ``x`` is [B,6], with a common floor(N). ``draws`` is one shared current
    standard-normal mapping or B mappings. The compact result contains NumPy
    moments[B,3], phi/Mbar[B], valid[B], diagnostics and explicit row errors.
    With return_equilibrium=True, equi retains all arrays on CUDA with leading B.
    Failed floating rows are NaN and failed integer counters are -1.
    """
    c, n = config or ModelConfig(), numerics or Numerics()
    params = np.asarray(x, dtype=np.float64)
    if params.ndim != 2 or params.shape[1] != 6 or params.shape[0] < 1:
        raise ValueError('x must have shape (B,6), B >= 1')
    for row, point in enumerate(params):
        try:
            _validate(point, c, n)
        except ValueError as exc:
            raise ValueError(f'parameter row {row}: {exc}') from exc
    B = len(params)
    M = math.floor(params[0, 4])
    if not np.all(np.floor(params[:, 4]) == M):
        raise ValueError('one GPU batch must share floor(N)')
    if dtype != torch.float64:
        raise ValueError('the current-qmp contract requires float64')
    dev = torch.device(device)
    if dev.type != 'cuda' or not torch.cuda.is_available():
        raise ValueError('the current GPU batch requires CUDA')
    dev = torch.device('cuda', torch.cuda.current_device() if dev.index is None else dev.index)
    if not isinstance(check_every, int) or check_every < 1:
        raise ValueError('check_every must be a positive integer')
    if prepared_inputs is None:
        all_z, all_u, sources = [], [], []
        for row, point in enumerate(params):
            injected = draws if draws is None or isinstance(draws, Mapping) else draws[row]
            z, u, source = build_productivity(point, c.markets, c.zbar, injected)
            all_z.append(z); all_u.append(u); sources.append(source)
        z = torch.as_tensor(np.stack(all_z), dtype=dtype, device=dev)
        u = torch.as_tensor(np.stack(all_u), dtype=dtype, device=dev)
    else:
        if draws is not None:
            raise ValueError('choose draws or prepared_inputs')
        z, u, sources = prepared_inputs
        if isinstance(sources, str):
            sources = [sources] * B
        for name, value, shape in (('productivity', z, (B, M, c.markets, 2)), ('overhead', u, (B, M, c.markets))):
            if not isinstance(value, torch.Tensor) or value.dtype != dtype or value.device != dev or tuple(value.shape) != shape:
                raise ValueError(f'prepared {name} must be CUDA float64 with shape {shape}')
            if not bool(torch.isfinite(value).all()) or not bool((value > 0).all()):
                raise ValueError(f'prepared {name} must be finite and positive')
    q = torch.as_tensor(params, dtype=dtype, device=dev)
    common = lambda v: torch.full((B, 1, 1), v, dtype=dtype, device=dev)
    cdf = Q.quantile_positions(M * c.markets)
    ranks = np.searchsorted(cdf, params[:, 5], side='right')
    supported = (params[:, 5] >= 1) | (ranks < len(cdf))
    pp = {'th': q[:, 0, None, None], 'et': q[:, 1, None, None], 'ga': common(c.gamma), 'aC': common(c.alpha_cogs),
          'zeta': q[:, 5], 'cdf_index': torch.as_tensor(np.minimum(ranks, len(cdf)-1), device=dev),
          'cdf_supported': torch.as_tensor(supported, device=dev)}
    phi = None
    prior = torch.ones(B, dtype=torch.bool, device=dev)
    first, phi, ok1, error1, trace1 = _period(z[:, :, :, 0], u, pp, c, n, phi, prior, check_every)
    second, _, ok2, error2, trace2 = _period(z[:, :, :, 1], u, pp, c, n, phi, ok1, check_every)
    moments = _three_moments(*Q.free_b(first['n'], first['phi_ij'], first['p'], first['y'], first['mu'], first['W'],
                                     second['n'], second['phi_ij']), c.gamma, c.alpha_cogs, c.psi_cogs, c.psi_sga)
    valid = ok1 & ok2 & torch.isfinite(moments).all(1)
    moments = torch.where(valid[:, None], moments, float('nan'))
    phi = torch.where(valid, phi, float('nan'))
    # Preserve the current CPU's sum/true-divide convention exactly. Counts
    # sum in int64 on CUDA, then cross as exact float64 integers; division by
    # J is performed once by NumPy below, rather than CUDA mean's reciprocal.
    total_firms = first['Njt'].sum(1)
    firm_count = torch.where(valid, total_firms.to(dtype), float('nan'))
    compact = torch.cat((moments, phi[:, None], firm_count[:, None], valid[:, None].to(dtype), second['err'],
                         first['rounds'][:, None].to(dtype), second['rounds'][:, None].to(dtype),
                         error1[:, None].to(dtype), error2[:, None].to(dtype)), dim=1).detach().cpu().numpy()
    compact[:, 4] = np.true_divide(compact[:, 4], c.markets)
    host_traces = [_traces_to_host(t, None, valid, c, n, sources) for t in (trace1, trace2)]
    diagnostics, errors = [], []
    for row in range(B):
        periods = []
        for t in range(2):
            rounds = host_traces[t][row]
            code = int(compact[row, 11+t])
            passed = bool(compact[row, 5]) if t == 1 else code == 0 and bool(rounds)
            last = rounds[-1] if rounds else {}
            reason = 'proposed_drop_below_threshold' if passed else 'iteration_limit' if code == 7 else 'numerical_failure'
            periods.append({**last, 'entry_iterations': len(rounds), 'entry_rounds': len(rounds),
                            'entry_stop_reason': reason, 'entry_stopping_rule_met': passed,
                            'remaining_loss_firms': last.get('loss_firms', 0), 'rounds': rounds})
        diagnosis = {'dtype': 'float64', 'draw_source': sources[row], 'config': asdict(c), 'numerics': asdict(n),
                     'periods': periods, 'entry_method': 'sequential_exit_pre_exit_stop_no_reentry_test',
                     'entry_stopping_rule_met': bool(compact[row, 5]),
                     'backend': 'existing_qmp_torch_compiled_batch_current_contract'}
        good = bool(compact[row, 5])
        if good and not diagnostic_quality(diagnosis, asdict(n))['passed']:
            good = False
            compact[row, :5] = np.nan
            compact[row, 5] = 0
            diagnosis['entry_stopping_rule_met'] = False
        code1, code2 = int(compact[row, 11]), int(compact[row, 12])
        error = None if good else ('period 1: '+ERROR_NAMES.get(code1, 'failed validation') if code1 else 'period 2: '+ERROR_NAMES.get(code2, 'failed validation'))
        diagnostics.append(diagnosis); errors.append(error)
    result = {'moments': compact[:, :3].copy(), 'moment_names': MOMENT_NAMES, 'phi': compact[:, 3].copy(),
              'Mbar': compact[:, 4].copy(), 'valid': compact[:, 5].astype(bool), 'err': compact[:, 6:9].copy(),
              'rounds': compact[:, 9:11].astype(np.int64), 'diagnostics': diagnostics, 'errors': errors}
    if return_equilibrium:
        equi = {f'{key}_ijt': torch.stack((first[old], second[old]), dim=3)
                for key, old in (('phi', 'phi_ij'), ('mu', 'mu'), ('z', 'z'), ('s', 's'), ('y', 'y'), ('p', 'p'), ('u', 'u'), ('n', 'n'))}
        equi.update({f'{key}_t': torch.stack((first[key], second[key]), dim=1) for key in ('W', 'Y', 'Ns', 'Nprod')})
        equi['Njt'] = torch.stack((first['Njt'], second['Njt']), dim=2)
        equi['share_iterations'] = torch.stack((first['share_iterations'], second['share_iterations']), dim=2)
        result['equi'] = equi
    return result
