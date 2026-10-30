"""Float64 CUDA arrays for the full two-period teaching economy.

Shares, prices, production, labor, profits, overhead calibration and exit use
CUDA tensors. The identical native random-input preparation and the aggregate
one-dimensional upper-root Brent calculation use the frozen NumPy/SciPy
reference. Only aggregate scalars cross to the host during equilibrium solving;
firm arrays never fall back to a CPU equilibrium solver.
"""
from __future__ import annotations

from dataclasses import asdict
import math
import numpy as np
import torch

from qmp.draws import build_productivity
from qmp.equilibrium import ModelConfig, Numerics, EquilibriumError, _validate, _solve_output
from .shares import solve_shares


def _cuda_device(device):
    target = torch.device(device)
    if target.type != 'cuda' or not torch.cuda.is_available():
        raise ValueError('the GPU economy requires an available CUDA device')
    return torch.device('cuda', torch.cuda.current_device() if target.index is None else target.index)


def _power(value, exponent, active):
    return torch.where(active, torch.where(active, value, 1.0) ** exponent, 0.0)


def _sum_firms(value):
    # Keep the reference's firms-within-markets, then markets convention.
    return float(value.sum(dim=0).sum().item())


def prepare_inputs(x, config=None, draws=None, device='cuda'):
    """Prepare precisely the reference productivity bank and upload it once.

    Input preparation is deliberately shared, so CPU/GPU comparisons do not
    compare two random-number streams or two exponential implementations.
    Timings may either include this work or explicitly start with resident
    inputs. Neither prepared tensor is mutated by ``solve_economy``.
    """
    c = config or ModelConfig()
    parameters = np.asarray(x, dtype=np.float64)
    _validate(parameters, c, Numerics())
    target = _cuda_device(device)
    productivity, overhead, source = build_productivity(parameters, c.markets, c.zbar, draws)
    return (torch.as_tensor(np.ascontiguousarray(productivity), dtype=torch.float64, device=target),
            torch.as_tensor(np.ascontiguousarray(overhead), dtype=torch.float64, device=target), source)


def _prices(z, active, s, mu, counts, market_count, theta, eta, c):
    ga, ac, ak = c.gamma, c.alpha_cogs, c.gamma - c.alpha_cogs
    number = counts[None, :].to(z.dtype)
    safe_number = torch.where(number > 0, number, 1.0)
    constant = (1 / ac) ** (ac / ga) * (c.r / ak) ** (ak / ga)
    base = (1 / market_count) * safe_number ** ((1 - theta) / (eta - 1)) * _power(s, (eta - theta) / (eta - 1), active)
    inverse_z = _power(z, -1 / ga, active)
    price_part = constant * _power(base, 1 / ga - 1, active) * mu * inverse_z
    sector_sum = (_power(price_part, ga * (1 - eta) / (ga - ga * theta + theta), active) / safe_number).sum(dim=0)
    operating = counts > 0
    sector_term = _power(sector_sum, (1 - theta) / (1 - eta), operating)
    wc = float(((sector_term.sum() / market_count) ** ((ga - ga * theta + theta) / (theta - 1)) * c.p**ga).item())
    price_part = constant * _power(base * c.p**theta, 1 / ga - 1, active) * mu * inverse_z * wc ** (1 / ga)
    p = _power(price_part, ga / (ga - ga * theta + theta), active)
    sector_prices = _power((_power(p, 1 - eta, active) / safe_number).sum(dim=0), 1 / (1 - eta), operating)
    safe_sector_prices = torch.where(operating, sector_prices, 1.0)[None, :]
    demand = _power(p / safe_sector_prices, -eta, active) * (safe_sector_prices / c.p) ** (-theta) / safe_number
    safe_z = torch.where(active, z, 1.0)
    production_part = _power(
        _power(number * s, (theta - eta) / (1 - eta), active)
        * _power(p, -theta, active) * c.p**theta / (safe_number * safe_z), 1 / ga, active
    )
    if not math.isfinite(wc) or wc <= 0 or not bool(torch.isfinite(p).all() & torch.isfinite(demand).all()):
        raise EquilibriumError('nonfinite or nonpositive price-system solution')
    return wc, p, demand, _sum_firms(production_part)


