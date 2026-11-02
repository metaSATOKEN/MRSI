"""Recompute saved Study2 evidence without generating or contacting a model."""
from pathlib import Path
import argparse
import copy
import hashlib
import importlib
import json
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_distribution():
    manifest = ROOT / 'MANIFEST.json'
    if not manifest.exists():
        raise RuntimeError('Distribution manifest is missing')
    records = json.loads(manifest.read_text())['sha256']
    for name, expected in records.items():
        path = ROOT / name
        if not path.is_file() or digest(path) != expected:
            raise RuntimeError('Distribution hash mismatch: ' + name)
    return len(records)

def offline_guard(event, args):
    if event.startswith('socket.') or event in (
        'subprocess.Popen', 'os.system', 'os.posix_spawn', 'os.exec',
    ):
        raise RuntimeError('Offline replay forbids ' + event)

def child(trial):
    # A fresh process keeps each experiment's frozen helper versions separate.
    sys.addaudithook(offline_guard)
    catalog = json.loads((ROOT/'EXPERIMENTS.json').read_text())
    if trial == 'TB01-PREP':
        entry = next(x for x in catalog if x['id'] == 'TB01')['preparation_attempt']
        base = ROOT/entry['base']
    else:
        entry = next(x for x in catalog if x['id'] == trial)
        base = ROOT/'experiments'/trial
    if digest(base/'payload.json') != entry['payload_sha256']:
        raise RuntimeError('Payload hash mismatch')
    packed = json.loads((base/'payload.json').read_text())
    for name, expected in entry['payload_code_hashes'].items():
        if digest(base/'code'/name) != expected:
            raise RuntimeError('Frozen code hash mismatch: '+name)
    archives = [ROOT/x['path'] for x in entry['archives']]
    for path, record in zip(archives, entry['archives']):
        if digest(path) != record['sha256']:
            raise RuntimeError('Archive hash mismatch: '+path.name)
    sys.path.insert(0, str(base/'code'))
    runtime = importlib.import_module(entry['module'])
    out = ROOT/'replay-output'
    out.mkdir(exist_ok=True)
    if trial == 'XM01':
        with tempfile.TemporaryDirectory(prefix='study2-xm-replay-') as temp:
            result = runtime.aggregate_archives(archives, packed, Path(temp)/'result.json')
    else:
        result = runtime.aggregate_archive(archives[0], packed)
    expected = json.loads((ROOT/entry['expected_result']).read_text())
    # Compare the persisted JSON representation (Python tuples become arrays),
    # matching how the original aggregate was saved. Raw answers are untouched.
    observed = json.loads(json.dumps(result))
    reference = copy.deepcopy(expected)
    # XM01 stamps a new aggregation time on each part. These two timestamps
    # are run metadata, not outcomes. Preserve both original and new values.
    ignored = []
    if trial == 'XM01':
        for part in ('PART1', 'PART2'):
            ignored.append('parts/'+part+'/generated_at')
            del observed['parts'][part]['generated_at']
            del reference['parts'][part]['generated_at']
    if observed != reference:
        (out/(trial+'-mismatch.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
        raise RuntimeError('Recomputed result differs: '+trial)
    (out/(trial+'.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    (out/(trial+'-verification.json')).write_text(json.dumps({'status':'PASS', 'ignored_metadata_paths':ignored, 'new_model_requests':0}, indent=2)+'\n')
    print(trial+': PASS — recomputed saved responses match the recorded aggregate', flush=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--all', action='store_true')
    group.add_argument('--trial', choices=[x['id'] for x in json.loads((ROOT/'EXPERIMENTS.json').read_text())] + ['TB01-PREP'])
    group.add_argument('--paper-01', action='store_true')
    group.add_argument('--verify', action='store_true', help='Verify distribution hashes only')
    group.add_argument('--child', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.child:
        child(args.child)
        return
    if not any((args.all, args.trial, args.paper_01, args.verify)):
        parser.print_help()
        return
    print('Distribution: '+str(verify_distribution())+' file hashes verified', flush=True)
    if args.verify:
        return
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    if args.all or args.paper_01:
        subprocess.run([sys.executable, str(ROOT/'evidence/paper-01/replay.py')], check=True, env=env)
    trials = [x['id'] for x in json.loads((ROOT/'EXPERIMENTS.json').read_text())] if args.all else ([args.trial] if args.trial else [])
    for trial in trials:
        subprocess.run([sys.executable, str(Path(__file__).resolve()), '--child', trial], check=True, env=env)
        if trial == 'TB01':
            subprocess.run([sys.executable, str(Path(__file__).resolve()), '--child', 'TB01-PREP'], check=True, env=env)
    print('PASS — all requested offline replays completed', flush=True)

if __name__ == '__main__':
    main()
