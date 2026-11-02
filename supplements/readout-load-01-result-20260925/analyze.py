"""Independent descriptive audit of RL01 returned records; standard library only."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
received = HERE / 'received'
design = json.loads((received / 'design.json').read_text())
requests = json.loads((received / 'requests.json').read_text())
formal = json.loads((HERE / 'recomputed.json').read_text())['report']
cases = {c['id']: c for c in design['cases']}
slots = design['allocation']
rows = {}; per_method = {}; notes = []; examples = {}

for s, expected in zip(slots, requests):
    folder = received / 'responses' / s['id']
    inp = json.loads((folder / 'input.json').read_text())
    assert all(inp[k] == expected[k] for k in expected)
    assert inp['prepared']['input_ids'] and len(inp['prepared']['input_ids']) <= 8192
    # Recorded rendering trims surrounding message whitespace; verify the
    # entire string rather than assuming the trailing system newlines survive.
    rendered = ''.join('<|im_start|>' + m['role'] + '\n' + m['content'].strip() + '<|im_end|>\n'
                       for m in expected['messages']) + '<|im_start|>assistant\n<think>\n\n</think>\n\n'
    assert inp['prepared']['rendered_prompt'] == rendered
    response = json.loads((folder / 'response.json').read_text())
    result = json.loads((folder / 'result.json').read_text())
    raw = (folder / 'answer.txt').read_text()
    assert raw == response['answer_text'] and response['finish_reason'] == 'EOS'
    assert response['output_token_ids'][-1] == 248046
    answer = json.loads(raw)
    c = cases[s['case']]
    payload = json.loads(expected['messages'][1]['content'].split('資料JSON:\n', 1)[1])
    assert payload == c['payload']
    records = {r['record_id']: r['body'] for r in payload['records']}
    cov = records['GROUP']['coverage']
    possible = [medium.upper() for medium in ('paper', 'digital')
                if cov['A'][medium] == 'ALL' and cov['B'][medium] == 'ALL']
    truth = possible[0] if len(possible) == 1 else 'UNKNOWN'
    assert truth == c['gold']['channel']
    predicted = answer['decision']['channel']
    correct = predicted == truth
    assert correct == result['score']['channel']
    if s['condition'] != 'CHANNEL':
        mascot = answer['decision']['mascot'] == records['PRIVATE']['customer']['animal']
        assert mascot == result['score']['mascot']
    rows[s['id']] = dict(s, role=c['role'], truth=truth, predicted=predicted, correct=correct,
                        mascot=result['score']['mascot'], format=result['score']['format_valid'])
    if not result['score']['format_valid']:
        notes.append({'id': s['id'], 'errors': result['score']['errors'], 'answer': answer,
                      'truth': truth, 'channel_still_evaluable': True})
    if s['id'] in ('RL01-M02-R1-FULL', 'RL01-M12-R2-DUAL', 'RL01-B04-R1-FULL', 'RL01-B03-R2-CHANNEL'):
        examples[s['id']] = {'payload': payload, 'answer': answer, 'truth': truth,
                              'answer_sha256': sha256(raw.encode()).hexdigest()}

for method in ('FULL', 'DUAL', 'CHANNEL'):
    selected = [r for r in rows.values() if r['condition'] == method]
    main = [r for r in selected if r['set'] == 'MAIN']
    boundary = [r for r in selected if r['set'] == 'BOUNDARY']
    n_correct = sum(r['correct'] for r in main)
    assert n_correct == formal['methods'][method]['main']['correct']
    perf = formal['performance'][method]
    per_method[method] = {'main_correct': n_correct, 'main_n': len(main),
        'by_replicate': {str(rep): sum(r['correct'] for r in main if r['replicate'] == rep) for rep in (1, 2)},
        'by_truth': {truth: sum(r['correct'] for r in main if r['truth'] == truth) for truth in ('PAPER', 'DIGITAL')},
        'mascot_correct': sum(r['mascot'] is True for r in selected) if method != 'CHANNEL' else None,
        'boundary_correct': sum(r['correct'] for r in boundary),
        'predictions': dict(Counter(r['predicted'] for r in main)),
        'repeat_changed_main_cases': sum(
            rows[f'{c["id"]}-R1-{method}']['predicted'] != rows[f'{c["id"]}-R2-{method}']['predicted']
            for c in design['cases'] if c['set'] == 'MAIN'),
        'output_tokens': sum(perf['output_tokens']), 'generation_seconds': sum(perf['generation_seconds']),
        'mean_input_tokens': sum(perf['input_tokens']) / 32}

contrasts = {}
for later, earlier in (('DUAL', 'FULL'), ('CHANNEL', 'DUAL')):
    paired = Counter()
    for c in design['cases']:
        if c['set'] == 'MAIN':
            for rep in (1, 2):
                left = rows[f'{c["id"]}-R{rep}-{earlier}']['correct']
                right = rows[f'{c["id"]}-R{rep}-{later}']['correct']
                paired[f'{earlier}={left}|{later}={right}'] += 1
    contrasts[later + '-' + earlier] = dict(paired)

elapsed = json.loads((received / 'run-end.json').read_text())['elapsed_seconds']
generation = sum(x['generation_seconds'] for x in per_method.values())
result = {'kind': 'INDEPENDENT_RAW_RESPONSE_DESCRIPTIVE_AUDIT',
          'request_payloads_checked': 96, 'raw_answers_checked': 96, 'all_eos': True,
          'rendered_prompts_checked_after_boundary_whitespace_trim': 96,
          'all_channel_values_evaluable': True, 'scores_match_frozen_formal_report': True,
          'methods': per_method, 'paired_outcomes': contrasts, 'format_cases': notes,
          'elapsed_seconds': elapsed, 'generation_seconds': generation,
          'other_elapsed_seconds': elapsed - generation,
          'no_new_model_generation': True, 'p_value': None, 'confidence_interval': None}
(HERE / 'diagnostics.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
(HERE / 'examples.json').write_text(json.dumps(examples, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
