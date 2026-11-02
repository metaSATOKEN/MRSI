"""Shared generation/controller implementation for the two-part main run. No model import at module import time.

Storage/controller functions are tested locally with an explicit fake backend.
Only worker_main creates a real Hugging Face backend, after Colab/GPU guards.
"""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time
import traceback
import uuid

import cross_model_e1_01_offline_runtime as core

MODEL_ID = "Qwen/Qwen3.5-27B"
MODEL_REVISION = "fc05daec18b0a78c049392ed2e771dde82bdf654"
# tokenizer_config.json at MODEL_REVISION: endoftext is PAD, im_end is EOS.
SPECIAL_TOKEN_IDS = {"<|endoftext|>": 248044, "<|im_start|>": 248045, "<|im_end|>": 248046}
PINS = {"transformers": "5.17.0", "accelerate": "1.15.0"}
GENERATION = {"do_sample": True, "temperature": 0.7, "top_p": 0.8, "top_k": 20,
              "repetition_penalty": 1.0, "max_new_tokens": 2048, "use_cache": True}
MAX_INPUT_TOKENS = 8192
MIN_TOTAL_VRAM = 75_000_000_000
MIN_FREE_VRAM = 65_000_000_000
STOP_REQUESTED = False


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    return sha256(core.encoded(value)).hexdigest()


