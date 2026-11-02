"""Offline controller for CROSS-MODEL-E1-01. Standard library, no model backend.

The builder embeds this file and a sealed E1 subset in a single Colab cell.
Synthetic answers below are test fixtures, never experimental observations.
"""
import base64
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys
import tempfile
import types
import zlib


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unpack_bundle(blob, expected_digest):
    raw = zlib.decompress(base64.b64decode(blob, validate=True))
    require(sha256(raw).hexdigest() == expected_digest, "BUNDLE_HASH_MISMATCH")
    bundle = json.loads(raw)
    for name, source in bundle["sources"].items():
        require(sha256(source.encode("utf-8")).hexdigest() == bundle["source_hashes"][name],
                "SOURCE_HASH_MISMATCH:" + name)
    require(len(bundle["materials"]) == 64, "MATERIAL_COUNT")
    require(len(bundle["base_slots"]) == 512, "BASE_SLOT_COUNT")
    return bundle


def load_fixed_code(bundle):
    # Use exact archived sources, without running their build()/main() functions.
    # Restore a user's existing imports after resolving this isolated module graph.
    names = ("note_provenance_split_v1", "row_carry_02_design_v1", "paper01_pair_design_v1")
    previous = {name: sys.modules.get(name) for name in names}
    loaded = {}
    try:
        for name in names:
            module = types.ModuleType(name)
            module.__file__ = "/npp_offline_bundle/code/" + name + ".py"
            sys.modules[name] = module
            exec(compile(bundle["sources"][name + ".py"], module.__file__, "exec"), module.__dict__)
            loaded[name] = module
    finally:
        for name, value in previous.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value
    return loaded[names[-1]]


def repeated_slots(base_slots):
    slots = []
    for rep in (1, 2, 3):
        for source in base_slots:
            slot = deepcopy(source)
            slot["source_id"] = source["id"]
            slot["id"] = f"XM01-R{rep}-" + source["id"]
            slot["replicate"] = rep
            slot["dependencies"] = [f"XM01-R{rep}-" + dep for dep in source["dependencies"]]
            seed_text = "CROSS-MODEL-E1-01/v1|" + slot["id"]
            slot["seed"] = int(sha256(seed_text.encode()).hexdigest()[:8], 16) % (2 ** 31)
            slots.append(slot)
    validate_slots(slots)
    return slots


def validate_slots(slots):
    seen = {}
    for slot in slots:
        require(slot["id"] not in seen, "DUPLICATE_SLOT_ID")
        expected_parents = 0 if slot["stage"] == "MERGE" else 1
        require(len(slot["dependencies"]) == expected_parents, "DEPENDENCY_COUNT")
        for dep in slot["dependencies"]:
            require(dep in seen, "PARENT_NOT_EARLIER")
            parent = seen[dep]
            require(parent["stage"] == "MERGE", "PARENT_STAGE")
            for field in ("group", "condition", "role", "replicate"):
                require(slot[field] == parent[field], "CROSS_BRANCH_PARENT:" + field)
        seen[slot["id"]] = slot


def projected_messages(bundle, slot, payload):
    prompt_key = "PROBE" if slot["stage"] == "PROBE" else "MERGE_" + slot["condition"]
    # No material truth, labels, hypotheses, scores, or prior model answers here.
    return [{"role": "system", "content": bundle["prompts"][prompt_key]},
            {"role": "user", "content": "\n資料JSON:\n" + encoded(payload).decode("utf-8")}]


def run_synthetic_case(bundle, pair, slots, answer_fixture, label):
    states, rows = {}, {}
    for slot in slots:
        material = bundle["materials"][slot["group"]]
        if any(dep not in states for dep in slot["dependencies"]):
            rows[slot["id"]] = {
                "status": "DEPENDENCY_MISSING", "raw": None, "payload": None,
                "score": {"strict": None, "content": None, "parts": {}},
                "gate": "NOT_RUN", "fixture": label,
            }
            continue
        payload = pair.e1_input(material, slot, states)
        require(not pair.validate_input("E1", slot["stage"], payload), "INGRESS_REJECT")
        messages = projected_messages(bundle, slot, payload)
        # This is an explicit synthetic fixture, NOT a stand-in used after model errors.
        raw = answer_fixture(material, slot, deepcopy(payload), pair)
        evaluation = pair.e1_evaluate(material, slot, raw, payload)
        row = {
            "fixture": label, "status": "SYNTHETIC", "payload": payload, "messages": messages,
            "raw": raw.decode("utf-8"), "raw_sha256": sha256(raw).hexdigest(),
            "score": evaluation["score"], "gate": evaluation["gate"],
            "bindings": evaluation.get("bindings", []),
            "normalized": evaluation.get("normalized"),
        }
        if slot["stage"] == "MERGE" and evaluation["gate"] == "PASS":
            states[slot["id"]] = deepcopy(evaluation["normalized"]["memory"])
            row["saved_state_sha256"] = sha256(encoded(states[slot["id"]])).hexdigest()
        rows[slot["id"]] = row
    require(set(rows) == {s["id"] for s in slots}, "EXPECTED_ID_SET_MISMATCH")
    return rows


