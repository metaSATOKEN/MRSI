# MRSI — Memory, Approval, and Collaboration in Two- and Three-Role LLM Systems

**A correct answer can hide a damaged record. A faithfully followed agreement can still be a poor agreement.**

In experiments with two and three LLM roles, we observed correct answers accompanied by incorrect provenance, successful repairs that an overall success score did not reveal, and poor agreements followed faithfully in subsequent responses. We traced these outcomes through the records actually saved, the inputs supplied to later calls, and the responses those calls produced.

**MRSI (formerly NPP) investigates what needs to be checked separately when LLM roles share information and coordinate actions while retaining their own information, judgments, and approval states.** This repository brings together four papers, a technical synthesis of failure patterns and design principles, readable code, and the experimental evidence.

[日本語の案内](README_ja.md) · [Papers](#start-reading) · [Reproduce results](#reproduce-the-recorded-results) · [Apache 2.0](LICENSE)

## What the experiments show

| Finding | Observation | Evidence |
|---|---|---|
| **Correct answers and incorrect provenance coexisted.** | Notes associated correct content with an incorrect source ID. Subsequent responses carried that ID forward while still making the correct decision. | [Paper 1](papers/paper-01/MRSI_Paper1-en-v1.0.md) |
| **An overall success score concealed a successful local repair.** | Comparisons using the same update proposals showed both directions: a correct shared answer could coexist with stale role-specific observations, and repairing those observations could leave end-to-end success unchanged because another field still failed. | [Paper 2](papers/paper-02/MRSI_Paper2-en-v1.0.md) |
| **Stable role-specific judgments coexisted with poor shared agreements.** | Roles retained their own recommendations while approving a plan inferior under the task's stated objective. Subsequent responses faithfully followed that agreement. | [Paper 3](papers/paper-03/MRSI_Paper3-en-v1.0.md) |
| **Correct group-level deferral coexisted with a misread vote.** | In a three-role readout, the model correctly kept agreement and execution pending but described a missing vote as an explicit hold. | [Paper 4](papers/paper-04/MRSI_Paper4-en-v1.0.md) |

Together, these observations show why answer correctness, record fidelity, agreement quality, and faithful execution need separate measurements. They also show why field-level repair and end-to-end success should be reported together.

## Implications for system design

The [technical synthesis](papers/two-role-failure-design/manuscript-en-v0.3-2026-10-13.md) develops the findings into design principles with worked examples and implementation code:

- **Check the record and its next use.** Keep content attached to its owner, revision, and source, then check those relationships in the saved state and the actual next input.
- **Measure repairs at the level where they act.** Report which fields were repaired and which defects remain, alongside success across the full process.
- **Separate judgment, proposal quality, actual votes, and permission to execute.** Derive execution permission from received votes and the agreement rule. Keep each role's recommendation distinguishable from its assignment under a shared plan.
- **Use deterministic code for copying fixed values, structural checks, and vote aggregation.** Check how these operations connect to model-generated proposals and interpretations, including fields outside the deterministic operation's scope.

## How the experiments work

Within each experiment, we run the **same LLM as two or three roles in separate contexts**. Roles receive different information or experiences. Depending on the comparison, the model and controller update and share notes, assess candidate plans, or interpret approval states. Actual saved notes are passed into later calls so that we can compare the stored record, the next input, and the subsequent response.

For example, some tasks give two roles different customer preferences for dog or cat designs while they choose a shared paper or digital guidance channel. These simple materials make ownership and shared decisions easy to distinguish. Later tasks use experience-based recommendations and numerical plan comparisons; three-role tasks distinguish a missing vote, an explicit hold, and approval.

These are exploratory findings from small synthetic tasks. Plan quality is evaluated against each task's stated objective. The papers specify the models, conditions, sample units, missing outcomes, and uncertainty for each comparison.

## Start reading

Read the four experimental reports and the concluding design synthesis in one volume. [*LLM Memory, Records, and Continued Use* — Collected Edition v1.4 (English PDF, 113 pages)](papers/mrsi_series_collected_edition.pdf)

For a standalone overview of the failure patterns and resulting design principles, start with the **technical synthesis**. For the experimental evidence, read Papers 1–4 in order.

| Report | Question | Read |
|---|---|---|
| **Paper 1 — Memory and provenance** | Can role-specific facts and shared observations retain their sources through storage, reuse, and revocation? | [Markdown](papers/paper-01/MRSI_Paper1-en-v1.0.md) · [PDF](papers/paper-01/MRSI_Paper1-en-v1.0.pdf) · [Evidence](papers/paper-01/S1.md) |
| **Paper 2 — Repair and freshness** | Which fields are repaired by deterministic processing, and can a correct update later roll back? | [Markdown](papers/paper-02/MRSI_Paper2-en-v1.0.md) · [PDF](papers/paper-02/MRSI_Paper2-en-v1.0.pdf) · [Evidence](papers/paper-02/S1.md) |
| **Paper 3 — Judgments and agreements** | Does supporting each role's judgment also improve the quality of the shared agreement? | [Markdown](papers/paper-03/MRSI_Paper3-en-v1.0.md) · [PDF](papers/paper-03/MRSI_Paper3-en-v1.0.pdf) · [Evidence](papers/paper-03/S1.md) |
| **Paper 4 — Individual approval and group agreement** | Can three roles preserve each actual vote while interpreting agreement and permission to execute? | [Markdown](papers/paper-04/MRSI_Paper4-en-v1.0.md) · [PDF](papers/paper-04/MRSI_Paper4-en-v1.0.pdf) · [Evidence](papers/paper-04/S1.md) |
| **Technical synthesis — Multi-role failures and design principles** | How do findings from two and three roles inform record, approval, and execution boundaries? | [Markdown](papers/two-role-failure-design/manuscript-en-v0.3-2026-10-13.md) · [PDF](papers/two-role-failure-design/manuscript-en-v0.3-2026-10-13.pdf) · [Evidence](papers/two-role-failure-design/S1.md) |

Find the Japanese manuscripts and supporting figures in the [paper directory](papers/README.md). The current author contact is **info@metaclan.jp**.

## Inspect an experiment

Start with **[OR01: field-level repair](experiments/OR01/README.md)**. It applies four storage configurations to the same update proposal, showing which fields each configuration repairs and how the saved record is used afterward.

Each trial folder contains:

- `payload.json` and `code/`: fixed materials, instructions, schemas, and the original scoring/controller code.
- `logs/`: readable inputs, raw answers, and actual saved states.
- `archives/`: the unchanged ZIPs returned from the experiment.
- `expected-result.json`: the recorded aggregate to compare against offline replay.
- `generation/`: readable Python modules, fixed materials, and a small Colab launcher. Start with [OR01's source](experiments/OR01/generation/source/) or [TAR01's source](experiments/TAR01/generation/source/). Running the launcher without `--run` only checks files; it does not load a model.

For three-role records, inspect **[TAR01](experiments/TAR01/README.md)**: the same saved material is read under missing-vote, explicit-hold, and all-approved conditions.

The complete [experiment index](experiments/README.md) explains the trial abbreviations and links all records. The [machine-readable catalog](EXPERIMENTS.json) records archive hashes and response-file counts.

## Reproduce the recorded results

Offline replay scores and aggregates **existing saved responses**. It needs no GPU, model download, account credentials, or API calls.

Current execution instructions are in **[RUNNING.md](RUNNING.md)** (2 November 2026); they take precedence over interpreter commands in older documents.

For a standalone working copy with its own `.venv`, run the read-only integrity check from that copy's root:

```sh
.venv/bin/python replay.py --verify
```

Inside the original research workspace, stay in its root and use `.venv/bin/python GitHub公開用/replay.py --verify` instead. The research environment is Python 3.13.17; hash verification needs only the standard library.

Scientific replay (`--trial`, `--paper-01`, `--all`) and the [Paper 4 builder](tools/rebuild_paper04_data.py) compute results and write files. Run them in a separate working copy with the applicable fixed specifications and dependency versions, as described in RUNNING.md.

Offline recalculation has matched the recorded aggregates for Paper 1, all 28 later trials, and TB01's initial preparation failure. Paper 4's table data and example extracts were rebuilt byte-for-byte from 26 packaged source files. See the [verification summary](VERIFICATION.md). For the separate Colab generation workflow, see the [readable-code guide](docs/READABLE_GENERATION.md).

## Records and scope

Paper 1 preserves **1,127 raw answers**, of which 792 are rescored by its replay; the other 335 earlier answers and original aggregates are retained. The **28 later Qwen trials** preserve 5,080 response files in 29 completed-run ZIPs, plus the separately retained TB01 preparation-error ZIP with zero generations. The five three-role trials contribute 459 of those response files. Response counts are not independent sample sizes: repeated calls, roles, shared parents, and branches retain the denominators defined in the papers.

Experimental inputs and answers remain in Japanese. Formal missing outcomes and post hoc diagnostic analyses are kept distinct. New model generation is a separate Colab/GPU workflow and may produce different responses.

See [distribution scope](PUBLICATION_SCOPE.md) for included and excluded material, [source/destination hashes](manifests/SOURCE_MAP.json) for copy provenance, and [unbundled references](manifests/UNBUNDLED_REFERENCES.json) for documentary sources outside this distribution.

## License, citation, and contact

**Apache License 2.0.** See [LICENSE](LICENSE), [NOTICE](NOTICE), and [license scope](LICENSE_STATUS.md). Historical license-pending statements in preserved records describe their preparation dates; the repository's current license is stated here.

Please cite the relevant paper and the Git commit used for the evidence. The repository is at [metaSATOKEN/MRSI](https://github.com/metaSATOKEN/MRSI). [Citation metadata](CITATION.cff)

**Kentaro Sato** · Independent Researcher · [info@metaclan.jp](mailto:info@metaclan.jp)
