"""RC02 staged memory exchange using the established bounded sender; no semantic repair."""
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter
import ast, copy, json, math, sys, time
import judge_retry_v2 as io
import judge_retry_host_v1 as host
import judge_overload_retry_v1 as overload
import research_controlled_sender_v3 as sender
import row_carry_02_design_v1 as design
base, wire, core = io.base, io.wire, io.core
VERSION = 'row-carry-02-v0.1'
PROTOCOL = 'ROW-CARRY-02'
MODEL = 'gpt-5.6-luna'
LIMITS = {'logical_requests':24, 'physical_requests':28, 'overload_retries':4,
          'per_logical_attempts':2, 'active_seconds':1800, 'reserve_seconds':200,
          'response_utf8_bytes':4096, 'input_text_utf8_bytes':32768}


def sha(path):
    return base.sha(Path(path).read_bytes())

def manifest(root, paths):
    return {str(p.relative_to(root)):sha(p) for p in sorted(paths) if p.is_file()}

def authorization(root, c):
    auth = io.read(root/'authorization.json')
    expected = {'protocol':PROTOCOL, 'approved':True, 'configuration_sha256':sha(root/'configuration.json'),
                'limits':LIMITS, 'retention_expires_at':c['retention_expires_at'], 'egress':c['egress']}
    if auth != expected:
        raise ValueError('live authorization not bound to this configuration')
    if datetime.now(timezone.utc) >= datetime.fromisoformat(c['retention_expires_at']):
        raise ValueError('retention period expired')
    if sha(Path(c['sender_template']['cli'])) != c['sender_template']['cli_sha256']:
        raise ValueError('bound CLI changed; prepare a reviewed new run')

def retry_decision(*, eligible, attempts, used_retries, remaining_requests, remaining_seconds, since_failure):
    """Same eligibility and delays as the established route; RC02 global cap is four."""
    if not eligible:
        return {'action':'STOP','reason':'NOT_ELIGIBLE'}
    if attempts != 1:
        return {'action':'STOP','reason':'PER_LOGICAL_REQUEST_CAP'}
    if used_retries >= LIMITS['overload_retries'] or remaining_requests <= 0:
        return {'action':'STOP','reason':'WINDOW_REQUEST_CAP'}
    if not all(math.isfinite(x) for x in (remaining_seconds,since_failure)) or since_failure < 0:
        return {'action':'STOP','reason':'INVALID_CLOCK'}
    delay = max(0.0,30-since_failure)
    if remaining_seconds-delay <= LIMITS['reserve_seconds']:
        return {'action':'STOP','reason':'ACTIVE_CLOCK_CAP'}
    return {'action':'RETRY','wait_seconds':delay,'next_ordinal':attempts+1}

def usage(upstream):
    """Keep raw reported usage; absence/invalidity never becomes zero consumption."""
    try:
        events = [base.strict_json(line[6:]) for line in upstream.splitlines() if line.startswith(b'data: ') and line != b'data: [DONE]']
        ends = [e for e in events if e.get('type') in ('response.completed','response.failed')]
        if len(ends) != 1 or 'usage' not in ends[0].get('response',{}) or ends[0]['response']['usage'] is None:
            return {'status':'UNAVAILABLE','reported':None,'totals':None}
        u = ends[0]['response']['usage']
        keys = ('input_tokens','output_tokens','total_tokens')
        valid = type(u) is dict and all(type(u.get(k)) is int and u[k] >= 0 for k in keys) and u['total_tokens'] == u['input_tokens'] + u['output_tokens']
        return {'status':'AVAILABLE' if valid else 'INVALID', 'reported':u, 'totals':{k:u[k] for k in keys} if valid else None}
    except (ValueError,TypeError,KeyError):
        return {'status':'INVALID','reported':None,'totals':None}

