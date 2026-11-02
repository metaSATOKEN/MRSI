"""Synthetic tests only; raw source preparations supplied by offline tests, never fake tokenizer hashes."""
from copy import deepcopy
import json
import summary_timing_02_fixtures as prior
from judgment_repeat_01_scoring import digest
correct_answer = prior.correct_answer

class SyntheticBackend:
    def __init__(self, preparations, transform=None):
        self.preparations=preparations;self.transform=transform;self.calls=0;self.requests=[]
    def prepare(self,messages):
        result=deepcopy(self.preparations[digest(messages)])
        result['synthetic_messages']=deepcopy(messages)
        return result
    def generate(self,prepared,seed,deadline):
        self.calls+=1;p,stage=prior.from_messages(prepared['synthetic_messages'])
        self.requests.append({'messages':deepcopy(prepared['synthetic_messages']),'seed':seed})
        answer=correct_answer(p,stage)
        raw=json.dumps(answer,ensure_ascii=False,separators=(',',':'))
        if self.transform:raw=self.transform(self.calls,p,stage,answer)
        return {'output_token_ids':[123,248046],'decoded_with_special_tokens':raw+'<|im_end|>',
                'answer_text':raw,'finish_reason':'EOS','generation_seconds':0.0,
                'peak_vram_bytes':0,'seed':seed,'synthetic_fixture':True}