def counts(values):
    values = list(values)
    return {"success": values.count(True), "failure": values.count(False),
            "unresolved": values.count(None), "total": len(values)}


def summarize(pair, slots, rows):
    require(set(rows) == {s["id"] for s in slots}, "SUMMARY_ID_SET_MISMATCH")
    groups = sorted({s["group"] for s in slots})
    reps = sorted({s["replicate"] for s in slots})
    require(reps == [1, 2, 3] and len(groups) == 64, "SUMMARY_DESIGN_COUNT")
    indexed = {}
    for slot in slots:
        key = (slot["group"], slot["condition"], slot["replicate"])
        indexed.setdefault(key, []).append(slot["id"])
    require(len(indexed) == 384 and all(len(ids) == 4 for ids in indexed.values()), "GROUP_REP_COUNT")
    result = {
        "kind": "SYNTHETIC_OFFLINE_ONLY", "model_generations": 0,
        "material_count": 64, "replicates_per_material": 3, "planned_responses": len(slots),
        "independent_material_count_not_192": 64,
        "response_status": dict(Counter(row["status"] for row in rows.values())),
        "metrics": {}, "stage_parts": {},
    }
    for metric in ("strict", "content"):
        grouped = {key: pair.rc.tri_and(rows[sid]["score"].get(metric) for sid in ids)
                   for key, ids in indexed.items()}
        methods = {}
        for method in ("REWRITE", "SELECT"):
            values = [grouped[g, method, rep] for g in groups for rep in reps]
            c = counts(values)
            patterns = Counter()
            disagreement = evaluable_pairs = unresolved_pairs = 0
            by_group = {}
            for g in groups:
                v = [grouped[g, method, rep] for rep in reps]
                by_group[g] = v
                pattern = ("has_unresolved" if None in v else "all_success" if all(v)
                           else "all_failure" if not any(v) else "mixed_success_failure")
                patterns[pattern] += 1
                for left, right in combinations(v, 2):
                    if left is None or right is None:
                        unresolved_pairs += 1
                    else:
                        evaluable_pairs += 1
                        disagreement += int(left != right)
            methods[method] = {
                "group_replicate_counts": c,
                "success_bounds": [c["success"] / 192, (c["success"] + c["unresolved"]) / 192],
                "by_replicate": {str(rep): counts(grouped[g, method, rep] for g in groups) for rep in reps},
                "by_group": by_group, "repeat_patterns": dict(patterns),
                "repeat_disagreement": {"different": disagreement, "evaluable_pairs": evaluable_pairs,
                                        "unresolved_pairs": unresolved_pairs,
                                        "rate": disagreement / evaluable_pairs if evaluable_pairs else None},
            }
        s_lo, s_hi = methods["SELECT"]["success_bounds"]
        r_lo, r_hi = methods["REWRITE"]["success_bounds"]
        result["metrics"][metric] = {
            "methods": methods,
            "select_minus_rewrite_missingness_bounds": [s_lo - r_hi, s_hi - r_lo],
            "paired_by_replicate": {
                str(rep): dict(Counter(f"R={grouped[g, 'REWRITE', rep]}|S={grouped[g, 'SELECT', rep]}"
                                       for g in groups)) for rep in reps},
            "p_value": None, "confidence_interval": None,
            "reason": "Descriptive fixed-material replication; no independent-N=192 test.",
        }
    # These are response/component counts, not independent sample counts.
    component_values = {}
    for slot in slots:
        expected_parts = (("private_note.customer", "private_note.coverage", "shared_note.coverage.A", "shared_note.coverage.B")
                          if slot["stage"] == "MERGE" else ("mascot", "channel"))
        for part in expected_parts:
            scores = rows[slot["id"]]["score"].get("parts", {}).get(part, {})
            for metric in ("strict", "content"):
                key = "|".join((slot["condition"], slot["stage"], part, metric))
                component_values.setdefault(key, []).append(scores.get(metric))
    result["stage_parts"] = {key: counts(values) for key, values in sorted(component_values.items())}
    return result


def perfect_fixture(material, slot, payload, pair):
    return encoded(pair.e1_ideal(material, slot))


