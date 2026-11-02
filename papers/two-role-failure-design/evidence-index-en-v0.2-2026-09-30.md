# Supplement S1: Evidence for the Failure Analysis and Design Principles

September 30, 2026 | Companion to [English draft v0.2](manuscript-en-v0.2-2026-09-30.md) | Private; no deletion deadline

This index connects claims to their evidence. The manuscript itself explains the tasks, operations, terminology, cases, and executable examples needed for comprehension. The English index follows [Japanese S1 v0.5](evidence-index-v0.5-2026-09-30.md); primary records remain in their original language. This synthesis adds no experiment, repair of original responses, or change to formal research scores.

## 1. Source Versions

| Reference | Source | Role in this report |
|---|---|---|
| 1 | [Report 1, Japanese v0.11](../paper-01/manuscript-v0.11-2026-09-23.md) | Provenance defects, local storage versus end-to-end success, revocation and deferral |
| 2 | [Report 2, Japanese v0.4](../paper-02/manuscript-ja-v0.4-2026-09-27.md) | Four-way field comparison, post-update rollback, purpose-specific use and two cycles |
| 3 | [Report 3, Japanese v0.2](../paper-03/manuscript-ja-v0.2-2026-09-29.md) | Support timing, actual paths with incorrect acceptance, fixed-input repetitions |
| 4–5 | *Failure Studies* v1.8 and *Autonomous LLM System Design* v1.16 in Meteon Collected Edition v1.1 (see the evidence index) | Organizing requirements and failure paths, and moving from observations to positive design principles; not pooled with experimental evidence from the three reports |

The Meteon sources were consulted at Sections 1–3 and the integrated failure paths in *Failure Studies*, and Section 3, Part III, and Appendix A in *Autonomous LLM System Design*. Their failure classes or 13 principles were not adopted as this report's classification count. The seven principles are a synthesis after reading the three reports. This translation does not add a new primary-literature review; the source reports' related-work sections provide entry points to adjacent work.

## 2. Observations and Primary Records

| Manuscript location | Case or result | Formal results and existing checks |
|---|---|---|
| Appendix C: additional provenance defects | Old ID in SM02 G03/B; ID absent from input in RC01 G03/B; correct content with inherited incorrect IDs in both | [SM02 results](../../docs/study2/shared-merge-02-results-v0.1-2026-09-19.md), [RC01 results](../../docs/study2/row-carry-01-results-v0.1-2026-09-19.md), Report 1 Section 5.1 |
| Section 4.1: one-character customer-ID omission | E1-G49/B: final `2` omitted in the private field outside mechanical copying; correct cat/paper response inherits the ID | [Worked example and complete records](../paper-01/examples-v0.1-2026-09-23.md), Report 1 Section 3.4; rewriting retained the correct ID at storage and use |
| Section 4.1: local and end-to-end outcomes | SELECT shared rows 256/256; end-to-end 59/64 versus 59/64; one unresolved REWRITE group; interval envelope −17.36 to 16.60 percentage points | [Formal combined analysis](../../supplements/paper-01-pair-resume1-20260921/combined-analysis.json), [component checks](../../supplements/paper-01-reader-claude-20260922/observations.json), Report 1 Section 5.2 and Appendix D |
| Section 4.2: rollback after adoption | CU01: adoption 16/16, unaffected-role retention 32/32, rollback 14/16 | [Results](../../experiments/CU01/docs/customer-update-01-result-2026-09-26.md), [aggregation](../../experiments/CU01/expected-result.json), [inputs, proposals, saved states, and use for the 14 cases](../../supplements/customer-update-01-result-20260926/proposal-diagnostics.json) |
| Sections 4.2 and 6.2: dog 77 / cat 76 | CU01-C06-R1/A: Section 4.2 describes the observation; Section 6.2 uses its values for a proposed design check | [Original example](../../supplements/customer-update-01-result-20260926/example.json) |
| Section 4.3 and Table 3: four-way comparison | OR01: 18 materials × two repetitions, 36 shared proposals, 144 branches; four own-field repairs overlap with shared-field defects | [Results](../../experiments/OR01/docs/owner-recency-01-result-2026-09-25.md), [formal reaggregation](../../experiments/OR01/expected-result.json), [all branches](../../supplements/owner-recency-01-result-20260925/branch-diagnostics.json) |
| Section 4.4: total-37 acceptance | ST02-EARLY-N05-LOWER: both own recommendations digital, candidate totals 45/37, 37 accepted, both USE responses conform | [ST02 results](../../experiments/ST02/docs/summary-timing-02-result-2026-09-29.md), [reaggregation](../../experiments/ST02/expected-result.json), [response review](../../supplements/summary-timing-02-20260929/reason-review.md) |
| Section 4.4: inapplicable recheck | RECHECK on that path was `SKIPPED_BY_PROTOCOL`, because no COUNTER occurred | `report.by_slot` in the preceding reaggregation; [runtime branch](../../reference-code/summary_timing_01_runtime.py). Not missing data or an execution error |
| Section 4.4: three incorrect acceptances | JR01-R1/R2/R3-EARLY-N05-LOWER-CONFIRM; original own notes fixed, new FORM outputs not connected | [JR01 results](../../experiments/JR01/docs/judgment-repeat-01-result-2026-09-29.md), [all-response diagnostics](../../supplements/judgment-repeat-01-20260929/diagnostics.json), [80 fixed inputs](../../experiments/JR01/design/source-inputs.json) |
| Section 4.5: changing defect locations | Three JR01-LATE-N05-DUPLICATE repetitions: B/C/V = true/false/false, true/false/false, false/true/false | JR01 diagnostics above; [response review](../../supplements/judgment-repeat-01-20260929/reason-review.md) |
| Section 4.5: endpoints versus intermediate states | ST01 and ST02 each: own retention 15/24 → 24/24; USE 48/48 in all conditions | [ST01 reaggregation](../../experiments/ST01/expected-result.json), ST02 reaggregation, [Report 3 evidence extract](../paper-03/evidence-extract-v0.1-2026-09-29.json) |
| Principle 6: appropriate deferral | Incorrect saved ID + ID-only notice: no guessed target, records retained and joint judgment deferred; details permit unique matching by construction | `analysis.E2` in the formal combined analysis; Report 1 Sections 4.3 and 5.3. Target non-identifiability itself is not treated as an empirical discovery |
| Principle 7: validator defects | BJ01: 53 agreements, four disagreements, seven unresolved / 64; four extra fields missed | [Fixed results](../../experiments/BJ01/docs/boundary-judge-01-result-2026-09-28.md). The seven unresolved outputs were not repaired into formal successes |

