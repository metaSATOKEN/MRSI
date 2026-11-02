# 補足資料S1：第2報の証拠対応表

2026-09-27／日本語草稿v0.4に対応。本文の主要数値・通し例から、固定集計と原記録へ進むための索引。原実験の意味採点や旧成績を変更せず、既存の資料を参照する。

## 1. 本文と結果資料

| 呼び名 | 本文 | 結果報告 | 固定設計・指示・規則 | 再集計 |
| --- | --- | --- | --- | --- |
| 読出し分離（RS01） | 表6・§5.1 | [結果](../../experiments/RS01/docs/readout-split-01-result-2026-09-25.md) | [design](../../experiments/RS01/design/design.json) | [集計](../../experiments/RS01/expected-result.json) |
| 実保存読出し（SVR01） | 表6・§5.1 | [結果](../../experiments/SVR01/docs/saved-readout-01-result-2026-09-25.md) | [design](../../experiments/SVR01/design/design.json) | [集計](../../experiments/SVR01/expected-result.json) |
| 保存先比較（OR01） | 表7・§5.2 | [結果](../../experiments/OR01/docs/owner-recency-01-result-2026-09-25.md) | [design](../../experiments/OR01/design/design.json) | [集計](../../experiments/OR01/expected-result.json) |
| 一巡目（SX01） | 表8・§5.3 | [結果](../../experiments/SX01/docs/self-update-exchange-01-result-2026-09-25.md) | [design](../../experiments/SX01/design/design.json) | [集計](../../experiments/SX01/expected-result.json) |
| 用途分離（RU01） | 表9・§5.3 | [結果](../../experiments/RU01/docs/role-shared-use-01-result-2026-09-25.md) | [design](../../experiments/RU01/design/design.json) | [集計](../../experiments/RU01/expected-result.json) |
| 二巡目（SX02） | 表8・§5.3 | [結果](../../experiments/SX02/docs/self-update-exchange-02-result-2026-09-25.md) | [design](../../experiments/SX02/design/design.json) | [集計](../../experiments/SX02/expected-result.json) |
| 希望更新診断（CU01） | 表4・表10・§5.4 | [結果](../../experiments/CU01/docs/customer-update-01-result-2026-09-26.md) | [design](../../experiments/CU01/design/design.json) | [集計](../../experiments/CU01/expected-result.json) |

## 2. 原ZIPと保存物の照合

各ZIPは返却原本の保管コピーである。下表の検証記録から、実入力、原回答、保存物、親子対応、環境の確認内容へ進める。ZIP内のコードをこの草稿作成のために実行していない。

| 試験 | 原ZIP | 別照合・診断 |
| --- | --- | --- |
| RS01 | [原ZIP](../../experiments/RS01/archives/npp-rs01-result-20260925-075422-5df6c18e.zip) | [照合](../../supplements/readout-split-01-result-20260925/diagnostics.json) |
| SVR01 | [原ZIP](../../experiments/SVR01/archives/npp-svr01-result-20260925-082353-4040f124.zip) | [照合](../../supplements/saved-readout-01-result-20260925/diagnostics.json) |
| OR01 | [原ZIP](../../experiments/OR01/archives/npp-or01-result-20260925-095720-c548e2a5.zip) | [照合](../../supplements/owner-recency-01-result-20260925/independent-verification.json) |
| SX01 | [原ZIP](../../experiments/SX01/archives/npp-sx01-result-20260925-104011-dacc6122.zip) | [照合](../../supplements/self-update-exchange-01-result-20260925/verification.json) |
| RU01 | [原ZIP](../../experiments/RU01/archives/npp-ru01-result-20260925-131522-816fc642.zip) | [照合](../../supplements/role-shared-use-01-result-20260925/verification.json) |
| SX02 | [原ZIP](../../experiments/SX02/archives/npp-sx02-result-20260925-140811-7f886ebd.zip) | [照合](../../supplements/self-update-exchange-02-result-20260925/verification.json) |
| CU01 | [原ZIP](../../experiments/CU01/archives/npp-cu01-result-20260926-095641-a7e7fd6f.zip) | [照合](../../supplements/customer-update-01-result-20260926/verification.json) |

### 原ZIPのSHA-256

