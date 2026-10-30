# Computational Economics

**Course website:** <https://computational-economics.zhongjiwei.org/>

An independent Python teaching implementation of a two-period oligopoly economy,
based on [De Loecker, Eeckhout and Mongey (2026)](https://doi.org/10.21034/sr.688).
The lessons connect parameters, firm decisions and equilibrium outcomes to
moments, estimation and faster computation. They rebuild the model in
Python and estimate it on the paper's data. The course uses its own parameter
values, so its results can differ from the paper's. The lessons do not
represent the views of the paper's authors. **All errors are my own.**

The course has six units. Each unit has a web page with saved results, units
01–04 also have short videos, and each unit has a Python script that computes
the same numbers on your machine. It is not the original authors' replication
package.

## Open the course

The website is built from `06_teaching/`. To preview it on your computer, start
the local server from this folder:

```bash
python run.py serve --site-dir 06_teaching
```

Then open http://127.0.0.1:8765/ in your browser. The pages show saved results;
the scripts below compute them on your machine.

## Install

You need Python 3.10 or later. Install NumPy, SciPy and Matplotlib, then run
the tests, which take a few seconds:

```bash
python -m pip install -r requirements-teaching.txt
python run.py test
```

The model itself needs only NumPy and SciPy (`requirements-cpu.txt`). The GPU
code needs an NVIDIA GPU with CUDA-enabled PyTorch; see
[dependencies](docs/DEPENDENCIES.md) and [GPU usage](docs/GPU.md).

## Run each unit's example

Run the commands from this folder; the results go to `outputs/`. Times are
rough, for one core unless stated.

| Unit | Command | Time | What it does |
| --- | --- | --- | --- |
| 00 Prerequisite | `python lessons/00_prerequisites/ab08.py`<br>`python lessons/00_prerequisites/berry92.py` | seconds | Prices and markups from market shares; entry in a small market |
| 01 Moment Matching | `python lessons/01_gmm_smm/gmm_smm.py` | seconds | Estimates one parameter by GMM and SMM and prints the numbers on the page |
| 02 One Economy | `python lessons/02_one_economy/parameters_to_moments.py` | about 10 seconds | Solves the economy of lesson 02.3 with 10,000 markets and checks each number the page shows |
| 03 Estimation | `python lessons/03_estimation/search_year.py --year 2000 --points 64` | about 5 minutes | Solves 64 candidates for 2000, picks the lowest loss and checks every economy against the saved search |
| 04 Parallel Computing and Acceleration | `python lessons/04_parallel/scaling.py --cases 16` | about 4 minutes on 4 cores | Times 16 economies with 1, 2, 4, … workers and checks the results |
| 04, lesson 02 | `python lessons/04_parallel/loop_vs_vectorized.py` | about 30 seconds | Solves the market shares of 2,000 markets in one call and in one call per market, and compares the answers and the times |
| 04, extra exercise | `python lessons/04_parallel/output_root.py` | about 10 seconds | Solves the output equations of unit 02's baseline economy with Newton's method and bisection, and compares the roots with the model's |
| 04, on a GPU | `python lessons/04_parallel/check_gpu.py` | needs a GPU | Checks the GPU code against the CPU solver |
| 05 Untargeted Moment | `python lessons/05_untargeted/decompose_markup.py --workers 4` | about 5 minutes with 4 workers | Solves the 44 estimated economies again and splits the change in the markup |

`python run.py --help` lists the same commands. The full annual search of unit
03 solves 22,528 economies, about 60 core-hours:
`python lessons/03_estimation/full_search.py --workers 8` runs it in about eight
hours on eight cores. The [course map](docs/COURSE_MAP.md) lists which functions
to read for each lesson.

## Data

`data/` holds the three tables the course uses: the annual target moments and
the search boxes for unit 03, and the markup decomposition for unit 05.
[data/README.md](data/README.md) describes each column and its source.

## What is where

| Path | Contents |
| --- | --- |
| `06_teaching/` | The website: pages, saved results, figures, videos and the code downloads |
| `lessons/` | The scripts for each unit |
| `07_python/qmp/` | The model: one economy, its moments, the estimation and the markup decomposition |
| `07_python/tests/` | The tests that `python run.py test` runs |
| `03_gpu/`, `08_gpu/` | The batched GPU engine and the single-economy GPU version |
| `run.py` | Commands for the CPU and GPU solvers, the tests and the website preview |
| `data/` | The three data tables and their sources |
| `docs/` | Course map, GPU usage, dependencies, checks and the website |
| `tools/` | Maintenance scripts, such as the builder of the website's code downloads; `tools/site/` built the saved results of units 01–03 |

[What has been checked](docs/VALIDATION.md) lists the tests, the scripts that
reproduce the saved results exactly, and the GPU checks.

## Licence and credit

The code is licensed under the [Apache License 2.0](LICENSE) and the course
content under [CC BY 4.0](LICENSE-CONTENT). You may reuse and adapt both,
including commercially, if you keep the credit in [NOTICE](NOTICE). See
[licences and credit](RIGHTS.md) for what each licence covers, and
[CITATION.cff](CITATION.cff) for how to cite the course.