At initial synthesis, the Report 3 evidence extract was checked against its hashes of nine source aggregation/diagnostic files. Table 3 was also recounted from OR01 branch diagnostics, and all 14 CU01 rollback cases were checked for correspondence among the newer input, old notice, proposal, saved state, and readout. These were checks of existing scores and records, not model reruns. The English pass preserves those source versions and checks translation against the Japanese synthesis.

## 3. Principles, Evidence, and Scope

| Principle | Main evidence | Procedures compared or observed | Remaining design proposals |
|---|---|---|---|
| 1. Correspondence | Report 1 provenance cases and E1 | Selected-row copying and component evaluation; no established end-to-end superiority | Coverage of all fields and rewriting locations |
| 2. Updates | OR01, CU01 | Per-observer latest-revision selection and actual customer-update paths | Customer-field controls, same-revision conflicts, authority, validity intervals |
| 3. Coverage | OR01, SX01/SX02 | Four branches from the same proposal; two controlled cycles | Longer continued comparisons including no-control conditions |
| 4. Purpose separation | RU01, ST01/ST02, JR01 | Purpose-specific use of assigned/shared information and timing of own summaries | Free-form experience and separate contribution of support at each stage |
| 5. Commitment | ST02, JR01 | Incorrect acceptance, inapplicable recheck, and subsequent use | Full-system performance with a common check |
| 6. Deferral | E2, format-defect storage rules | Deferral under fixed matching rules; separation of raw and derived artifacts | Ambiguous-target clarification, repair effects and side effects |
| 7. Evaluation | OR01, JR01, BJ01 | Component decomposition, repetition, and judge calibration | Calibration for new tasks and evaluation of excessive control |

[Report 2 S1](../paper-02/evidence-index-v0.4-2026-09-27.md) links to purpose-specific use and two-cycle results. [Report 1 implementation notes](../paper-01/implementation-notes-v0.3-2026-09-23.md) cover allowed generation operations, structural validation, and parent-record transfer. Later implementation contracts are not applied retrospectively to earlier trials.

## 4. Fixed Analytical Distinctions

