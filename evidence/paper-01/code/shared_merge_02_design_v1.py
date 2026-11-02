"""SHARED-MERGE-02 continuation design and finite offline simulation; no transport/model code."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import random
from note_provenance_split_v1 import obj, enum, ID, REVISION, shape, parse, json_bytes

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "study2/designs/shared-merge-02-20260919"
ROLES = ("A", "B")
REVISION = {"enum": [1, 2, 3, "UNKNOWN"]}  # new protocol; old schema remains untouched


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def other(role):
    return "B" if role == "A" else "A"


def schemas():
    refs = {"type": "array", "items": ID, "maxItems": 3, "uniqueItems": True}
    origins = {"type": "array", "items": ID, "maxItems": 2, "uniqueItems": True}
    customer = obj({"subject": enum("A", "B", "UNKNOWN"), "animal": enum("DOG", "CAT", "UNKNOWN"), "origin_id": ID})
    cov = obj({"observer": enum("A", "B", "UNKNOWN"), "paper": enum("ALL", "NOT_ALL", "UNKNOWN"),
               "digital": enum("ALL", "NOT_ALL", "UNKNOWN"), "origin_id": ID, "revision": REVISION})
    memory = obj({"private_note": obj({"customer": customer, "coverage": cov}),
                  "shared_note": obj({"coverage": obj({"A": cov, "B": cov})})})
    receipt = obj({"private_customer_refs": refs, "private_coverage_refs": refs,
                   "shared_coverage_refs": obj({"A": refs, "B": refs})})
    save = obj({"memory": memory, "read_receipt": receipt})
    probe = obj({"decision": obj({"mascot": enum("DOG", "CAT", "UNKNOWN"), "channel": enum("PAPER", "DIGITAL", "UNKNOWN")}),
                 "read_receipt": obj({"mascot_record_refs": refs, "channel_record_refs": refs}),
                 "origin_ids": obj({"mascot": origins, "channel": origins})})
    return {"UPDATE": save, "MERGE": deepcopy(save), "PROBE": probe}


PROMPTS = {
    "UPDATE": "あなたは架空の作業担当者です。PRIVATEは自分の保存済み個別ノート、BASE_GROUPは以前の共同ノート、NOTICEはあなたの担当範囲だけの正式な最新再確認です。担当客は変わりません。NOTICEで自分の観測を更新し、共同ノートの自分行も更新し、相手行は入力にある情報を保ってください。memory.private_noteとmemory.shared_noteを保存してください。共同ノートにはA/B別の観測だけを置き、案内の結論やノート全体の版番号は足さないでください。",
    "MERGE": "あなたは架空の作業担当者です。PRIVATEは自分の個別ノート、LOCAL_GROUPは自分が保存した共同草稿、PARTNER_GROUPは相手から届いた共同草稿です。各草稿には自分が新しく確認した行と、相手の昔の行が混在し得ます。担当客を保ち、自分の最新観測を個別ノートに保ち、共同ノートはA/Bそれぞれについて入力から最も新しい観測を選んで統合してください。一冊全体の到着順ではなく、同じobserver内のrevisionで判断してください。他人の担当客を推測して足さないでください。",
    "PROBE": "あなたは架空の作業担当者です。今回のPRIVATEとGROUPだけを根拠に仕事を決めてください。自分の担当客が希望した犬猫にmascotを合わせてください。案内方法はA/Bの両方でALLと確認できる方法がちょうど一つならPAPERまたはDIGITAL、0個または2個ならUNKNOWNとしてください。過去に出した結論を推測しないでください。根拠の現在記録名と元観測IDを分けて記録してください。"
}
COMMON = "revisionは同じobserverの再観測順です。AとBの番号同士やノート全体の新旧は比較しません。更新番号2/3は正式に付された手掛かりです。JSON以外を出力せず、schemaの全必須欄・A/B固定キーを守ってください。read_receiptは今回の各欄の根拠記録名で、ノート本文へ混ぜません。同じ値を支える記録が複数なら一件でも複数件でもよいですが、無関係な記録を加えず、元観測IDや昔の資料名を現在記録名の代わりにしないでください。確定した欄には現在参照を一件以上記録し、不明で根拠を挙げられない欄は空配列にしてください。"


def expected_memory(material, role, stage):
    shared = deepcopy(material["baseline_by_role"][role]["shared_note"]["coverage"])
    for r in ROLES if stage == "MERGE" else (role,):
        shared[r] = deepcopy(material["notices"][r])
    return {"private_note": {"customer": deepcopy(material["baseline_by_role"][role]["private_note"]["customer"]),
                              "coverage": deepcopy(material["notices"][role])},
            "shared_note": {"coverage": shared}}


def ideal(material, slot):
    role, stage = slot["role"], slot["stage"]
    if stage == "PROBE":
        return {"decision": {"mascot": material["baseline_by_role"][role]["private_note"]["customer"]["animal"], "channel": material["final_channel"]},
                "read_receipt": {"mascot_record_refs": ["PRIVATE"], "channel_record_refs": ["GROUP"]},
                "origin_ids": {"mascot": [material["baseline_by_role"][role]["private_note"]["customer"]["origin_id"]],
                               "channel": [material["notices"][r]["origin_id"] for r in ROLES]}}
    return {"memory": expected_memory(material, role, stage), "read_receipt": {
        "private_customer_refs": ["PRIVATE"], "private_coverage_refs": ["NOTICE" if stage == "UPDATE" else "PRIVATE"],
        "shared_coverage_refs": {r: (["NOTICE"] if r == role else ["BASE_GROUP"]) if stage == "UPDATE"
                                  else (["LOCAL_GROUP"] if r == role else ["PARTNER_GROUP"]) for r in ROLES}}}


def slot_id(group, stage, role, rep=None):
    return f"{group}-{stage}-{role}" + (f"-R{rep}" if rep else "")


def input_for(material, slot, memories):
    """Pure projection from actual parent states, never from an expected answer."""
    role, stage, g = slot["role"], slot["stage"], slot["group"]
    def rec(alias, body):
        return {"record_id": alias, "body": deepcopy(body)}
    if stage == "UPDATE":
        records = [rec("PRIVATE", material["baseline_by_role"][role]["private_note"]), rec("BASE_GROUP", material["baseline_by_role"][role]["shared_note"]), rec("NOTICE", material["notices"][role])]
    elif stage == "MERGE":
        mine = memories[slot_id(g, "UPDATE", role)]
        theirs = memories[slot_id(g, "UPDATE", other(role))]
        groups = [rec("LOCAL_GROUP", mine["shared_note"]), rec("PARTNER_GROUP", theirs["shared_note"])]
        if slot["group_order"] == "PARTNER_FIRST": groups.reverse()
        records = [rec("PRIVATE", mine["private_note"])] + groups
    else:
        mine = memories[slot_id(g, "MERGE", role)]
        records = [rec("PRIVATE", mine["private_note"]), rec("GROUP", mine["shared_note"])]
    return {"scene": material["scene"], "item": material["item"], "holder": role, "records": records}


def leaf(value, *keys):
    for k in keys:
        if type(value) is not dict or k not in value: return None
        value = value[k]
    return value


def reference_fields(value, stage):
    if stage == "PROBE":
        return [(leaf(value,"read_receipt",f"{k}_record_refs"), leaf(value,"decision",k) not in (None,"UNKNOWN")) for k in ("mascot","channel")]
    pairs = [(leaf(value,"read_receipt","private_customer_refs"), leaf(value,"memory","private_note","customer")),
             (leaf(value,"read_receipt","private_coverage_refs"), leaf(value,"memory","private_note","coverage"))]
    pairs += [(leaf(value,"read_receipt","shared_coverage_refs",r), leaf(value,"memory","shared_note","coverage",r)) for r in ROLES]
    return [(refs, type(component) is dict and all(v != "UNKNOWN" for v in component.values())) for refs,component in pairs]


def inspect(raw, payload, stage):
    """Schema/membership gate; known source-content mistakes are deliberately untouched."""
    result = {"gate": "REJECT", "value": None, "shape_errors": [], "ref_errors": []}
    if raw is None: return result
    if len(raw) > 4096:
        result["shape_errors"] = ["OUTPUT_BYTES"]; return result
    try: value = parse(raw)
    except (ValueError,UnicodeError,RecursionError):
        result["shape_errors"] = ["JSON"]; return result
    result["value"] = value
    result["shape_errors"] = shape(value, schemas()[stage])
    visible = {r["record_id"] for r in payload["records"]}
    assert len(visible) == len(payload["records"])
    for refs, known in reference_fields(value, stage):
        if type(refs) is list and all(type(x) is str for x in refs):
            if known and not refs: result["ref_errors"].append("KNOWN_EMPTY")
            for ref in refs:
                if ref not in visible: result["ref_errors"].append("NOT_CURRENT:"+ref)
    if not result["shape_errors"] and not result["ref_errors"]: result["gate"] = "PASS"
    return result


def tri_and(values):
    values = list(values)
    return False if False in values else (None if None in values else True)


def content(value):
    if type(value) is dict: return {k:content(v) for k,v in value.items() if k != "origin_id"}
    return value


def source_component(record, kind, owner):
    alias, body = record["record_id"], record["body"]
    if kind == "customer": return body.get("customer") if alias == "PRIVATE" else None
    if alias == "NOTICE": return body
    if alias == "PRIVATE": return body.get("coverage")
    return leaf(body,"coverage",owner)


def support(refs, value, payload, kind, owner):
    if type(refs) is not list or any(type(r) is not str for r in refs): return None
    if not refs: return False
    records = {r["record_id"]:r for r in payload["records"]}
    return all(ref in records and source_component(records[ref],kind,owner) == value for ref in refs)


def score(material, slot, raw, payload):
    checked = inspect(raw, payload, slot["stage"])
    value = checked["value"]
    stage, role = slot["stage"], slot["role"]
    strict, relaxed, parts = [], [], {}
    if stage != "PROBE":
        rules = schemas()[stage]["properties"]["memory"]["properties"]
        truth = expected_memory(material,role,stage)
        fields = [("customer",role,("private_note","customer"),("private_customer_refs",),rules["private_note"]["properties"]["customer"]),
                  ("coverage",role,("private_note","coverage"),("private_coverage_refs",),rules["private_note"]["properties"]["coverage"])]
        fields += [("coverage",r,("shared_note","coverage",r),("shared_coverage_refs",r),rules["shared_note"]["properties"]["coverage"]["properties"][r]) for r in ROLES]
        for kind,owner,path,rpath,rule in fields:
            observed = leaf(value,"memory",*path); expected = leaf(truth,*path)
            if shape(observed,rule): full = slim = None
            else:
                slim = content(observed) == content(expected)
                full = observed == expected and support(leaf(value,"read_receipt",*rpath),observed,payload,kind,owner)
            strict.append(full); relaxed.append(slim); parts[".".join(path)] = {"strict":full,"content":slim}
    else:
        truth = ideal(material,slot)
        for k in ("mascot","channel"):
            observed = leaf(value,"decision",k)
            if shape(observed,schemas()[stage]["properties"]["decision"]["properties"][k]): full = slim = None
            else:
                slim = observed == truth["decision"][k]
                refs = leaf(value,"read_receipt",k+"_record_refs")
                origins = leaf(value,"origin_ids",k)
                readable = type(refs) is list and all(type(x) is str for x in refs) and type(origins) is list and all(type(x) is str for x in origins)
                provenance = (refs == truth["read_receipt"][k+"_record_refs"] and set(origins) == set(truth["origin_ids"][k]) and len(origins) == len(set(origins))) if readable else None
                bodies = {r["record_id"]:r["body"] for r in payload["records"]}
                supported = (bodies["PRIVATE"]["customer"] == material["baseline_by_role"][role]["private_note"]["customer"]) if k == "mascot" else (bodies["GROUP"]["coverage"] == material["notices"])
                full = tri_and([slim,provenance,supported])
            strict.append(full); relaxed.append(slim);parts[k] = {"strict":full,"content":slim}
    strict += [None if checked["shape_errors"] or value is None else True,
               False if checked["ref_errors"] else (None if value is None else True)]
    return {"strict":tri_and(strict),"content":tri_and(relaxed),"parts":parts,"gate":checked["gate"],
            "shape_errors":checked["shape_errors"],"ref_errors":checked["ref_errors"]}


def aggregate(slots, results):
    groups = sorted({s["group"] for s in slots});out = {}
    for mode in ("strict","content"):
        by_group = {g:tri_and(results.get(s["id"],{}).get(mode) for s in slots if s["group"]==g) for g in groups}
        vals = list(by_group.values());lo=vals.count(True)/4;hi=(vals.count(True)+vals.count(None))/4
        out[mode] = {"groups":by_group,"bounds":[lo,hi]}
    lo,hi=out["strict"]["bounds"]
    out["prediction"] = "MET_IN_FIXED_SAMPLE" if lo>=.75 else "NOT_MET_IN_FIXED_SAMPLE" if hi<.75 else "INCONCLUSIVE"
    return out


def build():
    source = ROOT / 'study2/runs/shared-merge-01-prepared-20260919'
    result_seal = ROOT / 'study2/checks/shared-merge-01-live-20260919/live-completion.json'
    seals = [(result_seal, ROOT, '5c7f1620ed994b2e5f572558c2260a868b93262fcea4c51e2d42c03e11299214'),
             (source/'completion.json', source, 'f8026b6effa5362dbb77db56bbf4eb15bd0aaf3669e1c6ddfa2713f549ea74ec')]
    anchors = []
    for file, base, digest in seals:
        assert sha256(file.read_bytes()).hexdigest() == digest
        manifest = json.loads(file.read_text())['files_sha256']
        for name, expected in manifest.items():
            assert sha256((base/name).read_bytes()).hexdigest() == expected, name
        anchors.append({'file':str(file.relative_to(ROOT)), 'sha256':digest, 'verified_files':len(manifest)})
    previous = json.loads((source/'configuration.json').read_text())['materials']
    materials, bindings = {}, []
    for idx, old_group in enumerate(sorted(previous), 1):
        old = previous[old_group]; group = f'SM02-G{idx:02}'
        baselines = {}
        for role in ROLES:
            path = source/'states'/f'{old_group}-MERGE-{role}-note.json'
            archived = D/'source-notes'/path.name
            archived.parent.mkdir(parents=True, exist_ok=True)
            with archived.open('xb') as out: out.write(path.read_bytes())
            baselines[role] = json.loads(archived.read_text())
            assert set(baselines[role]) == {'private_note','shared_note'}
            assert baselines[role]['private_note']['coverage'] == old['notices'][role]
            assert baselines[role]['shared_note']['coverage'] == old['notices']
            bindings.append({'group':group,'role':role,'source_id':f'{old_group}-MERGE-{role}',
                             'source':str(path.relative_to(ROOT)), 'archived':str(archived.relative_to(ROOT)),
                             'sha256':sha256(path.read_bytes()).hexdigest()})
        initial = old['final_channel']; target = 'PAPER' if initial == 'DIGITAL' else 'DIGITAL'
        notices = {}
        for role in ROLES:
            prior = baselines[role]['private_note']['coverage']
            was_flexible = all(prior[k] == 'ALL' for k in ('paper','digital'))
            notices[role] = {'observer':role,
                            'paper':'ALL' if not was_flexible or target == 'PAPER' else 'NOT_ALL',
                            'digital':'ALL' if not was_flexible or target == 'DIGITAL' else 'NOT_ALL',
                            'origin_id':f'SM2G{idx}{role}', 'revision':3}
            assert any(notices[role][k] != prior[k] for k in ('paper','digital'))
        materials[group] = {'group':group,'scene':old['scene'],'item':old['item'],
                            'source_group':old_group,'original_source_group':old['source_group'],
                            'baseline_by_role':baselines,'notices':notices,
                            'initial_channel':initial,'final_channel':target}
    write(D/'materials.json',materials);write(D/'source-bindings.json',bindings)
    write(D/'source-seals.json',anchors);write(D/'response-schemas.json',schemas())
    for stage,prompt in PROMPTS.items():
        with (D/f'prompt-{stage.lower()}.txt').open('x') as out:
            out.write(prompt+'\n'+COMMON+'\n'+json.dumps(schemas()[stage],ensure_ascii=False,separators=(',',':'))+'\n')
    slots=[];rng=random.Random(2026091904)
    for stage,rep in [('UPDATE',None),('MERGE',None),('PROBE',1),('PROBE',2)]:
        batch=[]
        for i,g in enumerate(materials,1):
            for role in ROLES:
                deps=[] if stage=='UPDATE' else [slot_id(g,'UPDATE',r) for r in ROLES] if stage=='MERGE' else [slot_id(g,'MERGE',role)]
                batch.append({'id':slot_id(g,stage,role,rep),'group':g,'stage':stage,'role':role,'rep':rep,
                              'dependencies':deps,'group_order':'LOCAL_FIRST' if (i+(role=='B'))%2==0 else 'PARTNER_FIRST'})
        rng.shuffle(batch);slots+=batch
    write(D/'allocation.json',slots)
    memories={};results={}
    for s in slots:
        m=materials[s['group']];payload=input_for(m,s,memories);answer=ideal(m,s)
        results[s['id']]=score(m,s,json_bytes(answer),payload)
        write(D/'synthetic-perfect'/(s['id']+'.json'),{'kind':'SYNTHETIC_NOT_MODEL_DATA','slot':s,'input':payload,'output':answer,'score':results[s['id']]})
        if s['stage']!='PROBE':memories[s['id']]=answer['memory']
        if s['stage']=='UPDATE':write(D/'initial-inputs'/(s['id']+'.json'),payload)
    write(D/'synthetic-perfect-summary.json',aggregate(slots,results))
    write(D/'config.json',{'protocol':'SHARED-MERGE-02','cycle':'second_update_exchange_cycle_on_same_groups',
        'seed':2026091904,'planned_groups':4,'planned_slots':32,'initial_inputs':8,'dependent_slots':24,
        'source_notes':8,'previous_revision':2,'new_revision':3,'prediction_threshold':.75,
        'primary_metric':'M_PAIR_2','sensitivity_metric':'M_PAIR_2_CONTENT',
        'max_physical_requests':36,'max_seconds':1800,'model_candidate':'gpt-5.6-luna','reasoning_candidate':'medium',
        'execution_authorized':False,'transport_connected':False,'new_model_calls':0,'auth_calls':0,
        'retention_until':'2026-10-12T17:41:23+09:00'})
    print(json.dumps({'groups':4,'slots':32,'source_notes':8,'initial_inputs':8,'new_model_calls':0}))


if __name__ == '__main__':build()