def expect_rejection(action, reason):
    try:
        action()
    except ValueError as error:
        require(reason in str(error), "WRONG_REJECTION:" + str(error))
        return
    raise ValueError("MISSING_REJECTION:" + reason)


def offline_suite(bundle, pair, slots, verbose=True):
    checks = []
    if verbose:
        print("[1/4] 合成正答で1,536応答の経路を点検（LLM実測ではありません）")
    perfect = run_synthetic_case(bundle, pair, slots, perfect_fixture, "PERFECT_SYNTHETIC")
    summary = summarize(pair, slots, perfect)
    for metric in ("strict", "content"):
        for method in ("REWRITE", "SELECT"):
            require(summary["metrics"][metric]["methods"][method]["group_replicate_counts"] ==
                    {"success": 192, "failure": 0, "unresolved": 0, "total": 192}, "PERFECT_FAILED")
    checks.append("1536_synthetic_paths_and_384_group_replicates")

    target = next(s for s in slots if s["stage"] == "MERGE" and s["condition"] == "REWRITE")
    child = next(s for s in slots if s["dependencies"] == [target["id"]])
    branch = [target, child]
    good_origin = bundle["materials"][target["group"]]["baseline_by_role"][target["role"]]["private_note"]["customer"]["origin_id"]
    wrong_origin = good_origin[:-1]

    def corrupt_origin(material, slot, payload, pair):
        answer = pair.e1_ideal(material, slot)
        if slot["stage"] == "MERGE":
            answer["memory"]["private_note"]["customer"]["origin_id"] = wrong_origin
        else:
            # Explicit synthetic behavior: report the ID found in the actual saved note.
            answer["origin_ids"]["mascot"] = [payload["records"][0]["body"]["customer"]["origin_id"]]
        return encoded(answer)

    if verbose:
        print("[2/4] 誤出典の保持と、正答・出典評価の分離を点検")
    corrupted = run_synthetic_case(bundle, pair, branch, corrupt_origin, "CORRUPT_ORIGIN_SYNTHETIC")
    for sid in (target["id"], child["id"]):
        require(corrupted[sid]["gate"] == "PASS", "SEMANTIC_ERROR_SHOULD_PASS_STRUCTURE")
        require(corrupted[sid]["score"]["strict"] is False and corrupted[sid]["score"]["content"] is True,
                "CONTENT_PROVENANCE_NOT_SEPARATED")
    require(corrupted[child["id"]]["payload"]["records"][0]["body"]["customer"]["origin_id"] == wrong_origin,
            "WRONG_ORIGIN_WAS_REPAIRED")
    checks.append("bad_origin_passes_structure_fails_strict_and_reaches_probe")

    select = next(s for s in slots if s["stage"] == "MERGE" and s["condition"] == "SELECT")
    def stale_selection(material, slot, payload, pair):
        answer = pair.e1_ideal(material, slot)
        role = slot["role"]
        answer["memory"]["shared_note"]["coverage"][role] = {"record_id": "PARTNER_GROUP", "observer": role}
        answer["read_receipt"]["shared_coverage_refs"][role] = ["PARTNER_GROUP"]
        return encoded(answer)
    stale = run_synthetic_case(bundle, pair, [select], stale_selection, "STALE_SELECTION_SYNTHETIC")
    item = stale[select["id"]]
    require(item["gate"] == "PASS" and item["score"]["strict"] is False, "STALE_SELECTION_SCORE")
    selected_input = next(r for r in item["payload"]["records"] if r["record_id"] == "PARTNER_GROUP")
    require(item["normalized"]["memory"]["shared_note"]["coverage"][select["role"]] ==
            selected_input["body"]["coverage"][select["role"]], "COPY_NOT_FAITHFUL")
    checks.append("faithful_copy_of_wrong_selection_is_not_success")

    if verbose:
        print("[3/4] JSON欠損と依存欠測、欠測上下限を点検")
    def bad_json(material, slot, payload, pair):
        raw = perfect_fixture(material, slot, payload, pair)
        return raw[:-1] if slot["id"] == target["id"] else raw
    broken = run_synthetic_case(bundle, pair, slots, bad_json, "BROKEN_JSON_SYNTHETIC")
    require(broken[child["id"]]["status"] == "DEPENDENCY_MISSING", "MISSING_PARENT_WAS_FILLED")
    require(sum(r["status"] == "DEPENDENCY_MISSING" for r in broken.values()) == 1, "WRONG_MISSING_SCOPE")
    broken_summary = summarize(pair, slots, broken)
    bounds = broken_summary["metrics"]["strict"]["select_minus_rewrite_missingness_bounds"]
    require(abs(bounds[0]) < 1e-12 and abs(bounds[1] - 1 / 192) < 1e-12, "MISSING_BOUND_CALCULATION")
    checks.append("malformed_json_blocks_only_its_own_probe_without_imputation")
    checks.append("missingness_bounds_use_64_materials_times_3_repeats")

    # A single changed replicate must register as two discordant repeat pairs.
    altered = deepcopy(perfect)
    altered[target["id"]]["score"]["strict"] = False
    changed = summarize(pair, slots, altered)
    repeat_stats = changed["metrics"]["strict"]["methods"]["REWRITE"]["repeat_disagreement"]
    require(repeat_stats == {"different": 2, "evaluable_pairs": 192, "unresolved_pairs": 0, "rate": 2 / 192},
            "REPEAT_DISAGREEMENT_CALCULATION")
    checks.append("within_material_repeat_disagreement_2_of_192_pairs")

    if verbose:
        print("[4/4] ID集合・反復間の混線・同梱コードの改変検知を点検")
    expect_rejection(lambda: validate_slots(slots + [slots[0]]), "DUPLICATE_SLOT_ID")
    crossed = deepcopy(slots)
    victim = next(s for s in crossed if s["replicate"] == 2 and s["stage"] == "PROBE")
    victim["dependencies"][0] = victim["dependencies"][0].replace("XM01-R2-", "XM01-R1-")
    expect_rejection(lambda: validate_slots(crossed), "CROSS_BRANCH_PARENT:replicate")
    incomplete = dict(perfect)
    incomplete.pop(target["id"])
    expect_rejection(lambda: summarize(pair, slots, incomplete), "SUMMARY_ID_SET_MISMATCH")
    checks.extend(["duplicate_id_rejected", "cross_replicate_parent_rejected", "missing_result_id_rejected"])
    examples = {"corrupt_origin": corrupted, "stale_selection": stale,
                "broken_json": {sid: broken[sid] for sid in (target["id"], child["id"])}}
    return {"status": "PASS_OFFLINE_SYNTHETIC_ONLY", "checks": checks,
            "perfect_fixture": summary, "missing_fixture": broken_summary,
            "changed_repeat_fixture": changed, "examples": examples}


