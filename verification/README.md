# Verification records

These preparation records correspond to the documented local checks. Replay is an offline recalculation of existing evidence, not a new experiment. The initial hash count precedes the addition of this verification folder. The final MANIFEST covers this folder too.

[Replay](replay.log) · [Guards](guard.json) · [Navigation](navigation.json) · [Bounded disclosure scan](disclosure-scan.json) · [Summary](../VERIFICATION.md)

## 14 October 2026 extension

[Summary](update-20261014.json) · [Integrity and links](update-20261014-integrity.json) · [Paper 4 rebuild](update-20261014-paper04-rebuild.json)

Replay logs: [TB01 and initial failure](update-20261014-replay-TB01.log), [TVR01](update-20261014-replay-TVR01.log), [TCV01](update-20261014-replay-TCV01.log), [TCV02](update-20261014-replay-TCV02.log), [TAR01](update-20261014-replay-TAR01.log), and [OR01 regression](update-20261014-replay-OR01.log). Their hash count reflects the package before these reports were added; the root MANIFEST covers the final candidate.

## 23 October 2026 environment check

[Python and read-only integrity record](python-update-20261023.json). This update checks file hashes and preserves all experimental evidence; it does not repeat scientific replay. [Current execution procedure](../RUNNING.md).

## 29 October 2026 publication readability audit

[Summary](publication-audit-20261029.json) · [28 readable bundles and guards](readable-generation-20261029.json) · [Historical reference layout](paper01-public-layout-20261029.json) · [Navigation](readable-navigation-20261029.json) · [All-trial replay](replay-20261029.log) · [Paper 1 after relocation](paper01-after-layout-20261029.log) · [Paper 4 rebuild](paper04-rebuild-20261029.json) · [Replay dependencies](replay-environment-20261029.txt).

Run the readable-code regression checks with `.venv/bin/python -B tools/test_readable_generation.py` from a standalone copy's root, or use the NPP-root procedure in RUNNING.md. The temporary scientific replay environment is not distributed.

## 29 October 2026 reference and onboarding corrections

[Link and guide verification](links-and-guides-20261029.json). Eleven unresolved references were corrected or labeled as generated/unbundled material. Current guides include initial environment creation, evidence-preserving inspection, temporary-copy tests, and readable generation entry points. Scientific inputs, responses, code, and results are unchanged.
