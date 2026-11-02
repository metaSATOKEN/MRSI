# Supplement S1: Evidence Map for Failure Analysis and Design Principles

October 13, 2026 | Corresponds to [English v0.3](manuscript-en-v0.3-2026-10-13.md) and [Japanese v0.6](manuscript-ja-v0.6-2026-10-13.md) | Internal, private, no deletion deadline

This index supports evidence checking. The manuscript itself explains the tasks, manipulations, terms, and cases needed to understand the argument. The synthesis adds no experiments, repairs to original responses, or changes to formal scoring. Links below lead to specified source versions and original results.

## 1. Source Versions

| Reference | Source | Role in this synthesis |
|---|---|---|
| 1 | [Report 1, Japanese v0.11](../paper-01/MRSI_Paper1-ja-v1.0.md) | Provenance defects, local storage versus end-to-end outcomes, revocation and deferral |
| 2 | [Report 2, Japanese v0.4](../paper-02/MRSI_Paper2-ja-v1.0.md) | Four field-control branches, post-update rollback, purpose-specific use and two cycles |
| 3 | [Report 3, Japanese v0.2](../paper-03/MRSI_Paper3-ja-v1.0.md) | Support timing, actual paths with incorrect acceptance, fixed-input repetition |
| 6 | [Report 4, Japanese v0.2](../paper-04/MRSI_Paper4-ja-v1.0.md) | Three-role actual votes, approval-state readout, comparison fields and new materials |
| 4–5 | Failure Studies v1.8 and Autonomous LLM System Design v1.16 in Meteon Collected Edition v1.1 (source not bundled) | Organization around contracts and failure paths, followed by positive design requirements; not added to the four reports' experimental evidence |

English versions of [Report 1](../paper-01/MRSI_Paper1-en-v1.0.md), [Report 2](../paper-02/MRSI_Paper2-en-v1.0.md), [Report 3](../paper-03/MRSI_Paper3-en-v1.0.md), and [Report 4](../paper-04/MRSI_Paper4-en-v1.0.md) are also available.

The organizational references were Failure Studies Sections 1–3 and its integrated failure paths, and Autonomous LLM System Design Section 3, Part III, and Appendix A. Their taxonomies and 13 principles were not copied into this report's counts. The seven principles are a synthesis after the four reports. This was not a renewed primary-literature search; each source report's related-work section provides an entry point to the relevant literature.

## 2. Main Observations and Primary Records

