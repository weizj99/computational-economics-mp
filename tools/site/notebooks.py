"""Write the Colab notebooks in notebooks/ and the "Run in Colab" button of each unit page.

Each unit has one notebook. Its first cell fetches the course code from the
public repository when the notebook runs in Google Colab, and does nothing of
the kind on a computer that already has the repository; the other cells run the
unit's scripts, the same commands as on the unit's page. The button on each
unit page and the badge at the top of each notebook open the notebook in Colab
from the branch in docs/project_links.json. A button that is already on a page
keeps its place and only gets the new markup; a new one goes after the page's
source note. The check also reports a README without a badge for each notebook.

    python tools/site/notebooks.py           write the notebooks and the buttons
    python tools/site/notebooks.py --check   report notebooks or pages that are out of date
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source_links import ROOT, repository  # noqa: E402

SITE = ROOT / "website"
FOLDER = "notebooks"
BADGE = "https://colab.research.google.com/assets/colab-badge.svg"
CSS = "assets/colab-launch.css"
BUTTON = re.compile(r'<a class="colab-launch" data-colab="(?P<id>[^"]+)".*?</a>', re.S)
NOTE = re.compile(r'<p class="[^"]*\bcourse-source-note\b[^"]*">.*?</p>', re.S)
# The Colab mark, drawn here: two open rings.
MARK = ('<svg viewBox="0 0 48 32" width="48" height="32" focusable="false">'
        '<path d="M20.6 9.4A10 10 0 1 0 20.6 22.6" fill="none" stroke="#f9ab00" stroke-width="5.2" '
        'stroke-linecap="round"/>'
        '<path d="M27.4 9.4A10 10 0 1 1 27.4 22.6" fill="none" stroke="#e8710a" stroke-width="5.2" '
        'stroke-linecap="round"/></svg>')

SETUP = '''\
# Set up. In Colab this fetches the course code; on your own computer it uses
# the copy of the repository that this notebook is in.
import os
from pathlib import Path
import subprocess
import sys

REPOSITORY = "{repository}"
if "google.colab" in sys.modules:
    folder = Path("/content") / REPOSITORY.rsplit("/", 1)[-1]
    if not (folder / "run.py").exists():
        subprocess.run(["git", "clone", "--quiet", "--depth", "1", "--branch", "{branch}", REPOSITORY, str(folder)],
                       check=True)
    os.chdir(folder)
    subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "-r", "requirements-teaching.txt"], check=True)
else:
    folder = Path.cwd().resolve()
    while not (folder / "run.py").exists() and folder != folder.parent:
        folder = folder.parent
    if not (folder / "run.py").exists():
        raise SystemExit("Open this notebook in Colab, or from inside the course repository.")
    os.chdir(folder)


def run(*command):
    """Run a course script with this notebook's Python and show its output as it comes."""
    process = subprocess.Popen([sys.executable, *command], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, env={{**os.environ, "PYTHONUNBUFFERED": "1"}})
    for line in process.stdout:
        print(line, end="")
    if process.wait():
        raise RuntimeError(f"{{command[0]}} stopped with exit code {{process.returncode}}")


print("Course code in", Path.cwd())'''

GPU_FIND = '''\
# Look for a GPU, then solve one economy on the CPU and on the GPU and compare.
# The search runs in a separate process, so a missing or broken PyTorch only prints a message.
probe = subprocess.run([sys.executable, "-c", "import torch; print(torch.cuda.get_device_name(0) "
                        "if torch.cuda.is_available() else '')"], capture_output=True, text=True)
gpu = probe.stdout.strip() if probe.returncode == 0 else None
if probe.returncode != 0:
    print("PyTorch could not be loaded, so the GPU cells are skipped.\\n"
          "Install a CUDA build of PyTorch to run them, or use Colab.")
elif not gpu:
    print("No GPU found, so the GPU cells are skipped. The CPU cells above do not need one.\\n"
          "In Colab: Runtime > Change runtime type > T4 GPU, then run the first cell and this one again.")
else:
    subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "threadpoolctl"], check=True)
    print("GPU:", gpu)
    run("lessons/04_parallel/gpu_economy.py", "--case", "candidate_000", "--compare")'''

GPU_ALL = '''\
# All three GPU checks, if the cell above found a GPU.
if gpu:
    run("lessons/04_parallel/check_gpu.py")
