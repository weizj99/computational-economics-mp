"""Unit 05: test the estimated model on a moment it was not fitted to.

Solve each year's economy again at the parameters selected in unit 03, split
the year-to-year change in the sales-weighted markup into within-firm change,
reallocation and net entry, and compare the cumulated parts with the data.

Run from the repository root:
    python lessons/05_untargeted/decompose_markup.py --workers 4 --figure
It needs NumPy and SciPy; --figure also needs Matplotlib. The 44 economies take
about 18 core-minutes on the machine used for the course.
"""
from __future__ import annotations

import argparse
import csv
from concurrent.futures import ProcessPoolExecutor
import json
import math
import os
from pathlib import Path
import sys
import time

# One linear-algebra thread per process, as in the unit 03 estimation. With
# more threads, the sales-weighted sums can change in the last digits, and the
# moments no longer match the saved ones exactly. Set before NumPy loads.
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "07_python"))

from qmp import ModelConfig, Numerics, generate_draws, simulate  # noqa: E402
from qmp.estimation import FIXED, MOMENT_NAMES, RNG_CONTRACT  # noqa: E402
from qmp.untargeted import centred_moving_average, markup_decomposition  # noqa: E402

PARAMETERS = ROOT / "06_teaching/modules/03_estimation/assets/annual_parameters.csv"
DATA = ROOT / "data/Untargeted_Moment.csv"
PARTS = ("total", "within", "reallocation", "net_entry")
DATA_COLUMNS = {"total": "markup_total", "within": "markup_within",
                "reallocation": "markup_reallocation", "net_entry": "markup_netentry"}
FIRM_ARRAYS = ("mu_ijt", "s_ijt", "p_ijt", "y_ijt")


def solve_year(row):
    """Solve one year at its selected parameters with the estimation's draws."""
    config, numerics = ModelConfig(), Numerics()
    M = int(math.floor(row["N"]))
    draws = generate_draws(M, config.markets, seed=RNG_CONTRACT["seed"])
    x = [FIXED["theta"], FIXED["eta"], FIXED["rho"], row["sigma"], row["N"], row["zeta"]]
    started = time.perf_counter()
    result = simulate(x, config=config, numerics=numerics, draws=draws)
    return {
        "year": row["year"], "M": M, "seconds": time.perf_counter() - started,
        "moments": {name: float(result["moments"][name]) for name in MOMENT_NAMES},
        "entry_stopping_rule_met": bool(result["diagnostics"]["entry_stopping_rule_met"]),
        # Only period 1 enters the decomposition.
        "firms": {name: result["equi"][name][:, :, :1].copy() for name in FIRM_ARRAYS},
    }


def read_rows(path, numeric):
    with open(path, encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [{key: (int(value) if key == "year" else float(value)) for key, value in row.items()
             if key == "year" or key in numeric} for row in rows]


def levels(start, changes):
    """Cumulate yearly changes from a starting level; the first year has none."""
    return start + np.concatenate(([0.], np.cumsum(changes[1:])))


def decompose(parameters, data, workers):
    """Return one row per year: the decomposition, cumulated levels and checks."""
    with ProcessPoolExecutor(max_workers=workers) as pool:
        solved = sorted(pool.map(solve_year, parameters), key=lambda item: item["year"])
    years = [item["year"] for item in solved]
    if years != list(range(years[0], years[0] + len(years))):
        raise ValueError("parameters must cover consecutive years")
    rows = [{"year": item["year"], "M": item["M"], "same_firms_as_previous_year": "",
             "mu_bar": math.nan, **{part: math.nan for part in PARTS},
             "share": math.nan, "cross": math.nan, "error": math.nan} for item in solved]
    for previous, current, row, before in zip(solved, solved[1:], rows[1:], rows):
        parts = markup_decomposition(previous["firms"], current["firms"])
        row.update({key: parts[key] for key in (*PARTS, "share", "cross", "error")})
        # Slot (i, j) holds the same firm only when both years use the same draws.
        row["same_firms_as_previous_year"] = int(previous["M"] == current["M"])
        before["mu_bar"], row["mu_bar"] = parts["mu_bar"]

    data_by_year = {row["year"]: row for row in data}
    model_levels = {part: levels(rows[0]["mu_bar"], np.array([row[part] for row in rows])) for part in PARTS}
    data_levels = {part: np.array([data_by_year[y][DATA_COLUMNS[part]] for y in years]) for part in PARTS}
    model_ma = {part: centred_moving_average(model_levels[part]) for part in PARTS}
    data_ma = {part: centred_moving_average(data_levels[part]) for part in PARTS}
    shift = data_ma["total"][0] - model_ma["total"][0]
    for i, row in enumerate(rows):
        for part in PARTS:
            row[f"model_{part}"] = model_levels[part][i]
            row[f"model_{part}_ma"] = model_ma[part][i]
            row[f"data_{part}"] = data_levels[part][i]
            row[f"data_{part}_ma"] = data_ma[part][i]
            row[f"moved_model_{part}_ma"] = model_ma[part][i] + shift

    saved = {row["year"]: row for row in parameters}
    moment_gap = max(abs(item["moments"][name] - saved[item["year"]][name])
                     for item in solved for name in MOMENT_NAMES if name in saved[item["year"]])
    summary = {
        "years": [years[0], years[-1]],
        "economies_solved": len(solved),
        "entry_stopping_rule_met_every_year": all(item["entry_stopping_rule_met"] for item in solved),
        "largest_moment_difference_from_unit_03": moment_gap,
        "largest_adding_up_error": max(abs(row["error"]) for row in rows[1:]),
        "pairs_with_new_draws": [row["year"] for row in rows[1:] if not row["same_firms_as_previous_year"]],
        "model_markup_1980_2023": [rows[0]["mu_bar"], rows[-1]["mu_bar"]],
        "moved_to_data_1980_moving_average": data_ma["total"][0],
        "solve_seconds": {str(item["year"]): round(item["seconds"], 2) for item in solved},
    }
    return rows, summary


def write_csv(rows, path):
    fields = list(rows[0])
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: (format(value, ".12g") if isinstance(value, float) else value)
                             for key, value in row.items()})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--parameters", type=Path, default=PARAMETERS,
                        help="one row per year with year, sigma, N and zeta (default: unit 03's selection)")
    parser.add_argument("--data", type=Path, default=DATA, help="the data decomposition by year")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/untargeted")
    parser.add_argument("--workers", type=int, default=1, help="economies solved at the same time")
    parser.add_argument("--figure", action="store_true", help="also draw the three-panel figure")
    args = parser.parse_args(argv)

    numeric = {"sigma", "N", "zeta", *MOMENT_NAMES}
    parameters = read_rows(args.parameters, numeric)
    data = read_rows(args.data, set(DATA_COLUMNS.values()))
    started = time.perf_counter()
    rows, summary = decompose(parameters, data, max(1, args.workers))
    summary["wall_seconds"] = round(time.perf_counter() - started, 1)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(rows, args.output_dir / "markup_decomposition.csv")
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Solved {summary['economies_solved']} economies in {summary['wall_seconds']} s.")
    print(f"Largest difference from unit 03's saved moments: {summary['largest_moment_difference_from_unit_03']:.3g}")
    print(f"Largest adding-up error: {summary['largest_adding_up_error']:.3g}")
    print(f"Years whose firms are new draws: {len(summary['pairs_with_new_draws'])} of {len(rows) - 1}")
    if args.figure:
        from draw_figure import draw
        draw(rows, args.output_dir)
    print(f"Saved results to {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
