"""Inspect or run a readable MRSI experiment bundle.

Inspection uses only the Python standard library. Model generation requires
--run inside Google Colab and delegates to the preserved experiment supervisor.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checked_path(root: Path, relative: str) -> Path:
    """Reject traversal and symlinks, including symlinked parent directories."""
    path = PurePosixPath(relative)
    if path.is_absolute() or not path.parts or any(p in {'.', '..'} for p in path.parts):
        raise ValueError(f'Unsafe bundle path: {relative}')
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f'Symlink in bundle: {relative}')
    if not current.is_file() or not current.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Missing or escaped bundle file: {relative}')
    return current


def inspect_bundle(root: Path) -> tuple[dict, bytes]:
    """Reassemble the original JSON bytes without importing experiment code."""
    manifest = json.loads(checked_path(root, 'bundle.json').read_text(encoding='utf-8'))
    if manifest['format'] != 'npp-readable-generation-v1':
        raise ValueError('Unsupported bundle format')
    for relative, expected in manifest['files'].items():
        if digest(checked_path(root, relative).read_bytes()) != expected:
            raise ValueError(f'Changed bundle file: {relative}')

    def restore(spec: dict):
        kind = spec['kind']
        if kind == 'mapping':
            return {k: restore(v) for k, v in spec['items'].items()}
        relative = spec['path']
        if relative not in manifest['files']:
            raise ValueError(f'Unhashed input: {relative}')
        text = checked_path(root, relative).read_text(encoding='utf-8')
        if kind == 'text':
            return text
        if kind == 'json':
            return json.loads(text)
        raise ValueError(f'Unsupported input kind: {kind}')

    payload = restore(manifest['payload'])
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                     separators=(',', ':')).encode('utf-8')
    if digest(raw) != manifest['original_payload_sha256']:
        raise ValueError('Reassembled payload differs from the original OneCell payload')
    return manifest, raw


def main(root: Path, argv: list[str] | None = None) -> None:
    manifest, raw = inspect_bundle(root)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', help='Generate new responses on Colab')
    parser.add_argument('--no-download', action='store_true', help='Keep ZIP in Colab Files only')
    if manifest['entrypoint'] == 'run_main_colab':
        parser.add_argument('--part', type=int, choices=(1, 2), default=1)
        parser.add_argument('--resume-zip', default='')
        parser.add_argument('--recover-interrupted-run', action='store_true')
    args = parser.parse_args(argv)
    print(f"{manifest['trial']}: verified {len(manifest['files'])} readable files; "
          f"original payload SHA-256 {digest(raw)}")
    if not args.run:
        print('Inspection only. No model imports, installation, network access, or generation.')
        return
    # Check the execution environment BEFORE importing the experiment supervisor.
    if not Path('/content').is_dir():
        parser.error('--run requires Google Colab; local GPU execution is not supported')
    try:
        colab_available = importlib.util.find_spec('google.colab') is not None
    except ModuleNotFoundError:
        colab_available = False
    if not colab_available:
        parser.error('--run requires Google Colab')
    path = checked_path(root, 'supervisor.py')
    spec = importlib.util.spec_from_file_location('npp_readable_supervisor', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    entrypoint = getattr(module, manifest['entrypoint'])
    kwargs = {'download': not args.no_download}
    if manifest['entrypoint'] == 'run_main_colab':
        kwargs.update(part=args.part, run_main=True, resume_zip=args.resume_zip,
                      recover=args.recover_interrupted_run)
    entrypoint(raw, manifest['original_payload_sha256'], **kwargs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Verify readable generation files without executing them')
    parser.add_argument('--all', action='store_true', required=True)
    parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    reports = []
    for path in sorted((root / 'experiments').glob('*/generation/bundle.json')):
        manifest, raw = inspect_bundle(path.parent)
        reports.append({'trial': manifest['trial'], 'files': len(manifest['files']),
                        'original_payload_sha256': digest(raw)})
    expected = {row['id'] for row in json.loads((root / 'EXPERIMENTS.json').read_text())}
    if {r['trial'] for r in reports} != expected:
        raise ValueError('Readable bundles do not cover the experiment catalog')
    print(json.dumps({'status': 'PASS', 'trials': len(reports), 'model_calls': 0,
                      'bundles': reports}, indent=2))
