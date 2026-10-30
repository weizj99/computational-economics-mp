# Dependencies and execution

CPU package metadata in `model/pyproject.toml` is authoritative:
Python >=3.10, NumPy >=1.24 and SciPy >=1.10, with setuptools >=68 for packaging.
The plain requirements file repeats those runtime requirements for convenience.

CUDA execution additionally needs a PyTorch build compatible with the machine's
driver. Optional fusion, mixed and resident modules import Triton and its CUDA
libdevice helpers. Install these in a separate CUDA environment; installing an
arbitrary CPU-only Torch wheel does not enable GPU execution. Check the versions
on the machine you use; not every allowed version combination has been tested.

The checks of 2026-10-29 ran with Python 3.13, NumPy 2.5 and SciPy 1.18, and
they reproduced the saved results exactly. The GPU checks of 2026-10-30 ran
with PyTorch 2.11.0 (CUDA 12.8) and Triton 3.6.0 on an NVIDIA RTX 4500 Ada. The scripts in
`tools/site/` also need Matplotlib (`requirements-teaching.txt`).

No installed packages, virtual environments, drivers or generated caches are in
the repository. The website uses ordinary static files
and bundled webfonts; it has no Python runtime dependency.
