"""Audit a returned TB01 ZIP against locally frozen code; never execute ZIP code."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import three_role_boundary_01_runtime as runtime
import build_three_role_boundary_01_cell as build


def audit_registered_archive(archive):
    _, files = runtime.read_archive(archive)
    contract = json.loads(files['contract.json'])
    registry = [build.AUDIT / 'payload.json',
                build.ROOT / 'throughline/audits/three-role-boundary-01-preparation-20261013/payload.json']
    for path in registry:
        packed = json.loads(path.read_bytes())
        if contract != packed['contract']:
            continue
        if path == registry[0]:
            return runtime.aggregate_archive(archive, packed)
        # Legacy replay uses only the trusted local payload, never received ZIP code.
        # Its original checker must remain in place when interpreting the old failure.
        with tempfile.TemporaryDirectory(prefix='tb01-legacy-verifier-') as temp:
            folder = Path(temp)
            for name, source in packed['code'].items():
                if Path(name).name != name:
                    raise ValueError('INVALID_LOCAL_SOURCE_PATH')
                (folder / name).write_text(source)
            (folder / 'payload.json').write_text(json.dumps(packed))
            code = ('import json,sys;from pathlib import Path;import three_role_boundary_01_runtime as r;'
                    'p=json.loads(Path("payload.json").read_bytes());'
                    'Path("result.json").write_text(json.dumps(r.aggregate_archive(Path(sys.argv[1]),p)))')
            result = subprocess.run([sys.executable, '-c', code, str(Path(archive).resolve())],
                                    cwd=folder, capture_output=True, text=True, timeout=60)
            if result.returncode:
                raise RuntimeError('LEGACY_LOCAL_VERIFIER_FAILED: ' + result.stderr[-2000:])
            return json.loads((folder / 'result.json').read_bytes())
    raise ValueError('ARCHIVE_CONTRACT_NOT_IN_TRUSTED_LOCAL_REGISTRY')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('archive', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Choose a new output; preserved analyses are immutable.')
    # Trusted fixed payload from our delivery, not code embedded in the received archive.
    result = audit_registered_archive(args.archive)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write('\n')
    report = result['report']
    print(json.dumps({'gate': report['gate'], 'model_calls': report['attempted_generations'],
                      'evidence_kind': report['evidence_kind'], 'output': str(args.output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
