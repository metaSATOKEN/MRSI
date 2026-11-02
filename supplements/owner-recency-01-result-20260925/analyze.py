"""Independent, stdlib-only audit of OR01 returned evidence. No archived code execution."""
import collections
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REC = HERE / 'received'

def read(path):
    return json.loads(path.read_text())

def sha(data):
    return hashlib.sha256(data).hexdigest()

def write(name, value):
    with (HERE / name).open('x') as out:
        json.dump(value, out, ensure_ascii=False, indent=2)
        out.write('\n')

def four(memory):
    return {o: {k: memory['shared_note']['coverage'][o][k] for k in ('paper', 'digital')}
            for o in ('A', 'B')}

def channel(values):
    paper = all(values[o]['paper'] == 'ALL' for o in ('A', 'B'))
    digital = all(values[o]['digital'] == 'ALL' for o in ('A', 'B'))
    return 'PAPER' if paper and not digital else 'DIGITAL' if digital and not paper else 'UNKNOWN'

def payload(messages):
    return json.loads(messages[-1]['content'].split('資料JSON:\n', 1)[1])

design = read(REC / 'design.json')
assert (REC / 'design.json').read_bytes() == (ROOT / 'study2/designs/owner-recency-01-20260925/design.json').read_bytes()
cases = {x['id']: x for x in design['cases']}
report = read(HERE / 'recomputed.json')['report']
for f in REC.glob('report-*.json'):
    assert read(f) == report
assert len(list(REC.glob('report-*.json'))) == 2

source_hashes = {}
for case in cases.values():
    for path, digest in case['source_files_sha256'].items():
        assert sha((ROOT / path).read_bytes()) == digest
        source_hashes[path] = digest
    p = case['update_payload']
    records = {x['record_id']: x['body'] for x in p['records']}
    sources = {'PRIVATE.coverage': records['PRIVATE']['coverage'],
               'GROUP.coverage.A': records['GROUP']['coverage']['A'],
               'GROUP.coverage.B': records['GROUP']['coverage']['B'], 'NOTICE': p['incoming_notice']}
    assert {c['location']: c['row'] for c in p['row_catalog']} == sources
    for source in case['source_files_sha256']:
        if source.endswith('/saved-memory.json'):
            saved = read(ROOT / source)
            assert saved == {'private_note': records['PRIVATE'], 'shared_note': records['GROUP']}

physical = {}
normalization = collections.Counter()
for folder in sorted((REC / 'responses').iterdir()):
    result, response = read(folder / 'result.json'), read(folder / 'response.json')
    assert result['status'] == response['finish_reason'] == 'EOS'
    for name, digest in result['files_sha256'].items():
        assert sha((folder / name).read_bytes()) == digest
    raw = (folder / 'answer.txt').read_bytes()
    assert response['answer_text'].encode() == raw
    try:
        obj = json.loads(raw)
        normalized, status = raw, 'UNCHANGED'
    except json.JSONDecodeError:
        assert raw.startswith(b'```json\n') and raw.endswith(b'\n```')
        normalized, status = raw[8:-4], 'UNWRAPPED'
        obj = json.loads(normalized)
    assert (folder / 'normalized-answer.txt').read_bytes() == normalized
    norm = read(folder / 'normalization.json')
    assert norm['status'] == status and norm['value_repair'] is False
    assert norm['raw_sha256'] == sha(raw) and norm['normalized_sha256'] == sha(normalized)
    stage = 'UPDATE' if folder.name.endswith('-UPDATE') else 'READ'
    normalization[stage + ':' + status] += 1
    assert len(raw) <= (16384 if stage == 'UPDATE' else 4096)
    inp = read(folder / 'input.json')
    assert read(folder / 'started.json')['seed'] == inp['seed']
    physical[folder.name] = dict(answer=obj, input=inp, response=response, status=status)

