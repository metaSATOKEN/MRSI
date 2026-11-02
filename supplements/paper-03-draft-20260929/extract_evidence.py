"""Read-only extraction for Paper 3; no model calls or rescoring."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'papers/paper-03'

def read(rel):
    return json.loads((ROOT / rel).read_text())

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
    OUT.mkdir(exist_ok=True)
    sources, tables, examples = {}, {}, {}
    for name in ['summary-timing-01', 'summary-timing-02', 'judgment-repeat-01']:
        base = f'study2/results/{name}-20260929'
        for leaf in ['reaggregated.json', 'diagnostics.json', 'reason-review.json']:
            p = ROOT / base / leaf
            sources[str(p.relative_to(ROOT))] = digest(p)
        report = read(f'{base}/reaggregated.json')['report']
        diagnostics = read(f'{base}/diagnostics.json')
        if name != 'judgment-repeat-01':
            rows = []
            for arm in ['LATE', 'EARLY']:
                m = report['by_condition'][arm]['metrics']
                comp = diagnostics['stage_components'][arm]
                rows.append({'arm': arm,
                    'FORM': [comp['FORM']['metrics']['V'][k] for k in ['correct', 'n']],
                    **{key: [m[key][k] for k in ['correct', 'n']] for key in ['I','J','K','G','wrong_agreement']},
                    'USE': [comp['USE']['metrics']['V'][k] for k in ['correct','n']],
                    'artificial_recheck': [comp['RECHECK_DIAGNOSTIC']['metrics']['V'][k] for k in ['correct','n']],
                    'progression': report['by_condition'][arm]['progression']['status']})
            tables[name] = {'rows': rows, 'status_counts': report['status_counts'],
                'stage_totals': {s: sum(x['stage']==s and x['status']=='EOS' for x in report['by_slot'])
                    for s in sorted(set(x['stage'] for x in report['by_slot']))}}
            if name == 'summary-timing-02':
                examples['ST02_N05_EARLY_LOWER'] = [x for x in report['by_slot']
                    if x['case']=='N05' and x['condition_not_for_model']=='EARLY'
                    and (x['id'].startswith('ST02-EARLY-N05-LOWER-') or x['stage']=='FORM')]
                examples['ST02_N05_EARLY_LOWER_input'] = [x for x in diagnostics['nonpassing']
                    if x['case']=='N05' and x['condition']=='EARLY']
        else:
            tables[name] = {k: report[k] for k in ['fixed_inputs','planned_responses','materials','fresh_repeats',
                'by_repeat','fixed_input_stability','descriptive_by_stage','formation_prediction','status_counts']}
            examples['JR01_selected'] = [x for x in diagnostics['all_responses'] if x['stage']=='CONFIRM'
                and ((x['case']=='N05' and x['initial_type'] in ['LOWER','DUPLICATE'])
                    or (x['case']=='N02' and x['initial_type']=='OPTIMAL'))]
    assert [x['I'][0] for x in tables['summary-timing-01']['rows']] == [15,24]
    assert [x['I'][0] for x in tables['summary-timing-02']['rows']] == [15,24]
    assert [x['J'][0] for x in tables['summary-timing-01']['rows']] == [14,23]
    assert [x['J'][0] for x in tables['summary-timing-02']['rows']] == [15,23]
    jr = tables['judgment-repeat-01']
    for arm, expected in [('LATE',[13,13,11]),('EARLY',[16,16,16])]:
        assert [jr['by_repeat'][str(i)]['FORM']['by_condition'][arm]['F']['correct'] for i in [1,2,3]] == expected
    assert len(examples['JR01_selected']) == 18
    result = {'purpose':'Published-result extraction; no new inferential analysis or rescoring',
        'source_sha256':sources, 'tables':tables, 'examples':examples}
    target = OUT/'evidence-extract-v0.1-2026-09-29.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'output':str(target),'source_files':len(sources),
        'JR_examples':len(examples['JR01_selected']),
        'ST02_example_ids':[x['id'] for x in examples['ST02_N05_EARLY_LOWER']]}))

if __name__ == '__main__':
    run()
