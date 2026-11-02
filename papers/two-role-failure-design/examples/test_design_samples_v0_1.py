"""Illustrative-input checks only; these are not LLM experimental results."""
import unittest
from copy import deepcopy
from fractions import Fraction
from itertools import permutations

from design_samples_v0_1 import select_observation, record_assignment, commit_agreement


def row(owner, version, origin, paper="ALL", digital="NOT_ALL"):
    return {"observer": owner, "revision": version, "origin_id": origin,
            "paper": paper, "digital": digital}


def fixture(author="A", version=1):
    scores = {"A": {"PAPER": 17, "DIGITAL": 27},
              "B": {"PAPER": 18, "DIGITAL": 20}}
    proposal = {"id": "p1", "version": version, "evidence_version": "exp-7",
                "author": author, "allocation": {"A": "DIGITAL", "B": "PAPER"}}
    reply = {"author": "B" if author == "A" else "A", "action": "ACCEPT",
             "proposal_id": "p1", "proposal_version": version,
             "evidence_version": "exp-7", "allocation": deepcopy(proposal["allocation"])}
    return proposal, reply, scores


class Illustrations(unittest.TestCase):
    def test_owner_and_order(self):
        rows = [row("A", 2, "OA2"), row("B", 99, "OB99"), row("A", 3, "OA3")]
        for order in permutations(rows):
            with self.subTest(order=[r["origin_id"] for r in order]):
                self.assertEqual(select_observation(order, "A")["row"], rows[2])

    def test_legitimate_newer_row(self):
        rows = [row("A", 3, "OA3"), row("A", 4, "OA4", "NOT_ALL", "ALL")]
        self.assertEqual(select_observation(rows, "A")["row"], rows[1])

    def test_missing_owner(self):
        self.assertEqual(select_observation([row("B", 99, "OB99")], "A")["reason"], "MISSING_OWNER")

    def test_conflicting_same_version(self):
        rows = [row("A", 3, "OA3"), row("A", 3, "OA3", "NOT_ALL", "ALL")]
        self.assertEqual(select_observation(rows, "A")["reason"], "SAME_VERSION_CONFLICT")

    def test_conflicting_provenance(self):
        rows = [row("A", 3, "OA3"), row("A", 3, "DIFFERENT")]
        self.assertEqual(select_observation(rows, "A")["status"], "HOLD")

    def test_older_conflict_is_not_silently_discarded(self):
        rows = [row("A", 2, "OA2"), row("A", 2, "OTHER"), row("A", 3, "OA3")]
        self.assertEqual(select_observation(rows, "A")["status"], "HOLD")

    def test_identical_duplicates_and_copy(self):
        source = row("A", 3, "OA3")
        result = select_observation([source, deepcopy(source)], "A")
        self.assertEqual(result["row"], source)
        result["row"]["origin_id"] = "CHANGED"
        self.assertEqual(source["origin_id"], "OA3")

    def test_best_proposal_commits(self):
        p, r, scores = fixture()
        self.assertEqual(commit_agreement(p, r, scores, "exp-7")["status"], "COMMITTED")

    def test_lower_total_is_held(self):
        p, r, scores = fixture()
        p["allocation"] = r["allocation"] = {"A": "PAPER", "B": "DIGITAL"}
        self.assertEqual(commit_agreement(p, r, scores, "exp-7")["reason"], "LOWER_TOTAL")

    def test_one_device_cannot_be_assigned_twice(self):
        p, r, scores = fixture()
        p["allocation"] = r["allocation"] = {"A": "DIGITAL", "B": "DIGITAL"}
        self.assertEqual(commit_agreement(p, r, scores, "exp-7")["reason"], "RESOURCE_CONFLICT")

    def test_target_and_evidence_binding(self):
        for field, value in [("proposal_id", "other"), ("proposal_version", 0), ("evidence_version", "exp-6")]:
            with self.subTest(field=field):
                p, r, scores = fixture(); r[field] = value
                self.assertEqual(commit_agreement(p, r, scores, "exp-7")["reason"], "STALE_OR_DIFFERENT_TARGET")
        p, r, scores = fixture(); p["evidence_version"] = "exp-6"
        self.assertEqual(commit_agreement(p, r, scores, "exp-7")["reason"], "STALE_OR_DIFFERENT_TARGET")

    def test_counterproposal_and_hold_are_not_acceptance(self):
        for action in ("COUNTER", "HOLD"):
            with self.subTest(action=action):
                p, r, scores = fixture(); r["action"] = action
                self.assertEqual(commit_agreement(p, r, scores, "exp-7")["status"], "HOLD")

    def test_same_author_is_not_peer_acceptance(self):
        p, r, scores = fixture(); r["author"] = p["author"]
        self.assertEqual(commit_agreement(p, r, scores, "exp-7")["status"], "HOLD")

    def test_accepted_allocation_must_match(self):
        p, r, scores = fixture(); r["allocation"] = {"A": "PAPER", "B": "DIGITAL"}
        self.assertEqual(commit_agreement(p, r, scores, "exp-7")["status"], "HOLD")

    def test_either_proposer_uses_the_same_check(self):
        # Emulates the last proposal/acceptance pair, not the original LLM routes.
        for author in ("A", "B"):
            with self.subTest(author=author):
                p, r, scores = fixture(author, version=2)
                self.assertEqual(commit_agreement(p, r, scores, "exp-7")["status"], "COMMITTED")
                p["allocation"] = r["allocation"] = {"A": "PAPER", "B": "DIGITAL"}
                self.assertEqual(commit_agreement(p, r, scores, "exp-7")["reason"], "LOWER_TOTAL")

    def test_tied_maxima_both_pass(self):
        p, r, scores = fixture()
        scores = {"A": {"PAPER": Fraction(1, 3), "DIGITAL": Fraction(2, 3)},
                  "B": {"PAPER": Fraction(1, 3), "DIGITAL": Fraction(2, 3)}}
        for allocation in ({"A": "PAPER", "B": "DIGITAL"}, {"A": "DIGITAL", "B": "PAPER"}):
            p["allocation"] = r["allocation"] = allocation
            self.assertEqual(commit_agreement(p, r, scores, "exp-7")["status"], "COMMITTED")

    def test_joint_assignment_does_not_overwrite_own_judgment(self):
        p, r, scores = fixture()
        state = {"role": "B", "own_judgment": {"choice": "DIGITAL", "refs": ["b1", "b2"]},
                 "joint_assignment": None}
        before = deepcopy(state)
        agreement = commit_agreement(p, r, scores, "exp-7")
        result = record_assignment(state, agreement)["state"]
        self.assertEqual(state, before)
        self.assertEqual(result["own_judgment"], before["own_judgment"])
        self.assertEqual(result["joint_assignment"], {"medium": "PAPER", "proposal_id": "p1",
                                                     "proposal_version": 1, "evidence_version": "exp-7"})
        result["own_judgment"]["refs"].append("changed")
        self.assertEqual(state, before)
        agreement["proposal"]["allocation"]["B"] = "DIGITAL"
        self.assertEqual(result["joint_assignment"]["medium"], "PAPER")

    def test_hold_does_not_write_an_assignment(self):
        state = {"role": "B", "own_judgment": {"choice": "DIGITAL"}, "joint_assignment": {"medium": "PAPER"}}
        before = deepcopy(state)
        result = record_assignment(state, {"status": "HOLD"})
        self.assertEqual(state, before)
        self.assertEqual(result, {"status": "HOLD", "reason": "NO_COMMITTED_AGREEMENT"})

    def test_committing_copies_the_proposal(self):
        p, r, scores = fixture(); before = deepcopy(p)
        committed = commit_agreement(p, r, scores, "exp-7")
        committed["proposal"]["allocation"]["A"] = "PAPER"
        self.assertEqual(p, before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
