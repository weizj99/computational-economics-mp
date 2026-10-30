"""Portable entrypoints for the current teaching implementation."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
# Each unit's example: (unit, file it needs, command). A unit's download holds
# only that unit's files, so the help lists only the examples present here.
EXAMPLES = (
    ('00', 'lessons/00_prerequisites/ab08.py', 'python lessons/00_prerequisites/ab08.py'),
    ('00', 'lessons/00_prerequisites/berry92.py', 'python lessons/00_prerequisites/berry92.py'),
    ('01', 'lessons/01_gmm_smm/gmm_smm.py', 'python lessons/01_gmm_smm/gmm_smm.py'),
    ('02', 'lessons/02_one_economy/parameters_to_moments.py',
     'python lessons/02_one_economy/parameters_to_moments.py'),
    ('03', 'lessons/03_estimation/search_year.py',
     'python lessons/03_estimation/search_year.py --year 2000 --points 64'),
    ('04', 'lessons/04_parallel/scaling.py', 'python lessons/04_parallel/scaling.py --cases 16'),
    ('04', 'lessons/04_parallel/loop_vs_vectorized.py', 'python lessons/04_parallel/loop_vs_vectorized.py'),
    ('04', 'lessons/04_parallel/output_root.py', 'python lessons/04_parallel/output_root.py'),
    ('04', 'lessons/04_parallel/check_gpu.py', 'python lessons/04_parallel/check_gpu.py   (needs a CUDA GPU)'),
)


def examples():
    lines, previous = [], None
    for unit, needed, command in EXAMPLES:
        if (ROOT/needed).is_file():
            lines.append(f"  {unit if unit != previous else '  '}  {command}")
            previous = unit
    return '\n'.join(lines)


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ('-h', '--help'):
        print(f'''Computational Economics — current source

Each unit's example, run from this folder:
{examples()}

Commands:
  python run.py cpu [CPU options]          one native-input CPU economy
  python run.py gpu POINTS OUTPUT [options] current strict FP64 batch backend
  python run.py test                       existing CPU tests
  python run.py example-inputs DIRECTORY  write a small synthetic GPU example
  python run.py serve --site-dir website   preview the course website

Use cpu --help or gpu --help for the original solver options.
Optional mixed/fused/resident backends are explicit Python APIs; see docs/GPU.md.
The separate gpu/single_economy package is a reference port, not the batched engine.
''')
        return 0
    command, rest = args[0], args[1:]
    # A unit's download holds only that unit's files; say what is missing.
    needed = {'gpu': 'gpu/batched/run_points_current.py', 'example-inputs': 'tools/make_example_inputs.py',
              'serve': 'tools/serve_site.py'}.get(command)
    if needed and not (ROOT/needed).is_file():
        raise SystemExit(f'python run.py {command} needs {needed}, which this folder does not have. '
                         'Use the course repository, or for the GPU commands the unit 04 download.')
    sys.path[:0] = [str(ROOT/'model'), str(ROOT/'gpu/batched'), str(ROOT/'gpu/single_economy')]
    if command == 'cpu':
        from qmp.__main__ import main as cpu_main
        return cpu_main(rest)
    if command == 'gpu':
        from run_points_current import main as gpu_main
        return gpu_main(rest)
    if command == 'test':
        if rest:
            raise SystemExit('test takes no arguments; use unittest directly for a selected case')
        env = os.environ.copy()
        env['PYTHONPATH'] = str(ROOT/'model') + os.pathsep + env.get('PYTHONPATH', '')
        return subprocess.call([sys.executable, '-m', 'unittest', 'discover',
                                '-s', str(ROOT/'model/tests'), '-v'], env=env)
    if command == 'example-inputs':
        from tools.make_example_inputs import main as example_main
        return example_main(rest)
    if command == 'serve':
        parser = argparse.ArgumentParser(description='Read-only static website preview')
        parser.add_argument('--site-dir', type=Path, required=True)
        parser.add_argument('--port', type=int, default=8765)
        parser.add_argument('--host', default='127.0.0.1', help='Numeric loopback address only')
        selected = parser.parse_args(rest)
        if not (selected.site_dir/'prerequisites/index.html').is_file():
            parser.error('--site-dir must be the course website folder, website/')
        return subprocess.call([sys.executable, str(ROOT/'tools/serve_site.py'),
                                '--port', str(selected.port), '--host', selected.host,
                                '--directory', str(selected.site_dir.resolve())])
    raise SystemExit('Unknown command: '+command+'; use --help')


if __name__ == '__main__':
    raise SystemExit(main())
