# English v0.1: Translation and Figure Notes

September 27, 2026. The author approved [Japanese v0.4](manuscript-ja-v0.4-2026-09-27.md) as final and requested an English Markdown manuscript and figures, with PDF production handled separately.

## Source and coverage

The Japanese source is unchanged. Its SHA-256 is `e369c3335335d455d201866b90a0cfc53abe98cbcf7ee2e33b46425d465c10fb`.

[English v0.1](manuscript-en-v0.1-2026-09-27.md) includes the complete abstract, Sections 1–9, Tables 1–10, 20 references, and Appendices A/B, including the response-accounting table. It retains the order of findings and the distinction between formal outcomes and post hoc reference analyses. [English Supplement S1](evidence-index-en-v0.1-2026-09-27.md) provides access to the original evidence; underlying Japanese reports and research code retain their original names and content.

## Terminology

| Japanese term | English used | Intended distinction |
| --- | --- | --- |
| 保存先 | record field | A logical area in a note, not a physical file or memory store |
| 個別ノート／共同ノート | private note / shared note | Consistent with the first report |
| 担当客情報 | customer information; assigned customer's information | The customer's preference is distinct from the role's observations |
| 本人観測 | own observations / own-observation field | The role's observation of its own area |
| 共同観測 | shared observations | The A/B observation rows in each role's shared note |
| 元ID | origin ID | Preserves the provenance concept used in the first report and schema |
| 版 | revision | Identifies the version of the relevant record; compared within a person |
| 人物別最新版選択 | latest-revision selection by person | Restricts to the relevant observer before comparing revisions |
| 読出しの忠実性 | readout fidelity | Agreement with the supplied saved artifact |
| 最新情報との一致 | agreement with the latest state | Separate from fidelity to a potentially stale artifact |
| 全工程成立 | end-to-end success | Joint requirements within the stated group–repetition trajectory |
| 巻戻り | rollback | Return of an updated record to the old row |
| 32最終ノート | 32 final role-specific note sets | The saved artifact for each role; each set contains private and shared notes |

## Translation decisions

- The title uses **field-level comparisons** to make the logical scope of storage controls explicit. It does not imply a comparison of physical memory stores.
- The abstract retains the material/repetition denominators: 18 previously used materials × 2 repetitions for the 36 common proposals, and 8 new cases × 2 repetitions for the customer diagnostic.
- Table 8 counts mismatched **observation rows** by location and update, not separately for each erroneous value, origin ID, or revision. The same record copied into private and shared fields is counted at each location.
- The empirical overlap of four own-field defects with shared-field defects remains distinct from the logical property of an all-conditions metric. No novelty claim is added for that logical property.
- The paper continues to distinguish a controlled trajectory's pre-storage proposal from a separately executed trajectory with control disabled.
- The worked example retains its origin IDs, revisions, and JSON excerpt exactly. Customer information remains model-written; observation controls do not supply a customer ground truth.
- The first-report citation uses its corresponding English v0.2 title and link. All external primary-source URLs and cited versions are preserved. The literature is translated from the checked Japanese source rather than newly researched here.
- Section 9 identifies this as an internal English manuscript. Public-release declarations, DOI, and license retain their pending status.

## Figures and checks

The two Japanese Mermaid diagrams are rendered as English SVG and 300-dpi PNG files, with source code and format details in the [figure directory](figures/README.md).

Figure 1 distinguishes model generation/extraction from deterministic validation, row selection, copying, and channel computation. Figure 2 distinguishes continued use of actual saved notes from input-manipulation diagnostics and separate customer-update cases. The first-cycle readout requests shared values only; later diagnostic and second-cycle readouts also request customer information.

The [verification record](../../supplements/paper-02-english-20260927/verification.json) checks source preservation, table correspondence, exact excerpts and identifiers, citations, evidence links, and figure files. Figures were rendered and visually inspected for text, arrows, and clipping. Such mechanical checks support, rather than replace, editorial review of translation meaning. No model experiments, research rescoring, PDF production, or publication were performed.
