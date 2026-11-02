"""RC02 evidence reader. Does not import the producer, its parser, or its scorer."""
from pathlib import Path
from collections import Counter
import hashlib,json,sys,re

read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
canon=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
digest=lambda x:hashlib.sha256(canon(x)).hexdigest()


import audit_row_carry_02_design_v1 as independent
import audit_shared_merge_02_v1 as previous_reader
get,valid,tri=previous_reader.get,previous_reader.valid,previous_reader.tri


def decode(raw,s,payload,material,schemas,norm_schemas):
    payload=payload or {'records':[]};stage=s['stage']
    out=independent.check_response(material,s,raw,payload,norm_schemas[stage],schemas[stage])
    value,normalized,gate=out['value'],out['normalized'],out['gate']
    parts=previous_reader.decode(canon(normalized).decode() if normalized is not None else None,stage,payload,norm_schemas[stage])['valid_components']
    status='VALID' if gate=='PASS' else 'SELECTION_REJECT' if out['selection_errors'] else 'STRUCTURAL_MISSING' if not valid(value,schemas[stage]) else 'REFERENCE_REJECT'
    return {**out,'valid_components':parts,'status':status,'continuable':status=='VALID' and stage!='PROBE'}


def project(material,s,notes):
    return previous_reader.project(material,s,notes)


def proof(s,v,payload):
    return {'source_id':s['id'],'stage':s['stage'],'input_sha256':digest(payload),
            'raw_value_sha256':digest(v['value']),'normalized_value_sha256':digest(v['normalized']),
            'rows':v['bindings'],'gate':v['gate'],'method':'LITERAL_CURRENT_ROW' if s['stage']=='MERGE' else 'IDENTITY','semantic_repair':False}


def sse_text(raw):
    events=[json.loads(x[6:]) for x in raw.splitlines() if x.startswith(b'data: ') and x!=b'data: [DONE]']
    ends=[e['response'] for e in events if e.get('type')=='response.completed'];assert len(ends)==1 and ends[0]['status']=='completed'
    items=[e['item'] for e in sorted([e for e in events if e.get('type')=='response.output_item.done'],key=lambda e:e['output_index'])]
    assert all(i['type'] in ('reasoning','message') for i in items)
    msgs=[x for x in items if x['type']=='message'];assert len(msgs)==1 and msgs[0]['role']=='assistant'
    assert len(msgs[0]['content'])==1 and msgs[0]['content'][0]['type']=='output_text'
    text=msgs[0]['content'][0]['text']
    assert ''.join(e['delta'] for e in events if e.get('type')=='response.output_text.delta')==text
    assert [e['text'] for e in events if e.get('type')=='response.output_text.done']==[text]
    assert [e['part']['text'] for e in events if e.get('type')=='response.content_part.done']==[text]
    if ends[0].get('output'):assert ends[0]['output']==items
    return text


