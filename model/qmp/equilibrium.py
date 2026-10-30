"""A float64 NumPy/SciPy implementation of one two-period economy.

There are three nested calculations: Cournot shares within each market,
aggregate labor-market clearing, and the specified sequential exit algorithm.
The exit algorithm retains the *pre-exit* state when fewer than three firms
would leave. It constructs an approximate entry outcome, not a certificate of
Nash equilibrium: firms already removed are not tested for profitable reentry.
"""

from dataclasses import asdict, dataclass
from collections.abc import Mapping
import numpy as np
from scipy.optimize import brentq

from .draws import build_productivity


@dataclass(frozen=True)
class ModelConfig:
    """Technology, aggregate supply, and fixed market structure.

    ``varphi`` is the labor-supply exponent, 0.25 in the reference model.
    ``gamma`` is returns to scale; ``alpha_cogs`` is the COGS elasticity.
    The capital elasticity is their difference.
    """
    gamma: float = 1.0252
    alpha_cogs: float = 0.8365
    markets: int = 10000
    r: float = 1.16
    p: float = 1.0
    varphi: float = 0.25
    varphibar: float = 1.0
    psi_cogs: float = 0.33
    psi_sga: float = 0.33
    zbar: float = 1.0


@dataclass(frozen=True)
class Numerics:
    """Precision and iteration limits shared by every solve."""
    share_tol: float = 1e-10
    share_max_iter: int = 1000
    share_damping: float = 0.35
    root_tol: float = 1e-12
    root_max_iter: int = 100
    entry_max_iter: int = 50
    entry_drop_stop: int = 3


class EquilibriumError(RuntimeError):
    """A numerical subproblem failed or the positive equilibrium does not exist."""


def _validate(x: np.ndarray, c: ModelConfig, n: Numerics) -> None:
    if x.shape != (6,) or not np.isfinite(x).all():
        raise ValueError("x must contain 6 finite parameters")
    theta, eta, rho, sigma, firms, zeta = x
    if not 1 < theta <= eta:
        raise ValueError("Cournot demand requires 1 < theta <= eta")
    if not abs(rho) < 1 or min(sigma, zeta) < 0:
        raise ValueError("require |rho| < 1 and nonnegative sigma and zeta")
    if firms < 1:
        raise ValueError("floor(N) must be at least one potential firm per market")
    if not isinstance(c.markets, (int, np.integer)) or c.markets < 1:
        raise ValueError("markets must be a positive integer")
    if not all(np.isfinite(v) and v > 0 for k, v in asdict(c).items() if k != "markets"):
        raise ValueError("all ModelConfig scalars must be finite and positive")
    if not c.alpha_cogs < c.gamma < eta / (eta - 1):
        raise ValueError("require alpha_cogs < gamma < eta/(eta-1) for positive capital and overhead")
    a = c.varphi * (c.gamma - 1) / c.alpha_cogs
    b = (1 - c.gamma + c.alpha_cogs) / c.alpha_cogs
    if b <= max(a, 0):
        raise ValueError("technology and labor supply must imply output exponent b > max(a,0)")
    if not 0 < n.share_damping <= 1:
        raise ValueError("share_damping must lie in (0,1]")
    for name in ("share_tol", "root_tol"):
        if not np.isfinite(getattr(n, name)) or not 0 < getattr(n, name) < 1:
            raise ValueError(f"{name} must lie in (0,1)")
    for name in ("share_max_iter", "root_max_iter", "entry_max_iter", "entry_drop_stop"):
        v = getattr(n, name)
        if not isinstance(v, (int, np.integer)) or v < 1:
            raise ValueError(f"{name} must be a positive integer")


def _power(value: np.ndarray, exponent: float, active: np.ndarray) -> np.ndarray:
    """A power on operating firms only, including negative exponents."""
    return np.where(active, np.where(active, value, 1.0) ** exponent, 0.0)


def _sum_firms(value: np.ndarray) -> float:
    # Sum firms within markets, then markets, matching the reference convention.
    return float(np.sum(np.sum(value, axis=0)))


