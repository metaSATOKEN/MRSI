# TCV02 受領結果の照合

2026-10-13。新材料の固定117回答を照合して閉鎖。[結果報告](../../experiments/TCV02/docs/three-role-comparison-vote-02-result-2026-10-13.md)／チェックポイント (source not bundled)。

原ZIP：`npp-tcv02-result-20261013-061923-878369ad.zip`。1,285,871 bytes、SHA-256 `273060974458e5b16f86710c20eae52c2d36b4105a21e402a9e529b7a1c2216a`。1,445 member（うち1,444封印ファイル）。[保管コピー](../../experiments/TCV02/archives/npp-tcv02-result-20261013-061923-878369ad.zip)。ZIP内コードを実行せず、配布前の信頼済みコードで再計算した。

## 再集計と別実装

[aggregateスクリプト](../../reference-code/aggregate_three_role_comparison_vote_02.py)による[固定再集計](../../experiments/TCV02/expected-result.json)が、ZIP内二つのreportと一致。117EOS、FORM9/9、投票両条件54/54、COMPARE比較54/54、欠測0。両ゲート `PASS_IN_FIXED_COMPARISON`、54対すべて両成立、`TIED_ON_COMMON`。

[標準ライブラリ別実装](independent_check.py)はTCV01のJSON・schema検査helperを継承し、TCV02の実FORM→VOTE経路に合わせて変更。実験scorerをimportせず、原経験からの分数算術、全入力の再構成、親保存物のhash、二段tokenizerと実token列、本人・比較・票、54対と層別を照合した。[42,728項目PASS](independent-check.json)。同一プロジェクト内の照合で、第三者追試ではない。

各FORMの保存物は両条件・三反復の12投票で共用され、投票から投票へのフィードバックなし。新経験ID・数値構成、旧条件の指示・schema・モデル継承を確認。原文・保存物の修復、採点変更0。

| 保存物 | 内容 |
|---|---|
| [全投票診断](../../experiments/TCV02/analysis/diagnostics.json) | 108投票、候補合計・本人と割付の一致/不一致・費用 |
| [本人形成診断](../../experiments/TCV02/analysis/formation-diagnostics.json) | 共通前段9件、別分母 |
| [原文例](../../experiments/TCV02/analysis/evidence-extract.json) | 結果後に選んだN01/Aの形成＋高低×二条件、第1反復5件 |
| [前回と反復の比較](../../experiments/TCV02/analysis/repeat-comparison.json) | 旧結果を合算せず、今回の全18入力×二条件の反復を記録 |

準備込み886.855秒、生成681.347秒、出力12,466 token。GPUはRTX PRO 6000 Blackwell Server Edition。ライブラリのreference実装へのfallback警告はworker.logに保持され、取得は上限内で完了した。取得経路の変更は行っていない。

## 記帳と保全

記帳前に配布時50ファイルの一致を確認 (source not bundled)。最新ナビ5ファイルと台帳の更新前コピーを保存し、台帳§369へ結果・予想照合・次候補を追記。[最終照合](delivery-check.json)／保存hash一覧 (source not bundled)。次設計・新生成・旧論文変更・公開0。
