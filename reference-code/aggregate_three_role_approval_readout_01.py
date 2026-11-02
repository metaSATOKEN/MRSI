"""Replay TAR01 with the local frozen payload; returned ZIP code is not executed."""
import argparse
import json
from pathlib import Path
import three_role_approval_readout_01_runtime as rt
import build_three_role_approval_readout_01_cell as build

def main():
    p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():raise FileExistsError('Use a new output path; earlier results are immutable.')
    packed=json.loads((build.AUDIT/'payload.json').read_bytes())
    result=rt.aggregate_archive(args.archive,packed)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:result['report'][k] for k in ('gate','attempted_generations','totals','by_arm','triplet_totals')},ensure_ascii=False))

if __name__=='__main__':main()
