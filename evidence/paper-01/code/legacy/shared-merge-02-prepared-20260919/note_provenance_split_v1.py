"""NOTE-PROVENANCE-SPLIT-01: offline, pure functions; no model/transport imports.

This is a proposed snapshot-copy contract, not a general provenance resolver.
Receipt membership is neither attention evidence nor a correctness score.
"""
from copy import deepcopy
from hashlib import sha256
import json
import re

ID = {"type": "string", "pattern": "^[A-Z][A-Z0-9_]{0,31}$"}
REVISION = {"enum": [1, 2, "UNKNOWN"]}
MAX_OUTPUT_BYTES = 4096


def obj(properties):
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}


def enum(*values):
    return {"enum": list(values)}


def schema():
    coverage = obj({"observer": enum("A", "B", "UNKNOWN"),
                    "paper": enum("ALL", "NOT_ALL", "UNKNOWN"),
                    "digital": enum("ALL", "NOT_ALL", "UNKNOWN"), "origin_id": ID})
    private = obj({"customer": obj({"subject": enum("A", "B", "UNKNOWN"),
                                    "animal": enum("DOG", "CAT", "UNKNOWN"), "origin_id": ID}),
                   "coverage": coverage})
    shared = obj({"coverage": obj({"A": coverage, "B": coverage}),
                  "channel": enum("PAPER", "DIGITAL", "UNKNOWN"),
                  "channel_origin_ids": {"type": "array", "items": ID, "maxItems": 8}})
    return deepcopy(obj({"memory": obj({"private_note": private, "shared_note": shared,
                                        "shared_revision": REVISION}),
                         "read_receipt": obj({"shared_record_refs": {
                             "type": "array", "items": ID, "maxItems": 1, "uniqueItems": True}})}))


def json_bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def digest(value):
    return sha256(json_bytes(value)).hexdigest()


