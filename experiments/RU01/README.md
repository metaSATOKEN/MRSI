# RU01: role-shared-use-01

Supports paper-02. Fixed Japanese inputs and actual saved responses are retained.

- [Recorded aggregate](expected-result.json)
- [Fixed payload and original instructions](payload.json)
- [Frozen scoring and controller code](code/)
- [Complete original ZIPs](archives/)
- [Browser-readable response and state logs](logs/)
- [Analysis and worked examples](analysis/)
- [Readable generation code and Colab launcher](generation/)

Offline replay: `.venv/bin/python replay.py --trial RU01` from the repository root. Generation is a separate Colab/GPU operation. Never pool repeated or branched responses as independent samples.
