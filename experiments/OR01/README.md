# OR01: owner-recency-01

Supports paper-02. Fixed Japanese inputs and actual saved responses are retained.

Start with the [result report (Japanese)](docs/owner-recency-01-result-2026-09-25.md): it explains the four storage branches applied to the same model-generated update, which fields were repaired, and what remained incorrect. For the English account, see [Paper 2](../../papers/paper-02/MRSI_Paper2-en-v1.0.md). Then use the aggregate and original logs below to inspect the evidence.

- [Recorded aggregate](expected-result.json)
- [Fixed payload and original instructions](payload.json)
- [Frozen scoring and controller code](code/)
- [Complete original ZIPs](archives/)
- [Browser-readable response and state logs](logs/)
- [Analysis and worked examples](analysis/)
- [Readable generation code and Colab launcher](generation/)

Offline replay: `.venv/bin/python replay.py --trial OR01` from the root of a separate working copy prepared using [RUNNING.md](../../RUNNING.md). It writes replay outputs. Generation is a separate Colab/GPU operation. Never pool repeated or branched responses as independent samples.
