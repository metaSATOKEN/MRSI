"""Standard-library regression tests for public bundle inspection; no generation."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

import readable_generation as reader

ROOT = Path(__file__).resolve().parents[1]


class ReadableBundleTests(unittest.TestCase):
    def test_all_bundles_preserve_inputs_and_supervisor_logic(self):
        seen = set()
        for path in sorted((ROOT / 'experiments').glob('*/generation/bundle.json')):
            with self.subTest(trial=path.parts[-3]):
                manifest, raw = reader.inspect_bundle(path.parent)
                payload = json.loads(raw)
                recorded = json.loads((path.parent.parent / 'payload.json').read_text())
                self.assertEqual(payload, recorded)
                for name, text in payload['code'].items():
                    self.assertEqual((path.parent / 'source' / name).read_bytes(), text.encode())
                original = next(text for text in payload['code'].values()
                                if reader.digest(text.encode()) == manifest['original_supervisor_sha256'])
                expected = original.replace(
                    'zlib.decompress(base64.b64decode(blob, validate=True))', 'payload_bytes'
                ).replace('def ' + manifest['entrypoint'] + '(blob,',
                          'def ' + manifest['entrypoint'] + '(payload_bytes,')
                self.assertEqual((path.parent / 'supervisor.py').read_text(), expected)
                with contextlib.redirect_stdout(io.StringIO()):
                    reader.main(path.parent, [])
                seen.add(manifest['trial'])
        catalog = json.loads((ROOT / 'EXPERIMENTS.json').read_text())
        self.assertEqual(seen, {entry['id'] for entry in catalog})
        self.assertNotIn('npp_readable_supervisor', sys.modules)
        self.assertNotIn('torch', sys.modules)

    def test_altered_files_and_escaped_paths_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix='npp-readable-test-') as temp:
            bundle = Path(temp) / 'generation'
            shutil.copytree(ROOT / 'experiments/OR01/generation', bundle)
            for target in [next((bundle / 'source').glob('*.py')),
                           next((bundle / 'materials').glob('*.json'))]:
                raw = target.read_bytes()
                target.write_bytes(raw + b' ')
                with self.assertRaises(ValueError):
                    reader.inspect_bundle(bundle)
                target.write_bytes(raw)
            source = next((bundle / 'source').glob('*.py'))
            outside = Path(temp) / 'same-bytes.py'
            outside.write_bytes(source.read_bytes())
            source.unlink()
            source.symlink_to(outside)
            with self.assertRaises(ValueError):
                reader.inspect_bundle(bundle)
            with self.assertRaises(ValueError):
                reader.checked_path(bundle, '../same-bytes.py')

    @unittest.skipIf(Path('/content').is_dir(), 'Never exercise --run in a possible Colab runtime')
    def test_local_run_is_rejected_before_importing_supervisor(self):
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                reader.main(ROOT / 'experiments/OR01/generation', ['--run'])
        self.assertEqual(error.exception.code, 2)
        self.assertNotIn('npp_readable_supervisor', sys.modules)


if __name__ == '__main__':
    def offline_guard(event, args):
        if event.startswith('socket.') or event in {'subprocess.Popen', 'os.system', 'os.posix_spawn', 'os.exec'}:
            raise RuntimeError('Inspection test attempted network/process execution: ' + event)
    sys.addaudithook(offline_guard)
    unittest.main()
