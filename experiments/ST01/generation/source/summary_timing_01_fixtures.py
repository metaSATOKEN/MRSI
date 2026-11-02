"""Synthetic protocol fixtures. Never substituted for real missing answers."""
from copy import deepcopy
from fractions import Fraction
import json
import summary_timing_01_scoring as sc

def correct_answer(payload,stage):
    rows=payload['experiences'];role=payload['holder'];rates={}
    for r in {x['observer'] for x in rows}:
        own=[x for x in rows if x['observer']==r];n=sum(x['attempts_per_medium'] for x in own)
        rates[r]={m:Fraction(sum(x[m.lower()+'_success'] for x in own),n) for m in ('PAPER','DIGITAL')}
    local={'subject':role,'choice':max(rates[role],key=rates[role].get),
           'evidence_refs':[x['episode_id'] for x in rows if x['observer']==role]}
    if stage=='FORM':return {'local':local}
    best=({'A':'PAPER','B':'DIGITAL'} if rates['A']['PAPER']+rates['B']['DIGITAL']>
          rates['A']['DIGITAL']+rates['B']['PAPER'] else {'A':'DIGITAL','B':'PAPER'})
    if stage=='CONFIRM':
        p=payload['initial_proposal'];action='ACCEPT' if p['body']['allocation']==best else 'COUNTER'
        return {'local':local,'reply':{'action':action,'reply_to':p['record_id'],
             'allocation':best,'evidence_refs':[x['episode_id'] for x in rows]}}
    if stage in ('RECHECK','RECHECK_DIAGNOSTIC'):
        p,c=payload['initial_proposal'],payload['counter_record'];b=c['body'];expected={x['episode_id'] for x in rows}
        valid=(c['author']!=p['author'] and b['action']=='COUNTER' and b['reply_to']==p['record_id']
               and len(b['evidence_refs'])==len(expected) and set(b['evidence_refs'])==expected and b['allocation']==best)
        return {'local':local,'reply':{'action':'ACCEPT' if valid else 'HOLD','reply_to':c['record_id'],
             'allocation':deepcopy(b['allocation']) if valid else {'A':'UNDECIDED','B':'UNDECIDED'},'evidence_refs':[x['episode_id'] for x in rows]}}
    records=payload['joint_records'];p,c=records[:2];b=c['body']
    linked=c['author']!=p['author'] and b['reply_to']==p['record_id']
    if len(records)==2:
        k=linked and b['action']=='ACCEPT' and b['allocation']==p['body']['allocation'] and sorted(b['allocation'].values())==['DIGITAL','PAPER']
    else:
        r=records[2];rb=r['body']
        k=(linked and b['action']=='COUNTER' and r['author']==p['author'] and rb['action']=='ACCEPT'
           and rb['reply_to']==c['record_id'] and rb['allocation']==b['allocation'] and sorted(b['allocation'].values())==['DIGITAL','PAPER'])
    return {'local':local,'team':{'allocation':deepcopy(records[-2]['body']['allocation']) if k else {'A':'UNDECIDED','B':'UNDECIDED'},
        'basis':'SHARED_DECISION' if k else 'UNRESOLVED','evidence_refs':[x['record_id'] for x in records[-2:]]}}

def from_messages(messages):
    p=json.loads(messages[1]['content'].split('資料JSON:\n',1)[1])
    stage=('USE' if 'joint_records' in p else 'RECHECK' if 'counter_record' in p else
           'CONFIRM' if 'initial_proposal' in p else 'FORM')
    return p,stage

class SyntheticBackend:
    def __init__(self,transform=None):self.calls=0;self.transform=transform;self.requests=[]
    def prepare(self,messages):
        return {'rendered_prompt':'SYNTHETIC_NOT_A_MODEL_TEMPLATE\n'+sc.displayed(messages),
                'input_ids':[1],'synthetic_messages':deepcopy(messages)}
    def generate(self,prepared,seed,deadline):
        self.calls+=1;p,stage=from_messages(prepared['synthetic_messages'])
        self.requests.append({'payload':p,'stage':stage,'seed':seed})
        a=correct_answer(p,stage);raw=sc.enc(a).decode()
        if self.transform:raw=self.transform(self.calls,p,stage,a)
        return {'output_token_ids':[123,248046],'decoded_with_special_tokens':raw+'<|im_end|>',
            'answer_text':raw,'finish_reason':'EOS','generation_seconds':0.0,'peak_vram_bytes':0,'seed':seed,'synthetic_fixture':True}
