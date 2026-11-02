# English v0.2: Translation and PDF-Production Handoff

September 30, 2026. English v0.2 corresponds to Japanese v0.5 after a source-checked correction to Section 4.4. Use this version for PDF production. The earlier Japanese v0.4 and English v0.1 are preserved. Figures and executable code are unchanged.

## Files to Use

- [English manuscript](manuscript-en-v0.2-2026-09-30.md): complete abstract, Sections 1–10, references, tables, and Appendices A–D.
- [English figures](figures/README.md): two 300-dpi PNGs, two SVGs, and generation source.
- [English Supplement S1](evidence-index-en-v0.2-2026-09-30.md): evidence map with original record links.
- [Japanese source v0.5](manuscript-ja-v0.5-2026-09-30.md).

The main document remains standalone for understanding the tasks, observations, and design principles. Appendix D contains the complete executable example, complete inputs, all 19 tests, and instructions; it does not require a separate Python file. The [English standalone Python file](examples/design_samples_complete_en_v0_1.py) is a convenience copy identical to the appendix.

## Terminology

| Japanese | English | Meaning |
|---|---|---|
| 故障学 | failure analysis | Locating a requirement violation and tracing it through stored artifacts and use |
| 本人判断 | own judgment / role-specific judgment | Recommendation grounded in that role's experience; not personality or identity |
| 本人観測 | own observation | The staff role's observation, separate from its customer's preference |
| 担当客情報 | assigned-customer information | Preference, provenance, and where applicable revision for that role's customer |
| 個別ノート | private note | A per-role record; not a claim about personal data |
| 共同観測 | shared observations | Observation rows copied into shared notes |
| 共同担当 | joint assignment | Medium allocated to the role for the joint task |
| 元ID | origin ID | Identifier of the original source, distinct from a reference to the present input |
| 現在参照 | current evidence reference | Direct evidence location in the current call's input |
| 版 | revision / version | Revision for an observation; version for a proposal or evidence snapshot |
| 保存器 | storage component | Program component saving the actual artifact |
| 契約 | contract / explicit requirement | Requirement for a field or stage, not a legal agreement |
| 合意確定 | agreement commitment | Controller-authorized transition from a checked proposal/acceptance pair to usable agreement |
| 保留 | deferral / hold | Explicit state, with the affected task and reason |
| 未確定 | unresolved outcome | Outcome not established, including structurally unusable responses |
| 非適用 | inapplicable by protocol | A stage not required on that path; distinct from failed execution |

Use “feasible” for resource-conforming allocations and “suboptimal” for the total-37 proposal. Faithful use and agreement quality remain separate evaluation targets. Revocation is defined at first use in the detailed diagnostic as invalidating a recorded observation, not withdrawing access permission.

## Preserved Content and Code

The five cases and seven principles follow the Japanese structure. The 64-group method comparison retains the unresolved outcome, the interval envelope, and the uncalculated primary p-value. The 36 proposals branch four ways, with 55 actual readout generations; branches are not independent materials. CU01 retains adoption 16/16, unaffected information 32/32, and rollback 14/16. Fixed-input repetitions remain unconnected panels, with no subsequent-use rerun. Example functions 2 and 3 and the complete Figure 2 architecture remain proposals, not measured system improvements.

The first three Python blocks are identical to Japanese v0.5. In the full Appendix D program, only the module description and comments are translated. Executable statements, data, keys, IDs, test cases, and output semantics remain unchanged. Extracting that block into an isolated directory and running it checks both the 19 tests and agreement with the Japanese example output. It does not count as a new research experiment.

Figure 1 uses a vertical processing chain with audit records alongside it. Figure 2 separates private-state updating from joint-agreement commitment and preserves direct evidence access, private/shared inputs, own-judgment use, and both hold paths. The source diagrams' connections are checked against the generation script's edge lists. The final PNGs are visually inspected for labels, arrows, and clipping.

## PDF Production

Keep `figures/` beside the Markdown so both relative PNG links resolve. Use SVGs when the typesetter supports vector artwork. Figure 2 is portrait; do not stretch it or crop the hold-state note. Retain the captions and its “proposed architecture” status.

The manuscript contains long code blocks and wide tables. Wrap long code lines visually without changing identifiers, strings, or indentation in the underlying source. Allow Appendix D to span pages with a clear continuation label; preserve all 19 tests and the final entry point. The short code blocks in Section 5 intentionally recur in the complete Appendix D program. They support different reading needs.

Source links and S1 still point into a private research directory, with original Japanese sources and optional existing English versions. Those links must be replaced with the corresponding public resources during publication preparation. Preserve origin IDs exactly, particularly the one-character difference `RAD9D1FEC60F1FA2` / `RAD9D1FEC60F1FA`. Keep contact text visible, not only an embedded email link.

This delivery produces no PDF and adds no literature search, new experimental generations, or research rescoring. Public archive, license, and author declarations remain publication-preparation items as in the Japanese source.

## Source-Checked Correction

Section 4.4 now states that the confirmation input contained both roles’ experience records and only B’s own correct judgment note, together with B’s summary and the joint totals. The earlier claim that both own notes were supplied was too broad. The correction changes input-description accuracy, not the observed incorrect acceptance or the conclusion. See the [correction record](input-description-correction-2026-09-30.md).
