"""TB01 fixed three-role pilot. Standard library only; no model calls."""
from copy import deepcopy
from hashlib import sha256
import json
import random

PROTOCOL = 'THREE-ROLE-BOUNDARY-01-v0.1'
ROLES = ('A', 'B', 'C')
MEDIA = ('PAPER', 'DIGITAL')
STAGES = ('FORM', 'VOTE', 'READ')
REPEATS = (1, 2)


def enc(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return sha256(enc(value)).hexdigest()


def seed(sid):
    return int(sha256(('TB01-20261013|' + sid).encode()).hexdigest()[:8], 16) % 2**31


def obj(**fields):
    return {'type': 'object', 'properties': fields, 'required': list(fields), 'additionalProperties': False}


def choice(*values):
    return {'type': 'string', 'enum': list(values)}


TEXT = {'type': 'string', 'minLength': 1, 'maxLength': 128}
OWN = obj(holder=choice(*ROLES), recommendation=choice(*MEDIA),
          evidence_ids={'type': 'array', 'items': TEXT, 'minItems': 1, 'maxItems': 6})
SCHEMAS = {
    'FORM': obj(own=OWN),
    'VOTE': obj(own=OWN, vote=obj(proposal_id=TEXT, decision=choice('ACCEPT', 'HOLD'))),
    'READ': obj(own=OWN, approval_state=obj(**{r: choice('ACCEPT', 'HOLD', 'MISSING', 'WRONG_PROPOSAL') for r in ROLES}),
                agreement=choice('AGREED', 'PENDING'), joint_action=choice(*MEDIA, 'HOLD')),
}
COMMON = '''あなたは三人の担当者のうちholderで示された本人です。出力は指定schemaのJSON一個だけ。説明文や追加キーは出さない。
各人は自分の客に案内する媒体をPAPERまたはDIGITALから推奨する。本人推奨は自分の全経験を合算した成功人数/試行人数の高い媒体とする。ownには本人のholder、推奨、本人の全経験のIDを記録する。他人の経験を本人の根拠に混ぜない。
共同作業では資源の数が限られる。提示された二つの実行可能な候補のうち、三人分の予測成功人数の合計が高い候補が適切である。本人推奨と共同で担当する媒体は異なってよい。共同担当に合わせて本人推奨を書き換えない。
本人集計と共同候補の合計は、それぞれ対応する経験から計算済みの補助資料である。保存ノートは過去の本人の出力であり、経験資料より優先する正解ではない。
合意成立には、同一proposal_idへのA、B、C全員の明示的ACCEPTが必要。二人の賛成や未返答者の推測では成立しない。候補の合計がよいことも、全員の承認の代わりにはならない。
'''
PROMPTS = {
    'FORM': COMMON + '今回は本人推奨の形成だけを行う。共同の投票や割付は出力しない。\n',
    'VOTE': COMMON + '今回は提示されたproposalを本人として確認する。合計が高い候補ならACCEPT、低い候補ならHOLD。同意は本人一人の分だけであり他人の承認を代行しない。proposal_idは提示されたものをそのまま書く。\n',
    'READ': COMMON + '''今回は保存された投票記録の読出しを行う。ownは本人の経験に基づく推奨を記す。
receiptsのsenderは保存器が当事者に結び付けた身元である。approval_stateには各senderの同一proposal_idへの実際のdecisionを記す。該当senderの記録がなければMISSING、別proposal_idへの票ならWRONG_PROPOSALとする。
全員が同一案へACCEPTならAGREEDとし、その案の本人担当をjoint_actionへ転記する。それ以外はPENDINGとしjoint_actionはHOLDとする。読出しでは合意の再最適化や新しい投票をしない。合意の有無と案の良し悪しは別に報告する。
''',
}


def materials():
    """Three numeric triads; minority and last voter each rotate across A/B/C."""
    specifications = [
        ('T01', ('A', 'B', 'C'), 'PAPER', [(34, 22), (27, 23), (18, 30)]),
        ('T02', ('B', 'C', 'A'), 'DIGITAL', [(33, 24), (29, 26), (17, 31)]),
        ('T03', ('C', 'A', 'B'), 'PAPER', [(32, 21), (26, 22), (19, 29)]),
    ]
    result = []
    for idx, (cid, order, scarce, totals) in enumerate(specifications):
        other = next(m for m in MEDIA if m != scarce)
        rows = []
        for role, (scarce_n, other_n) in zip(order, totals):
            for session in (1, 2):
                values = {}
                for medium, total in [(scarce, scarce_n), (other, other_n)]:
                    first = max(total - 20, min(20, total // 2 + (2 if medium == scarce else -2)))
                    values[medium] = {'success': first if session == 1 else total - first, 'trials': 20}
                rows.append({'id': 'E' + sha256(f'TB01|{cid}|{role}|{session}'.encode()).hexdigest()[:10],
                             'owner': role, 'session': session, 'observed': values})
        candidates = []
        # Random-looking IDs/order do not reveal the higher-total candidate.
        for number, recipient in enumerate(order[:2]):
            assignment = {r: scarce if r == recipient else other for r in ROLES}
            candidates.append({'candidate_id': ['C1', 'C2'][(number + idx) % 2], 'assignment': assignment})
        random.Random(2026101301 + idx).shuffle(candidates)
        result.append({'id': cid, 'scene': ['町の相談会', '地域の展示会', '共同の案内所'][idx],
                       'role_order': list(order), 'vote_order': [order[0], order[2], order[1]],
                       'resource_count': {scarce: 1, other: 2}, 'experiences': rows, 'candidates': candidates})
    return result


def own_summary(case, role):
    rows = [r for r in case['experiences'] if r['owner'] == role]
    values = {}
    for medium in MEDIA:
        success = sum(r['observed'][medium]['success'] for r in rows)
        trials = sum(r['observed'][medium]['trials'] for r in rows)
        assert trials == 40
        values[medium] = {'success': success, 'trials': trials, 'expected_success_for_40': success}
    return {'owner': role, 'source_ids': [r['id'] for r in rows], 'by_medium': values}


def candidate_table(case):
    table = []
    for c in case['candidates']:
        each = {r: own_summary(case, r)['by_medium'][c['assignment'][r]]['expected_success_for_40'] for r in ROLES}
        table.append(dict(deepcopy(c), expected_success_by_role=each, expected_total=sum(each.values()),
                          source_ids=[row['id'] for row in case['experiences']]))
    return table


def form_id(case, rep, role):
    return f'TB01-{case}-R{rep}-FORM-{role}'


def vote_id(case, rep, branch, role):
    return f'TB01-{case}-R{rep}-{branch}-VOTE-{role}'


def allocation(cases):
    slots = []
    units = [(case, rep) for case in cases for rep in REPEATS]
    random.Random(2026101302).shuffle(units)
    for case, rep in units:
        cid = case['id']
        for r in case['role_order']:
            slots.append({'id': form_id(cid, rep, r), 'stage': 'FORM', 'case': cid, 'repeat': rep,
                          'role': r, 'branch': None, 'snapshot': None, 'parents': []})
        branches = ['HIGHER', 'LOWER'] if (int(cid[-1]) + rep) % 2 else ['LOWER', 'HIGHER']
        for branch in branches:
            arrived = []
            for i, r in enumerate(case['vote_order']):
                vid = vote_id(cid, rep, branch, r)
                slots.append({'id': vid, 'stage': 'VOTE', 'case': cid, 'repeat': rep, 'role': r,
                              'branch': branch, 'snapshot': None, 'parents': [form_id(cid, rep, r)]})
                arrived.append(vid)
                if i in (1, 2):
                    snap = 'TWO_RECEIVED' if i == 1 else 'THREE_RECEIVED'
                    for holder in case['role_order']:
                        own_parent = vote_id(cid, rep, branch, holder)
                        if own_parent not in arrived:
                            own_parent = form_id(cid, rep, holder)
                        parents = list(dict.fromkeys([own_parent] + arrived))
                        slots.append({'id': f'TB01-{cid}-R{rep}-{branch}-{snap}-{holder}', 'stage': 'READ',
                                      'case': cid, 'repeat': rep, 'role': holder, 'branch': branch,
                                      'snapshot': snap, 'parents': parents, 'own_parent': own_parent,
                                      'vote_parents': list(arrived)})
    for s in slots:
        s['seed'] = seed(s['id'])
    assert len(slots) == 126
    return slots


def build_design(model):
    cases = materials()
    return {'protocol': PROTOCOL, 'date': '2026-10-13', 'cases': cases, 'allocation': allocation(cases),
            'schemas': SCHEMAS, 'prompts': PROMPTS, 'model': model,
            'budget': {'max_generations': 126, 'total_seconds': 2700, 'reserve_seconds': 90,
                       'max_raw_bytes': 16384, 'retries': 0},
            'repeats': list(REPEATS), 'stop_rule': 'One fixed pass regardless of outcomes; no additional samples.',
            'support_policy': 'Own summaries at every stage; candidate totals at VOTE and READ.',
            'retention': 'private_no_deletion_deadline'}


def case_for(design, slot):
    return next(c for c in design['cases'] if c['id'] == slot['case'])


def payload_for(design, slot, states):
    case = case_for(design, slot)
    role = slot['role']; stage = slot['stage']
    payload = {'holder': role, 'scene': case['scene'], 'schema': design['schemas'][stage],
               'experiences': deepcopy([r for r in case['experiences'] if stage != 'FORM' or r['owner'] == role]),
               'own_experience_summary': own_summary(case, role)}
    if stage == 'FORM':
        return payload
    table = candidate_table(case)
    ranked = sorted(table, key=lambda c: c['expected_total'], reverse=True)
    candidate = ranked[0 if slot['branch'] == 'HIGHER' else 1]
    proposal_id = 'P' + sha256(f"TB01|{case['id']}|{candidate['candidate_id']}".encode()).hexdigest()[:8]
    payload.update(resource_count=deepcopy(case['resource_count']), candidates=table,
                   proposal={'proposal_id': proposal_id, 'candidate_id': candidate['candidate_id']})
    own_parent = slot['parents'][0] if stage == 'VOTE' else slot['own_parent']
    payload['own_saved_note'] = deepcopy(states[own_parent]['own'])
    if stage == 'READ':
        payload['receipts'] = []
        slots = {s['id']: s for s in design['allocation']}
        for pid in slot['vote_parents']:
            payload['receipts'].append({'sender': slots[pid]['role'], **deepcopy(states[pid]['vote'])})
        # Deliberately no expected agreement, stage-name hint, or host commit status.
    return payload


def request_for(design, slot, states):
    payload = payload_for(design, slot, states)
    return {'id': slot['id'], 'seed': slot['seed'], 'messages': [
        {'role': 'system', 'content': design['prompts'][slot['stage']]},
        {'role': 'user', 'content': enc(payload).decode()}]}
