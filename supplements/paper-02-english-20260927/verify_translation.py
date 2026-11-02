"""Offline transcription/asset checks against the finalized Japanese manuscript.

No research inference, rescoring, archive execution, or network access.
Mechanical correspondence does not establish translation quality by itself.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
AUDIT = Path(__file__).resolve().parent
PAPER = ROOT / 'papers/paper-02'
JA = PAPER / 'manuscript-ja-v0.4-2026-09-27.md'
EN = PAPER / 'manuscript-en-v0.1-2026-09-27.md'
j, e = JA.read_text(), EN.read_text()
checks = []


def check(name, actual, expected):
    checks.append({'check': name, 'actual': actual, 'expected': expected,
                   'pass': actual == expected})


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tables(text):
    return [[row.strip('|').split('|') for row in block.splitlines()
             if not re.fullmatch(r'[| :\-]+', row)]
            for block in re.findall(r'(?m)^\|.*(?:\n\|.*)*', text)]


def numbers(cell):
    # Table 5 uses the English word "twice" for Japanese "2 repetitions".
    cell = cell.replace('twice', '2')
    return re.findall(r'(?<![A-Za-z\d])\d[\d,]*(?:\.\d+)*(?:/\d+)?', cell)


approval = load(AUDIT / 'japanese-final-approval.json')
check('approved Japanese source unchanged', sha(JA), approval['sha256'])
anchors = load(AUDIT / 'anchors-before.json')
mutable = {'README.md', 'study2/README.md', 'throughline/PROJECT.md', 'papers/paper-02/README.md'}
immutable = {p: h for p, h in anchors.items() if p not in mutable}
changed = [p for p, h in immutable.items() if not (ROOT / p).is_file() or sha(ROOT / p) != h]
check('immutable source anchors', changed, [])
prior = ROOT / 'throughline/audits/paper-02-revision-v04-20260927'
prior_manifest = load(prior / 'MANIFEST.json')
check('prior Japanese v0.4 audit seal', [p for p, h in prior_manifest.items() if sha(prior / p) != h], [])
ledger = (ROOT / 'throughline/audits/ledger-2026-09.md').read_bytes()
before = load(AUDIT / 'ledger-before.json')
check('old ledger prefix unchanged', hashlib.sha256(ledger[:before['bytes']]).hexdigest(), before['sha256'])

check('numbered section/subsection coverage', re.findall(r'^#{2,3} (\d+(?:\.\d+)?)', e, re.M),
      re.findall(r'^#{2,3} (\d+(?:\.\d+)?)', j, re.M))
check('appendix subsection coverage', re.findall(r'^### ([AB]\.\d+)', e, re.M),
      re.findall(r'^### ([AB]\.\d+)', j, re.M))
check('table caption numbering', re.findall(r'^\*\*Table (\d+)\.', e, re.M), [str(n) for n in range(1, 11)])
jt, et = tables(j), tables(e)
check('all table blocks including Appendix B', [len(jt), len(et)], [11, 11])
numeric_cells = 0
for t, (ja_table, en_table) in enumerate(zip(jt, et), 1):
    check(f'table {t} row and column structure', [len(row) for row in en_table], [len(row) for row in ja_table])
    differences = []
    for r, (ja_row, en_row) in enumerate(zip(ja_table, en_table)):
        for c, (ja_cell, en_cell) in enumerate(zip(ja_row, en_row)):
            a, b = numbers(ja_cell), numbers(en_cell)
            if a or b:
                numeric_cells += 1
            if a != b:
                differences.append({'row': r, 'column': c, 'ja': a, 'en': b})
    check(f'table {t} numeric cells', differences, [])

fraction_pattern = r'(?<![A-Za-z0-9])\d+/\d+(?![A-Za-z0-9])'
ja_fractions = Counter(re.findall(fraction_pattern, j))
en_fractions = Counter(re.findall(fraction_pattern, e))
check('fraction notation differences', [dict(ja_fractions - en_fractions), dict(en_fractions - ja_fractions)],
      [{'32/32': 2}, {}])
check('two all-32 equivalents preserve the fractions',
      ['all 32 final shared readouts succeeded' in e, 'final joint guidance was correct in all 32 responses' in e], [True, True])
check('literal code/ID tokens unchanged', Counter(re.findall(r'`([^`\n]+)`', e)), Counter(re.findall(r'`([^`\n]+)`', j)))
check('JSON example unchanged', re.findall(r'```json\n(.*?)\n```', e, re.S), re.findall(r'```json\n(.*?)\n```', j, re.S))
check('all external URLs and occurrence counts', Counter(re.findall(r'\]\((https?://[^)]+)\)', e)),
      Counter(re.findall(r'\]\((https?://[^)]+)\)', j)))
check('reference count and order', re.findall(r'^(\d+)\. ', e.split('## References\n')[1].split('## Appendix')[0], re.M), [str(i) for i in range(1, 21)])
check('author and contact', all(x in e for x in ['Kentaro Sato', 'Independent Researcher', '`info@mataclan.jp`']), True)
check('English manuscript has no untranslated CJK text', bool(re.search(r'[\u3040-\u30ff\u3400-\u9fff]', e)), False)
check('abstract proposal denominator retained', '18 previously used materials with two repetitions each' in e.split('## 1.')[0], True)
check('abstract diagnostic denominator retained', 'eight new cases with two repetitions each' in e.split('## 1.')[0], True)
check('model and customer-field scopes retained', all(x in e for x in [
    'same Qwen3.5-27B model as two roles in separate contexts',
    'Customer information remains model-written in every condition',
    'Semantic scoring did not use a separate LLM judge',
    'The storage controller never receives the expected state used for scoring',
    'The second cycle begins with the notes actually saved in the first cycle, not the manipulated notes',
    'no p-values or population confidence intervals are calculated']), True)

# English evidence index preserves the original seven archives and their hashes.
index = (PAPER / 'evidence-index-en-v0.1-2026-09-27.md').read_text()
ja_index = (PAPER / 'evidence-index-v0.4-2026-09-27.md').read_text()
check('archive hash table unchanged', re.findall(r'`([a-f0-9]{64})`', index), re.findall(r'`([a-f0-9]{64})`', ja_index))
sources = load(AUDIT / 'evidence-sources.json')
zip_links = re.findall(r'\]\(([^)]+\.zip)\)', index)
zip_hashes = [sha((PAPER / p).resolve()) for p in zip_links]
check('seven original archive hashes match the index', zip_hashes, re.findall(r'`([a-f0-9]{64})`', index))
check('source trials mapped in English S1', all(s['trial'] in index for s in sources), True)

deliverable_md = [EN, PAPER / 'evidence-index-en-v0.1-2026-09-27.md',
                  PAPER / 'translation-notes-en-v0.1-2026-09-27.md', PAPER / 'figures/README.md', PAPER / 'README.md']
broken, local_count = [], 0
future_output = AUDIT / 'verification.json'
for p in deliverable_md:
    for target in re.findall(r'\]\(([^)]+)\)', p.read_text()):
        if target.startswith(('http:', 'https:', 'mailto:', '#')):
            continue
        dest = (p.parent / target.split('#', 1)[0]).resolve()
        local_count += 1
        if not dest.exists() and dest != future_output:
            broken.append({'source': str(p.relative_to(ROOT)), 'target': target})
check('relative deliverable links resolve', broken, [])

figure_records = []
for stem, expected_size in [('fig01-update-control-en-v1', (4350, 3030)),
                            ('fig02-study-connections-en-v1', (4350, 2850))]:
    png, svg = [PAPER / 'figures' / f'{stem}.{ext}' for ext in ['png', 'svg']]
    with Image.open(png) as im:
        size, dpi = im.size, im.info.get('dpi')
        check(stem + ' PNG dimensions', list(size), list(expected_size))
        check(stem + ' 300-dpi metadata', all(abs(d - 300) < .1 for d in dpi), True)
    xml = ET.parse(svg).getroot()
    check(stem + ' SVG root', xml.tag, '{http://www.w3.org/2000/svg}svg')
    external = [v for node in xml.iter() for k, v in node.attrib.items() if k.endswith('href') and not v.startswith('#')]
    check(stem + ' SVG resources are self-contained', external, [])
    check(stem + ' PNG is embedded in manuscript', f'figures/{stem}.png' in e, True)
    figure_records.append({'name': stem, 'png_size': size, 'png_dpi': dpi,
                           'png_sha256': sha(png), 'svg_sha256': sha(svg)})
fit = load(PAPER / 'figures/layout-checks-en-v1.json')
check('figure text fits boxes', all(c['inside_box'] for f in fit for c in f['checks']), True)
check('English body has exactly two image figures', len(re.findall(r'!\[[^\]]*\]\(figures/', e)), 2)
check('no PDF in paper-02', list(str(p.relative_to(PAPER)) for p in PAPER.rglob('*.pdf')), [])

result = {'status': 'PASS' if all(c['pass'] for c in checks) else 'FAIL',
          'checks': len(checks), 'passed': sum(c['pass'] for c in checks),
          'immutable_anchors': len(immutable), 'prior_sealed_files': len(prior_manifest),
          'table_numeric_cells': numeric_cells, 'local_links': local_count,
          'figures': figure_records, 'research_inference_calls': 0, 'research_rescoring': 0,
          'method': 'Source-hash, section/table, literal-example, URL, archive, link and asset checks; editorial meaning review recorded separately.',
          'details': checks}
(AUDIT / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k not in ['details', 'figures']}, ensure_ascii=False))
for row in checks:
    if not row['pass']:
        print(json.dumps(row, ensure_ascii=False))
assert result['status'] == 'PASS'
