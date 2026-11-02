"""SC03 offline design: shared-note codec before storage and later projection.

No transport, authentication, persistence, or real model calls. SC02's content
scorer is unchanged; only DRAFT/EDIT prompts and structural ingestion differ.
"""
from copy import deepcopy
import shared_carry_02_design_v1 as base
import shared_note_codec_v1 as codec

ROLES, ARMS, SEED = base.ROLES, base.ARMS, base.SEED
LIMITS = deepcopy(base.LIMITS)
PROMPTS = dict(base.PROMPTS)
for _stage in ("DRAFT", "EDIT"):
    PROMPTS[_stage] += "\n\n" + codec.prompt_contract()

canon, sid, payload, ideal = base.canon, base.sid, base.payload, base.ideal
STATUSES = ("NATIVE", "NORMALIZED", "REJECTED", "NO_RESPONSE", "DEPENDENCY_UNISSUED")


def materials():
    groups = base.materials()
    for group in groups:
        group["group"] = group["group"].replace("SC02", "SC03", 1)
    return groups


def allocation(groups):
    return base.allocation(groups)


def input_text(group, slot, parsed):
    packet = payload(group, slot, parsed)
    return None if packet is None else PROMPTS[slot["stage"]] + "\n資料JSON:\n" + canon(packet)


def ingest(raw, stage):
    """Pure receipt handling; real callers must persist raw/audit before delivery."""
    if raw is not None and type(raw) is not str:
        raise TypeError("raw response must be text or None")
    record = codec.normalize(raw) if stage in ("DRAFT", "EDIT") and raw is not None else None
    accepted = record["accepted_text"] if record is not None else raw
    parsed = base.parse(accepted, stage)
    return dict(accepted_text=accepted, codec_record=record, parsed=parsed)


def analyse(groups, slots, outputs):
    assert set(outputs) == {s["id"] for s in slots}, "planned IDs must match exactly"
    receipts = {s["id"]: ingest(outputs[s["id"]], s["stage"]) for s in slots}
    accepted = {key: value["accepted_text"] for key, value in receipts.items()}
    result = base.analyse(groups, slots, accepted)
    row_by_id = {r["id"]: r for r in result["rows"]}
    format_rows = []
    for slot in slots:
        key = slot["id"]
        blocked = row_by_id[key]["dependency_unissued"]
        if blocked and outputs[key] is not None:
            raise ValueError("output exists despite unavailable parent: " + key)
        if slot["stage"] not in ("DRAFT", "EDIT"):
            continue
        record = receipts[key]["codec_record"]
        status = ("DEPENDENCY_UNISSUED" if blocked else "NO_RESPONSE"
                  if record is None else record["status"])
        format_rows.append(dict(id=key, group=slot["group"], stage=slot["stage"], status=status))

    summary = {}
    for stage in ("DRAFT", "EDIT", "ALL"):
        rows = [r for r in format_rows if stage == "ALL" or r["stage"] == stage]
        counts = {label: sum(r["status"] == label for r in rows) for label in STATUSES}
        received = sum(counts[label] for label in STATUSES[:3])
        summary[stage] = dict(
            planned=len(rows), counts=counts, received=received,
            received_fraction_of_planned=received / len(rows),
            rates_among_received={label: counts[label] / received if received else None
                                  for label in STATUSES[:3]},
            usable_format_rate=(counts["NATIVE"] + counts["NORMALIZED"]) / received if received else None,
        )
    result.update(format_rows=format_rows, format_summary=summary,
                  estimand="SYSTEM_WITH_FIXED_SCHEMA_PROMPT_AND_CODEC",
                  raw_only_counterfactual_score_computed=False)
    return result


def simulate(groups, slots, mutation=None):
    """Synthetic fixture generator; ideal answers are not supplied to real workers."""
    by_group = {g["group"]: g for g in groups}
    parsed, outputs, accepted, receipts, inputs = {}, {}, {}, {}, {}
    blocked = []
    for slot in slots:
        group = by_group[slot["group"]]
        text = input_text(group, slot, parsed)
        if text is None:
            raw = None
            blocked.append(slot["id"])
        else:
            inputs[slot["id"]] = text
            obj = ideal(group, slot)
            if mutation:
                obj = mutation(slot, obj)
            raw = obj if type(obj) is str or obj is None else canon(obj)
        key = slot["id"]
        receipt = ingest(raw, slot["stage"])
        outputs[key] = raw
        accepted[key] = receipt["accepted_text"]
        parsed[key] = receipt["parsed"]
        receipts[key] = receipt["codec_record"]
    return dict(outputs=outputs, accepted_outputs=accepted, codec_records=receipts,
                parsed=parsed, inputs=inputs, dependency_unissued=blocked,
                analysis=analyse(groups, slots, outputs))
