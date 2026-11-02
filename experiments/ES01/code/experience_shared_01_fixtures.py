"""Synthetic fixtures only. Never a fallback or replacement for a model response."""
from copy import deepcopy
import json
import experience_shared_01_design as sc


def correct_answer(payload, stage):
    rows = payload['experiences']; role = payload['holder']
    own = [x for x in rows if x['observer'] == role]
    local, opts = sc.expected_from_rows(rows)
    self_answer = {'subject': role, 'choice': local[role],
                   'evidence_refs': [x['episode_id'] for x in own]}
    if stage == 'SELF': return self_answer
    if stage == 'FORM':
        proposal = payload.get('first_proposal', {}).get('body', {}).get('allocation')
        allocation = proposal if proposal in opts else opts[0]
        return {'allocation': deepcopy(allocation), 'evidence_refs': [x['episode_id'] for x in rows]}
    joint = payload['joint_records']
    allocation = (joint[0]['body']['allocation'] if sc.agreed(joint) else {r: 'UNDECIDED' for r in sc.ROLES}) if joint else opts[0]
    return {'local': self_answer, 'team': {'allocation': deepcopy(allocation),
        'basis': ('SHARED_DECISION' if sc.agreed(joint) else 'UNRESOLVED') if joint else 'EXPERIENCE',
        'evidence_refs': [x['record_id'] for x in joint] if joint else [x['episode_id'] for x in rows]}}


def from_messages(messages):
    payload = json.loads(messages[1]['content'].split('資料JSON:\n', 1)[1])
    stage = 'USE' if 'joint_records' in payload else 'FORM' if 'self_judgments' in payload else 'SELF'
    return payload, stage


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
