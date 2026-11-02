# TCV01 受領結果の照合

2026-10-13。108回答の固定一巡を閉鎖。[結果報告](../../experiments/TCV01/docs/three-role-comparison-vote-01-result-2026-10-13.md)／チェックポイント (source not bundled)。

原ZIP：`npp-tcv01-result-20261013-053413-76c1649c.zip`。1,241,411 bytes、SHA-256 `64b9e29f467136c593df9b18d0ee7db923f95d5f247fa277aa92d7c0c49cfce9`。1,335 member（うち1,334封印ファイル）。[保管コピー](../../experiments/TCV01/archives/npp-tcv01-result-20261013-053413-76c1649c.zip)。ZIP内コードは実行せず、配布前の信頼済みコードを使った。

## 再集計

[aggregateスクリプト](../../reference-code/aggregate_three_role_comparison_vote_01.py)で全108回答を再集計。配布payload・schema・事前割付・実入力・保存hashを照合し、ZIP内二つのreportと一致した。[固定再集計](../../experiments/TCV01/expected-result.json)。

[別実装](independent_check.py)は標準ライブラリのみで、実験scorerをimportしない。全108回答と旧本人ノートの対応、原経験の分数算術、比較欄と票、実prompt/token hash、54対応対、層別・反復を照合。[結果](independent-check.json)の63,771チェックがPASS。照合項目数は標本数ではなく、第三者追試でもない。

| 項目 | 結果 |
|---|---|
| 完走 | 108 EOS、形式不備/欠測0 |
| 本人保持 | 両条件54/54 |
| 共通成立 | DIRECT52/54、COMPARE54/54 |
| 比較と票の適合 | COMPARE54/54 |
| 対応対 | 両成立52、COMPAREのみ2 |
| 正式ゲート / 条件差 | FAIL / BETTER_ON_COMMON |
| 実行時間 | 準備込み885.890秒、生成672.755秒 |

2不成立は第1反復のT02/C高案のHOLDとT03/A低案のACCEPT。指定2入力×2条件×3反復の12原文と実入力を読み、[抜粋](../../experiments/TCV01/analysis/evidence-extract.json)へ保存した。[全108診断](../../experiments/TCV01/analysis/diagnostics.json)／[旧TVR01を背景に分けた反復表](../../experiments/TCV01/analysis/repeat-comparison.json)。

## 記帳・保存

記帳前に配布時45ファイルの一致を確認 (source not bundled)。ナビゲーションを更新する前のコピーとledger-beforeを保存。台帳§367へ結果と次候補を記録。原結果・凍結配布物・旧論文は保持し、今回新規モデル実行・外部送信・公開0。

[最終照合](delivery-check.json)／保存hash一覧 (source not bundled)。次候補は二条件を固定した未使用の三者材料比較であり、次の実測・コードは未着手。
