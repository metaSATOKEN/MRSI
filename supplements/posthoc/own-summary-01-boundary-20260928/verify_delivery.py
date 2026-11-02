"""Delivery checks for the completed, offline-only OS01 boundary audit."""
from hashlib import sha256
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
checks = []


def check(name, ok):
    checks.append({'name': name, 'pass': bool(ok)})
    if not ok:
        raise AssertionError(name)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


check('not already sealed', not (HERE/'MANIFEST.json').exists())
before = json.loads((HERE/'protected-before.json').read_bytes())
for name, h in before.items():
    check('protected '+name, digest(ROOT/name) == h)
code = json.loads((HERE/'before-run.json').read_bytes())
for name, h in code['files'].items():
    check('before-run file '+name, digest(HERE/name) == h)
manifest = json.loads((HERE/'analysis/MANIFEST.json').read_bytes())
for name, h in manifest.items():
    check('analysis seal '+name, digest(HERE/'analysis'/name) == h)
raw_ledger = (ROOT/'throughline/audits/ledger-2026-09.md').read_bytes()
ledger_before = json.loads((HERE/'ledger-before.json').read_bytes())
check('ledger prefix unchanged', sha256(raw_ledger[:ledger_before['bytes']]).hexdigest() == ledger_before['sha256'])
check('ledger exact append', raw_ledger[ledger_before['bytes']:] == (HERE/'ledger-entry.md').read_bytes())
for name in ('README.md', 'study2/README.md', 'study2/colab/README.md', 'throughline/PROJECT.md'):
    old = (HERE/'navigation-before'/name).read_text()
    new = (ROOT/name).read_text()
    check('nav saved '+name, (ROOT/name).read_bytes() == (HERE/'navigation-after'/name).read_bytes())
    title, body = old.split('\n', 1)
    check('nav old body '+name, new.startswith(title+'\n') and new.endswith(body))
    check('nav latest '+name, '台帳§326' in new.split('\n\n')[1])
report = ROOT/'study2/own-summary-01-boundary-audit-2026-09-28.md'
check('report copy', report.read_bytes() == (HERE/'report.md').read_bytes())
for target in re.findall(r'\]\(([^)]+)\)', report.read_text()):
    check('report link '+target, (report.parent/target).exists())
comp = json.loads((HERE/'analysis/comparison.json').read_bytes())
reference = json.loads((HERE/'analysis/reference-summary.json').read_bytes())
check('receipt counts', comp['candidate_status_counts'] == {'UNCHANGED': 328, 'QUARANTINED': 56})
check('semantic counts', (comp['quarantined_required_semantics_correct'], comp['quarantined_required_semantics_incorrect']) == (54, 2))
check('numeric error count', comp['extra_numeric_rows_incorrect'] == 20)
check('model calls', comp['model_calls'] == 0)
check('no promotion', reference['operational_promotion'] is False)
for formation in ('F0', 'F1'):
    expected = {'U0': {'U_target': (31, 1), 'U_peer': (32, 0), 'J': (28, 4), 'Q': (13, 3), 'S_target': (15, 1), 'I_peer': (16, 0)},
                'U1': {'U_target': (32, 0), 'U_peer': (32, 0), 'J': (29, 3), 'Q': (13, 3), 'S_target': (16, 0), 'I_peer': (16, 0)}}
    for use, metrics in expected.items():
        for k, values in metrics.items():
            actual = reference['metrics'][formation+'_'+use][k]
            check('reported '+formation+use+k, (actual['correct'], actual['incorrect'], actual['unresolved']) == (*values, 0))
    comparison = reference['comparisons']['utilization'][formation]
    check('paired difference '+formation, comparison['paired_categories']['WITH_ONLY'] == 1 and comparison['difference_missing_bounds'] == [1/32, 1/32])
    cells = [c for c in reference['paths'] if c['formation'] == formation and c['root'] == 'M12']
    m12 = {(c['use'], c['arm']): c['J'] for c in cells}
    check('M12 overlap '+formation, m12 == {('U0', 'REVERSE'): False, ('U1', 'REVERSE'): True, ('U0', 'REINFORCE'): False, ('U1', 'REINFORCE'): False})
check('tests passed', 'Ran 20 tests' in (HERE/'test-attempt-01.log').read_text() and (HERE/'test-attempt-01.log').read_text().rstrip().endswith('OK'))
check('audit passed', json.loads((HERE/'analysis/checks.json').read_bytes())['count'] == 8984)
check('candidate artifacts', len(list((HERE/'analysis/candidates').glob('*.json'))) == len(list((HERE/'analysis/quarantine').glob('*.json'))) == 56)
result = {'status': 'PASS', 'checks': len(checks), 'details': checks}
with (HERE/'delivery-check.json').open('x') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
with (HERE/'MANIFEST.json').open('x') as f:
    files = {str(p.relative_to(HERE)): digest(p) for p in sorted(HERE.rglob('*'))
             if p.is_file() and '__pycache__' not in p.parts and p != HERE/'MANIFEST.json'}
    json.dump(files, f, ensure_ascii=False, indent=2)
print(json.dumps({'status': 'PASS', 'delivery_checks': len(checks), 'sealed_files': len(files)}))
