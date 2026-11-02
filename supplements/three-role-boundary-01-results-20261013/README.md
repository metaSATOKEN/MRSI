# TB01 実測完走の照合記録

2026-10-13。[結果報告](../../experiments/TB01/docs/three-role-boundary-01-result-2026-10-13.md)／チェックポイント (source not bundled)。

## 原記録と固定再集計

原ZIP `npp-tb01-result-20261013-041945-c6e2c94d.zip`、1,370,167 bytes、SHA-256 `6069f4b583b414f4350440c6e163e77d0a09e1a48b6377a3b67d9ad7c2b58387`。manifest以外1,547ファイル。ローカルに凍結したv0.1.1配布payloadとの一致、原文・保存・親hash・実入力・採点と保存済み二つのreportを再現した。

```sh
python3 scripts/aggregate_three_role_boundary_01.py npp-tb01-result-20261013-041945-c6e2c94d.zip --output /tmp/tb01-recheck-new.json
python3 throughline/audits/three-role-boundary-01-results-20261013/independent_check.py
```

第一行はNPPルートから実行し、出力には未使用のファイル名を指定する。第二行はスクリプト自身の位置からパスを解決する。受領ZIPのPythonコードは実行せず、採点器は事前に保存したローカル版を使う。

## 別実装の照合

[independent_check.py](independent_check.py)は標準ライブラリだけを使い、元の採点器・設計モジュールをimportしない。封印hash、凍結design、schema、原文JSON、原経験のFraction算術、本人情報、元回答からの票、保存親、各回答の採点を照合。全126回答で固定採点と一致した。[機械結果](independent-check.json)。54,172 assertionにはJSONキー重複検査等を含み、この件数を独立検証数・標本数とはしない。

全18種類の投票入力について、二反復間のmessage・整形prompt・入力token列が同一。票が異なるのはT02高合計/Cのみ。原記録の再計算であり、別モデルによる採点・第三者の盲検評価ではない。

## 内容の点検

主担当が唯一の不成立票、90/84の候補表、system指示、Cの本人資料、T02高合計の二/三票時の実受領票と読出し、反復2の対応回答を非盲検で読解した。残りは全126回答の構造化一覧と算術照合で確認。理由文はそもそも取得しておらず、HOLDの内的理由は判定しない。数値・意味採点の訂正0。

- [結果保存先](../../experiments/TB01)
- [T02両反復の本人形成＋高合計経路24回答の原文・実message抽出](../../experiments/TB01/analysis/evidence-extract.json)
- [全126回答の診断](../../experiments/TB01/analysis/diagnostics.json)

修正後の実tokenizer事前点検はPASS、その後126回答EOS。研究ゲートFAILの原因はT02-R1-HIGHER-VOTE-CのHOLD一件。本人126/126、投票35/36、読出し72/72、全工程11/12、材料反復5/6。準備込み689.279秒。初回0生成結果と混ぜず、追加生成・ローカルモデルロード・公開0。

## 記帳

台帳§363。新しい結果報告とチェックポイントを作成。入口文書の変更前コピーは navigation-before (source not bundled) に保持。原ZIP、凍結実装、採点、既存論文・公開候補は不変。ファイル対応は [delivery-check.json](delivery-check.json)／manifest.json (source not bundled)。
