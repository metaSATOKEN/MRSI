"""Verify/re-score a returned SX01 ZIP offline with frozen local code, never archive code."""
import argparse
import json
from pathlib import Path
from build_self_update_exchange_01_cell import unpack_cell
from self_update_exchange_01_runtime import aggregate_archive

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('zip');p.add_argument('--output',required=True);args=p.parse_args()
    result=aggregate_archive(args.zip,unpack_cell())
    with Path(args.output).open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'closed':result['report']['closed_logical_responses'],
                      'generations':result['report']['attempted_generations'],
                      'path':result['report']['path'],'status':result['report']['status_counts']},ensure_ascii=False))
