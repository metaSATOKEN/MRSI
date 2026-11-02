"""RU01 offline fixed inputs, interventions and scoring. Standard library; no model."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import zipfile

import owner_recency_01_scoring as receiver
import update_readout_01_scoring as base

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'study2/designs/role-shared-use-01-20260925'
PROTOCOL = 'ROLE-SHARED-USE-01/v1'
ARMS = ('P0G0', 'P1G0', 'P0G1', 'P1G1')
SOURCE = 'throughline/audits/self-update-exchange-01-result-20260925/npp-sx01-result-20260925-104011-dacc6122.zip'
SOURCE_SHA = '6655aab50dead38cea2e4060475366db88e83c3351c524e10052ad067945ee36'
SOURCE_DESIGN_SHA = '64ed94a8e4d08400d9df709675c1f7fd1f71c4917db5220f3e9eae887a8847a9'
DEPENDENCIES = ('owner_recency_01_scoring.py', 'update_readout_01_scoring.py',
                'update_readout_01_envelope.py', 'saved_readout_01_scoring.py',
                'readout_split_01_scoring.py')
enc = base.enc


def digest(value):
    return sha256(enc(value)).hexdigest()


def read_sources(path=None):
    """Read every terminal note by fixed allocation, without outcome-based selection."""
    path = Path(path) if path else ROOT / SOURCE
    if sha256(path.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError('SOURCE_ARCHIVE_CHANGED')
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if len(names) != len(set(names)):
            raise ValueError('DUPLICATE_ARCHIVE_PATH')
        manifest = json.loads(z.read('FEEDBACK_MANIFEST.json'))['files_sha256']
        if set(names) != set(manifest) | {'FEEDBACK_MANIFEST.json'}:
            raise ValueError('SOURCE_MEMBER_SET')
        for name, h in manifest.items():
            if sha256(z.read(name)).hexdigest() != h:
                raise ValueError('SOURCE_MEMBER_CHANGED:' + name)
        raw = z.read('design.json')
        if sha256(raw).hexdigest() != SOURCE_DESIGN_SHA:
            raise ValueError('SOURCE_DESIGN_CHANGED')
        old = json.loads(raw)
        cases = {c['id']: c for c in old['cases']}
        sources = []
        for slot in old['allocation']:
            if slot['stage'] != 'DELAY':
                continue
            prefix = 'responses/' + slot['id'] + '/'
            note_raw, result_raw = z.read(prefix + 'saved-memory.json'), z.read(prefix + 'result.json')
            memory, result = json.loads(note_raw), json.loads(result_raw)
            if result['id'] != slot['id'] or result['status'] != 'EOS':
                raise ValueError('SOURCE_NOTE_UNAVAILABLE')
            if sha256(note_raw).hexdigest() != result['files_sha256']['saved-memory.json']:
                raise ValueError('SOURCE_NOTE_BINDING')
            if base.shape(memory, old['update_schema']):
                raise ValueError('SOURCE_NOTE_SCHEMA')
            role = slot['role']
            if memory['private_note']['customer']['subject'] != role:
                raise ValueError('SOURCE_CUSTOMER_OWNER')
            if memory['private_note']['coverage'] != memory['shared_note']['coverage'][role]:
                raise ValueError('SOURCE_DUPLICATE_CONFLICT')
            if base.compute_channel(memory['shared_note']['coverage']) not in ('PAPER', 'DIGITAL'):
                raise ValueError('SOURCE_CHANNEL_NOT_UNIQUE')
            case = cases[slot['case']]
            sources.append({'id': slot['run'].replace('SX01-', 'RU01-') + '-' + role,
                            'case': slot['case'].replace('SX01-', 'RU01-'),
                            'run': slot['run'].replace('SX01-', 'RU01-'),
                            'replicate': slot['replicate'], 'role': role,
                            'scene': case['scene'], 'item': case['item'],
                            'source_response': slot['id'],
                            'source_memory_path': prefix + 'saved-memory.json',
                            'source_memory_sha256': sha256(note_raw).hexdigest(),
                            'source_result_path': prefix + 'result.json',
                            'source_result_sha256': sha256(result_raw).hexdigest(),
                            'memory': memory})
    if len(sources) != 32 or len({s['id'] for s in sources}) != 32:
        raise ValueError('SOURCE_ID_SET')
    return old, sources


def intervene(memory, arm):
    """Research counterfactual; preserve original and record every changed leaf."""
    if arm not in ARMS:
        raise ValueError('UNKNOWN_ARM')
    result = deepcopy(memory)
    if arm[1] == '1':
        value = result['private_note']['customer']['animal']
        result['private_note']['customer']['animal'] = {'DOG': 'CAT', 'CAT': 'DOG'}[value]
    if arm[3] == '1':
        rows = [result['private_note']['coverage'], *result['shared_note']['coverage'].values()]
        for row in rows:
            row['paper'], row['digital'] = row['digital'], row['paper']
    changes = []
    def compare(left, right, path=''):
        if isinstance(left, dict):
            if set(left) != set(right):
                raise ValueError('INTERVENTION_SHAPE_CHANGED')
            for key in sorted(left):
                compare(left[key], right[key], path + '.' + key if path else key)
        elif left != right:
            changes.append({'path': path, 'before': left, 'after': right})
    compare(memory, result)
    return result, {'kind': 'RESEARCH_COUNTERFACTUAL_NOT_OBSERVED_UPDATE' if arm != 'P0G0' else 'ORIGINAL_SAVED_CONTENT',
                    'arm': arm, 'before_content_sha256': digest(memory),
                    'after_content_sha256': digest(result), 'changes': changes}


def input_payload(source, memory):
    return {'holder': source['role'], 'scene': source['scene'], 'item': source['item'],
            'records': [{'record_id': 'PRIVATE', 'body': deepcopy(memory['private_note'])},
                        {'record_id': 'GROUP', 'body': deepcopy(memory['shared_note'])}]}


def expected_answer(payload):
    records = {r['record_id']: r['body'] for r in payload['records']}
    return {'customer': {k: records['PRIVATE']['customer'][k] for k in ('subject', 'animal')},
            'coverage': {o: {k: records['GROUP']['coverage'][o][k] for k in ('paper', 'digital')}
                         for o in ('A', 'B')}}


def response_schema(old):
    schema = deepcopy(old['read_schema'])
    schema['properties']['customer'] = {'type': 'object', 'properties': {
        'subject': {'enum': ['A', 'B']}, 'animal': {'enum': ['DOG', 'CAT']}},
        'required': ['subject', 'animal'], 'additionalProperties': False}
    schema['required'] = ['customer', 'coverage']
    return schema


def build_design():
    old, sources = read_sources()
    schema = response_schema(old)
    prompt = ('あなたは架空の作業担当者です。今回の資料だけを使い、担当客に渡すカードの絵柄と、'
              '共同の案内に使う観測値を一つのJSONで返してください。'
              'recordsのrecord_idがPRIVATEのbody.customerからsubjectとanimalを取り出し、customerに書きます。'
              'animalはそのままカードの絵柄として使います。役名や場面から希望を推測せず、記載された希望を使ってください。'
              'record_idがGROUPのbody.coverageからA/B両方のpaperとdigitalを、そのままcoverageに転記します。'
              'ALLとNOT_ALLを保ち、本人の担当に関係なく四値をすべて書いてください。'
              '案内方法は後でこの四値から計算するので、ここでは選びません。'
              '理由、元ID、版、参照名、余分な欄は出力せず、JSONのみで全必須欄を満たしてください。\n'
              + enc(schema).decode() + '\n')
    runs = [{k: r[k] for k in ('id', 'case', 'replicate')} for r in old['runs']]
    for run in runs:
        run['id'] = run['id'].replace('SX01-', 'RU01-')
        run['case'] = run['case'].replace('SX01-', 'RU01-')
    source_map = {s['id']: s for s in sources}
    branches, allocation = [], []
    for i, run in enumerate(runs):
        roles = ('A', 'B') if i % 2 == 0 else ('B', 'A')
        for j, role in enumerate(roles):
            source = source_map[run['id'] + '-' + role]
            shift = (2 * i + j) % 4
            order = ARMS[shift:] + ARMS[:shift]
            if run['replicate'] == 2:
                order = order[::-1]
            seed = int(digest([PROTOCOL, source['id'], 'generation'])[:8], 16) % 2**31
            for pos, arm in enumerate(order, 1):
                memory, trace = intervene(source['memory'], arm)
                payload = input_payload(source, memory)
                sid = source['id'] + '-' + arm
                branches.append({'id': sid, 'source_id': source['id'], 'arm': arm,
                                 'payload': payload, 'payload_sha256': digest(payload),
                                 'trace': trace, 'gold': expected_answer(payload)})
                allocation.append({'id': sid, 'source_id': source['id'], 'run': run['id'], 'case': run['case'],
                                   'role': role, 'replicate': run['replicate'], 'arm': arm,
                                   'condition_position': pos, 'seed': seed, 'dependencies': []})
    return {'protocol': PROTOCOL, 'status': 'DESIGN_FROZEN_NO_MODEL_GENERATION',
            'source_archive': SOURCE, 'source_archive_sha256': SOURCE_SHA,
            'source_design_sha256': SOURCE_DESIGN_SHA, 'sources': sources, 'branches': branches,
            'runs': runs, 'allocation': allocation, 'schema': schema, 'prompt': prompt,
            'model': deepcopy(old['model']),
            'limits': {'max_generations': 128, 'seconds_including_setup': 2700, 'reserved_final_seconds': 90,
                       'automatic_regenerations': 0, 'raw_answer_bytes': 4096,
                       'cloud_drive': 'not_used', 'retention': 'private_no_deletion_deadline'},
            'decision_rules': {'complete_pair_runs': 14, 'each_repeat': 7, 'p_value': None, 'confidence_interval': None},
            'source_pins': {'scripts/' + n: sha256((ROOT / 'scripts' / n).read_bytes()).hexdigest()
                            for n in DEPENDENCIES}}


def requests(design):
    branches = {b['id']: b for b in design['branches']}
    return [{'id': s['id'], 'seed': s['seed'], 'messages': [
        {'role': 'system', 'content': design['prompt']},
        {'role': 'user', 'content': '\n資料JSON:\n' + enc(branches[s['id']]['payload']).decode()}]}
        for s in design['allocation']]


def actions(answer):
    """No access to input or gold: the animal is used as returned, channel from returned four."""
    return {'card_animal': answer['customer']['animal'], 'subject': answer['customer']['subject'],
            'channel': base.compute_channel(answer['coverage'])}


def score_response(raw, payload, schema, finish_reason='EOS'):
    receipt = receiver.receive(raw, 'READ', finish_reason)
    result = {'format_valid': False, 'subject': None, 'animal': None, 'four_exact': None,
              'channel': None, 'joint': None, 'answer': None, 'actions': None,
              'normalization': {k: v for k, v in receipt.items() if k != 'normalized_bytes'}, 'errors': []}
    if receipt['normalized_bytes'] is None:
        result['errors'] = [receipt['reason']]
        return result
    answer = base.parse(receipt['normalized_bytes'])
    errors = base.shape(answer, schema)
    if errors:
        result['errors'] = errors
        return result
    expected = expected_answer(payload)
    actual_actions = actions(answer)
    result.update(format_valid=True, subject=answer['customer']['subject'] == expected['customer']['subject'],
                  animal=answer['customer']['animal'] == expected['customer']['animal'],
                  four_exact=answer['coverage'] == expected['coverage'],
                  channel=actual_actions['channel'] == base.compute_channel(expected['coverage']),
                  answer=answer, actions=actual_actions)
    result['joint'] = all(result[k] for k in ('subject', 'animal', 'four_exact', 'channel'))
    return result


def contrast(left, right, axis):
    if axis not in ('P', 'G'):
        raise ValueError('CONTRAST_AXIS')
    if left.get('format_valid') is not True or right.get('format_valid') is not True:
        return {'target_changed': None, 'off_target_unchanged': None, 'aligned': None}
    l, r = left['answer'], right['answer']
    if axis == 'P':
        target = l['customer']['animal'] != r['customer']['animal']
        off = l['coverage'] == r['coverage'] and l['customer']['subject'] == r['customer']['subject']
    else:
        target = l['coverage'] != r['coverage'] and left['actions']['channel'] != right['actions']['channel']
        off = l['customer'] == r['customer']
    return {'target_changed': target, 'off_target_unchanged': off,
            'aligned': left['joint'] and right['joint'] and target and off}


def summarize(design, outcomes):
    ids = {s['id'] for s in design['allocation']}
    if set(outcomes) - ids:
        raise ValueError('UNEXPECTED_RESPONSE')
    counts = base.counts
    paths = []
    pairs = []
    edges = []
    for run in design['runs']:
        values = [outcomes.get(run['id'] + '-' + role + '-' + arm, {}) for role in ('A', 'B') for arm in ARMS]
        success = all(s.get('joint') is True for s in values) if all(s.get('format_valid') is True for s in values) else None
        paths.append({**run, 'success': success})
        for arm in ARMS:
            left, right = [outcomes.get(run['id'] + '-' + role + '-' + arm, {}) for role in ('A', 'B')]
            row = {'run': run['id'], 'arm': arm, 'distinct_animals': None, 'same_channel': None, 'joint': None}
            if left.get('format_valid') is True and right.get('format_valid') is True:
                row.update(distinct_animals=left['actions']['card_animal'] != right['actions']['card_animal'],
                           same_channel=left['actions']['channel'] == right['actions']['channel'],
                           joint=left['joint'] and right['joint'])
            pairs.append(row)
        for role in ('A', 'B'):
            for axis, names in [('P', ('P0G0', 'P1G0')), ('P', ('P0G1', 'P1G1')),
                                ('G', ('P0G0', 'P0G1')), ('G', ('P1G0', 'P1G1'))]:
                l, r = [outcomes.get(run['id'] + '-' + role + '-' + arm, {}) for arm in names]
                edges.append({'run': run['id'], 'role': role, 'axis': axis, 'arms': list(names), **contrast(l, r, axis)})
    total = counts([p['success'] for p in paths])
    reps = {str(r): counts([p['success'] for p in paths if p['replicate'] == r]) for r in (1, 2)}
    tests = [(total, design['decision_rules']['complete_pair_runs'])] + [(x, design['decision_rules']['each_repeat']) for x in reps.values()]
    status = 'MET' if all(c['correct'] >= n for c, n in tests) else 'NOT_MET' if any(c['correct'] + c['unresolved'] < n for c, n in tests) else 'INCONCLUSIVE'
    component_names = ('subject', 'animal', 'four_exact', 'channel', 'joint')
    by_arm = {arm: {k: counts([outcomes.get(s['id'], {}).get(k) for s in design['allocation'] if s['arm'] == arm])
                    for k in component_names} for arm in ARMS}
    return {'protocol': PROTOCOL, 'materials': 8, 'pair_runs': 16, 'planned_responses': 128,
            'supplied_outcomes': len(outcomes), 'path': total, 'by_repeat': reps, 'criterion_status': status,
            'path_fraction_missing_bounds': [total['correct']/16, (total['correct']+total['unresolved'])/16],
            'by_arm': by_arm, 'paths': paths, 'condition_pairs': pairs,
            'pair_metrics': {k: counts([p[k] for p in pairs]) for k in ('distinct_animals','same_channel','joint')},
            'contrasts': {axis: {k: counts([e[k] for e in edges if e['axis']==axis])
                                for k in ('target_changed','off_target_unchanged','aligned')} for axis in ('P','G')},
            'contrast_rows': edges, 'p_value': None, 'confidence_interval': None}


def freeze():
    design = build_design()
    OUT.mkdir(parents=True, exist_ok=False)
    def write(name, value):
        (OUT / name).write_bytes(enc(value) + b'\n')
    write('design.json', design)
    write('requests.json', requests(design))
    write('schema.json', design['schema'])
    (OUT / 'prompt.txt').write_text(design['prompt'])
    with zipfile.ZipFile(ROOT / SOURCE) as z:
        for source in design['sources']:
            directory = OUT / 'sources' / source['id']
            directory.mkdir(parents=True)
            for kind in ('memory', 'result'):
                raw = z.read(source['source_' + kind + '_path'])
                assert sha256(raw).hexdigest() == source['source_' + kind + '_sha256']
                (directory / (kind + '.json')).write_bytes(raw)
    for name in ('role_shared_use_01_design.py', *DEPENDENCIES):
        (OUT / name).write_bytes((ROOT / 'scripts' / name).read_bytes())
    (OUT / 'README.md').write_text('# ROLE-SHARED-USE-01 固定設計\n\n'
        'SX01全32最終ノート×本人希望反転2×観測反転2＝128固定入力。\n'
        'P0G0は実保存内容、他の三条件は研究者操作の対照枝。原ノートは不変。\n'
        '観測はGROUPとPRIVATEの同じ写しを一緒に反転し、IDと版を保持する。\n'
        '派生枝は実際の更新や元観測の忠実な複製ではない。\n'
        'LLMは担当客のsubject/animalと共同四値を返し、案内だけ実四値からコード計算。\n'
        '8材料・16ペア実行、最大128生成・45分案。Colab実行器・実モデル生成は未実施。\n')
    write('MANIFEST.json', {str(p.relative_to(OUT)): sha256(p.read_bytes()).hexdigest()
                            for p in sorted(OUT.rglob('*')) if p.is_file()})
    print(json.dumps({'path': str(OUT), 'design_sha256': sha256((OUT/'design.json').read_bytes()).hexdigest(),
                      'requests_sha256': sha256((OUT/'requests.json').read_bytes()).hexdigest(),
                      'sources': len(design['sources']), 'requests': len(design['allocation'])}))


if __name__ == '__main__':
    freeze()
