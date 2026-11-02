"""多者系の設計例：標準ライブラリのみ。LLM呼出し・ファイル書込みなし。

select_observation は旧例を再利用する。他は参照構成の設計例であり、
元の二者・三者LLM実験へ接続したコードではない。
入力の型・出所・ID/版と内容の対応は管理側で事前に確認する。
"""
import json
import unittest
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from itertools import permutations


def select_observation(rows, owner):
    candidates = [r for r in rows if r["observer"] == owner]
    if not candidates:
        return {"status": "HOLD", "reason": "MISSING_OWNER"}
    by_version = {}
    for row in candidates:
        version = row["revision"]
        if version in by_version and by_version[version] != row:
            return {"status": "HOLD", "reason": "SAME_VERSION_CONFLICT"}
        by_version[version] = row
    latest = by_version[max(by_version)]
    return {"status": "READY", "row": deepcopy(latest)}


def record_assignment(state, decision):
    if decision["execution"] != "AUTHORIZED":
        return {"status": "DEFERRED", "reason": "NO_EXECUTION_PERMISSION"}
    proposal = decision["proposal"]
    updated = deepcopy(state)
    updated["joint_assignment"] = {
        "medium": proposal["allocation"][state["role"]],
        "proposal_id": proposal["id"],
        "proposal_version": proposal["version"],
        "evidence_version": proposal["evidence_version"],
    }
    return {"status": "READY", "state": updated}


def assess_proposal(proposal, scores, candidates, capacity, evidence_version):
    """固定された候補集合内で評価する。新しい候補は探索しない。"""
    def feasible(allocation):
        return (set(allocation) == set(scores)
                and Counter(allocation.values()) == Counter(capacity))

    def total(allocation):
        return sum(scores[r][allocation[r]] for r in scores)

    if proposal["evidence_version"] != evidence_version:
        return {"eligible": False, "reason": "STALE_EVIDENCE"}
    if not scores or not candidates or not all(feasible(a) for a in candidates):
        return {"eligible": False, "reason": "INVALID_CANDIDATE_CATALOG"}
    allocation = proposal["allocation"]
    if not feasible(allocation):
        return {"eligible": False, "reason": "RESOURCE_CONFLICT"}
    if allocation not in candidates:
        return {"eligible": False, "reason": "OUTSIDE_CANDIDATES"}
    value, best = total(allocation), max(map(total, candidates))
    return {"eligible": value == best, "total": value, "best": best,
            "reason": "MEETS_CRITERION" if value == best else "LOWER_TOTAL"}


def project_votes(proposal, receipts, participants):
    """同じ提案への実票から全員承認を判定する。未受領はMISSING。"""
    if not participants or len(set(participants)) != len(participants):
        raise ValueError("Participants must be nonempty and unique")
    key = (proposal["id"], proposal["version"], proposal["evidence_version"])
    states = {r: "MISSING" for r in participants}
    issues, seen = [], set()
    for vote in receipts:
        actor = vote["author"]
        target = (vote["proposal_id"], vote["proposal_version"], vote["evidence_version"])
        if actor not in states or target != key:
            issues.append("UNBOUND_RECEIPT")
            continue
        if actor in seen:
            states[actor] = "UNRESOLVED"
            issues.append("DUPLICATE_RECEIPT")
            continue
        seen.add(actor)
        if vote["action"] not in ("ACCEPT", "HOLD"):
            states[actor] = "UNRESOLVED"
            issues.append("UNSUPPORTED_ACTION")
        else:
            states[actor] = vote["action"]
    agreed = not issues and all(v == "ACCEPT" for v in states.values())
    return {"states": states, "agreement": "AGREED" if agreed else "PENDING",
            "issues": issues, "receipts": deepcopy(receipts)}


def decide(proposal, receipts, scores, candidates, capacity, evidence_version):
    assessment = assess_proposal(proposal, scores, candidates, capacity, evidence_version)
    approvals = project_votes(proposal, receipts, tuple(scores))
    authorized = assessment["eligible"] and approvals["agreement"] == "AGREED"
    return {"proposal": deepcopy(proposal), "assessment": assessment,
            "approvals": approvals,
            "execution": "AUTHORIZED" if authorized else "DEFERRED"}