def _strict_quantile_index(size, zeta):
    """Reproduce the reference's sequential uniform CDF using host scalars.

    A parallel cumulative sum can select a different rank at exact CDF ties.
    This scalar rank calculation transfers no economic array off the device.
    It intentionally retains the implemented strict ``CDF > zeta`` rule.
    """
    weight, cumulative = 1.0 / size, 0.0
    for index in range(size):
        cumulative += weight
        if cumulative > zeta:
            return index
    raise EquilibriumError('strict overhead quantile has no support at this zeta')


def _solve_period(z_initial, u_initial, theta, eta, zeta, c, n, phi):
    z, u = z_initial.clone(), u_initial.clone()
    round_records = []
    for iteration in range(1, n.entry_max_iter + 1):
        active = z > 0
        counts = active.sum(dim=0)
        market_count = int(torch.count_nonzero(counts).item())
        if market_count == 0:
            raise EquilibriumError('the entry algorithm removed every firm')
        s, mu, share = solve_shares(z, theta, eta, c.gamma, n)
        wc, p, demand, sum_part = _prices(z, active, s, mu, counts, market_count, theta, eta, c)
        if phi is None:
            demand_power = _power(demand, 1 / c.gamma, active)
            numerator = (mu - c.gamma) * c.varphibar * wc ** (c.varphi / c.alpha_cogs) * demand_power
            denominator = (c.alpha_cogs * c.psi_cogs * u * _power(z, 1 / c.gamma, active) / c.psi_sga * sum_part
                           + (mu - c.gamma) * demand_power * _sum_firms(u))
            gamma_values = (numerator[active] / denominator[active]).sort().values
            if zeta < 1:
                index = _strict_quantile_index(gamma_values.numel(), zeta)
                phi = float(gamma_values[index].item())
            else:
                phi = float(gamma_values[-1].item() * zeta)
            if not math.isfinite(phi) or phi < 0:
                raise EquilibriumError('the fixed labor phi is not finite and nonnegative')
        fixed_labor = phi * u
        overhead = _sum_firms(fixed_labor)
        # The exact same upper-positive-branch scalar root helper; no firm
        # arrays, market arrays or equilibrium solves are moved to the CPU.
        output, root_residual, root_iterations = _solve_output(wc, market_count, sum_part, overhead, c, n)
        wage = float((wc / output ** (1 - c.gamma)) ** (1 / c.alpha_cogs))
        technology = z * (1 / c.psi_cogs) ** c.gamma * ((c.gamma - c.alpha_cogs) * wage / (c.alpha_cogs * c.r)) ** (c.gamma - c.alpha_cogs)
        y = demand * output / market_count
        labor = _power(y / torch.where(active, technology, 1.0), 1 / c.gamma, active)
        supply = float(c.varphibar * wage**c.varphi)
        actual_production = _sum_firms(labor)
        labor_residual = float((actual_production + overhead - supply) / supply)
        profits = p * y - c.gamma * wage * labor / (c.alpha_cogs * c.psi_cogs) - wage * fixed_labor / c.psi_sga
        losses = profits[active & (profits <= 0)]
        rank = losses.numel() // 3
        threshold = float(torch.kthvalue(losses, rank + 1).values.item()) if losses.numel() else 0.0
        drop = active & (profits <= threshold)
        dropped = int(drop.sum().item())
        record = {
            'iteration': iteration, 'active_firms': int(active.sum().item()), 'active_markets': market_count,
            'loss_firms': losses.numel(), 'proposed_drop': dropped,
            'root_relative_residual': root_residual, 'root_iterations': root_iterations,
            'labor_relative_residual': labor_residual,
            'max_share_stopping_residual': float(share['stopping_residual'].max().item()),
            'max_share_residual': float(share['returned_residual'].max().item()),
            'max_share_iterations': int(share['iterations'].max().item()),
        }
        round_records.append(record)
        if dropped < n.entry_drop_stop or iteration == n.entry_max_iter:
            reason = 'proposed_drop_below_threshold' if dropped < n.entry_drop_stop else 'iteration_limit'
            result = {'z': z, 'u': u, 's': s, 'mu': mu, 'p': p, 'y': y, 'n': labor,
                      'phi': fixed_labor, 'W': wage, 'Y': output, 'Ns': supply,
                      'Nprod': supply - overhead, 'Njt': counts,
                      'share_iterations': share['iterations']}
            for value in result.values():
                if isinstance(value, torch.Tensor):
                    finite = bool(torch.isfinite(value).all())
                else:
                    finite = math.isfinite(value)
                if not finite:
                    raise EquilibriumError('nonfinite final firm or aggregate quantities')
            diagnosis = {**record, 'entry_iterations': iteration, 'entry_rounds': iteration,
                         'entry_stop_reason': reason, 'entry_stopping_rule_met': reason != 'iteration_limit',
                         'remaining_loss_firms': losses.numel(), 'actual_production_labor': actual_production,
                         'overhead_labor': overhead, 'rounds': round_records}
            err = torch.stack(((share['iterations'] >= n.share_max_iter).to(z.dtype).mean(),
                               share['iterations'].to(z.dtype).mean(), z.mean()))
            return result, phi, err, diagnosis
        z = torch.where(drop, 0.0, z)
        u = torch.where(drop, 0.0, u)
    raise AssertionError('entry loop must return or raise')