else:
    print("No GPU, so the GPU checks are skipped.")'''


LINKS = json.loads((ROOT / "docs/project_links.json").read_text(encoding="utf-8"))
BASE, BRANCH = repository()


def site(page):
    """A page of the course website."""
    return LINKS["site_url"].rstrip("/") + "/" + page.replace("index.html", "")


def code(path):
    """A file of the repository on GitHub."""
    return f"{BASE}/blob/{BRANCH}/{path}"


UNITS = [
    {
        "id": "00",
        "notebook": "00_prerequisites.ipynb",
        "title": "Prerequisites: market shares and entry",
        "pages": ["prerequisites/ab08.html", "prerequisites/berry92.html"],
        "button": "Both prerequisite examples, in your browser. Nothing to install.",
        "intro": "This notebook runs the examples of the two prerequisite pages, "
                 f"[market shares and markups]({site('prerequisites/ab08.html')}) and "
                 f"[entry and market structure]({site('prerequisites/berry92.html')}).",
        "cells": [
            ("markdown", "## Market shares and markups\n\nThe page's default sector, first under Cournot and then "
                         "under Bertrand conduct. It takes under a second. Compare the output with "
                         "“Check your result” on the page."),
            ("code", 'run("lessons/00_prerequisites/ab08.py")'),
            ("markdown", "## Entry and market structure\n\nAll 16 sets of the four firms at δ = 1: the sets "
                         "that pass the deviation tests and the set that ranking by profitability chooses."),
            ("code", 'run("lessons/00_prerequisites/berry92.py")'),
        ],
    },
    {
        "id": "01",
        "notebook": "01_gmm_smm.ipynb",
        "title": "Unit 01: Moment matching, GMM and SMM",
        "pages": ["modules/01_gmm_smm/index.html"],
        "button": "This unit’s code, in your browser. Nothing to install.",
        "intro": f"This notebook runs the experiment of [unit 01]({site('modules/01_gmm_smm/index.html')}).",
        "cells": [
            ("markdown", "## Run the experiment\n\nThe script estimates σ<sub>A</sub> by GMM and SMM, repeats "
                         "the estimation on 1,000 new samples and prints the numbers on the page. It takes about "
                         "a second. Compare the output with “Check your result” on the page; "
                         f"[the six exercises]({code('lessons/01_gmm_smm/exercise.md')}) take the same steps one at a "
                         "time."),
            ("code", 'run("lessons/01_gmm_smm/gmm_smm.py")'),
        ],
    },
    {
        "id": "02",
        "notebook": "02_one_economy.ipynb",
        "title": "Unit 02: Inside one economy",
        "pages": ["modules/02_one_economy/index.html"],
        "button": "This unit’s code, in your browser. Nothing to install.",
        "intro": "This notebook solves the economy of lesson 02.3 in "
                 f"[unit 02]({site('modules/02_one_economy/index.html')}).",
        "cells": [
            ("markdown", "## Solve the baseline economy\n\nThe baseline economy with the page's random draws, "
                         "10,000 markets and two periods. Next to each number the script says whether the page "
                         "shows the same value; all 25 lines should say “same”. It takes about "
                         "ten seconds."),
            ("code", 'run("lessons/02_one_economy/parameters_to_moments.py")'),
            ("markdown", "## The next point on the σ path\n\nThe same economy with the next value of "
                         "σ. Add `\"--firm\", \"3\"` to follow another firm of Market 1."),
            ("code", 'run("lessons/02_one_economy/parameters_to_moments.py", "--case", "sigma_3")'),
        ],
    },
    {
        "id": "03",
        "notebook": "03_estimation.ipynb",
        "title": "Unit 03: Estimating the economy",
        "pages": ["modules/03_estimation/index.html"],
        "button": "This unit’s code, in your browser. Nothing to install.",
        "intro": "This notebook searches 64 candidates for 2000, as in "
                 f"[unit 03]({site('modules/03_estimation/index.html')}).",
        "cells": [
            ("markdown", "## Search 64 candidates for 2000\n\nThe script solves the first 64 of the 512 Sobol "
                         "points for 2000, prints the lowest loss and compares every economy with the saved "
                         "search on the page. One economy takes about 4.5 seconds on one core; the cell solves "
                         "as many at a time as the machine has cores. Compare the output with “Check your "
                         "result” on the page."),
            ("code", 'run("lessons/03_estimation/search_year.py", "--year", "2000", "--points", "64",\n'
                     '    "--workers", str(os.cpu_count()))'),
        ],
    },
    {
        "id": "04",
        "notebook": "04_parallel.ipynb",
        "title": "Unit 04: Parallel computing and acceleration",
        "pages": ["modules/04_parallel/index.html"],
        "button": "CPU and GPU code, in your browser. Nothing to install.",
        "intro": "This notebook runs the CPU and GPU code of "
                 f"[unit 04]({site('modules/04_parallel/index.html')}). The CPU cells run on any machine; "
                 "the GPU cells need an NVIDIA GPU. In Colab, choose one under Runtime > Change runtime type "
                 "(T4 GPU) before you start, or run the CPU cells first and switch later.",
        "cells": [
            ("markdown", "## Time the CPU workers\n\nThe first 16 of unit 03's timed economies, solved with "
                         "1, 2, 4, … worker processes up to the number of cores. Every line should end with "
                         "“matches saved results: True”. On four cores it takes about four minutes."),
            ("code", 'run("lessons/04_parallel/scaling.py", "--cases", "16")'),
            ("markdown", "## Lesson 02: one call or one call per market\n\nThe market shares of 2,000 markets, "
                         "solved in one call and in one call per market. It takes about 30 seconds."),
            ("code", 'run("lessons/04_parallel/loop_vs_vectorized.py")'),
            ("markdown", "## Extra exercise: the output equations\n\nNewton's method and bisection on the "
                         "output equations of unit 02's baseline economy. It takes about ten seconds."),
            ("code", 'run("lessons/04_parallel/output_root.py")'),
            ("markdown", "## On a GPU\n\nThe next cell looks for a GPU. If it finds one, it solves one economy "
                         "on the CPU and on the GPU and compares the two; `\"passed\": true` means they agree. "
                         "The first GPU solve compiles the kernels, so it takes longer than later ones."),
            ("code", GPU_FIND),
            ("markdown", "The last cell runs all three GPU checks against the CPU solver: 17 economies on the "
                         "single-economy GPU code, 8 on the batched engine and the market-share block. Its "
                         "last line should read “All GPU checks passed.” It takes several minutes."),
            ("code", GPU_ALL),
        ],
    },
]


def colab(base, branch, notebook):
    owner_repo = base.removeprefix("https://github.com/")
    return f"https://colab.research.google.com/github/{owner_repo}/blob/{branch}/{FOLDER}/{notebook}"


def lines(text):
    rows = text.split("\n")
    return [row + "\n" for row in rows[:-1]] + [rows[-1]]


def notebook(unit, base, branch):
    head = (f"# {unit['title']}\n\n"
            f"[![Open in Colab]({BADGE})]({colab(base, branch, unit['notebook'])})\n\n"
            f"{unit['intro']}\n\n"
            "Run the cells from top to bottom. The first cell fetches the course code when the notebook runs "
            "in Google Colab; on your own computer it uses the repository the notebook is in.")
    cells = [("markdown", head), ("code", SETUP.format(repository=base, branch=branch)), *unit["cells"]]
    out = []
    for number, (kind, text) in enumerate(cells):
        cell = {"cell_type": kind, "id": f"cell-{number:02d}", "metadata": {}, "source": lines(text)}
        if kind == "code":
            cell.update(execution_count=None, outputs=[])
        out.append(cell)
    document = {"cells": out,
                "metadata": {"colab": {"provenance": []},
                             "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                             "language_info": {"name": "python"}},
                "nbformat": 4, "nbformat_minor": 5}
    return json.dumps(document, indent=1, ensure_ascii=False) + "\n"


def button(unit, base, branch):
    return (f'<a class="colab-launch" data-colab="{unit["id"]}" href="{colab(base, branch, unit["notebook"])}">'
            f'<span class="colab-launch-mark" aria-hidden="true">{MARK}</span>'
            f'<span class="colab-launch-text"><strong>Run this {"page" if unit["id"] == "00" else "unit"} '
            f'in Google Colab</strong><small>{unit["button"]}</small></span>'
            '<span class="colab-launch-arrow" aria-hidden="true">↗</span></a>')


def page(text, unit, base, branch, path):
    new = button(unit, base, branch)
    found = [m for m in BUTTON.finditer(text) if m.group("id") == unit["id"]]
    if len(found) > 1:
        raise SystemExit(f"{path}: {len(found)} Colab buttons for unit {unit['id']}")
    if found:
        text = text[:found[0].start()] + new + text[found[0].end():]
    else:
        note = NOTE.search(text)
        if not note:
            raise SystemExit(f"{path}: no source note to place the Colab button after")
        text = text[:note.end()] + new + text[note.end():]
    # Each page loads the button's style after the shared typography.
    depth = path.count("/")
    link = f'<link rel="stylesheet" href="{"../" * depth}{CSS}">'
    if link not in text:
        anchor = re.search(r'<link rel="stylesheet" href="(?:\.\./)*assets/typography\.css">', text)
        if not anchor:
            raise SystemExit(f"{path}: no typography stylesheet to place the Colab stylesheet after")
        text = text[:anchor.end()] + "\n  " + link + text[anchor.end():]
    return text


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report out-of-date files and change nothing")
    args = parser.parse_args(argv)
    base, branch = BASE, BRANCH
    wanted = {}
    for unit in UNITS:
        wanted[ROOT / FOLDER / unit["notebook"]] = notebook(unit, base, branch)
        for name in unit["pages"]:
            path = SITE / name
            current = wanted.get(path, path.read_bytes().decode("utf-8"))
            wanted[path] = page(current, unit, base, branch, name)
    stale = [path for path, text in wanted.items()
             if not path.exists() or path.read_bytes() != text.encode("utf-8")]
    readme = (ROOT / "README.md").read_bytes().decode("utf-8")
    missing = [unit["notebook"] for unit in UNITS if colab(base, branch, unit["notebook"]) not in readme]
    if args.check:
        for path in stale:
            print(f"out of date: {path.relative_to(ROOT).as_posix()}")
        for name in missing:
            print(f"README.md has no Colab badge for {FOLDER}/{name}")
        if stale or missing:
            return 1
        print(f"{len(UNITS)} notebooks and their page buttons are up to date.")
        return 0
    for path in stale:
        path.parent.mkdir(parents=True, exist_ok=True)
        # Keep each page's line endings: pages are stored byte for byte.
        path.write_bytes(wanted[path].encode("utf-8"))
        print(f"wrote {path.relative_to(ROOT).as_posix()}")
    for name in missing:
        print(f"add a Colab badge for {FOLDER}/{name} to README.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