def fixture(size=3, lower=False):
    """既存事例の数値を使う合成入力。原実験のJSONとは別形式。"""
    if size == 2:
        scores = {"A": {"PAPER": 17, "DIGITAL": 27},
                  "B": {"PAPER": 18, "DIGITAL": 20}}
        candidates = [{"A": "DIGITAL", "B": "PAPER"},
                      {"A": "PAPER", "B": "DIGITAL"}]
        capacity = {"PAPER": 1, "DIGITAL": 1}
    elif size == 3:
        scores = {"A": {"PAPER": 24, "DIGITAL": 29},
                  "B": {"PAPER": 24, "DIGITAL": 35},
                  "C": {"PAPER": 32, "DIGITAL": 16}}
        candidates = [{"A": "PAPER", "B": "DIGITAL", "C": "PAPER"},
                      {"A": "DIGITAL", "B": "PAPER", "C": "PAPER"}]
        capacity = {"PAPER": 2, "DIGITAL": 1}
    else:
        raise ValueError("This illustration has fixtures for two or three roles")
    proposal = {"id": "p-low" if lower else "p-high", "version": 1,
                "evidence_version": "exp-7", "author": "A",
                "allocation": deepcopy(candidates[int(lower)])}
    receipts = [{"author": r, "action": "ACCEPT", "proposal_id": proposal["id"],
                 "proposal_version": 1, "evidence_version": "exp-7"} for r in scores]
    return proposal, receipts, scores, candidates, capacity, "exp-7"


def observation(owner, revision, origin):
    return {"observer": owner, "revision": revision, "origin_id": origin,
            "paper": "ALL", "digital": "NOT_ALL"}


