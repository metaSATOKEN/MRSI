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
RESULT = ROOT / 'study2/results/three-role-comparison-vote-01-20261013'
ARCHIVE = ROOT / 'npp-tcv01-result-20261013-053413-76c1649c.zip'
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


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def main():
    with zipfile.ZipFile(ARCHIVE) as z:
        check(len(z.namelist()) == len(set(z.namelist())), 'unique_archive_members')
        files = {n: z.read(n) for n in z.namelist()}
    manifest = parse(files.pop('FEEDBACK_MANIFEST.json'))
    check(set(files) == set(manifest['files_sha256']), 'manifest_members')
    for n, b in files.items(): check(sha256(b).hexdigest() == manifest['files_sha256'][n], 'file_hash', n)
    def j(n): return parse(files[n])
    frozen = json.loads((HERE.parent / 'three-role-comparison-vote-01-preparation-20261013/payload.json').read_bytes())
    check(j('payload.json') == frozen, 'frozen_payload')
    design = j('design.json')
    check(design == json.loads(frozen['design_text']), 'frozen_design')
    report = json.loads((RESULT / 'reaggregated.json').read_bytes())['report']
    for n in files:
        if n.startswith('report-') and n.endswith('.json'): check(j(n) == report, 'archived_report')
    pre = j('tokenizer-preflight.json')
    check(pre['status'] == 'PASS' and len(pre['checked']) == 108, 'actual_tokenizer_preflight')
    before = {r['id']:r for r in pre['checked']}
    check(set(before) == {s['id'] for s in design['allocation']}, 'preflight_id_set')
    old_path = ROOT / 'npp-tb01-result-20261013-041945-c6e2c94d.zip'
    check(sha256(old_path.read_bytes()).hexdigest() == design['source']['archive_sha256'], 'source_zip_hash')
    with zipfile.ZipFile(old_path) as z: old = {n:z.read(n) for n in z.namelist()}
    sources = {s['key']:s for s in design['source']['items']}
    for key, item in sources.items():
        for field, hf in [('source_slot_id','source_input_sha256'),('source_repeat2_slot_id','source_repeat2_input_sha256')]:
            folder = 'responses/'+item[field]+'/'
            check(sha256(old[folder+'input.json']).hexdigest() == item[hf], 'old_input_hash', key)
            inp = parse(old[folder+'input.json'])
            check(inp['messages'] == item['messages'] and inp['prepared'] == item['prepared'], 'old_input_identity', key)
        check(parse(old['responses/'+item['source_parent']['id']+'/carry-answer.json']) == item['source_parent']['saved_answer'], 'source_parent', key)
    rows, extracts = [], []
    for slot in design['allocation']:
        sid, role, arm = slot['id'], slot['role'], slot['arm']
        path = 'responses/'+sid+'/'
        inp, response, saved = j(path+'input.json'), j(path+'response.json'), j(path+'result.json')
        item = sources[slot['input_key']]
        expected = json.loads(json.dumps(item['messages']))
        if arm == 'COMPARE':
            expected[0]['content'] += design['compare_instruction']
            user = parse(expected[1]['content']); user['schema'] = design['schemas']['COMPARE']
            expected[1]['content'] = canonical(user).decode()
        check(inp['messages'] == expected, 'actual_input_arm_contract', sid)
        check(inp['binding'] == {} and slot['parents'] == [] and slot['stage'] == 'VOTE', 'no_generated_feedback', sid)
        check(inp['id'] == sid and inp['seed'] == slot['seed'] == response['seed'], 'id_seed', sid)
        prepared = inp['prepared']
        check(sha256(canonical(prepared)).hexdigest() == before[sid]['prepared_sha256'], 'preflight_actual_tokenization', sid)
        check(sha256(prepared['rendered_prompt'].encode()).hexdigest() == before[sid]['rendered_sha256'], 'render_hash', sid)
        check(len(prepared['input_ids']) == before[sid]['input_tokens'], 'input_token_count', sid)
        rendered = ''.join('<|im_start|>'+m['role']+'\n'+m['content'].strip()+'<|im_end|>\n' for m in expected)
        rendered += '<|im_start|>assistant\n<think>\n\n</think>\n\n'
        check(prepared['rendered_prompt'] == rendered, 'full_render', sid)
        if arm == 'DIRECT': check(prepared == item['prepared'], 'direct_prior_tokens', sid)
        payload = parse(inp['messages'][1]['content'])
        raw = files[path+'answer.txt']; answer = parse(raw)
        shape(answer, design['schemas'][arm])
        check(response['finish_reason'] == 'EOS' and response['output_token_ids'][-1] == j('tokenizer-binding.json')['eos_token_id'], 'eos', sid)
        check(response['answer_text'].encode() == raw == files[path+'normalized-answer.txt'], 'no_format_repair', sid)
        check(answer == j(path+'saved-answer.json') == j(path+'carry-answer.json') == saved['score']['answer'], 'full_answer_preserved', sid)
        check(saved['score']['format_valid'] is True and not response.get('synthetic_fixture'), 'real_valid_response', sid)
        case = next(c for c in design['cases'] if c['id'] == slot['case'])
        rates, refs = {}, {}
        for r in ('A','B','C'):
            exp = [e for e in case['experiences'] if e['owner'] == r]
            refs[r] = [e['id'] for e in exp]
            rates[r] = {m: Fraction(sum(e['observed'][m]['success'] for e in exp), sum(e['observed'][m]['trials'] for e in exp)) for m in ('PAPER','DIGITAL')}
        totals = {c['candidate_id']:sum(40*rates[r][c['assignment'][r]] for r in rates) for c in case['candidates']}
        check(len(set(totals.values())) == 2, 'no_tie', sid)
        for c in payload['candidates']:
            check(totals[c['candidate_id']] == c['expected_total'], 'candidate_total', sid)
            check(all(40*rates[r][c['assignment'][r]] == c['expected_success_by_role'][r] for r in rates), 'role_total', sid)
        check(payload['holder'] == role and payload['own_saved_note'] == item['source_parent']['saved_answer']['own'], 'holder_prior_note', sid)
        for medium in ('PAPER','DIGITAL'):
            check(payload['own_experience_summary']['by_medium'][medium]['expected_success_for_40'] == 40*rates[role][medium], 'own_total', sid)
        proposed = payload['proposal']['candidate_id']; best = max(totals,key=totals.get)
        relation = 'HIGHER' if proposed == best else 'LOWER'
        expected_vote = 'ACCEPT' if proposed == best else 'HOLD'
        check(relation == slot['branch'], 'branch_truth', sid)
        own, vote = answer['own'], answer['vote']
        metrics = {'own_holder':own['holder'] == role,
            'own_recommendation':own['recommendation'] == max(rates[role],key=rates[role].get),
            'own_sources':Counter(own['evidence_ids']) == Counter(refs[role]),
            'vote':vote == {'proposal_id':payload['proposal']['proposal_id'],'decision':expected_vote}}
        strict = all(metrics.values()); comparison = None; cls = 'NOT_APPLICABLE'; extended = strict
        if arm == 'COMPARE':
            c = answer['comparison']; other = next(k for k in totals if k != proposed)
            binding = c['candidate_id'] == proposed and c['other_candidate_id'] == other
            correct_relation = c['relation'] == relation; correct = binding and correct_relation
            consistent = vote['decision'] == ('ACCEPT' if c['relation'] == 'HIGHER' else 'HOLD') if binding and vote['proposal_id'] == payload['proposal']['proposal_id'] else None
            comparison = {'binding':binding,'relation':correct_relation,'correct':correct,'vote_consistent':consistent,
                'comparison_before_vote':list(answer).index('comparison') < list(answer).index('vote')}
            cls = 'MISBOUND_COMPARISON' if not binding else 'COMPARISON_'+('CORRECT' if correct else 'WRONG')+'_VOTE_'+('CORRECT' if metrics['vote'] else 'WRONG')
            extended = strict and correct
        check(metrics == saved['score']['metrics'] and strict == saved['score']['strict'], 'common_scoring', sid)
        check(comparison == saved['score']['comparison'] and cls == saved['score']['diagnostic_class'] and extended == saved['score']['extended_strict'], 'comparison_scoring', sid)
        selected = next(c for c in case['candidates'] if c['candidate_id'] == proposed)
        rows.append({**slot,'answer':answer,'expected_vote':expected_vote,'expected_relation':relation,
            'candidate_totals':{k:float(v) for k,v in totals.items()},
            'own_success_for_40':{k:float(40*v) for k,v in rates[role].items()},
            'offered_assignment':selected['assignment'][role], 'own_assignment_match':own['recommendation'] == selected['assignment'][role],
            'metrics':metrics,'strict':strict,'comparison':comparison,'diagnostic_class':cls,'extended_strict':extended,
            'input_tokens':len(prepared['input_ids']),'output_tokens':len(response['output_token_ids']),
            'answer_bytes':len(raw),'generation_seconds':response['generation_seconds']})
        if slot['input_key'] in ('T02-C-HIGHER','T03-A-LOWER'):
            extracts.append({'slot':slot,'input':inp,'raw_answer':raw.decode(),'score':saved['score']})
    check(len(rows) == report['attempted_generations'] == 108, 'response_count')
    check(sum(r['strict'] for r in rows) == report['totals']['correct'], 'common_total')
    check(sum(r['output_tokens'] for r in rows) == report['output_tokens'], 'token_total')
    check(abs(sum(r['generation_seconds'] for r in rows)-report['generation_seconds']) < 1e-8, 'duration_total')
    arm_costs = {}
    for arm in ('DIRECT','COMPARE'):
        group = [r for r in rows if r['arm'] == arm]; expected = report['by_arm'][arm]
        check(len(group) == expected['strict']['planned'] == 54 and sum(r['strict'] for r in group) == expected['strict']['correct'], 'arm_score', arm)
        for m in metrics: check(sum(r['metrics'][m] for r in group) == expected['metrics'][m]['correct'], 'arm_metric', arm+'/'+m)
        for name, field in [('by_repeat','repeat'),('by_offer','branch'),('by_role','role'),('by_case','case')]:
            for level, e in expected[name].items():
                sub = [r for r in group if str(r[field]) == level]
                check(len(sub) == e['strict']['planned'] and sum(r['strict'] for r in sub) == e['strict']['correct'], 'stratum_total', arm+'/'+name+'/'+level)
                for m in metrics: check(sum(r['metrics'][m] for r in sub) == e['metrics'][m]['correct'], 'stratum_metric', arm+'/'+name+'/'+level+'/'+m)
        arm_costs[arm] = {'output_tokens':sum(r['output_tokens'] for r in group),
            'mean_output_tokens':sum(r['output_tokens'] for r in group)/54,
            'mean_answer_bytes':sum(r['answer_bytes'] for r in group)/54,
            'generation_seconds':sum(r['generation_seconds'] for r in group),
            'input_tokens_minmax':[min(r['input_tokens'] for r in group),max(r['input_tokens'] for r in group)]}
    for item in report['by_input']:
        sub = sorted([r for r in rows if r['arm'] == item['arm'] and r['input_key'] == item['key']],key=lambda r:r['repeat'])
        truth = [r['metrics']['vote'] for r in sub]; decisions = [r['answer']['vote']['decision'] for r in sub]
        cls = 'ALL_CORRECT' if all(truth) else 'ALL_INCORRECT' if not any(truth) else 'MIXED'
        check(len(sub) == 3 and decisions == item['decisions'] and truth == item['vote_correct'] and cls == item['vote_class'], 'repeat_group', item['key'])
    comp = [r for r in rows if r['arm'] == 'COMPARE']; cd = report['comparison_diagnostics']
    check(dict(Counter(r['diagnostic_class'] for r in comp)) == cd['classes'], 'comparison_classes')
    check(sum(r['extended_strict'] for r in comp) == cd['extended_strict']['correct'], 'extended_total')
    for m in cd['metrics']: check(sum(r['comparison'][m] is True for r in comp) == cd['metrics'][m]['correct'], 'comparison_metric', m)
    pc = Counter(); seeds = set(); delta = 0
    for pair in report['paired']['pairs']:
        sub = [r for r in rows if r['pair_id'] == pair['pair_id']]; a = {r['arm']:r['strict'] for r in sub}
        check(len(sub) == 2 and sub[0]['seed'] == sub[1]['seed'], 'pair_seed', pair['pair_id']);seeds.add(sub[0]['seed'])
        cls = 'BOTH_CORRECT' if all(a.values()) else 'DIRECT_ONLY' if a['DIRECT'] else 'COMPARE_ONLY' if a['COMPARE'] else 'BOTH_INCORRECT'
        d = int(a['COMPARE'])-int(a['DIRECT']);delta += d;pc[cls] += 1
        check(a['DIRECT'] == pair['DIRECT'] and a['COMPARE'] == pair['COMPARE'] and cls == pair['class'] and pair['difference_bounds'] == [d,d], 'paired_score')
    old_seeds = set(design['source']['old_seeds'])
    tvr = json.loads((ROOT/'study2/results/three-role-vote-repeat-01-20261013/reaggregated.json').read_bytes())['report']
    old_seeds.update(s['seed'] for s in tvr['by_slot'])
    check(len(seeds) == 54 and not seeds.intersection(old_seeds), 'new_pair_seeds')
    for rep in (1,2,3):check(Counter(r['arm'] for r in rows if r['repeat'] == rep and r['arm_position'] == 1) == {'DIRECT':9,'COMPARE':9}, 'balanced_order')
    check(dict(pc) == report['paired']['counts'] and report['paired']['difference_count_bounds'] == [delta,delta], 'paired_totals')
    check(report['paired']['difference_pp_bounds'] == [100*delta/54]*2, 'paired_pp')
    check(report['paired']['direction'] == ('BETTER_ON_COMMON' if delta>0 else 'WORSE_ON_COMMON' if delta<0 else 'TIED_ON_COMMON'), 'paired_direction')
    failures = [r['id'] for r in rows if not r['strict']]
    gate = 'FAIL' if failures or any(not r['extended_strict'] for r in comp) else 'PASS_IN_FIXED_COMPARISON'
    check(gate == report['gate'] and report['unresolved_responses'] == 0, 'gate')
    result = {'status':'PASS','kind':'POSTRUN_STDLIB_CROSSCHECK_WITHIN_SAME_PROJECT',
        'checks':dict(CHECKS),'total_checks':sum(CHECKS.values()),'archive_sha256':sha256(ARCHIVE.read_bytes()).hexdigest(),
        'archive_bytes':ARCHIVE.stat().st_size,'sealed_files':len(files),'response_count':108,'gate':gate,
        'failure_ids':failures,'paired_counts':dict(pc),'comparison_classes':cd['classes'],
        'elapsed_seconds':j('run-end.json')['elapsed_seconds'],'generation_seconds':report['generation_seconds'],
        'gpu':j('environment.json')['gpu'],'arm_costs':arm_costs,'model_calls_in_this_check':0}
    repetitions = [{'key':key,
        'old_TVR01_background_only':next(x['decisions'] for x in tvr['by_input'] if x['key']==key),
        **{a:next(x['decisions'] for x in report['by_input'] if x['key']==key and x['arm']==a) for a in ('DIRECT','COMPARE')}} for key in sources]
    for p,v in [(HERE/'independent-check.json',result),(RESULT/'diagnostics.json',rows),
                (RESULT/'evidence-extract.json',extracts),(RESULT/'repeat-comparison.json',repetitions)]:
        data=(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
        if p.exists(): check(p.read_bytes()==data,'saved_output_unchanged',str(p))
        else:p.write_bytes(data)
    copy=RESULT/ARCHIVE.name
    if not copy.exists():shutil.copy2(ARCHIVE,copy)
    check(copy.read_bytes()==ARCHIVE.read_bytes(),'copied_archive')
    print(json.dumps({k:v for k,v in result.items() if k!='checks'},ensure_ascii=False,indent=2))


if __name__ == '__main__':main()


