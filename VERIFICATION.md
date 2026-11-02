# Verifying the saved results

Start with the [execution guide](RUNNING.md). In a standalone checkout, these commands use the environment at its root.

| Check | Command | What is compared |
|---|---|---|
| Distribution integrity | `.venv/bin/python -B replay.py --verify` | SHA-256 for the files in the distribution manifest, including all 30 original ZIPs |
| Full offline replay | `.venv/bin/python -B replay.py --all` | Paper 1 scoring, all 28 Qwen trial aggregates, and the separate TB01 preparation failure against saved results |
| Generation inputs | `.venv/bin/python -B tools/readable_generation.py --all` | The 28 readable input bundles against their original payloads |
| Paper 4 tables and examples | `.venv/bin/python -B tools/rebuild_paper04_data.py --output-dir /tmp/mrsi-paper04-new` | Two JSON files rebuilt from 26 source files against the published bytes |

Use a separate working copy for scientific recalculation and a new external directory for rebuilt tables. The full replay retains formal missing outcomes and the zero-generation failure. XM01 records a fresh aggregation time for each part, so the comparison excludes those two timestamps.

Paper 1 includes 1,127 answers and rescores 792 of them. The [evidence index](papers/paper-01/S1.md) gives access to the original records and fixed scorers. The [design programs](papers/two-role-failure-design/examples/README.md) each include 18 tests of the illustrative controller. Model generation is a separate workflow.
