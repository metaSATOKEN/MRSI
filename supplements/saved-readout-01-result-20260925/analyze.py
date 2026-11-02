"""Independent raw-answer audit, using original saved inputs and latest notices. No model calls."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

A = Path(__file__).resolve().parent
ROOT = A.parents[2]
S = A / 'received'
sys.path.insert(0, str(ROOT / 'scripts'))
from aggregate_cross_model_e1_01 import load_payload


def load(path):
    return json.loads(path.read_bytes())


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def choose(coverage):
    available = {m.upper() for m in ('paper', 'digital')
                 if {coverage[r][m] for r in ('A', 'B')} == {'ALL'}}
    return next(iter(available)) if len(available) == 1 else 'UNKNOWN'


def four(coverage):
    return {r: {m: coverage[r][m] for m in ('paper', 'digital')} for r in ('A', 'B')}


def write(name, value):
    (A / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


design = load(S / 'design.json')
requests = load(S / 'requests.json')
report = load(A / 'recomputed.json')['report']
by_id = {r['id']: r for r in report['by_response']}
cases = {c['id']: c for c in design['cases']}
for path, expected in design['source_pins'].items():
    assert sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
original = load_payload(ROOT / 'study2/colab/cross_model_e1_01_main_onecell.py')
source_hashes = {}; truths = {}
for case in design['cases']:
    evidence = {}
    for path, expected in case['source_files_sha256'].items():
        raw = (ROOT / path).read_bytes()
        assert sha256(raw).hexdigest() == expected, path
        source_hashes[path] = expected
        evidence[Path(path).name] = json.loads(raw)
    assert evidence['result.json']['gate'] == 'PASS'
    payload = evidence['input.json']['payload']
    assert payload == case['notes_payload']
    assert sha256(canonical(payload)).hexdigest() == case['payload_sha256']
    bodies = {r['record_id']: r['body'] for r in payload['records']}
    assert bodies == {'PRIVATE': evidence['saved-memory.json']['private_note'], 'GROUP': evidence['saved-memory.json']['shared_note']}
    material = original['bundle']['materials'][case['source_group']]
    group = bodies['GROUP']['coverage']; latest = material['notices']
    note_four, latest_four = four(group), four(latest)
    assert all(x in ('ALL', 'NOT_ALL') for f in (note_four, latest_four) for r in f.values() for x in r.values())
    note_truth, latest_truth = choose(group), choose(latest)
    assert latest_truth == material['final_channel']
    assert case['gold'] == {'four_values': note_four, 'channel': note_truth, 'latest_four_values': latest_four, 'latest_channel': latest_truth}
    row_exact = {r: group[r] == latest[r] for r in ('A', 'B')}
    state = {'shared_latest_exact': all(row_exact.values()), 'shared_rows_latest_exact': row_exact,
             'private_customer_latest_exact': bodies['PRIVATE']['customer'] == material['baseline_by_role'][case['role']]['private_note']['customer'],
             'private_observation_latest_exact': bodies['PRIVATE']['coverage'] == latest[case['role']],
             'private_group_observation_conflict': bodies['PRIVATE']['coverage'] != group[case['role']],
             'stale_rows': [r for r in ('A', 'B') if not row_exact[r]],
             'saved_coverage': group, 'latest_coverage': latest, 'note_world_channel_agree': note_truth == latest_truth}
    assert state == case['note_state']
    truths[case['id']] = note_four, latest_four, note_truth, latest_truth

rows = []
for slot, request in zip(design['allocation'], requests):
    folder = S / 'responses' / slot['id']; case = cases[slot['case']]
    saved_input = load(folder / 'input.json'); response = load(folder / 'response.json'); answer = load(folder / 'answer.txt')
    assert {k: saved_input[k] for k in request} == request
    assert request['messages'] == [{'role': 'system', 'content': design['prompts'][slot['condition']]},
                                  {'role': 'user', 'content': '\n資料JSON:\n' + canonical(case['notes_payload']).decode()}]
    rendered = ''.join('<|im_start|>' + m['role'] + '\n' + m['content'].strip() + '<|im_end|>\n'
                       for m in request['messages']) + '<|im_start|>assistant\n<think>\n\n</think>\n\n'
    assert saved_input['prepared']['rendered_prompt'] == rendered
    assert response['seed'] == slot['seed'] == request['seed']
    assert response['finish_reason'] == 'EOS' and response['output_token_ids'][-1] == 248046
    assert response['decoded_with_special_tokens'] == response['answer_text'] + '<|im_end|>'
    assert (folder / 'answer.txt').read_bytes() == response['answer_text'].encode()
    note_four, latest_four, note_truth, latest_truth = truths[case['id']]
    fields = None
    if slot['condition'] == 'EXTRACT':
        assert set(answer) == {'coverage'} and set(answer['coverage']) == {'A', 'B'}
        values = answer['coverage']
        assert all(set(v) == {'paper', 'digital'} and all(x in ('ALL', 'NOT_ALL') for x in v.values()) for v in values.values())
        fields = {r + '.' + m: values[r][m] == note_four[r][m] for r in ('A', 'B') for m in ('paper', 'digital')}
        exact = all(fields.values()); latest_exact = values == latest_four; output = choose(values)
        derived = load(folder / 'derived-decision.json')
        assert derived['extracted_values'] == values and derived['four_valid'] is True and derived['channel'] == output
        assert derived['answer_sha256'] == sha256((folder / 'answer.txt').read_bytes()).hexdigest()
        assert derived['additional_model_requests'] == 0
    else:
        assert set(answer) == {'decision'} and set(answer['decision']) == {'channel'}
        output = answer['decision']['channel']; assert output in ('PAPER', 'DIGITAL', 'UNKNOWN')
        values = exact = latest_exact = None
    correct_note, correct_latest = output == note_truth, output == latest_truth
    score = by_id[slot['id']]['score']
    for k, expected in {'channel_output': output, 'channel': correct_note, 'channel_note': correct_note,
                        'channel_latest': correct_latest, 'four_exact': exact, 'four_latest_exact': latest_exact,
                        'fields': fields, 'format_valid': True}.items():
        assert score[k] == expected, (slot['id'], k)
    assert by_id[slot['id']]['note_state'] == case['note_state']
    rows.append(dict(slot, role=case['role'], source_group=case['source_group'], source_condition=case['source_condition'],
                     note_truth=note_truth, latest_truth=latest_truth, note_kind=case['note_kind'],
                     output=output, correct_note=correct_note, correct_latest=correct_latest,
                     pattern=case['pattern'], four_exact=exact, four_latest_exact=latest_exact,
                     input_tokens=len(saved_input['prepared']['input_ids']), output_tokens=len(response['output_token_ids']),
                     output_bytes=len(response['answer_text'].encode()), seconds=response['generation_seconds']))

counts = {}
for method in ('DIRECT', 'EXTRACT'):
    selected = [r for r in rows if r['condition'] == method]
    counts[method] = {}
    for subset in ('MAIN', 'STALE'):
        part = [r for r in selected if r['set'] == subset]
        note_count = sum(r['correct_note'] for r in part); latest_count = sum(r['correct_latest'] for r in part)
        assert note_count == report['methods'][method][subset.lower()]['correct']
        assert latest_count == report['latest_channel'][method][subset]['correct']
        counts[method][subset] = {'n': len(part), 'note_correct': note_count, 'latest_correct': latest_count,
             'outputs': dict(Counter(r['output'] for r in part)),
             'repeat_output_changed_materials': sum(len({r['output'] for r in part if r['case'] == c}) > 1 for c in {r['case'] for r in part}),
             'note_latest_cross': dict(Counter(str(r['correct_note']) + '|' + str(r['correct_latest']) for r in part))}
    counts[method]['all_input_tokens'] = sum(r['input_tokens'] for r in selected)
    counts[method]['all_output_tokens'] = sum(r['output_tokens'] for r in selected)
    counts[method]['generation_seconds'] = sum(r['seconds'] for r in selected)

paired = []
for before in (r for r in rows if r['set'] == 'MAIN' and r['condition'] == 'DIRECT'):
    after = next(r for r in rows if r['case'] == before['case'] and r['replicate'] == before['replicate'] and r['condition'] == 'EXTRACT')
    paired.append({'case': before['case'], 'replicate': before['replicate'], 'truth': before['note_truth'],
                   'before': before['correct_note'], 'after': after['correct_note'],
                   'difference': int(after['correct_note']) - int(before['correct_note'])})
contrast = {'paired_correctness': dict(Counter(str(r['before']) + '->' + str(r['after']) for r in paired)),
            'net_correct': sum(r['difference'] for r in paired),
            'by_replicate': {str(rep): sum(r['difference'] for r in paired if r['replicate'] == rep) for rep in (1, 2)},
            'by_truth': {t: sum(r['difference'] for r in paired if r['truth'] == t) for t in ('PAPER', 'DIGITAL')}}
assert contrast['net_correct'] / 32 == report['contrast']['bounds'][0] == report['contrast']['bounds'][1]

case_details = []
for c in design['cases']:
    part = [r for r in rows if r['case'] == c['id']]
    case_details.append({k: c[k] for k in ('id', 'set', 'source_group', 'source_condition', 'role', 'note_kind', 'pattern', 'note_state', 'gold')} |
        {'outputs': {m: [r['output'] for r in part if r['condition'] == m] for m in ('DIRECT', 'EXTRACT')}})
assert len(rows) == 104 and sum(r['four_exact'] is True for r in rows) == 52
elapsed = load(S / 'run-end.json')['elapsed_seconds']; generation = sum(r['seconds'] for r in rows)
result = {'kind': 'INDEPENDENT_OFFLINE_RAW_ANSWER_AND_SOURCE_AUDIT', 'checked_responses': 104,
          'exact_extraction_responses': 52, 'exact_extraction_field_values': 208,
          'source_files_checked': len(source_hashes), 'methods': counts, 'contrast': contrast,
          'elapsed_seconds': elapsed, 'generation_seconds': generation, 'other_seconds': elapsed - generation,
          'environment': load(S / 'environment.json'), 'rows': rows, 'cases': case_details,
          'model_calls_during_audit': 0, 'p_value': None, 'confidence_interval': None}
write('diagnostics.json', result); write('source-hashes.json', source_hashes)
# Representative examples chosen after scoring, for illustration only.
main_example = next(r['case'] for r in rows if r['set'] == 'MAIN' and r['condition'] == 'DIRECT' and not r['correct_note'])
stale_example = next(c['id'] for c in design['cases'] if c['set'] == 'STALE' and not c['note_state']['note_world_channel_agree'] and not c['note_state']['private_group_observation_conflict'])
conflict_example = next(c['id'] for c in design['cases'] if c['note_state']['private_group_observation_conflict'])
examples = []
for case_id in (main_example, stale_example, conflict_example):
    c = cases[case_id]
    ex = {'case': case_id, 'source_group': c['source_group'], 'role': c['role'], 'gold': c['gold'], 'note_state': c['note_state'], 'conditions': {}}
    for method in ('DIRECT', 'EXTRACT'):
        folder = S / 'responses' / f'{case_id}-R1-{method}'
        names = ['input.json','answer.txt','result.json'] + (['derived-decision.json'] if method == 'EXTRACT' else [])
        ex['conditions'][method] = {'raw': (folder / 'answer.txt').read_text(), 'input': load(folder / 'input.json')['messages'],
           'evidence_sha256': {str((folder / p).relative_to(A)):sha256((folder / p).read_bytes()).hexdigest() for p in names}}
    examples.append(ex)
write('examples.json', examples)
print(json.dumps({k: result[k] for k in ('checked_responses', 'exact_extraction_responses', 'source_files_checked', 'methods', 'contrast', 'elapsed_seconds', 'generation_seconds', 'other_seconds')}, ensure_ascii=False, indent=2))
