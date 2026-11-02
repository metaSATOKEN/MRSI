# Local preparation verification

## 23 October 2026: local Python and read-only integrity check

The research host used an isolated root `.venv` with Python 3.13.17 and pip 26.2.2. No third-party scientific packages were installed. The current procedure is [RUNNING.md](RUNNING.md): explicit interpreter selection, root-relative paths, read-only hashes separated from scientific replay, and unchanged Colab cells.

The pre-update distribution passed its 61,162-file hash check in this environment. Final hashes and evidence preservation are recorded in [the environment check](verification/python-update-20261023.json). Only current execution guidance and package metadata were changed. Scientific scoring, model inference, table rebuilding, and figure/PDF regeneration were not run. Earlier replay results below remain records of their original environments, not new validation under Python 3.13.17.


Initial package: 30 September 2026; content update: 14 October 2026. No new model requests or external publication.

## 14 October 2026: Paper 4 and multi-role synthesis

- Current Japanese/English manuscripts, figures, complete example programs, and received PDFs were added. Experimental text and results match the source editions; derived Markdown links and reproduction guidance were made portable.
- The five added trials (TB01, TVR01, TCV01, TCV02, TAR01) replay successfully from their original archives and frozen local payloads. All persisted results match. TB01’s initial zero-generation preparation error is separately replayed with its own original payload; it remains INCONCLUSIVE. OR01 also passed as a regression check of the extended replay wrapper.
- Paper 4 table data and worked-example extracts were rebuilt from 26 packaged source files. Both JSON outputs are byte-identical to the recorded versions.
- The current Japanese and English illustrative design programs each passed 18 tests. These are controller examples, not additional LLM observations.
- The existing evidence was retained. Source/destination hashes, added browser-readable logs against their original ZIP members, relative Markdown targets, and the bounded scan of added files were checked. See the [integrity report](verification/update-20261014-integrity.json), [replay and example summary](verification/update-20261014.json), and [Paper 4 rebuild](verification/update-20261014-paper04-rebuild.json). The final distribution manifest seals the current files.
- Both new PDF covers retain the old email spelling. Their bytes are preserved as received; corrected exports using **info@metaclan.jp** remain a [release item](RELEASE_CHECKLIST.md). This was a cover/edition/contact check, not a new full PDF layout review.

The candidate now includes 28 later Qwen trials, 29 completed-run ZIPs plus the separate TB01 preparation-error ZIP, and 5,080 response files. The extension adds 459 responses. Counts are inventories, not independent sample sizes.

## 30 September 2026: original package checks

- Paper 1: 1,127 raw answers preserved; 792 rescored, with 10,794 checks passing. The other 335 earlier answers remain preserved evidence, without a newly unified rescoring.
- Qwen experiments: all 23 trials were re-aggregated from 24 original returned ZIPs using their frozen payload code. Persisted outcomes match the recorded aggregates. Only XM01's two newly generated aggregation timestamps are omitted from outcome comparison, as documented in `replay.py`; both versions are retained.
- Portability: the complete `replay.py --all` run succeeded when launched from a separate working directory, outside the research project. No original workspace path is required for these replays.
- Evidence derivation: 7,088 source-file copies and 47,799 browser-readable ZIP-member copies were checked against their source hashes. The final distribution has its own SHA-256 manifest. Each original ZIP is retained unchanged.
- Navigation: all local Markdown targets checked within the distribution exist; no absolute local Markdown link targets remain. Received PDFs retain their original embedded links, which require connection to the eventual release URLs.
- Integrity controls: altered evidence was rejected; socket creation, subprocess execution and shell execution were rejected inside the offline guard.
- Disclosure check: no high-confidence OpenAI/Hugging Face/GitHub/AWS credential signatures, private-key blocks, or credential/database filenames were found in the scanned files and ZIP members. This bounded scan does not prove the absence of every kind of private information; review the candidate before public upload.

Formal missing outcomes, structural failures, and post hoc diagnostic/reference results retain their original classification. Response files, repeated generations and branch results are not pooled as independent observations.

