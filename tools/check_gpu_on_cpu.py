"""Run lessons/04_parallel/check_gpu.py on a machine without a GPU.

This is a maintainer's check, not a substitute for a GPU run. It copies the GPU
code to a temporary folder, changes only the lines that demand a CUDA device so
that the tensors live on the CPU, removes the torch.compile decorators so the
same functions run eagerly, and runs the usual three checks against the NumPy
solver. It exercises the Python logic of the GPU
code (parameters, batching, ordering, moments); CUDA kernels, Triton and speed
are not tested. It needs PyTorch (any build) and threadpoolctl. All 17 economies
take about half an hour on four cores; --cases picks fewer.

    python tools/check_gpu_on_cpu.py --cases candidate_000 2018_new_seed100
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PARTS = ("model", "gpu/batched", "gpu/single_economy", "lessons/04_parallel", "data")
# (file, text that demands CUDA, CPU replacement); each text must occur exactly once.
PATCHES = (
    ("gpu/single_economy/qmp_gpu/equilibrium.py",
     "    target = torch.device(device)\n    if target.type != 'cuda' or not torch.cuda.is_available():\n"
     "        raise ValueError('the GPU economy requires an available CUDA device')\n"
     "    return torch.device('cuda', torch.cuda.current_device() if target.index is None else target.index)",
     "    return torch.device('cpu')"),
    ("gpu/single_economy/qmp_gpu/shares.py", "z.device.type != 'cuda'", "False"),
    ("gpu/batched/qmp_torch_current.py",
     "    if dev.type != 'cuda' or not torch.cuda.is_available():\n        raise ValueError('the current GPU batch requires CUDA')\n"
     "    dev = torch.device('cuda', torch.cuda.current_device() if dev.index is None else dev.index)",
     "    dev = torch.device('cpu')"),
    ("lessons/04_parallel/gpu_share_check.py",
     '    if not torch.cuda.is_available():\n        raise RuntimeError("This check needs a CUDA GPU")\n', ""),
    ("lessons/04_parallel/gpu_share_check.py",
     '    device = torch.device("cuda")\n    props = torch.cuda.get_device_properties(device)\n',
     '    device = torch.device("cpu")\n    props = type("Device", (), {"name": "CPU", "total_memory": 0})\n'),
    ("lessons/04_parallel/gpu_share_check.py", "        torch.cuda.synchronize(device)\n", "        pass\n"),
)


def main():
    with tempfile.TemporaryDirectory() as folder:
        copy = Path(folder)
        for part in PARTS:
            shutil.copytree(ROOT / part, copy / part, ignore=shutil.ignore_patterns("__pycache__"))
        for name, old, new in PATCHES:
            path = copy / name
            text = path.read_text(encoding="utf-8")
            if text.count(old) != 1:
                raise SystemExit(f"{name}: the CUDA line to patch has changed; update PATCHES")
            path.write_text(text.replace(old, new), encoding="utf-8")
        for path in (copy / "gpu/batched").glob("*.py"):
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace("@torch.compile(fullgraph=True)\n", ""), encoding="utf-8")
        env = dict(os.environ)
        # Any arguments, such as --cases, pass through to check_gpu.py.
        return subprocess.call([sys.executable, str(copy / "lessons/04_parallel/check_gpu.py"),
                                "--output-dir", str(copy / "outputs"), *sys.argv[1:]], cwd=copy, env=env)


if __name__ == "__main__":
    sys.exit(main())
