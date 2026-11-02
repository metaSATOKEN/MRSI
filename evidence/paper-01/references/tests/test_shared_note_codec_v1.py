"""Offline contract checks, including rejection and non-repair of semantic errors."""
from copy import deepcopy
import hashlib
import itertools
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import shared_note_codec_v1 as codec
import shared_update_design_v1 as old
import shared_carry_02_design_v1 as sc02


def sample():
    return {"shared_note": {
        "coverage": {
            "A": {"observer": "A", "paper": "ALL", "digital": "NOT_ALL", "origin_id": "OA"},
            "B": {"observer": "B", "paper": "ALL", "digital": "ALL", "origin_id": "OB"},
        },
        "channel": "PAPER", "channel_read_refs": ["OBS_A", "OBS_B"],
        "channel_origin_ids": ["OA", "OB"],
    }}


def array_form(value, order=("A", "B")):
    value = deepcopy(value)
    cov = value["shared_note"]["coverage"]
    value["shared_note"]["coverage"] = [cov[r] for r in order]
    return value


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


class CodecTest(unittest.TestCase):
    def assert_rejected(self, raw):
        result = codec.normalize(raw)
        self.assertEqual(result["status"], "REJECTED")
        self.assertIsNone(result["accepted_text"])
        self.assertIsNone(result["accepted_sha256"])
        self.assertTrue(result["errors"])
        self.assertEqual(result["raw_text"], raw)

    def test_native_bytes_preserved(self):
        raw = " \n" + json.dumps(sample(), indent=2) + "\n"
        result = codec.normalize(raw)
        self.assertEqual(result["status"], "NATIVE")
        self.assertEqual(result["accepted_text"], raw)
        self.assertEqual(result["accepted_sha256"], result["raw_sha256"])
        self.assertEqual(result["mapping"], [])
        self.assertIsNone(result["rule_id"])

    def test_explicit_observer_not_array_position(self):
        for order in (("A", "B"), ("B", "A")):
            with self.subTest(order=order):
                raw = encode(array_form(sample(), order))
                result = codec.normalize(raw)
                self.assertEqual(result["status"], "NORMALIZED")
                self.assertEqual(json.loads(result["accepted_text"]), sample())
                self.assertEqual(result["mapping"][0]["to"], f"/shared_note/coverage/{order[0]}")
                self.assertEqual(result["changed_paths"], ["/shared_note/coverage"])
                self.assertEqual(result["rule_id"], codec.RULE)

    def test_idempotent_and_deterministic(self):
        raw = encode(array_form(sample()))
        first = codec.normalize(raw)
        self.assertEqual(codec.normalize(raw), first)
        second = codec.normalize(first["accepted_text"])
        self.assertEqual(second["status"], "NATIVE")
        self.assertEqual(first["accepted_text"], second["accepted_text"])

    def test_audit_hashes(self):
        raw = encode(array_form(sample()))
        result = codec.normalize(raw)
        for text_key, hash_key in (("raw_text", "raw_sha256"), ("accepted_text", "accepted_sha256")):
            self.assertEqual(result[hash_key], hashlib.sha256(result[text_key].encode()).hexdigest())
        self.assertEqual(result["schema_sha256"], hashlib.sha256(encode(codec.schema()).encode()).hexdigest())

    def test_ambiguous_arrays_rejected(self):
        cov = array_form(sample())["shared_note"]["coverage"]
        variants = [[], cov[:1], cov + [cov[0]], [cov[0], cov[0]], [None, cov[1]],
                    [dict(cov[0], observer="UNKNOWN"), cov[1]],
                    [dict(cov[0], observer="a"), cov[1]],
                    [dict(cov[0], observer=1), cov[1]],
                    [{k: v for k, v in cov[0].items() if k != "observer"}, cov[1]]]
        for variant in variants:
            with self.subTest(variant=variant):
                value = sample(); value["shared_note"]["coverage"] = variant
                self.assert_rejected(encode(value))

    def test_missing_and_extra_fields_rejected(self):
        paths = [(), ("shared_note",), ("shared_note", "coverage", "A")]
        for path in paths:
            for operation in ("missing", "extra"):
                with self.subTest(path=path, operation=operation):
                    value = sample(); node = value
                    for key in path: node = node[key]
                    if operation == "missing": del node[next(iter(node))]
                    else: node["unexpected"] = "ALL"
                    self.assert_rejected(encode(value))
        value = array_form(sample()); del value["shared_note"]["coverage"][0]["paper"]
        self.assert_rejected(encode(value))

    def test_invalid_json_never_repaired(self):
        valid = encode(sample())
        cases = [valid[:-1], "```json\n" + valid + "\n```", valid + valid,
                 valid.replace('"PAPER"', 'NaN'), valid.replace('"PAPER"', 'Infinity'),
                 valid.replace('"channel":"PAPER"', '"channel":"PAPER","channel":"DIGITAL"'),
                 valid.replace('"origin_id":"OA"', '"origin_id":"OA","origin_id":"OB"'),
                 valid.replace('"origin_id":"OA"', '"origin_id":"OA","origin_\\u0069d":"OB"'),
                 "null", "[]", "42", '["x"]', '"shared_note"',
                 '[' * 1800 + '0' + ']' * 1800]
        for raw in cases:
            with self.subTest(raw=raw[:90]): self.assert_rejected(raw)

    def test_invalid_values_and_types_rejected(self):
        cases = [None, True, 1, [], {}, "SOME", "", "all"]
        for bad in cases:
            value = array_form(sample()); value["shared_note"]["coverage"][0]["paper"] = bad
            with self.subTest(bad=bad): self.assert_rejected(encode(value))
        for identifier in ("oa", "OA\n", "A" * 33, "A B", "犬", "\ud800"):
            value = sample(); value["shared_note"]["coverage"]["A"]["origin_id"] = identifier
            self.assert_rejected(json.dumps(value))

    def test_byte_limit_and_unicode(self):
        raw = encode(sample())
        self.assertEqual(codec.normalize(raw + ' ' * (4096 - len(raw.encode())))["status"], "NATIVE")
        self.assert_rejected(raw + ' ' * (4097 - len(raw.encode())))
        self.assert_rejected("犬" * 1366)
        self.assert_rejected("\ud800")

    def test_semantically_wrong_values_survive(self):
        truth = sample()["shared_note"]
        for changes in ({"channel": "DIGITAL"}, {"channel_read_refs": ["OBS_A", "OBS_A"]},
                        {"channel_origin_ids": ["OB", "OA", "MISSING"]}):
            value = sample(); value["shared_note"].update(changes)
            result = codec.normalize(encode(array_form(value)))
            self.assertEqual(result["status"], "NORMALIZED")
            accepted = old.parse(result["accepted_text"], "DRAFT")["shared_note"]
            self.assertEqual(accepted, value["shared_note"])
            self.assertFalse(sc02.equivalent(accepted, truth))

    def test_canonical_misattribution_is_not_rekeyed(self):
        value = sample(); value["shared_note"]["coverage"]["A"]["observer"] = "B"
        raw = encode(value); result = codec.normalize(raw)
        self.assertEqual(result["status"], "NATIVE")
        self.assertEqual(result["accepted_text"], raw)
        self.assertFalse(sc02.equivalent(value["shared_note"], sample()["shared_note"]))

    def test_unknown_and_reference_order_preserved(self):
        value = sample(); note = value["shared_note"]
        note["coverage"]["A"]["paper"] = "UNKNOWN"
        note["channel"] = "UNKNOWN"
        note["channel_read_refs"].reverse(); note["channel_origin_ids"].reverse()
        result = codec.normalize(encode(array_form(value)))
        self.assertEqual(result["status"], "NORMALIZED")
        self.assertEqual(json.loads(result["accepted_text"]), value)

    def test_schema_and_prompt_share_contract(self):
        detached = codec.schema()
        detached["properties"]["shared_note"]["required"].clear()
        self.assertTrue(codec.schema()["properties"]["shared_note"]["required"])
        prompt = codec.prompt_contract()
        self.assertEqual(json.loads(prompt.split("\n", 1)[1]), codec.schema())
        self.assertIn("固定キーA/B", prompt)
        self.assertIn("coverageに配列を使いません", prompt)

    def test_legacy_contract_agrees_on_enum_product(self):
        # Includes legal UNKNOWN attribution and invalid labels; no truth oracle in codec.
        for observer, paper, digital, channel in itertools.product(
                ("A", "B", "UNKNOWN", "BAD"), ("ALL", "NOT_ALL", "UNKNOWN", "BAD"),
                ("ALL", "NOT_ALL", "UNKNOWN", "BAD"), ("PAPER", "DIGITAL", "UNKNOWN", "BAD")):
            value = sample(); note = value["shared_note"]
            note["coverage"]["A"].update(observer=observer, paper=paper, digital=digital)
            note["channel"] = channel; raw = encode(value)
            self.assertEqual(codec.normalize(raw)["status"] == "NATIVE",
                             old.parse(raw, "DRAFT")["shared_note"] is not None)

    def test_reference_limits_and_unknown_observer(self):
        for length in (0, 8, 9):
            value = sample(); value["shared_note"]["channel_read_refs"] = ["X"] * length
            value["shared_note"]["coverage"]["A"]["observer"] = "UNKNOWN"
            raw = encode(value)
            self.assertEqual(codec.normalize(raw)["status"] == "NATIVE", length <= 8)
            self.assertEqual(codec.normalize(raw)["status"] == "NATIVE",
                             old.parse(raw, "DRAFT")["shared_note"] is not None)

    def test_other_stage_top_structure_rejected(self):
        value = sample(); value["private_note"] = {}
        self.assert_rejected(encode(value))
        self.assert_rejected(encode({"private_note": {}}))

    def test_known_sc02_cases_are_calibration_only(self):
        root = ROOT / "study2/runs/shared-carry-02-prepared-20260918/generations"
        paths = sorted(root.glob("SC02-*-DRAFT-*-raw.txt"))
        self.assertEqual(len(paths), 4)
        for path in paths:
            raw = path.read_text(); result = codec.normalize(raw)
            self.assertIsNone(old.parse(raw, "DRAFT")["shared_note"])
            self.assertEqual(result["status"], "NORMALIZED")
            self.assertIsNotNone(old.parse(result["accepted_text"], "DRAFT")["shared_note"])
            before = json.loads(raw)["shared_note"]; after = json.loads(result["accepted_text"])["shared_note"]
            self.assertEqual({v["observer"]: v for v in before.pop("coverage")}, after.pop("coverage"))
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
