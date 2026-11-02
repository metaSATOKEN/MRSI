"""Synthetic answers with saved prior input tokens; never used for research answers."""
from copy import deepcopy
import three_role_boundary_01_fixtures as base

ideal=base.ideal


class SyntheticBackend(base.SyntheticBackend):
    def __init__(self, design, mutate=None):
        super().__init__(mutate)
        self.fixed=design['source']['items']

    def prepare(self,messages):
        # This is a fixture lookup, NOT independent tokenization.
        return deepcopy(next(x['prepared'] for x in self.fixed if x['messages']==messages))
