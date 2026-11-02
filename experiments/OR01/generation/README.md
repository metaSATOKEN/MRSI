# OR01: readable generation files

Start with [`source/`](source/): the original experiment implementation, with each Python module in a normal file. [`supervisor.py`](supervisor.py) manages Colab setup, execution limits, recovery, and result ZIP download. [`materials/`](materials/) contains the frozen inputs and contracts. Original Japanese inputs are preserved.

For a first code reading, follow [`owner_recency_01_runtime.py`](source/owner_recency_01_runtime.py) for the execution flow and [`owner_recency_01_scoring.py`](source/owner_recency_01_scoring.py) for scoring. The [result report](../docs/owner-recency-01-result-2026-09-25.md) explains the four-branch comparison before the implementation details.

[`run_colab.py`](run_colab.py) is the public entry point. From a standalone repository's root, inspect the bundle using:

```sh
.venv/bin/python -B experiments/OR01/generation/run_colab.py
```

This only verifies files and reconstructs the original JSON bytes in memory. It imports no model or experiment module, performs no installation, and makes no network request. Inside the NPP research workspace, use its root `.venv/bin/python` and prefix the script path with `GitHub公開用/`.

For **new model generation**, put the complete repository in Google Colab, review the fixed contract and GPU requirements, change to the repository root, and run:

```python
import subprocess, sys
subprocess.run([sys.executable, "experiments/OR01/generation/run_colab.py", "--run"], check=True)
```

The supervisor installs the experiment's dependencies, downloads its pinned model, and runs generation only after its original environment checks. It uses the same recorded resource limits and isolated Colab environment. It does not mount Drive. The result ZIP is downloaded automatically; `--no-download` leaves it in Colab Files. This is a costly GPU workflow, separate from offline scoring; new answers may differ.

## Preservation

`source/` contains exact embedded source bytes. The supervisor changes only its transport argument from compressed text to reconstructed JSON bytes; the model settings, prompts, parsing, scoring, retry policy, limits, and error handling remain unchanged. The public launcher defaults to inspection and requires `--run` for generation.

`bundle.json` records file hashes and the original payload SHA-256, `6ae66f89836bfba2b158e5030e0e32e3bccf583ab50e87f8d47ce37874662de5`. The shared [loader](../../../tools/readable_generation.py) rebuilds the compact original JSON and checks that digest. See the [publication audit](../../../docs/READABLE_GENERATION.md) for verification scope. GPU execution of this readable wrapper has not been rerun.
