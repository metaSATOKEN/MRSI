# TVR01 実測完走の照合記録

2026-10-13。[結果報告](../../experiments/TVR01/docs/three-role-vote-repeat-01-result-2026-10-13.md)／チェックポイント (source not bundled)。

原ZIPは672,528 bytes、SHA-256 `b631313a70cd56f9e4cb3c83832224edee24d692e6e0adbe12d5ba25c164f2bc`。manifest以外686ファイル。事前に凍結したローカルpayloadとコードで再集計し、ZIP内の二つのreportと一致した。返送ZIP内のPythonは実行していない。

```sh
python3 scripts/aggregate_three_role_vote_repeat_01.py npp-tvr01-result-20261013-045940-cf404568.zip --output /tmp/tvr01-recheck-new.json
python3 throughline/audits/three-role-vote-repeat-01-results-20261013/independent_check.py
```

第一行はNPPルートから実行し、出力には未使用の名前を指定する。第二行は自身の場所を基点に読む。

## 別実装照合

[検算コード](independent_check.py)はTB01検算の標準ライブラリ部分を再利用し、固定入力三反復の検査へ差分変更した。元の実験採点器・設計moduleをimportせず、原回答JSONと経験のFraction算術から四軸を検算した。同一プロジェクト内の別実装であり、第三者の盲検採点ではない。

[照合結果](independent-check.json)はPASS。26,001 assertionには重複キー検査等を含み、標本数を表さない。

- 全686ファイルのhash、凍結payload・design、原文と保存回答、EOS・seedを照合。
- 全54入力のmessage・prepared全体が旧固定入力と一致。旧TB01の二反復にも照合し、旧FORM本人ノートとの対応を確認。
- 全54回答のschema、本人・候補の経験算術、本人三項目、proposal_idと投票を検算。固定採点との不一致0。
- 役・材料・案・反復の分母と成立数、全18入力の三回の票と変動分類を再現。
- 元配布時の43ファイルは記帳前に全hash一致。記帳で更新した入口文書と台帳は変更前コピーを保存し、凍結実験部分は不変。

主担当は二つの混在入力の原資料・候補表・system指示・三反復の全6回答を非盲検で確認した。本人情報を正しく書いたまま誤保留／誤承認した。理由文は取得していないため、内的理由を確定しない。JSON修復、意味採点の訂正、追加生成は0。

## 証拠への入口

- [固定再集計](../../experiments/TVR01/expected-result.json)
- [全54回答の診断](../../experiments/TVR01/analysis/diagnostics.json)
- [18入力の新旧対応（分母は別）](../../experiments/TVR01/analysis/repeat-comparison.json)
- [混在2入力・6回答の実入力と原文](../../experiments/TVR01/analysis/evidence-extract.json)
- [原ZIPの同一コピー](../../experiments/TVR01/archives/npp-tvr01-result-20261013-045940-cf404568.zip)
- [配布照合](delivery-check.json)／今回のhash一覧 (source not bundled)

54 EOS、本人54/54、投票52/54、混在2/18入力、研究ゲートFAIL。準備込み480.308秒。台帳§365へ記帳し、結果にかかわらず固定一巡を閉じた。旧正式結果・一セル・指示・採点・論文・公開候補は保持。ローカルモデル取得・GPU実行・外部公開は0。
