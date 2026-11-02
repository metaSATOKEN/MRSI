# Supplement S1: Evidence Index for the Second Report

September 27, 2026. This index accompanies [English manuscript v0.1](manuscript-en-v0.1-2026-09-27.md), translated from the author-approved [Japanese manuscript v0.4](manuscript-ja-v0.4-2026-09-27.md). It links results and worked examples to fixed aggregates and original records. The underlying result reports and design documents remain in their original language; the translation does not change scoring or formal outcomes.

## 1. Manuscript results and source records

| Trial | Manuscript location | Result report (Japanese) | Fixed design, instructions, and rules | Re-aggregation |
| --- | --- | --- | --- | --- |
| Readout decomposition (RS01) | Table 6; Section 5.1 | [Report](../../experiments/RS01/docs/readout-split-01-result-2026-09-25.md) | [Design](../../experiments/RS01/design/design.json) | [Aggregate](../../experiments/RS01/expected-result.json) |
| Saved-note readout (SVR01) | Table 6; Section 5.1 | [Report](../../experiments/SVR01/docs/saved-readout-01-result-2026-09-25.md) | [Design](../../experiments/SVR01/design/design.json) | [Aggregate](../../experiments/SVR01/expected-result.json) |
| Field-level storage comparison (OR01) | Table 7; Section 5.2 | [Report](../../experiments/OR01/docs/owner-recency-01-result-2026-09-25.md) | [Design](../../experiments/OR01/design/design.json) | [Aggregate](../../experiments/OR01/expected-result.json) |
| First cycle (SX01) | Table 8; Section 5.3 | [Report](../../experiments/SX01/docs/self-update-exchange-01-result-2026-09-25.md) | [Design](../../experiments/SX01/design/design.json) | [Aggregate](../../experiments/SX01/expected-result.json) |
| Selective use (RU01) | Table 9; Section 5.3 | [Report](../../experiments/RU01/docs/role-shared-use-01-result-2026-09-25.md) | [Design](../../experiments/RU01/design/design.json) | [Aggregate](../../experiments/RU01/expected-result.json) |
| Second cycle (SX02) | Table 8; Section 5.3 | [Report](../../experiments/SX02/docs/self-update-exchange-02-result-2026-09-25.md) | [Design](../../experiments/SX02/design/design.json) | [Aggregate](../../experiments/SX02/expected-result.json) |
| Customer-update diagnostic (CU01) | Tables 4 and 10; Section 5.4 | [Report](../../experiments/CU01/docs/customer-update-01-result-2026-09-26.md) | [Design](../../experiments/CU01/design/design.json) | [Aggregate](../../experiments/CU01/expected-result.json) |

## 2. Original archives and saved artifacts

Each ZIP is a retained byte-for-byte copy of an archive returned from an experiment. The verification records below document actual inputs, raw responses, saved artifacts, parent–child relationships, and execution environments. Code inside the returned ZIPs was not executed to prepare either the Japanese manuscript or this translation.

| Trial | Original archive | Separate verification or diagnostic |
| --- | --- | --- |
| RS01 | [ZIP](../../experiments/RS01/archives/npp-rs01-result-20260925-075422-5df6c18e.zip) | [Diagnostics](../../supplements/readout-split-01-result-20260925/diagnostics.json) |
| SVR01 | [ZIP](../../experiments/SVR01/archives/npp-svr01-result-20260925-082353-4040f124.zip) | [Diagnostics](../../supplements/saved-readout-01-result-20260925/diagnostics.json) |
| OR01 | [ZIP](../../experiments/OR01/archives/npp-or01-result-20260925-095720-c548e2a5.zip) | [Verification](../../supplements/owner-recency-01-result-20260925/independent-verification.json) |
| SX01 | [ZIP](../../experiments/SX01/archives/npp-sx01-result-20260925-104011-dacc6122.zip) | [Verification](../../supplements/self-update-exchange-01-result-20260925/verification.json) |
| RU01 | [ZIP](../../experiments/RU01/archives/npp-ru01-result-20260925-131522-816fc642.zip) | [Verification](../../supplements/role-shared-use-01-result-20260925/verification.json) |
| SX02 | [ZIP](../../experiments/SX02/archives/npp-sx02-result-20260925-140811-7f886ebd.zip) | [Verification](../../supplements/self-update-exchange-02-result-20260925/verification.json) |
| CU01 | [ZIP](../../experiments/CU01/archives/npp-cu01-result-20260926-095641-a7e7fd6f.zip) | [Verification](../../supplements/customer-update-01-result-20260926/verification.json) |

### Archive SHA-256 hashes

| Trial | SHA-256 |
| --- | --- |
| RS01 | `61a29b9fb11879c7ac76db18ffe5e61f3d10a10f991c683fbc2724f248caa1c4` |
| SVR01 | `7e9b6f8f79053841f48a329d4e954e3457a8c976c6ea591ef2c4234f1b401b06` |
| OR01 | `f80f1d81a62f07cf0940ee318b4dccf6a283f5fb7f5ed4d0ed5688a1c2875565` |
| SX01 | `6655aab50dead38cea2e4060475366db88e83c3351c524e10052ad067945ee36` |
| RU01 | `6333e83dfe41d717b27183aad33d4bf2df8f9082001253cc0af4011e7ede6121` |
| SX02 | `fcbd9fdff7a3d3a0fdc98e6033638e0338b97c9084e0bde87b29e35336c530ee` |
| CU01 | `3b75f91c68a9e4c17635f505ee0b13226f45e9767015eb59d28da6f5e4813ca9` |

## 3. Worked examples and component-level traces

