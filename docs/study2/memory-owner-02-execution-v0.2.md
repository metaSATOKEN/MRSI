# MEMORY-OWNER-02 v0.2 実行手順

2026-09-13。準備済み、実モデル未発行。事前カード (see the evidence index)と[準備結果](memory-owner-02-ready-v0.2-2026-09-13.md)を参照。旧v0.1仕様をこの改訂で上書きしない。

対象runは`study2/runs/memory-owner-02-prepared-20260913`。configは生成24、初回採点8、理由欄だけの最大8追加を含む40slotを事前固定した。全体43分、逐次、既存ChatGPT認証と同じ固定backend。実機の再提出分岐は前回未発動で、その成功は未測定。

## 発行前

1. この具体範囲へのユーザーGOを受け取り、発言をrun外の台帳へ記録する。今回の「次行こう」は接続準備として記録しており、このrunの発行記録はまだない。
2. `configuration-seal.json`と凍結ファイル、準備証拠、旧履歴のhashを再確認する。CLIのバイナリhashと`login status`が既存ChatGPT認証を示すことを確認する。キーや認証ファイルを読む必要はない。
3. GO後にだけrun直下へ`authorization.json`を新規作成する。形は次の4キーだけ：`approved: true`、`configuration_sha256: 現configの実hash`、`max_model_requests: 40`、`destination: https://chatgpt.com/backend-api/codex/responses`。別途台帳に範囲と実際の承認発言を残す。未承認時にこのファイルを用意しない。
4. localhost bind／外向き通信がsandboxで拒否される環境では、証拠付きの権限申請でこの固定実行を審査に出す。拒否を別経路で回避しない。発行済みか不明なら自動再実行しない。

## 実行

凍結版`frozen/memory_owner_v2.py`の`acquire RUN`を1回だけ起動する。現在のscripts版を更新して同じrunへ差し替えない。実行開始は排他的で、再起動／同IDの再送は拒否される。

controllerは24生成を閉じ、全て形式有効なら全8採点初回wireを一括生成・封印する。その後、固定順に初回採点と対象欠欄への最大1再提出を行う。初回だけ完全なら再提出なし。生成に不正があれば部分採点しない。経路故障なら後続を停止する。外側の全体時限とsenderの通信／子プロセス時限を併用する。

生成／採点の原文は`generations/`と`batches/`、実送信境界は`sender/`、排他的dispatch記録は`dispatch/`。judgeバッチの閉包内へ任意の追加ファイルを置かず、説明用コピーはrun外または別フォルダに出す。出力のNULLや不正票を手で補修しない。

## 全件レビューと集計

`acquisition.json`と`acquisition-seal.json`の保存・照合を確認する。正常取得でも主要Δはまだnullで、意味PASSではない。

各`batches/m2v2jNNN`について、凍結版`judge_retry_v1.review_bundle`から候補原文・元packet・差分を読み、全6IDの7項目と具体的noteを記録する。全8batch・48票を点検する。原文を最後まで読み、非空理由を自動PASSにしない。レビュー票は`submit_review`で1回だけ保存し、FAIL／UNRESOLVEDを成功へ書き換えない。研究仮説や期待方向に合わせた再採点を発行しない。

最後に凍結版`memory_owner_v2.py status RUN`または`conclude(RUN)`で状態を照合する。全48がレビュー受理されるまで両主要Δはnull。1欠測ならINCONCLUSIVE、構造が完全で意味に懸念があればMEASUREMENT_CONCERNS。全PASS時のみ各自己役・4組・2採点法の記述値を保存する。再提出があれば初回Δはnullで、最終候補のΔと合算しない。

結果は原SSE・SQLite・匿名対応表から別実装で再計算し、全レビューの候補hash、初回／補完の回数、未解決票を確認する。合成試験に保存したΔ=2は計器テスト用の人工値で、今回の研究結果へ混ぜない。

取得・レビュー・照合完了後に結果報告／completion／throughline台帳を作る。保管期限2026-10-12 17:41:23 JSTを継承し、新HANDOFFや予約はユーザーの終了指示なしには作らない。