| 試験 | SHA-256 |
| --- | --- |
| RS01 | `61a29b9fb11879c7ac76db18ffe5e61f3d10a10f991c683fbc2724f248caa1c4` |
| SVR01 | `7e9b6f8f79053841f48a329d4e954e3457a8c976c6ea591ef2c4234f1b401b06` |
| OR01 | `f80f1d81a62f07cf0940ee318b4dccf6a283f5fb7f5ed4d0ed5688a1c2875565` |
| SX01 | `6655aab50dead38cea2e4060475366db88e83c3351c524e10052ad067945ee36` |
| RU01 | `6333e83dfe41d717b27183aad33d4bf2df8f9082001253cc0af4011e7ede6121` |
| SX02 | `fcbd9fdff7a3d3a0fdc98e6033638e0338b97c9084e0bde87b29e35336c530ee` |
| CU01 | `3b75f91c68a9e4c17635f505ee0b13226f45e9767015eb59d28da6f5e4813ca9` |

## 3. 本文の具体例と成分の追跡

- 表4・§3.4：CU01-C06-R1/A。初期の猫・版76、新通知の犬・版77、CHANGEの実保存、DELAYの実入力・原案・実保存、READまでを [example.json](../../supplements/customer-update-01-result-20260926/example.json) で照合できる。JSONの短い抜粋は同一回答のcustomer欄。全14件の巻戻りは [proposal-diagnostics.json](../../supplements/customer-update-01-result-20260926/proposal-diagnostics.json)。
- 表7・§5.2：4条件の集計に加え、[全分岐の内訳](../../supplements/owner-recency-01-result-20260925/branch-diagnostics.json) と [11件の原案](../../supplements/owner-recency-01-result-20260925/failure-examples.json) を保持。本文のB版4→1の例はG04。
- 表9・§5.3：最初の割付組RU01-C07-R1の [四条件の回答と導出](../../supplements/role-shared-use-01-result-20260925/example.json)。
- 表8・§5.3：[一巡目17更新・24行](../../supplements/self-update-exchange-01-result-20260925/proposal-diagnostics.json)、[二巡目23更新・32行](../../supplements/self-update-exchange-02-result-20260925/proposal-diagnostics.json)。同じ実経路内の原案と保存物を示し、処理OFFの別実行結果とは区別する。

## 4. 処理・採点コード

| 試験 | 固定設計・処理 | ZIPの集計入口 |
| --- | --- | --- |
| RS01 | [readout_split_01_design.py](../../reference-code/readout_split_01_design.py) | [集計器](../../reference-code/aggregate_readout_split_01.py) |
| SVR01 | [saved_readout_01_design.py](../../reference-code/saved_readout_01_design.py) | [集計器](../../reference-code/aggregate_saved_readout_01.py) |
| OR01 | [owner_recency_01_design.py](../../reference-code/owner_recency_01_design.py) | [集計器](../../reference-code/aggregate_owner_recency_01.py) |
| SX01 | [self_update_exchange_01_design.py](../../reference-code/self_update_exchange_01_design.py) | [集計器](../../reference-code/aggregate_self_update_exchange_01.py) |
| RU01 | [role_shared_use_01_design.py](../../reference-code/role_shared_use_01_design.py) | [集計器](../../reference-code/aggregate_role_shared_use_01.py) |
| SX02 | [self_update_exchange_02_design.py](../../reference-code/self_update_exchange_02_design.py) | [集計器](../../reference-code/aggregate_self_update_exchange_02.py) |
| CU01 | [customer_update_01_design.py](../../reference-code/customer_update_01_design.py) | [集計器](../../reference-code/aggregate_customer_update_01.py) |

意味評価は各試験のschema・固定期待状態・実回答を比較する決定論的コードによる。保存処理は入力内の候補を参照し、採点の期待状態を取得しない。コードは相互に補助モジュールを参照するため、単一ファイルだけでなく各Colab配布セルと封印済み資料を参照する。

## 5. 外部文献の照合範囲

v0.3では関連研究の探索を追加し、[調査メモ](related-work-review-v0.1-2026-09-27.md)に一次資料の版・確認した方法節・本稿との対照・候補棚をまとめた。本文§2と表2、§6、参考文献へ反映した。以下の表は初稿時の確認記録として保持する。