The local audit retains the full replay log, original/destination hash checks, scan scope, relocation records and engineering corrections. The distribution is ready for content review; Apache License 2.0 is now assigned; upload and persistent identifiers remain pending. The README/license update changes documentation and licensing metadata only; recorded results and frozen evidence remain unchanged.

14 October 2026 contact-only amendment: author metadata and manuscript contact fields were corrected; original scientific evidence and historical audit records remain unchanged. Distribution hashes and derived-file provenance were updated. See [contact correction](CONTACT_CORRECTION.md).

## 29 October 2026 — readable code and public reference layout

[Audit summary](verification/publication-audit-20261029.json) · [Readable-code checks](verification/readable-generation-20261029.json) · [Reference relocation](verification/paper01-public-layout-20261029.json) · [Navigation](verification/readable-navigation-20261029.json).

All 28 generation bundles rebuild their original payload bytes; 250 source modules match exactly. Public launchers default to inspection, with three standard-library regression tests covering source/material integrity, transport-only supervisor adaptation, guarded inspection, path/symlink rejection, and rejection of local model execution. The readable GPU wrappers were not rerun.

A separate working copy used Python 3.13.17, SciPy 1.17.0, and NumPy 2.5.4. [Full offline replay](verification/replay-20261029.log) matched Paper 1 and all 28 later trial aggregates plus TB01-PREP. Following the reference cleanup, [Paper 1 replay](verification/paper01-after-layout-20261029.log) again rescored 792 of 1,127 retained raw answers successfully. Its 4,815 non-hash checks are unchanged; total checks are now 10,781 because the derivative manifest has 5,966 entries instead of 5,979. The removed entries are editorial records, not scientific tests or responses.

[Paper 4 reconstruction](verification/paper04-rebuild-20261029.json) used 26 packaged source files and reproduced both the table-data and example JSON files byte-for-byte. This is offline recalculation within the same project, not new model generation or third-party replication. [Replay dependency versions](verification/replay-environment-20261029.txt).

Sixteen scientific/reference files formerly under a workflow-named directory are retained byte-for-byte under `evidence/paper-01/references/analysis/`. Thirteen internal editorial records are excluded. Paper 1's replay changes one path only; its scorers and raw data remain fixed. The original v0.5 package remains privately preserved. The earlier readability check's 60,808-file preservation count describes the stage before this documented reference-layout change.

The candidate contains no framework/ledger files, including in ZIP member names, and no opaque payload literals in the expanded Python sources. There are no files above 100 MiB. Original ZIP bytes are unchanged. Existing received-PDF contact/link fixes remain pending, as listed in RELEASE_CHECKLIST.md. No model was loaded locally and nothing was uploaded.

## 29 October 2026 — public collection name

On 29 October the guides, citation title, NOTICE, and distribution scope used the project’s former name, NPP. Historical directory names and experimental identifiers are retained for traceability. This is an editorial naming update; experiment inputs, code, results, papers, figures, and original archives are unchanged. [Naming verification](verification/public-naming-20261029.json).

## 29 October 2026 — findings-first README

The English and Japanese READMEs now introduce the observed findings and design implications before explaining the synthetic tasks. Each finding links to its supporting paper. The example materials appear in the methods overview, and code inspection is separated from offline recalculation. This is an editorial rewrite; papers, code, raw evidence, and recorded results are unchanged. [Editorial verification](verification/readme-findings-first-20261029.json).

## 29 October 2026 — reference links and first-use guidance

Nine historical reference links now target the retained public files. A post-replay table is labeled as a generated output, and an excluded internal retention record is named without a dead link. Earlier records of byte-identical relocation describe that stage; this later update changes navigation in reference documents only. Fixed scoring code, raw inputs/responses, numerical results, and original ZIPs are unchanged.

Current guides add standalone environment creation, a direct OR01 result link, and readable-generation labels for the five three-role trials. Inspection examples use `-B`; temporary-copy regression tests are described separately from read-only inspection. The 28 readable bundles retain their original reconstructed payload hashes; their README hashes are refreshed. [Verification details](verification/links-and-guides-20261029.json). No model generation or scientific recalculation was performed for this editorial update.