def audit(directory):
    root=Path(directory);c=read(root/'configuration.json');n=0
    def ck(x,why):
        nonlocal n
        if not x:raise AssertionError(why)
        n+=1
    ck(read(root/'configuration-seal.json')=={'sha256':sha(root/'configuration.json')},'configuration seal')
    for f,h in c['frozen_sha256'].items():ck(sha(root/f)==h,'frozen '+f)
    ck(c['protocol']=='ROW-CARRY-02' and c['version']=='row-carry-02-v0.1','protocol')
    ck(c['limits']==dict(logical_requests=24,physical_requests=28,overload_retries=4,per_logical_attempts=2,active_seconds=1800,reserve_seconds=200,response_utf8_bytes=4096,input_text_utf8_bytes=32768),'limits')
    ck(c['retention_expires_at']=='2026-10-12T17:41:23+09:00','retention')
    ck(c['egress']['destination']=='https://chatgpt.com/backend-api/codex/responses','destination')
    for key,name in [('root_inputs_sha256','root-inputs.json'),('constructor_sha256','row_carry_02_design_v1.py'),('runtime_sha256','row_carry_02_v1.py'),('materials_sha256','materials.json'),('source_bindings_sha256','source-bindings.json'),('schema_file_sha256','response-schemas.json')]:ck(c['egress'][key]==sha(root/'frozen'/name),'egress binding')
    specs=c['allocation'];materials=c['materials'];schema=read(root/'frozen/response-schemas.json');roots=read(root/'frozen/root-inputs.json');norm_schema=read(root/'frozen/normalized-schemas.json')
    ck(specs==read(root/'frozen/allocation.json') and materials==read(root/'frozen/materials.json'),'design inputs')
    ck(len(specs)==len({s['id'] for s in specs})==24 and len(materials)==4,'inventory')
    ck(Counter(s['stage'] for s in specs)=={'UPDATE':8,'MERGE':8,'PROBE':8},'stages')
    ck(len(list((root/'fixed-inputs').glob('*.json')))==8,'fixed inputs')
    ck(sha(root/'frozen/design-completion.json')==c['design_completion_sha256'],'design seal')
    bindings=read(root/'frozen/source-bindings.json')
    ck(len(bindings)==8 and {(b['group'],b['role']) for b in bindings}=={(g,r) for g in materials for r in ('A','B')},'eight role-specific sources')
    for b in bindings:
        f=root/'frozen/source-notes'/Path(b['source']).name
        ck(sha(f)==b['sha256'],'source original')
        ck(read(f)==materials[b['group']]['baseline_by_role'][b['role']],'whole own source note')
        ck(Path(b['source']).name==materials[b['group']]['source_group']+'-SELECT-MERGE-'+b['role']+'-note.json','source role identity')
    def pp(s,p):
        name='prompt-'+s['stage'].lower()+'.txt'
        return {'instructions':(root/'frozen'/name).read_text(),'input':'\n資料JSON:\n'+canon(p).decode()}
    def check_wire(path,p):
        v=read(path);ck(set(v)=={'model','input','tools','tool_choice','parallel_tool_calls','reasoning','store','stream'},'wire keys')
        ck(v['model']=='gpt-5.6-luna' and v['tools']==[] and v['tool_choice']=='none' and v['parallel_tool_calls'] is False and v['reasoning']=={'effort':'medium'} and v['store'] is False and v['stream'] is True,'wire options')
        ck(v['input']==[{'type':'message','role':'developer','content':[{'type':'input_text','text':p['instructions']}]},{'type':'message','role':'user','content':[{'type':'input_text','text':p['input']}]}],'wire text')
    for s in specs:
        if s['stage']=='UPDATE':
            p=pp(s,project(materials[s['group']],s,{}));ck(roots[s['id']]==p['instructions']+p['input'],'root text');check_wire(root/'fixed-inputs'/(s['id']+'.json'),p)
    if not (root/'acquisition-closure.json').exists():
        ck(not (root/'execution-start.json').exists(),'not started')
        ck(not any((root/'dispatch').iterdir()) and not any((root/'requests').iterdir()),'no requests')
        return {'status':'PASS','checks':n,'scope':'Prepared evidence only; no fresh authentication','authorization_present':(root/'authorization.json').exists()}
    report=read(root/'analysis.json');closure=read(root/'acquisition-closure.json');notes={};parsed={};scored={};wires={};inputs={};statuses={}
    for s in specs:
        sid=s['id'];m=materials[s['group']];rawp=root/'generations'/(sid+'-raw.txt');saved=root/'generations'/(sid+'-parsed.json');req=root/'requests'/(sid+'.json');payload=None
        if req.exists():
            ck(all(p in notes for p in s['dependencies']),'required parent exists')
            payload=project(m,s,notes);p=pp(s,payload);inputs[sid]=payload;wires[sid]=req.read_bytes()
            ck(read(root/'states'/(sid+'-incoming.json'))==payload,'actual parent projection');ck(read(root/'requests'/(sid+'-packet.json'))==p,'packet');check_wire(req,p)
            b=read(root/'requests'/(sid+'-binding.json'))
            ck(b['source_id']==sid and b['parents']==s['dependencies'] and b['stage']==s['stage'] and b['role']==s['role'],'input identity')
            ck(b['configuration_sha256']==sha(root/'configuration.json') and b['request_sha256']==sha(req) and b['incoming_sha256']==sha(root/'states'/(sid+'-incoming.json')),'input hashes')
            ck(b['input_text_utf8_bytes']==len((p['instructions']+p['input']).encode())<=32768,'input size')
            for parent in s['dependencies']:
                ck(b['parent_bindings'][parent]=={'parsed_sha256':sha(root/'generations'/(parent+'-parsed.json')),'raw_sha256':sha(root/'generations'/(parent+'-raw.txt')),'note_sha256':sha(root/'states'/(parent+'-note.json')),'receipt_sha256':sha(root/'receipts'/(parent+'.json')),'materialization_sha256':sha(root/'materializations'/(parent+'.json'))},'parent hash binding')
        raw=rawp.read_text() if rawp.exists() else None;v=decode(raw,s,payload,m,schema,norm_schema);parsed[sid]=v
        if saved.exists():
            x=read(saved);statuses[sid]=x['status']
            if rawp.exists():
                for key in ('value','normalized','gate','status','continuable','valid_components'):ck(x[key]==v[key],'parsed '+key)
                ck(read(root/'states'/(sid+'-components.json'))==v['valid_components'],'partial components')
                receipt=read(root/'receipts'/(sid+'.json'));ck(receipt['source_id']==sid and receipt['input_sha256']==digest(payload),'receipt scope')
                rr=get(v['value'],'read_receipt');ck(receipt['declared_read_receipt']==rr,'raw declared receipt')
                expected=[];visible={r['record_id']:r['body'] for r in payload['records']}
                for field,refs in (rr.items() if type(rr) is dict else []):
                    fields=[(field+'.'+k,a) for k,a in refs.items()] if field=='shared_coverage_refs' and type(refs) is dict else [(field,refs)]
                    for field,refs in fields:
                        if type(refs) is not list or any(type(x) is not str for x in refs):expected.append({'field':field,'status':'UNREADABLE','declared':refs});continue
                        for alias in refs:expected.append({'field':field,'record_id':alias,'status':'PRESENT' if alias in visible else 'NOT_CURRENT','body_sha256':digest(visible[alias]) if alias in visible else None})
                ck(receipt['claims']==expected,'receipt claims and referenced bodies')
                tid=read(root/'logical'/(sid+'-completion.json'))['physical_id']
                ck(sse_text((root/'sender'/tid/'results'/(tid+'-upstream.raw')).read_bytes())==raw,'original SSE to raw')
            elif x['status']=='DEPENDENCY_UNISSUED':
                ck(not req.exists() and x['blocked_parents']==[p for p in s['dependencies'] if not parsed[p]['continuable']],'dependency stop')
            else:ck(x['status']=='TRANSPORT_FAILURE' and req.exists(),'transport failure')
        else:statuses[sid]='UNISSUED'
        if v['continuable']:
            notes[sid]=v['normalized']['memory'];ck(read(root/'states'/(sid+'-note.json'))==notes[sid],'memory saved verbatim')
            ck('read_receipt' not in json.dumps(notes[sid]),'receipt not in memory')
        else:ck(not (root/'states'/(sid+'-note.json')).exists(),'rejected/probe memory not forwarded')
        if rawp.exists() and s['stage']!='PROBE':ck(read(root/'materializations'/(sid+'.json'))==proof(s,v,payload),'literal row materialization proof')
        scored[sid]=v['score']
        for k in ('strict','content','parts'):ck(report['slot_scores'][sid][k]==scored[sid][k],'slot score '+k)
    agg={}
    for mode,key in [('strict','M_CONT'),('content','M_CONT_CONTENT')]:
        groups={g:tri(scored[s['id']][mode] for s in specs if s['group']==g) for g in materials}
        vals=list(groups.values());bounds=[vals.count(True)/4,(vals.count(True)+vals.count(None))/4]
        agg[mode]={'groups':groups,'bounds':bounds};ck(report[key]==bounds,'fixed denominator '+mode)
    lo,hi=agg['strict']['bounds'];prediction='MET_IN_FIXED_SAMPLE' if lo>=.75 else 'NOT_MET_IN_FIXED_SAMPLE' if hi<.75 else 'INCONCLUSIVE'
    agg['prediction']=prediction;ck(report['aggregate']==agg,'entire independent aggregate');ck(report['prediction_status']==prediction,'prediction')
    def counts(vals):
        vals=list(vals);return {'true':vals.count(True),'false':vals.count(False),'unknown':vals.count(None),'planned':len(vals)}
    ck(report['status_counts']==dict(Counter(statuses.values())),'status counts')
    for stage in ['UPDATE','MERGE','PROBE']:
        ss=[s for s in specs if s['stage']==stage]
        for mode in ['strict','content']:ck(report['stages'][stage][mode]==counts(scored[s['id']][mode] for s in ss),'stage count')
        for role in ['A','B']:
            for part,row in report['components_by_stage_role'][stage+'-'+role].items():
                for mode in ['strict','content']:ck(row[mode]==counts(scored[s['id']]['parts'][part][mode] for s in ss if s['role']==role),'component count')
    expected_rows=[];final=[]
    for s in specs:
        v=parsed[s['id']]['normalized'];m=materials[s['group']]
        if s['stage']=='PROBE':
            channel=get(v,'decision','channel')
            final.append({'id':s['id'],'channel':channel,'UNKNOWN':channel=='UNKNOWN' if channel is not None else None,
                          'correct_channel':scored[s['id']]['parts']['channel']['content'],'correct_customer':scored[s['id']]['parts']['mascot']['content']})
        elif s['stage']=='MERGE':
            candidates=[]
            for record in inputs.get(s['id'],{}).get('records',[]):
                candidates+= [record['body']['coverage']] if record['record_id']=='PRIVATE' else list(record['body']['coverage'].values())
            for who in ['A','B']:
                row=get(v,'memory','shared_note','coverage',who);seen=valid(row,norm_schema['MERGE']['properties']['memory']['properties']['shared_note']['properties']['coverage']['properties'][who])
                expected_rows.append({'id':s['id'],'observer':who,'existing_whole_row':row in candidates if seen else None,
                    'latest_full':row==m['notices'][who] if seen else None,'wrong_observer':row['observer']!=who if seen else None,'old_revision':row['revision'] in (1,2,3) if seen else None})
    ck(report['merge_observation_details']==expected_rows,'whole row membership and meaning kept separate');ck(report['final_decisions']==final,'final decisions')
    for name in ['update','merge','probe']:
        path=root/'stages'/(name+'-closure.json')
        if path.exists():
            z=read(path)
            for f,h in z['files_sha256'].items():ck(sha(root/f)==h,'stage hash')
            ck(z['outcomes']=={s['id']:statuses[s['id']] for s in specs if s['stage'].lower()==name},'stage outcomes')
    launches=sorted((root/'dispatch').glob('*-launch.json'),key=lambda p:read(p)['sequence']);retries=0;us=[];order=[]
    positions={s['id']:i for i,s in enumerate(specs)}
    for i,path in enumerate(launches,1):
        l=read(path);sid=l['source_id'];pid=path.name.removesuffix('-launch.json');phase=root/'sender'/pid;order.append(positions[sid])
        ck(l['sequence']==i and 1<=l['ordinal']<=2 and l['remaining_seconds']>200,'budget')
        ck(l['request_sha256']==sha(root/'requests'/(sid+'.json'))==sha(phase/'frozen/request.json'),'same sent bytes')
        ck(l['configuration_sha256']==sha(phase/'configuration.json'),'child configuration')
        for f,h in read(phase/'configuration.json')['frozen_sha256'].items():ck(sha(phase/f)==h,'sender file')
        sent=phase/'results'/(pid+'-sent.json')
        if sent.exists():ck(sha(sent)==l['request_sha256'],'actual sent')
        if l['ordinal']>1:
            retries+=1;prior=sid+'-p1';ck(read(root/'dispatch'/(prior+'-receipt.json'))['overload_eligible'] and read(root/'dispatch'/(prior+'-decision.json'))['action']=='RETRY','eligible resend')
        ufile=root/'dispatch'/(pid+'-usage.json')
        if ufile.exists():
            u=read(ufile);us.append(u);raw=(phase/'results'/(pid+'-upstream.raw')).read_bytes();ev=[json.loads(x[6:]) for x in raw.splitlines() if x.startswith(b'data: ') and x!=b'data: [DONE]']
            ends=[e for e in ev if e.get('type') in ('response.completed','response.failed')];reported=ends[0].get('response',{}).get('usage') if len(ends)==1 else None
            if reported is None:ck(u=={'status':'UNAVAILABLE','reported':None,'totals':None},'missing usage')
            else:
                keys=('input_tokens','output_tokens','total_tokens');okay=type(reported) is dict and all(type(reported.get(k)) is int and reported[k]>=0 for k in keys) and reported['total_tokens']==reported['input_tokens']+reported['output_tokens']
                ck(u=={'status':'AVAILABLE' if okay else 'INVALID','reported':reported,'totals':{k:reported[k] for k in keys} if okay else None},'reported usage')
    ck(order==sorted(order),'planned request order');ck(len(launches)==closure['claimed_physical_requests']<=28 and retries==closure['overload_resends']<=4,'request limits')
    u=read(root/'usage.json');known=[x for x in us if x['status']=='AVAILABLE']
    ck(u['physical_attempts']==len(launches) and u['available']==len(known) and u['unavailable_or_unproven']==len(launches)-len(known),'usage counts')
    ck(u['reported_subtotal']==({k:sum(x['totals'][k] for x in known) for k in ('input_tokens','output_tokens','total_tokens')} if known else None),'usage sum')
    status='ACQUISITION_INCONCLUSIVE' if (root/'halt.json').exists() else 'COMPLETE_DESCRIPTIVE' if all(s=='VALID' for s in statuses.values()) else 'COMPLETE_WITH_GATE_MISSINGNESS'
    ck(closure['status']==status and not closure['automatic_resume'],'closure')
    ck(closure['completed_logical_outputs']==len(list((root/'logical').glob('*-completion.json')))==sum(s in ('VALID','STRUCTURAL_MISSING','REFERENCE_REJECT','SELECTION_REJECT') for s in statuses.values()),'completed outputs')
    for f,h in read(root/'completion.json')['files_sha256'].items():ck(sha(root/f)==h,'completion seal')
    return {'status':'PASS','checks':n,'physical_requests':len(launches),'M_CONT':report['M_CONT'],'M_CONT_CONTENT':report['M_CONT_CONTENT'],
            'scope':'Same-author separate saved-evidence reader; not independent human/model review'}


if __name__=='__main__':print(json.dumps(audit(sys.argv[1]),ensure_ascii=False,indent=2))
