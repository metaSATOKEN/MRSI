# Paper 1 evidence and offline replay

The [paper](../../papers/paper-01/README.md) tracks role-specific facts, shared observations and their provenance through storage, reuse and revocation. The [evidence index](../../papers/paper-01/S1.md) connects the examples and evaluation rules to the saved records.

The bundle holds 1,127 original answers. Offline replay rescores 792. The other 335 answers are included with the aggregates from their original trials. Formal missing outcomes and post hoc sensitivity calculations have separate records.

- [Trial inventory](data/study-index.json) · [paired trials](data/pair/)
- [Frozen scoring code](code/) · [numerical checks](references/analysis/)
- [Source map](SOURCE_MANIFEST.json) · [file hashes](MANIFEST.json) · [retention terms](RETENTION.json)

In a separate working copy with the dependencies listed in the [execution guide](../../RUNNING.md), run the following from the repository root.

```sh
.venv/bin/python -B replay.py --paper-01
```
