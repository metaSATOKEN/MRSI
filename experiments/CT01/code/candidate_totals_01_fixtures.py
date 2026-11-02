"""Synthetic arithmetic fixtures only. No fallback to these answers at runtime."""
from copy import deepcopy
from fractions import Fraction
import json
import candidate_totals_01_design as sc


def correct_answer(payload,stage,method='BASE'):
    rows=payload['experiences'];role=payload['holder'];rates={}
    for r in ('A','B'):
        own=[x for x in rows if x['observer']==r];n=sum(x['attempts_per_medium'] for x in own)
        rates[r]={m:Fraction(sum(x[m.lower()+'_success'] for x in own),n) for m in ('PAPER','DIGITAL')}
    best={'A':'PAPER','B':'DIGITAL'} if rates['A']['PAPER']+rates['B']['DIGITAL']>rates['A']['DIGITAL']+rates['B']['PAPER'] else {'A':'DIGITAL','B':'PAPER'}
    local={'subject':role,'choice':max(rates[role],key=rates[role].get),'evidence_refs':[x['episode_id'] for x in rows if x['observer']==role]}
    if stage=='PROPOSE':
        proposal={'evidence_refs':[x['episode_id'] for x in rows]}
        proposal['candidate_id']=next(c['candidate_id'] for c in payload['candidates'] if c['allocation']==best)
        return {'local':local,'proposal':proposal}
    if stage=='CONFIRM':
        p=payload['proposal'];valid=p['body']['allocation']==best
        return {'local':local,'reply':{'action':'ACCEPT' if valid else 'COUNTER','reply_to':p['record_id'],
                'allocation':deepcopy(best),'evidence_refs':[x['episode_id'] for x in rows]}}
    proposal=next(x for x in payload['joint_records'] if 'action' not in x['body'])
    reply=next(x for x in payload['joint_records'] if 'action' in x['body']);r=reply['body']
    k=(proposal['author']!=reply['author'] and r['action']=='ACCEPT' and r['reply_to']==proposal['record_id']
       and r['allocation']==proposal['body']['allocation'] and sorted(r['allocation'].values())==['DIGITAL','PAPER'])
    return {'local':local,'team':{'allocation':deepcopy(r['allocation']) if k else {'A':'UNDECIDED','B':'UNDECIDED'},
            'basis':'SHARED_DECISION' if k else 'UNRESOLVED','evidence_refs':[x['record_id'] for x in payload['joint_records']]}}


def from_messages(messages):
    p=json.loads(messages[1]['content'].split('資料JSON:\n',1)[1])
    stage='USE' if 'joint_records' in p else 'CONFIRM' if 'proposal' in p else 'PROPOSE'
    method='TOTALS' if stage=='PROPOSE' and sc.TOTAL_FIELD in p['candidates'][0] else 'BASE'
    return p,stage,method


class SyntheticBackend:
    def __init__(self,transform=None):self.calls=0;self.transform=transform;self.requests=[]
    def prepare(self,messages):
        return {'rendered_prompt':'SYNTHETIC_NOT_A_MODEL_TEMPLATE\n'+sc.displayed(messages),
                'input_ids':[1],'synthetic_messages':deepcopy(messages)}
    def generate(self,prepared,seed,deadline):
        self.calls+=1;p,stage,method=from_messages(prepared['synthetic_messages'])
        self.requests.append({'payload':p,'stage':stage,'method':method,'seed':seed})
        a=correct_answer(p,stage,method);raw=sc.enc(a).decode()
        if self.transform:raw=self.transform(self.calls,p,stage,a)
        return {'output_token_ids':[123,248046],'decoded_with_special_tokens':raw+'<|im_end|>',
                'answer_text':raw,'finish_reason':'EOS','generation_seconds':0.0,'peak_vram_bytes':0,'seed':seed,'synthetic_fixture':True}