rows, failures, parent_read_counts = [], [], collections.Counter()
read_usage, observed_read_ids = collections.Counter(), set()
format_by_quality = collections.Counter()
for parent in design['parents']:
    pid = parent['id']
    case = cases[parent['case']]
    p = case['update_payload']
    update = physical[pid + '-UPDATE']
    assert update['input']['seed'] == parent['update_seed']
    assert payload(update['input']['messages']) == p
    proposal = update['answer']
    catalog = p['row_catalog']
    latest, selected = {}, {}
    for owner in ('A', 'B'):
        candidates = [c for c in catalog if c['row']['observer'] == owner]
        revision = max(c['row']['revision'] for c in candidates)
        ties = sorted([c for c in candidates if c['row']['revision'] == revision], key=lambda c: c['row_id'])
        assert all(c['row'] == ties[0]['row'] for c in ties)
        latest[owner], selected[owner] = ties[0]['row'], ties[0]
    original_private = next(x['body'] for x in p['records'] if x['record_id'] == 'PRIVATE')
    expected = {'private_note': {'customer': original_private['customer'], 'coverage': latest[p['holder']]},
                'shared_note': {'coverage': latest}}
    assert expected == case['expected_memory']
    assert original_private['coverage'] == latest[p['holder']]
    assert channel(four(expected)) == case['latest_channel']
    assert proposal['private_note']['coverage']['observer'] == p['holder']
    assert proposal['private_note']['customer'] == original_private['customer']
    shared_bad = [o for o in ('A', 'B') if proposal['shared_note']['coverage'][o] != latest[o]]
    for o in ('A', 'B'):
        assert any(proposal['shared_note']['coverage'][o] == c['row'] for c in catalog)
    private_bad = proposal['private_note']['coverage'] != latest[p['holder']]
    format_by_quality[update['status'] + (':correct' if proposal == expected else ':incorrect')] += 1
    if proposal != expected:
        failures.append({'parent': pid, 'case': case['id'], 'source_group': case['source_group'],
                         'set': case['set'], 'holder': p['holder'], 'shared_bad': shared_bad,
                         'private_bad': private_bad, 'proposal': proposal, 'expected': expected,
                         'notice': p['incoming_notice'], 'channel_output': channel(four(proposal)),
                         'channel_latest': case['latest_channel']})
        for o in shared_bad:
            if case['set'] == 'GUARD':
                assert proposal['shared_note']['coverage'][o] == p['incoming_notice']
            else:
                assert proposal['shared_note']['coverage'][o] == next(x['body'] for x in p['records'] if x['record_id'] == 'GROUP')['coverage'][o]
        if private_bad:
            assert case['set'] == 'GUARD' and proposal['private_note']['coverage'] == p['incoming_notice']
    plan = read(REC / 'parents' / pid / 'read-plan.json')
    parent_read_counts[len(plan)] += 1
    assert sorted(a for entry in plan for a in entry['arms']) == ['G0P0', 'G0P1', 'G1P0', 'G1P1']
    identities = []
    for entry in plan:
        rid = entry['id']
        assert rid not in observed_read_ids
        observed_read_ids.add(rid)
        phys = physical[rid]
        assert entry['seed'] == parent['read_seed'] == phys['input']['seed']
        assert entry['model'] == design['model'] and entry['schema'] == design['read_schema']
        assert entry['messages'] == phys['input']['messages']
        identities.append(json.dumps({k: entry[k] for k in ('messages', 'model', 'schema', 'seed')}, sort_keys=True))
        binding = phys['input']['binding']
        assert binding['update_result_sha256'] == sha((REC / 'responses' / (pid + '-UPDATE') / 'result.json').read_bytes())
        for arm in entry['arms']:
            bd = REC / 'branches' / (pid + '-' + arm)
            saved, branch, logical = read(bd / 'saved-memory.json'), read(bd / 'branch.json'), read(bd / 'logical-result.json')
            rebuilt = copy.deepcopy(proposal)
            if arm[1] == '1':
                rebuilt['shared_note']['coverage'] = copy.deepcopy(latest)
            if arm[3] == '1':
                rebuilt['private_note']['coverage'] = copy.deepcopy(latest[p['holder']])
            assert saved == rebuilt
            assert branch['saved_memory_sha256'] == binding['branches'][arm]['saved_memory_sha256'] == sha((bd / 'saved-memory.json').read_bytes())
            assert logical['physical_read_id'] == rid
            assert logical['physical_result_sha256'] == sha((REC / 'responses' / rid / 'result.json').read_bytes())
            assert logical['branch_json_sha256'] == binding['branches'][arm]['branch_json_sha256'] == sha((bd / 'branch.json').read_bytes())
            rp = payload(entry['messages'])
            assert rp == {k: p[k] for k in ('holder', 'scene', 'item')} | {'records': [
                {'record_id': 'PRIVATE', 'body': saved['private_note']}, {'record_id': 'GROUP', 'body': saved['shared_note']}]}
            assert phys['answer'] == {'coverage': four(saved)}
            actual_channel = channel(phys['answer']['coverage'])
            assert logical['read']['channel_output'] == actual_channel
            joint = saved == expected
            assert branch['score']['joint_state_exact'] == joint
            assert logical['read']['four_exact'] is True
            assert logical['read']['channel_latest'] == (actual_channel == case['latest_channel'])
            rows.append({'parent': pid, 'case': case['id'], 'set': case['set'], 'replicate': parent['replicate'],
                         'arm': arm, 'read_id': rid, 'joint': joint, 'channel_latest': actual_channel == case['latest_channel'],
                         'private': saved['private_note']['coverage'] == expected['private_note']['coverage'],
                         'shared': saved['shared_note'] == expected['shared_note']})
            read_usage[rid] += 1
    assert len(identities) == len(set(identities))

