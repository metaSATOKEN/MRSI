# Local execution and environment selection

Updated 2 November 2026. **Use `.venv/bin/python` from the root of the working copy.** This procedure supersedes interpreter commands in earlier READMEs, manuscripts, and audit records. Preserved code and experiment records are not rewritten.

## Which root?

When this distribution is inside the author's MRSI research workspace, stay in its root (the folder named `NPP/`) and use its environment:

```sh
.venv/bin/python GitHub公開用/replay.py --verify
```

When using a standalone copy of this repository elsewhere, stay in that copy's root and use **its own** `.venv`:

```sh
.venv/bin/python --version
.venv/bin/python -c 'import sys; print(sys.executable)'
.venv/bin/python -m pip --version
.venv/bin/python replay.py --verify
```

Do not rely on activation or the shell's `python3`/`pip` lookup. If `.venv/bin/python` is absent, first check the working directory. Before creating an environment, choose and verify an absolute Python executable and the dependencies required for the intended operation. Preserve existing environments and backups. A virtual environment created on one machine is not a portable research artifact.

The research host was checked with **Python 3.13.17**, pip 26.2.2, and an isolated environment containing no third-party scientific packages. Standard-library hashing works in that environment. This check does not establish scientific reproducibility with all earlier runtime versions.

## First use of a standalone copy (macOS/Linux)

Start in the root of a fresh clone or downloaded copy, where `replay.py` and this file are located. Use Python 3.13; the preparation checks used 3.13.17. Set `MRSI_PYTHON` below to the **actual absolute path** of the interpreter you have installed. The placeholder is not an executable path.

```sh
MRSI_PYTHON="/absolute/path/to/python3.13"
"$MRSI_PYTHON" --version
test ! -e .venv && test ! -L .venv && "$MRSI_PYTHON" -m venv .venv
.venv/bin/python --version
.venv/bin/python -c 'import sys; print(sys.executable)'
.venv/bin/python -B replay.py --verify
```

The creation guard leaves an existing `.venv` directory or symlink untouched. If one already exists, inspect its interpreter before using it; do not replace it with this setup. The examples use the POSIX `.venv/bin/python` layout. No dependency installation, GPU, or credentials are needed for the hash check. `-B` suppresses Python bytecode-cache writes.

This creates an environment only in the new copy. When working inside the original research folder, keep using its existing root environment and the root-relative paths above. For scientific recalculation, use a separate working copy and install only the dependencies needed for that operation, as described below.

## Read-only integrity check

`replay.py --verify` reads the root `MANIFEST.json` and compares the listed files' SHA-256 hashes, including the original ZIP archives. It does not score answers, recompute scientific quantities, write result files, or load a model. Additional unlisted files are outside this manifest check. No external dependencies or separate release assets are needed for this command.

## Scientific recalculation uses a separate working copy

`--trial`, `--paper-01`, and `--all` score or aggregate saved responses and write outputs. `tools/rebuild_paper04_data.py` regenerates Paper 4 table data and examples. These operations are distinct from the read-only integrity check.

To perform them, first prepare a new working copy outside the preserved research folder, review the relevant fixed design and dependency versions, and create an environment at that copy's root. Run scripts from that root using its `.venv/bin/python`. The following commands are examples **for that separate working copy**, not instructions to rerun the preserved evidence during an environment update:

```sh
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python replay.py --trial TAR01
.venv/bin/python tools/rebuild_paper04_data.py --output-dir /tmp/mrsi-paper04-new-output
```

Choose a still-unused output directory outside the working copy for the Paper 4 builder. Trial replay writes `replay-output/`; Paper 1 replay also writes `evidence/paper-01/replay-output/` within the copy.

The retained requirements specify `scipy==1.17.0` for Paper 1 calculations; later Qwen offline scoring uses the standard library. That requirements file is not a complete lock of every historical environment. Resolve other dependencies according to the intended calculation, and record the resulting versions. Figure, manuscript, and PDF tools likewise belong in a suitable version-specific working copy.

## Colab and historical records

Mac Python selection does not reproduce a Colab GPU environment. For example, TAR01's recorded `environment.json` reports Python 3.13.15, NumPy 2.1.3, PyTorch 2.11.0+cu130, Transformers 5.17.0, and CUDA 13.0. The new host environment does not include those scientific/GPU packages.

The public generation workflow uses readable files under each trial's `generation/` folder. Run its `run_colab.py` without arguments to inspect files; new generation requires `--run` inside Colab. The original supervisor retains its `sys.executable` and isolated-environment handling. Do not replace those with a Mac `.venv` path. Original private OneCells and archived acquisition code remain unchanged.

To check all 28 readable bundles from the research root:

```sh
.venv/bin/python -B GitHub公開用/tools/readable_generation.py --all
```

In a standalone copy, omit `GitHub公開用/`. This standard-library-only check reassembles the original payload bytes and compares their hashes. It does not run experiment code. Detailed inspection and Colab instructions are in [readable generation](docs/READABLE_GENERATION.md).

See the [verification guide](VERIFICATION.md) for the scope of each check.
