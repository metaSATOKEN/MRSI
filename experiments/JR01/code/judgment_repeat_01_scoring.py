"""JR01 repeated-input summaries; ST02 semantic scoring is inherited unchanged."""
from collections import Counter
from hashlib import sha256
import json
import summary_timing_02_scoring as prior

PROTOCOL = 'JUDGMENT-REPEAT-01/v0.1'
PROPOSAL_SHA = '2b8ac12256d09ae696a123349aad3ece01d731eac4979e41a1c87af4207dba0d'
REQUESTS_SHA = 'd6695472494ffe0f4212ddc5660f2fe4654977ec1d4242e03e9808ec6a6450b7'
enc = prior.enc; digest = prior.digest; displayed = prior.displayed
require = prior.require; receive = prior.receive; SCHEMAS = prior.SCHEMAS
STAGES = ('FORM', 'CONFIRM'); ARMS = ('LATE', 'EARLY')
METRICS = {'FORM': ('F',), 'CONFIRM': ('C', 'B', 'V', 'K0', 'G0', 'bad_accept')}


def payload_of(request):
    return json.loads(request['messages'][1]['content'].split('資料JSON:\n', 1)[1])


def score(raw, slot, payload, rows, finish='EOS'):
    result = prior.score(raw, slot, payload, rows, finish)
    result.update(F=None, B=None, C=None, K0=None, G0=None, bad_accept=None,
                  action=None, own_input_valid=None, transition=None, action_category='UNRESOLVED',
                  accept_defects=[])
    if slot['stage'] == 'FORM':
        result['F'] = result['V']
        return result
    own = payload['own_judgment']['body']
    parent = prior.score(enc({'local': own}), dict(slot, stage='FORM'), payload, rows)
    result['own_input_valid'] = parent['V']
    if result['answer'] is None:
        result['transition'] = str(parent['V']).upper() + '_UNKNOWN'
        return result
    result['B'] = result['L'] and result['Z_local']
    result['C'] = result['appropriate_response']
    result['transition'] = str(parent['V']).upper() + '_' + str(result['B']).upper()
    reply = result['answer']['reply']; action = reply['action']
    result['action'] = action
    agreement = prior.agreement([payload['initial_proposal'], prior.record(slot, result['answer'], 'reply')], rows)
    result['K0'] = agreement['K']; result['G0'] = agreement['G']
    result['bad_accept'] = action == 'ACCEPT' and not result['C']
    if result['C']:
        result['action_category'] = {'ACCEPT': 'APPROPRIATE_ACCEPT', 'COUNTER': 'OPTIMAL_COUNTER', 'HOLD': 'APPROPRIATE_HOLD'}[action]
    elif not result['Z_team']:
        result['action_category'] = 'REFERENCE_DEFECT'
    elif action == 'ACCEPT':
        result['action_category'] = 'BAD_ACCEPT'
    elif payload['initial_proposal']['body']['allocation'] in prior.expected(rows)[1]:
        result['action_category'] = 'UNNECESSARY_RETURN'
    else:
        result['action_category'] = 'OTHER_INAPPROPRIATE_RESPONSE'
    if result['bad_accept']:
        if not prior.legal(reply['allocation']):result['accept_defects'].append('RESOURCE_VIOLATION')
        elif reply['allocation'] not in prior.expected(rows)[1]:result['accept_defects'].append('SUBOPTIMAL_ALLOCATION')
        if not result['Z_team']:result['accept_defects'].append('REFERENCE_DEFECT')
        if reply['allocation'] != payload['initial_proposal']['body']['allocation']:result['accept_defects'].append('ACCEPT_CHANGED_ALLOCATION')
    return result


def counts(values):
    values = list(values)
    require(bool(values) and all(x is None or type(x) is bool for x in values), 'BOOL_VALUES_REQUIRED')
    p = sum(x is True for x in values); u = sum(x is None for x in values); n = len(values)
    return {'n': n, 'correct': p, 'incorrect': n-p-u, 'unresolved': u,
            'success_rate_bounds': [p/n, (p+u)/n], 'interval_type': 'MISSING_OUTCOME_BOUNDS_NOT_CI'}


def stability(values):
    values = list(values); require(len(values) == 3, 'EXACTLY_THREE_REPEATS')
    c = counts(values); mixed = c['correct'] > 0 and c['incorrect'] > 0
    status = ('UNRESOLVED' if c['unresolved'] else 'MIXED' if mixed else
              'ALL_PASS' if c['correct'] == 3 else 'ALL_FAIL')
    return dict(c, status=status, known_mixed=mixed, outcomes=values)


