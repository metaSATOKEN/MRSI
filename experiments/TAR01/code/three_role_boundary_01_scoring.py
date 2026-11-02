"""TB01 deterministic scoring. Recomputes references from rows, not supplied summaries."""
from fractions import Fraction
from collections import Counter
import three_role_boundary_01_design as d
import readout_split_01_scoring as strict_json
import update_readout_01_envelope as envelope

METRICS = ('own_holder', 'own_recommendation', 'own_sources', 'vote', 'approval_state', 'agreement', 'execution')


def shape(value, schema, path='$'):
    if schema['type'] == 'object':
        if type(value) is not dict:
            return [path + ':OBJECT']
        errors = [path + ':KEYS'] if set(value) != set(schema['required']) else []
        for k, v in value.items():
            if k in schema['properties']:
                errors.extend(shape(v, schema['properties'][k], path + '.' + k))
        return errors
    if schema['type'] == 'array':
        if type(value) is not list or not schema['minItems'] <= len(value) <= schema['maxItems']:
            return [path + ':ARRAY']
        return [e for i, v in enumerate(value) for e in shape(v, schema['items'], path + f'[{i}]')]
    if type(value) is not str:
        return [path + ':STRING']
    if 'enum' in schema:
        return [] if value in schema['enum'] else [path + ':ENUM']
    return [] if schema['minLength'] <= len(value) <= schema['maxLength'] else [path + ':LENGTH']


def own_reference(case, role):
    rows = [row for row in case['experiences'] if row['owner'] == role]
    rates = {m: Fraction(sum(r['observed'][m]['success'] for r in rows),
                         sum(r['observed'][m]['trials'] for r in rows)) for m in d.MEDIA}
    assert rates['PAPER'] != rates['DIGITAL']
    return {'holder': role, 'recommendation': max(rates, key=rates.get),
            'evidence_ids': [r['id'] for r in rows]}


def best_candidate(case):
    totals = {}
    for c in case['candidates']:
        total = Fraction(0)
        for r in d.ROLES:
            rows = [row for row in case['experiences'] if row['owner'] == r]
            m = c['assignment'][r]
            total += 40 * Fraction(sum(x['observed'][m]['success'] for x in rows),
                                   sum(x['observed'][m]['trials'] for x in rows))
        totals[c['candidate_id']] = total
    assert len(set(totals.values())) == 2
    return max(totals, key=totals.get)


def read_reference(payload):
    receipts = {r['sender']: r for r in payload['receipts']}
    assert len(receipts) == len(payload['receipts']) and set(receipts) <= set(d.ROLES)
    expected = {}
    for role in d.ROLES:
        if role not in receipts:
            expected[role] = 'MISSING'
        elif receipts[role]['proposal_id'] != payload['proposal']['proposal_id']:
            expected[role] = 'WRONG_PROPOSAL'
        else:
            expected[role] = receipts[role]['decision']
    agreed = all(v == 'ACCEPT' for v in expected.values())
    candidate = next(c for c in payload['candidates'] if c['candidate_id'] == payload['proposal']['candidate_id'])
    return {'approval_state': expected, 'agreement': 'AGREED' if agreed else 'PENDING',
            'joint_action': candidate['assignment'][payload['holder']] if agreed else 'HOLD'}


def tri_all(values):
    values = list(values)
    return False if False in values else None if None in values else True


