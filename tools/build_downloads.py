"""Build the website's code downloads from the files in this repository.

Each package is a zip of repository files under their repository paths, with a
short README for its unit, so a command in the course works the same way in the
repository and in the unpacked package. The single-file downloads of units 00
and 01 are copies of the files in lessons/.

    python tools/build_downloads.py           write the downloads into 06_teaching
    python tools/build_downloads.py --check   report downloads that differ from the repository
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "06_teaching"
# Every entry gets this time stamp, so rebuilding unchanged files gives the same zip.
STAMP = (2026, 1, 1, 0, 0, 0)

COPIES = {
    "prerequisites/ab08.py": "lessons/00_prerequisites/ab08.py",
    "prerequisites/berry92.py": "lessons/00_prerequisites/berry92.py",
    "modules/01_gmm_smm/gmm_smm.py": "lessons/01_gmm_smm/gmm_smm.py",
    "modules/01_gmm_smm/exercise.md": "lessons/01_gmm_smm/exercise.md",
}

COMMON = ("LICENSE", "LICENSE-CONTENT", "NOTICE", "RIGHTS.md", "requirements-cpu.txt",
          "run.py", "07_python/pyproject.toml", "07_python/qmp", "07_python/tests", "data")

SETUP = """## Set up

You need Python 3.10 or later. Install NumPy and SciPy:

    python -m pip install -r requirements-cpu.txt
"""

CREDIT = """## Licence and credit

The code is under the Apache License 2.0 (LICENSE, NOTICE) and the text under
CC BY 4.0 (LICENSE-CONTENT). RIGHTS.md says how to credit the course, and
data/README.md lists the sources of the data.
"""

PACKAGES = {
    "02": {
        "zip": "modules/02_one_economy/assets/computational-economics-02.zip",
        "title": "Unit 02: Inside one economy",
        "lessons": ("02_",),
        "files": COMMON + ("lessons/02_one_economy",
                           "06_teaching/modules/02_one_economy/task11_gallery.json",
                           "06_teaching/modules/02_one_economy/assets/moment_steps_data.js"),
        "run": """## Run

Solve the economy that lesson 02.3 traces and compare it with the page, in
about ten seconds:

    python lessons/02_one_economy/parameters_to_moments.py

The script prints phi, the operating firms, the three moments, the employment
totals, one firm of Market 1 and Market 1's contributions, each next to the
value saved for the page in 06_teaching/modules/02_one_economy. All 25 lines
should match. The three moments should equal the saved values; on another
computer they can differ in the last digit. --case sigma_3 solves the next
point on the sigma path, and --firm 3 shows another firm of Market 1.

To solve an economy with parameters of your choice, use the course's CPU
solver. With 200 markets it takes about a second:

    python run.py cpu --markets 200 --output outputs/example_cpu

Each run saves the three moments, the firm arrays and the solver diagnostics.
`python run.py cpu --help` lists the settings you can change, and
`python run.py test` runs the tests.
""",
    },
    "03": {
        "zip": "modules/03_estimation/assets/computational-economics-03.zip",
        "title": "Unit 03: Estimating the economy",
        "lessons": ("03_",),
        "files": COMMON + ("lessons/03_estimation",
                           "06_teaching/modules/03_estimation/assets/search_results.csv"),
        "run": """## Run

Search one year as the full estimation does. The script maps the first 64 of
the course's 512 Sobol points into the search box for 2000, solves each
economy, and prints the lowest loss with its three contributions. It then
compares every economy with the saved candidate table that the website uses,
06_teaching/modules/03_estimation/assets/search_results.csv:

    python lessons/03_estimation/search_year.py --year 2000 --points 64

On the machine used for the course, one economy for 2000 took about 4.5
seconds on one core, so 64 points take about five minutes; --workers 4 solves
four economies at a time. Any year from 1980 to 2023 works, and --points 512
runs the whole year. The candidates go to outputs/search_2000/candidates.csv.

The full search solves 512 candidate economies for each year from 1980 to 2023,
22,528 in all: about 60 core-hours, most of them for the 1980s. This runs eight
shards side by side, which takes about eight hours with eight cores:

    python lessons/03_estimation/full_search.py --workers 8

It fixes the candidates and the inputs, solves the shards, and then chooses the
best candidate for each year (outputs/annual_run/annual_estimates.csv). Each
solved candidate is saved at once, so a stopped run carries on when you start it
again. Add --limit 2 for a quick test; an unfinished run marks its choice as
provisional. The three steps are also commands of their own, run from the
07_python folder: `python -m qmp.estimation prepare`, `solve` and `select`.
""",
    },
    "04": {
        "zip": "modules/04_parallel/assets/computational-economics-04.zip",
        "title": "Unit 04: Parallel computing and acceleration",
        "lessons": ("04_",),
        "files": COMMON + ("03_gpu", "08_gpu", "lessons/04_parallel", "tools/make_example_inputs.py",
                           "docs/GPU.md"),
        "run": """## Run

The CPU code needs only NumPy and SciPy. The GPU code also needs an NVIDIA GPU
and PyTorch with CUDA (and threadpoolctl for the GPU checks); docs/GPU.md
describes its entry points.

