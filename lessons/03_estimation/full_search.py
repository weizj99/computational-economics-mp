"""Unit 03: run the full annual search on one computer, several shards at a time.

The search solves 512 candidates for each year from 1980 to 2023, 22,528
economies in all, about 60 core-hours on the machine used for the course, most
of them for the 1980s. The script fixes the candidates and inputs, starts one
solver process per shard, each with one linear-algebra thread, waits for all of
them, and then chooses the best candidate for each year. With eight workers the
search takes about eight hours. Every solved candidate is saved as soon as it is
done, so running the script again after a stop carries on where it left off.

Run from the repository root:
    python lessons/03_estimation/full_search.py --workers 8
--limit 2 solves only two candidates in each shard, as a quick test; the
choice of winners is then marked as provisional.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def estimation(*args):
    return [sys.executable, "-m", "qmp.estimation", *map(str, args)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--workers", type=int, default=os.cpu_count() or 1, help="shards solved at the same time")
    parser.add_argument("--run-dir", type=Path, default=ROOT/"outputs/annual_run")
    parser.add_argument("--data-dir", type=Path, default=ROOT/"data")
    parser.add_argument("--limit", type=int, help="solve at most this many candidates in each shard")
    args = parser.parse_args(argv)
    if args.workers < 1:
        parser.error("use at least one worker")
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(filter(None, [str(ROOT/"model"), os.environ.get("PYTHONPATH")])),
               OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    run_dir = args.run_dir.resolve()

    # 1. Fix the candidates and the inputs. On a second run this checks that nothing changed.
    subprocess.run(estimation("prepare", "--data-dir", args.data_dir.resolve(), "--run-dir", run_dir),
                   env=env, check=True)

    # 2. One process per shard. A shard holds every row whose row_id-1 leaves that remainder
    #    when divided by the number of shards, so the shards never share a row.
    (run_dir/"logs").mkdir(exist_ok=True)
    shards = []
    for index in range(args.workers):
        command = estimation("solve", "--run-dir", run_dir, "--shard-index", index, "--shard-count", args.workers)
        if args.limit:
            command += ["--limit", str(args.limit)]
        log = (run_dir/"logs"/f"shard_{index:03d}.log").open("w", encoding="utf-8")
        shards.append((index, subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT), log))
    print(f"Started {args.workers} shards; their progress is in {run_dir/'logs'}.", flush=True)
    failed = []
    for index, process, log in shards:
        if process.wait():
            failed.append(index)
        log.close()
    if failed:
        print(f"Shards {failed} reported failed or unfinished candidates; see their logs.")

    # 3. Only after every shard has stopped: check that each record is present, then choose.
    chosen = subprocess.run(estimation("select", "--run-dir", run_dir), env=env)
    print(f"Winners: {run_dir/'annual_estimates.csv'}; audit: {run_dir/'summary.json'}")
    return 1 if failed else chosen.returncode


if __name__ == "__main__":
    sys.exit(main())
