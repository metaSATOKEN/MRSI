"""Read-only OS01 archive audit and separately labelled posthoc reference scoring.
Run: python3 <this-file> <new-output-directory>. Standard library only.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT/'scripts'))
import own_summary_01_design as sc
from receiver_candidate import receive, POINTER

HERE = Path(__file__).resolve().parent
ZIP = ROOT/'study2/results/own-summary-01-20260928/npp-os01-result-20260928-114016-19b98b69.zip'
ZIP_SHA = '26b40a51c11b2f72f6569483dba2b4240436d991e16b5c9046e41671b5606b4d'


def refs(actual, wanted):
    return len(actual) == len(set(actual)) and set(actual) == set(wanted)


def independent_use(answer, payload):
    """Compute from actual inputs; no scorer helpers or precomputed answer keys."""
    role = payload['holder']
    own = [row for row in payload['experiences'] if row['observer'] == role]
    denominator = sum(row['attempts_per_medium'] for row in own)
    projected = {m: Fraction(40 * sum(row[m.lower()+'_success'] for row in own), denominator)
                 for m in ('PAPER', 'DIGITAL')}
    values = list(projected.values())
    expected = max(projected, key=projected.get) if values[0] != values[1] else 'UNDECIDED'
    proposal = next(r for r in payload['joint_records'] if 'action' not in r['body'])
    reply = next(r for r in payload['joint_records'] if 'action' in r['body'])
    pr, re = proposal['body'], reply['body']
    legal = sorted(pr['allocation'].values()) == ['DIGITAL', 'PAPER']
    agreed = (proposal['author'] != reply['author'] and legal
              and re['reply_to'] == proposal['record_id'] and re['action'] == 'ACCEPT'
              and re['allocation'] == pr['allocation'])
    allocation = pr['allocation'] if agreed else {'A': 'UNDECIDED', 'B': 'UNDECIDED'}
    basis = 'SHARED_DECISION' if agreed else 'UNRESOLVED'
    local, team = answer['local'], answer['team']
    return {'L': local['subject'] == role and local['choice'] == expected,
            'Z_local': local['subject'] == role and refs(local['evidence_refs'], [r['episode_id'] for r in own]),
            'H': team['allocation'] == allocation and team['basis'] == basis,
            'Z_team': team['basis'] == basis and refs(team['evidence_refs'], [r['record_id'] for r in payload['joint_records']])}, {
                'expected_choice': expected, 'projected_success_per_40': {m: str(v) for m, v in projected.items()},
                'agreement': agreed}


def main(destination):
    out = Path(destination)
    out.mkdir(parents=True, exist_ok=False)
    checks = []

    def check(name, value):
        checks.append({'name': name, 'pass': bool(value)})
        if not value:
            dump('failed-check.json', {'checks': checks})
            raise AssertionError(name)

    def dump(name, value):
        p = out/name
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('x') as f:
            json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
            f.write('\n')

    def binary(name, value):
        p = out/name
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('xb') as f:
            f.write(value)

    protected = json.loads((HERE/'protected-before.json').read_bytes())
    for name, h in protected.items():
        check('before '+name, sha256((ROOT/name).read_bytes()).hexdigest() == h)
    check('zip hash', sha256(ZIP.read_bytes()).hexdigest() == ZIP_SHA)
    old = json.loads((ROOT/'study2/results/own-summary-01-20260928/reaggregated.json').read_bytes())['report']
    records, outcomes, atomic, checksums, raw_errors, extra_diagnostics = [], {}, {}, [], [], []
    with zipfile.ZipFile(ZIP) as z:
        names = z.namelist()
        manifest = json.loads(z.read('FEEDBACK_MANIFEST.json'))['files_sha256']
        check('zip members', len(names) == len(set(names)) and set(names) == set(manifest)|{'FEEDBACK_MANIFEST.json'})
        for name, h in manifest.items():
            check('zip member '+name, sha256(z.read(name)).hexdigest() == h)
        design = json.loads(z.read('design.json'))
        check('schemas frozen', design['schemas'] == sc.SCHEMAS)
        roots = {r['id']: r for r in design['roots']}
        branches = {b['id']: b for b in design['branches']}
        formal = {r['id']: r['score'] for r in old['by_slot']}
        for slot in design['allocation']:
            sid, stage = slot['id'], slot['stage']
            folder = 'responses/'+sid+'/'
            raw = z.read(folder+'answer.txt')
            original = sc.strict_json.parse(raw)
            response = json.loads(z.read(folder+'response.json'))
            result = json.loads(z.read(folder+'result.json'))
            request = json.loads(z.read(folder+'input.json'))
            payload = json.loads(request['messages'][1]['content'].split('資料JSON:\n', 1)[1])
            source, branch = roots[slot['root']], branches[slot['branch']]
            rows = sc.case_rows(source, branch)
            check(sid+' formal unchanged score', sc.score(raw, slot, payload, rows, response['finish_reason']) == result['score'] == formal[sid])
            receipt = receive(raw, stage, response['finish_reason'])
            candidate = receipt.pop('candidate_bytes')
            check(sid+' accepted candidate', candidate is not None)
            answer = sc.strict_json.parse(candidate)
            if receipt['status'] == 'UNCHANGED':
                check(sid+' unchanged bytes', candidate == raw)
            else:
                check(sid+' one path', [q['pointer'] for q in receipt['quarantine']] == [POINTER])
                restored = deepcopy(answer)
                restored['local']['own_experience_summary'] = receipt['quarantine'][0]['value']
                check(sid+' exactly reversible values', restored == original)
                check(sid+' no real carry of invalid output', folder+'saved-answer.json' not in names and folder+'carry-answer.json' not in names)
                binary('candidates/'+sid+'.json', candidate)
                dump('quarantine/'+sid+'.json', receipt)
            reference = sc.score(candidate, slot, payload, rows, response['finish_reason'])
            check(sid+' shape valid', reference['format_valid'] is True)
            check(sid+' added field never forwarded', 'own_experience_summary' not in reference['carried_answer']['local'])
            if receipt['status'] == 'UNCHANGED':
                check(sid+' unchanged scoring', reference == formal[sid])
            outcomes[sid] = reference
            if stage == 'USE':
                sem, context = independent_use(original, payload)
                for k, value in sem.items():
                    check(sid+' independent '+k, reference[k] is value)
                atomic[sid] = sem
                if not sem['L']:
                    raw_errors.append({'id': sid, 'choice': original['local']['choice'],
                                       'saved_choice': payload['own_judgment']['body']['choice'], **context})
                if receipt['quarantine']:
                    extra = receipt['quarantine'][0]['value']
                    own = [r for r in payload['experiences'] if r['observer'] == payload['holder']]
                    numeric = {m: Fraction(str(extra['projected_success_per_40'][m])) == Fraction(v)
                               for m, v in context['projected_success_per_40'].items()}
                    extra_diagnostics.append({'id': sid, 'numeric_matches': numeric,
                        'observer_correct': extra['observer'] == payload['holder'],
                        'refs_correct': refs(extra['experience_refs'], [r['episode_id'] for r in own]),
                        'denominator_correct': extra['attempts_per_medium_total'] == sum(r['attempts_per_medium'] for r in own),
                        'used_for_scoring': False})
            else:
                atomic[sid] = formal[sid]  # unchanged prefix, already independently audited in §325
            receipt.update(candidate_sha256=sha256(candidate).hexdigest(),
                           original_sha256=sha256(raw).hexdigest())
            records.append({'slot': slot, 'receipt': receipt, 'formal_score': formal[sid], 'reference_score': reference})
        summary = sc.summarize(design, outcomes)
        # Independent J/Q/S/I reconstruction from direct field checks and unchanged prefixes.
        path_values = {}
        for cell in design['cells']:
            p, c = (atomic[cell[k]] for k in ('propose_id', 'confirm_id'))
            us = {role: atomic[sid] for role, sid in cell['use_ids'].items()}
            v = {'J': all([p['L'], p['Z'], c['L'], c['Z'], c['C']] +
                         [u[k] for u in us.values() for k in ('L', 'Z_local', 'H', 'Z_team')]),
                 'U_target': all(us[cell['target']][k] for k in ('L', 'Z_local')),
                 'U_peer': all(us[cell['peer']][k] for k in ('L', 'Z_local'))}
            target = next(r for r in summary['paths'] if r['id'] == cell['id'])
            for k, value in v.items():
                check(cell['id']+' independent aggregate '+k, target[k] is value)
            path_values[cell['id']] = v
        for pair in summary['pairs']:
            cells = [c for c in design['cells'] if c['condition'] == pair['condition'] and c['root'] == pair['root']]
            v = {'Q': all(path_values[c['id']]['J'] for c in cells),
                 'S_target': all(atomic[sid]['L'] for c in cells for sid in (c['propose_id'], c['use_ids'][c['target']])),
                 'I_peer': all(atomic[sid]['L'] for c in cells for sid in (c['confirm_id'], c['use_ids'][c['peer']]))}
            for k, value in v.items():
                check(pair['root']+pair['condition']+' independent pair '+k, pair[k] is value)
        # The old complete metrics are reproducible without substituting any scores.
        original_summary = sc.summarize(design, formal)
        for k, v in original_summary.items():
            check('formal summary preserved '+k, old[k] == v)
        summary['kind'] = 'POSTHOC_OS01_SINGLE_FIELD_QUARANTINE_REFERENCE_ONLY'
        summary['operational_promotion'] = False
        summary['notice'] = 'Old thresholds are displayed for comparability only. Formal OS01 results and progression decisions remain unchanged.'
        differences = {}
        for condition, m in summary['metrics'].items():
            differences[condition] = {k: {'formal': old['metrics'][condition][k], 'reference': m[k]}
                                      for k in ('U_target', 'U_peer', 'J', 'Q', 'S_target', 'I_peer')}
        counts = Counter(r['receipt']['status'] for r in records)
        recovered = [r for r in records if r['receipt']['status'] == 'QUARANTINED']
        use_failures = [r['slot']['id'] for r in records if r['slot']['stage'] == 'USE' and not all(r['reference_score'][k] for k in ('L', 'Z', 'H'))]
        confirm_failures = [r['slot']['id'] for r in records if r['slot']['stage'] == 'CONFIRM' and not all(r['reference_score'][k] for k in ('C', 'L', 'Z'))]
        compact = {'kind': summary['kind'], 'model_calls': 0, 'reference_only': True,
                   'response_count': len(records), 'candidate_status_counts': dict(counts),
                   'quarantined_required_semantics_correct': sum(all(r['reference_score'][k] for k in ('L', 'Z', 'H')) for r in recovered),
                   'quarantined_required_semantics_incorrect': sum(not all(r['reference_score'][k] for k in ('L', 'Z', 'H')) for r in recovered),
                   'extra_numeric_rows_correct': sum(all(r['numeric_matches'].values()) for r in extra_diagnostics),
                   'extra_numeric_rows_incorrect': sum(not all(r['numeric_matches'].values()) for r in extra_diagnostics),
                   'reference_differences': differences, 'use_semantic_failure_ids': use_failures,
                   'confirm_failure_ids': confirm_failures,
                   'formal_source_sha256': sha256((ROOT/'study2/results/own-summary-01-20260928/reaggregated.json').read_bytes()).hexdigest(),
                   'not_an_independent_replication': True}
        dump('reference-summary.json', summary)
        dump('comparison.json', compact)
        dump('per-response.json', records)
        dump('raw-choice-errors.json', raw_errors)
        dump('quarantined-value-audit.json', extra_diagnostics)
    for name, h in protected.items():
        check('after '+name, sha256((ROOT/name).read_bytes()).hexdigest() == h)
    check('no ML runtime imported', not any(m in sys.modules for m in ('torch', 'transformers', 'accelerate')))
    dump('checks.json', {'status': 'PASS', 'count': len(checks), 'checks': checks,
                         'scope': 'USE and composite scores independently recomputed; prefix semantics reuse the unchanged prior audited scores'})
    dump('MANIFEST.json', {str(p.relative_to(out)): sha256(p.read_bytes()).hexdigest()
                           for p in sorted(out.rglob('*')) if p.is_file()})
    print(json.dumps({'status': 'PASS', 'checks': len(checks), 'candidate_status_counts': dict(counts),
                      'recovered_correct': compact['quarantined_required_semantics_correct'],
                      'recovered_incorrect': compact['quarantined_required_semantics_incorrect']}, ensure_ascii=False))


if __name__ == '__main__':
    main(sys.argv[1])