class DesignTests(unittest.TestCase):
    def test_owner_then_version_and_copy(self):
        rows = [observation("A", 2, "a2"), observation("B", 99, "b99"),
                observation("A", 3, "a3")]
        for ordered in permutations(rows):
            result = select_observation(ordered, "A")
            self.assertEqual(result["row"], rows[2])
            result["row"]["origin_id"] = "changed"
            self.assertEqual(rows[2]["origin_id"], "a3")

    def test_observation_missing_conflict_and_newer(self):
        self.assertEqual(select_observation([], "A")["reason"], "MISSING_OWNER")
        rows = [observation("A", 3, "a3"), observation("A", 3, "other")]
        self.assertEqual(select_observation(rows, "A")["reason"], "SAME_VERSION_CONFLICT")
        rows = [observation("A", 3, "a3"), observation("A", 4, "a4")]
        self.assertEqual(select_observation(rows, "A")["row"]["revision"], 4)

    def test_normal_two_and_three_role_progress(self):
        for n, best in [(2, 45), (3, 91)]:
            result = decide(*fixture(n))
            self.assertEqual(result["execution"], "AUTHORIZED")
            self.assertEqual(result["assessment"]["total"], best)

    def test_missing_is_not_explicit_hold(self):
        for n in (2, 3):
            args = fixture(n)
            args[1].pop(0)
            missing = decide(*args)
            args = fixture(n)
            args[1][0]["action"] = "HOLD"
            held = decide(*args)
            self.assertEqual(missing["approvals"]["states"]["A"], "MISSING")
            self.assertEqual(held["approvals"]["states"]["A"], "HOLD")
            for r in (missing, held):
                self.assertEqual(r["approvals"]["agreement"], "PENDING")
                self.assertEqual(r["execution"], "DEFERRED")

    def test_proposing_does_not_supply_a_vote(self):
        proposal, _, scores, *_ = fixture()
        r = project_votes(proposal, [], tuple(scores))
        self.assertEqual(set(r["states"].values()), {"MISSING"})
        self.assertEqual(r["agreement"], "PENDING")

    def test_lower_total_keeps_unanimous_approval(self):
        for n, lower in [(2, 37), (3, 85)]:
            args = fixture(n, lower=True)
            r = decide(*args)
            self.assertEqual(r["assessment"]["total"], lower)
            self.assertEqual(r["assessment"]["reason"], "LOWER_TOTAL")
            self.assertEqual(r["approvals"]["agreement"], "AGREED")
            self.assertEqual(r["execution"], "DEFERRED")
            self.assertEqual(r["approvals"]["receipts"], args[1])
            self.assertEqual(r["proposal"], args[0])

    def test_resource_conflict_keeps_votes(self):
        args = fixture(2)
        args[0]["allocation"]["B"] = "DIGITAL"
        r = decide(*args)
        self.assertEqual(r["assessment"]["reason"], "RESOURCE_CONFLICT")
        self.assertEqual(r["approvals"]["agreement"], "AGREED")
        self.assertEqual(r["execution"], "DEFERRED")

    def test_different_proposal_or_version_cannot_authorize(self):
        for key, value in [("proposal_id", "other"), ("proposal_version", 0),
                           ("evidence_version", "exp-old")]:
            args = fixture()
            args[1][0][key] = value
            r = decide(*args)
            self.assertEqual(r["execution"], "DEFERRED")
            self.assertEqual(r["approvals"]["states"]["A"], "MISSING")
            self.assertTrue(r["approvals"]["issues"])

    def test_stale_snapshot_keeps_actual_agreement(self):
        args = list(fixture())
        args[-1] = "exp-8"
        r = decide(*args)
        self.assertEqual(r["approvals"]["agreement"], "AGREED")
        self.assertEqual(r["assessment"]["reason"], "STALE_EVIDENCE")
        self.assertEqual(r["execution"], "DEFERRED")

    def test_duplicate_votes_not_counted_as_another_person(self):
        for action in ("ACCEPT", "HOLD"):
            args = fixture()
            duplicate = deepcopy(args[1][0])
            duplicate["action"] = action
            args[1].append(duplicate)
            r = decide(*args)
            self.assertEqual(r["approvals"]["states"]["A"], "UNRESOLVED")
            self.assertEqual(len(r["approvals"]["receipts"]), 4)
            self.assertEqual(r["execution"], "DEFERRED")

    def test_unknown_actor_and_unsupported_action(self):
        for key, value in [("author", "OUTSIDER"), ("action", "COUNTER")]:
            args = fixture()
            args[1][0][key] = value
            r = decide(*args)
            self.assertEqual(r["execution"], "DEFERRED")
            self.assertTrue(r["approvals"]["issues"])

    def test_empty_or_duplicate_participant_set(self):
        p, receipts, *_ = fixture()
        for roles in [(), ("A", "A")]:
            with self.assertRaises(ValueError):
                project_votes(p, receipts, roles)

    def test_receipt_order_does_not_change_states(self):
        args = list(fixture())
        for ordered in permutations(args[1]):
            args[1] = list(ordered)
            r = decide(*args)
            self.assertEqual(r["execution"], "AUTHORIZED")
            self.assertEqual(set(r["approvals"]["states"].values()), {"ACCEPT"})

    def test_tie_and_exact_fraction(self):
        for lower in (False, True):
            args = fixture(2, lower)
            args[2]["A"]["PAPER"] = Fraction(20, 3)
            args[2]["A"]["DIGITAL"] = Fraction(20, 3)
            args[2]["B"]["PAPER"] = Fraction(10, 3)
            args[2]["B"]["DIGITAL"] = Fraction(10, 3)
            r = decide(*args)
            self.assertEqual(r["assessment"]["total"], 10)
            self.assertEqual(r["execution"], "AUTHORIZED")

    def test_candidate_scope_and_catalog(self):
        args = fixture()
        args[0]["allocation"] = {"A": "PAPER", "B": "PAPER", "C": "DIGITAL"}
        self.assertEqual(decide(*args)["assessment"]["reason"], "OUTSIDE_CANDIDATES")
        args[3].clear()
        self.assertEqual(decide(*args)["assessment"]["reason"], "INVALID_CANDIDATE_CATALOG")

    def test_assignment_preserves_own_judgment(self):
        for n, role in [(2, "B"), (3, "A")]:
            state = {"role": role, "own_judgment": {"choice": "DIGITAL", "refs": ["e1"]}}
            before = deepcopy(state)
            out = record_assignment(state, decide(*fixture(n)))
            self.assertEqual(out["state"]["joint_assignment"]["medium"], "PAPER")
            self.assertEqual(out["state"]["own_judgment"], before["own_judgment"])
            self.assertEqual(state, before)

    def test_no_assignment_without_permission(self):
        args = fixture()
        args[1].pop()
        self.assertEqual(record_assignment({"role": "A"}, decide(*args))["status"], "DEFERRED")

    def test_no_input_mutation_or_output_alias(self):
        args = fixture()
        before = deepcopy(args)
        out = decide(*args)
        self.assertEqual(args, before)
        out["proposal"]["allocation"]["A"] = "CHANGED"
        out["approvals"]["receipts"][0]["action"] = "CHANGED"
        self.assertEqual(args, before)


def demonstrate():
    examples = {}
    for label in ("MISSING", "HOLD", "ACCEPT"):
        args = fixture()
        if label == "MISSING":
            args[1].pop(0)
        elif label == "HOLD":
            args[1][0]["action"] = "HOLD"
        result = decide(*args)
        examples[label] = {"states": result["approvals"]["states"],
                           "agreement": result["approvals"]["agreement"],
                           "execution": result["execution"]}
    examples["LOWER_WITH_ALL_ACCEPT"] = decide(*fixture(2, lower=True))
    state = {"role": "A", "own_judgment": {"choice": "DIGITAL", "refs": ["a1", "a2"]}}
    examples["OWN_AND_ASSIGNMENT"] = record_assignment(state, decide(*fixture()))
    examples["LATEST_ROW"] = select_observation(
        [observation("A", 2, "a2"), observation("B", 99, "b99"), observation("A", 3, "a3")], "A")
    print(json.dumps(examples, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    demonstrate()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DesignTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