def dependencies():
    directory=Path(__file__).parent;found={};todo=['row_carry_02_v1.py','prepare_row_carry_02_v1.py','audit_row_carry_02_v1.py']
    while todo:
        name=todo.pop()
        if name in found:continue
        p=directory/name;found[name]=sha(p)
        for n in ast.walk(ast.parse(p.read_text())):
            names=[a.name for a in n.names] if isinstance(n,ast.Import) else [n.module] if isinstance(n,ast.ImportFrom) and n.module else []
            todo += [i+'.py' for i in names if (directory/(i+'.py')).is_file() and i+'.py' not in found]
    return dict(sorted(found.items()))


def prompt_name(spec):
    return 'prompt-'+spec['stage'].lower()+'.txt'

def packet(root,spec,payload):
    return {'instructions':(Path(root)/'frozen'/prompt_name(spec)).read_text(),
            'input':'\n資料JSON:\n'+design.json_bytes(payload).decode()}


def egress(root):
    return {'destination':'https://chatgpt.com/backend-api/codex/responses',
            'payload':'8 fictional initial inputs from each own archived RC01 SELECT note and own new notice, then 16 dependent inputs carrying actual generated private/shared memory; past receipts, selectors, truth table and partner private notes excluded',
            'root_inputs_sha256':sha(root/'frozen/root-inputs.json'),
            'constructor_sha256':sha(root/'frozen/row_carry_02_design_v1.py'),
            'runtime_sha256':sha(root/'frozen/row_carry_02_v1.py'),
            'materials_sha256':sha(root/'frozen/materials.json'),
            'source_bindings_sha256':sha(root/'frozen/source-bindings.json'),
            'schema_file_sha256':sha(root/'frozen/response-schemas.json')}


def verify(root):
    root=Path(root);c=io.read(root/'configuration.json')
    if io.read(root/'configuration-seal.json')!={'sha256':sha(root/'configuration.json')}:raise ValueError('configuration seal mismatch')
    if (c['protocol'],c['version'],c['limits'])!=(PROTOCOL,VERSION,LIMITS) or c['mode'] not in ('SYNTHETIC','LIVE_PENDING_GO'):raise ValueError('configuration contract mismatch')
    if c['dependencies']!=dependencies():raise ValueError('loaded dependency changed')
    for p,h in c['frozen_sha256'].items():
        if sha(root/p)!=h:raise ValueError('frozen input changed: '+p)
    if c['allocation']!=io.read(root/'frozen/allocation.json') or c['materials']!=io.read(root/'frozen/materials.json'):raise ValueError('frozen design mismatch')
    if c['egress']!=egress(root) or c['retention_expires_at']!='2026-10-12T17:41:23+09:00':raise ValueError('egress or retention changed')
    if sha(root/'frozen/design-completion.json')!=c['design_completion_sha256']:raise ValueError('design anchor changed')
    cfg=io.read(root/'frozen/design-config.json')
    if cfg['planned_slots']!=24 or cfg['prediction_threshold']!=.75 or cfg['max_physical_requests']!=28 or cfg['max_seconds']!=1800:raise ValueError('design limits changed')
    if io.read(root/'frozen/response-schemas.json')!=design.schemas() or io.read(root/'frozen/normalized-schemas.json')!=design.memory_schemas():raise ValueError('schema changed')
    for stage in ('UPDATE','MERGE','PROBE'):
        if (root/'frozen'/prompt_name({'stage':stage})).read_text()!=design.prompt(stage):raise ValueError('prompt changed')
    specs=c['allocation'];seen=set()
    if len(specs)!=24 or Counter(s['stage'] for s in specs)!={'UPDATE':8,'MERGE':8,'PROBE':8} or len(c['materials'])!=4:raise ValueError('inventory changed')
    for s in specs:
        if s['id'] in seen or not set(s['dependencies'])<=seen:raise ValueError('dependency inventory')
        expected=[] if s['stage']=='UPDATE' else [design.slot_id(s['group'],'UPDATE',r) for r in ('A','B')] if s['stage']=='MERGE' else [design.slot_id(s['group'],'MERGE',s['role'])]
        if s['dependencies']!=expected:raise ValueError('role-specific parent')
        seen.add(s['id'])
    bindings=io.read(root/'frozen/source-bindings.json')
    if len(bindings)!=8 or {(b['group'],b['role']) for b in bindings}!={(g,r) for g in c['materials'] for r in ('A','B')}:raise ValueError('source inventory')
    for b in bindings:
        path=root/'frozen/source-notes'/Path(b['source']).name
        if sha(path)!=b['sha256']:raise ValueError('source note hash')
        if io.read(path)!=c['materials'][b['group']]['baseline_by_role'][b['role']]:raise ValueError('own source note mismatch')
    return c