def score(raw, slot, payload, case, finish_reason='EOS'):
    stage = slot['stage']
    applicable = ['own_holder', 'own_recommendation', 'own_sources']
    if stage == 'VOTE':
        applicable += ['vote']
    if stage == 'READ':
        applicable += ['approval_state', 'agreement', 'execution']
    result = {'format_valid': None, 'answer': None, 'applicable': applicable,
              'metrics': {m: None for m in applicable}, 'strict': None, 'errors': [],
              'unsafe_commit': None, 'false_agreement': None, 'unwarranted_hold': None}
    if raw is None:
        result['errors'] = ['NO_RESPONSE']; return result
    norm = envelope.normalize(raw, finish_reason)
    result['normalization'] = {k: v for k, v in norm.items() if k != 'normalized_bytes'}
    if norm['normalized_bytes'] is None:
        result['format_valid'] = False if finish_reason == 'EOS' else None
        result['errors'] = [norm['reason']]; return result
    value = strict_json.parse(norm['normalized_bytes'])
    errors = shape(value, d.SCHEMAS[stage])
    result['format_valid'] = not errors
    if errors:
        result['errors'] = errors; return result
    result['answer'] = value
    own = own_reference(case, slot['role']); actual = value['own']
    result['metrics'].update(own_holder=actual['holder'] == own['holder'],
        own_recommendation=actual['recommendation'] == own['recommendation'],
        own_sources=len(actual['evidence_ids']) == len(own['evidence_ids']) and set(actual['evidence_ids']) == set(own['evidence_ids']))
    if stage == 'VOTE':
        correct_vote = 'ACCEPT' if payload['proposal']['candidate_id'] == best_candidate(case) else 'HOLD'
        result['metrics']['vote'] = value['vote'] == {'proposal_id': payload['proposal']['proposal_id'], 'decision': correct_vote}
    if stage == 'READ':
        expected = read_reference(payload)
        result['metrics'].update(approval_state=value['approval_state'] == expected['approval_state'],
                                 agreement=value['agreement'] == expected['agreement'],
                                 execution=value['joint_action'] == expected['joint_action'])
        result['false_agreement'] = value['agreement'] == 'AGREED' and expected['agreement'] != 'AGREED'
        result['unwarranted_hold'] = expected['agreement'] == 'AGREED' and value['agreement'] != 'AGREED'
        # Faithful execution of a bad unanimous agreement can be correct readout yet unsafe end-to-end.
        result['unsafe_commit'] = value['agreement'] == 'AGREED' and payload['proposal']['candidate_id'] != best_candidate(case)
    result['strict'] = tri_all(result['metrics'].values())
    return result


def counts(values):
    values = list(values)
    return {'planned': len(values), 'correct': sum(v is True for v in values),
            'incorrect': sum(v is False for v in values), 'unresolved': sum(v is None for v in values)}


def summarize(design, scores):
    slots = design['allocation']
    assert set(scores) == {s['id'] for s in slots}
    report = {'unit': '3 numeric triads; 2 technical replicates; two offers share each replicate\'s FORM notes',
              'by_stage': {}, 'read_by_snapshot_and_offer': {}, 'paths': [], 'triad_replicates': []}
    for stage in d.STAGES:
        chosen = [s for s in slots if s['stage'] == stage]
        report['by_stage'][stage] = {'strict': counts(scores[s['id']]['strict'] for s in chosen), 'metrics': {
            m: counts(scores[s['id']]['metrics'].get(m) for s in chosen if m in scores[s['id']]['applicable'])
            for m in METRICS if any(m in scores[s['id']]['applicable'] for s in chosen)}}
    for branch in ('HIGHER', 'LOWER'):
        for snapshot in ('TWO_RECEIVED', 'THREE_RECEIVED'):
            ids = [s['id'] for s in slots if s['branch'] == branch and s['snapshot'] == snapshot]
            report['read_by_snapshot_and_offer'][branch + '/' + snapshot] = {
                'strict': counts(scores[i]['strict'] for i in ids),
                'false_agreements': sum(scores[i]['false_agreement'] is True for i in ids),
                'unsafe_commits': sum(scores[i]['unsafe_commit'] is True for i in ids),
                'unwarranted_holds': sum(scores[i]['unwarranted_hold'] is True for i in ids)}
    for case in design['cases']:
        for rep in d.REPEATS:
            units = []
            for branch in ('HIGHER', 'LOWER'):
                ids = [s['id'] for s in slots if s['case'] == case['id'] and s['repeat'] == rep and s['branch'] in (None, branch)]
                strict = tri_all(scores[i]['strict'] for i in ids)
                units.append(strict)
                report['paths'].append({'case': case['id'], 'repeat': rep, 'offer': branch,
                                        'strict': strict, 'own_preserved': tri_all(
                    scores[i]['metrics'][m] for i in ids for m in ('own_holder', 'own_recommendation', 'own_sources'))})
            report['triad_replicates'].append({'case': case['id'], 'repeat': rep, 'both_offers_strict': tri_all(units)})
    report['path_totals'] = counts(x['strict'] for x in report['paths'])
    report['triad_replicate_totals'] = counts(x['both_offers_strict'] for x in report['triad_replicates'])
    missing = sum(scores[s['id']]['strict'] is None for s in slots)
    failures = sum(scores[s['id']]['strict'] is False for s in slots)
    report['gate'] = 'INCONCLUSIVE' if missing else 'FAIL' if failures else 'PASS_IN_FIXED_PILOT'
    report['observed_failed_responses'] = failures
    report['unresolved_responses'] = missing
    report['gate_definition'] = 'All 126 required responses interpretable and strict; no population claim or p-value.'
    return report
