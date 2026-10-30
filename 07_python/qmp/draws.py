"""Reusable Gaussian shocks for a two-period economy.

Simulations use NumPy's PCG64 generator, so the same seed gives the same
draws. A caller can pass its own ``eps_z1`` and ``eps_z2`` arrays instead.
"""

from collections.abc import Mapping
import numpy as np


def generate_draws(firms: int, markets: int, seed: int = 100) -> dict[str, np.ndarray]:
    """Generate standard normals once so parameters can share random numbers.

    ``eps_z1`` sets period-1 productivity and ``eps_z2`` the innovation from
    period 1 to period 2. Both are float64 arrays of shape ``(firms, markets)``.
    """
    if int(firms) != firms or firms < 1 or int(markets) != markets or markets < 1:
        raise ValueError("firms and markets must be positive integers")
    rng = np.random.default_rng(seed)
    # The course's saved results first drew a (markets, 2) block and a
    # (firms, markets) block, for sector and permanent shocks that this model
    # does not have. Drawing and discarding them keeps eps_z1 and eps_z2
    # identical to those results.
    rng.standard_normal((int(markets), 2))
    rng.standard_normal((int(firms), int(markets)))
    return {
        "eps_z1": rng.standard_normal((int(firms), int(markets))),
        "eps_z2": rng.standard_normal((int(firms), int(markets))),
    }


def build_productivity(
    x: np.ndarray, markets: int, zbar: float,
    draws: Mapping[str, np.ndarray] | None = None,
) -> tuple[np.ndarray, np.ndarray, str]:
    """Return productivity ``(M,J,2)`` and overhead multipliers ``(M,J)``.

    Log productivity is an AR(1): period 1 is drawn from its stationary
    distribution and period 2 adds one innovation. The drift keeps mean
    productivity at ``zbar``. Every firm's overhead multiplier is one.
    """
    firms = int(np.floor(x[4]))
    source = "numpy_pcg64_seed_100" if draws is None else "injected_standard_normals"
    draw_map = generate_draws(firms, markets) if draws is None else draws

    def get(name: str, shape: tuple[int, ...]) -> np.ndarray:
        if name not in draw_map:
            raise ValueError(f"draws must contain {name!r} with shape {shape}")
        value = np.asarray(draw_map[name], dtype=np.float64)
        if value.shape != shape or not np.isfinite(value).all():
            raise ValueError(f"draws[{name!r}] must be finite with shape {shape}")
        return value

    eps1 = get("eps_z1", (firms, markets))
    eps2 = get("eps_z2", (firms, markets))
    rho, sigma = x[2:4]
    drift = -0.5 * sigma**2 / (1 + rho)
    log_z1 = drift / (1 - rho) + sigma / np.sqrt(1 - rho**2) * eps1
    log_z2 = rho * log_z1 + drift + sigma * eps2
    with np.errstate(over="ignore", under="ignore"):
        productivity = zbar * np.exp(np.stack((log_z1, log_z2), axis=2))
    if not np.isfinite(productivity).all() or np.any(productivity <= 0):
        raise ValueError("productivity overflowed or underflowed; reduce shock magnitudes")
    return productivity, np.ones((firms, markets)), source