| Manuscript location | Case or result | Formal results and existing checks |
|---|---|---|
| Appendix C: additional provenance defects | SM02 G03/B retained an old ID; RC01 G03/B produced an ID absent from input. Both combined correct content with inherited incorrect provenance | [SM02 results](../../docs/study2/shared-merge-02-results-v0.1-2026-09-19.md), [RC01 results](../../docs/study2/row-carry-01-results-v0.1-2026-09-19.md), Report 1 Section 5.1 |
| Section 4.1: one-character customer-ID omission | E1-G49/B: final `2` omitted outside the copied fields; later cat/paper answer correct with the same incorrect ID | [Worked example and complete records](../paper-01/examples-v0.1-2026-09-23.md), Report 1 Section 3.4. Rewriting retained the correct customer ID at both stages |
| Section 4.1: local versus end-to-end success | SELECT shared rows 256/256; end-to-end 59/64 versus 59/64; one unresolved REWRITE outcome; interval envelope −17.36 to 16.60 percentage points | [Formal combined analysis](../../supplements/paper-01-pair-resume1-20260921/combined-analysis.json), [component checks](../../supplements/paper-01-e1-components/observations.json), Report 1 Section 5.2 and Appendix D |
| Section 4.2: rollback after adoption | CU01: adoption 16/16, unaffected information 32/32, rollback 14/16 | [Results](../../experiments/CU01/docs/customer-update-01-result-2026-09-26.md), [aggregation](../../experiments/CU01/expected-result.json), [14 input/proposal/storage/readout traces](../../supplements/customer-update-01-result-20260926/proposal-diagnostics.json) |
| Sections 4.2 and 6.2: dog 77 / cat 76 | CU01-C06-R1/A. Section 4.2 is an observation; Section 6.2 is a proposed design check using the same values | [Original example](../../supplements/customer-update-01-result-20260926/example.json) |
| Section 4.3 and Table 3: four field-control branches | OR01: 18 materials × two repetitions, the same 36 proposals, 144 branches. Four own-field repairs overlapped with shared-field defects | [Results](../../experiments/OR01/docs/owner-recency-01-result-2026-09-25.md), [formal reaggregation](../../experiments/OR01/expected-result.json), [all branch diagnostics](../../supplements/owner-recency-01-result-20260925/branch-diagnostics.json) |
| Section 4.4: incorrect acceptance of total 37 | ST02-EARLY-N05-LOWER: A/B own recommendations digital, candidates 45/37, acceptance of 37, both USE responses conforming | [ST02 results](../../experiments/ST02/docs/summary-timing-02-result-2026-09-29.md), [reaggregation](../../experiments/ST02/expected-result.json), [raw-response review](../../supplements/summary-timing-02-20260929/reason-review.md) |
| Section 4.4: inapplicable recheck | RECHECK on that path was SKIPPED_BY_PROTOCOL because no COUNTER was generated | `report.by_slot` in the above reaggregation; [runtime branch](../../reference-code/summary_timing_01_runtime.py). Not missingness or an execution error |
| Section 4.4: three repetitions of incorrect acceptance | JR01-R1/R2/R3-EARLY-N05-LOWER-CONFIRM; old own note fixed, not connected to new FORM outputs | [JR01 results](../../experiments/JR01/docs/judgment-repeat-01-result-2026-09-29.md), [all-response diagnostics](../../supplements/judgment-repeat-01-20260929/diagnostics.json), [80 fixed inputs](../../experiments/JR01/design/source-inputs.json) |
| Section 4.6: changes in defect location | JR01-LATE-N05-DUPLICATE: B/C/V across three repetitions were true/false/false, true/false/false, false/true/false | Above JR01 diagnostics; [raw-response review](../../supplements/judgment-repeat-01-20260929/reason-review.md) |
| Section 4.6: endpoint versus intermediate state | ST01/ST02: own preservation 15/24 to 24/24 in each trial; USE 48/48 under every condition | [ST01 reaggregation](../../experiments/ST01/expected-result.json), ST02 reaggregation, [Report 3 extracts](../paper-03/evidence-extract-v0.1-2026-09-29.json) |
| Principle 6: appropriate deferral | E2: incorrect ID + ID-only notice left the target unidentified and retained records with deferral. Detailed notices could uniquely match the constructed targets | `analysis.E2` in the formal combined analysis; Report 1 Sections 4.3 and 5.3. Nonidentifiability itself is not an empirical discovery |
| Principle 7: judge defects | BJ01: 53 agreements, four disagreements, seven unresolved out of 64; four extra-field defects missed | [Fixed results](../../experiments/BJ01/docs/boundary-judge-01-result-2026-09-28.md). The seven unresolved outputs were not repaired and added to formal success |
| Section 4.4: three-role incorrect hold and faithful readout | TB01 T02/C: HOLD on total 90; votes 35/36, readout 72/72 | [Formal results](../../experiments/TB01/docs/three-role-boundary-01-result-2026-10-13.md), [reaggregation](../../experiments/TB01/expected-result.json), [Report 4 original-input/response extracts](../paper-04/evidence-extract-v0.1-2026-10-13.json) |
| Section 4.5 and Table 4: missing vote described as explicit hold | TAR01: own three axes, agreement, and execution each 54/54; approval states 53/54; success across all three states in 17/18 matched triplets | [Formal results](../../experiments/TAR01/docs/three-role-approval-readout-01-result-2026-10-13.md), [reaggregation](../../experiments/TAR01/expected-result.json), [repetition comparison](../../experiments/TAR01/analysis/repeat-comparison.json) |
| Principle 7: inspectable comparison fields versus performance | TCV01: 52/54 versus 54/54; TCV02: both 54/54. Each used three materials and 54 matched pairs | [TCV01 results](../../experiments/TCV01/docs/three-role-comparison-vote-01-result-2026-10-13.md), [TCV02 results](../../experiments/TCV02/docs/three-role-comparison-vote-02-result-2026-10-13.md), [Report 4 manuscript data](../paper-04/paper-data-v0.1-2026-10-13.json) |

The existing Report 3 extract checked during initial drafting is a reference copy carrying SHA-256 hashes for nine original aggregation/diagnostic files. Those hashes were checked before use. OR01 Table 3 was also recounted from all-branch diagnostics. For all 14 CU01 rollback cases, checks matched the new input state, old notice, model proposal, actual saved artifact, and readout. These are checks of existing records and scoring, not reruns of the model.

## 3. Evidence and Scope of the Design Principles