def decode(text,spec,payload,material):
    checked=design.evaluate(material,spec,text.encode() if text is not None else None,payload)
    value=checked['normalized'];stage=spec['stage'];parts={}
    rule=design.memory_schemas()[stage]
    if stage=='PROBE':
        for name in ('mascot','channel'):
            v=design.leaf(value,'decision',name)
            parts[name]=v if not design.shape(v,rule['properties']['decision']['properties'][name]) else None
    else:
        rules=rule['properties']['memory']['properties']
        paths=[('private_customer',('private_note','customer'),rules['private_note']['properties']['customer']),
               ('private_coverage',('private_note','coverage'),rules['private_note']['properties']['coverage'])]
        paths += [('shared_'+r,('shared_note','coverage',r),rules['shared_note']['properties']['coverage']['properties'][r]) for r in ('A','B')]
        for name,path,rr in paths:
            v=design.leaf(value,'memory',*path);parts[name]=copy.deepcopy(v) if not design.shape(v,rr) else None
    raw_rule=design.schemas()[stage]
    bad_shape=checked['value'] is None or bool(design.shape(checked['value'],raw_rule))
    status='VALID' if checked['gate']=='PASS' else 'SELECTION_REJECT' if checked['selection_errors'] else 'STRUCTURAL_MISSING' if bad_shape else 'REFERENCE_REJECT'
    return {**checked,'status':status,'continuable':status=='VALID' and stage!='PROBE','valid_components':parts}


def materialization(spec,parsed,payload):
    return {'source_id':spec['id'],'stage':spec['stage'],
            'input_sha256':base.sha(design.json_bytes(payload)),
            'raw_value_sha256':base.sha(design.json_bytes(parsed['value'])),
            'normalized_value_sha256':base.sha(design.json_bytes(parsed['normalized'])),
            'rows':parsed['bindings'],'gate':parsed['gate'],
            'method':'LITERAL_CURRENT_ROW' if spec['stage']=='MERGE' else 'IDENTITY',
            'semantic_repair':False}


def note_state(parsed):
    return copy.deepcopy(parsed['normalized']['memory']) if parsed.get('continuable') else None


def bind_receipt(spec,parsed,payload):
    receipt=design.leaf(parsed['value'],'read_receipt');flat=[]
    if type(receipt) is dict:
        for k,v in receipt.items():
            if k=='shared_coverage_refs' and type(v) is dict:flat += [(k+'.'+r,refs) for r,refs in v.items()]
            else:flat.append((k,v))
    records={r['record_id']:r for r in payload['records']};claims=[]
    for field,refs in flat:
        if type(refs) is not list or any(type(x) is not str for x in refs):
            claims.append({'field':field,'status':'UNREADABLE','declared':refs});continue
        for alias in refs:
            present=alias in records
            claims.append({'field':field,'record_id':alias,'status':'PRESENT' if present else 'NOT_CURRENT',
                           'body_sha256':base.sha(design.json_bytes(records[alias]['body'])) if present else None})
    return {'source_id':spec['id'],'input_sha256':base.sha(design.json_bytes(payload)),
            'declared_read_receipt':receipt,'claims':claims,'scope':'Scoped declared references, not observed attention or semantic validation'}


