"""Executable illustrations for manuscript v0.3; no model calls or file writes.

Inputs are already validated, attributed, and bound to one task/snapshot.
Sample 1 restates the core of OR01 latest_rows; its HOLD interface is new.
Samples 2 and 3 are design proposals, not the code used in the LLM trials.
"""

# BEGIN sample1
from copy import deepcopy

def select_observation(rows, owner):
    candidates = [r for r in rows if r["observer"] == owner]
    if not candidates:
        return {"status": "HOLD", "reason": "MISSING_OWNER"}
    by_version = {}
    for row in candidates:
        version = row["revision"]
        if version in by_version and by_version[version] != row:
            return {"status": "HOLD", "reason": "SAME_VERSION_CONFLICT"}
        by_version[version] = row
    latest = by_version[max(by_version)]
    return {"status": "READY", "row": deepcopy(latest)}
# END sample1


# BEGIN sample2
from copy import deepcopy

def record_assignment(state, agreement):
    if agreement["status"] != "COMMITTED":
        return {"status": "HOLD", "reason": "NO_COMMITTED_AGREEMENT"}
    proposal = agreement["proposal"]
    updated = deepcopy(state)
    updated["joint_assignment"] = {
        "medium": proposal["allocation"][state["role"]],
        "proposal_id": proposal["id"],
        "proposal_version": proposal["version"],
        "evidence_version": agreement["evidence_version"],
    }
    return {"status": "READY", "state": updated}
# END sample2


# BEGIN sample3
from copy import deepcopy

def commit_agreement(proposal, reply, scores, evidence_version):
    key = (proposal["id"], proposal["version"], evidence_version)
    target = (reply["proposal_id"], reply["proposal_version"], reply["evidence_version"])
    if proposal["evidence_version"] != evidence_version or target != key:
        return {"status": "HOLD", "reason": "STALE_OR_DIFFERENT_TARGET"}
    allocation = proposal["allocation"]
    if (reply["action"] != "ACCEPT" or reply["author"] == proposal["author"]
            or reply["allocation"] != allocation):
        return {"status": "HOLD", "reason": "NO_MATCHING_PEER_ACCEPTANCE"}
    if set(allocation) != {"A", "B"} or sorted(allocation.values()) != ["DIGITAL", "PAPER"]:
        return {"status": "HOLD", "reason": "RESOURCE_CONFLICT"}
    total = sum(scores[r][allocation[r]] for r in ("A", "B"))
    best = max(scores["A"]["PAPER"] + scores["B"]["DIGITAL"],
               scores["A"]["DIGITAL"] + scores["B"]["PAPER"])
    if total < best:
        return {"status": "HOLD", "reason": "LOWER_TOTAL"}
    return {"status": "COMMITTED", "proposal": deepcopy(proposal),
            "evidence_version": evidence_version}
# END sample3
