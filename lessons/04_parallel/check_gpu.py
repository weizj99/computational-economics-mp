"""Unit 04: check the GPU code against the CPU solver on one machine.

Three checks, each against the NumPy solver on the same inputs:
1. the single-economy GPU reference (08_gpu) on the 17 fixed economies in
   gpu_cases.json, comparing moments, the fixed cost, every array and the
   operating firms;
2. the batched GPU engine (03_gpu) on the 8 timed economies, comparing the
   moments, the fixed cost and the mean number of operating firms;
3. the market-share block alone (gpu_share_check.py).

It needs an NVIDIA GPU with CUDA-enabled PyTorch, and threadpoolctl. Run from
the repository root:
    python lessons/04_parallel/check_gpu.py
The first batched solve for each number of potential firms compiles the GPU
kernels, so it takes longer than later ones.
"""
from __future__ import annotations

import os

for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_name] = "1"

import argparse  # noqa: E402
import math  # noqa: E402
from pathlib import Path  # noqa: E402
import sys  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "07_python"), str(ROOT / "03_gpu"), str(ROOT / "08_gpu")]

import gpu_economy  # noqa: E402
import gpu_share_check  # noqa: E402
import qmp  # noqa: E402
from qmp.estimation import FIXED, MOMENT_NAMES  # noqa: E402


def single_economies(cases):
    print("1. Single-economy GPU reference against the CPU solver")
    cpu_results, passed = {}, True
    for case in cases:
        cpu = gpu_economy.solve(case["id"], "cpu")
        report = gpu_economy.compare(cpu, gpu_economy.solve(case["id"], "gpu"))
        cpu_results[case["id"]] = cpu
        passed &= report["passed"]
        print(f"   {case['id']:<24} moments {report['moments']:.1e}  phi {report['phi']:.1e}  "
              f"same operating firms {report['operating_sets_equal']}  {'pass' if report['passed'] else 'FAIL'}")
    return passed, cpu_results


def batched_engine(cases, cpu_results):
    from qmp_torch_current import solve_batch_current
    print("2. Batched GPU engine against the CPU solver")
    config, passed = qmp.ModelConfig(), True
    by_m = {}
    for case in cases:
        by_m.setdefault(math.floor(case["N"]), []).append(case)
    for M, group in sorted(by_m.items()):
        x = np.array([[FIXED["theta"], FIXED["eta"], FIXED["rho"], c["sigma"], c["N"], c["zeta"]] for c in group])
        draws = qmp.generate_draws(M, config.markets, seed=100)
        answer = solve_batch_current(x, config=config, numerics=qmp.Numerics(), draws=draws)
        for row, case in enumerate(group):
            cpu = cpu_results[case["id"]]
            moments = max(abs(answer["moments"][row, k] - cpu["moments"][name]) for k, name in enumerate(MOMENT_NAMES))
            phi = abs(answer["phi"][row] - cpu["phi"])
            firms = abs(answer["Mbar"][row] - cpu["operating_firms_per_market"])
            ok = bool(answer["valid"][row]) and moments <= 1e-10 and phi <= max(1e-14, 1e-10 * cpu["phi"]) and firms == 0
            passed &= ok
            print(f"   {case['id']:<24} M={M:<3} moments {moments:.1e}  phi {phi:.1e}  "
                  f"operating firms {firms:.0e}  {'pass' if ok else 'FAIL'}")
    return passed


def share_block(output):
    print("3. Market-share block (gpu_share_check.py)")
    try:
        gpu_share_check.main(["--output", str(output)])
    except RuntimeError as exc:
        print(f"   FAIL: {exc}")
        return False
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/gpu_check")
    parser.add_argument("--cases", nargs="+", metavar="ID", help="check only these cases (default: all 17)")
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cases = [c for c in gpu_economy.CASES if not args.cases or c["id"] in args.cases]
    if args.cases and len(cases) != len(set(args.cases)):
        parser.error("unknown case; the ids are in gpu_cases.json")
    first, cpu_results = single_economies(cases)
    second = batched_engine([c for c in cases if c["timed"]], cpu_results)
    third = share_block(args.output_dir / "gpu_share_check.json")
    passed = first and second and third
    print("All GPU checks passed." if passed else "Some GPU checks FAILED; see the lines marked FAIL.")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
