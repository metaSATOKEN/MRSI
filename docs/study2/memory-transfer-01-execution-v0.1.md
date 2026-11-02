# MEMORY-TRANSFER-01 v0.1 実行手順

対象はstudy2/runs/memory-transfer-01-prepared-20260914。既知4履歴のKEEP48／共通DROP12、固定した翌月の動画再生E2、全6帰属配置×現在PC/CP。新60回答・Sol/Luna120票、通常80／最大100要求・逐次モデル60分。研究仕様は[設計](memory-transfer-01-plan-2026-09-14.md)、二欄の契約は凍結review-contract.md。

## 発行直前

接続・合成テストのGOとは別に、この具体範囲を提示して実測GOを確認する。GOの原文、対象run、config hash、上限、保存期限をauthorization-contextへ記録する。既に選択済みのChatGPT利用枠と架空材料だけを使い、新APIキー・支払い設定・モデル変更をしない。

設計completion、接続completion、preparation-completion、config、元24履歴、固定60入力、100枠、実行器の依存ファイル、CLI binary hashを現在の実物で照合する。ログイン確認は方式だけを残し、秘密値を出力しない。generations／batches／sender／dispatchが空、authorization／execution-start／acquisitionがないことを確認し、旧証拠の保護一覧を保存する。

authorization.jsonを排他作成する。5欄のみ：approved=true、configuration_sha256=今回configのSHA256、max_model_requests=100、max_seconds=3600、destination=https://chatgpt.com/backend-api/codex/responses。

```sh
python3 -B /Users/user/Desktop/Recync系/NPP/study2/runs/memory-transfer-01-prepared-20260914/frozen/memory_transfer_v1.py acquire /Users/user/Desktop/Recync系/NPP/study2/runs/memory-transfer-01-prepared-20260914
```

一度だけacquireする。未閉鎖runを自動再開しない。ローカル受信口にsandbox制約がある場合、同じ承認範囲の送受信に必要な自動承認審査付き実行を使う。

## 取得

送信直前に毎回入力を再構築し、固定bytesと照合する。KEEP/DROPの差は会話節だけ。共通の時点案内とE2事実を全条件に保持する。元JSON24件を計288回そのまま挿入し、DROPの二種類の入力を新規文脈で各6回生成する。別個体や新履歴群と数えない。SWAP条件はない。

全60生成が形式上成立してから、10匿名バッチ×Sol/Lunaの20採点要求を固定する。採点者にはE2（PC表記）・匿名説明・v0.4だけを渡す。tools=[]／tool_choice=none／parallel_tool_calls=false、全モデルmedium。理由構造欠損だけ各バッチ最大1再提出。元応答・補完・予定外の変更差分を保存する。意味の再採点、生成修復、追加件数、別材料への切替はしない。

開始3400秒又は残り200秒未満で新発行停止、総上限100要求。入力256KiB／原SSE4MiB／本文64KiB、受信120秒／CLI180秒／外側190秒＋終了最大5秒。入力・封印・保存・送信不明・経路の異常は即停止。生成不正のみなら生成段階を閉じ採点なし。採点形式不成立のみなら予定分母を保持する。

## 全件レビュー

status、review-bundle、review-templateを排他保存する。レビュー前の主値はnull。未開始、開始したが未閉鎖、INCONCLUSIVE_ROUTE、INCONCLUSIVE_GENERATION、PENDING_SEMANTIC_REVIEWを区別する。

全120票を非盲検で最後まで読み、label／quote／adoption／alternative／uncertainty／change／changes、主説明未選択、具体的理由を記録する。全60原文には役名参照と次の二欄を別々に記録する。

| 欄 | 記録すること |
| --- | --- |
| event_target | E2の動画再生を説明しているか、旧事象だけか、対象不明か |
| fact_grounding | 主説明の観測前提がE2と対応するか。昔の事実や未提示情報を今回の観測済み事実へ混ぜていないか |

各欄はverdict（PASS／FAIL／UNRESOLVED）、quote、fact_ids、reasonを必須にする。quoteはJSONを復号した元explanationに連続して存在する引用。全60生成は既に非空の説明として成立しているため、レビューの空引用は受理しない。fact_idsはE2-INTRO、E2-P、E2-C-POSITION、E2-C-BUTTON、E2-LIMITATIONS、OLD-ONLY、NONEから重複なしで選ぶ。NONEと他IDは併記しない。event_targetがFAILならfact_groundingもFAIL、UNRESOLVEDなら同じくUNRESOLVED。PASSの対象に対してgroundingだけFAIL/UNRESOLVEDは許容する。

単語の出現だけで裁かない。明示的な過去との類推や仮説と、未提示事実の断定を分ける。OTHERの未選択も両欄PASSになり得る。機械はID・hash・引用の実在・欄の充足を確認するが、意味の正しさを保証しない。曖昧な原文は未確定のまま残す。研究用生成LLMへ意味修正のリトライはしない。

全120票／60原文の予定ID集合の完全一致、原文hash、acquisition、source-strata、E2材料・二欄の記録契約・係数契約のhashが保存前の必須条件。submit-reviewで一度だけ封印する。条件別集計を見る前にレビューを固定する。rootの非盲検点検を独立した正解とは置かない。

## 集計と保存

statusをreviewed-result.jsonへ排他保存。主P_TRANSFER=KEEP_P−DROP、C_TRANSFER=DROP−KEEP_Cを別々に算出する。label/quote/adoptionの非支持、新二欄の非PASS、採点欠測・UNSCORABLEは原文ごとの共有x∈{−1,0,+1}へ。両採点法・全指標で同じ原文を一変数とし、DROPを複製せず、予定分母から除かない。

frame_supportedとE2対応込みのsupported、未確定理由を別に残す。原ラベルだけの参考範囲も保存するが、主要判定には使わない。二主対象の和、別々の端点の同時実現、信頼区間、p値、内部記憶・人格・NPP認定へ読み替えない。

原SSE・送信境界・二段SQLite・原ラベル・レビューから、実験計算器を使わない別計算で照合する。各現在順・各履歴・各帰属配置・生ラベル・未選択・二欄・品質・欠測・preferenceの内訳を記録する。結果とcompletionを封印し、throughline台帳・PROJECT・Study 2 README・新pointerを更新する。元試験・失敗・pointer・BAR台帳は保持する。

保持期限2026-10-12 17:41:23 JST、dir0700/file0600。取得後のレビュー・検証・記帳はモデル60分枠の外で完了させる。追加実験・HANDOFF・予約は自動で作らない。
