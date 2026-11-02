"""CPU-only TCV01 fixtures: saved tokens for DIRECT; synthetic tokens for COMPARE."""
from copy import deepcopy
import three_role_boundary_01_fixtures as base


def ideal(payload, stage):
    answer=base.ideal(payload,stage)
    if 'comparison' in payload['schema']['properties']:
        proposed=payload['proposal']['candidate_id']
        other=next(c['candidate_id'] for c in payload['candidates'] if c['candidate_id']!=proposed)
        totals={c['candidate_id']:c['expected_total'] for c in payload['candidates']}
        comparison={'candidate_id':proposed,'other_candidate_id':other,
                    'relation':'HIGHER' if totals[proposed]>totals[other] else 'LOWER'}
        answer={'own':answer['own'],'comparison':comparison,'vote':answer['vote']}
    return answer


class SyntheticBackend(base.SyntheticBackend):
    def __init__(self,design,mutate=None):
        self.fixed=design['source']['items']
        def adapted(answer,payload,stage,call):
            value=ideal(payload,stage)
            return mutate(value,payload,stage,call) if mutate else value
        super().__init__(adapted)

    def prepare(self,messages):
        prior=next((x for x in self.fixed if x['messages']==messages),None)
        return deepcopy(prior['prepared']) if prior else super().prepare(messages)
