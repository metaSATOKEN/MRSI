"""Print synthetic examples for manuscript v0.3; no LLM calls."""
import json
from copy import deepcopy
from design_samples_v0_1 import select_observation, record_assignment, commit_agreement

rows = [
    {"observer": "A", "revision": 2, "origin_id": "OA2", "paper": "ALL", "digital": "NOT_ALL"},
    {"observer": "B", "revision": 99, "origin_id": "OB99", "paper": "ALL", "digital": "NOT_ALL"},
    {"observer": "A", "revision": 3, "origin_id": "OA3", "paper": "NOT_ALL", "digital": "ALL"},
]
scores = {"A": {"PAPER": 17, "DIGITAL": 27}, "B": {"PAPER": 18, "DIGITAL": 20}}
proposal = {"id": "p1", "version": 1, "evidence_version": "exp-7", "author": "A",
            "allocation": {"A": "DIGITAL", "B": "PAPER"}}
reply = {"author": "B", "action": "ACCEPT", "proposal_id": "p1", "proposal_version": 1,
         "evidence_version": "exp-7", "allocation": deepcopy(proposal["allocation"])}
state = {"role": "B", "own_judgment": {"choice": "DIGITAL", "refs": ["b1", "b2"]},
         "joint_assignment": None}
agreement = commit_agreement(proposal, reply, scores, "exp-7")
lower_proposal, lower_reply = deepcopy(proposal), deepcopy(reply)
lower_proposal["allocation"] = {"A": "PAPER", "B": "DIGITAL"}
lower_reply["allocation"] = deepcopy(lower_proposal["allocation"])
print(json.dumps({
    "note": "Synthetic code examples, not additional experimental observations.",
    "sample1_A_latest": select_observation(rows, "A"),
    "sample2_B_assignment": record_assignment(state, agreement),
    "sample3_total45": agreement,
    "sample3_total37": commit_agreement(lower_proposal, lower_reply, scores, "exp-7"),
}, ensure_ascii=False, indent=2))
