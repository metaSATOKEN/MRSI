# English Version v0.1: Translation and Production Notes

September 29, 2026. The author approved Japanese v0.2 as the current finalized Japanese version and requested English Markdown and figures. The Japanese source remains byte-for-byte unchanged. Its historical header still says “draft”; the author's approval is recorded here, in the paper README, and in ledger §349.

## Source and deliverables

- [Approved Japanese v0.2](manuscript-ja-v0.2-2026-09-29.md)
- [English manuscript v0.1](manuscript-en-v0.1-2026-09-29.md)
- [English Supplement S1](evidence-index-en-v0.1-2026-09-29.md)
- [Figures: PNG, SVG, and generation source](figures/README.md)

The manuscript is translated through Sections 1–9, all tables, References, and Appendices A–B. Its organization follows the Japanese findings-first structure. The literature review memo, fixed experimental instructions, and primary records remain in their original language. Experimental prompts were not translated or rerun. There is no new literature search in this translation pass.

## Terminology

| Japanese concept | English usage | Scope |
| --- | --- | --- |
| 本人判断 | role-specific judgment | Recommendation derived from the role's own experience; not an identity or personality claim |
| 本人の推奨 | role-specific recommendation / own recommendation | The answer to the role's own task, separate from its joint assignment |
| 本人集計 | own-experience summary | Code-computed evidence supplied to the model; schema name `own_experience_summary` |
| 共同応答 | joint response | Acceptance, counterproposal, or deferral concerning a joint proposal |
| 共同合意の質 | joint agreement quality | Feasibility and total maximization with appropriate references in this task |
| 共同担当 | joint assignment | The role's medium under the joint allocation |
| 本人形成 | judgment formation | The stage that generates and saves a role-specific judgment; `FORM` in records |
| 共同確認 | joint confirmation | The first response to the initial joint proposal; `CONFIRM` |
| 再確認 | recheck | Called only after a counterproposal; `RECHECK` |
| 保留 | deferral / hold | Deferral of the joint task; `HOLD` in model responses |
| 後続利用 | subsequent use | Correct own judgment and references, faithful use of approved feasible agreements or appropriate deferral; `USE` |
| 実経路 | actual execution path / pathway | Actual model-generated records are supplied to the next applicable stage |
| 人工対案診断 | constructed-counterproposal diagnostic | A separate diagnostic using researcher-constructed counterproposals |
| 未確定 | unresolved | Missing or structurally unusable response; distinct from a substantive failure |
| 工学的進行目安 | engineering progression criteria | Fixed-sample requirements, separate from statistical significance |

“Feasible” replaces literal “legal” when describing allocations that satisfy equipment constraints. “Joint confirmation” names a response stage, not proof that agreement is already established. A counterproposal alone is not agreement. Repetition refers to fresh-seed responses to fixed inputs, not three connected end-to-end runs.

## Preserved distinctions

The abstract and introduction separate actual-path observations of three targets from the two stages repeated in JR01. Table 6 explains how an incorrect agreement can coexist with correct subsequent use. Tables 9–10 preserve component-level variability and the dependence of repeated inputs. The reasons for an incorrect acceptance remain unidentified; the translation adds no psychological or causal explanation.

The Figures 1–2 relationship diagrams are redrawn with English labels. Figure 1 places the supply schedule alongside the execution graph to avoid crossing support arrows; it retains all supply conditions and the conditional recheck branch. Figure 2 keeps the two panels visually separate and identifies the original ST02 notes as part of the fixed confirmation input. The figures add no experimental data.

## Handoff for PDF production

Use the English manuscript and keep the `figures/` subfolder beside it so its relative image links resolve. SVG versions are available for vector placement; the Markdown uses 300-dpi PNGs. Preserve the equation, JSON excerpt, table denominators, figure captions, and the distinction between appropriate agreement G and subsequent-use correctness. Supplement S1 is a separate document. Research-data links still point into the private research folder; public repository and persistent-identifier links are pending publication preparation.

No PDF is created in this delivery. Funding and conflict-of-interest declarations remain pending the author's public-version confirmation, as in the Japanese source. The English version is a draft for author review, not an independently approved final edition.