def solve_shares(
    z: np.ndarray, theta: float, eta: float, gamma: float,
    numerics: Numerics | None = None,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Solve all markets; ``z`` has shape (firms, markets), zeros mean inactive.

    Returns shares, markups, and diagnostic arrays. Empty markets return zeros;
    monopolies return share one and markup ``theta/(theta-1)``. As in the
    reference iteration, markups use the last *pre-damping* shares, whereas
    returned shares include that damping step. Tight precision controls this
    small difference. Markets stop individually and then stay frozen.
    """
    n = numerics or Numerics()
    z = np.asarray(z, dtype=np.float64)
    if z.ndim != 2 or not np.isfinite(z).all() or np.any(z < 0):
        raise ValueError("z must be a finite, nonnegative two-dimensional array")
    if not 1 < theta <= eta or not 0 < gamma < eta / (eta - 1):
        raise ValueError("invalid demand parameters or returns to scale")
    if not 0 < n.share_damping <= 1 or not 0 < n.share_tol < 1 or n.share_max_iter < 1:
        raise ValueError("invalid share iteration controls")
    active = z > 0
    count = active.sum(axis=0)
    total = z.sum(axis=0)
    s = z / np.where(total > 0, total, 1.0)
    mu = np.zeros_like(z)
    iterations = np.zeros(z.shape[1], dtype=np.int64)
    residual = np.zeros(z.shape[1])
    done = count == 0
    monopoly = count == 1
    mu[:, monopoly] = active[:, monopoly] * theta / (theta - 1)
    iterations[monopoly] = 1
    done |= monopoly
    z_inverse = _power(z, -1 / gamma, active)
    exponent = gamma * (1 - eta) / (gamma - gamma * eta + eta)

    def update(shares: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        elasticity = 1 / (shares / theta + (1 - shares) / eta)
        markups = elasticity / (elasticity - 1)
        weight = _power(markups * z_inverse, exponent, active)
        weight_sum = weight.sum(axis=0)
        proposed = weight / np.where(weight_sum > 0, weight_sum, 1.0)
        return proposed, np.where(active, markups, 0.0)

    for iteration in range(1, n.share_max_iter + 1):
        if done.all():
            break
        proposed, current_mu = update(s)
        denominator = np.linalg.norm(s, axis=0)
        distance = np.linalg.norm(proposed - s, axis=0) / np.where(denominator > 0, denominator, 1)
        working = ~done
        relaxed = n.share_damping * proposed + (1 - n.share_damping) * s
        normalizer = relaxed.sum(axis=0)
        relaxed /= np.where(normalizer > 0, normalizer, 1.0)
        s[:, working] = relaxed[:, working]
        mu[:, working] = current_mu[:, working]
        iterations[working] = iteration
        residual[working] = distance[working]
        done |= working & (distance < n.share_tol)
    if not done.all():
        failed = np.flatnonzero(~done)
        raise EquilibriumError(
            f"share fixed point failed in {failed.size} markets after {n.share_max_iter} iterations; "
            f"maximum relative residual {residual[failed].max():.3g}"
        )
    proposed, _ = update(s)
    denominator = np.linalg.norm(s, axis=0)
    returned_residual = np.linalg.norm(proposed - s, axis=0) / np.where(denominator > 0, denominator, 1)
    if not np.isfinite(s).all() or not np.isfinite(mu).all():
        raise EquilibriumError("nonfinite shares or markups")
    return s, mu, {"iterations": iterations, "stopping_residual": residual,
                   "returned_residual": returned_residual}


def _prices(z, active, s, mu, counts, market_count, theta, eta, c):
    """Price index, relative prices, and sector demand before aggregate Y."""
    ga, ac, ak = c.gamma, c.alpha_cogs, c.gamma - c.alpha_cogs
    number = counts[None, :]
    safe_number = np.where(number > 0, number, 1.0)
    constant = (1 / ac) ** (ac / ga) * (c.r / ak) ** (ak / ga)
    base = (1 / market_count) * safe_number ** ((1 - theta) / (eta - 1)) * _power(s, (eta - theta) / (eta - 1), active)
    inverse_z = _power(z, -1 / ga, active)
    price_part = constant * _power(base, 1 / ga - 1, active) * mu * inverse_z
    sector_sum = (_power(price_part, ga * (1 - eta) / (ga - ga * theta + theta), active) / safe_number).sum(axis=0)
    operating = counts > 0
    sector_term = _power(sector_sum, (1 - theta) / (1 - eta), operating)
    wc = float((sector_term.sum() / market_count) ** ((ga - ga * theta + theta) / (theta - 1)) * c.p**ga)
    price_part = constant * _power(base * c.p**theta, 1 / ga - 1, active) * mu * inverse_z * wc ** (1 / ga)
    p = _power(price_part, ga / (ga - ga * theta + theta), active)
    sector_prices = _power((_power(p, 1 - eta, active) / safe_number).sum(axis=0), 1 / (1 - eta), operating)
    safe_sector_prices = np.where(operating, sector_prices, 1.0)[None, :]
    demand = _power(p / safe_sector_prices, -eta, active) * (safe_sector_prices / c.p) ** (-theta) / safe_number
    safe_z = np.where(active, z, 1.0)
    production_part = _power(
        _power(number * s, (theta - eta) / (1 - eta), active)
        * _power(p, -theta, active) * c.p**theta / (safe_number * safe_z), 1 / ga, active
    )
    if not np.isfinite(wc) or wc <= 0 or not np.isfinite(p).all() or not np.isfinite(demand).all():
        raise EquilibriumError("nonfinite or nonpositive price-system solution")
    return wc, p, demand, _sum_firms(production_part)


def _solve_output(wc, markets, sum_production_part, overhead, c, n):
    """Select the economically relevant upper positive labor-clearing root.

    F(Y)=K1*Y^a-K2*Y^b-overhead. When a>0, F can have two roots;
    its known maximum brackets the upper root. Solving in log Y preserves
    positivity and avoids an arbitrary near-zero lower bracket.
    """
    ga, ac, ak = c.gamma, c.alpha_cogs, c.gamma - c.alpha_cogs
    k1 = c.varphibar * wc ** (c.varphi / ac)
    k2 = (1 / (wc ** (ak / ac) * markets)) ** (1 / ga) * c.psi_cogs * (c.r * ac / ak) ** (ak / ga) * sum_production_part
    a, b = c.varphi * (ga - 1) / ac, (1 - ak) / ac
    if min(k1, k2) <= 0 or not np.isfinite([k1, k2, overhead]).all():
        raise EquilibriumError("invalid labor-clearing coefficients")
    log_k1, log_k2 = np.log(k1), np.log(k2)
    upper = float((log_k1 - log_k2) / (b - a))

    def residual(log_y):
        return float(1 - np.exp(log_k2 - log_k1 + (b - a) * log_y)
                     - overhead * np.exp(-log_k1 - a * log_y))

    if overhead == 0:
        solution, iterations = upper, 0
    else:
        if a > 0:
            lower = float((np.log(a / b) + log_k1 - log_k2) / (b - a))
            if residual(lower) <= 0:
                raise EquilibriumError("overhead exceeds maximum available labor: no upper positive output root")
        else:
            lower = upper - 2
            for _ in range(n.root_max_iter):
                if residual(lower) > 0:
                    break
                lower -= 2
            else:
                raise EquilibriumError("could not bracket a positive output root")
        try:
            solution, info = brentq(residual, lower, upper, xtol=5e-15,
                                   rtol=4 * np.finfo(float).eps,
                                   maxiter=n.root_max_iter, full_output=True)
        except (RuntimeError, ValueError) as exc:
            raise EquilibriumError(f"aggregate output solver failed: {exc}") from exc
        iterations = info.iterations
    output = float(np.exp(solution))
    relative_residual = abs(residual(solution))
    if not np.isfinite(output) or output <= 0 or relative_residual > n.root_tol:
        raise EquilibriumError(f"output root residual {relative_residual:.3g} exceeds {n.root_tol:.3g}")
    return output, relative_residual, int(iterations)


def _solve_period(z_initial, u_initial, theta, eta, zeta, c, n, phi):
    z, u = z_initial.copy(), u_initial.copy()
    round_records = []
    for iteration in range(1, n.entry_max_iter + 1):
        active = z > 0
        counts = active.sum(axis=0)
        market_count = int(np.count_nonzero(counts))
        if market_count == 0:
            raise EquilibriumError("the entry algorithm removed every firm")
        s, mu, share = solve_shares(z, theta, eta, c.gamma, n)
        wc, p, demand, sum_part = _prices(z, active, s, mu, counts, market_count, theta, eta, c)
        if phi is None:
            demand_power = _power(demand, 1 / c.gamma, active)
            numerator = (mu - c.gamma) * c.varphibar * wc ** (c.varphi / c.alpha_cogs) * demand_power
            denominator = c.alpha_cogs * c.psi_cogs * u * _power(z, 1 / c.gamma, active) / c.psi_sga * sum_part + (mu - c.gamma) * demand_power * _sum_firms(u)
            gamma_values = numerator[active] / denominator[active]
            gamma_values.sort()
            if zeta < 1:
                cdf = np.cumsum(np.full(gamma_values.size, 1 / gamma_values.size))
                index = int(np.searchsorted(cdf, zeta, side="right"))
                if index == gamma_values.size:
                    raise EquilibriumError("strict overhead quantile has no support at this zeta")
                phi = float(gamma_values[index])
            else:
                phi = float(gamma_values[-1] * zeta)
            if not np.isfinite(phi) or phi < 0:
                raise EquilibriumError("the fixed labor phi is not finite and nonnegative")
        fixed_labor = phi * u
        overhead = _sum_firms(fixed_labor)
        output, root_residual, root_iterations = _solve_output(wc, market_count, sum_part, overhead, c, n)
        wage = float((wc / output ** (1 - c.gamma)) ** (1 / c.alpha_cogs))
        technology = z * (1 / c.psi_cogs) ** c.gamma * ((c.gamma - c.alpha_cogs) * wage / (c.alpha_cogs * c.r)) ** (c.gamma - c.alpha_cogs)
        y = demand * output / market_count
        labor = _power(y / np.where(active, technology, 1.0), 1 / c.gamma, active)
        supply = float(c.varphibar * wage**c.varphi)
        actual_production = _sum_firms(labor)
        labor_residual = float((actual_production + overhead - supply) / supply)
        profits = p * y - c.gamma * wage * labor / (c.alpha_cogs * c.psi_cogs) - wage * fixed_labor / c.psi_sga
        losses = profits[active & (profits <= 0)]
        threshold = float(np.partition(losses, int(np.floor(losses.size / 3)))[int(np.floor(losses.size / 3))]) if losses.size else 0.0
        drop = active & (profits <= threshold)
        dropped = int(drop.sum())
        record = {
            "iteration": iteration, "active_firms": int(active.sum()), "active_markets": market_count,
            "loss_firms": int(losses.size), "proposed_drop": dropped,
            "root_relative_residual": root_residual, "root_iterations": root_iterations,
            "labor_relative_residual": labor_residual,
            "max_share_stopping_residual": float(share["stopping_residual"].max()),
            "max_share_residual": float(share["returned_residual"].max()),
            "max_share_iterations": int(share["iterations"].max()),
        }
        round_records.append(record)
        if dropped < n.entry_drop_stop or iteration == n.entry_max_iter:
            reason = "proposed_drop_below_threshold" if dropped < n.entry_drop_stop else "iteration_limit"
            result = {"z": z, "u": u, "s": s, "mu": mu, "p": p, "y": y, "n": labor,
                      "phi": fixed_labor, "W": wage, "Y": output, "Ns": supply,
                      # Compatibility field. Independent accounting uses sum(n), above.
                      "Nprod": supply - overhead, "Njt": counts,
                      "share_iterations": share["iterations"]}
            if not all(np.isfinite(value).all() for value in result.values()):
                raise EquilibriumError("nonfinite final firm or aggregate quantities")
            diagnosis = {**record, "entry_iterations": iteration, "entry_rounds": iteration,
                         "entry_stop_reason": reason,
                         "entry_stopping_rule_met": reason != "iteration_limit",
                         "remaining_loss_firms": int(losses.size),
                         "actual_production_labor": actual_production,
                         "overhead_labor": overhead, "rounds": round_records}
            # The legacy diagnostic marks an iteration at the cap, even if
            # that very iteration first satisfied the convergence tolerance.
            err = np.array([(share["iterations"] >= n.share_max_iter).mean(),
                            share["iterations"].mean(), z.mean()])
            return result, phi, err, diagnosis
        z[drop], u[drop] = 0.0, 0.0
    raise AssertionError("entry loop must return or raise")


def solve_economy(
    x, config: ModelConfig | None = None, numerics: Numerics | None = None,
    draws: Mapping[str, np.ndarray] | None = None,
) -> dict:
    """Solve one economy and preserve firm identity across its two periods.

    x = (theta, eta, rho, sigma, potential firms, zeta). Potential firms are
    ``floor(x[4])`` per market.
    Each period begins with every potential firm; period 2 keeps period 1's
    fixed labor phi. Firm arrays are ``(M, J, 2)``. Moments are computed by the
    separate moments module. There is no parameter search in this function.
    """
    c, n = config or ModelConfig(), numerics or Numerics()
    parameters = np.asarray(x, dtype=np.float64)
    _validate(parameters, c, n)
    productivity, overhead, draw_source = build_productivity(parameters, c.markets, c.zbar, draws)
    theta, eta, _, _, _, zeta = parameters[:6]
    periods, diagnostics = [], []
    phi = None
    for t in range(2):
        period, phi, err, diagnosis = _solve_period(productivity[:, :, t], overhead, theta, eta, zeta, c, n, phi)
        periods.append(period)
        diagnostics.append(diagnosis)
    equi = {f"{key}_ijt": np.stack([period[key] for period in periods], axis=2)
            for key in ("phi", "mu", "z", "s", "y", "p", "u", "n")}
    equi.update({f"{key}_t": np.array([period[key] for period in periods])
                 for key in ("W", "Y", "Ns", "Nprod")})
    equi["Njt"] = np.stack([period["Njt"] for period in periods], axis=1)
    equi["share_iterations"] = np.stack([period["share_iterations"] for period in periods], axis=1)
    return {"equi": equi, "phi": phi, "err": err,
            "diagnostics": {"dtype": "float64", "draw_source": draw_source,
                            "config": asdict(c), "numerics": asdict(n),
                            "periods": diagnostics,
                            "entry_method": "sequential_exit_pre_exit_stop_no_reentry_test"}}
