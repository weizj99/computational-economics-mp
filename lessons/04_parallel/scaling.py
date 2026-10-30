"""Unit 04: time the same 256 economies with 1, 2, 4, ... worker processes.

The work is fixed: the first 256 candidates of the unit 03 search for the year
2000 (Sobol indices 0-255), each a full economy with 10,000 markets. Every
worker count starts a fresh pool of processes, and each worker uses one
linear-algebra thread. The clock runs from creating the pool until it has shut
down: start-up, draws, solving and writing each result are all inside it.
Every result must match unit 03's saved values within 1e-10, and every worker
count must give the same results as the first one.

Run from the repository root:
    python lessons/04_parallel/scaling.py --workers 1 2 4
Each worker count solves all 256 economies; one worker took about 19 minutes on
the machine used for the recorded runs. --cases 16 runs a quick version with
the first 16 economies.
"""
from __future__ import annotations

import os

# One linear-algebra thread per worker, set before NumPy loads.
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_name] = "1"

import argparse  # noqa: E402
from collections import OrderedDict  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
import csv  # noqa: E402
from dataclasses import asdict  # noqa: E402
import json  # noqa: E402
import multiprocessing as mp  # noqa: E402
from pathlib import Path  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "model"))

from qmp import ModelConfig, Numerics, generate_draws, simulate  # noqa: E402
from qmp.estimation import FIXED, MOMENT_NAMES, diagnostic_quality, read_inputs  # noqa: E402

CASES = Path(__file__).with_name("scaling_cases.csv")
FIELDS = (*MOMENT_NAMES, "phi", "Mbar", "loss")
TOLERANCE = 1e-10
_worker = {}


def read_cases(count):
    with CASES.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))[:count]
    return [{key: (int(value) if key in ("row_id", "sobol_index", "M") else float(value))
             for key, value in row.items()} for row in rows]


def physical_cores():
    """One logical CPU per physical core that this process may use (Linux only)."""
    cores = {}
    for cpu in sorted(os.sched_getaffinity(0)):
        topology = Path(f"/sys/devices/system/cpu/cpu{cpu}/topology")
        key = ((topology / "physical_package_id").read_text(), (topology / "core_id").read_text())
        cores.setdefault(key, cpu)
    return list(cores.values())


def start_worker(target, weights, trial_dir, pin_cpus, counter):
    with counter.get_lock():
        rank = counter.value
        counter.value += 1
    if pin_cpus:
        os.sched_setaffinity(0, {pin_cpus[rank]})
    # Each fresh worker starts with an empty cache of draws, as in the annual search.
    _worker.update(config=ModelConfig(), numerics=Numerics(), draws=OrderedDict(),
                   target=np.array(target), weights=np.array(weights), trial_dir=Path(trial_dir))


def solve_case(case):
    w = _worker
    M = case["M"]
    if M not in w["draws"]:
        w["draws"][M] = generate_draws(M, w["config"].markets, seed=100)
        if len(w["draws"]) > 4:
            w["draws"].popitem(last=False)
    w["draws"].move_to_end(M)
    x = [FIXED["theta"], FIXED["eta"], FIXED["rho"], case["sigma"], case["N"], case["zeta"]]
    result = simulate(x, config=w["config"], numerics=w["numerics"], draws=w["draws"][M])
    moments = np.array([result["moments"][name] for name in MOMENT_NAMES])
    record = {"row_id": case["row_id"], **dict(zip(MOMENT_NAMES, moments.tolist())),
              "phi": float(result["phi"]), "Mbar": float(np.mean(result["equi"]["Njt"][:, 0])),
              "loss": float(np.sum((moments - w["target"]) ** 2 * w["weights"])),
              "quality_passed": diagnostic_quality(result["diagnostics"], asdict(w["numerics"]))["passed"]}
    # Writing each result is part of the timed work, as in the recorded runs.
    (w["trial_dir"] / f"{case['row_id']}.json").write_text(json.dumps(record), encoding="utf-8")
    return record


def trial(cases, workers, target, weights, trial_dir, pin_cpus):
    trial_dir.mkdir(parents=True, exist_ok=False)
    context = mp.get_context("spawn")
    counter = context.Value("i", 0)
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers, mp_context=context, initializer=start_worker,
                             initargs=(target, weights, str(trial_dir), pin_cpus, counter)) as pool:
        records = list(pool.map(solve_case, cases))
    return time.perf_counter() - started, records


def largest_errors(records, reference):
    return {field: max(abs(r[field] - c[field]) for r, c in zip(records, reference)) for field in FIELDS}


def main(argv=None):
    available = os.cpu_count() or 1
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--workers", type=int, nargs="+",
                        default=[w for w in (1, 2, 4, 8, 16) if w <= available])
    parser.add_argument("--cases", type=int, default=256, help="use the first N of the 256 economies")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/scaling")
    parser.add_argument("--pin", action="store_true",
                        help="Linux: run each worker on its own physical core, as in the recorded runs")
    args = parser.parse_args(argv)
    if not 1 <= args.cases <= 256 or min(args.workers) < 1:
        parser.error("choose 1 to 256 cases and at least one worker")
    cases = read_cases(args.cases)
    targets, _, weights = read_inputs(ROOT / "data")
    pin_cpus = physical_cores() if args.pin else None
    if pin_cpus is not None and len(pin_cpus) < max(args.workers):
        parser.error(f"--pin needs {max(args.workers)} physical cores; this process may use {len(pin_cpus)}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows, first = [], None
    for workers in args.workers:
        trial_dir = args.output_dir / f"trial_w{workers:02d}_{time.strftime('%Y%m%d_%H%M%S')}"
        seconds, records = trial(cases, workers, targets[2000], weights, trial_dir, pin_cpus)
        saved = largest_errors(records, cases)
        same = largest_errors(records, first) if first else {field: 0.0 for field in FIELDS}
        passed = (all(r["quality_passed"] for r in records) and max(saved.values()) <= TOLERANCE
                  and max(same.values()) <= TOLERANCE)
        first = first or records
        rows.append({"workers": workers, "seconds": round(seconds, 3), "passed": passed,
                     "largest_difference_from_saved": max(saved.values()),
                     "largest_difference_from_first": max(same.values())})
        print(f"{workers:>2} workers: {seconds:8.1f} s   matches saved results: {passed}", flush=True)
    # Speed-up and efficiency are relative to the first worker count, usually 1.
    first_seconds, first_workers = rows[0]["seconds"], rows[0]["workers"]
    for row in rows:
        row["speedup"] = round(first_seconds / row["seconds"], 3)
        row["efficiency"] = round(row["speedup"] * first_workers / row["workers"], 3)
        row["worker_core_seconds"] = round(row["workers"] * row["seconds"], 1)
    with (args.output_dir / "timings.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved the timings to {args.output_dir / 'timings.csv'}")
    return 0 if all(row["passed"] for row in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
