"""Synthetic fixtures only. Never a fallback or replacement for a model response."""
from copy import deepcopy
import json
import agreement_confirm_01_design as sc


def correct_answer(payload,stage):
    rows=payload['experiences'];role=payload['holder'];local,opts=sc.expected_from_rows(rows)
    if stage=='CONFIRM':
        peer=payload['peer_proposal'];alloc=peer['body']['allocation'];valid=alloc in opts
        return {'action':'ACCEPT' if valid else 'COUNTER','reply_to':peer['record_id'],
                'allocation':deepcopy(alloc if valid else opts[0]),'evidence_refs':[r['episode_id'] for r in rows]}
    peer,confirmation=sc.split_records(payload['joint_records']);k=sc.agreement(peer,confirmation)
    return {'local':{'subject':role,'choice':local[role],'evidence_refs':[r['episode_id'] for r in rows if r['observer']==role]},
            'team':{'allocation':deepcopy(peer['body']['allocation']) if k else {r:'UNDECIDED' for r in sc.ROLES},
                    'basis':'SHARED_DECISION' if k else 'UNRESOLVED','evidence_refs':[r['record_id'] for r in payload['joint_records']]}}


def from_messages(messages):
    payload=json.loads(messages[1]['content'].split('資料JSON:\n',1)[1])
    return payload,'USE' if 'joint_records' in payload else 'CONFIRM'


class SyntheticBackend:
    """Offline tests only; no model/tokenizer/network imports or fallback path."""
    def __init__(self, transform=None):
        self.calls = 0; self.transform = transform; self.requests = []

    def prepare(self, messages):
        return {'rendered_prompt': 'SYNTHETIC_NOT_A_MODEL_TEMPLATE\n' + sc.displayed(messages),
                'input_ids': [1], 'synthetic_messages': deepcopy(messages)}

    def generate(self, prepared, seed, deadline):
        self.calls += 1
        payload, stage = from_messages(prepared['synthetic_messages'])
        self.requests.append({'payload': payload, 'stage': stage, 'seed': seed})
        answer = correct_answer(payload, stage)
        raw = sc.enc(answer).decode()
        if self.transform:
            raw = self.transform(self.calls, payload, stage, answer)
        return {'output_token_ids': [123, 248046], 'decoded_with_special_tokens': raw + '<|im_end|>',
                'answer_text': raw, 'finish_reason': 'EOS', 'generation_seconds': 0.0,
                'peak_vram_bytes': 0, 'seed': seed, 'synthetic_fixture': True}