totals = {}
for arm in ('G0P0', 'G1P0', 'G0P1', 'G1P1'):
    ar = [r for r in rows if r['arm'] == arm]
    totals[arm] = {k: sum(r[k] for r in ar) for k in ('joint', 'channel_latest', 'private', 'shared')}
    for subset in ('REPAIR', 'GUARD'):
        subset_rows = [r for r in ar if r['set'] == subset]
        total = sum(r['joint'] for r in subset_rows)
        for metric in ('joint_state_exact', 'end_to_end_exact'):
            assert report['arms'][arm][metric]['by_set'][subset] == {'correct': total, 'incorrect': len(subset_rows)-total, 'unresolved': 0, 'n': len(subset_rows)}
            for rep in (1, 2):
                rr = [r for r in subset_rows if r['replicate'] == rep]
                assert report['arms'][arm][metric]['by_repeat'][subset][str(rep)]['correct'] == sum(r['joint'] for r in rr)

assert len(physical) == 91 and len(observed_read_ids) == 55 and len(rows) == 144
assert set(physical) == observed_read_ids | {p['id'] + '-UPDATE' for p in design['parents']}
write('source-hashes.json', source_hashes)
write('branch-diagnostics.json', rows)
write('failure-examples.json', failures)
verification = {'status': 'PASS', 'archived_reports_equal_recomputed': 2, 'source_files_checked': len(source_hashes),
                'physical_generations': len(physical), 'parents': len(design['parents']), 'unique_READ': len(observed_read_ids),
                'logical_READ': len(rows), 'totals': totals, 'normalization': dict(normalization),
                'update_format_by_quality': dict(format_by_quality), 'parent_unique_read_distribution': dict(parent_read_counts),
                'physical_read_use_distribution': dict(collections.Counter(read_usage.values())),
                'bad_parent_count': len(failures), 'private_bad_count': sum(x['private_bad'] for x in failures),
                'bad_memory_correct_channel': [x['parent'] for x in failures if x['channel_output'] == x['channel_latest']],
                'elapsed_seconds': read(REC / 'run-end.json')['elapsed_seconds'],
                'generation_seconds': sum(x['response']['generation_seconds'] for x in physical.values()),
                'scope': 'Saved evidence and deterministic rules; no new model generation; no archived executable imported.'}
write('independent-verification.json', verification)
print(json.dumps(verification, ensure_ascii=False, indent=2))
