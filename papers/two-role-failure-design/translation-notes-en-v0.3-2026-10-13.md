# English v0.3: Translation and Figure Handoff

October 13, 2026. This English version corresponds to Japanese v0.6 and expands the synthesis to two- and three-role tasks. It supersedes English v0.2 for PDF production. The source Japanese manuscript and earlier English manuscript/PDF remain unchanged.

## Files to Send to the PDF Team

- [English manuscript v0.3](manuscript-en-v0.3-2026-10-13.md): abstract, Sections 1–10, six references, all tables, and Appendices A–D.
- [Figure 1, PNG](figures/fig01-record-trace-en-v2.png) / [SVG](figures/fig01-record-trace-en-v2.svg).
- [Figure 2, PNG](figures/fig02-reference-architecture-en-v2.png) / [SVG](figures/fig02-reference-architecture-en-v2.svg).
- [English Supplement S1](evidence-index-en-v0.3-2026-10-13.md): links to the evidence; not required to understand the main argument.
- [Japanese source v0.6](manuscript-ja-v0.6-2026-10-13.md), for bilingual review.

Keep the `figures/` subfolder next to the Markdown so its relative image links resolve. Use SVG for vector typesetting when supported; PNGs are 300 dpi. Figure 2 is portrait and contains two parallel decision paths. Preserve aspect ratio, all arrows, and the caption identifying it as a proposed architecture. Allow it a full page if needed. Figure 1 is the observation framework; Figure 2 is the design proposal, not a measured full system.

## Terms and Meaning

| Japanese | English | Distinction retained |
|---|---|---|
| 多者系 | multi-role systems | Two- and three-role evidence; no arbitrary-N performance claim |
| 本人判断 | own judgment / role-specific judgment | Experience-grounded recommendation, distinct from joint assignment |
| 実票 | actual votes / received votes | What the roles actually expressed and what the input actually contains |
| 未返答 | missing vote / nonreceipt | MISSING does not imply an explicit HOLD |
| 明示保留 | explicit hold | An expressed HOLD vote, distinct from absent approval |
| 集団合意 | group agreement | Application of the specified agreement rule to actual votes |
| 実行許可 | execution authorization | Controller decision combining agreement and proposal assessment |
| 共同担当 | joint assignment | Allocation for the shared task, without rewriting own judgment |
| 元ID | origin ID | Original source identifier, distinct from the current evidence reference |
| 版 | revision / version | Observation revision; proposal/evidence version |
| 保留 | hold / deferral | HOLD for experimental votes/actions; DEFERRED for the illustrative controller |
| 対応三状態組 | matched three-state triplet | TAR01's 18 matched triplets, not 54 independent materials |

The English text retains separate criteria for vote appropriateness and fidelity to actual votes. It preserves the constructed nature of TAR01's HOLD condition and the endpoint at READ output. It does not turn that state misdescription into an observed downstream propagation. The two-role use-stage criterion and the added execution check in the design examples remain distinct.

## Code and Numbers

Appendix D contains the entire executable program, all synthetic inputs, and 18 tests. It can be saved as one Python file or pasted into one notebook cell. [The English standalone file](examples/design_samples_complete_en_v0_2.py) is a convenience copy identical to the appendix. Only documentation strings were translated from the Japanese code; executable statements, fixtures, identifiers, and tests are unchanged.

The program preserves original votes, distinguishes MISSING/HOLD/ACCEPT, derives PENDING/AGREED, and separately returns DEFERRED/AUTHORIZED. Unanimous approval of the total-37 proposal remains AGREED while execution is deferred. The proposer must explicitly vote under this illustrative rule; it is not a reproduction of the original two-role protocol.

Bilingual checks cover table dimensions and numeric cells, prose numerical claims, code syntax and extracted execution, references, and local links. Diagram checks compare the edge lists with both Japanese Mermaid sources, inspect text containment, and include visual review of the rendered PNGs. Details are in the [translation audit](../../supplements/multi-role-failure-design-en-20261013/README.md).

## Typesetting Details

- Keep `info@metaclan.jp` visible as text; the adjacent `email` label carries the mailto link.
- Do not use the previous v0.2 PDF as the manuscript source or the old v1 Figure 2.
- Preserve the full Appendix D, its indentation, and all 18 tests. Long lines may wrap visually without changing source text. Mark continuation pages when needed.
- Main-text code examples intentionally recur in Appendix D, serving explanation and standalone execution respectively.
- Preserve `RAD9D1FEC60F1FA2` versus `RAD9D1FEC60F1FA` exactly, and the interval envelope −17.36 to 16.60 percentage points.
- The research-directory evidence links remain private. Public archive, identifiers, license, and final author declarations require publication preparation; they were not inferred during translation.

No PDF, new LLM experiment, literature search, or public upload is part of this delivery.
