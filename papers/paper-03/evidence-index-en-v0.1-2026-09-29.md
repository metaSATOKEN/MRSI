# Supplement S1: Evidence Index for the Third Report

September 29, 2026. This index accompanies [English manuscript v0.1](MRSI_Paper3-en-v1.0.md), translated from the author-approved [Japanese v0.2](MRSI_Paper3-ja-v1.0.md). Underlying plans and result reports remain in their original language. Materials are private, retained without a deletion deadline. Relative links refer to the current research folder; no public package or persistent identifier has yet been assigned.

## 1. Claims and supporting records

| Manuscript location | Evidence | What can be checked directly |
| --- | --- | --- |
| Section 3; Table 3 | [ST02 fixed plan](../../experiments/ST02/docs/summary-timing-02-plan-v0.1-2026-09-29.md), Section 3; [extracted tables and examples](evidence-extract-v0.1-2026-09-29.json) | N05 projections of 17/27 and 18/20; joint totals 45/37 |
| Section 4; Figure 1; Tables 4–5 | [ST01 plan](../../experiments/ST01/docs/summary-timing-01-plan-v0.1-2026-09-29.md); [ST02 plan](../../experiments/ST02/docs/summary-timing-02-plan-v0.1-2026-09-29.md); [JR01 plan](../../experiments/JR01/docs/judgment-repeat-01-plan-v0.1-2026-09-29.md) | Condition differences, reused formation responses, stage connections, scoring units, and stopping rules |
| Section 4.1; Figure 2 | [80 fixed inputs](../../experiments/JR01/design/source-inputs.json); [old role-specific notes](../../experiments/JR01/design/source-parent-evidence.json); [240 scheduled generations](../../experiments/JR01/design/requests.json) | Across both conditions: 32 formation inputs × 3 and 48 confirmation inputs × 3; no new formation-to-confirmation connection |
| Section 5.1; Table 6 | [ST01 aggregate](../../experiments/ST01/expected-result.json); [ST02 aggregate](../../experiments/ST02/expected-result.json) | I/J/K/G, incorrect agreements, and stage-level responses under `report.by_condition` |
| Section 5.1; Table 7 | [JR01 aggregate](../../experiments/JR01/expected-result.json) | Formation results under `report.by_repeat`; three-repetition categories under `fixed_input_stability` |
| Section 5.2; Table 8; JSON excerpt | [ST02 diagnostics](../../supplements/summary-timing-02-20260929/diagnostics.json); [original-response reading record](../../supplements/summary-timing-02-20260929/reason-review.md) | Actual input, incorrect acceptance, and subsequent use by both roles for EARLY N05 LOWER |
| Section 5.3; Tables 9–10 | [JR01 response diagnostics](../../supplements/judgment-repeat-01-20260929/diagnostics.json); [original-response reading record](../../supplements/judgment-repeat-01-20260929/reason-review.md) | All three responses and fixed inputs for N05 LOWER/DUPLICATE and N02 OPTIMAL |
| Appendix B; Table B1 | `progression` in ST01/ST02 aggregates and `stage_components` in diagnostics | Constructed diagnostics and the components of unmet progression criteria |

The extracted JSON is a reference copy derived from existing aggregates and diagnostics for the three main trials. It contains principal aggregates under `tables`, responses and inputs under `examples`, and hashes of nine source files under `source_sha256`. It performs no rescoring or new estimation. The [extraction script](../../reference-code/paper03/extract_evidence.py) is retained.

## 2. Primary records and fixed designs

### ST01: Supply timing with previously used materials

- [Result report](../../experiments/ST01/docs/summary-timing-01-result-2026-09-29.md), [fixed plan](../../experiments/ST01/docs/summary-timing-01-plan-v0.1-2026-09-29.md), and [pre-execution card](../../supplements/prereg/summary-timing-01-v0.1.md).
- Result manifest (see the evidence index), [aggregate](../../experiments/ST01/expected-result.json), and [diagnostics](../../supplements/summary-timing-01-20260929/diagnostics.json). A byte-for-byte copy of the original ZIP is retained in the result directory.
- [Separate verification code](../../supplements/summary-timing-01-results-20260929/independent_check.py) and [verification output](../../supplements/summary-timing-01-results-20260929/independent-check.json).
- [Original-response reading record](../../supplements/summary-timing-01-20260929/reason-review.md) and [completion record](../../supplements/summary-timing-01-20260929/reason-review.json).

### ST02: Supply timing with previously unused numerical materials

- [Result report](../../experiments/ST02/docs/summary-timing-02-result-2026-09-29.md), [fixed plan](../../experiments/ST02/docs/summary-timing-02-plan-v0.1-2026-09-29.md), and [pre-execution card](../../supplements/prereg/summary-timing-02-v0.1.md).
- [Original ZIP](../../experiments/ST02/archives/npp-st02-result-20260929-073815-2a1541bf.zip) and manifest (see the evidence index). ZIP SHA-256: `7086be6367b5e83f3ccefdb07ac95b36aad31623c95a08b9e52980dc4cd8a7a1`.
- [Separate verification code](../../supplements/summary-timing-02-results-20260929/independent_check.py) and [verification output](../../supplements/summary-timing-02-results-20260929/independent-check.json).
- [Inventory used to check material novelty](../../supplements/summary-timing-02-design-20260929/prior-material-inventory.json). N01–N08 identify strata; experience values and IDs differ from ST01 materials with the same labels.