2026-09-26に一次資料を参照した。以下は草稿で述べた特徴の確認であり、網羅的な関連研究調査ではない。

| 資料 | 確認した範囲 | 草稿での用途 |
| --- | --- | --- |
| [MemGPT v2](https://arxiv.org/abs/2310.08560v2) | 著者・題名・版・要旨の階層的文脈管理と評価課題 | 外部記憶の位置づけ |
| [Collaborative Memory v1](https://arxiv.org/abs/2505.18279v1) | 著者・題名・要旨の個別／共有、来歴属性、動的アクセス制御 | 個別・共有領域との接点 |
| [PROV-DM](https://www.w3.org/TR/prov-dm/) | 編集者・2013年勧告、実体・活動・主体と由来関係 | 出典の表現 |
| [CaMeL v2](https://arxiv.org/abs/2503.18813v2) | 著者・題名・要旨の制御／データフローとcapability | 生成と規則の処理分担との接点 |
| [Qwen3.5-27B公式カード](https://huggingface.co/Qwen/Qwen3.5-27B) | モデル識別、提供者、2026年の引用情報 | 使用モデル。実測設定は保存済みdesignとenvironmentを優先 |

## 6. 保存・公開と執筆時の照合

資料は現在ローカル保管・非公開で、上記のリンクは研究フォルダ内を指す。公開用のDOI・ライセンス・独立した配布パッケージは未作成。第一報の再現資料を、第2報の再現資料として扱わない。

今回の主要7試験の監査資料2,933ファイルは、各試験の封印MANIFESTに対して一致を確認した。執筆前の原資料とナビを2,971アンカーとして記録し、ナビ以外の元資料を保持する。原回答の再生成・研究の再採点は行っていない。

- [本文数値・原文例・リンク等の照合結果](../../supplements/paper-02-draft-20260926/verification.json)
- [照合に用いたコード](../../supplements/paper-02-draft-20260926/verify_draft.py)
- [原資料の封印照合](../../supplements/paper-02-draft-20260926/source-manifest-verification.json)
- [引用した資料の対応とhash](../../supplements/paper-02-draft-20260926/evidence-sources.json)

### v0.2の編集照合

v0.2は既存結果を三つの知見から統合した編集改訂である。v0.1の表9（原案と実保存）を表8へ、表8（用途別利用の例）を表9へ移した。表2〜10のデータ、通し例、正式成績、事後参考分析の位置づけは保持する。上の初稿監査は初稿時点の記録として残し、改訂の照合は以下へ分けた。

- [改訂の照合結果](../../supplements/paper-02-revision-v02-20260926/verification.json)
- [改訂の照合コード](../../supplements/paper-02-revision-v02-20260926/verify_draft.py)
- レビューの採否と変更箇所 (see the evidence index)

### v0.3の関連研究調査と編集照合

方法・結果・実験表・原文例を保持し、関連研究節と考察の接続を追加した。表2だけを近接研究との比較表へ改訂した。MemProbe／MemAuditの版による改題と、同名のMemTrace二本を区別し、参照した版を明記する。

- [関連研究の調査メモと候補棚](related-work-review-v0.1-2026-09-27.md)
- 改訂メモ (see the evidence index)
- [今回の照合結果](../../supplements/paper-02-related-work-20260927/verification.json)
- [照合コード](../../supplements/paper-02-related-work-20260927/verify_draft.py)

### v0.4の用語・単位・解釈の明確化

「保存先」を論理的な情報欄と定義し、要旨へOR01の18材料×2反復とCU01の8ケース×2反復を補った。表8の24・32は観測行の不一致件数であり、同じ行の値・元ID・版に複数の違いがあっても一行と数える。§6.2では、全工程指標の定義上の性質と、実原案における重複不備・修復の観測を分けた。数値・採点・正式成績は変更していない。

- [レビューの採否と改訂箇所](revision-notes-v0.4-2026-09-27.md)
- [今回の照合結果](../../supplements/paper-02-revision-v04-20260927/verification.json)
- [照合コード](../../supplements/paper-02-revision-v04-20260927/verify_draft.py)
