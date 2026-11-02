"""Re-score a returned READOUT-SPLIT-01 ZIP offline; never execute archived code."""
import argparse
import json
from pathlib import Path
from build_readout_split_01_cell import unpack_cell
from readout_split_01_runtime import aggregate_archive

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('zip'); p.add_argument('--output', required=True)
    args = p.parse_args()
    result = aggregate_archive(args.zip, unpack_cell())
    with Path(args.output).open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps({'closed': result['report']['closed_responses'], 'generations': result['report']['attempted_generations'],
                      'status': result['report']['status_counts']}, ensure_ascii=False))