class Campaign:
    def __init__(self, root, *, launcher=None, clock=time.monotonic, sleeper=time.sleep):
        self.root = Path(root).resolve()
        self.c = verify(self.root)
        if self.c['mode'] == 'LIVE_PENDING_GO':
            if launcher is not None or clock is not time.monotonic or sleeper is not time.sleep:
                raise ValueError('live transport and clock overrides prohibited')
            authorization(self.root,self.c)
            launcher = host.launch_sender
        elif launcher is None or launcher is host.launch_sender:
            raise ValueError('inert synthetic launcher required')
        self.launcher,self.clock,self.sleeper = launcher,clock,sleeper
        self.calls = self.invoked = self.retries = self.cursor = 0
        self.started = clock()
        self.results = {}
        self.usage_rows = []
        self.invoked_ids = set()
        self.runtime_files = {}
        self.requests = {}
        self.expected_wires = {}
        self.states = {}
        self.applied = {}
        self.raw_outputs = {x['id']:None for x in self.c['allocation']}
        self.packets = io.read(self.root/'frozen/root-inputs.json')

    def remaining(self):
        elapsed = self.clock() - self.started
        if not 0 <= elapsed:
            raise ValueError('invalid monotonic clock')
        return LIMITS['active_seconds'] - elapsed

    def integrity(self):
        verify(self.root)
        if self.c['mode'] == 'LIVE_PENDING_GO':
            authorization(self.root,self.c)
        for name, digest in self.runtime_files.items():
            if sha(self.root/name) != digest:
                raise ValueError('saved runtime evidence changed: '+name)

    def guard(self, *, after_claim=False):
        self.integrity()
        if (self.root/'halt.json').exists() or (self.root/'acquisition-closure.json').exists():
            raise ValueError('run already closed')
        if len(list((self.root/'dispatch').glob('*-launch.json'))) != self.calls:
            raise ValueError('physical claim count mismatch')
        if self.remaining() <= LIMITS['reserve_seconds']:
            raise TimeoutError('active clock reserve reached')
        if self.calls > LIMITS['physical_requests'] or (not after_claim and self.calls >= LIMITS['physical_requests']) or self.retries > LIMITS['overload_retries']:
            raise ValueError('physical request ceiling reached')

    def send(self, sid, raw):
        self.guard()
        spec = self.c['allocation'][self.cursor]
        if sid != spec['id'] or raw != self.expected_wires.get(sid) or raw != (self.root/'requests'/(sid+'.json')).read_bytes():
            raise ValueError('planned next request mismatch')
        wire.validate_input(raw, {'stage':'generation','model':MODEL,'request_sha256':base.sha(raw)})
        io.write(self.root/'logical'/(sid+'-claim.json'), {'at':io.now(),'source_id':sid,'request_sha256':base.sha(raw)})
        for ordinal in range(1,3):
            self.guard()
            if ordinal > 1 and self.retries >= LIMITS['overload_retries']:
                raise ValueError('overload resend ceiling reached')
            pid = sid+'-p'+str(ordinal)
            phase = self.root/'sender'/pid
            phase.mkdir(mode=0o700)
            for d in ('frozen','results'):
                (phase/d).mkdir(mode=0o700)
            for name in host.SENDER_FILES:
                base._write_new(phase/'frozen'/name,(self.root/'frozen'/name).read_bytes())
            base._write_new(phase/'frozen/request.json',raw)
            child = copy.deepcopy(self.c['sender_template'])
            child.update(protocol='RC02-'+pid, at=io.now(), model=MODEL, order=[pid],
                         trials={pid:{'stage':'generation','request':'frozen/request.json','request_sha256':base.sha(raw)}})
            child['configs'] = [v for v in child['configs'] if not v.startswith('model_catalog_json=')]
            child['configs'].append('model_catalog_json='+json.dumps(str(phase/'frozen/model-catalog.json'),ensure_ascii=False))
            child['frozen_sha256'] = manifest(phase,(phase/'frozen').iterdir())
            io.write(phase/'configuration.json',child)
            self.guard()
            io.write(self.root/'dispatch'/(pid+'-launch.json'),{'at':io.now(),'source_id':sid,'ordinal':ordinal,
                'sequence':self.calls+1,'overload_resend':ordinal>1,'request_sha256':base.sha(raw),
                'configuration_sha256':sha(phase/'configuration.json'),'remaining_seconds':self.remaining()})
            self.calls += 1
            self.retries += int(ordinal > 1)
            self.guard(after_claim=True)
            self.invoked += 1
            self.invoked_ids.add(sid)
            code = self.launcher(phase,pid,self.root/'dispatch')
            receipt,upstream = overload.inspect_receipt(phase,pid,raw,code)
            failed_at = self.clock()
            io.write(self.root/'dispatch'/(pid+'-receipt.json'),receipt)
            u = usage(upstream)
            io.write(self.root/'dispatch'/(pid+'-usage.json'),u)
            self.usage_rows.append({'physical_id':pid,**u})
            self.integrity()
            if self.remaining() < 0:
                raise TimeoutError('active clock exceeded')
            if receipt['accepted']:
                io.write(self.root/'logical'/(sid+'-completion.json'),{'physical_id':pid,'request_sha256':base.sha(raw),
                    'raw_sse_sha256':base.sha(upstream),'first_normal_retained':True})
                return upstream
            if self.retries >= LIMITS['overload_retries']:
                raise RuntimeError('overload resend ceiling reached')
            decision = retry_decision(eligible=receipt['overload_eligible'],attempts=ordinal,
                used_retries=self.retries,remaining_requests=LIMITS['physical_requests']-self.calls,remaining_seconds=self.remaining(),since_failure=self.clock()-failed_at)
            io.write(self.root/'dispatch'/(pid+'-decision.json'),decision)
            if decision['action'] != 'RETRY':
                raise RuntimeError('transport stopped: '+decision['reason'])
            deadline = failed_at + 30
            while self.clock() < deadline:
                self.guard()
                self.sleeper(min(30,deadline-self.clock()))
        raise RuntimeError('unreachable')

    def track(self, path):
        self.runtime_files[str(path.relative_to(self.root))] = sha(path)

    def save(self, path, value):
        io.write(path, value)
        if io.read(path) != value:
            raise ValueError('saved JSON differs from intended evidence: '+str(path))
        self.track(path)

    def parent_binding(self, parent):
        result = {'parsed_sha256':sha(self.root/'generations'/(parent+'-parsed.json')),
                  'raw_sha256':sha(self.root/'generations'/(parent+'-raw.txt')),
                  'note_sha256':sha(self.root/'states'/(parent+'-note.json')),
                  'receipt_sha256':sha(self.root/'receipts'/(parent+'.json')),
                  'materialization_sha256':sha(self.root/'materializations'/(parent+'.json'))}
        return result

    def ingest_saved_raw(self, spec, text):
        sid = spec['id']
        raw_path = self.root/'generations'/(sid+'-raw.txt')
        if raw_path.read_bytes() != text.encode():
            raise ValueError('raw receipt not preserved')
        return decode(text,spec,self.states[sid],self.c['materials'][spec['group']])

    def assemble(self,spec):
        self.integrity()
        if spec!=self.c['allocation'][self.cursor] or not self.stage_done(spec):raise ValueError('planned dependency or stage mismatch')
        sid=spec['id'];parents=spec['dependencies']
        if any(p not in self.results for p in parents):raise ValueError('unaccounted parent')
        for parent in parents:
            if self.results[parent]!=io.read(self.root/'generations'/(parent+'-parsed.json')):raise ValueError('parent parsed mismatch')
            if self.results[parent].get('continuable') and note_state(self.results[parent])!=io.read(self.root/'states'/(parent+'-note.json')):raise ValueError('saved parent note mismatch')
        blocked=[p for p in parents if not self.results[p].get('continuable')]
        if blocked:
            parsed={**decode(None,spec,None,self.c['materials'][spec['group']]),'status':'DEPENDENCY_UNISSUED','blocked_parents':blocked,'continuable':False}
            self.save(self.root/'generations'/(sid+'-parsed.json'),parsed);self.results[sid]=parsed
            return None
        payload=design.input_for(self.c['materials'][spec['group']],spec,self.applied)
        pp=packet(self.root,spec,payload);text=pp['instructions']+pp['input']
        raw=sender.make_request(MODEL,pp['instructions'],pp['input'])
        if spec['stage']=='UPDATE' and (text!=self.packets[sid] or raw!=(self.root/'fixed-inputs'/(sid+'.json')).read_bytes()):raise ValueError('root packet mismatch')
        if len(text.encode())>LIMITS['input_text_utf8_bytes']:raise ValueError('input size limit')
        wire.validate_input(raw,{'stage':'generation','model':MODEL,'request_sha256':base.sha(raw)})
        self.save(self.root/'states'/(sid+'-incoming.json'),payload)
        self.save(self.root/'requests'/(sid+'-packet.json'),pp)
        path=self.root/'requests'/(sid+'.json');base._write_new(path,raw);self.track(path)
        self.save(self.root/'requests'/(sid+'-binding.json'),{'source_id':sid,'parents':parents,'stage':spec['stage'],'role':spec['role'],
            'configuration_sha256':sha(self.root/'configuration.json'),'request_sha256':base.sha(raw),
            'incoming_sha256':sha(self.root/'states'/(sid+'-incoming.json')),'parent_bindings':{p:self.parent_binding(p) for p in parents},
            'materials_sha256':sha(self.root/'frozen/materials.json'),'source_bindings_sha256':sha(self.root/'frozen/source-bindings.json'),
            'input_text_utf8_bytes':len(text.encode())})
        self.states[sid]=payload;self.requests[sid]=pp;self.expected_wires[sid]=raw
        return raw

    def apply(self,spec,parsed):
        sid=spec['id']
        self.save(self.root/'states'/(sid+'-components.json'),parsed['valid_components'])
        self.save(self.root/'receipts'/(sid+'.json'),bind_receipt(spec,parsed,self.states[sid]))
        if spec['stage']!='PROBE':self.save(self.root/'materializations'/(sid+'.json'),materialization(spec,parsed,self.states[sid]))
        state=note_state(parsed)
        if state is not None:
            self.save(self.root/'states'/(sid+'-note.json'),state);self.applied[sid]=state

    @staticmethod
    def stage(spec):
        return spec['stage'].lower()

    def stage_done(self,spec):
        stages=['update','merge','probe'];index=stages.index(self.stage(spec))
        return index==0 or (self.root/'stages'/(stages[index-1]+'-closure.json')).exists()

    def close_stage(self, name):
        self.integrity()
        specs = [s for s in self.c['allocation'] if self.stage(s)==name]
        if any(s['id'] not in self.results for s in specs):
            raise ValueError('incomplete stage cannot close')
        names = [s['id'] for s in specs]
        evidence = [p for d in ('generations','requests','states','receipts','materializations') for p in (self.root/d).iterdir()
                    if any(p.name.startswith(sid+'-') or p.name==sid+'.json' for sid in names)]
        self.save(self.root/'stages'/(name+'-closure.json'),{'at':io.now(),'stage':name,
                  'outcomes':{sid:self.results[sid]['status'] for sid in names},'files_sha256':manifest(self.root,evidence)})

    def run(self):
        io.write(self.root/'execution-start.json',{'at':io.now(),'mode':self.c['mode'],
                 'configuration_sha256':sha(self.root/'configuration.json')})
        self.started = self.clock()
        sid = None
        try:
            for index,spec in enumerate(self.c['allocation']):
                self.cursor = index
                sid = spec['id']
                self.guard()
                if not self.stage_done(spec):
                    raise ValueError('stage barrier not satisfied')
                raw = self.assemble(spec)
                if raw is not None:
                    campaign = self
                    class Transport:
                        def send(self, sent):
                            try:
                                return campaign.send(sid,sent)
                            except Exception as exc:
                                io.write(campaign.root/'logical'/(sid+'-failure.json'),{'exception_class':type(exc).__name__,'reason':str(exc)})
                                raise
                    runner = wire.ResponsesRunner('RC02-'+sid,{sid:core.Ticket('generation',MODEL,base.sha(raw))},
                        self.root/'journals'/(sid+'.sqlite'),Transport(),gate=core.GateProcess(script=Path(wire.__file__)))
                    result = runner.run(sid,raw)
                    self.save(self.root/'generations'/(sid+'-transport.json'),asdict(result))
                    if result.status != 'ACCEPTED':
                        raise RuntimeError('outer transport not accepted: '+result.status)
                    path = self.root/'generations'/(sid+'-raw.txt')
                    base._write_new(path,result.text.encode()); self.track(path)
                    parsed = self.ingest_saved_raw(spec,result.text)
                    self.raw_outputs[sid] = result.text
                    self.save(self.root/'generations'/(sid+'-parsed.json'),parsed)
                    self.results[sid] = parsed
                    self.apply(spec,parsed)
                stage = self.stage(spec)
                if index==len(self.c['allocation'])-1 or self.stage(self.c['allocation'][index+1])!=stage:
                    self.close_stage(stage)
        except Exception as exc:
            if sid is not None and sid not in self.results and sid in self.invoked_ids:
                self.results[sid] = {**decode(None,spec,self.states.get(sid),self.c['materials'][spec['group']]),'status':'TRANSPORT_FAILURE','continuable':False}
                path=self.root/'generations'/(sid+'-parsed.json')
                if not path.exists():self.save(path,self.results[sid])
            io.write(self.root/'halt.json',{'at':io.now(),'source_id':sid,'exception_class':type(exc).__name__,
                     'reason':str(exc),'automatic_resume':False})
        closed = not (self.root/'halt.json').exists()
        valid = sum(r['status']=='VALID' for r in self.results.values())
        status = ('COMPLETE_DESCRIPTIVE' if len(self.results)==24 and all(r['status']=='VALID' for r in self.results.values()) else 'COMPLETE_WITH_GATE_MISSINGNESS') if closed else 'ACQUISITION_INCONCLUSIVE'
        io.write(self.root/'acquisition-closure.json',{'at':io.now(),'mode':self.c['mode'],'status':status,
                 'planned_slots':24,'claimed_physical_requests':self.calls,'invoked_sender_requests':self.invoked,
                 'overload_resends':self.retries,'seconds':self.clock()-self.started,
                 'completed_logical_outputs':sum(r['status'] in ('VALID','STRUCTURAL_MISSING','REFERENCE_REJECT','SELECTION_REJECT') for r in self.results.values()),
                 'automatic_resume':False})
        report = summarize(self.c['materials'],self.c['allocation'],self.raw_outputs,self.results,self.states,self.expected_wires)
        io.write(self.root/'analysis.json',report)
        known = [r for r in self.usage_rows if r['status']=='AVAILABLE']
        io.write(self.root/'usage.json',{'physical_attempts':self.calls,'available':len(known),
                 'unavailable_or_unproven':self.calls-len(known),'complete':len(known)==self.calls,
                 'reported_subtotal':{k:sum(r['totals'][k] for r in known) for k in ('input_tokens','output_tokens','total_tokens')} if known else None,
                 'scope':'Upstream request usage only; excludes orchestration and authentication bootstrap. Missing is not zero.','rows':self.usage_rows})
        io.write(self.root/'completion.json',{'at':io.now(),'mode':self.c['mode'],'files_sha256':manifest(self.root,self.root.rglob('*'))})
        return {'status':status,'physical_requests':self.calls,'valid':valid,
                'status_counts':report['status_counts'],'M_CONT':report['M_CONT'],'M_CONT_CONTENT':report['M_CONT_CONTENT']}


