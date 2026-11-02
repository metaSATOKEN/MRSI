"""Independent raw-answer audit and descriptive diagnostics; no archived code imports."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

A = Path(__file__).resolve().parent
S = A / 'received'


def load(p):
    return json.loads(p.read_bytes())


def choose(coverage):
    available = {m.upper() for m in ('paper', 'digital')
                 if {coverage[r][m] for r in ('A', 'B')} == {'ALL'}}
    return next(iter(available)) if len(available) == 1 else 'UNKNOWN'


def write(name, value):
    (A / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


design = load(S / 'design.json')
requests = load(S / 'requests.json')
report = load(A / 'recomputed.json')['report']
by_id = {r['id']: r for r in report['by_response']}
cases = {c['id']: c for c in design['cases']}
rows = []
for slot, request in zip(design['allocation'], requests):
    folder = S / 'responses' / slot['id']
    case = cases[slot['case']]
    saved_input = load(folder / 'input.json')
    response = load(folder / 'response.json')
    answer = load(folder / 'answer.txt')
    assert {k: saved_input[k] for k in request} == request
    rendered = ''.join('<|im_start|>' + m['role'] + '\n' + m['content'].strip() + '<|im_end|>\n'
                       for m in request['messages']) + '<|im_start|>assistant\n<think>\n\n</think>\n\n'
    assert saved_input['prepared']['rendered_prompt'] == rendered
    assert response['finish_reason'] == 'EOS'
    assert response['output_token_ids'][-1] == 248046
    assert response['decoded_with_special_tokens'] == response['answer_text'] + '<|im_end|>'
    assert (folder / 'answer.txt').read_bytes() == response['answer_text'].encode()
    # Derive truth from the original GROUP record, not the design's gold label.
    group = next(r for r in case['notes_payload']['records'] if r['record_id'] == 'GROUP')
    original = {r: {m: group['body']['coverage'][r][m] for m in ('paper', 'digital')} for r in ('A', 'B')}
    assert original == case['rule_payload']['coverage'] == case['gold']['four_values']
    truth = choose(original)
    assert truth == case['gold']['channel']
    assert all(x == 'ALL' or x == 'NOT_ALL' for r in original.values() for x in r.values())
    if slot['condition'] == 'EXTRACT':
        four = answer['coverage']
        fields = {r + '.' + m: four[r][m] == original[r][m] for r in ('A', 'B') for m in ('paper', 'digital')}
        exact = all(fields.values())
        output = choose(four)
        derived = load(folder / 'derived-decision.json')
        assert derived['extracted_values'] == four
        assert derived['channel'] == output
        assert derived['answer_sha256'] == sha256((folder / 'answer.txt').read_bytes()).hexdigest()
        assert by_id[slot['id']]['score']['fields'] == fields
        assert by_id[slot['id']]['score']['four_exact'] == exact
    else:
        four, exact = None, None
        output = answer['decision']['channel']
    correct = output == truth
    assert by_id[slot['id']]['score']['channel_output'] == output
    assert by_id[slot['id']]['score']['channel'] == correct
    assert by_id[slot['id']]['score']['format_valid'] is True
    rows.append(dict(slot, role=case['role'], truth=truth, output=output, correct=correct,
                     pattern=case['pattern'], four_exact=exact, four=four,
                     input_tokens=len(saved_input['prepared']['input_ids']),
                     output_tokens=len(response['output_token_ids']), seconds=response['generation_seconds']))

counts = {}
for method in ('DIRECT', 'EXTRACT', 'RULE'):
    selected = [r for r in rows if r['condition'] == method]
    main = [r for r in selected if r['set'] == 'MAIN']
    assert sum(r['correct'] for r in main) == report['methods'][method]['main']['correct']
    counts[method] = {'main_correct': sum(r['correct'] for r in main), 'main_n': len(main),
                     'all_correct': sum(r['correct'] for r in selected),
                     'main_outputs': dict(Counter(r['output'] for r in main)),
                     'main_repeat_output_changed_materials': sum(
                         len({r['output'] for r in main if r['case'] == c}) > 1 for c in {r['case'] for r in main}),
                     'all_input_tokens': sum(r['input_tokens'] for r in selected),
                     'all_output_tokens': sum(r['output_tokens'] for r in selected),
                     'generation_seconds': sum(r['seconds'] for r in selected)}

contrasts = {}
for method in ('EXTRACT', 'RULE'):
    paired = []
    for before in (r for r in rows if r['set'] == 'MAIN' and r['condition'] == 'DIRECT'):
        after = next(r for r in rows if r['case'] == before['case'] and r['replicate'] == before['replicate'] and r['condition'] == method)
        paired.append({'case': before['case'], 'replicate': before['replicate'], 'truth': before['truth'],
                       'before': before['correct'], 'after': after['correct'], 'difference': int(after['correct']) - int(before['correct'])})
    contrasts[method + '-DIRECT'] = {
        'paired_correctness': dict(Counter(str(r['before']) + '->' + str(r['after']) for r in paired)),
        'net_correct': sum(r['difference'] for r in paired),
        'by_replicate': {str(rep): sum(r['difference'] for r in paired if r['replicate'] == rep) for rep in (1, 2)},
        'by_truth': {truth: sum(r['difference'] for r in paired if r['truth'] == truth) for truth in ('PAPER', 'DIGITAL')}}

patterns = []
for pattern in sorted({r['pattern'] for r in rows}):
    matching = [r for r in rows if r['pattern'] == pattern]
    cases_here = sorted({r['case'] for r in matching})
    rule_input_texts = {load(S / 'responses' / r['id'] / 'input.json')['messages'][1]['content']
                       for r in matching if r['condition'] == 'RULE'}
    rule_input_ids = {tuple(load(S / 'responses' / r['id'] / 'input.json')['prepared']['input_ids'])
                      for r in matching if r['condition'] == 'RULE'}
    assert len(rule_input_texts) == len(rule_input_ids) == 1
    pattern_row = {'pattern': pattern, 'cases': cases_here, 'set': matching[0]['set'], 'truth': matching[0]['truth'],
                   'coverage': cases[cases_here[0]]['rule_payload']['coverage'], 'methods': {}}
    for method in ('DIRECT', 'EXTRACT', 'RULE'):
        subset = [r for r in matching if r['condition'] == method]
        assert len(subset) == 4
        pattern_row['methods'][method] = {'correct': sum(r['correct'] for r in subset), 'n': 4,
                                          'outputs': dict(Counter(r['output'] for r in subset))}
    patterns.append(pattern_row)

extracts = [r for r in rows if r['condition'] == 'EXTRACT']
assert all(r['four_exact'] for r in extracts)
assert len(rows) == 96 and len(extracts) == 32
elapsed = load(S / 'run-end.json')['elapsed_seconds']
generation = sum(r['seconds'] for r in rows)
result = {'kind': 'INDEPENDENT_OFFLINE_RAW_ANSWER_AUDIT', 'checked_responses': 96,
          'exact_extraction_responses': 32, 'exact_extraction_field_values': 128,
          'methods': counts, 'contrasts': contrasts, 'patterns': patterns,
          'elapsed_seconds': elapsed, 'generation_seconds': generation, 'other_seconds': elapsed - generation,
          'environment': load(S / 'environment.json'), 'rows': rows,
          'no_p_value_or_population_ci': True, 'model_calls_during_audit': 0}
write('diagnostics.json', result)
examples = []
for prefix in ('RS01-M01-R1', 'RS01-M08-R1', 'RS01-B03-R1'):
    cs = cases[prefix.rsplit('-R', 1)[0]]
    example = {'id': prefix, 'correct_four': cs['rule_payload']['coverage'], 'gold': cs['gold']['channel'], 'conditions': {}}
    for method in ('DIRECT', 'EXTRACT', 'RULE'):
        folder = S / 'responses' / (prefix + '-' + method)
        paths = ['input.json', 'answer.txt', 'result.json'] + (['derived-decision.json'] if method == 'EXTRACT' else [])
        example['conditions'][method] = {'raw': (folder / 'answer.txt').read_text(),
             'input': load(folder / 'input.json')['messages'],
             'evidence_sha256': {str((folder / p).relative_to(A)): sha256((folder / p).read_bytes()).hexdigest() for p in paths}}
    examples.append(example)
write('examples.json', examples)
print(json.dumps({k: result[k] for k in ('checked_responses', 'exact_extraction_responses', 'methods', 'contrasts',
                                       'elapsed_seconds', 'generation_seconds', 'other_seconds')}, ensure_ascii=False, indent=2))
