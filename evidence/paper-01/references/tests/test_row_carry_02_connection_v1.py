from pathlib import Path
from unittest.mock import patch
import copy,json,sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import row_carry_02_v1 as study
import prepare_row_carry_02_v1 as prep
import audit_row_carry_02_v1 as audit
from row_carry_02_connection_v1_fixtures import Clock,FakeSender

A=study.io.read(prep.DESIGN/'allocation.json');M=study.io.read(prep.DESIGN/'materials.json');SCHEMA=study.io.read(prep.DESIGN/'response-schemas.json');NORMAL=study.io.read(prep.DESIGN/'normalized-schemas.json')


class Connection(unittest.TestCase):
    def make(self,tmp,actions=None,kind='perfect'):
        root=prep.prepare(Path(tmp)/'run',mode='SYNTHETIC');clock=Clock();fake=FakeSender(root,clock,actions=actions,kind=kind)
        return root,clock,fake,study.Campaign(root,launcher=fake,clock=clock,sleeper=clock.sleep)

    def test_01_prepared_no_auth_and_bad_auth_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=prep.prepare(Path(tmp)/'live')
            with self.assertRaises(FileNotFoundError):study.Campaign(root)
            with self.assertRaises(ValueError):study.Campaign(root,launcher=lambda *_:0)
            with self.assertRaises(ValueError):study.Campaign(root,clock=lambda:0)
            study.io.write(root/'authorization.json',{'approved':True})
            with self.assertRaises(ValueError):study.Campaign(root)
            self.assertFalse((root/'execution-start.json').exists());self.assertFalse(any((root/'dispatch').iterdir()))

    def test_02_synthetic_no_real_sender_or_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,clock,fake,c=self.make(tmp,{1:'throw'})
            with self.assertRaises(ValueError):study.Campaign(root)
            with self.assertRaises(ValueError):study.Campaign(root,launcher=study.host.launch_sender)
            c.run()
            with self.assertRaises(FileExistsError):c.run()

    def test_03_saved_design_parser_and_score_agree(self):
        for p in sorted((prep.DESIGN/'finite-cases').glob('*.json')):
            for row in study.io.read(p)['evidence']:
                if 'input' not in row:continue
                s=row['slot'];raw=row['raw'];payload=row['input']
                observed=study.decode(raw,s,payload,M[s['group']]);independent=audit.decode(raw,s,payload,M[s['group']],SCHEMA,NORMAL)
                for key in ('value','normalized','gate','status','continuable','valid_components','bindings'):self.assertEqual(observed[key],independent[key],(p.name,s['id'],key))
                for key in ('strict','content','parts'):self.assertEqual(independent['score'][key],row['evaluation']['score'][key],(p.name,s['id'],key))

    def test_04_stage_boundaries_and_role_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,clock,fake,c=self.make(tmp);c.cursor=8
            with self.assertRaises(ValueError):c.assemble(A[8])
            with self.assertRaises(ValueError):c.close_stage('update')
            c.cursor=0;s=copy.deepcopy(A[0]);s['role']='B' if s['role']=='A' else 'A'
            with self.assertRaises(ValueError):c.assemble(s)

    def test_05_fixed_inputs_and_request_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,clock,fake,c=self.make(tmp)
            with self.assertRaises(ValueError):c.send(A[1]['id'],b'{}')
            c.packets[A[0]['id']]+='modified'
            with self.assertRaises(ValueError):c.assemble(A[0])
            path=next((root/'fixed-inputs').glob('*.json'));path.write_bytes(path.read_bytes()+b' ')
            with self.assertRaises(ValueError):c.integrity()
            with self.assertRaises(AssertionError):audit.audit(root)

    def test_06_source_archives_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,clock,fake,c=self.make(tmp);path=next((root/'frozen/source-notes').glob('*.json'));original=path.read_bytes()
            path.write_bytes(original+b' ')
            with self.assertRaises(ValueError):c.integrity()
            with self.assertRaises(AssertionError):audit.audit(root)

    def test_07_clocks_before_and_after_claim(self):
        for moment in ('child','claim'):
            with self.subTest(moment),tempfile.TemporaryDirectory() as tmp:
                root,clock,fake,c=self.make(tmp);write=study.io.write
                def delayed(path,obj):
                    write(path,obj)
                    if moment=='child' and path.name=='configuration.json' and 'sender' in path.parts or moment=='claim' and path.name.endswith('-launch.json'):clock.seconds=1600
                with patch.object(study.io,'write',delayed):out=c.run()
                self.assertEqual(fake.calls,[]);self.assertEqual(out['status_counts']['UNISSUED'],24)

    def test_08_partial_tool_exception_stop(self):
        for action in ('partial','tool','throw'):
            with self.subTest(action),tempfile.TemporaryDirectory() as tmp:
                root,clock,fake,c=self.make(tmp,{1:action});out=c.run()
                self.assertEqual(out['physical_requests'],1);self.assertEqual(out['status'],'ACQUISITION_INCONCLUSIVE')
                self.assertEqual(audit.audit(root)['status'],'PASS')

    def test_09_retry_caps(self):
        for actions,count,delay in [({1:'overload',2:'overload'},2,30),({x:'overload' for x in (1,3,5,7,9)},9,120)]:
            with self.subTest(count),tempfile.TemporaryDirectory() as tmp:
                root,clock,fake,c=self.make(tmp,actions);out=c.run()
                self.assertEqual(out['physical_requests'],count);self.assertEqual(sum(clock.waits),delay)
                self.assertEqual(audit.audit(root)['status'],'PASS')

    def test_10_invalid_retry_clocks(self):
        for seconds,since,used in [(230,0,0),(float('nan'),0,0),(500,-1,0),(500,0,4)]:
            self.assertEqual(study.retry_decision(eligible=True,attempts=1,used_retries=used,remaining_requests=10,remaining_seconds=seconds,since_failure=since)['action'],'STOP')

    def test_11_memory_receipt_separation_and_no_semantic_repair(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,clock,fake,c=self.make(tmp);s=next(s for s in A if s['stage']=='UPDATE');c.cursor=A.index(s);c.assemble(s);v=study.design.ideal(M[s['group']],s)
            v['memory']['private_note']['customer']['animal']='UNKNOWN'
            parsed=study.decode(json.dumps(v),s,c.states[s['id']],M[s['group']]);self.assertTrue(parsed['continuable']);c.apply(s,parsed)
            note=study.io.read(root/'states'/(s['id']+'-note.json'));self.assertEqual(note,v['memory']);self.assertNotIn('read_receipt',note)
            receipt=study.io.read(root/'receipts'/(s['id']+'.json'));self.assertEqual(receipt['declared_read_receipt'],v['read_receipt'])

    def test_12_rejected_refs_keep_components_but_block_memory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,clock,fake,c=self.make(tmp);s=next(s for s in A if s['stage']=='UPDATE');c.cursor=A.index(s);c.assemble(s);v=study.design.ideal(M[s['group']],s)
            v['read_receipt']['private_customer_refs']=['HISTORICAL']
            p=study.decode(json.dumps(v),s,c.states[s['id']],M[s['group']]);self.assertEqual(p['status'],'REFERENCE_REJECT');c.apply(s,p)
            self.assertTrue(all(v is not None for v in p['valid_components'].values()));self.assertFalse((root/'states'/(s['id']+'-note.json')).exists())
            receipt=study.io.read(root/'receipts'/(s['id']+'.json'));self.assertIn('NOT_CURRENT',[r['status'] for r in receipt['claims']])

    def test_13_receipt_scoped_to_step_input_and_body(self):
        s=A[0];p=study.design.input_for(M[s['group']],s,{});v=study.decode(json.dumps(study.design.ideal(M[s['group']],s)),s,p,M[s['group']])
        a=study.bind_receipt(s,v,p);other=copy.deepcopy(p);other['item']+='別';ss={**s,'id':'SECOND'};b=study.bind_receipt(ss,v,other)
        self.assertNotEqual(a['source_id'],b['source_id']);self.assertNotEqual(a['input_sha256'],b['input_sha256'])
        self.assertEqual(a['claims'],b['claims'])

    def test_14_saved_note_failure_and_silent_corruption(self):
        for mode in ('raise','corrupt'):
            with self.subTest(mode),tempfile.TemporaryDirectory() as tmp:
                root,clock,fake,c=self.make(tmp);write=study.io.write
                def altered(path,value):
                    if path.name.endswith('-note.json'):
                        if mode=='raise':raise OSError('synthetic storage error')
                        value=copy.deepcopy(value);value['private_note']['customer']['animal']='UNKNOWN'
                    write(path,value)
                with patch.object(study.io,'write',altered):out=c.run()
                self.assertEqual(out['status'],'ACQUISITION_INCONCLUSIVE');self.assertEqual(len(fake.calls),1)
                if mode=='raise':
                    with self.assertRaises(FileNotFoundError) as rejected:audit.audit(root)
                    self.assertTrue(str(rejected.exception.filename).endswith('-note.json'))
                else:
                    with self.assertRaises(AssertionError):audit.audit(root)

    def test_15_runtime_tampering_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,clock,fake,c=self.make(tmp);path=root/'states/saved.json';path.write_text('{}');c.track(path)
            def alter(phase,pid,dispatch):
                out=fake(phase,pid,dispatch);path.write_text('{"changed":true}');return out
            c.launcher=alter;out=c.run();self.assertEqual(out['valid'],0);self.assertEqual(len(fake.calls),1)

    def test_16_probe_is_not_forwarded(self):
        probes={s['id'] for s in A if s['stage']=='PROBE'};self.assertTrue(all(not probes.intersection(s['dependencies']) for s in A))
        row=next(x for x in study.io.read(prep.DESIGN/'finite-cases/perfect.json')['evidence'] if x['slot']['stage']=='PROBE');s=row['slot']
        p=study.decode(row['raw'],s,row['input'],M[s['group']]);self.assertEqual(p['status'],'VALID');self.assertFalse(p['continuable'])

    def test_17_role_specific_source_and_no_truth_reinjection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=prep.prepare(Path(tmp)/'live');bindings=study.io.read(root/'frozen/source-bindings.json');self.assertEqual(len(bindings),8)
            for b in bindings:
                original=study.io.read(root/'frozen/source-notes'/Path(b['source']).name)
                sid=study.design.slot_id(b['group'],'UPDATE',b['role'])
                wire=study.io.read(root/'fixed-inputs'/(sid+'.json'))
                body=json.loads(wire['input'][1]['content'][0]['text'].split('\n資料JSON:\n',1)[1])
                records={x['record_id']:x['body'] for x in body['records']}
                self.assertEqual(records['PRIVATE'],original['private_note']);self.assertEqual(records['BASE_GROUP'],original['shared_note'])
                self.assertEqual(set(records),{'PRIVATE','BASE_GROUP','NOTICE'});self.assertEqual(records['NOTICE']['observer'],b['role'])
                self.assertNotIn('read_receipt',json.dumps(body))
            self.assertEqual(audit.audit(root)['status'],'PASS')

    def test_18_wrong_existing_row_is_copied_without_repair(self):
        row=next(x for x in study.io.read(prep.DESIGN/'finite-cases/perfect.json')['evidence'] if x['slot']['stage']=='MERGE');s=row['slot'];payload=row['input']
        for who in ('A','B'):
            raw=json.loads(row['raw']);raw['memory']['shared_note']['coverage']['A']={'record_id':'LOCAL_GROUP','observer':who}
            p=study.decode(json.dumps(raw),s,payload,M[s['group']]);self.assertTrue(p['continuable'])
            expected=study.design.candidates(payload)[('LOCAL_GROUP',who)]
            self.assertEqual(study.note_state(p)['shared_note']['coverage']['A'],expected)
            q=audit.decode(json.dumps(raw),s,payload,M[s['group']],SCHEMA,NORMAL)
            self.assertEqual(study.materialization(s,p,payload),audit.proof(s,q,payload))

    def test_19_corrupt_materialization_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,clock,fake,c=self.make(tmp);s=A[0];c.assemble(s);p=study.decode(json.dumps(study.design.ideal(M[s['group']],s)),s,c.states[s['id']],M[s['group']]);c.apply(s,p)
            path=root/'materializations'/(s['id']+'.json');path.write_bytes(path.read_bytes()+b' ')
            with self.assertRaises(ValueError):c.integrity()

    def test_20_dependency_block_scope(self):
        for kind,status,blocked,calls in [('noncurrent_selector','SELECTION_REJECT',1,23),('selector_extra_field','STRUCTURAL_MISSING',1,23),('known_wrong_plus_null_update','STRUCTURAL_MISSING',4,20)]:
            with self.subTest(kind),tempfile.TemporaryDirectory() as tmp:
                root,clock,fake,c=self.make(tmp,kind=kind);out=c.run()
                self.assertEqual(out['physical_requests'],calls);self.assertEqual(out['status_counts']['DEPENDENCY_UNISSUED'],blocked);self.assertEqual(out['status_counts'][status],1)
                self.assertEqual(audit.audit(root)['status'],'PASS')

    def test_21_input_wrong_origin_is_copied_not_corrected(self):
        row=next(x for x in study.io.read(prep.DESIGN/'finite-cases/perfect.json')['evidence'] if x['slot']['stage']=='MERGE');s=row['slot'];payload=copy.deepcopy(row['input']);who='B' if s['role']=='A' else 'A'
        source=next(r for r in payload['records'] if r['record_id']=='PARTNER_GROUP')['body']['coverage'][who];source['origin_id']='BAD1'
        parsed=study.decode(row['raw'],s,payload,M[s['group']]);self.assertEqual(parsed['normalized']['memory']['shared_note']['coverage'][who]['origin_id'],'BAD1')
        self.assertFalse(parsed['score']['strict']);self.assertTrue(parsed['continuable'])


if __name__=='__main__':unittest.main(verbosity=2)
