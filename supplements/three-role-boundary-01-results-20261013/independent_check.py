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
RESULT = ROOT / 'study2/results/three-role-boundary-01-20261013/attempt-02-complete'
ARCHIVE = ROOT / 'npp-tb01-result-20261013-041945-c6e2c94d.zip'
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
    for n, b in files.items(): check(sha256(b).hexdigest() == manifest['files_sha256'][n], 'file_hash', n)
    def j(n): return parse(files[n])
    frozen = json.loads((HERE.parent / 'three-role-boundary-01-render-fix-20261013/payload.json').read_bytes())
    check(j('payload.json') == frozen, 'frozen_payload')
    design = j('design.json')
    check(design == json.loads(frozen['design_text']), 'frozen_design')
    report = json.loads((RESULT / 'reaggregated.json').read_bytes())['report']
    for n in files:
        if n.startswith('report-') and n.endswith('.json'): check(j(n) == report, 'archived_report')
    check(j('tokenizer-preflight.json')['status'] == 'PASS', 'tokenizer_preflight')
    answers, inputs, rows = {}, {}, []
    for slot in design['allocation']:
        sid, role, stage = slot['id'], slot['role'], slot['stage']
        folder = 'responses/' + sid + '/'
        inp, response, saved = j(folder+'input.json'), j(folder+'response.json'), j(folder+'result.json')
        payload = parse(inp['messages'][1]['content'])
        raw = files[folder+'answer.txt']
        answer = parse(raw)  # All returned responses are bare JSON; no repairs.
        shape(answer, design['schemas'][stage])
        check(response['finish_reason'] == 'EOS' and response['output_token_ids'][-1] == j('tokenizer-binding.json')['eos_token_id'], 'eos', sid)
        check(response['seed'] == inp['seed'] == slot['seed'], 'seed', sid)
        check(response['answer_text'].encode() == raw == files[folder+'normalized-answer.txt'], 'raw_unchanged', sid)
        check(answer == j(folder+'saved-answer.json') == j(folder+'carry-answer.json'), 'saved_carry', sid)
        case = next(c for c in design['cases'] if c['id'] == slot['case'])
        rates, refs = {}, {}
        for r in ('A','B','C'):
            exp = [e for e in case['experiences'] if e['owner'] == r]
            refs[r] = [e['id'] for e in exp]
            rates[r] = {m: Fraction(sum(e['observed'][m]['success'] for e in exp), sum(e['observed'][m]['trials'] for e in exp)) for m in ('PAPER','DIGITAL')}
        check(payload['holder'] == role, 'payload_holder', sid)
        own = answer['own']
        metrics = {'own_holder': own['holder'] == role,
                   'own_recommendation': own['recommendation'] == max(rates[role], key=rates[role].get),
                   'own_sources': Counter(own['evidence_ids']) == Counter(refs[role])}
        totals = {c['candidate_id']: sum(40*rates[r][c['assignment'][r]] for r in ('A','B','C')) for c in case['candidates']}
        if stage != 'FORM':
            for c in payload['candidates']:
                check(totals[c['candidate_id']] == c['expected_total'], 'candidate_total', sid)
                check(all(40*rates[r][c['assignment'][r]] == c['expected_success_by_role'][r] for r in rates), 'candidate_role_total', sid)
            parent = slot.get('own_parent', slot['parents'][0])
            check(payload['own_saved_note'] == answers[parent]['own'], 'own_actual_parent', sid)
        for parent in slot['parents']:
            for key, name in (('answer_sha256','answer.txt'),('carry_answer_sha256','carry-answer.json'),('result_sha256','result.json')):
                check(inp['binding'][parent][key] == sha256(files['responses/'+parent+'/'+name]).hexdigest(), 'parent_hash', sid)
        expected_vote = None
        expected_read = None
        if stage == 'VOTE':
            expected_vote = 'ACCEPT' if payload['proposal']['candidate_id'] == max(totals,key=totals.get) else 'HOLD'
            metrics['vote'] = answer['vote'] == {'proposal_id':payload['proposal']['proposal_id'],'decision':expected_vote}
        if stage == 'READ':
            receipts = [{'sender':p.rsplit('-',1)[1], **answers[p]['vote']} for p in slot['vote_parents']]
            check(receipts == payload['receipts'], 'actual_receipts', sid)
            check(len(receipts) == (2 if slot['snapshot'] == 'TWO_RECEIVED' else 3), 'receipt_count', sid)
            states = {r:'MISSING' for r in ('A','B','C')}
            for receipt in receipts:
                states[receipt['sender']] = receipt['decision'] if receipt['proposal_id']==payload['proposal']['proposal_id'] else 'WRONG_PROPOSAL'
            agreement = 'AGREED' if all(v=='ACCEPT' for v in states.values()) else 'PENDING'
            c = next(c for c in case['candidates'] if c['candidate_id'] == payload['proposal']['candidate_id'])
            action = c['assignment'][role] if agreement=='AGREED' else 'HOLD'
            expected_read = {'approval_state':states,'agreement':agreement,'joint_action':action}
            metrics.update(approval_state=answer['approval_state']==states, agreement=answer['agreement']==agreement, execution=answer['joint_action']==action)
        check(metrics == saved['score']['metrics'], 'metric_vector', sid)
        check(all(metrics.values()) == saved['score']['strict'], 'strict_score', sid)
        answers[sid], inputs[sid] = answer, inp
        rows.append({**slot,'answer':answer,'expected_vote':expected_vote,'expected_read':expected_read,'metrics':metrics,'strict':all(metrics.values()),
                     'input_tokens':len(inp['prepared']['input_ids']),'output_tokens':len(response['output_token_ids']),
                     'answer_bytes':len(raw)})
    check(len(rows) == len(report['by_slot']) == 126, 'response_count')
    check(sum(r['output_tokens'] for r in rows) == report['output_tokens'], 'output_tokens')
    for stage in ('FORM','VOTE','READ'):
        subset = [r for r in rows if r['stage']==stage]
        check(sum(r['strict'] for r in subset) == report['by_stage'][stage]['strict']['correct'], 'stage_count', stage)
    routes = []
    for c in design['cases']:
        for rep in (1,2):
            for branch in ('HIGHER','LOWER'):
                subset = [r for r in rows if r['case']==c['id'] and r['repeat']==rep and r['branch'] in (None,branch)]
                votes = {r['role']:r['answer']['vote']['decision'] for r in subset if r['stage']=='VOTE'}
                final = [r for r in subset if r['stage']=='READ' and r['snapshot']=='THREE_RECEIVED']
                routes.append({'case':c['id'],'repeat':rep,'offer':branch,'votes':votes,
                    'final_agreement':{r['role']:r['answer']['agreement'] for r in final},'strict':all(r['strict'] for r in subset)})
    check(sum(r['strict'] for r in routes)==report['path_totals']['correct'], 'path_count')
    failure_ids = [r['id'] for r in rows if not r['strict']]
    check(len(failure_ids)==report['observed_failed_responses'], 'failure_count')
    repeat_pairs = []
    for row in rows:
        if row['stage']=='VOTE' and row['repeat']==1:
            a=row['id']; b=a.replace('-R1-','-R2-')
            repeat_pairs.append({'first':a,'second':b,'messages_equal':inputs[a]['messages']==inputs[b]['messages'],
                'prepared_equal':inputs[a]['prepared']==inputs[b]['prepared'],'vote_equal':answers[a]['vote']==answers[b]['vote']})
    check(all(p['messages_equal'] and p['prepared_equal'] for p in repeat_pairs), 'repeat_vote_inputs_equal')
    durations = j('run-end.json')
    result = {'status':'PASS','kind':'POSTRUN_STDLIB_CROSSCHECK_WITHIN_SAME_PROJECT','checks':dict(CHECKS),
        'total_checks':sum(CHECKS.values()),'archive_sha256':sha256(ARCHIVE.read_bytes()).hexdigest(),
        'sealed_files':len(files),'gate':report['gate'],'failure_ids':failure_ids,
        'elapsed_seconds':durations['elapsed_seconds'],'generation_seconds':report['generation_seconds'],
        'input_tokens_minmax':[min(r['input_tokens'] for r in rows),max(r['input_tokens'] for r in rows)],
        'output_tokens_minmax':[min(r['output_tokens'] for r in rows),max(r['output_tokens'] for r in rows)],
        'routes':routes,'vote_repeat_pairs':repeat_pairs,'model_calls_in_this_check':0}
    for path, data in ((HERE/'independent-check.json',result),(RESULT/'diagnostics.json',rows)):
        encoded=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode()
        if path.exists(): check(path.read_bytes()==encoded,'existing_output_equal',str(path))
        else: path.write_bytes(encoded)
    copy = RESULT / ARCHIVE.name
    if not copy.exists(): shutil.copy2(ARCHIVE, copy)
    check(copy.read_bytes()==ARCHIVE.read_bytes(),'archive_copy')
    print(json.dumps({k:v for k,v in result.items() if k not in ('routes','vote_repeat_pairs','checks')},ensure_ascii=False,indent=2))


if __name__=='__main__': main()
