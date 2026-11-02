# HISTORY-STABILITY-02 実行手順

2026-09-15。接続準備用。本実験は明日以降、ユーザーが実測開始を指示してから。今日の指示は準備まで。自動予約なし。

## 固定する対象

- run：`/Users/user/Desktop/Recync系/NPP/study2/runs/history-stability-02-prepared-20260915`
- 実行器：`/Users/user/Desktop/Recync系/NPP/scripts/history_stability_replication_v1.py`
- 状態ファイル：`/Users/user/Desktop/Recync系/NPP/study2/current-history-stability-02.json`
- 固定設計：`/Users/user/Desktop/Recync系/NPP/study2/designs/history-stability-02-20260915`
- 原文・候補・レビューの規則：[レビュー契約](history-stability-02-review-contract-v0.1.md)

新12場面・24履歴、形成144＋プローブ576＝720生成、Sol/Lunaの1,440評価枠。通常960要求、理由欄再提出240、空の明示的混雑への再送30、総1,230上限。6窓・各205要求／モデル活動90分、逐次。意味レビュー時間は別。

## 明日の開始前

1. HANDOFF、current pointer、準備completion、configuration-sealを実物照合する。コード・入力・割付・CLI hash・Python/NumPy/SciPy・保持期限を照合する。新旧の実験を合算しない。
2. 実測のGOを受けたら、`authorization_value(run)` が返す固定範囲を、runの新しい `authorization.json` に一度だけ保存する。今日そのファイルは作らない。モデルや件数・時計・指示を変更した値を承認文へ紛れ込ませない。
3. CLIは今日 `0.154.0-alpha.6.2` のローカルversion/helpだけ確認した。実際の認証とモデル応答は未確認。明日もCLI hashが一致しなければ、原runを保持し新しい準備記録で更新点を再検証してから実測する。APIキーの作成・読み出し・課金へ切り替えない。
4. 最初の予定要求から実際の疎通も観測する。正常応答を別の予備標本として捨てず、その予定IDの最初の応答として使う。未知の故障は固定停止。空の明示的混雑だけ固定再送対象。

## 6窓の順序

各窓NNは `wNN-formation` と `wNN-probe` の2区間。NN=01〜06を固定順で進む。順序の変更・並列発行・前段レビューの省略をしない。

1. `acquire-stage RUN wNN-formation`：r0 12件→r1 12件→形成採点8要求。構造上有効な全6発言を各群の履歴として保持する。
2. `review-bundle RUN wNN-formation` と `review-template RUN wNN-formation` を**ファイルへ保存**。bundleの24原文・48評価枠を全件読む。6件単位で読み出し、本文と候補を照合し、原文側2基準・役参照、判定側7基準・未選択・具体的注記を埋める。既存テンプレートのNULLを自動でPASSへ置き換えない。
3. `submit-review RUN wNN-formation REVIEW.json` で全予定ID・hash・引用・欄を検査し封印する。形成が全P／全C、意味不備／未裁定でも群を選び直さない。
4. `acquire-stage RUN wNN-probe`：96原文→プローブ採点32要求。KEEPに当該群の6原文、DROPは会話部分のみ除去。前の反復回答を次へ渡さない。
5. 同じ方法で96原文・192評価枠を全件レビューし、`submit-review RUN wNN-probe REVIEW.json` で閉じる。
6. 次窓へ進む。窓間の表示は取得数・故障・レビュー完了状況。S・CI・pに基づいて材料や件数を変更しない。

実際の呼出しは `python3 -B /Users/user/Desktop/Recync系/NPP/scripts/history_stability_replication_v1.py` に上記actionと絶対パスを渡す。`status RUN` は進行状態を返し、途中の統計値を計算しない。

形成とプローブの活動秒・物理要求・混雑再送を窓単位で合算する。間のレビューや休止時間は活動時計から除く。新しい窓になれば次の固定90分枠へ進む。失敗した窓を再起動して時計や再送枠をリセットする操作は禁止。

## 異常時

同一論理要求は初回含め最大3物理試行、30/90秒。窓の追加混雑再送は最大5。正常な輸送応答が出たら、その後の生成形式・引用・ラベル・意味を理由に再生成しない。理由NULL等だけは既存の最大1回差し戻しへ進め、非NULL欄・ラベル等の変更を候補単位で拒否する。

入力hash不一致・部分出力・未知エラー・timeout・ツール出力・生成形式不備・上限・時計切れは保存して停止する。`halt.json` または途中まで作られたstageを、そのまま再発行しない。`INCONCLUSIVE_ACQUISITION` として部分証拠を閉じ、必要なら別承認・別記録の継続案へ分ける。サブエージェント採点への自動切替はない。

## 全件終了後

全12区間のレビューを封印後、`export RUN` を1回実行する。全1,440枠をレビュー原本から再導出し、4分類一致率・全96セル・12材料の分類感度・t近似区間・片側p・Sol/Luna共通判定・副指標を保存する。

次に `python3 -B /Users/user/Desktop/Recync系/NPP/scripts/audit_history_stability_replication_v1.py RUN` で、原SSE・実送信・入力・履歴・レビュー・主S・t端点を別のコード経路で照合する。これは独立研究者の意味レビューではない。結果が正・負・未確定・採点法依存のどれでも閉じる。

生データ・各試行・レビュー・解析・照合をcompletionに封印して、throughline台帳とpointerを更新する。保持期限は2026-10-12 17:41:23 JST。今回の試験を終えたら、NPP予測利得の再現と機構分離のどちらへ進むかを符号に依存せず相談する。
