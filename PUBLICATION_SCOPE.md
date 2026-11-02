# Repository contents

The [collected edition and individual papers](papers/README.md) cover MRSI’s two- and three-role experiments. Each report has a Japanese manuscript, an English manuscript, an English PDF and a guide to its evidence.

- **Paper 1.** [Saved records and scoring code](evidence/paper-01/README.md) cover 1,127 answers, including 792 scored in the offline replay.
- **Papers 2–4.** [28 Qwen trials](experiments/README.md) include frozen inputs, schemas, readable code, saved states, raw answers and recorded aggregates. The 29 completed-run ZIPs hold 5,080 response files. A separate ZIP documents TB01’s initial preparation failure with zero generations. Counts describe files. Each paper defines its own evaluation units.
- **Design synthesis.** The [evidence index](papers/two-role-failure-design/S1.md) connects design principles to observed failures. Illustrative controller programs accompany the synthesis in both languages.
- **Methods and provenance.** Fixed trial designs and reports document what was measured. Post hoc diagnostics, including UR01 envelope normalization and OS01 boundary normalization, are identified separately from formal results. Where original archives use NPP, the former project name, their identifiers preserve the link to acquisition.

[Offline replay](RUNNING.md) uses the saved evidence. [Colab generation](docs/READABLE_GENERATION.md) uses the original materials to obtain fresh responses. The repository excludes private workflow records, credentials, transport artifacts and third-party full texts. For licensing and attribution, see [license scope](LICENSE_STATUS.md).
