# Experiment index

[Repository overview](../README.md) · [Japanese guide](../README_ja.md) · [Machine-readable catalog](../EXPERIMENTS.json)

Start with [OR01](OR01/README.md) to inspect a field-level comparison, [CU01](CU01/README.md) to trace rollback after a correct update, or [JR01](JR01/README.md) to inspect fixed-input repetitions of role-specific and joint judgments.

Paper 1’s earlier trials and E1/E2 are in the separate [sealed evidence package](../evidence/paper-01/README.md). The table below covers 28 later Qwen trials, including five three-role trials. Counts describe recorded response files; use the papers’ sample units for statistical interpretation.

| Trial | What it examines | Report | Response files |
|---|---|---|---:|
| [XM01](XM01/README.md) | Cross-model replay of the first report’s method comparison | paper-02 | 1,008 |
| [RL01](RL01/README.md) | Readout load: diagnosing difficulty in reading saved information | paper-02 | 96 |
| [RS01](RS01/README.md) | Readout split: separating decision components | paper-02 | 96 |
| [SVR01](SVR01/README.md) | Saved-note readout: using actual retained notes | paper-02 | 104 |
| [UR01](UR01/README.md) | Update and readout: structural acceptance versus content correctness | paper-02 | 107 |
| [OR01](OR01/README.md) | Owner and recency: four storage branches of the same update | paper-02 | 91 |
| [SX01](SX01/README.md) | Self-update and exchange: the first update cycle | paper-02 | 128 |
| [RU01](RU01/README.md) | Role/shared use: choosing which saved information to use | paper-02 | 128 |
| [SX02](SX02/README.md) | Self-update and exchange: the second update cycle | paper-02 | 128 |
| [CU01](CU01/README.md) | Customer update: new preferences followed by old notices | paper-02 | 96 |
| [ES01](ES01/README.md) | Own experience and shared decisions | paper-03 | 144 |
| [AC01](AC01/README.md) | Agreement confirmation on tied candidates | paper-03 | 120 |
| [EU01](EU01/README.md) | Experience updates and joint assignments | paper-03 | 128 |
| [FC01](FC01/README.md) | Choice between feasible joint candidates | paper-03 | 256 |
| [FC02](FC02/README.md) | Candidate choice with new experience materials | paper-03 | 256 |
| [CT01](CT01/README.md) | Computed totals for joint candidates | paper-03 | 256 |
| [OS01](OS01/README.md) | Separate summaries for own experience and joint candidates | paper-03 | 384 |
| [BJ01](BJ01/README.md) | Boundary-judge calibration on fixed answers | paper-03 | 64 |
| [CS01](CS01/README.md) | Computational support at partner confirmation | paper-03 | 208 |
| [CR01](CR01/README.md) | Partner recheck of a counterproposal | paper-03 | 117 |
| [ST01](ST01/README.md) | Summary timing: support at final use versus earlier stages | paper-03 | 235 |
| [ST02](ST02/README.md) | Summary timing with previously unused numerical materials | paper-03 | 231 |
| [JR01](JR01/README.md) | Three fixed-input repetitions of formation and confirmation | paper-03 | 240 |
| [TB01](TB01/README.md) | Three roles: own judgment, actual votes, and group readout | paper-04 | 126 |
| [TVR01](TVR01/README.md) | Repeated votes with fixed inputs | paper-04 | 54 |
| [TCV01](TCV01/README.md) | Explicit comparison field versus direct voting | paper-04 | 108 |
| [TCV02](TCV02/README.md) | Same comparison on new numerical materials | paper-04 | 117 |
| [TAR01](TAR01/README.md) | Missing, explicit-hold, and all-approved readout states | paper-04 | 54 |

Each folder links its fixed payload, frozen code, readable logs, original archives, and recorded aggregate. Formal missing outcomes and post hoc reference analyses remain separate. To recompute one trial, first prepare a separate working copy and its environment using [RUNNING.md](../RUNNING.md). From that copy's root, run `.venv/bin/python replay.py --trial OR01`, replacing `OR01` with the desired trial ID. This writes replay outputs; use `--verify` for a file-integrity check only.

TB01 has a separately retained initial preparation failure with zero generations. `--trial TB01` checks both attempts; `--trial TB01-PREP` checks only that failure. It is not counted as a 29th trial. The package contains 29 completed-run ZIPs plus that one failure ZIP, and 5,080 recorded response files.
