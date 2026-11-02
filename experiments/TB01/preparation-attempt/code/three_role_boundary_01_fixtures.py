"""Synthetic TB01 fixtures only. They never supply missing experimental answers."""
from copy import deepcopy
from fractions import Fraction
import json


def ideal(payload, stage):
    role = payload['holder']
    rows = [r for r in payload['experiences'] if r['owner'] == role]
    rates = {m: Fraction(sum(r['observed'][m]['success'] for r in rows), sum(r['observed'][m]['trials'] for r in rows))
             for m in ('PAPER', 'DIGITAL')}
    answer = {'own': {'holder': role, 'recommendation': max(rates, key=rates.get), 'evidence_ids': [r['id'] for r in rows]}}
    if stage == 'VOTE':
        best = max(payload['candidates'], key=lambda c: c['expected_total'])['candidate_id']
        answer['vote'] = {'proposal_id': payload['proposal']['proposal_id'],
                          'decision': 'ACCEPT' if best == payload['proposal']['candidate_id'] else 'HOLD'}
    if stage == 'READ':
        states = {r: 'MISSING' for r in ('A', 'B', 'C')}
        for receipt in payload['receipts']:
            states[receipt['sender']] = receipt['decision'] if receipt['proposal_id'] == payload['proposal']['proposal_id'] else 'WRONG_PROPOSAL'
        agreed = set(states.values()) == {'ACCEPT'}
        candidate = next(c for c in payload['candidates'] if c['candidate_id'] == payload['proposal']['candidate_id'])
        answer.update(approval_state=states, agreement='AGREED' if agreed else 'PENDING',
                      joint_action=candidate['assignment'][role] if agreed else 'HOLD')
    return answer


class SyntheticBackend:
    """Works without importing torch; records conspicuous synthetic markers."""
    def __init__(self, mutate=None):
        self.mutate = mutate; self.calls = 0

    def prepare(self, messages):
        return {'rendered_prompt': '\n'.join(m['content'] for m in messages) + '<|im_start|>assistant\n<think>\n\n</think>\n\n',
                'input_ids': [1, 2, 3]}

    def generate(self, prepared, seed, deadline):
        prompt = prepared['rendered_prompt']
        # Synthetic only: user JSON starts immediately after the system's last newline.
        start = prompt.index('{"')
        payload, _ = json.JSONDecoder().raw_decode(prompt[start:])
        properties = set(payload['schema']['properties'])
        stage = 'READ' if 'approval_state' in properties else 'VOTE' if 'vote' in properties else 'FORM'
        answer = ideal(payload, stage)
        self.calls += 1
        if self.mutate:
            answer = self.mutate(deepcopy(answer), payload, stage, self.calls)
        raw = answer if type(answer) is str else json.dumps(answer, ensure_ascii=False, separators=(',', ':'))
        return {'answer_text': raw, 'decoded_with_special_tokens': raw + '<|im_end|>', 'output_token_ids': [10, 248046],
                'finish_reason': 'EOS', 'generation_seconds': 0.0, 'peak_vram_bytes': 0, 'seed': seed,
                'synthetic_fixture': True}