- E1's primary p-value remains uncalculated. The brace-repair sensitivity result is not promoted into formal evidence here.
- OR01's four conditions branch from identical proposals; 144 branches are not 144 independent materials.
- CU01 uses eight cases × two repetitions. Fourteen rollbacks and their 14 downstream responses are not additional independent failures.
- ST01/ST02 each use eight materials × three initial proposals; some defects originate in shared formation responses.
- JR01 repeats 32 formation and 48 confirmation inputs three times without connecting the panels or adding the old ST02 outputs to the new repetitions.
- Different models, implementations, materials, and metrics are not recast as a common-scale model comparison or meta-analysis.
- Faithful use may conform to Report 3's use contract even after inappropriate acceptance of a suboptimal proposal.
- The reference architecture, design-review examples, Table 5, and Appendix B are proposals, not measured evidence of their effectiveness.

## 5. Editorial History and Verification

Japanese v0.2 made the report standalone: it defined both tasks and processing actors, rewrote five cases as question/manipulation → generation/storage/use → design implications, and moved trial identifiers to Appendix C. Its primary provenance example became the existing E1-G49/B example, with SM02/RC01 retained in the appendix. Core outcomes and uncertainty were preserved. See the v0.2 revision notes (see the evidence index), [standalone-revision audit](../../supplements/two-role-failure-design-standalone-20260929/README.md), and [initial evidence verification](../../supplements/two-role-failure-design-draft-20260929/verification.json).

Japanese v0.3 added the three short code examples and input/output explanations without changing the research prose. Japanese v0.4 combined the functions, examples, helpers, all 19 tests, and entry point into Appendix D. The code ran independently of the research directory, matched the previous example output, and passed 19 tests. These illustrative tests do not contribute to research N or formal experimental results. See the v0.3 notes (see the evidence index), [code audit](../../supplements/two-role-failure-design-code-20260929/README.md), v0.4 notes (see the evidence index), and [inline-code audit](../../supplements/two-role-failure-design-inline-20260929/README.md).

The English pass translates the complete manuscript, including Appendix D, and redraws both diagrams in English. Function behavior, test conditions, identifiers, and data remain unchanged; code comments and the module description are translated. See the [translation and production notes](translation-notes-en-v0.2-2026-09-30.md) and [English-pass audit](../../supplements/two-role-failure-design-english-20260930/README.md).

## 6. Code Examples and Their Evidential Status

| Example | Source procedure or observation | Status of the published illustration |
|---|---|---|
| 1. Per-observer selection and copying | [OR01 latest_rows/transform](../../reference-code/owner_recency_01_scoring.py) | Reconstructs filtering by observer, detecting conflicts among candidates of every revision, and copying the highest-revision row. Input-catalog matching, structural validation, and source audit are omitted; exceptions become HOLD |
| 2. Separate own and joint storage | Section 4.4 and Report 3's separate own/joint evaluation | New storage example. The original experiments evaluated model-written fields rather than overwriting them with this function |
| 3. Common commitment check | Section 4.4, [original agreement logic/scoring](../../reference-code/summary_timing_01_scoring.py), [original runtime](../../reference-code/summary_timing_01_runtime.py) | New design example. The original experiment used the accepted feasible total-37 allocation as an agreement. This proposal checks adoption criteria before commitment and holds that allocation |

Example 1 represents the original conflict-detection rule, but the original LLM comparison used consistent candidates. Conflicting-input unit tests do not extend its experimental result. Examples 2 and 3 have not been connected to the original experimental pipeline. The full executable illustration and its input contract are embedded in Appendix D; [the English standalone file](examples/design_samples_complete_en_v0_1.py) is an identical convenience copy.

This remains a private evidence index, not a public reproducibility package. Relative paths lead into the research directory. Publication preparation must connect the relevant version to persistent public resources. Editorial checks within this project are distinct from independent rescoring or replication.


## 7. Correction to the Section 4.4 Input Description

English v0.2 and Japanese v0.5 replace the claim that both roles' own notes were supplied with the verified description: experience records for both roles, role B's own correct judgment note, B's own-experience summary, and joint candidate totals of 45 and 37. The raw CONFIRM input in the result ZIP matches the extracted and diagnostic payloads. `own_judgment` contains one B record; `experiences` contains both roles' experience. The A-authored record is the initial joint proposal, not A's own judgment note. Outcomes, scoring, numbers, code, and figures are unchanged.

See the [correction record](input-description-correction-2026-09-30.md) and [source check](../../supplements/two-role-failure-design-input-correction-20260930/README.md). Earlier manuscripts retain the superseded wording as historical artifacts.
