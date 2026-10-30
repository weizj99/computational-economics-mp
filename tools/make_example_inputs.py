"""Write declared synthetic GPU inputs; never read private annual data."""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
import json
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args(argv)
    from qmp import ModelConfig, Numerics
    args.directory.mkdir(parents=True, exist_ok=True)
    points, contract = args.directory/'points.csv', args.directory/'contract.json'
    if points.exists() or contract.exists():
        parser.error('use a new directory; existing example inputs are preserved')
    with points.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['row_id', 'year', 'sigma', 'N', 'zeta'])
        writer.writerows([[1, 0, .06, 12, .7], [2, 0, .07, 12, .7]])
    payload = {
        'model_config': asdict(ModelConfig(markets=200)), 'numerics': asdict(Numerics()),
        'input_scope': 'Two declared illustrative parameter points, not estimated years or benchmark data.',
        'year_zero_is_a_label': True
    }
    contract.write_text(json.dumps(payload, indent=2)+'\n', encoding='utf-8')
    print('Wrote points.csv and contract.json to '+str(args.directory))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