def parse(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("DUPLICATE_KEY:" + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError("NON_JSON_NUMBER:" + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def shape(value, rule, path="$"):
    """Finite schema subset used here; no coercion (including bool/int or float/int)."""
    if "enum" in rule and not any(type(value) is type(x) and value == x for x in rule["enum"]):
        return [path + ":ENUM_OR_TYPE"]
    kind = rule.get("type")
    want = {"object": dict, "array": list, "string": str}.get(kind)
    if want and type(value) is not want:
        return [path + ":TYPE"]
    errors = []
    if kind == "object":
        if set(value) != set(rule["properties"]):
            errors.append(path + ":KEY_SET")
        for key in value.keys() & rule["properties"].keys():
            errors += shape(value[key], rule["properties"][key], path + "." + key)
    elif kind == "array":
        if len(value) > rule["maxItems"]:
            errors.append(path + ":COUNT")
        if rule.get("uniqueItems") and len({json_bytes(x) for x in value}) != len(value):
            errors.append(path + ":DUPLICATE_REF")
        for i, x in enumerate(value):
            errors += shape(x, rule["items"], path + f"[{i}]")
    elif kind == "string" and "pattern" in rule:
        if re.fullmatch(rule["pattern"], value) is None:
            errors.append(path + ":PATTERN")
    return sorted(errors)


def registry(payload):
    """Bind current input aliases to content; do not choose a winning revision."""
    if type(payload) is not dict or set(payload) != {"scene", "item", "holder", "records"}:
        raise ValueError("INPUT_KEYS")
    if payload["holder"] not in ("A", "B") or any(
            type(payload[k]) is not str or not 1 <= len(payload[k]) <= 128 for k in ("scene", "item")):
        raise ValueError("INPUT_CONTEXT")
    records = payload["records"]
    if type(records) is not list or len(records) not in (2, 3):
        raise ValueError("INPUT_RECORD_COUNT")
    memory_rules = schema()["properties"]["memory"]["properties"]
    result = {}
    for record in records:
        if type(record) is not dict:
            raise ValueError("INPUT_RECORD_TYPE")
        alias = record.get("record_id")
        if type(alias) is not str or alias not in ("PRIVATE", "MEMORY_GROUP", "INCOMING_GROUP") or alias in result:
            raise ValueError("INPUT_ALIAS")
        shared = alias != "PRIVATE"
        keys = {"record_id", "author", "body"} | ({"revision"} if shared else set())
        if set(record) != keys or record["author"] not in ("A", "B"):
            raise ValueError("INPUT_RECORD_KEYS_OR_AUTHOR")
        if shape(record["body"], memory_rules["shared_note" if shared else "private_note"]):
            raise ValueError("INPUT_BODY_SHAPE")
        if shared and shape(record["revision"], REVISION):
            raise ValueError("INPUT_REVISION")
        result[alias] = {"kind": "SHARED" if shared else "PRIVATE",
                         "body_sha256": digest(record["body"]), "record": deepcopy(record)}
    if not {"PRIVATE", "INCOMING_GROUP"} <= set(result):
        raise ValueError("INPUT_REQUIRED_RECORDS")
    return result


def project_legacy_input(raw, step_id):
    """Input projection ONLY. No corresponding old-response repair operation."""
    original = parse(raw)
    projected = deepcopy(original)
    claims = []
    for rec in projected["records"]:
        if rec["record_id"] != "PRIVATE":
            refs = rec["body"].pop("channel_read_refs")
            if shape(refs, {"type": "array", "items": ID, "maxItems": 8}):
                raise ValueError("LEGACY_REFS_SHAPE")
            claims.append({"record_id": rec["record_id"], "legacy_claimed_refs": refs,
                           "status": "LEGACY_NOT_RESOLVED"})
    registry(projected)
    archive = {"step_id": step_id, "raw_utf8_text": raw.decode("utf-8"),
               "raw_sha256": sha256(raw).hexdigest(), "projected_input_sha256": digest(projected),
               "claims": claims, "claim_scope": "As observed inside the old input body; not verified historical edges"}
    return projected, archive


def validate(raw, payload, step_id):
    if type(raw) is not bytes:
        raise TypeError("raw must be bytes")
    if type(step_id) is not str or not 1 <= len(step_id) <= 128:
        raise ValueError("STEP_ID")
    records = registry(payload)  # Invalid host input is an error, not a model failure.
    result = {"status": "REJECT", "raw_sha256": sha256(raw).hexdigest(),
              "input_sha256": digest(payload), "step_id": step_id,
              "errors": [], "valid_components": {}, "bound_refs": []}
    if len(raw) > MAX_OUTPUT_BYTES:
        result["errors"] = ["OUTPUT_BYTES"]
        return result
    try:
        value = parse(raw)
    except (ValueError, UnicodeError, RecursionError) as e:
        result["errors"] = ["JSON:" + str(e)[:128]]
        return result
    result["errors"] = shape(value, schema(), "$")
    if type(value) is dict and type(value.get("memory")) is dict:
        for key, rule in schema()["properties"]["memory"]["properties"].items():
            if key in value["memory"] and not shape(value["memory"][key], rule):
                result["valid_components"][key] = deepcopy(value["memory"][key])
    receipt = value.get("read_receipt") if type(value) is dict else None
    refs = receipt.get("shared_record_refs") if type(receipt) is dict else None
    if (type(refs) is not list or any(type(r) is not str for r in refs)
            or "shared_note" not in result["valid_components"]):
        return result
    known = value["memory"]["shared_note"]["channel"] != "UNKNOWN"
    if len(refs) != int(known):
        result["errors"].append("RECEIPT_CHANNEL_COUNT")
    for alias in refs:
        if alias not in records:
            result["errors"].append("REF_NOT_CURRENT:" + alias)
        elif records[alias]["kind"] != "SHARED":
            result["errors"].append("REF_NOT_SHARED:" + alias)
    if not result["errors"]:
        result["status"] = "PASS"
        result["bound_refs"] = [{"step_id": step_id, "input_sha256": digest(payload),
                                 "record_id": alias, "body_sha256": records[alias]["body_sha256"]}
                                for alias in refs]
    return result


def local_consistency(raw, payload, step_id):
    """Observe exact snapshot support, without repair, latest-version selection or scoring."""
    gate = validate(raw, payload, step_id)
    if gate["status"] != "PASS":
        return {"status": "NOT_EVALUATED_GATE_REJECT"}
    value, records = parse(raw), registry(payload)
    memory = value["memory"]
    refs = value["read_receipt"]["shared_record_refs"]
    picked = records[refs[0]]["record"] if refs else None
    return {"status": "OBSERVED", "private_matches_input": memory["private_note"] == records["PRIVATE"]["record"]["body"],
            "shared_matches_claimed_input": memory["shared_note"] == picked["body"] if picked else None,
            "revision_matches_claimed_input": memory["shared_revision"] == picked["revision"] if picked else None}


def make_next_memory(raw, payload, step_id):
    gate = validate(raw, payload, step_id)
    if gate["status"] != "PASS":
        raise ValueError("DEPENDENT_HANDOFF_BLOCKED")
    return deepcopy(parse(raw)["memory"])
