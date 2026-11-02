"""Post-run cross-check using stdlib only; no experiment scorer or model imports.

This is a separately implemented check within the same project, not an
independent replication. The raw archive and the preregistered score stay fixed.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import shutil
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESULT = ROOT / 'study2/results/three-role-vote-repeat-01-20261013'
ARCHIVE = ROOT / 'npp-tvr01-result-20261013-045940-cf404568.zip'
CHECKS = Counter()


def check(ok, category, detail=''):
    if not ok:
        raise AssertionError((category, detail))
    CHECKS[category] += 1


def pairs(items):
    d = {}
    for k, v in items:
        check(k not in d, 'unique_json_key', k)
        d[k] = v
    return d


def parse(raw):
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def shape(obj, schema):
    t = schema['type']
    if t == 'object':
        check(type(obj) is dict and set(obj) == set(schema['required']), 'schema_object')
        for k, v in obj.items(): shape(v, schema['properties'][k])
    elif t == 'array':
        check(type(obj) is list and schema['minItems'] <= len(obj) <= schema['maxItems'], 'schema_array')
        for v in obj: shape(v, schema['items'])
    else:
        check(type(obj) is str, 'schema_string')
        check(obj in schema['enum'] if 'enum' in schema else schema['minLength'] <= len(obj) <= schema['maxLength'], 'schema_value')


def main():
    with zipfile.ZipFile(ARCHIVE) as z:
        names = z.namelist()
        check(len(names) == len(set(names)), 'unique_archive_members')
        files = {n: z.read(n) for n in names}
    manifest = parse(files.pop('FEEDBACK_MANIFEST.json'))
    check(set(files) == set(manifest['files_sha256']), 'manifest_members')
    for n, b in files.items():
        check(sha256(b).hexdigest() == manifest['files_sha256'][n], 'file_hash', n)
    def j(n): return parse(files[n])
    frozen = json.loads((HERE.parent / 'three-role-vote-repeat-01-preparation-20261013/payload.json').read_bytes())
    check(j('payload.json') == frozen, 'frozen_payload')
    design = j('design.json')
    check(design == json.loads(frozen['design_text']), 'frozen_design')
    report = json.loads((RESULT / 'reaggregated.json').read_bytes())['report']
    for n in files:
        if n.startswith('report-') and n.endswith('.json'):
            check(j(n) == report, 'archived_report')
    pre = j('tokenizer-preflight.json')
    check(pre['status'] == 'PASS' and len(pre['checked']) == 54, 'actual_tokenizer_preflight')
    old_path = ROOT / 'npp-tb01-result-20261013-041945-c6e2c94d.zip'
    check(sha256(old_path.read_bytes()).hexdigest() == design['source']['archive_sha256'], 'source_zip_hash')
    with zipfile.ZipFile(old_path) as old_zip:
        old = {n: old_zip.read(n) for n in old_zip.namelist()}
    sources = {s['key']: s for s in design['source']['items']}
    old_votes = {}
    for key, item in sources.items():
        old_votes[key] = []
        for field, hf in [('source_slot_id', 'source_input_sha256'),
                          ('source_repeat2_slot_id', 'source_repeat2_input_sha256')]:
            path = 'responses/' + item[field] + '/'
            check(sha256(old[path+'input.json']).hexdigest() == item[hf], 'source_input_hash', key)
            inp = parse(old[path+'input.json'])
            check(inp['messages'] == item['messages'] and inp['prepared'] == item['prepared'], 'old_repeats_exact', key)
            old_votes[key].append(parse(old[path+'answer.txt'])['vote']['decision'])
        parent = item['source_parent']['id']
        check(parse(old['responses/'+parent+'/carry-answer.json']) == item['source_parent']['saved_answer'], 'source_parent', key)

    rows, extracts = [], []
    seeds = []
    for slot in design['allocation']:
        sid, role = slot['id'], slot['role']
        check(slot['stage'] == 'VOTE' and slot['parents'] == [], 'vote_only_no_parents', sid)
        folder = 'responses/' + sid + '/'
        inp, response, saved = j(folder+'input.json'), j(folder+'response.json'), j(folder+'result.json')
        item = sources[slot['input_key']]
        check(inp['messages'] == item['messages'] and inp['prepared'] == item['prepared'], 'fixed_actual_input', sid)
        check(inp['binding'] == {}, 'no_new_response_feedback', sid)
        check(inp['id'] == sid and inp['seed'] == slot['seed'] == response['seed'], 'id_seed', sid)
        seeds.append(inp['seed'])
        payload = parse(inp['messages'][1]['content'])
        raw = files[folder+'answer.txt']
        answer = parse(raw)
        shape(answer, design['schemas']['VOTE'])
        check(response['finish_reason'] == 'EOS' and response['output_token_ids'][-1] == j('tokenizer-binding.json')['eos_token_id'], 'eos', sid)
        check(response['answer_text'].encode() == raw == files[folder+'normalized-answer.txt'], 'raw_unchanged', sid)
        check(answer == j(folder+'saved-answer.json') == j(folder+'carry-answer.json'), 'saved_carry', sid)
        case = next(c for c in design['cases'] if c['id'] == slot['case'])
        rates, refs = {}, {}
        for role_key in ('A','B','C'):
            exp = [e for e in case['experiences'] if e['owner'] == role_key]
            refs[role_key] = [e['id'] for e in exp]
            rates[role_key] = {m: Fraction(sum(e['observed'][m]['success'] for e in exp),
                sum(e['observed'][m]['trials'] for e in exp)) for m in ('PAPER','DIGITAL')}
        totals = {c['candidate_id']: sum(40*rates[r][c['assignment'][r]] for r in rates) for c in case['candidates']}
        check(len(set(totals.values())) == 2, 'unique_best', sid)
        for candidate in payload['candidates']:
            check(totals[candidate['candidate_id']] == candidate['expected_total'], 'candidate_total', sid)
            check(all(40*rates[r][candidate['assignment'][r]] == candidate['expected_success_by_role'][r] for r in rates), 'candidate_role_total', sid)
        check(payload['holder'] == role, 'payload_holder', sid)
        check(payload['own_saved_note'] == item['source_parent']['saved_answer']['own'], 'actual_prior_note', sid)
        for medium in ('PAPER','DIGITAL'):
            check(payload['own_experience_summary']['by_medium'][medium]['expected_success_for_40'] == 40*rates[role][medium], 'own_summary', sid)
        own = answer['own']
        expected_vote = 'ACCEPT' if payload['proposal']['candidate_id'] == max(totals,key=totals.get) else 'HOLD'
        metrics = {'own_holder': own['holder'] == role,
                   'own_recommendation': own['recommendation'] == max(rates[role],key=rates[role].get),
                   'own_sources': Counter(own['evidence_ids']) == Counter(refs[role]),
                   'vote': answer['vote'] == {'proposal_id':payload['proposal']['proposal_id'],'decision':expected_vote}}
        check(metrics == saved['score']['metrics'], 'metric_vector', sid)
        check(all(metrics.values()) == saved['score']['strict'], 'strict_score', sid)
        selected = next(c for c in case['candidates'] if c['candidate_id'] == payload['proposal']['candidate_id'])
        rows.append({**slot, 'answer':answer, 'expected_vote':expected_vote,
            'candidate_totals':{k:float(v) for k,v in totals.items()},
            'own_success_for_40':{m:float(40*v) for m,v in rates[role].items()},
            'offered_assignment':selected['assignment'][role],
            'own_assignment_match':own['recommendation'] == selected['assignment'][role],
            'metrics':metrics, 'strict':all(metrics.values()), 'input_tokens':len(inp['prepared']['input_ids']),
            'output_tokens':len(response['output_token_ids']), 'generation_seconds':response['generation_seconds']})
        if slot['input_key'] in ('T02-C-HIGHER','T03-A-LOWER'):
            extracts.append({'slot':slot,'input':inp,'raw_answer':raw.decode(),'score':saved['score']})

    check(len(rows) == report['attempted_generations'] == 54, 'response_count')
    check(len(set(seeds)) == 54 and not set(seeds).intersection(design['source']['old_seeds']), 'new_seeds')
    check(sum(r['strict'] for r in rows) == report['totals']['correct'], 'total_score')
    check(sum(r['output_tokens'] for r in rows) == report['output_tokens'], 'output_tokens')
    check(abs(sum(r['generation_seconds'] for r in rows) - report['generation_seconds']) < 1e-9, 'generation_seconds')
    for name, field in [('by_repeat','repeat'),('by_offer','branch'),('by_role','role'),('by_case','case')]:
        for level, expected in report[name].items():
            selected = [r for r in rows if str(r[field]) == level]
            check(len(selected) == expected['strict']['planned'] and sum(r['strict'] for r in selected) == expected['strict']['correct'], 'stratum_count', name+'/'+level)
            for metric in metrics:
                check(sum(r['metrics'][metric] for r in selected) == expected['metrics'][metric]['correct'], 'stratum_metric', name+'/'+level+'/'+metric)
    repetitions = []
    for item in report['by_input']:
        chosen = sorted([r for r in rows if r['input_key'] == item['key']],key=lambda r:r['repeat'])
        decisions = [r['answer']['vote']['decision'] for r in chosen]
        truth = [r['metrics']['vote'] for r in chosen]
        classification = 'ALL_CORRECT' if all(truth) else 'ALL_INCORRECT' if not any(truth) else 'MIXED'
        check(len(chosen) == 3 and decisions == item['decisions'] and truth == item['vote_correct'] and classification == item['vote_class'], 'repeat_group', item['key'])
        check((len(set(decisions)) == 1) == item['identical_decisions'], 'decision_stability', item['key'])
        repetitions.append({'key':item['key'],'old_TB01_decisions_background_only':old_votes[item['key']],
            'new_TVR01_decisions':decisions, 'vote_class':classification, 'own_assignment_match':item['own_assignment_match']})
    check(dict(Counter(x['vote_class'] for x in repetitions)) == report['vote_repeat_classes'], 'repeat_classes')
    failures = [r['id'] for r in rows if not r['strict']]
    check(len(failures) == report['observed_failed_responses'] and report['gate'] == ('FAIL' if failures else 'PASS_IN_FIXED_REPEAT'), 'gate')
    result = {'status':'PASS', 'kind':'POSTRUN_STDLIB_CROSSCHECK_WITHIN_SAME_PROJECT',
        'checks':dict(CHECKS), 'total_checks':sum(CHECKS.values()),
        'archive_sha256':sha256(ARCHIVE.read_bytes()).hexdigest(), 'archive_bytes':ARCHIVE.stat().st_size,
        'sealed_files':len(files), 'gate':report['gate'], 'failure_ids':failures,
        'elapsed_seconds':j('run-end.json')['elapsed_seconds'], 'generation_seconds':report['generation_seconds'],
        'gpu':j('environment.json')['gpu'], 'response_count':len(rows),
        'input_tokens_minmax':[min(r['input_tokens'] for r in rows),max(r['input_tokens'] for r in rows)],
        'output_tokens_minmax':[min(r['output_tokens'] for r in rows),max(r['output_tokens'] for r in rows)],
        'model_calls_in_this_check':0}
    outputs = [(HERE/'independent-check.json',result),(RESULT/'diagnostics.json',rows),
               (RESULT/'repeat-comparison.json',repetitions),(RESULT/'evidence-extract.json',extracts)]
    for path, data in outputs:
        encoded = (json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode()
        if path.exists():
            if path.read_bytes() != encoded: raise AssertionError('Existing output changed: '+str(path))
        else: path.write_bytes(encoded)
    copy = RESULT / ARCHIVE.name
    if not copy.exists(): shutil.copy2(ARCHIVE, copy)
    assert copy.read_bytes() == ARCHIVE.read_bytes()
    print(json.dumps({k:v for k,v in result.items() if k != 'checks'},ensure_ascii=False,indent=2))


if __name__ == '__main__': main()


