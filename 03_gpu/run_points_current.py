"""Current Python contract on the original M-grouped GPU batch driver.

This is the input/output adapter for ``run_points.py --current``. Grouping,
cell-budget chunks, atomic batch checkpoints and identity checks follow the
original driver. Numerical work stays in qmp_torch.solve_batch_current.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '07_python'))
from qmp import ModelConfig, Numerics, generate_draws
from qmp.estimation import diagnostic_quality

MOMENTS = ('employment_reallocation_rate', 'markup_sales_weighted',
           'sga_cost_share_sales_weighted')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def object_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    tmp.replace(path)


def groups(rows, markets, cells):
    """Use the existing driver's floor(N), M grouping and B*M*J budget."""
    if not math.isfinite(cells) or cells < markets:
        raise ValueError('cells must be a positive firm-market-cell budget')
    by_m = {}
    ids = [int(r['row_id']) for r in rows]
    if len(set(ids)) != len(ids):
        raise ValueError('row_id must be unique')
    for row in rows:
        m = math.floor(row['x'][4])
        by_m.setdefault(m, []).append(row)
    for m in sorted(by_m):
        size = max(1, int(cells // (m * markets)))
        for start in range(0, len(by_m[m]), size):
            yield m, by_m[m][start:start + size]


def solve_rows(rows, *, config=None, numerics=None, draws_by_m=None,
               seed=100, cells=6e7, device='cuda', checkpoint=None,
               completed=None):
    """Return compact, ordered results; optionally persist each finished batch.

    The caller may provide already prepared standard normals. Productivity
    construction, upload and final compact host return remain inside this call.
    No input selection, search, ranking, or objective change happens here.
    """
    import torch
    import qmp_torch as q
    config = config or ModelConfig()
    numerics = numerics or Numerics()
    draws_by_m = {} if draws_by_m is None else draws_by_m
    complete = {} if completed is None else dict(completed)
    batch_trace = []
    for m, batch in groups(rows, config.markets, cells):
        batch = [r for r in batch if int(r['row_id']) not in complete]
        if not batch:
            continue
        if m not in draws_by_m:
            draws_by_m[m] = generate_draws(m, config.markets, seed=seed)
        params = np.asarray([r['x'] for r in batch], dtype=np.float64)
        started = time.perf_counter()
        answer = q.solve_batch_current(params, config=config, numerics=numerics,
                                       draws=draws_by_m[m], device=device)
        if str(device).startswith('cuda'):
            torch.cuda.synchronize()
        elapsed = time.perf_counter() - started
        batch_records = []
        for i, row in enumerate(batch):
            quality = diagnostic_quality(answer['diagnostics'][i], asdict(numerics))
            valid = bool(answer['valid'][i]) and quality['passed']
            values = np.asarray(answer['moments'][i], dtype=float)
            valid = valid and bool(np.isfinite(values).all())
            record = {'index': int(row.get('index', row['row_id'])),
                      'row_id': int(row['row_id']), 'year': int(row.get('year', 0)),
                      'status': 'ok' if valid else 'failed',
                      'moments': {k: float(v) if math.isfinite(v) else None
                                  for k, v in zip(MOMENTS, values)},
                      'phi': float(answer['phi'][i]) if valid else None,
                      'Mbar': float(answer['Mbar'][i]) if valid else None,
                      'quality': quality, 'error': answer['errors'][i]}
            batch_records.append(record)
            complete[record['row_id']] = record
        trace = {'M': m, 'B': len(batch), 'row_ids': [int(r['row_id']) for r in batch],
                 'elapsed_seconds': elapsed,
                 'peak_allocated_GB': torch.cuda.max_memory_allocated()/2**30
                 if str(device).startswith('cuda') else 0.,
                 'peak_reserved_GB': torch.cuda.max_memory_reserved()/2**30
                 if str(device).startswith('cuda') else 0.}
        batch_trace.append(trace)
        if checkpoint is not None:
            checkpoint(batch_records, trace)
    ordered = [complete[int(r['row_id'])] for r in rows]
    if len(ordered) != len(rows) or {r['row_id'] for r in ordered} != {r['row_id'] for r in rows}:
        raise ValueError('every requested point must appear exactly once')
    return ordered, batch_trace


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('points', type=Path)
    parser.add_argument('outdir', type=Path)
    parser.add_argument('--contract', type=Path,
                        help='JSON containing current model_config and numerics')
    parser.add_argument('--cells', type=float, default=6e7)
    parser.add_argument('--seed', type=int, default=100)
    parser.add_argument('--device', default='cuda')
    args = parser.parse_args(argv)
    contract = json.loads(args.contract.read_text()) if args.contract else {}
    config = ModelConfig(**contract.get('model_config', {}))
    numerics = Numerics(**contract.get('numerics', {}))
    rows = []
    with args.points.open(newline='') as handle:
        for index, row in enumerate(csv.DictReader(handle)):
            x = ([float(row[f'x{k}']) for k in range(6)] if 'x0' in row else
                 [1.13125, 4.36875, .9, float(row['sigma']), float(row['N']),
                  float(row['zeta'])])
            rows.append({'index': index, 'row_id': int(row['row_id']),
                         'year': int(row.get('year', 0)), 'x': x})
    args.outdir.mkdir(parents=True, exist_ok=True)
    import qmp.equilibrium as eq
    base = Path(eq.__file__).parent
    source = {str(p.name): sha(p) for p in (Path(__file__), Path(__file__).with_name('qmp_torch.py'),
              Path(__file__).with_name('qmp_torch_current.py'))}
    source.update({'qmp/' + p.name: sha(p) for p in base.glob('*.py')})
    manifest = {'input_sha256': sha(args.points), 'model_config': asdict(config),
                'numerics': asdict(numerics), 'seed': args.seed, 'dtype': 'float64',
                'source_sha256': source, 'rows': rows}
    fingerprint = object_hash(manifest)
    mf = args.outdir/'current_manifest.json'
    if mf.exists():
        if json.loads(mf.read_text()) != manifest:
            raise ValueError('input/configuration/source changed; use a new output directory')
    else:
        atomic_json(mf, manifest)
    completed = {}
    for path in sorted(args.outdir.glob('batch_current_*.json')):
        part = json.loads(path.read_text())
        if part['fingerprint'] != fingerprint:
            raise ValueError('checkpoint belongs to a different run')
        for row in part['records']:
            if row['row_id'] in completed:
                raise ValueError('duplicate checkpoint row')
            completed[row['row_id']] = row
    if not set(completed).issubset({r['row_id'] for r in rows}):
        raise ValueError('checkpoint contains unrequested rows')
    number = len(list(args.outdir.glob('batch_current_*.json')))

    def checkpoint(records, trace):
        nonlocal number
        atomic_json(args.outdir/f'batch_current_{number:06d}.json',
                    {'fingerprint': fingerprint, 'records': records, 'trace': trace})
        number += 1
        print(json.dumps({'M': trace['M'], 'B': trace['B'],
                          'seconds': trace['elapsed_seconds'],
                          'valid': sum(r['status'] == 'ok' for r in records)}), flush=True)

    records, trace = solve_rows(rows, config=config, numerics=numerics, seed=args.seed,
                               cells=args.cells, device=args.device, checkpoint=checkpoint,
                               completed=completed)
    passed = all(r['status'] == 'ok' for r in records)
    atomic_json(args.outdir/'results_current.json',
                {'fingerprint': fingerprint, 'passed': passed,
                 'count': len(records), 'records': records, 'batch_trace': trace})
    if not passed:
        raise SystemExit('Some economies failed; see preserved per-row diagnostics')


if __name__ == '__main__':
    main()
