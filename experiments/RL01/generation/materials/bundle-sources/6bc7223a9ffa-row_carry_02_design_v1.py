"""ROW-CARRY-02 continuation from RC01 SELECT notes design and finite offline simulation; no transport/model code."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import random
from note_provenance_split_v1 import obj, enum, ID, REVISION, shape, parse, json_bytes

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "study2/designs/row-carry-02-20260920"
ROLES = ("A", "B")
REVISION = {"enum": [1, 2, 3, 4, "UNKNOWN"]}  # new protocol; old schema remains untouched


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f: f.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def other(role):
    return "B" if role == "A" else "A"


def memory_schemas():
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
COMMON = "revisionは同じobserverの再観測順です。AとBの番号同士やノート全体の新旧は比較しません。更新番号3/4は正式に付された手掛かりです。JSON以外を出力せず、schemaの全必須欄・A/B固定キーを守ってください。read_receiptは今回の各欄の根拠記録名で、ノート本文へ混ぜません。同じ値を支える記録が複数なら一件でも複数件でもよいですが、無関係な記録を加えず、元観測IDや昔の資料名を現在記録名の代わりにしないでください。確定した欄には現在参照を一件以上記録し、不明で根拠を挙げられない欄は空配列にしてください。"


def expected_memory(material, role, stage):
    shared = deepcopy(material["baseline_by_role"][role]["shared_note"]["coverage"])
    for r in ROLES if stage == "MERGE" else (role,):
        shared[r] = deepcopy(material["notices"][r])
    return {"private_note": {"customer": deepcopy(material["baseline_by_role"][role]["private_note"]["customer"]),
                              "coverage": deepcopy(material["notices"][role])},
            "shared_note": {"coverage": shared}}


def ideal_normal(material, slot):
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


def inspect_normal(raw, payload, stage):
    """Schema/membership gate; known source-content mistakes are deliberately untouched."""
    result = {"gate": "REJECT", "value": None, "shape_errors": [], "ref_errors": []}
    if raw is None: return result
    if len(raw) > 4096:
        result["shape_errors"] = ["OUTPUT_BYTES"]; return result
    try: value = parse(raw)
    except (ValueError,UnicodeError,RecursionError):
        result["shape_errors"] = ["JSON"]; return result
    result["value"] = value
    result["shape_errors"] = shape(value, memory_schemas()[stage])
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


def score_normal(material, slot, raw, payload):
    checked = inspect_normal(raw, payload, slot["stage"])
    value = checked["value"]
    stage, role = slot["stage"], slot["role"]
    strict, relaxed, parts = [], [], {}
    if stage != "PROBE":
        rules = memory_schemas()[stage]["properties"]["memory"]["properties"]
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
        truth = ideal_normal(material,slot)
        for k in ("mascot","channel"):
            observed = leaf(value,"decision",k)
            if shape(observed,memory_schemas()[stage]["properties"]["decision"]["properties"][k]): full = slim = None
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


def candidates(payload):
    """Only available records; no expected answer, revision ranking or owner filtering."""
    result = {}
    for record in payload['records']:
        alias, body = record['record_id'], record['body']
        if alias == 'PRIVATE':
            row = body['coverage'];result[(alias,row['observer'])] = row
        elif alias in ('LOCAL_GROUP','PARTNER_GROUP'):
            for owner,row in body['coverage'].items():result[(alias,owner)] = row
    return result



def schemas():
    result=memory_schemas();pointer=obj({'record_id':ID,'observer':enum('A','B')})
    result['MERGE']['properties']['memory']['properties']['shared_note']['properties']['coverage']=obj({'A':pointer,'B':pointer})
    return result


def prompt(stage):
    text=PROMPTS[stage]+'\n'+COMMON
    if stage=='MERGE':
        text+='\nPRIVATEのcoverageは本人の一行、LOCAL_GROUPとPARTNER_GROUPのcoverageはA/Bの各行です。'
        text+='\nshared_note.coverageのA/Bそれぞれには、採用する入力行の場所だけをrecord_idとobserverで指定してください。保存係はその場所の観測行全体を変更せず複製します。PRIVATEを指定する場合は実在する本人のobserverを指定します。観測の値・版・元IDをこの指定欄に書き足さないでください。private_noteとread_receiptは自分でschemaどおり出力してください。read_receiptの参照は選択後に保存される観測内容を根拠づける記録名です。'
    return text+'\n'+json.dumps(schemas()[stage],ensure_ascii=False,separators=(',',':'))+'\n'


def ideal(material,slot):
    value=ideal_normal(material,slot)
    if slot['stage']=='MERGE':
        role=slot['role'];value['memory']['shared_note']['coverage']={r:{'record_id':'LOCAL_GROUP' if r==role else 'PARTNER_GROUP','observer':r} for r in ROLES}
    return value


def evaluate(material,slot,raw,payload):
    stage=slot['stage']
    if stage!='MERGE':
        checked=inspect_normal(raw,payload,stage)
        return {'score':score_normal(material,slot,raw,payload),'gate':checked['gate'],'value':checked['value'],
                'normalized':checked['value'],'bindings':[],'selection_errors':[],'selection_shape_errors':[]}
    value=None;shape_errors=[];errors=[];bindings=[];normalized=None
    if raw is not None:
        if len(raw)>4096:shape_errors=['OUTPUT_BYTES']
        else:
            try:value=parse(raw)
            except (ValueError,UnicodeError,RecursionError):shape_errors=['JSON']
        if value is not None:
            shape_errors+=shape(value,schemas()['MERGE']);normalized=deepcopy(value);available=candidates(payload)
            for owner in ROLES:
                pointer=leaf(value,'memory','shared_note','coverage',owner)
                rule=schemas()['MERGE']['properties']['memory']['properties']['shared_note']['properties']['coverage']['properties'][owner]
                selected=None
                if not shape(pointer,rule):
                    selected=available.get((pointer['record_id'],pointer['observer']))
                    if selected is None:errors.append('SELECTION_NOT_CURRENT:'+owner)
                    bindings.append({'destination':owner,'selected':pointer,'body_sha256':sha256(json_bytes(selected)).hexdigest() if selected is not None else None})
                if type(leaf(normalized,'memory','shared_note','coverage')) is dict:normalized['memory']['shared_note']['coverage'][owner]=deepcopy(selected)
    norm_raw=json_bytes(normalized) if normalized is not None else None
    score=score_normal(material,slot,norm_raw,payload)
    score['strict']=tri_and([score['strict'],False if errors else None if shape_errors or raw is None else True])
    gate='PASS' if not shape_errors and not errors and inspect_normal(norm_raw,payload,stage)['gate']=='PASS' else 'REJECT'
    return {'score':score,'gate':gate,'value':value,'normalized':normalized,'bindings':bindings,'selection_errors':errors,'selection_shape_errors':shape_errors}


def build():
    source=ROOT/'study2/runs/row-carry-01-prepared-20260919'
    seals=[(ROOT/'study2/checks/row-carry-01-live-20260919/live-completion.json',ROOT,'6be2b1a238835450db0899db0029dc407c57609eaddbbe5e50b1b38099b93d20'),
           (source/'completion.json',source,'143a0453c80ddd8d642827526e4e10150d58f7d53f7b79196596cf0d46dabcda')]
    anchors=[]
    for path,base,digest in seals:
        assert sha256(path.read_bytes()).hexdigest()==digest
        files=json.loads(path.read_text())['files_sha256']
        for name,h in files.items():assert sha256((base/name).read_bytes()).hexdigest()==h,name
        anchors.append({'file':str(path.relative_to(ROOT)),'sha256':digest,'verified_files':len(files)})
    previous=json.loads((source/'configuration.json').read_text())['materials'];materials={};bindings=[]
    for index,(old_group,old) in enumerate(sorted(previous.items()),1):
        group=f'RC02-G{index:02}';baselines={}
        for role in ROLES:
            sid=f'{old_group}-SELECT-MERGE-{role}';p=source/'states'/(sid+'-note.json');archived=D/'source-notes'/p.name
            archived.parent.mkdir(parents=True,exist_ok=True)
            with archived.open('xb') as f:f.write(p.read_bytes())
            baselines[role]=json.loads(archived.read_text())
            assert baselines[role]['shared_note']['coverage']==old['notices']
            assert baselines[role]['private_note']['coverage']==old['notices'][role]
            bindings.append({'group':group,'role':role,'source_id':sid,'source':str(p.relative_to(ROOT)),'archived':str(archived.relative_to(ROOT)),'sha256':sha256(p.read_bytes()).hexdigest()})
        initial=old['final_channel'];target='PAPER' if initial=='DIGITAL' else 'DIGITAL';notices={}
        for role in ROLES:
            prior=baselines[role]['private_note']['coverage'];flexible=all(prior[k]=='ALL' for k in ('paper','digital'))
            notices[role]={'observer':role,'paper':'ALL' if not flexible or target=='PAPER' else 'NOT_ALL',
                'digital':'ALL' if not flexible or target=='DIGITAL' else 'NOT_ALL','origin_id':f'RC2G{index}{role}','revision':4}
            assert any(notices[role][k]!=prior[k] for k in ('paper','digital'))
        materials[group]={'group':group,'scene':old['scene'],'item':old['item'],'source_group':old_group,
            'baseline_by_role':baselines,'notices':notices,'initial_channel':initial,'final_channel':target}
    write(D/'materials.json',materials);write(D/'source-bindings.json',bindings);write(D/'source-seals.json',anchors)
    write(D/'response-schemas.json',schemas());write(D/'normalized-schemas.json',memory_schemas())
    for stage in ('UPDATE','MERGE','PROBE'):
        with (D/f'prompt-{stage.lower()}.txt').open('x') as f:f.write(prompt(stage))
    slots=[];rng=random.Random(2026092001)
    for stage in ('UPDATE','MERGE','PROBE'):
        batch=[]
        for i,g in enumerate(materials,1):
            for role in ROLES:
                deps=[] if stage=='UPDATE' else [slot_id(g,'UPDATE',r) for r in ROLES] if stage=='MERGE' else [slot_id(g,'MERGE',role)]
                batch.append({'id':slot_id(g,stage,role),'group':g,'stage':stage,'role':role,'dependencies':deps,
                              'group_order':'LOCAL_FIRST' if (i+(role=='B'))%2==0 else 'PARTNER_FIRST'})
        rng.shuffle(batch);slots+=batch
    write(D/'allocation.json',slots);states={};scores={};lengths=[]
    for s in slots:
        m=materials[s['group']];p=input_for(m,s,states);answer=ideal(m,s);ev=evaluate(m,s,json_bytes(answer),p);scores[s['id']]=ev['score']
        assert ev['gate']=='PASS' and ev['score']['strict'] is True
        write(D/'synthetic-perfect'/(s['id']+'.json'),{'kind':'SYNTHETIC_NOT_MODEL_DATA','slot':s,'input':p,'output':answer,'evaluation':ev})
        if s['stage']!='PROBE':states[s['id']]=deepcopy(ev['normalized']['memory'])
        if s['stage']=='UPDATE':
            write(D/'initial-inputs'/(s['id']+'.json'),p);lengths.append(len((prompt('UPDATE')+'\n資料JSON:\n'+json_bytes(p).decode()).encode()))
    write(D/'synthetic-perfect-summary.json',aggregate(slots,scores))
    write(D/'config.json',{'protocol':'ROW-CARRY-02','seed':2026092001,'planned_groups':4,'planned_slots':24,'initial_inputs':8,'dependent_slots':16,
        'source_notes':8,'source_condition':'RC01_SELECT','previous_revision':3,'new_revision':4,'prediction_threshold':.75,'primary_metric':'M_CONT','sensitivity_metric':'M_CONT_CONTENT',
        'UPDATE_contract':'FULL_RECORD','MERGE_shared_contract':'CURRENT_ROW_SELECTOR','PROBE_repeats':1,'max_physical_requests':28,'max_seconds':1800,
        'model_candidate':'gpt-5.6-luna','reasoning_candidate':'medium','retention_until':'2026-10-12T17:41:23+09:00','execution_authorized':False,'transport_connected':False,
        'new_model_calls':0,'new_auth_calls':0,'initial_input_text_bytes':{'sum':sum(lengths),'max':max(lengths)}})
    print(json.dumps({'groups':4,'slots':24,'source_notes':8,'initial_inputs':8,'initial_text_bytes':sum(lengths),'model_calls':0}))


if __name__=='__main__':build()
