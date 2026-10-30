# Current GPU entrypoints

`03_gpu/qmp_torch.py::solve_batch_current` connects the grouped batch engine to
the CPU solver's settings and checks through `qmp_torch_current.py`. Parameter points with the same
`floor(N)` share a batch shaped `(B, M, J)`; completed economies leave the active
batch. Each economy retains its own parameters and stopping state.

The portable wrapper calls `run_points_current.main` directly:

```bash
python run.py gpu points.csv outputs/current --contract contract.json
```

The CSV accepts `row_id,year,sigma,N,zeta`, or `row_id,year,x0,...,x5` for the
full parameter vector. A contract contains `model_config` and `numerics` from
the CPU dataclasses. `python run.py example-inputs outputs/example_inputs`
creates two small example points with 200 markets and the default numerical
settings. The annual targets and search boxes are in `data/`.

The current CLI accepts `--contract`, `--cells`, `--seed` and `--device`; it
does not expose mixed or resident switches. Output records and checkpoints
keep fingerprints of the inputs, the settings and the source code, and record
every failure.

## The first run compiles

`@torch.compile` marks the functions that do most of the batched engine's array
work, in `03_gpu/qmp_torch.py` and `qmp_torch_current.py`. It merges the lines
of each function into a few GPU programs, so the GPU reads and writes each array
fewer times. PyTorch builds these programs the first time the functions run, and
again for each new M (the number of potential firms), market count or
precision. The number of points in a batch can change without a new build.

The first batch for each M therefore takes longer than the batches after it.
This is normal. The `seconds` that `run.py gpu` prints for that batch include
the compile time. In `check_gpu.py` the wait falls in the second check, the
batched engine, whose eight economies use four values of M.

On its first run, Triton, the GPU compiler that `torch.compile` uses, also
builds a small C helper with the machine's C compiler. It needs `gcc` or
`clang` and Python's header files: conda's Python includes them, and for
Ubuntu's system Python you install `python3-dev`. The compiler may print a few
notes; they do no harm.

Warm up before you time anything: run each M once outside the clock, then time
the repeats. Lesson 08 of unit 04, Fair comparison, keeps preparation and
compilation outside the clock in the same way.

PyTorch saves the compiled programs on disk. Two environment variables name the
folders: `TORCHINDUCTOR_CACHE_DIR` for the code that PyTorch's compiler
generates, and `TRITON_CACHE_DIR` for the GPU binaries built from it. Unset,
both live under `torchinductor_<your user name>` in the system's temporary
folder, usually `/tmp`, which is often emptied at reboot. Set both to a folder
in the project before you start Python; `outputs/` is already ignored by git:

```bash
export TORCHINDUCTOR_CACHE_DIR="$PWD/outputs/compile_cache/inductor"
export TRITON_CACHE_DIR="$PWD/outputs/compile_cache/triton"
python lessons/04_parallel/check_gpu.py --cases candidate_000
```

A later run with the same shapes finds the programs there and skips most of the
compiling. On an RTX 4500 Ada, `check_gpu.py --cases candidate_000` took 22
seconds with empty cache folders and 8 seconds with filled ones. Each new
process still traces the functions once, so warm up either way.

To skip compilation, set `TORCH_COMPILE_DISABLE=1`. The marked functions then
run as plain PyTorch array code: there is no compile wait, but every line reads
and writes whole arrays, so each iteration is slower. Use it to debug or for a
quick look. Keep compilation on for timings and for `check_gpu.py`, which tests
the compiled programs. To compile again, unset the variable
(`unset TORCH_COMPILE_DISABLE`); in older PyTorch releases such as 2.7, any
value, even `0`, turns compilation off.

The experimental backends in the next section also launch two kernels written
directly in Triton, in `qmp_torch_share_fused.py` and
`qmp_torch_share_resident.py`. Triton compiles them itself, outside
`torch.compile`, so they compile even with `TORCH_COMPILE_DISABLE=1`: each one
the first time it is launched with a new M. Triton keeps them in
`TRITON_CACHE_DIR`. Unset, that is `~/.triton/cache`, or the temporary folder
above once `torch.compile` has built anything in the same process. Setting both
variables as shown keeps every compiled program in one place. The default path
(`run.py gpu`, `solve_batch_current` and `check_gpu.py`) compiles through
`torch.compile` only.

## The optional fused, mixed and resident solvers

Install the CPU package first. A separately authored GPU script also needs
`03_gpu` on its own import path. On a Linux machine with a CUDA GPU, launch it
from the repository root with `PYTHONPATH=03_gpu python your_gpu_script.py`.
Running `run.py` earlier does not change another process's import path.

```python
import numpy as np
from qmp import ModelConfig, Numerics, generate_draws
from qmp_torch import solve_batch_current
from qmp_torch_precision import precision_backend
from qmp_torch_share_resident import resident_backend

# Example: two points, one common potential-firm count.
x = np.array([[1.13125, 4.36875, .9, sigma, 12, .7]
              for sigma in (.06, .07)], dtype=np.float64)
M = int(np.floor(x[0, 4]))
config, numerics = ModelConfig(markets=200), Numerics()
draws = generate_draws(M, config.markets, seed=100)
with precision_backend("fused_fp64"):
    fused = solve_batch_current(x, config=config, numerics=numerics, draws=draws)
with precision_backend("mixed"):
    mixed = solve_batch_current(x, config=config, numerics=numerics, draws=draws)
with resident_backend():
    resident = solve_batch_current(x, config=config, numerics=numerics, draws=draws)
```

The fused backend combines one strict share update. Mixed precision uses an
FP32 share predictor followed by mandatory FP64 correction. Resident mode
retains that predictor and moves the correction loop onto the device, preserving
its per-market first stops and independent final residual. Prices, root solving,
exit decisions and moments stay in FP64 and pass the same checks.

These contexts temporarily select module functions and restore them on exit.
Use separate isolated worker processes; do not run competing contexts in threads
sharing the same module globals. Importing a module does not switch defaults.
The fingerprint that the CLI writes covers default runs; a run with one of these
contexts needs its own record of what was checked.

## Separate reference port

`08_gpu/qmp_gpu` is a single-economy numerical reference. Its `simulate` API uses
the CPU configuration and native draws. It is not the batched engine, and its
timing against one CPU thread is a different comparison from the 64-core CPU
and multi-GPU timings.

The old `load_draws` and `solve_batch` functions in the preserved batch source
refer to historical MATLAB draws that are deliberately absent. Neither the new
root runner nor the current API calls that legacy input path.
