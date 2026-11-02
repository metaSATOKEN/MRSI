# MEMORY-OWNER-05 v0.1 実行手順

対象はstudy2/runs/memory-owner-05-prepared-20260914。[設計](memory-owner-05-plan-2026-09-14.md)と固定研究カード (see the evidence index)に従う。準備済みrunを再抽選・上書き・自動再起動しない。

## 発行前

1. 新48回答＋96新評価、通常64／最大80要求、逐次・モデル60分、理由構造欠損だけ最大1再提出／バッチ、レビュー・検証はモデル枠外、架空材料のみ・既存ChatGPT利用枠・追加支払い設定なしの具体範囲を確認する。受けたGOをauthorization-context.jsonへ保存。準備のGOだけで発行しない。
2. configuration、準備completion、frozen、inherited、48入力の封印と、設計source-manifestの保護対象を照合。CLI binary hashとChatGPT loginを安全に確認し、認証値を出力・保存しない。既に選択済みのChatGPT経路を使い、APIキーの作成・変更・再選択は行わない。authorization／execution-start／acquisitionがなく、generations／batches／sender／dispatchが空であることを確認。
3. run/authorization.jsonを排他作成。approved=true、configuration_sha256=当該configuration.jsonのSHA256、max_model_requests=80、max_seconds=3600、destination=https://chatgpt.com/backend-api/codex/responses の5欄だけ。これを別runへ転用しない。
4. 凍結入口を一度だけ実行する。

```sh
python3 -B /Users/user/Desktop/Recync系/NPP/study2/runs/memory-owner-05-prepared-20260914/frozen/memory_owner_v5.py acquire /Users/user/Desktop/Recync系/NPP/study2/runs/memory-owner-05-prepared-20260914
```

## 実行中

全48入力は原履歴・共通指示・PC/CP事実から送信直前に再構築し、固定bytesへ照合する。旧24履歴と24基準票は分離保持。PC/CPとも新規回答で、旧04回答を補充しない。全48生成閉鎖後に匿名8バッチ×2採点者を固定し、順序どおり発行する。

現在順3PC/3CP・履歴初期順3PC/3CP、同一ペアは別バッチ。採点者は説明文と同じ出来事、v0.4指示だけを見る。理由4欄の構造欠損のみ最大1回の補完を認め、初回・補完・予定外変更を含む全差分を保存。非空理由の意味不備や分類未確定は再採点しない。

開始3400秒、または残り200秒未満では新規発行しない。各senderの受信120秒／CLI180秒／外側190秒＋終了最大5秒を継承。tools=[]、tool_choice=none、操作itemは拒否。入力256KiB・原SSE4MiB・本文64KiB。

生成形式不正のみなら生成段階の残りを閉じ、採点へ進まない。採点形式不正のみなら正常経路の残りを閉じ、該当原文は測定未確定。誤入力・gate/保存/hash/経路異常・送信不明なら即時新規発行停止。生成や経路不成立を分類未確定で埋めて主比較を出さない。

## 取得後

`status RUN`はDISPATCH_PREPARED_AWAITING_GO、ACQUISITION_STARTED_NOT_CLOSED、INCONCLUSIVE_OBSERVATION、PENDING_SEMANTIC_REVIEW、COMPLETE_SENSITIVITYを分ける。前2状態を混同せず、再実行しない。

1. 原ログとacquisition sealを照合し、review-bundle／review-templateを排他保存。レビュー前は主値null。
2. 新96票の全文・引用・4理由・差分をrootが非盲検で一巡し、label/quote/adoption/alternative/uncertainty/change/changesのPASS/FAIL/UNRESOLVED、主説明未選択、具体的理由を記入。新48原文の役名参照も記入する。旧24履歴の注記・旧基準を再裁定しない。
3. `submit-review RUN JSON_FILE`で一度だけ保存・封印。形式完全は意味正解の保証としない。曖昧さが残っていても全記録が完結したら分析する。
4. `status RUN`からreviewed-result.jsonを排他保存。primary_rangeは現在の順序差ORDER。analysis内のOWN_PC/OWN_CP/OWN_Dは副次の帰属差で、旧基準未確定はこれらにだけ寄与する。主ORDERに旧基準変数が混入していないこと、48新原文と全4組を保持することを別コードで照合。
5. 端点・割当、組別・自己役別内訳、未選択/OTHER/preference/品質/欠損/役名注記を別記。主ORDERが正でも、P↔C反転だけで生じたとは限らないため未選択の移動も確認。範囲をCI・p値に置き換えない。0を含む範囲は消失・同等の証明ではない。
6. 結果とcompletionを封印し、throughline台帳・PROJECT・Study 2 README・05 pointerを更新。元04/03/02の結果・pointerとBAR台帳を保持。追加実験を自動実行しない。

保持期限2026-10-12 17:41:23 JST、dir0700/file0600。新しいモデル要求の範囲を確認してから実行し、終了後のオフライン記録まで完了させる。
