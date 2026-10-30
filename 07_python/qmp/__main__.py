"""Solve one economy with freshly generated random draws; no other data is needed."""
import argparse
import csv
import json
from pathlib import Path
import time

import numpy as np

from . import ModelConfig, generate_draws, simulate


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--markets", type=int, default=10000)
    parser.add_argument("--firms", type=int, default=12, help="Potential firms per market")
    parser.add_argument("--sigma", type=float, default=0.06)
    parser.add_argument("--zeta", type=float, default=0.7)
    parser.add_argument("--seed", type=int, default=100)
    parser.add_argument("--output", type=Path, default=Path("single_economy_output"))
    args = parser.parse_args(argv)
    x = [1.13125, 4.36875, 0.9, args.sigma, args.firms, args.zeta]
    config = ModelConfig(markets=args.markets)
    started = time.perf_counter()
    draws = generate_draws(args.firms, args.markets, seed=args.seed)
    result = simulate(x, config=config, draws=draws)
    elapsed = time.perf_counter() - started
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / "moments.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["moment", "value"])
        for name, value in result["moments"].items():
            writer.writerow([name, format(value, ".17g")])
    np.savez_compressed(args.output / "equilibrium.npz", **result["equi"])
    summary = {
        "description": "Illustrative single economy, not an estimated calendar year",
        "parameters": x, "rng": "NumPy PCG64", "seed": args.seed,
        "moments": result["moments"], "fixed_labor_phi": result["phi"],
        "seconds_including_draws_and_moments": elapsed,
        "diagnostics": result["diagnostics"],
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Solved {args.markets:,} markets, two periods, in {elapsed:.2f}s.")
    for name, value in result["moments"].items():
        print(f"{name} = {value:.12g}")
    print(f"Saved three course moments, firm arrays, and diagnostics to {args.output.resolve()}")
    if not result["diagnostics"]["entry_stopping_rule_met"]:
        print("The entry iteration limit was reached; inspect summary.json before using the result.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
