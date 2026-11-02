# Distribution scope

Updated 29 October 2026. This repository collects NPP research on memory, approval, and collaboration in two- and three-role LLM systems, including Papers 1–4 and the multi-role technical synthesis.

Included:

- Current Japanese/English manuscripts, received English PDFs, figures and figure-generation code.
- Paper 1's reproducibility v0.5 as a public derivative: source/data bytes are preserved; scientific references are relocated, internal editorial records are excluded, and the replay has a one-path adaptation with a new manifest. Its bundled manuscript is historical v0.10; the current v0.11 Japanese and v0.2 English manuscripts are in `papers/paper-01/`. All 1,127 raw answers are retained; 792 are rescored. The earlier 335 answers are retained without a newly unified rescoring.
- All 28 Qwen trials linked to Papers 2–4, including appendices and judge calibration: fixed materials/instructions, schemas, source code, actual raw answers, saved states, dependency records, generation settings and environments.
- Detailed evidence indexes, selected independent verification and diagnostic results. UR01 envelope-normalized analysis is post hoc reference evidence; absent downstream READs are not fabricated. OS01 boundary-normalized scores remain separate from formal scores.
- Author-written plans, results, and context notes supporting these papers. Documentation of earlier exploratory experiments provides context for the reported comparisons.

Excluded:

- Unrelated source datasets and private workflow ledgers; Meteon reference code and third-party full-text PDFs.
- Account credentials, authorization artifacts, transport databases/headers/streams, private worker directories, caches, and bulk synthetic connection-test fixtures.
- Unselected superseded manuscripts and duplicated incoming files. The preceding two-role synthesis remains as explicitly labeled history for existing references.

`manifests/UNBUNDLED_REFERENCES.json` lists historical/documentary references outside this bounded distribution. Removed local navigation targets are represented as plain source descriptions, rather than broken links. Scientific text, observed results and raw response bytes are retained. Derived Markdown navigation and package-specific reproduction instructions are updated; author contact corrections are documented separately. Absolute Colab runtime paths inside raw archives are historical metadata, not local dependencies for offline replay.

Historical directory names and experiment identifiers are retained for evidence traceability. The public collection is named NPP throughout its introductory and citation materials.

Reproducibility levels differ. Offline replay verifies saved evidence against fixed code. It does not promise regenerated answers from a provider model or identical sampling on a different GPU. Qwen generation code is provided as readable source and material files, with an explicit Colab launcher and no Drive synchronization. Original source modules and archives are retained; see docs/READABLE_GENERATION.md.

The author authorized local retention without a deletion deadline and selected Apache License 2.0 on 30 September 2026. The initial GitHub deposit is private. [MRSI repository](https://github.com/metaSATOKEN/MRSI) · [License scope](LICENSE_STATUS.md) · [Publication status](RELEASE_CHECKLIST.md)

The 14 October extension adds 459 completed responses in five trials and the separate zero-generation preparation attempt. It also includes both current synthesis programs (18 tests each) and a portable builder for Paper 4 data/extracts. The new PDF covers still carry the earlier email spelling; the release checklist requires corrected exports.