def run_offline_cell(blob, expected_digest, output_dir=None, verbose=True):
    bundle = unpack_bundle(blob, expected_digest)
    pair = load_fixed_code(bundle)
    slots = repeated_slots(bundle["base_slots"])
    # A new folder per invocation keeps the demonstrations separate and avoids overwrite.
    if output_dir is None:
        parent = Path("/content") if Path("/content").is_dir() else Path(tempfile.gettempdir())
    else:
        parent = Path(output_dir).expanduser()
        parent.mkdir(parents=True, exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix="npp-xm01-offline-", dir=str(parent)))
    if verbose:
        print("CROSS-MODEL-E1-01 / オフライン実装点検のみ / モデル生成 0")
        print("GPU・ネットワーク・認証・Drive接続は使用しません。")
    report = offline_suite(bundle, pair, slots, verbose=verbose)
    # Hash failure checks use a deliberately wrong digest / altered source.
    expect_rejection(lambda: unpack_bundle(blob, "0" * 64), "BUNDLE_HASH_MISMATCH")
    changed_bundle = deepcopy(bundle)
    source_name = next(iter(changed_bundle["sources"]))
    changed_bundle["sources"][source_name] += "\n# changed\n"
    changed_bytes = encoded(changed_bundle)
    expect_rejection(lambda: unpack_bundle(base64.b64encode(zlib.compress(changed_bytes)).decode(),
                                          sha256(changed_bytes).hexdigest()), "SOURCE_HASH_MISMATCH")
    report["checks"].extend(["bundle_digest_mismatch_rejected", "source_digest_mismatch_rejected"])
    (out / "code").mkdir()
    for name, source in bundle["sources"].items():
        (out / "code" / name).write_text(source, encoding="utf-8")
    (out / "bundle.json").write_bytes(encoded(bundle) + b"\n")
    (out / "allocation.json").write_bytes(encoded(slots) + b"\n")
    (out / "offline-report.json").write_bytes(encoded(report) + b"\n")
    file_hashes = {str(p.relative_to(out)): sha256(p.read_bytes()).hexdigest()
                   for p in sorted(out.rglob("*")) if p.is_file()}
    (out / "MANIFEST.json").write_bytes(encoded({"kind": "SYNTHETIC_OFFLINE_ONLY", "model_generations": 0,
                                                "bundle_sha256": expected_digest, "files_sha256": file_hashes}) + b"\n")
    if verbose:
        print(f"完了：{len(report['checks'])}項目。合成1,536応答、LLM性能の測定は0件。")
        print("出力先:", out)
        print("このファイルは実機推論・中断再開を未実装です。実機版は接続準備で別途固定します。")
    return out