def solve_economy(x, config=None, numerics=None, draws=None, device='cuda', prepared_inputs=None):
    """Solve both periods with CUDA firm arrays and identical CPU contracts.

    ``prepared_inputs`` may be the tuple returned by ``prepare_inputs`` to time
    resident inputs. Otherwise identical NumPy input preparation and its upload
    occur inside this call. Both periods begin with all potential firms; zeta
    picks the fixed scalar phi in period 1 and period 2 keeps it.
    """
    c, n = config or ModelConfig(), numerics or Numerics()
    parameters = np.asarray(x, dtype=np.float64)
    _validate(parameters, c, n)
    target = _cuda_device(device)
    if prepared_inputs is None:
        productivity, overhead, draw_source = prepare_inputs(parameters, c, draws, target)
    else:
        if draws is not None:
            raise ValueError('choose draws or prepared_inputs, not both')
        productivity, overhead, draw_source = prepared_inputs
        firms = int(np.floor(parameters[4]))
        for name, value, shape in (('productivity', productivity, (firms, c.markets, 2)),
                                   ('overhead', overhead, (firms, c.markets))):
            if (not isinstance(value, torch.Tensor) or value.dtype != torch.float64
                    or value.device != target or tuple(value.shape) != shape):
                raise ValueError(f'prepared {name} must be float64 on {target} with shape {shape}')
            if not bool(torch.isfinite(value).all()) or not bool((value > 0).all()):
                raise ValueError(f'prepared {name} must be finite and positive')
    theta, eta, _, _, _, zeta = map(float, parameters[:6])
    periods, diagnostics = [], []
    phi = None
    for t in range(2):
        period, phi, err, diagnosis = _solve_period(productivity[:, :, t], overhead, theta, eta, zeta, c, n, phi)
        periods.append(period)
        diagnostics.append(diagnosis)
    equi = {f'{key}_ijt': torch.stack([period[key] for period in periods], dim=2)
            for key in ('phi', 'mu', 'z', 's', 'y', 'p', 'u', 'n')}
    equi.update({f'{key}_t': torch.tensor([period[key] for period in periods], dtype=torch.float64, device=target)
                 for key in ('W', 'Y', 'Ns', 'Nprod')})
    equi['Njt'] = torch.stack([period['Njt'] for period in periods], dim=1)
    equi['share_iterations'] = torch.stack([period['share_iterations'] for period in periods], dim=1)
    return {'equi': equi, 'phi': phi, 'err': err,
            'diagnostics': {'dtype': 'float64', 'draw_source': draw_source, 'config': asdict(c), 'numerics': asdict(n),
                            'periods': diagnostics, 'entry_method': 'sequential_exit_pre_exit_stop_no_reentry_test',
                            'backend': 'pytorch_cuda_float64',
                            'host_work': 'identical input preparation; aggregate scalar upper-root Brent; strict scalar CDF rank'}}