def summarize(design, outcomes):
    slots = design['allocation']; smap = {s['id']: s for s in slots}
    require(set(outcomes) == set(smap), 'EXACT_SCORE_SET_REQUIRED')
    by_id = outcomes
    cells = []
    for source_id in sorted({s['source_id'] for s in slots}):
        group = sorted([s for s in slots if s['source_id'] == source_id], key=lambda s:s['repeat'])
        first = group[0]; ids = [s['id'] for s in group]; scores = [by_id[i] for i in ids]
        metrics = {k:stability(s[k] for s in scores) for k in METRICS[first['stage']]}
        actions = [s['action'] for s in scores]
        answers = [s['answer'] for s in scores]
        known_hashes = {digest(a) for a in answers if a is not None}
        cells.append({k:first[k] for k in ('source_id','case','stage','role','condition_not_for_model','initial_type_not_for_model')} |
                     {'response_ids':ids,'metrics':metrics,'actions':actions,
                      'known_action_variation':len({a for a in actions if a is not None})>1,
                      'action_unresolved':sum(a is None for a in actions) if first['stage']=='CONFIRM' else 0,
                      'answer_json_distinct_known':len(known_hashes), 'answer_json_unresolved':sum(a is None for a in answers)})
    per_repeat = {}
    for repeat in design['repeats']:
        item = {}
        for stage in STAGES:
            group = [s for s in slots if s['repeat']==repeat and s['stage']==stage]
            pairs = [p for p in design['paired_responses'] if p['repeat']==repeat and p['stage']==stage]
            item[stage] = {'by_condition':{arm:{k:counts(by_id[s['id']][k] for s in group if s['condition_not_for_model']==arm)
                                              for k in METRICS[stage]} for arm in ARMS},
                           'paired':{k:prior.paired_counts((by_id[p['response_ids']['EARLY']][k],by_id[p['response_ids']['LATE']][k]) for p in pairs)
                                     for k in METRICS[stage]}}
        per_repeat[str(repeat)] = item
    differences = [per_repeat[str(r)]['FORM']['paired']['F'] for r in design['repeats']]
    bounds = [x['difference_count_bounds'] for x in differences]
    all_positive = all(b[0]>0 for b in bounds)
    prediction = {'status': 'IMPROVEMENT_IN_ALL_THREE_REPEATS' if all_positive else
                  'NOT_IN_ALL_THREE_REPEATS' if any(b[1]<=0 for b in bounds) else 'UNRESOLVED',
                  'difference_count_bounds_by_repeat': bounds,
                  'mean_difference_count_bounds':[sum(b[i] for b in bounds)/3 for i in (0,1)],
                  'range_difference_count_envelope':[min(b[0] for b in bounds),max(b[1] for b in bounds)],
                  'mean_difference_rate_bounds':[sum(b[i] for b in bounds)/48 for i in (0,1)]}
    summary = {}; strata = {}
    for stage in STAGES:
        summary[stage] = {}
        group = [s for s in slots if s['stage']==stage]
        for arm in ARMS:
            subset = [s for s in group if s['condition_not_for_model']==arm]
            armcells = [c for c in cells if c['stage']==stage and c['condition_not_for_model']==arm]
            summary[stage][arm] = {'counts':{k:counts(by_id[s['id']][k] for s in subset) for k in METRICS[stage]},
                'stability':{k:dict(Counter(c['metrics'][k]['status'] for c in armcells)) for k in METRICS[stage]},
                'actions':dict(Counter(by_id[s['id']]['action'] or 'UNRESOLVED' for s in subset)) if stage=='CONFIRM' else {},
                'action_categories':dict(Counter(by_id[s['id']]['action_category'] for s in subset)) if stage=='CONFIRM' else {},
                'own_transitions':dict(Counter(by_id[s['id']]['transition'] for s in subset)) if stage=='CONFIRM' else {},
                'bad_accept_defects_nonexclusive':dict(Counter(d for s in subset for d in by_id[s['id']]['accept_defects']))}
        fields = ('case','role','initial_type_not_for_model') if stage=='CONFIRM' else ('case','role')
        strata[stage] = {field:{str(value):{arm:{k:counts(by_id[s['id']][k] for s in group if s[field]==value and s['condition_not_for_model']==arm)
                                                  for k in METRICS[stage]} for arm in ARMS}
                                for value in sorted({s[field] for s in group},key=str)} for field in fields}
    failed = [s['id'] for s in slots if by_id[s['id']]['V'] is not True]
    varied = [c for c in cells if c['known_action_variation'] or any(c['metrics'][k]['known_mixed'] for k in ('F',) if c['stage']=='FORM')
              or (c['stage']=='CONFIRM' and any(c['metrics'][k]['known_mixed'] for k in ('C','B','V')))]
    normal = {}; selected = set(failed)
    for c in varied:selected.update(c['response_ids'])
    special = [s['id'] for s in slots if s['case']=='N05' and s['stage']=='CONFIRM' and s['initial_type_not_for_model']=='LOWER']
    selected.update(special)
    for stage in STAGES:
        pairs = [p for p in design['paired_responses'] if p['repeat']==1 and p['stage']==stage]
        eligible = []
        for pair in pairs:
            sources = {smap[sid]['source_id'] for sid in pair['response_ids'].values()}
            responses = [s['id'] for s in slots if s['source_id'] in sources]
            if all(by_id[sid]['V'] is True for sid in responses):eligible.append((pair['fixed_pair_id'],responses))
        eligible.sort(key=lambda x:sha256(('JR01-review|2026092905|'+stage+'|'+x[0]).encode()).hexdigest())
        normal[stage] = [x[0] for x in eligible[:4]]
        for _,ids in eligible[:4]:selected.update(ids)
    review = {'status':'PENDING_OFFLINE_REVIEW','nonpassing_or_unknown':failed,
              'mixed_fixed_inputs':[c['source_id'] for c in varied],'special_N05_lower':special,'normal_pairs':normal,
              'all_response_ids':[s['id'] for s in slots if s['id'] in selected],
              'fixed_source_inputs':sorted({smap[i]['source_id'] for i in selected}),
              'fixed_source_parents':sorted({p for i in selected for p in smap[i]['source_parent_ids']})}
    return {'experiment':PROTOCOL,'fixed_inputs':80,'planned_responses':240,'materials':8,'fresh_repeats':3,
            'by_repeat':per_repeat,'fixed_input_stability':cells,'descriptive_by_stage':summary,'strata':strata,
            'formation_prediction':prediction,'reason_review':review,
            'scope':design['inference'],'closure':'ONE_RUN_THEN_PAPER_3_REGARDLESS_OF_SIGN_OR_MISSINGNESS',
            'old_responses_in_new_denominators':0,'full_path_metrics_computed':False,'population_p_values_or_CI':False}