def summarize(materials,allocation,raw,results,states,wires):
    scores={s['id']:design.evaluate(materials[s['group']],s,raw[s['id']].encode() if raw.get(s['id']) is not None else None,states.get(s['id']))['score'] for s in allocation}
    agg=design.aggregate(allocation,scores)
    def counts(values):
        values=list(values);return {'true':values.count(True),'false':values.count(False),'unknown':values.count(None),'planned':len(values)}
    report={'planned_groups':4,'planned_slots':24,'M_CONT':agg['strict']['bounds'],'M_CONT_CONTENT':agg['content']['bounds'],
            'prediction_status':agg['prediction'],'aggregate':agg,'slot_scores':scores,
            'status_counts':dict(Counter(results.get(s['id'],{}).get('status','UNISSUED') for s in allocation)),
            'all_slot_statuses':[{'id':s['id'],'stage':s['stage'],'status':results.get(s['id'],{}).get('status','UNISSUED')} for s in allocation]}
    detail={};stages={}
    for stage in ('UPDATE','MERGE','PROBE'):
        ss=[s for s in allocation if s['stage']==stage]
        stages[stage]={mode:counts(scores[s['id']][mode] for s in ss) for mode in ('strict','content')}
        for role in ('A','B'):
            sr=[s for s in ss if s['role']==role]
            names=('mascot','channel') if stage=='PROBE' else ('private_note.customer','private_note.coverage','shared_note.coverage.A','shared_note.coverage.B')
            detail[stage+'-'+role]={key:{mode:counts(scores[s['id']]['parts'][key][mode] for s in sr) for mode in ('strict','content')} for key in names}
    report['stages']=stages;report['components_by_stage_role']=detail
    final=[];rows=[]
    for s in allocation:
        v=results.get(s['id'],{}).get('normalized');m=materials[s['group']]
        if s['stage']=='PROBE':
            channel=design.leaf(v,'decision','channel')
            final.append({'id':s['id'],'channel':channel,'UNKNOWN':channel=='UNKNOWN' if channel is not None else None,
                          'correct_channel':scores[s['id']]['parts']['channel']['content'],'correct_customer':scores[s['id']]['parts']['mascot']['content']})
        elif s['stage']=='MERGE':
            available=design.candidates(states[s['id']]) if s['id'] in states else {}
            for owner in ('A','B'):
                row=design.leaf(v,'memory','shared_note','coverage',owner)
                valid=not design.shape(row,design.memory_schemas()['MERGE']['properties']['memory']['properties']['shared_note']['properties']['coverage']['properties'][owner])
                rows.append({'id':s['id'],'observer':owner,'existing_whole_row':row in available.values() if valid else None,
                    'latest_full':row==m['notices'][owner] if valid else None,'wrong_observer':row['observer']!=owner if valid else None,
                    'old_revision':row['revision'] in (1,2,3) if valid else None})
    report['final_decisions']=final;report['merge_observation_details']=rows
    report['scope']='Conditional continuation of four known groups, six slots each. Missingness bounds are not confidence intervals. Copy integrity is separate from selection success.'
    return report


if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: row_carry_02_v1.py PREPARED_RUN (requires bound live authorization)')
    print(json.dumps(Campaign(sys.argv[1]).run(),ensure_ascii=False,indent=2))