Time the same 256 economies with 1, 2 and 4 worker processes. Each worker
count solves all 256; one worker took about 19 minutes on the machine used for
the recorded runs. Add --cases 16 for a quick version:

    python lessons/04_parallel/scaling.py --workers 1 2 4

Time the market-share solver in one call and in one call per market, for 5
to 80 firms per market (lesson 02, about 30 seconds):

    python lessons/04_parallel/loop_vs_vectorized.py

Solve the output equations of unit 02's baseline economy with Newton's method
and bisection, and compare the roots with the model's (the extra exercise):

    python lessons/04_parallel/output_root.py

Check the GPU code against the CPU solver: the single-economy reference on 17
economies, the batched engine on 8, and the market-share block:

    python lessons/04_parallel/check_gpu.py

Solve one fixed economy on the GPU, or on both and compare:

    python lessons/04_parallel/gpu_economy.py --case candidate_000 --compare

Write two small example points, then solve them with the batched engine:

    python run.py example-inputs outputs/gpu_inputs
    python run.py gpu outputs/gpu_inputs/points.csv outputs/gpu_run --contract outputs/gpu_inputs/contract.json

The first run for a given number of potential firms compiles the GPU kernels,
so it is slower than later runs.
""",
    },
    "05": {
        "zip": "modules/05_untargeted/assets/computational-economics-05.zip",
        "title": "Unit 05: Untargeted moment",
        "lessons": ("05_",),
        "files": COMMON + ("lessons/05_untargeted",
                           "06_teaching/modules/03_estimation/assets/annual_parameters.csv"),
        "run": """## Run

The figure also needs Matplotlib:

    python -m pip install matplotlib

Solve the 44 annual economies again at the unit 03 estimates and split the
change in the markup. This takes about 18 core-minutes, or about 5 minutes
with four workers:

    python lessons/05_untargeted/decompose_markup.py --workers 4 --figure

The results go to outputs/untargeted. The unit 03 estimates are in
06_teaching/modules/03_estimation/assets/annual_parameters.csv. Check what the
script prints: the moments differ from unit 03's saved values by 0, the three
parts add up to within 1e-15, and 27 of the 43 pairs of years have new draws.
""",
    },
}


def tracked(paths):
    """Repository files under the given paths, as git tracks them."""
    listed = subprocess.run(["git", "ls-files", "-z", "--", *paths], cwd=ROOT,
                            check=True, capture_output=True).stdout.decode().split("\0")
    files = sorted(name for name in listed if name)
    missing = [p for p in paths if not any(f == p or f.startswith(p.rstrip("/") + "/") for f in files)]
    # A file on disk that git does not track (or ignores) would be left out silently.
    on_disk = {str(f.relative_to(ROOT)) for p in paths if (ROOT / p).is_dir() for f in (ROOT / p).rglob("*")
               if f.is_file() and "__pycache__" not in f.parts}
    missing += sorted(on_disk - set(files))
    if missing:
        raise SystemExit(f"not tracked by git: {', '.join(missing)}")
    return files


def reading_list(prefixes):
    """Lines that say where to read each lesson, from course_map.json."""
    lessons = json.loads((ROOT / "course_map.json").read_text(encoding="utf-8"))["lessons"]
    lines = []
    for lesson in lessons:
        if lesson["id"].startswith(prefixes):
            lines.append(f"- {lesson['title']}")
            for source in lesson["sources"]:
                symbols = f": {', '.join(source['symbols'])}" if source["symbols"] else ""
                lines.append(f"  {source['path']}{symbols}")
    return "\n".join(lines)


def readme(unit, spec):
    return "\n".join([
        f"# Computational Economics — {spec['title']}",
        "",
        f"The code and data for unit {unit}. Each file keeps its path in the course",
        "repository, https://github.com/weizj99/computational-economics-mp, so the",
        "commands in the course work here unchanged. Run them from this folder.",
        "",
        SETUP,
        spec["run"],
        "## Where to read",
        "",
        reading_list(spec["lessons"]),
        "",
        CREDIT,
    ])


def package(unit, spec):
    """Zip entries for one unit as {name: bytes}."""
    top = f"computational-economics-{unit}"
    entries = {f"{top}/{name}": (ROOT / name).read_bytes() for name in tracked(spec["files"])}
    entries[f"{top}/README.md"] = readme(unit, spec).encode("utf-8")
    return entries


def write_zip(path, entries):
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if name.endswith(".sh") else 0o644) << 16
            archive.writestr(info, entries[name])


def read_zip(path):
    with zipfile.ZipFile(path) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="compare the saved downloads with the repository; write nothing")
    args = parser.parse_args(argv)
    differ = []
    for site_name, source in COPIES.items():
        target, content = SITE / site_name, (ROOT / source).read_bytes()
        if args.check:
            if not target.exists() or target.read_bytes() != content:
                differ.append(site_name)
        else:
            target.write_bytes(content)
    for unit, spec in PACKAGES.items():
        target, entries = SITE / spec["zip"], package(unit, spec)
        if args.check:
            if not target.exists() or read_zip(target) != entries:
                differ.append(spec["zip"])
        else:
            write_zip(target, entries)
            print(f"{spec['zip']}: {len(entries)} files, {target.stat().st_size / 1024:.0f} KB")
    if args.check:
        print("\n".join(f"differs from the repository: {name}" for name in differ)
              or "Every download matches the repository.")
        return 1 if differ else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
