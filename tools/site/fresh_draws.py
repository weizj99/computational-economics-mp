"""Solve unit 03's 44 annual winners again with three new draws.

The page's optional check asks whether each year's fit holds when the economy is
simulated with random numbers the search never used. For every year the script
takes the winner in annual_parameters.csv and solves its economy with seeds 300,
301 and 302 instead of the search's seed 100. Nothing else changes: as in the
search, zeta picks the fixed labor phi from the new draws. The 132 economies go
to fresh_draws.csv in the unit's assets folder, one row per year and seed;
plot_estimation.py draws the page's figure from that table.

    python tools/site/fresh_draws.py --workers 4

On four cores it takes about a quarter of an hour; the 1980s economies have the
most potential firms and take longest.
"""
from __future__ import annotations

import os

# One linear-algebra thread per process, as in the saved estimation; with more
# threads the sales-weighted moments can change in the last digits.
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import argparse  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
import csv  # noqa: E402
from dataclasses import asdict  # noqa: E402
from pathlib import Path  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "model"))

from qmp import ModelConfig, Numerics, generate_draws, simulate  # noqa: E402
from qmp.estimation import FIXED, MOMENT_NAMES, diagnostic_quality  # noqa: E402

ASSETS = ROOT / "website/modules/03_estimation/assets"
SEEDS = (300, 301, 302)


def solve(task):
    """One winner on one new draw, with the estimation's settings."""
    winner, seed = task
    config, numerics = ModelConfig(), Numerics()
    started = time.perf_counter()
    draws = generate_draws(int(winner["M"]), config.markets, seed=seed)
    x = [FIXED["theta"], FIXED["eta"], FIXED["rho"], float(winner["sigma"]), float(winner["N"]),
         float(winner["zeta"])]
    result = simulate(x, config=config, numerics=numerics, draws=draws)
    quality = diagnostic_quality(result["diagnostics"], asdict(numerics))
    if not quality["passed"]:
        raise RuntimeError(f"{winner['year']}, seed {seed}: {'; '.join(quality['issues'])}")
    return {"year": int(winner["year"]), "seed": seed, "phi": float(result["phi"]),
            **{name: float(result["moments"][name]) for name in MOMENT_NAMES},
            "seconds": time.perf_counter() - started}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--workers", type=int, default=1, help="economies solved at the same time")
    args = parser.parse_args(argv)
    with open(ASSETS / "annual_parameters.csv", encoding="utf-8", newline="") as handle:
        winners = list(csv.DictReader(handle))
    assert len(winners) == 44
    # The largest economies first, so the workers finish together.
    tasks = sorted(((w, seed) for w in winners for seed in SEEDS), key=lambda t: -int(t[0]["M"]))
    rows, started = [], time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for row in pool.map(solve, tasks):
            rows.append(row)
            print(f"  {len(rows):>3}/{len(tasks)}  {row['year']}  seed {row['seed']}  {row['seconds']:5.1f} s",
                  flush=True)
    rows.sort(key=lambda r: (r["year"], r["seed"]))
    with open(ASSETS / "fresh_draws.csv", "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["year", "seed", "phi", *MOMENT_NAMES], lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: repr(value) if isinstance(value, float) else value
                          for key, value in row.items() if key != "seconds"} for row in rows)
    print(f"Solved {len(rows)} economies in {time.perf_counter() - started:.0f} s; wrote {ASSETS / 'fresh_draws.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
