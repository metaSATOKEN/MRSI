# TAR01 — 受領結果を照合して一巡閉鎖

2026-10-13。[結果報告](../../experiments/TAR01/docs/three-role-approval-readout-01-result-2026-10-13.md)／論文化チェックポイント (source not bundled)。

原ZIPは`npp-tar01-result-20261013-071229-08c825b9.zip`、928,777 bytes、SHA-256 `88f38a17a92140779aaf76637e441a87cfdf8a4d0e13bfcad34eea4c59db643a`。[同一保管コピー](../../experiments/TAR01/archives/npp-tar01-result-20261013-071229-08c825b9.zip)。688 memberのうち687封印ファイル。ZIP内コードを実行せず、配布前に保存したローカルコードを使用した。

## 固定再集計

[aggregate](../../reference-code/aggregate_three_role_approval_readout_01.py)の[再集計](../../experiments/TAR01/expected-result.json)がZIP内二つのreportと一致。54EOS、欠測・再生成0。本人三軸・合意・実行は54/54、承認状態53/54、全成立53/54、対応17/18、材料反復5/6。正式ゲートFAIL。

唯一の不成立は`TAR01-N01-A-R1-MISSING`。提示された票はB/CのACCEPTだけだが、AをHOLDと記録した。合意と実行判断はPENDING/HOLDで適切。同じ実prompt/token列の第2反復はA=MISSINGと記録した。N01/Aの全三状態・両反復を抜粋して保存した。

## 別実装の原文照合

[検算コード](independent_check.py)は標準ライブラリだけを使用し、実験scorerをimportしない。TCV02監査のJSON/schema検査の型を継承し、原親資料からの入力再構成、全実token列hash、ノート・票の由来と最小変換、原経験と実票からの六軸、状態別・対応組・反復・費用を計算。[32,201項目一致](independent-check.json)。同一プロジェクト内の別実装であり、新規モデル反復や第三者追試ではない。

| 保存資料 | 内容 |
|---|---|
| [診断](../../experiments/TAR01/analysis/diagnostics.json) | 全54件の実票、正解、回答、成分別成否、tokenと時間 |
| [原文抜粋](../../experiments/TAR01/analysis/evidence-extract.json) | 不成立を含むN01/Aの全6件、結果後の説明用選定 |
| [反復対応](../../experiments/TAR01/analysis/repeat-comparison.json) | 全27入力の二反復、同一入力、内容が変わった1件 |
| [補足](../../experiments/TAR01/analysis/supplementary-analysis.json) | 層別、状態混同行列、費用、既存JSONキーの意味 |

既存の`agreement_execution_all_states`は承認状態も含む三軸で17/18。合意と実行だけの18/18と区別して文書化した。正式コード・指標・成績を変更した補正ではない。

## 保全と次工程

記帳前確認 (source not bundled)で配布時51ファイル不変を確認。ナビ6ファイルと台帳を更新前に保全。台帳§372に正式FAIL、未返答の取り違え、実行判断の成立と終了規則を記録した。[最終照合](delivery-check.json)／hash一覧 (source not bundled)。

取得前の約束どおり追加生成・指示修正へ進まず、一巡を閉じる。最小追加の観測が揃ったので、次は第四報の日本語草稿と焦点を絞った関連研究確認。旧論文・旧成績・公開候補・今回の配布コードは保持する。
