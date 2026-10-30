"""Unit 03: search one year as the full estimation does, and check every economy.

The script maps the first --points of the course's 512 Sobol points into the
year's search box, solves each candidate economy (10,000 markets, two periods),
scores it with the three weighted squared gaps and reports the lowest loss with
its three contributions. Every economy is then compared with unit 03's saved
candidate table, so the run either reproduces the website's numbers or shows
where it differs.

Run from the repository root (it needs NumPy and SciPy):
    python lessons/03_estimation/search_year.py --year 2000 --points 64
On the machine used for the course, one economy for 2000 took about 4.5 seconds
on one core, so 64 points take about five minutes; --workers 4 solves four at a
time. --points 512 runs the whole year. Economies in the 1980s have more
potential firms and take several times longer.
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

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "07_python"))

from qmp import ModelConfig, Numerics, generate_draws, simulate  # noqa: E402
from qmp.estimation import (FIXED, MOMENT_NAMES, RNG_CONTRACT, YEARS, diagnostic_quality,  # noqa: E402
                            make_points, rank_records, read_inputs)

SAVED = ROOT / "06_teaching/modules/03_estimation/assets/search_results.csv"
LABELS = ("Employment reallocation", "Sales-weighted markup", "SGA cost share")
COMPARED = ("phi", "Mbar", *MOMENT_NAMES, "loss")
TOLERANCE = 1e-10


def solve_candidate(point):
    """Solve one candidate with the estimation's settings and draws."""
    config, numerics = ModelConfig(), Numerics()
    started = time.perf_counter()
    try:
        # Every candidate with the same M uses the same draws (seed 100).
        draws = generate_draws(point["M"], config.markets, seed=RNG_CONTRACT["seed"])
        x = [FIXED["theta"], FIXED["eta"], FIXED["rho"], point["sigma"], point["N"], point["zeta"]]
        result = simulate(x, config=config, numerics=numerics, draws=draws)
    except Exception as exc:  # keep the failure as a record, as the full search does
        return {**point, "status": "failed", "error": f"{type(exc).__name__}: {exc}",
                "seconds": time.perf_counter() - started}
    quality = diagnostic_quality(result["diagnostics"], asdict(numerics))
    return {**point, "status": "ok" if quality["passed"] else "partial",
            "error": "; ".join(quality["issues"]),
            "phi": float(result["phi"]), "Mbar": float(np.mean(result["equi"]["Njt"][:, 0])),
            "moments": {name: float(result["moments"][name]) for name in MOMENT_NAMES},
            "seconds": time.perf_counter() - started}


def read_saved(path, year):
    """The saved candidates for one year, by row ID; None if the table is missing."""
    if not Path(path).is_file():
        return None
    with open(path, encoding="utf-8", newline="") as handle:
        return {int(row["row_id"]): row for row in csv.DictReader(handle) if int(row["year"]) == year}


def compare(records, saved):
    """Largest difference from the saved table, and the rows that do not match it."""
    largest, differing = 0.0, []
    for record in records:
        row = saved.get(record["row_id"])
        if record["status"] != "ok" or row is None:
            differing.append(record["row_id"])
            continue
        same_point = (all(float(row[key]) == record[key] for key in ("sigma", "N", "zeta"))
                      and int(row["M"]) == record["M"] and int(row["sobol_index"]) == record["sobol_index"])
        values = {"phi": record["phi"], "Mbar": record["Mbar"], "loss": record["loss"], **record["moments"]}
        gap = max(abs(values[key] - float(row[key])) for key in COMPARED)
        largest = max(largest, gap)
        if not same_point or gap > TOLERANCE:
            differing.append(record["row_id"])
    return largest, differing


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--year", type=int, default=2000, help="a year from 1980 to 2023")
    parser.add_argument("--points", type=int, default=64, help="use the first N of the year's 512 points")
    parser.add_argument("--workers", type=int, default=1, help="economies solved at the same time")
    parser.add_argument("--saved", type=Path, default=SAVED, help="saved candidate table to compare with")
    parser.add_argument("--output-dir", type=Path, help="default: outputs/search_YEAR")
    args = parser.parse_args(argv)
    if args.year not in YEARS or not 1 <= args.points <= 512 or args.workers < 1:
        parser.error("choose a year from 1980 to 2023, 1 to 512 points and at least one worker")
    output_dir = args.output_dir or ROOT / f"outputs/search_{args.year}"

    targets, boxes, weights = read_inputs(ROOT / "data")
    # make_points maps the course's Sobol points (standard_sobol_points) into each
    # year's box, in the same order and with the same row IDs as the full search.
    points = [p for p in make_points(boxes) if p["year"] == args.year][:args.points]
    print(f"Year {args.year}: solving {len(points)} of 512 candidates with {args.workers} worker(s).", flush=True)
    started, records = time.perf_counter(), []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for record in pool.map(solve_candidate, points):
            records.append(record)
            print(f"  {len(records):>3}/{len(points)}  row {record['row_id']}  M = {record['M']}  "
                  f"{record['seconds']:5.1f} s  {record['status']}", flush=True)
    seconds = time.perf_counter() - started

    ranked = rank_records(records, targets[args.year], weights)
    for loss, _, record in ranked:
        record["loss"] = loss
    print(f"Solved in {seconds:.0f} s; {len(ranked)} of {len(records)} economies passed the solver's checks.")
    if not ranked:
        return 1
    loss, row_id, best = ranked[0]
    target = np.array(targets[args.year])
    model = np.array([best["moments"][name] for name in MOMENT_NAMES])
    contributions = np.array(weights) * (model - target) ** 2
    print(f"\nLowest loss: row {row_id} (Sobol point {best['sobol_index']}), loss {loss:.6g}")
    print(f"  sigma {best['sigma']:.6g}   N {best['N']:.6g} (M = {best['M']})   zeta {best['zeta']:.6g}"
          f"   phi {best['phi']:.6g}")
    print(f"  {'Moment':<25}{'Model':>10}{'Target':>10}{'Weight':>11}{'Contribution':>14}")
    for row in zip(LABELS, model, target, weights, contributions):
        print("  {:<25}{:>10.5f}{:>10.5f}{:>11.6g}{:>14.6g}".format(*row))

    output_dir.mkdir(parents=True, exist_ok=True)
    fields = ["row_id", "year", "sobol_index", "sigma", "N", "M", "zeta", "status", "phi", "Mbar",
              *MOMENT_NAMES, "loss", "seconds", "error"]
    with open(output_dir / "candidates.csv", "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows({**record, **record.get("moments", {})} for record in records)
    print(f"\nSaved the candidates to {output_dir / 'candidates.csv'}")

    saved = read_saved(args.saved, args.year)
    if saved is None:
        print(f"No saved candidate table at {args.saved}; skipped the comparison.")
        return 0 if len(ranked) == len(records) else 1
    largest, differing = compare(records, saved)
    print(f"Compared with the saved candidates: {len(records) - len(differing)} of {len(records)} "
          f"economies match; largest difference {largest:.3g}.")
    if row_id in saved:
        print(f"In the saved search of all 512 points for {args.year}, row {row_id} has rank {saved[row_id]['rank']}.")
    if differing:
        print(f"Rows that do not match: {sorted(differing)}")
    return 0 if not differing else 1


if __name__ == "__main__":
    raise SystemExit(main())
