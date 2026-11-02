# TB01: three-role-boundary-01

Supports [Paper 4](../../papers/paper-04/README.md). 126 recorded responses; this count is not an independent sample size.

- [Recorded formal aggregate](expected-result.json)
- [Local pre-execution payload](payload.json) / [frozen code](code/) / [fixed inputs and design](design/)
- [Original ZIP](archives/) / [readable inputs, raw answers, and saved records](logs/)
- [Diagnostic and post hoc files](analysis/) / [plans and result report](docs/)
- [Readable generation code and Colab launcher](generation/)

Offline replay: `.venv/bin/python replay.py --trial TB01` from the root of a separate working copy prepared using [RUNNING.md](../../RUNNING.md). It writes replay outputs and imports the locally fixed code, checks the returned archive, and never calls a model. Colab generation is a separate operation.

[Initial preparation failure: zero generations](preparation-attempt/README.md).
