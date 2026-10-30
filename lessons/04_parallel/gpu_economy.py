"""Unit 04: solve one fixed economy on the CPU, on a GPU, or on both and compare.

The GPU version is the single-economy reference in gpu/single_economy/qmp_gpu: the same
float64 algorithm with the firm and market arrays on a CUDA device. Both
versions use the same random numbers. With --compare, the script solves the
economy both ways and checks the agreement the course requires: moments and
loss-relevant values within 1e-10, continuous arrays within 1e-12 (or 1e-9
relative), and the same operating firms in every market.

Run from the repository root (the GPU needs CUDA-enabled PyTorch):
    python lessons/04_parallel/gpu_economy.py --case candidate_000 --compare
The cases are in gpu_cases.json.
"""
from __future__ import annotations

import os

for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_name] = "1"

import argparse  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
from pathlib import Path  # noqa: E402
import sys  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "model"), str(ROOT / "gpu/single_economy")]

import qmp  # noqa: E402
from qmp.estimation import FIXED  # noqa: E402

CASES = json.loads(Path(__file__).with_name("gpu_cases.json").read_text(encoding="utf-8"))


def case_inputs(case_id):
    case = next((c for c in CASES if c["id"] == case_id), None)
    if case is None:
        raise SystemExit(f"unknown case {case_id!r}; choose one from gpu_cases.json")
    x = [FIXED["theta"], FIXED["eta"], FIXED["rho"], case["sigma"], case["N"], case["zeta"]]
    M = math.floor(case["N"])
    config = qmp.ModelConfig()
    # The teaching baseline draws an 18-firm bank and keeps its first M rows.
    bank = case["draw_firms"] or M
    draws = qmp.generate_draws(bank, config.markets, seed=case["seed"])
    return x, {name: value[:M, :] for name, value in draws.items()}, config


def solve(case_id, backend):
    x, draws, config = case_inputs(case_id)
    if backend == "cpu":
        result = qmp.simulate(x, config=config, numerics=qmp.Numerics(), draws=draws)
        arrays = result["equi"]
    else:
        try:
            import torch
        except ImportError:
            raise SystemExit("The GPU backend needs PyTorch with CUDA; see docs/GPU.md.") from None
        import qmp_gpu
        torch.set_num_threads(1)
        result = qmp_gpu.simulate(x, config=config, numerics=qmp.Numerics(), draws=draws)
        arrays = {name: value.cpu().numpy() for name, value in result["equi"].items()}
    return {"moments": result["moments"], "phi": float(result["phi"]),
            "operating_firms_per_market": float(np.mean(arrays["Njt"][:, 0])), "arrays": arrays}


def compare(cpu, gpu):
    """Largest differences, and whether they meet the course's tolerances."""
    report = {"moments": max(abs(cpu["moments"][k] - gpu["moments"][k]) for k in cpu["moments"]),
              "phi": abs(cpu["phi"] - gpu["phi"]),
              "operating_sets_equal": bool(np.array_equal(cpu["arrays"]["Njt"], gpu["arrays"]["Njt"])
                                           and np.array_equal(cpu["arrays"]["z_ijt"] > 0, gpu["arrays"]["z_ijt"] > 0))}
    arrays_ok = True
    for name, value in cpu["arrays"].items():
        other = np.asarray(gpu["arrays"][name], dtype=np.float64)
        value = np.asarray(value, dtype=np.float64)
        gap = np.abs(value - other)
        report[f"array_{name}"] = float(gap.max()) if gap.size else 0.0
        # Share-iteration counts are reported, not required to match.
        if name != "share_iterations":
            arrays_ok &= bool(np.all(gap <= np.maximum(1e-12, 1e-9 * np.abs(value))))
    report["passed"] = (report["moments"] <= 1e-10 and report["phi"] <= max(1e-14, 1e-10 * abs(cpu["phi"]))
                        and report["operating_sets_equal"] and arrays_ok)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--case", default="teaching_2000_baseline")
    parser.add_argument("--backend", choices=("cpu", "gpu"), default="gpu")
    parser.add_argument("--compare", action="store_true", help="solve on the CPU and the GPU and compare")
    args = parser.parse_args(argv)
    if args.compare:
        report = compare(solve(args.case, "cpu"), solve(args.case, "gpu"))
        print(json.dumps({"case": args.case, **report}, indent=2))
        return 0 if report["passed"] else 1
    answer = solve(args.case, args.backend)
    answer.pop("arrays")
    print(json.dumps({"case": args.case, "backend": args.backend, **answer}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
