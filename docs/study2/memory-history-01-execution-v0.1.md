# MEMORY-HISTORY-01 v0.1 実行手順

対象：study2/runs/memory-history-01-prepared-20260914。固定60入力、100枠、二主対象。設計・source-strata・割付・採点v0.4を変更しない。

## 発行直前

新60回答（KEEP48＋DROP12）・Sol/Luna計120評価、通常80／最大100要求・逐次・モデル60分、理由構造欠損だけ各採点バッチ最大1補完、架空材料のみ・既存ChatGPT利用枠・追加支払い設定なしの具体範囲を確認し、GOの原文をauthorization-contextへ保存する。今回の設計・準備の承認と、まだ具体化されていなかった発行枠を区別する。

準備completion、configuration、設計source-manifest、source-strata、全60入力、旧24履歴とCLI binary hashを照合する。ChatGPT loginを値の保存なしで確認し、APIキーの作成・変更・再選択はしない。authorization／execution-start／acquisitionがなく、generations／batches／sender／dispatchが空であることを確認する。旧証拠の保護一覧を保存する。

authorization.jsonを排他作成：approved=true、configuration_sha256=当該configのSHA256、max_model_requests=100、max_seconds=3600、destination=https://chatgpt.com/backend-api/codex/responses の5欄のみ。

```sh
python3 -B /Users/user/Desktop/Recync系/NPP/study2/runs/memory-history-01-prepared-20260914/frozen/memory_history_v1.py acquire /Users/user/Desktop/Recync系/NPP/study2/runs/memory-history-01-prepared-20260914
```

一度だけ実行する。未閉鎖runを自動再開しない。既知のsandbox受信口制約がある場合は、同じ承認範囲のローカル受信・送信について自動承認審査付き実行を使う。

## 取得中

全60要求を送信直前に再構築して固定bytesへ照合。KEEPでは原履歴288挿入、DROPでは現在事実・指示・役X・選択肢が残り、会話節がないことを維持する。DROPのCP6回とPC6回はそれぞれ同一入力の新文脈再生成であり、架空の履歴群・自己帰属を作らない。全60生成が閉じてから匿名10バッチ×両採点者の20要求を凍結し発行する。

全モデルmedium・tools=[]・tool_choice=none。採点者は出来事・原説明・v0.4指示だけを見る。理由のNULL等の構造欠損のみ1再提出、初回・再提出・予定外の変更差分を全保存。意味修復・生成修復・N追加・モデル代替はしない。

開始3400秒／残り200秒未満で新発行停止、最大100要求。生成形式不正のみなら生成段階を閉じ、主比較NA・採点しない。採点形式不正のみなら予定分母を維持して測定未確定。誤入力・hash・gate・保存・経路・送信不明の異常は即新規発行停止する。原SSE4MiB・本文64KiB・入力256KiB、受信120秒・CLI180秒・外側190秒＋停止最大5秒を維持。

## 取得後

1. status、review-bundle、review-templateを排他保存。主値はレビューまでnull。ACQUISITION_STARTED_NOT_CLOSED／INCONCLUSIVE_OBSERVATION／PENDING_SEMANTIC_REVIEWを分ける。
2. 全120票と60原文をrootが非盲検で最後まで一巡する。label／quote／adoption／alternative／uncertainty／change／changes、主説明未選択、原文への具体的理由、役名参照を記録。source-strataを後から付け替えたり旧票を追加したりしない。曖昧さは記録して感度分析へ渡す。
3. submit-review RUN JSON_FILEで一度だけ封印。各票は原バッチ・原採点hash・差分・acquisition・source-strataに結び付く。意味レビューは独立正解保証ではない。
4. status RUNをreviewed-result.jsonへ排他保存。primary_rangeは採点法ごとのP_SHIFT／C_SHIFT二つ。共通DROPの原文変数を両主対象・全履歴で一度だけ扱い、別指標の端点同士を同時実現点としない。P_SHIFT+C_SHIFTを主対象へ変更しない。
5. 原SSE・二段SQLite・原ラベル・レビューから、実験計算モジュールを使わず別計算で照合。各現在順、各履歴、全帰属配置、未選択・OTHER・preference・品質・測定欠損・明示参照を残す。幅をCI・p値・一般的効果ゼロの証明にしない。
6. 結果・completionを封印し、throughline台帳・PROJECT・Study 2 README・新pointerを更新。過去の結果・pointerとBAR台帳は保持する。追加実験やHANDOFF・予約を自動作成しない。

保持期限2026-10-12 17:41:23 JST、dir0700/file0600。モデル60分の後にオフラインレビュー・検証・記帳まで完了させる。