- **Table 4 and Section 3.4:** [CU01-C06-R1/A](../../supplements/customer-update-01-result-20260926/example.json) traces the initial cat preference at revision 76, the new dog preference at revision 77, the actual saved state after CHANGE, the input/proposal/saved state at DELAY, and READ. The JSON excerpt reproduces the customer field of that same response. [Proposal diagnostics](../../supplements/customer-update-01-result-20260926/proposal-diagnostics.json) retain all 14 exact rollbacks.
- **Table 7 and Section 5.2:** [All branch outcomes](../../supplements/owner-recency-01-result-20260925/branch-diagnostics.json) and [11 defective proposals](../../supplements/owner-recency-01-result-20260925/failure-examples.json) supplement the four-condition aggregates. The example in which B's revision changes from 4 to 1 is G04.
- **Table 9 and Section 5.3:** [RU01-C07-R1](../../supplements/role-shared-use-01-result-20260925/example.json), the first group in execution order, contains the four conditions' actual responses and derived actions.
- **Table 8 and Section 5.3:** [First cycle: 17 updates and 24 mismatched rows](../../supplements/self-update-exchange-01-result-20260925/proposal-diagnostics.json); [second cycle: 23 updates and 32 mismatched rows](../../supplements/self-update-exchange-02-result-20260925/proposal-diagnostics.json). These compare proposals and saved artifacts within the same controlled trajectories, rather than outcomes of separate trajectories run with control disabled. Multiple item-level errors in a row count once; copies in own and shared fields count separately.

## 4. Processing and scoring code

| Trial | Fixed design and processing | Archive aggregation entry point |
| --- | --- | --- |
| RS01 | [readout_split_01_design.py](../../reference-code/readout_split_01_design.py) | [Aggregator](../../reference-code/aggregate_readout_split_01.py) |
| SVR01 | [saved_readout_01_design.py](../../reference-code/saved_readout_01_design.py) | [Aggregator](../../reference-code/aggregate_saved_readout_01.py) |
| OR01 | [owner_recency_01_design.py](../../reference-code/owner_recency_01_design.py) | [Aggregator](../../reference-code/aggregate_owner_recency_01.py) |
| SX01 | [self_update_exchange_01_design.py](../../reference-code/self_update_exchange_01_design.py) | [Aggregator](../../reference-code/aggregate_self_update_exchange_01.py) |
| RU01 | [role_shared_use_01_design.py](../../reference-code/role_shared_use_01_design.py) | [Aggregator](../../reference-code/aggregate_role_shared_use_01.py) |
| SX02 | [self_update_exchange_02_design.py](../../reference-code/self_update_exchange_02_design.py) | [Aggregator](../../reference-code/aggregate_self_update_exchange_02.py) |
| CU01 | [customer_update_01_design.py](../../reference-code/customer_update_01_design.py) | [Aggregator](../../reference-code/aggregate_customer_update_01.py) |

Semantic evaluation uses deterministic code comparing each trial's schema, fixed expected state, and actual response. The storage procedure accesses candidates in the input and does not receive the scoring oracle. Modules depend on shared helpers; the complete distributed Colab cells and sealed materials, rather than a single standalone module, specify each implementation.

## 5. Literature and version correspondence

The [related-work review (Japanese)](related-work-review-v0.1-2026-09-27.md) records primary-source versions, inspected methods, comparisons with this report, and candidates for future research. It informed Section 2, Table 2, the discussion, and the references in Japanese v0.3 and v0.4. The English manuscript preserves those source versions and distinctions, including MemProbe's renaming to MemAudit and the two separate papers titled MemTrace.

The [Japanese evidence index](evidence-index-v0.4-2026-09-27.md) also retains the initial source checks from September 26 and the editorial history. This translation introduces no new literature search. Its citation to the first report points to the corresponding English v0.2 rather than Japanese v0.11.

## 6. Retention, availability, and editorial verification

The records are retained locally without a deletion deadline. They are not yet public, and the relative links above resolve within the research workspace. A public DOI, data license, and standalone distribution package have not been created. The first report's reproduction package is separate from the second report's evidence.

At initial drafting, 2,933 files in the seven main trials' audit directories were checked against their sealed manifests; source and navigation files were recorded as 2,971 anchors. Later editorial checks retain each prior version. Raw responses have not been regenerated, and the experiments have not been rescored for translation.

| Editorial stage | Verification | Supporting record |
| --- | --- | --- |
| Initial Japanese draft | [Checks](../../supplements/paper-02-draft-20260926/verification.json) | [Source-manifest checks](../../supplements/paper-02-draft-20260926/source-manifest-verification.json); [source map and hashes](../../supplements/paper-02-draft-20260926/evidence-sources.json) |
| Findings-centered Japanese v0.2 | [Checks](../../supplements/paper-02-revision-v02-20260926/verification.json) | Revision notes, Japanese (see the evidence index) |
| Related work in Japanese v0.3 | [Checks](../../supplements/paper-02-related-work-20260927/verification.json) | Revision notes, Japanese (see the evidence index) |
| Terminology and unit clarification in Japanese v0.4 | [Checks](../../supplements/paper-02-revision-v04-20260927/verification.json) | [Revision notes, Japanese](revision-notes-v0.4-2026-09-27.md) |
| English v0.1 and English figures | [Checks](../../supplements/paper-02-english-20260927/verification.json) | [Verification code](../../supplements/paper-02-english-20260927/verify_translation.py); [translation notes](translation-notes-en-v0.1-2026-09-27.md); [figure files and source](figures/README.md) |

The author approved Japanese v0.4 as final before translation. The approval record (see the evidence index) fixes its SHA-256 hash. English v0.1 retains the abstract, Sections 1–9, Tables 1–10, all 20 references, and Appendices A/B. The two English diagrams render the processing relationships in the Japanese manuscript; they add no experimental results. Numerical, citation, example, and link checks accompany editorial review of the translated meaning.
