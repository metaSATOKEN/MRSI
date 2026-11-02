# Readable experiment code

## Where to start

All 28 later Qwen experiments now expose ordinary Python files. For a small worked example, read [OR01](../experiments/OR01/generation/README.md); for the three-role boundary experiment, read [TAR01](../experiments/TAR01/generation/README.md).

Each `generation/` folder contains:

| File or directory | Purpose |
|---|---|
| `source/` | Exact source modules extracted from the original generation bundle. |
| `materials/` | Plain JSON inputs, schemas, and frozen acquisition contracts. |
| `design.md`, `requests.jsonl` where supplied | The original readable design and request text. |
| `supervisor.py` | Colab environment checks, dependency installation, model setup, bounded execution, and ZIP download. |
| `run_colab.py` | Small public entry point; inspection is the default. |
| `bundle.json` | File hashes, assembly map, and original payload digest. |

There is no compressed executable payload in the public launchers. The [shared loader](../tools/readable_generation.py) reads the plain files and rebuilds the exact original compact JSON bytes in memory. It compares their SHA-256 to the original bundle before any experiment module is imported. Symlinks and paths escaping the bundle are rejected.

## Inspect locally; generate explicitly on Colab

Follow [RUNNING.md](../RUNNING.md) for interpreter and working-directory selection. With a standalone repository's `.venv`, either inspect one experiment or all bundles:

```sh
.venv/bin/python -B experiments/OR01/generation/run_colab.py
.venv/bin/python -B tools/readable_generation.py --all
```

These two inspection commands use the standard library and read the bundle files without modifying them. `-B` suppresses bytecode-cache writes. They do not install packages, download weights, import experiment modules, or perform generation. A local GPU is not used. For an initial environment, follow the [standalone setup example](../RUNNING.md#first-use-of-a-standalone-copy-macoslinux).

The optional packaging regression tests are a separate check:

```sh
.venv/bin/python -B tools/test_readable_generation.py
```

These tests create, modify, and remove temporary copies to check rejection of altered files and escaped paths. They preserve the distributed evidence, do not load a model, and do not perform scientific rescoring. They are not a file-read-only operation.

For new generation, copy the complete repository to Colab and follow the experiment's `generation/README.md`. The launcher requires `--run` and Colab. Its supervisor retains the original GPU-memory checks, pinned model revision, dependencies, budgets, error handling, and automatic ZIP download. No Drive mounting is required. XM01 retains its two-part selection and resume options. Review the fixed contract before starting this separate GPU workflow.

## What changed, and what stayed fixed

This is a packaging change. Source modules, materials, prompts, model settings, parsers, scoring rules, formal missing outcomes, and saved responses retain their original values. The original ZIP archives and recorded `payload.json` files retain their original bytes.

The public supervisor differs from its frozen source in two places only: its payload argument has a descriptive name, and it accepts the reconstructed JSON bytes directly instead of decoding base64/zlib text. The public launcher defaults to inspection; `--run` is the explicit generation switch. The original bootstrap modules remain in `source/` and `code/` for provenance. Their decoding functions describe the historical transport and contain no opaque embedded program.

The private OneCells are retained outside this publication folder. An original archive may contain historical source and execution records; archive bytes are never rewritten to match the new presentation.

## Verification scope

The publication audit checks all 28 original payload digests, exact embedded-source bytes, and the two-line supervisor transport adaptation. It checks that default inspection cannot install packages, call subprocesses, or access the network, and that altered inputs and symlinks are rejected. The saved-response replays and Paper 4 reconstruction run separately in a new working copy. See [verification records](../verification/README.md).

The readable GPU wrapper has not been executed on Colab in this audit. Byte-equivalent inputs and a transport-only supervisor change are verified; fresh model outputs are not claimed. Offline replay checks existing responses, independently of the new generation entry point.

Internal workflow ledgers, handoff files, and the THROUGHLINE framework are not distributed. Scientific designs and historical source-path references remain as provenance where needed. The repository's [Apache-2.0 license](../LICENSE) is unchanged.

## Paper 1 historical references

The original v0.5 package used an internal workflow directory name for 29 references. This public derivative keeps 16 scientific/reference files under `evidence/paper-01/references/analysis/` and excludes 13 editorial review, retention-check, and manuscript-diff records. Reference-document links are adapted to the public layout; numerical results are unchanged. Its replay changes only the path to the numerical audit; fixed scorers, raw responses, experiment inputs, expected values, and original archives are unchanged. Documentation changes are recorded in the source manifests and [verification history](../VERIFICATION.md). The original sealed package remains in the private research archive.
