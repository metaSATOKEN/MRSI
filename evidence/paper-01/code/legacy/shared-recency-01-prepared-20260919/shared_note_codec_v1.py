"""Offline candidate codec for shared_note-only responses (DRAFT / EDIT).

No I/O, model calls, default filling, or semantic repair. Callers must persist the
returned audit record before using accepted_text. Structural acceptance says
nothing about the truth of an observation, attribution, choice, or reference.
"""

from copy import deepcopy
import hashlib
import json
import re

VERSION = "shared-note-codec-v1"
RULE = "coverage-explicit-observer-array-to-object-v1"
MAX_BYTES = 4096


def _object(properties):
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}


def _enum(*values):
    return {"type": "string", "enum": list(values)}


_ID = {"type": "string", "pattern": r"^[A-Z][A-Z0-9_]{0,31}$"}
_OBSERVATION = _object({
    "observer": _enum("A", "B", "UNKNOWN"),
    "paper": _enum("ALL", "NOT_ALL", "UNKNOWN"),
    "digital": _enum("ALL", "NOT_ALL", "UNKNOWN"),
    "origin_id": _ID,
})
_REFERENCES = {"type": "array", "items": _ID, "maxItems": 8}
_SCHEMA = _object({"shared_note": _object({
    "coverage": _object({"A": _OBSERVATION, "B": _OBSERVATION}),
    "channel": _enum("PAPER", "DIGITAL", "UNKNOWN"),
    "channel_read_refs": _REFERENCES,
    "channel_origin_ids": _REFERENCES,
})})


def schema():
    """Return a detached schema; consumers cannot mutate the codec's contract."""
    return deepcopy(_SCHEMA)


def _json(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _roles():
    return tuple(_SCHEMA["properties"]["shared_note"]["properties"]
                 ["coverage"]["required"])


def prompt_contract():
    """Candidate appendix only; this does not enable generation constraints."""
    return (
        "出力形式：shared_note.coverageは、固定キー"
        + "/".join(_roles())
        + "を各1個持つJSON objectです。coverageに配列を使いません。"
        "各キーにはその担当の観測オブジェクトを入れます。"
        "以下は回答の形を示すスキーマであり、観測データではありません。"
        "例示値やスキーマ自体を回答として出さず、資料の値を記録してください。\n"
        + _json(schema())
    )


def _validate(value, contract, path=""):
    """Validate only this module's small schema vocabulary, not general JSON Schema.

    Unknown schema keywords are programming errors, never silently ignored.
    References intentionally allow duplicates structurally, like the old parser;
    the separate semantic scorer rejects inappropriate references.
    """
    supported = {"type", "properties", "required", "additionalProperties",
                 "enum", "pattern", "items", "maxItems"}
    if set(contract) - supported:
        raise RuntimeError("unsupported schema keyword")
    kind = contract["type"]
    expected = {"object": dict, "array": list, "string": str}[kind]
    if type(value) is not expected:
        return [f"{path or '/'}: expected {kind}"]
    if kind == "object":
        if set(value) != set(contract["required"]):
            return [f"{path or '/'}: missing or extra keys"]
        return [error for key, child in contract["properties"].items()
                for error in _validate(value[key], child, f"{path}/{key}")]
    if kind == "array":
        if len(value) > contract["maxItems"]:
            return [f"{path}: too many items"]
        return [error for i, item in enumerate(value)
                for error in _validate(item, contract["items"], f"{path}/{i}")]
    if "enum" in contract and value not in contract["enum"]:
        return [f"{path}: invalid enum"]
    if "pattern" in contract and re.fullmatch(contract["pattern"], value) is None:
        return [f"{path}: invalid identifier"]
    return []


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _non_json(_value):
    raise ValueError("non-JSON constant")


def normalize(raw):
    """Return raw evidence plus NATIVE / NORMALIZED / REJECTED and audit metadata.

    Requires str (missing responses remain the caller's responsibility). Only
    accepted_text may be sent to a structural parser. REJECTED always has None.
    An already valid object is byte-preserved, even when semantically wrong.
    """
    if type(raw) is not str:
        raise TypeError("normalize requires raw response text")
    result = {
        "codec_version": VERSION,
        "schema_sha256": _sha(_json(schema()).encode("utf-8")),
        "raw_text": raw, "raw_sha256": None,
        "status": "REJECTED", "accepted_text": None,
        "accepted_sha256": None, "rule_id": None,
        "changed_paths": [], "mapping": [], "errors": [],
    }
    try:
        raw_bytes = raw.encode("utf-8")
    except UnicodeEncodeError:
        result["errors"] = ["invalid UTF-8 text"]
        return result
    result["raw_sha256"] = _sha(raw_bytes)
    if len(raw_bytes) > MAX_BYTES:
        result["errors"] = ["raw response exceeds byte limit"]
        return result
    try:
        value = json.loads(raw, object_pairs_hook=_unique, parse_constant=_non_json)
    except (ValueError, RecursionError):
        result["errors"] = ["invalid JSON, duplicate key, non-JSON constant, or depth"]
        return result

    note = value.get("shared_note") if type(value) is dict else None
    coverage = note.get("coverage") if type(note) is dict else None
    mapping = []
    if type(coverage) is list:
        roles = _roles()
        if (len(coverage) != len(roles)
                or any(_validate(item, _OBSERVATION) for item in coverage)
                or sorted(item["observer"] for item in coverage) != sorted(roles)):
            result["errors"] = ["coverage array requires complete, unique A/B observations"]
            return result
        mapping = [{"from": f"/shared_note/coverage/{i}",
                    "to": f"/shared_note/coverage/{item['observer']}"}
                   for i, item in enumerate(coverage)]
        by_role = {item["observer"]: item for item in coverage}
        note["coverage"] = {role: by_role[role] for role in roles}

    errors = _validate(value, _SCHEMA)
    if errors:
        result["errors"] = errors
        return result
    accepted = _json(value) if mapping else raw
    accepted_bytes = accepted.encode("utf-8")
    if len(accepted_bytes) > MAX_BYTES:
        result["errors"] = ["accepted response exceeds byte limit"]
        return result
    result.update(status="NORMALIZED" if mapping else "NATIVE",
                  accepted_text=accepted, accepted_sha256=_sha(accepted_bytes),
                  rule_id=RULE if mapping else None,
                  changed_paths=["/shared_note/coverage"] if mapping else [],
                  mapping=mapping)
    return result
