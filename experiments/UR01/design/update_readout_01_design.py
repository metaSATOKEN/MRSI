"""UPDATE-READOUT-01 frozen repair/rollback diagnostic. Offline only; no model imports."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re

from aggregate_cross_model_e1_01 import load_payload
import readout_split_01_scoring as base
import saved_readout_01_scoring as readout

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'study2/designs/update-readout-01-20260925'
PROTOCOL = 'UPDATE-READOUT-01/v1'
METHODS = ('REWRITE', 'SELECT')
SOURCE = 'study2/designs/saved-readout-01-20260925/design.json'
PINS = {SOURCE: '9144fbb4a2d69a716de9720fb7a54ed8371cb1446abd1ba253b5f6238f3ae960',
        'scripts/readout_split_01_scoring.py': 'fc4bc5aa181a46745c6f29875d650a63c3e1908735331eda85ff653eb99b1e45',
        'scripts/saved_readout_01_scoring.py': '771585161c56963b938bb13ef36decafdaa9711125adfc1f3abc5eef4a73525a'}
enc = base.enc


def rank(value):
    return sha256((PROTOCOL + '|' + value).encode()).hexdigest()


def obj(properties):
    return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}


def schemas():
    origin = {'type': 'string', 'pattern': '^[A-Z][A-Z0-9_]{0,31}$'}
    row = obj({'observer': {'enum': ['A', 'B']}, 'paper': {'enum': ['ALL', 'NOT_ALL']},
               'digital': {'enum': ['ALL', 'NOT_ALL']}, 'origin_id': origin,
               'revision': {'type': 'integer', 'minimum': 1, 'maximum': 1000000}})
    private = obj({'customer': obj({'subject': {'enum': ['A', 'B']}, 'animal': {'enum': ['DOG', 'CAT']},
                                   'origin_id': origin}), 'coverage': row})
    choices = obj({r: {'enum': ['C1', 'C2', 'C3', 'C4']} for r in ('A', 'B')})
    return {'REWRITE': obj({'private_note': private, 'shared_note': obj({'coverage': obj({'A': row, 'B': row})})}),
            'SELECT': obj({'private_note': private, 'shared_choice': choices})}


def prompts(schema):
    common = ('あなたは架空の作業担当者です。保存済みの個別・共同ノートと、新たに届いた一件の通知から、次へ渡すノートを作ってください。'
        '新着通知が旧版の遅配である場合もあります。到着順ではなく、同じobserverのrevisionが最大の行を使ってください。'
        'AとBのrevisionを比較せず、それぞれの最新行を選びます。同じobserver・同じrevisionの候補は本資料では全欄同一です。'
        'PRIVATEの担当客customerをsubject・animal・origin_idごと保持し、PRIVATE.coverageにはholder本人の最新行を保持してください。'
        'GROUP.coverageにはAとBそれぞれの最新行を入れてください。observer・paper・digital・origin_id・revisionを一つの行として扱い、別の行の項目を混ぜないでください。'
        'row_catalogは今回の資料に実在する四行の一覧です。C1〜C4は今回だけの候補位置IDであり、元観測を表すorigin_idとは異なります。'
        'private_noteは両方式とも本文を記述します。案内方法、犬猫の選択回答、説明、受領票は出力しません。JSONのみを出力し、全必須欄とA/B固定キーを守ってください。\n')
    method = {'REWRITE': 'private_noteとshared_note.coverage.A/Bの本文を、schemaどおりに記述してください。\n',
              'SELECT': 'private_noteの本文と、shared_choice.A/Bに採用する候補位置IDを記述してください。保存器がその候補行を全欄そのまま複製します。同じ内容の候補が複数あれば、どれを選んでも構いません。shared_note本文は出力しません。\n'}
    return {m: common + method[m] + enc(schema[m]).decode() + '\n' for m in METHODS}


def build_design():
    for path, expected in PINS.items():
        if sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError('SOURCE_CHANGED:' + path)
    previous = json.loads((ROOT / SOURCE).read_bytes())
    for path, expected in previous['source_pins'].items():
        if sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError('SOURCE_CHANGED:' + path)
    original = load_payload(ROOT / 'study2/colab/cross_model_e1_01_main_onecell.py')
    repairs = sorted([c for c in previous['cases'] if c['set'] == 'STALE'], key=lambda c: rank('repair|' + c['source_response_id']))
    guards = []
    for method in ('REWRITE', 'SELECT'):
        for role in ('A', 'B'):
            for channel in ('PAPER', 'DIGITAL'):
                options = [c for c in previous['cases'] if c['set'] == 'MAIN' and
                           (c['source_condition'], c['role'], c['gold']['channel']) == (method, role, channel)]
                guards.append(min(options, key=lambda c: rank('guard|' + c['source_response_id'])))
    cases = []
    for subset, selected, prefix in [('REPAIR', repairs, 'R'), ('GUARD', guards, 'G')]:
        for i, source in enumerate(selected):
            c = deepcopy(source)
            for path, expected in c['source_files_sha256'].items():
                if sha256((ROOT / path).read_bytes()).hexdigest() != expected:
                    raise ValueError('EVIDENCE_CHANGED:' + path)
            source_input = next(path for path in c['source_files_sha256'] if path.endswith('/input.json'))
            source_memory = next(path for path in c['source_files_sha256'] if path.endswith('/saved-memory.json'))
            assert json.loads((ROOT / source_input).read_bytes())['payload'] == c['notes_payload']
            saved = json.loads((ROOT / source_memory).read_bytes())
            bodies = {r['record_id']: r['body'] for r in c['notes_payload']['records']}
            assert bodies == {'PRIVATE': saved['private_note'], 'GROUP': saved['shared_note']}
            material = original['bundle']['materials'][c['source_group']]
            latest = material['notices']
            assert latest == c['note_state']['latest_coverage']
            assert bodies['PRIVATE']['coverage'] == latest[c['role']]
            if subset == 'REPAIR':
                assert len(c['note_state']['stale_rows']) == 1
                target = c['note_state']['stale_rows'][0]
                notice = deepcopy(latest[target])
                assert notice['revision'] > bodies['GROUP']['coverage'][target]['revision']
            else:
                # Four self / four partner notices, balanced within holder and latest channel.
                target = c['role'] if (i + i // 2) % 2 == 0 else ('B' if c['role'] == 'A' else 'A')
                notice = deepcopy(material['baseline_by_role'][target]['private_note']['coverage'])
                assert notice['revision'] < latest[target]['revision']
                assert bodies['GROUP']['coverage'] == latest
            catalog = [{'location': 'PRIVATE.coverage', 'row': deepcopy(bodies['PRIVATE']['coverage'])}] + [
                {'location': 'GROUP.coverage.' + r, 'row': deepcopy(bodies['GROUP']['coverage'][r])} for r in ('A', 'B')]
            catalog.sort(key=lambda x: rank('catalog|' + c['source_response_id'] + '|' + x['location']))
            catalog.insert(i % 4, {'location': 'NOTICE', 'row': notice})
            catalog = [dict(row_id='C' + str(j + 1), **v) for j, v in enumerate(catalog)]
            # Check equal-revision ties: choosing any duplicate is acceptable.
            for a in catalog:
                for b in catalog:
                    if (a['row']['observer'], a['row']['revision']) == (b['row']['observer'], b['row']['revision']):
                        assert a['row'] == b['row']
            payload = dict(deepcopy(c['notes_payload']), incoming_notice=deepcopy(notice), row_catalog=catalog)
            expected = {'private_note': deepcopy(bodies['PRIVATE']), 'shared_note': {'coverage': deepcopy(latest)}}
            for role in ('A', 'B'):
                available = [v['row'] for v in catalog if v['row']['observer'] == role]
                assert max(available, key=lambda v: v['revision']) == latest[role]
            cases.append({'id': f'UR01-{prefix}{i+1:02}', 'set': subset, 'source_case': c['id'],
                'source_group': c['source_group'], 'source_condition': c['source_condition'], 'role': c['role'],
                'source_response_id': c['source_response_id'], 'source_files_sha256': c['source_files_sha256'],
                'original_notes_payload': c['notes_payload'], 'original_payload_sha256': c['payload_sha256'],
                'original_note_state': c['note_state'], 'notice_target': target,
                'notice_relation': 'SELF' if target == c['role'] else 'PARTNER', 'notice_catalog_position': i % 4 + 1,
                'update_payload': payload, 'update_payload_sha256': sha256(enc(payload)).hexdigest(),
                'expected_memory': expected, 'latest_channel': material['final_channel']})
    assert len(cases) == len({c['source_group'] for c in cases}) == 18
    repair_order = sorted(cases[:10], key=lambda c: rank('order|' + c['id']))
    guard_order = sorted(cases[10:], key=lambda c: rank('order|' + c['id']))
    blocks = []
    for i, c in enumerate(repair_order):
        blocks.append((c, METHODS if i % 2 == 0 else METHODS[::-1]))
        if i < len(guard_order):
            blocks.append((guard_order[i], METHODS if i % 2 == 0 else METHODS[::-1]))
    allocation = []; pipelines = []
    for rep in (1, 2):
        for case, order in blocks:
            order = order if rep == 1 else order[::-1]
            for method in order:
                pid = f'{case["id"]}-R{rep}-{method}'
                pipelines.append({'id': pid, 'case': case['id'], 'set': case['set'], 'condition': method, 'replicate': rep})
            for stage in ('UPDATE', 'READ'):
                seed = int(rank(f'seed|{case["id"]}|{rep}|{stage}')[:8], 16) % (2 ** 31)
                for pos, method in enumerate(order, 1):
                    pid = f'{case["id"]}-R{rep}-{method}'
                    allocation.append({'id': pid + '-' + stage, 'pipeline': pid, 'case': case['id'], 'set': case['set'],
                        'condition': method, 'replicate': rep, 'condition_position': pos, 'stage': stage, 'seed': seed,
                        'dependencies': [] if stage == 'UPDATE' else [pid + '-UPDATE']})
    schema = schemas()
    return {'protocol': PROTOCOL, 'status': 'DESIGN_FROZEN_NO_MODEL_GENERATION', 'source_pins': PINS | previous['source_pins'],
        'cases': cases, 'pipelines': pipelines, 'allocation': allocation, 'schemas': schema, 'prompts': prompts(schema),
        'read_prompt': previous['prompts']['EXTRACT'], 'read_schema': previous['schemas']['EXTRACT'],
        'model': previous['model'], 'limits': {'max_generations': 144, 'max_updates': 72, 'max_reads': 72,
            'seconds_including_setup': 5400, 'max_update_output_bytes': 16384, 'max_read_output_bytes': 4096,
            'automatic_regenerations': 0, 'cloud_drive': 'not_used', 'retention': 'private_no_deletion_deadline'},
        'decision_rules': {'repair': 18, 'repair_each_repeat': 9, 'guard': 14, 'guard_each_repeat': 7,
            'private_customer': 36, 'repair_contrast_lower_correct_per_20': 4, 'each_repeat_positive': True,
            'guard_nonnegative': True, 'p_value': None, 'confidence_interval': None}}


def requests(design):
    cases = {c['id']: c for c in design['cases']}
    return [{'id': s['id'], 'seed': s['seed'], 'messages': [
        {'role': 'system', 'content': design['prompts'][s['condition']]},
        {'role': 'user', 'content': '\n資料JSON:\n' + enc(cases[s['case']]['update_payload']).decode()}]}
        for s in design['allocation'] if s['stage'] == 'UPDATE']


def shape(value, schema, path='$'):
    if 'enum' in schema:
        return [] if type(value) is str and value in schema['enum'] else [path + ':ENUM']
    if schema['type'] == 'string':
        return [] if type(value) is str and re.fullmatch(schema['pattern'], value) else [path + ':STRING']
    if schema['type'] == 'integer':
        return [] if type(value) is int and schema['minimum'] <= value <= schema['maximum'] else [path + ':INTEGER']
    if type(value) is not dict:
        return [path + ':OBJECT']
    errors = [path + '.' + k + ':MISSING' for k in schema['required'] if k not in value]
    errors += [path + '.' + k + ':EXTRA' for k in value if k not in schema['properties']]
    for k, spec in schema['properties'].items():
        if k in value:
            errors += shape(value[k], spec, path + '.' + k)
    return errors


def materialize(value, payload, method, schema):
    """Structural/selector validation only; no expected memory or hidden latest truth."""
    if method not in METHODS:
        raise ValueError('UNKNOWN_METHOD')
    errors = shape(value, schema)
    if errors:
        return None, [], errors
    if method == 'REWRITE':
        return deepcopy(value), [], []
    catalog = {r['row_id']: r for r in payload['row_catalog']}
    if any(value['shared_choice'][r] not in catalog for r in ('A', 'B')):
        return None, [], ['UNRESOLVED_SELECTOR']
    chosen = {r: catalog[value['shared_choice'][r]] for r in ('A', 'B')}
    memory = {'private_note': deepcopy(value['private_note']),
              'shared_note': {'coverage': {r: deepcopy(chosen[r]['row']) for r in ('A', 'B')}}}
    trace = [{'target': r, 'row_id': chosen[r]['row_id'], 'location': chosen[r]['location'],
              'source_row_sha256': sha256(enc(chosen[r]['row'])).hexdigest()} for r in ('A', 'B')]
    return memory, trace, []


def ideal_update(case, method):
    memory = deepcopy(case['expected_memory'])
    if method == 'REWRITE':
        return memory
    if method != 'SELECT':
        raise ValueError('UNKNOWN_METHOD')
    return {'private_note': memory['private_note'], 'shared_choice': {r:
        next(v['row_id'] for v in case['update_payload']['row_catalog'] if v['row'] == memory['shared_note']['coverage'][r])
        for r in ('A', 'B')}}


def score_update(raw, case, method, schema, finish_reason='EOS'):
    result = {'gate': 'UNRESOLVED', 'parse_valid': None, 'format_valid': None, 'memory': None, 'choice_trace': [],
        'private_customer_exact': None, 'private_observation_exact': None, 'shared_rows_exact': {'A': None, 'B': None},
        'shared_values_exact': None, 'shared_provenance_exact': None, 'shared_latest_exact': None,
        'shared_row_matches_input': {'A': None, 'B': None}, 'joint_state_exact': None, 'errors': []}
    if method not in METHODS:
        raise ValueError('UNKNOWN_METHOD')
    if raw is None or finish_reason != 'EOS':
        result['errors'] = ['MISSING_OR_NON_EOS']; return result
    raw = raw.encode() if isinstance(raw, str) else raw
    if len(raw) > 16384:
        result.update(parse_valid=False, format_valid=False, gate='REJECT', errors=['OUTPUT_BYTES']); return result
    try:
        value = base.parse(raw)
    except (ValueError, UnicodeError, RecursionError):
        result.update(parse_valid=False, format_valid=False, gate='REJECT', errors=['JSON']); return result
    result['parse_valid'] = True
    memory, trace, errors = materialize(value, case['update_payload'], method, schema)
    result.update(format_valid=not errors, memory=memory, choice_trace=trace, errors=errors, gate='REJECT' if errors else 'PASS')
    if memory is None:
        return result
    expected = case['expected_memory']; group = memory['shared_note']['coverage']; latest = expected['shared_note']['coverage']
    result['private_customer_exact'] = memory['private_note']['customer'] == expected['private_note']['customer']
    result['private_observation_exact'] = memory['private_note']['coverage'] == expected['private_note']['coverage']
    result['shared_rows_exact'] = {r: group[r] == latest[r] for r in ('A', 'B')}
    result['shared_values_exact'] = all(group[r][m] == latest[r][m] for r in ('A', 'B') for m in ('paper', 'digital'))
    result['shared_provenance_exact'] = all(group[r][m] == latest[r][m] for r in ('A', 'B') for m in ('observer', 'origin_id', 'revision'))
    result['shared_latest_exact'] = all(result['shared_rows_exact'].values())
    result['shared_row_matches_input'] = {r: any(group[r] == v['row'] for v in case['update_payload']['row_catalog']) for r in ('A', 'B')}
    result['joint_state_exact'] = all(result[k] for k in ('private_customer_exact', 'private_observation_exact', 'shared_latest_exact'))
    return result


def read_payload(case, memory):
    if memory is None:
        raise ValueError('NO_ACCEPTED_MEMORY')
    payload = deepcopy(case['original_notes_payload'])
    payload['records'] = [{'record_id': 'PRIVATE', 'body': deepcopy(memory['private_note'])},
                          {'record_id': 'GROUP', 'body': deepcopy(memory['shared_note'])}]
    return payload


def read_request(design, slot, case, memory):
    if slot['stage'] != 'READ':
        raise ValueError('NOT_READ_SLOT')
    return {'id': slot['id'], 'seed': slot['seed'], 'messages': [
        {'role': 'system', 'content': design['read_prompt']},
        {'role': 'user', 'content': '\n資料JSON:\n' + enc(read_payload(case, memory)).decode()}]}


def score_read(raw, memory, case, schema, finish_reason='EOS'):
    if memory is None:
        return {'dependency_missing': True, 'format_valid': None, 'four_exact': None, 'channel_note': None, 'channel_latest': None}
    group = memory['shared_note']['coverage']; latest = case['expected_memory']['shared_note']['coverage']
    pseudo_case = {'gold': {'four_values': group, 'channel': base.compute_channel(group),
        'latest_four_values': latest, 'latest_channel': case['latest_channel']}}
    result = readout.score(raw, pseudo_case, 'EXTRACT', schema, finish_reason)
    result['dependency_missing'] = False
    return result


def end_to_end(update, read):
    if update.get('gate') != 'PASS' or read.get('format_valid') is not True:
        return None
    return base.tri_all([update['joint_state_exact'], read.get('four_exact'), read.get('channel_latest')])


def summarize(design, outcomes):
    expected_ids = {p['id'] for p in design['pipelines']}
    if set(outcomes) - expected_ids:
        raise ValueError('UNEXPECTED_PIPELINE')
    def values(method, metric, subset=None, rep=None):
        out = []
        for p in design['pipelines']:
            if p['condition'] != method or (subset is not None and p['set'] != subset) or (rep is not None and p['replicate'] != rep):
                continue
            item = outcomes.get(p['id'], {}); update = item.get('update', {}); read = item.get('read', {})
            out.append(end_to_end(update, read) if metric == 'end_to_end_exact' else update.get(metric))
        return out
    def metric_summary(method, metric):
        groups = {s: base.counts(values(method, metric, s)) for s in ('REPAIR', 'GUARD')}
        reps = {s: {str(r): base.counts(values(method, metric, s, r)) for r in (1, 2)} for s in groups}
        person = base.counts(values(method, 'private_customer_exact'))
        tests = [(groups['REPAIR'], 18), (groups['GUARD'], 14), (person, 36)]
        tests += [(v, 9 if s == 'REPAIR' else 7) for s in reps for v in reps[s].values()]
        status = 'MET' if all(c['correct'] >= n for c, n in tests) else 'NOT_MET' if any(c['correct'] + c['unresolved'] < n for c, n in tests) else 'INCONCLUSIVE'
        return {'by_set': groups, 'by_repeat': reps, 'private_customer': person, 'criterion_status': status}
    def signal(a, b, metric):
        return (base.difference(values(a, metric, 'REPAIR'), values(b, metric, 'REPAIR'))[0] >= 4/20 - 1e-12
            and all(base.difference(values(a, metric, 'REPAIR', r), values(b, metric, 'REPAIR', r))[0] > 1e-12 for r in (1, 2))
            and base.difference(values(a, metric, 'GUARD'), values(b, metric, 'GUARD'))[0] >= -1e-12)
    metrics = ('joint_state_exact', 'end_to_end_exact')
    return {'kind': 'DESCRIPTIVE_UPDATE_AND_READOUT', 'planned_pipelines': 72, 'planned_responses': 144,
        'materials': {'REPAIR': 10, 'GUARD': 8},
        'methods': {m: {metric: metric_summary(m, metric) for metric in metrics} for m in METHODS},
        'contrasts': {metric: {'repair_bounds': base.difference(values('SELECT', metric, 'REPAIR'), values('REWRITE', metric, 'REPAIR')),
            'guard_bounds': base.difference(values('SELECT', metric, 'GUARD'), values('REWRITE', metric, 'GUARD')),
            'positive_signal': signal('SELECT', 'REWRITE', metric), 'negative_signal': signal('REWRITE', 'SELECT', metric)} for metric in metrics},
        'p_value': None, 'confidence_interval': None}


def freeze():
    design = build_design(); OUT.mkdir(parents=True, exist_ok=False)
    items = {'design.json': enc(design) + b'\n', 'update-requests.json': enc(requests(design)) + b'\n',
        'update_readout_01_design.py': Path(__file__).read_bytes(),
        'readout_split_01_scoring.py': (ROOT / 'scripts/readout_split_01_scoring.py').read_bytes(),
        'saved_readout_01_scoring.py': (ROOT / 'scripts/saved_readout_01_scoring.py').read_bytes(),
        'prompt-rewrite.txt': design['prompts']['REWRITE'].encode(), 'prompt-select.txt': design['prompts']['SELECT'].encode(),
        'prompt-read.txt': design['read_prompt'].encode()}
    for name, raw in items.items(): (OUT / name).write_bytes(raw)
    v = {'kind': 'OFFLINE_DESIGN_FREEZE_NO_MODEL_RESULTS', 'files_sha256': {n: sha256(b).hexdigest() for n, b in items.items()},
         'materials': 18, 'planned_update_requests': 72, 'planned_conditional_read_requests': 72, 'model_generations': 0}
    (OUT / 'verification.json').write_text(json.dumps(v, indent=2) + '\n')
    print(json.dumps(v))


if __name__ == '__main__':
    freeze()
