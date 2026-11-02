# Paper 4: Evidence Index

October 13, 2026 | v0.1 | [English manuscript](manuscript-en-v0.1-2026-10-13.md)

This index connects the manuscript's tables and examples to original records. The task, materials, scoring, and repetition units are explained in the manuscript and its appendices. Original ZIP archives, fixed designs, and execution code are retained unchanged. Preparing this manuscript involved no model calls or changes to formal scores. Original experimental prompts and responses remain in their recorded language; the English manuscript and this index do not replace them.

## 1. Findings and Evidence

| Manuscript location | Item to check | Primary records and summaries |
|---|---|---|
| Table 6, Figure 2, Section 5.1 | Incorrect HOLD on a higher-total proposal and correct subsequent pending agreement | [TB01 report (Japanese)](../../experiments/TB01/docs/three-role-boundary-01-result-2026-10-13.md), [reaggregation](../../experiments/TB01/expected-result.json) |
| Repetition in Section 5.1 | Three generations for each of 18 fixed inputs; incorrect hold and incorrect approval | [TVR01 report (Japanese)](../../experiments/TVR01/docs/three-role-vote-repeat-01-result-2026-10-13.md), [reaggregation](../../experiments/TVR01/expected-result.json) |
| Tables 7–8, Section 5.2 | MISSING/HOLD/ACCEPT, six scoring dimensions, and matched triplets | [TAR01 report (Japanese)](../../experiments/TAR01/docs/three-role-approval-readout-01-result-2026-10-13.md), [reaggregation](../../experiments/TAR01/expected-result.json), [post hoc supplement](../../experiments/TAR01/analysis/supplementary-analysis.json) |
| Tables 9–10, Section 5.3 | Comparison field versus DIRECT; 54 matched pairs | [TCV01 report (Japanese)](../../experiments/TCV01/docs/three-role-comparison-vote-01-result-2026-10-13.md), [reaggregation](../../experiments/TCV01/expected-result.json) |
| Tables 9–10, Section 5.3 | New numerical cases with the same two conditions | [TCV02 report (Japanese)](../../experiments/TCV02/docs/three-role-comparison-vote-02-result-2026-10-13.md), [reaggregation](../../experiments/TCV02/expected-result.json) |
| Appendices A–C | Response counts, all six cases, and generation settings | Trial summaries, `case_inputs`, and `model` in [paper data](paper-data-v0.1-2026-10-13.json) |

Paper data contain extracts from existing reaggregations and cost counts from `response.json` files in the original archives. SHA-256 hashes of source results appear under `sources`. The 459 completed responses are an inventory count, not an independent sample size or the denominator of a single success rate.

## 2. Original Archives and Designs Fixed Before Execution

| Trial | Original ZIP | Design card fixed before execution | Local analysis code |
|---|---|---|---|
| TB01 | [Completed run](../../experiments/TB01/archives/npp-tb01-result-20261013-041945-c6e2c94d.zip) | [Card](../../experiments/TB01/docs/three-role-boundary-01-v0.1-2026-10-13.md) | [Aggregator](../../reference-code/aggregate_three_role_boundary_01.py) |
| TVR01 | [Original ZIP](../../experiments/TVR01/archives/npp-tvr01-result-20261013-045940-cf404568.zip) | [Card](../../experiments/TVR01/docs/three-role-vote-repeat-01-v0.1-2026-10-13.md) | [Aggregator](../../reference-code/aggregate_three_role_vote_repeat_01.py) |
| TCV01 | [Original ZIP](../../experiments/TCV01/archives/npp-tcv01-result-20261013-053413-76c1649c.zip) | [Card](../../experiments/TCV01/docs/three-role-comparison-vote-01-v0.1-2026-10-13.md) | [Aggregator](../../reference-code/aggregate_three_role_comparison_vote_01.py) |
| TCV02 | [Original ZIP](../../experiments/TCV02/archives/npp-tcv02-result-20261013-061923-878369ad.zip) | [Card](../../experiments/TCV02/docs/three-role-comparison-vote-02-v0.1-2026-10-13.md) | [Aggregator](../../reference-code/aggregate_three_role_comparison_vote_02.py) |
| TAR01 | [Original ZIP](../../experiments/TAR01/archives/npp-tar01-result-20261013-071229-08c825b9.zip) | [Card](../../experiments/TAR01/docs/three-role-approval-readout-01-v0.1-2026-10-13.md) | [Aggregator](../../reference-code/aggregate_three_role_approval_readout_01.py) |

The initial TB01 preparation failure is retained in a [separate archive](../../experiments/TB01/preparation-attempt/archives/npp-tb01-result-20261013-035934-aaa05b73.zip). It produced no generations and is excluded from the completed run's 126 responses.

Each archive includes the pre-execution design in `frozen/`, distributed code in `code/`, and actual inputs, original answers, and saved records in `responses/`. Verification uses trusted local aggregators and the originally distributed payload, without executing code returned inside result archives.

## 3. Checking the Examples

The [evidence extracts](evidence-extract-v0.1-2026-10-13.json) were selected after execution for explanation.

- **TB01:** All nine voting/readout responses from T02's higher-total path in the first replicate, plus C's vote and three-vote readout in the second replicate: 11 records. These show the original experiences, totals of 90 and 84, C's own DIGITAL recommendation, the actual HOLD vote, and PENDING in the three subsequent readouts.
- **TAR01:** All six records for N01 read by A: three states × two replicates. These show identical JSON values for MISSING and HOLD in the first replicate, correct MISSING in the second, and coexistence of an own DIGITAL recommendation with a joint PAPER assignment when all votes are ACCEPT.

Each item includes the complete original `input.json`, the interpreted user payload, original `answer.txt`, JSON values, formal scores, and relative archive/member locations. Original answer strings are unchanged. Only the JSON example displayed in the manuscript has its whitespace reformatted.

The [existing TCV01 extracts](../../experiments/TCV01/analysis/evidence-extract.json) cover both conditions and all three replicates for the two inputs in Table 9. The [TAR01 repeat comparison](../../experiments/TAR01/analysis/repeat-comparison.json) covers all 27 inputs.

## 4. Metric Names and Their Contents

| Saved key | What it includes | Value and interpretation in the manuscript |
|---|---|---|
| `metrics.approval_state` | All A/B/C states in one response | 53/54 responses |
| `triplet_totals` | All six dimensions in each of the three states | 17/18 matched triplets |
| `paired_metrics.agreement_execution_all_states` | Three dimensions: approval state + agreement + execution | 17/18; not agreement and execution alone |
| Supplementary `agreement_and_execution_only_triplets` | Two dimensions: agreement + execution only | 18/18; post hoc supplementary summary |

Formal keys and scores remain unchanged. The 18 responses to constructed HOLD votes are distinguished from the 36 responses to subsets or full sets of actual votes.

## 5. Recalculation

Rebuild both table data and worked examples from the 26 recorded inputs using the [portable builder](../../tools/rebuild_paper04_data.py). [Execution instructions](../../RUNNING.md)