| Principle | Main evidence | Procedures compared or observed in actual paths | Proposed extensions |
|---|---|---|---|
| 1. Correspondence | Report 1 provenance cases and E1 | Selected-row copying and component evaluation; end-to-end superiority unconfirmed | All stored fields and rewriting locations |
| 2. Updates | OR01, CU01 | Per-observer latest-revision selection; actual customer-update paths | Controls for customer fields, same-revision conflicts, authority, validity intervals |
| 3. Coverage | OR01, SX01/SX02 | Four branches of the same proposal; two cycles with controls | Longer continued comparisons including control-off conditions |
| 4. Purpose separation | RU01, ST01/ST02, JR01 | Purpose-specific use of assigned/shared information; timing of own-summary supply | Free-form experience and isolated contributions of each supply stage |
| 5. Assessment, votes, agreement, execution | ST02, JR01, TB01, TAR01 | Incorrect votes with faithful use of actual records; per-role state readout | Performance of a complete architecture connecting the separate controller decisions |
| 6. Deferral | E2, TAR01, format-defect retention rules | Appropriate deferral under fixed conditions; missing/explicit-hold confusion | Reconfirmation of ambiguous targets, delayed/duplicate votes, subsequent use of reasons |
| 7. Evaluation | OR01, JR01, BJ01, TCV01/02, TAR01 | Component breakdowns, repetition, judge calibration, comparison/vote correspondence | Calibration on new tasks and operational evaluation of excessive control |

[Report 2 S1](../paper-02/evidence-index-v0.4-2026-09-27.md) provides entry points for purpose separation and two-cycle results. [Report 1 implementation notes](../paper-01/implementation-notes-v0.3-2026-09-23.md) cover permitted generation operations, structural checks, and parent-record transfer. Later implementation contracts are not retroactively assigned to earlier trials.

## 4. Fixed Aggregation and Interpretation Boundaries

- E1's primary p-value remains uncalculated. The brace-repair sensitivity result is not promoted to formal evidence here.
- OR01's four conditions branch from the same proposals. Its 144 branches are not 144 independent materials.
- CU01 has eight cases × two repetitions. The 14 rollbacks and 14 corresponding later responses are not counted as separate independent failures.
- ST01/ST02 have 24 paths from eight materials × three initial proposals. Some defects derive from shared formation responses.
- JR01 repeats 32 fixed formation inputs and 48 fixed confirmation inputs three times each. The panels are unconnected; old ST02 responses are not added to these repetitions.
- Different models, implementations, materials, and metrics across the four reports are not converted into a common-scale model comparison or meta-analysis.
- Faithful use of an agreement can conform to Report 3's use-stage contract while approval of the proposal is inappropriate.
- The reference architecture, proposed design checks, Table 6, and Appendix B are proposals, not measured effectiveness of an implemented complete system.
- TAR01 has two repetitions of 27 inputs from three materials, organized into 18 matched three-state triplets. MISSING/ACCEPT supply subsets/all actual votes; HOLD is constructed. Reinjection of READ outputs was not evaluated.
- TAR01's formal `agreement_execution_all_states` key includes approval-state correctness as well as agreement and execution, giving 17/18. The manuscript reports all-six-axis success across the three states, also 17/18. Agreement/execution alone gives 18/18 in a separate post-acquisition aggregation; do not substitute that value based on the key name.
- The two- and three-role studies are not a matched comparison changing only group size, and results are not extrapolated to arbitrary N.

## 5. Code and Figures for the Revised Architecture

The [standalone English code](examples/design_samples_complete_en_v0_2.py) is identical to Appendix D and uses the standard library only. Observation selection reuses the earlier function. Joint-assignment writing is conditioned on execution authorization, and numerical assessment, projection of original votes, unanimous agreement, and execution decisions are separate. This new reference design neither overwrites original LLM responses nor has been applied to the original experimental pipeline.

- Received votes remain unchanged. Votes bound to the target are represented by role, distinguishing MISSING, HOLD, and ACCEPT.
- Unanimous approval of a suboptimal proposal remains AGREED, with the original votes retained; only execution becomes DEFERRED under the task criterion.
- The illustrative rule requires every participant's explicit vote, including the proposer's. It does not reproduce the original two-role agreement rule.
- The 18 tests check valid two-/three-role progress and boundary conditions. They do not measure model performance at larger group sizes or the complete architecture's effectiveness.
- Figure 1 shows observation from generation to subsequent use. Figure 2 separates proposal assessment from actual-vote processing. [English figure sources and PNG/SVG files](figures/README.md) accompany the manuscript.
