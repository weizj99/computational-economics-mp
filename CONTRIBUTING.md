# Contributing

Corrections and suggestions are welcome. To report an error, open an issue
that names the lesson or the file and says what you expected. The
[course map](docs/COURSE_MAP.md) lists the code behind each lesson.

## Keep the numbers

The saved results on the website come from the code in this repository, so a
change to the model code in `07_python/`, `03_gpu/` or `08_gpu/` must reproduce
them. Do not change the objective, the precision, the random draws, the root
solver or the stopping rules as part of another fix; a change that alters a
result needs its own explanation and new checks.

Optional GPU contexts change module globals while they run; compare them in
separate worker processes, as described in [GPU usage](docs/GPU.md). Check that
the outputs agree before you compare speed.

## Check your change

Run `python run.py test`; the tests take a few seconds. The full annual search
of unit 03 takes about 60 core-hours, so run it only when a change affects the
solver or the estimation.

The website's code downloads and its "Code on GitHub" lines are built from the
repository. After you change code, data or `course_map.json`, run
`python tools/build_downloads.py` and `python tools/site/source_links.py`; with
`--check`, each reports what no longer matches.

A change to the GPU code needs a GPU check: `python lessons/04_parallel/check_gpu.py`
compares the GPU code with the CPU solver. Without a GPU,
`python tools/check_gpu_on_cpu.py` runs the same checks with the tensors on the
CPU (it needs PyTorch). That tests the Python logic, not the CUDA kernels or the
speed.

When you describe a change, say what it fixes, which files it touches and which
checks you ran. Keep measured times apart from illustrative work units.

Contributions are accepted under the same licences as the rest of the
repository; see [licences and credit](RIGHTS.md).