Table 8 and the excerpt correspond to `ST02-EARLY-N05-LOWER-CONFIRM`, `ST02-EARLY-N05-LOWER-USE-A`, and `ST02-EARLY-N05-LOWER-USE-B`. The initial joint record ID is `Q4A67A15B6A`; the confirmation record ID is `Q906DCEFF8B`. The aggregate's `by_slot` entries contain saved responses and scores. Rendered inputs and raw responses are retained in the original ZIP. Reference fields omitted from the excerpt remain in the complete response.

The recheck omission discussed in Section 6.2 corresponds to `ST02-EARLY-N05-LOWER-RECHECK`, whose activation condition is `reply.action == COUNTER` and whose status is `SKIPPED_BY_PROTOCOL`. It is a protocol-defined non-applicable stage, not missing data. The [execution code](../../reference-code/summary_timing_01_runtime.py) and [ST02 scoring code](../../reference-code/summary_timing_02_scoring.py) implement the same branch.

### JR01: Three repetitions of fixed inputs

- [Result report](../../experiments/JR01/docs/judgment-repeat-01-result-2026-09-29.md), [fixed plan](../../experiments/JR01/docs/judgment-repeat-01-plan-v0.1-2026-09-29.md), and [pre-execution card](../../supplements/prereg/judgment-repeat-01-v0.1.md).
- [Original ZIP](../../experiments/JR01/archives/npp-jr01-result-20260929-092936-6e2d67ef.zip) and manifest (see the evidence index). ZIP SHA-256: `520e0cd052adcd6c6da8927674db38341611963f76591362a7df90cbeb1cddb3`.
- [80 fixed inputs](../../experiments/JR01/design/source-inputs.json), [old parent records](../../experiments/JR01/design/source-parent-evidence.json), and [240 scheduled generations](../../experiments/JR01/design/requests.json).
- [Separate verification code](../../supplements/judgment-repeat-01-results-20260929/independent_check.py) and [verification output](../../supplements/judgment-repeat-01-results-20260929/independent-check.json).

The example response IDs are `JR01-R{1,2,3}-{EARLY,LATE}-N05-{LOWER,DUPLICATE}-CONFIRM` and `JR01-R{1,2,3}-{EARLY,LATE}-N02-OPTIMAL-CONFIRM`. The diagnostics' `all_responses` entries contain raw text, actual payloads, expected values, and component scores for all 240 responses. Newly generated formation responses do not enter confirmation. Old ST02 responses are not added to the denominators of the three fresh repetitions.

## 3. Preceding exploration

| Trial | Fixed result report | Interpretation note |
| --- | --- | --- |
| ES01 | [Own experience and joint records](../../experiments/ES01/docs/experience-shared-01-result-2026-09-28.md) | Joint-allocation reversal used diagnostic copies, not a new agreement process |
| AC01 | [Agreement on tied candidates](../../experiments/AC01/docs/agreement-confirm-01-result-2026-09-28.md) | Its exchange and input contracts differ from those of the main trials |
| EU01 | [Experience updates](../../experiments/EU01/docs/experience-update-01-result-2026-09-28.md) | Own updates and joint allocation are separate metrics |
| FC01 | [Candidate selection](../../experiments/FC01/docs/feasible-choice-01-result-2026-09-28.md) | A local method comparison |
| FC02 | [Candidate selection with new experience](../../experiments/FC02/docs/feasible-choice-02-result-2026-09-28.md) | FC01 results are not reused as a control for new materials |
| CT01 | [Joint candidate totals](../../experiments/CT01/docs/candidate-totals-01-result-2026-09-28.md) | Optimal selection, role-specific fields, and partner confirmation have separate scores |
| OS01 | [Own-experience summaries](../../experiments/OS01/docs/own-summary-01-result-2026-09-28.md); [post hoc boundary audit](../../docs/study2/own-summary-01-boundary-audit-2026-09-28.md) | The 56 formally unresolved responses remain separate from normalized reference evaluation |
| BJ01 | [Boundary judge](../../experiments/BJ01/docs/boundary-judge-01-result-2026-09-28.md) | Judge calibration is not pooled into main-experiment accuracy |
| CS01 | [Support at partner confirmation](../../experiments/CS01/docs/confirm-support-01-result-2026-09-29.md) | Main comparisons with appropriate proposals and controls with incorrect proposals remain separate |
| CR01 | [Counterproposal recheck](../../experiments/CR01/docs/counter-recheck-01-result-2026-09-29.md) | Correct final answers are distinct from intermediate formation correctness |

Each report links its fixed plan, original archive, aggregates, scoring code, and verification. Finalized versions of the first and second reports remain unchanged.