def write_new(path, raw):
    """Single-writer, immutable files; publish only a complete temporary file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    core.require(not path.exists(), "WOULD_OVERWRITE:" + path.name)
    temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    with temporary.open("xb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    core.require(not path.exists(), "CONCURRENT_WRITER")
    os.rename(temporary, path)
    core.require(path.read_bytes() == raw, "PERSISTENCE_READBACK_FAILED")


def write_json(path, value):
    write_new(path, core.encoded(value) + b"\n")


def read_json(path):
    return json.loads(Path(path).read_bytes())


def fix_or_compare(path, value):
    if Path(path).exists():
        core.require(read_json(path) == value, "RESUME_CONTRACT_MISMATCH:" + Path(path).name)
    else:
        write_json(path, value)


def make_canary(bundle):
    """Dedicated structural clone; origin IDs and scene separate it from the 64 groups."""
    old_group = "E1-G01"
    material = deepcopy(bundle["materials"][old_group])
    mapping = {}
    def remap(value):
        if isinstance(value, dict):
            return {key: (mapping.setdefault(item, "C" + sha256(("XM01_CANARY|" + item).encode()).hexdigest()[:15].upper())
                          if key == "origin_id" else remap(item)) for key, item in value.items()}
        if isinstance(value, list):
            return [remap(item) for item in value]
        return value
    material = remap(material)
    material["scene"] = "接続確認用の架空会場"
    material["item"] = "担当客の犬猫希望と案内方法の確認"
    group = "XM01-CANARY01"
    slots = []
    for old in bundle["base_slots"]:
        if old["group"] != old_group:
            continue
        slot = deepcopy(old)
        slot["id"] = old["id"].replace(old_group, group)
        slot["group"] = group
        slot["replicate"] = 1
        slot["dependencies"] = [dep.replace(old_group, group) for dep in old["dependencies"]]
        slot["seed"] = int(sha256(("CROSS-MODEL-E1-01/v1|" + slot["id"]).encode()).hexdigest()[:8], 16) % (2 ** 31)
        slots.append(slot)
    core.validate_slots(slots)
    core.require(len(slots) == 8 and len(mapping) == len(set(mapping.values())), "CANARY_ALLOCATION")
    core.require(not set(mapping) & set(mapping.values()), "CANARY_IDS_NOT_SEPARATE")
    return {group: material}, slots


def contract_for(bundle, slots, source_hashes):
    return {"protocol": "CROSS-MODEL-E1-01-SMOKE-v0.4", "model": MODEL_ID, "revision": MODEL_REVISION,
            "special_token_ids": SPECIAL_TOKEN_IDS,
            "prior_setup_seconds": 54.087,
            "prior_feedback_sha256": "a3deb0aaebdb33eb8c815e39e46d5356497b495263728ddbf88778758fd9c66f",
            "storage": {"mode": "colab_ephemeral", "root": "/content/npp_xm01_runs", "cloud_drive": "not_used",
                        "delivery": "zip_download_at_end", "resume": "while_local_files_survive"},
            "bundle_sha256": digest(bundle), "allocation_sha256": digest(slots), "source_hashes": source_hashes,
            "pins": PINS, "generation": GENERATION, "max_input_tokens": MAX_INPUT_TOKENS,
            "enable_thinking": False, "dtype": "bfloat16", "attention": "sdpa",
            "max_generations": 8, "total_seconds": 3600, "automatic_retries": 0,
            "eos_policy": "Remove one final im_end token only; retain all other text/tokens.",
            "non_eos_policy": "Preserve raw output; primary score unresolved; no downstream memory."}


def unknown_score():
    return {"strict": None, "content": None, "parts": {}, "gate": "NOT_EVALUABLE",
            "shape_errors": [], "ref_errors": []}


class EvidenceStore:
    def __init__(self, root, contract):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        fix_or_compare(self.root / "contract.json", contract)

    def directory(self, slot):
        return self.root / "responses" / slot["id"]

    def completed(self, slot):
        return (self.directory(slot) / "result.json").exists()

    def load(self, slot):
        folder = self.directory(slot)
        result = read_json(folder / "result.json")
        core.require(result["id"] == slot["id"], "RESULT_ID_MISMATCH")
        present = {p.name for p in folder.iterdir() if p.is_file() and ".tmp-" not in p.name and p.name != "result.json"}
        core.require(present == set(result["files_sha256"]), "RESULT_FILE_SET_MISMATCH")
        for name, expected in result["files_sha256"].items():
            core.require(sha256((folder / name).read_bytes()).hexdigest() == expected, "EVIDENCE_HASH_MISMATCH:" + name)
        return result

    def finish(self, slot, status, score=None, gate="NOT_RUN"):
        folder = self.directory(slot)
        folder.mkdir(parents=True, exist_ok=True)
        hashes = {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(folder.iterdir())
                  if p.is_file() and ".tmp-" not in p.name and p.name != "result.json"}
        result = {"id": slot["id"], "status": status, "score": score or unknown_score(),
                  "gate": gate, "finished_at": now(), "files_sha256": hashes}
        write_json(folder / "result.json", result)
        return result


def finish_response(store, pair, material, slot):
    folder = store.directory(slot)
    request = read_json(folder / "input.json")
    response = read_json(folder / "response.json")
    core.require(response.get("payload_sha256") == digest({key: value for key, value in response.items() if key != "payload_sha256"}),
                 "PENDING_RESPONSE_HASH")
    core.require(response["finish_reason"] in ("EOS", "LENGTH", "TIME_LIMIT"), "FINISH_REASON")
    # Last EOS removal happens once in the backend, with its token IDs retained.
    answer = response["answer_text"].encode("utf-8")
    fix = lambda name, raw: (core.require((folder / name).read_bytes() == raw, "RECOVERY_ARTIFACT_MISMATCH:" + name)
                             if (folder / name).exists() else write_new(folder / name, raw))
    fix("answer.txt", answer)
    fix("decoded-with-special-tokens.txt", response["decoded_with_special_tokens"].encode("utf-8"))
    if response["finish_reason"] != "EOS":
        return store.finish(slot, response["finish_reason"])
    evaluation = pair.e1_evaluate(material, slot, answer, request["payload"])
    fix("evaluation.json", core.encoded(evaluation) + b"\n")
    if slot["stage"] == "MERGE" and evaluation["gate"] == "PASS":
        fix("saved-memory.json", core.encoded(evaluation["normalized"]["memory"]) + b"\n")
    status = "EOS" if evaluation["gate"] == "PASS" else "STRUCTURE_REJECT"
    return store.finish(slot, status, evaluation["score"], evaluation["gate"])


def expected_input(pair, bundle, slot, states, materials):
    payload = pair.e1_input(materials[slot["group"]], slot, states)
    core.require(not pair.validate_input("E1", slot["stage"], payload), "INGRESS_REJECT")
    return {"payload": payload, "messages": core.projected_messages(bundle, slot, payload),
            "parents": {dep: digest(states[dep]) for dep in slot["dependencies"]}, "seed": slot["seed"]}


def run_routes(store, bundle, pair, materials, slots, backend=None, deadline=float("inf")):
    """backend=None only reconstructs recorded state; never calls a fixture fallback."""
    states, rows = {}, {}
    for slot in slots:
        folder = store.directory(slot)
        material = materials[slot["group"]]
        missing_parent = any(dep not in states for dep in slot["dependencies"])
        expected = None if missing_parent else expected_input(pair, bundle, slot, states, materials)
        if store.completed(slot):
            result = store.load(slot)
            if (folder / "input.json").exists():
                stored = read_json(folder / "input.json")
                core.require(expected is not None and all(stored[key] == expected[key] for key in expected),
                             "INPUT_OR_PARENT_CHANGED")
            if result["status"] in ("EOS", "STRUCTURE_REJECT"):
                response = read_json(folder / "response.json")
                core.require(response.get("payload_sha256") == digest({k: v for k, v in response.items() if k != "payload_sha256"}),
                             "RESPONSE_HASH_MISMATCH")
                core.require((folder / "answer.txt").read_bytes() == response["answer_text"].encode(), "ANSWER_RESPONSE_MISMATCH")
                replay = pair.e1_evaluate(material, slot, (folder / "answer.txt").read_bytes(), expected["payload"])
                core.require(replay == read_json(folder / "evaluation.json") and replay["score"] == result["score"]
                             and replay["gate"] == result["gate"], "REPLAY_MISMATCH")
                if slot["stage"] == "MERGE" and result["gate"] == "PASS":
                    core.require(read_json(folder / "saved-memory.json") == replay["normalized"]["memory"], "SAVED_MEMORY_MISMATCH")
        elif (folder / "started.json").exists():
            stored = read_json(folder / "input.json")
            core.require(expected is not None and all(stored[key] == expected[key] for key in expected), "PENDING_INPUT_CHANGED")
            started = read_json(folder / "started.json")
            core.require(started["input_sha256"] == sha256((folder / "input.json").read_bytes()).hexdigest(), "PENDING_INPUT_HASH")
            if (folder / "response.json").exists():
                result = finish_response(store, pair, material, slot)
            else:
                result = store.finish(slot, "INTERRUPTED_UNCERTAIN")
        elif missing_parent:
            # A parent not yet attempted remains pending; a closed rejected parent blocks its child.
            if not all(dep in rows for dep in slot["dependencies"]):
                continue
            result = store.finish(slot, "DEPENDENCY_MISSING")
        elif backend is None or STOP_REQUESTED or time.monotonic() >= deadline:
            continue
        else:
            # Reject leftover input files that predate a start marker; do not overwrite or infer a call.
            if folder.exists() and any(folder.iterdir()):
                result = store.finish(slot, "PREPARATION_INTERRUPTED")
                rows[slot["id"]] = result
                continue
            prepared = backend.prepare(expected["messages"])
            request = dict(expected, prepared=prepared)
            write_json(folder / "input.json", request)
            if len(prepared["input_ids"]) > MAX_INPUT_TOKENS:
                result = store.finish(slot, "INPUT_TOO_LONG")
            else:
                if STOP_REQUESTED or time.monotonic() >= deadline:
                    result = store.finish(slot, "STOPPED_BEFORE_GENERATION")
                else:
                    write_json(folder / "started.json", {"started_at": now(), "seed": slot["seed"],
                                                        "input_sha256": sha256((folder / "input.json").read_bytes()).hexdigest()})
                    try:
                        response = backend.generate(prepared, slot["seed"], deadline)
                        response["payload_sha256"] = digest(response)
                        write_json(folder / "response.json", response)
                    except Exception as error:
                        write_json(folder / "generation-error.json", {"type": type(error).__name__, "message": str(error),
                                                                     "traceback": traceback.format_exc()})
                        store.finish(slot, "GENERATION_ERROR")
                        raise
                    result = finish_response(store, pair, material, slot)
                    print(f"[{slot['id']}] {result['status']} / strict={result['score']['strict']}", flush=True)
        rows[slot["id"]] = result
        if slot["stage"] == "MERGE" and result["gate"] == "PASS":
            states[slot["id"]] = read_json(folder / "saved-memory.json")
    return rows


def make_report(store, slots, rows):
    rows = {slot["id"]: rows.get(slot["id"], {"status": "NOT_ISSUED", "score": unknown_score(), "gate": "NOT_RUN"})
            for slot in slots}
    connected = {}
    for method in ("REWRITE", "SELECT"):
        connected[method] = [slot["role"] for slot in slots if slot["condition"] == method and slot["stage"] == "PROBE"
                             and rows[slot["dependencies"][0]]["gate"] == "PASS"
                             and rows[slot["id"]]["status"] in ("EOS", "STRUCTURE_REJECT")]
    closed_ok = all(row["status"] in ("EOS", "STRUCTURE_REJECT", "DEPENDENCY_MISSING") for row in rows.values())
    timings = []
    for slot in slots:
        response_path = store.directory(slot) / "response.json"
        if response_path.exists():
            response = read_json(response_path)
            timings.append({"id": slot["id"], "tokens": len(response["output_token_ids"]),
                            "seconds": response["generation_seconds"], "peak_vram_bytes": response["peak_vram_bytes"]})
    seconds = sum(row["seconds"] for row in timings)
    return {"kind": "CANARY_ROUTE_CHECK_NOT_RESEARCH_REPLICATION", "generated_at": now(), "planned_responses": 8,
            "route_status": "ROUTE_READY" if closed_ok and all(connected.values()) else "NEEDS_REVIEW",
            "connected_probe_roles": connected, "semantic_accuracy_is_not_a_route_gate": True,
            "attempted_generations": sum((store.directory(slot) / "started.json").exists() for slot in slots),
            "status_counts": dict(core.Counter(row["status"] for row in rows.values())),
            "strict": core.counts(row["score"]["strict"] for row in rows.values()),
            "rows": rows, "generation_timings": timings,
            "observed_tokens_per_second": sum(row["tokens"] for row in timings) / seconds if seconds else None,
            "rough_1536_generation_hours": (seconds / len(timings) * 1536 / 3600) if timings else None,
            "estimate_note": "Small canary extrapolation only; excludes setup/storage and does not approve MAIN."}


def gpu_guard(info):
    core.require(info["cuda_available"], "CUDA_REQUIRED_NO_MODEL_LOAD")
    core.require(info["total_bytes"] >= MIN_TOTAL_VRAM, "INSUFFICIENT_TOTAL_VRAM_NO_MODEL_LOAD")
    core.require(info["free_bytes"] >= MIN_FREE_VRAM, "INSUFFICIENT_FREE_VRAM_NO_MODEL_LOAD")
    core.require(info["bf16_supported"], "BF16_REQUIRED_NO_MODEL_LOAD")


def bind_tokenizer(tokenizer, root):
    observed_ids = {token: tokenizer.convert_tokens_to_ids(token) for token in SPECIAL_TOKEN_IDS}
    roundtrip = {token: tokenizer.convert_ids_to_tokens(value) if type(value) is int else None
                 for token, value in observed_ids.items()}
    binding = {"revision": MODEL_REVISION, "vocab_size": len(tokenizer),
               "special_token_ids": observed_ids, "roundtrip": roundtrip,
               "eos_token_id": tokenizer.eos_token_id, "pad_token_id": tokenizer.pad_token_id,
               "bos_token_id": tokenizer.bos_token_id,
               "chat_template_sha256": sha256(tokenizer.get_chat_template().encode()).hexdigest()}
    # Preserve actual values even when the following guard rejects them.
    write_json(Path(root) / ("tokenizer-observed-" + uuid.uuid4().hex + ".json"), binding)
    for token, expected in SPECIAL_TOKEN_IDS.items():
        actual = observed_ids[token]
        core.require(type(actual) is int and actual == expected and roundtrip[token] == token,
                     f"TOKENIZER_BINDING_MISMATCH:{token}:expected={expected}:observed={actual!r}:roundtrip={roundtrip[token]!r}")
    core.require(tokenizer.eos_token_id == observed_ids["<|im_end|>"],
                 f"TOKENIZER_EOS_DECLARATION_MISMATCH:observed={tokenizer.eos_token_id!r}")
    core.require(tokenizer.pad_token_id == observed_ids["<|endoftext|>"],
                 f"TOKENIZER_PAD_DECLARATION_MISMATCH:observed={tokenizer.pad_token_id!r}")
    return binding


def split_final_eos(tokens, eos):
    ended = bool(tokens) and tokens[-1] == eos
    return ended, tokens[:-1] if ended else tokens[:]


class HuggingFaceBackend:
    def __init__(self, root, deadline):
        # Only reached inside a Colab subprocess. Never instantiated by local checks.
        import torch
        import transformers
        from transformers import AutoTokenizer, Qwen3_5ForConditionalGeneration, GenerationConfig
        self.torch, self.transformers = torch, transformers
        free, total = torch.cuda.mem_get_info(0) if torch.cuda.is_available() else (0, 0)
        info = {"cuda_available": torch.cuda.is_available(), "total_bytes": total, "free_bytes": free,
                "bf16_supported": torch.cuda.is_available() and torch.cuda.is_bf16_supported(),
                "name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}
        write_json(root / ("hardware-" + uuid.uuid4().hex + ".json"), info)
        gpu_guard(info)
        core.require(time.monotonic() < deadline, "SETUP_TIME_LIMIT")
        for package, version in PINS.items():
            core.require(importlib.metadata.version(package) == version, "PACKAGE_PIN_MISMATCH:" + package)
        packages = {}
        for package in ("torch", "transformers", "accelerate", "tokenizers", "huggingface-hub", "safetensors", "numpy", "triton", "causal-conv1d", "flash-linear-attention", "fla-core", "kernels"):
            try:
                packages[package] = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                packages[package] = None
        environment = {"python": platform.python_version(), "packages": packages, "cuda": torch.version.cuda,
                       "cudnn": torch.backends.cudnn.version(), "gpu": info["name"], "total_vram": total,
                       "capability": list(torch.cuda.get_device_capability(0))}
        environment["driver"] = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"], text=True, timeout=10).strip()
        fix_or_compare(root / "environment.json", environment)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        print("Tokenizerを固定revisionから取得します。", flush=True)
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION, token=False, trust_remote_code=False)
        binding = bind_tokenizer(self.tokenizer, root)
        self.eos = binding["eos_token_id"]
        self.config = GenerationConfig(**GENERATION, eos_token_id=self.eos, pad_token_id=self.tokenizer.pad_token_id,
                                       bos_token_id=self.tokenizer.bos_token_id)
        fix_or_compare(root / "generation-config.json", self.config.to_dict())
        fix_or_compare(root / "tokenizer-binding.json", binding)
        core.require(time.monotonic() < deadline, "SETUP_TIME_LIMIT")
        print("Qwen3.5-27BをBF16でGPUへロードします（初回は約56GBの重み取得）。", flush=True)
        self.model = Qwen3_5ForConditionalGeneration.from_pretrained(
            MODEL_ID, revision=MODEL_REVISION, token=False, trust_remote_code=False, use_safetensors=True,
            dtype=torch.bfloat16, device_map={"": "cuda:0"}, attn_implementation="sdpa")
        self.model.eval()
        core.require(getattr(self.model.config, "_commit_hash", None) == MODEL_REVISION, "MODEL_REVISION_MISMATCH")
        devices = {str(parameter.device) for parameter in self.model.parameters()}
        core.require(devices == {"cuda:0"}, "UNEXPECTED_CPU_OR_DISK_OFFLOAD")
        dtype_counts = {}
        for parameter in self.model.parameters():
            name = str(parameter.dtype)
            dtype_counts[name] = dtype_counts.get(name, 0) + parameter.numel()
        fix_or_compare(root / "loaded-parameters.json", {"devices": sorted(devices), "parameter_dtype_counts": dtype_counts})
        model_config = self.model.config.to_dict()
        model_config.pop("_name_or_path", None)
        fix_or_compare(root / "model-config.json", model_config)
        print("ロード完了。固定割付の生成を開始します。", flush=True)

    def prepare(self, messages):
        rendered = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        core.require(rendered.endswith("<|im_start|>assistant\n<think>\n\n</think>\n\n"), "NONTHINKING_TEMPLATE_MISMATCH")
        tokens = self.tokenizer(rendered, add_special_tokens=False, truncation=False)["input_ids"]
        return {"rendered_prompt": rendered, "input_ids": tokens}

    def generate(self, prepared, seed, deadline):
        torch = self.torch
        from transformers import StoppingCriteria, StoppingCriteriaList
        class StopAtDeadline(StoppingCriteria):
            def __call__(self, input_ids, scores, **kwargs):
                return STOP_REQUESTED or time.monotonic() >= deadline
        self.transformers.set_seed(seed)
        ids = torch.tensor([prepared["input_ids"]], dtype=torch.long, device="cuda:0")
        mask = torch.ones_like(ids)
        torch.cuda.reset_peak_memory_stats(0)
        torch.cuda.synchronize()
        started = time.monotonic()
        with torch.inference_mode():
            output = self.model.generate(input_ids=ids, attention_mask=mask, generation_config=self.config,
                                         stopping_criteria=StoppingCriteriaList([StopAtDeadline()]), logits_to_keep=1)
        torch.cuda.synchronize()
        elapsed = time.monotonic() - started
        tokens = output[0, ids.shape[1]:].tolist()
        ended, answer_ids = split_final_eos(tokens, self.eos)
        finish = "EOS" if ended else "TIME_LIMIT" if STOP_REQUESTED or time.monotonic() >= deadline else "LENGTH"
        decode = lambda values: self.tokenizer.decode(values, skip_special_tokens=False, clean_up_tokenization_spaces=False)
        response = {"output_token_ids": tokens, "decoded_with_special_tokens": decode(tokens),
                    "answer_text": decode(answer_ids), "finish_reason": finish, "generation_seconds": elapsed,
                    "peak_vram_bytes": torch.cuda.max_memory_allocated(0), "seed": seed}
        del ids, mask, output
        return response


def worker_main(root, bundle_path, contract_path, seconds, audit_only=False):
    global STOP_REQUESTED
    root = Path(root)
    def stop_handler(signum, frame):
        global STOP_REQUESTED
        STOP_REQUESTED = True
    signal.signal(signal.SIGTERM, stop_handler)
    signal.signal(signal.SIGINT, stop_handler)
    core.require(platform.system() == "Linux" and Path("/content").is_dir(), "COLAB_ONLY_NO_MODEL_LOAD")
    bundle = read_json(bundle_path)
    slots = bundle["smoke_slots"]
    core.require(len(slots) == 8, "SMOKE_SCOPE_MISMATCH")
    core.validate_slots(slots)
    materials = bundle["smoke_materials"]
    pair = core.load_fixed_code(bundle)
    store = EvidenceStore(root, read_json(contract_path))
    deadline = time.monotonic() + seconds
    try:
        rows = run_routes(store, bundle, pair, materials, slots)
        if len(rows) < len(slots) and not audit_only:
            backend = HuggingFaceBackend(root, deadline)
            run_routes(store, bundle, pair, materials, slots, backend=backend, deadline=deadline)
    finally:
        rows = run_routes(store, bundle, pair, materials, slots)
        report = make_report(store, slots, rows)
        report_path = root / ("report-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json")
        write_json(report_path, report)
        print(json.dumps({"route_status": report["route_status"], "status_counts": report["status_counts"],
                          "attempted_generations": report["attempted_generations"],
                          "rough_1536_generation_hours": report["rough_1536_generation_hours"]}, ensure_ascii=False), flush=True)
        print("小試行で終了。本番は自動実行しません。", flush=True)
        print("報告ファイル:", report_path.name, flush=True)


if __name__ == "__main__":
    worker_main(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), audit_only=len(sys.argv) > 5 and sys.argv[5] == "AUDIT_ONLY")
