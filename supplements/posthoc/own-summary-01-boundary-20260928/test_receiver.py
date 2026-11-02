"""Boundary fixtures only; no model and no additions to research sample size."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT/'scripts'))
import own_summary_01_design as sc
from receiver_candidate import receive

BASE = {'local': {'subject': 'A', 'choice': 'PAPER', 'evidence_refs': ['EA1', 'EA2']},
        'team': {'allocation': {'A': 'PAPER', 'B': 'DIGITAL'}, 'basis': 'SHARED_DECISION', 'evidence_refs': ['Q1', 'Q2']}}


class BoundaryTests(unittest.TestCase):
    def extra(self, value=None):
        a = deepcopy(BASE)
        a['local']['own_experience_summary'] = value
        return a

    def reject(self, raw, stage='USE', finish='EOS'):
        r = receive(raw, stage, finish)
        self.assertEqual(r['status'], 'REJECT')
        self.assertIsNone(r['candidate_bytes'])
        return r

    def test_valid_unchanged_bytes(self):
        raw = b'  '+sc.enc(BASE)+b'\n'
        self.assertEqual(receive(raw, 'USE')['candidate_bytes'], raw)

    def test_extra_is_quarantined_even_if_false_or_null(self):
        for value in [None, 4, 'untrusted text', {'observer': 'B', 'choice': 'DIGITAL', 'attempts_per_medium_total': -1}]:
            with self.subTest(value=value):
                raw = sc.enc(self.extra(value)); r = receive(raw, 'USE')
                self.assertEqual(r['status'], 'QUARANTINED')
                self.assertEqual(sc.strict_json.parse(r['candidate_bytes']), BASE)
                self.assertEqual(r['quarantine'][0]['value'], value)
                self.assertFalse(r['quarantine'][0]['for_downstream'])
                self.assertEqual(raw, sc.enc(self.extra(value)))

    def test_idempotence(self):
        a = receive(sc.enc(self.extra()), 'USE')
        b = receive(a['candidate_bytes'], 'USE')
        self.assertEqual(b['status'], 'UNCHANGED')
        self.assertEqual(a['candidate_bytes'], b['candidate_bytes'])

    def test_unknown_local_key(self):
        a = self.extra(); a['local']['explanation'] = 'text'
        self.reject(sc.enc(a))

    def test_unknown_root_key(self):
        a = self.extra(); a['explanation'] = 'text'
        self.reject(sc.enc(a))

    def test_wrong_location(self):
        a = deepcopy(BASE); a['own_experience_summary'] = {}
        self.reject(sc.enc(a))

    def test_missing_required(self):
        a = self.extra(); del a['local']['choice']
        self.reject(sc.enc(a))

    def test_wrong_type(self):
        a = self.extra(); a['local']['evidence_refs'] = 'EA1'
        self.reject(sc.enc(a))

    def test_invalid_enum(self):
        a = self.extra(); a['local']['choice'] = 'paper'
        self.reject(sc.enc(a))

    def test_no_arbitrary_stage_repair(self):
        for stage in ('PROPOSE', 'CONFIRM', 'UNKNOWN'):
            self.reject(sc.enc(self.extra()), stage)

    def test_duplicate_key(self):
        raw = sc.enc(self.extra()).replace(b'"choice":"PAPER"', b'"choice":"DIGITAL","choice":"PAPER"')
        self.reject(raw)

    def test_no_syntax_repair(self):
        self.reject(sc.enc(self.extra())[:-1])

    def test_no_trailing_prose(self):
        self.reject(sc.enc(self.extra())+b' explanation')

    def test_non_eos(self):
        self.reject(sc.enc(self.extra()), finish='LENGTH')

    def test_limit(self):
        self.reject(sc.enc(self.extra('x'*17000)))

    def test_invalid_utf8(self):
        self.reject(b'\xff')

    def test_nonstandard_number(self):
        self.reject(sc.enc(self.extra()).replace(b'null', b'NaN'))

    def test_only_old_exact_envelope(self):
        r = receive(b'```json\n'+sc.enc(self.extra())+b'\n```', 'USE')
        self.assertEqual(r['status'], 'QUARANTINED')
        self.assertEqual(r['envelope']['status'], 'UNWRAPPED')
        self.reject(b'```JSON\n'+sc.enc(self.extra())+b'\n```')

    def test_semantic_errors_not_fixed(self):
        a = self.extra({'recommended_answer': 'PAPER'})
        a['local'].update(subject='B', choice='DIGITAL', evidence_refs=['WRONG', 'WRONG'])
        r = receive(sc.enc(a), 'USE')
        projected = sc.strict_json.parse(r['candidate_bytes'])
        self.assertEqual(projected['local'], {'subject': 'B', 'choice': 'DIGITAL', 'evidence_refs': ['WRONG', 'WRONG']})
        self.assertFalse(r['semantic_repair'])

    def test_no_allocation_repair(self):
        a = self.extra(); a['team']['allocation']['B'] = 'PAPER'
        r = receive(sc.enc(a), 'USE')
        self.assertEqual(sc.strict_json.parse(r['candidate_bytes'])['team']['allocation'], {'A': 'PAPER', 'B': 'PAPER'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
