"""Unit 04, lesson 02: time a loop over markets against the vectorized solver.

Lesson 02 replaces a loop over markets with array operations on the whole
M x J productivity matrix. This script runs the course's share solver,
`qmp.equilibrium.solve_shares`, both ways on the same markets: once on all
markets together, and once market by market, one column per call. For each
number of potential firms M it prints the two times, the speedup and how far
apart the two answers are.

The loop pays a fixed cost in every call (Python, the input checks, many small
array operations), about the same for 5 firms as for 80. The vectorized call
pays it once for all markets, and its time grows with M. So the speedup falls
as M rises.

Run from the repository root (it needs NumPy and SciPy):
    python lessons/04_parallel/loop_vs_vectorized.py
It takes about a minute. --markets and --firms change the sizes.
"""
from __future__ import annotations

import os

# One linear-algebra thread, so that both versions use one core.
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import argparse  # noqa: E402
from pathlib import Path  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "model"))

from qmp import ModelConfig, generate_draws  # noqa: E402
from qmp.draws import build_productivity  # noqa: E402
from qmp.equilibrium import solve_shares  # noqa: E402
from qmp.estimation import FIXED  # noqa: E402

THETA, ETA = FIXED["theta"], FIXED["eta"]
GAMMA = ModelConfig().gamma
SIGMA, ZETA = 0.047041, 0.919212  # the centre of the year-2000 search box


def productivity(firms, markets, seed):
    """First-period productivity of every potential firm, shape (firms, markets)."""
    x = np.array([THETA, ETA, FIXED["rho"], SIGMA, float(firms), ZETA])
    z, _, _ = build_productivity(x, markets, ModelConfig().zbar, generate_draws(firms, markets, seed=seed))
    return z[:, :, 0]


def by_market(z):
    """The same solver, called once for each market."""
    shares, markups = np.empty_like(z), np.empty_like(z)
    iterations = np.empty(z.shape[1], dtype=np.int64)
    for j in range(z.shape[1]):
        s, mu, info = solve_shares(z[:, j:j + 1], THETA, ETA, GAMMA)
        shares[:, j], markups[:, j], iterations[j] = s[:, 0], mu[:, 0], info["iterations"][0]
    return shares, markups, iterations


def best_time(function, repeats):
    """The fastest of several runs, and the result of the last one."""
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = function()
        times.append(time.perf_counter() - start)
    return min(times), result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--markets", type=int, default=2000, help="markets J (default 2000)")
    parser.add_argument("--firms", type=int, nargs="+", default=[5, 10, 20, 40, 80],
                        help="potential firms per market M (default 5 10 20 40 80)")
    parser.add_argument("--seed", type=int, default=100)
    args = parser.parse_args(argv)

    print(f"Share solver on {args.markets:,} markets, all potential firms active, one thread")
    print(f"{'M':>4}  {'vectorized':>11}  {'loop':>9}  {'speedup':>8}  {'largest difference':>19}  same iterations")
    agree = True
    for firms in args.firms:
        z = productivity(firms, args.markets, args.seed)
        fast, (s, mu, info) = best_time(lambda: solve_shares(z, THETA, ETA, GAMMA), 3)
        slow, (s_loop, mu_loop, iterations) = best_time(lambda: by_market(z), 1)
        difference = max(np.abs(s - s_loop).max(), np.abs(mu - mu_loop).max())
        same = bool(np.array_equal(iterations, info["iterations"]))
        agree &= same and difference <= 1e-14
        print(f"{firms:>4}  {fast:>10.3f}s  {slow:>8.2f}s  {slow / fast:>7.0f}x  {difference:>19.1e}  {same}")
    print()
    print("Both versions give the same shares and markups up to rounding (at most 1e-14) "
          "and the same iterations in every market." if agree else
          "The two versions disagree by more than rounding: check the inputs.")
    return 0 if agree else 1


if __name__ == "__main__":
    raise SystemExit(main())
