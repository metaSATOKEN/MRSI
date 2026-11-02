# MEMORY-TRANSFER-02 v0.1 実行手順

対象runはstudy2/runs/memory-transfer-02-prepared-20260914。研究仕様は[固定設計](memory-transfer-02-plan-2026-09-14.md)。既知4履歴×全6役名配置×TIME/TYPEのKEEP48、会話履歴なし・共通事実メモ付きDROP12、計60新回答・Sol/Luna120票。E2本文はPC固定。通常80／最大100要求、逐次・モデル60分。設計・接続の承認と、実測開始の承認を区別する。

## 発行前

この範囲へのGOを受け、承認原文・対象run・config SHA・上限・保持期限をauthorization-contextに排他保存する。設計／接続completion、preparation-completion、config、元24履歴、固定60入力、100枠、依存ファイル、CLI binary hashを現在の実物で照合する。既選択のChatGPT利用枠を使い、新API鍵・支払い・モデルを設定しない。必要なlogin確認は秘密値を保存・表示しない。旧証拠の保護一覧を作る。

authorization／execution-start／acquisitionがなく、generations／batches／sender／dispatchが空であることを確認。authorization.jsonを排他作成する。5欄だけ：approved=true、configuration_sha256=今回config SHA、max_model_requests=100、max_seconds=3600、destination=https://chatgpt.com/backend-api/codex/responses。

```sh
python3 -B /Users/user/Desktop/Recync系/NPP/study2/runs/memory-transfer-02-prepared-20260914/frozen/memory_transfer_v2.py acquire /Users/user/Desktop/Recync系/NPP/study2/runs/memory-transfer-02-prepared-20260914
```

一度だけacquireし、未閉鎖runを自動再開しない。必要なローカル受信口がsandboxで制限された場合は、同じ承認範囲の処理に対する自動承認審査付き実行を使う。

## 取得

Luna medium、fresh context。送信直前に固定bytesを再構成する。TIME/TYPEは共通事実メモの中間2文だけが入れ替わる。KEEPには旧JSON原文24件を計288回そのまま挿入。DROPは会話節だけを持たず、旧今両方の事実メモを持つ。4種類のDROP入力を各3回新規生成し、合計60回答・52入力種類を区別する。新しい履歴群は0。

全60生成が形式成立した後、固定10バッチ×Sol/Luna mediumを採点。各バッチ6匿名説明＋同一E2 PC＋不変v0.4だけを渡す。履歴・メモ・条件・帰属・preference・他票は渡さない。tools=[]／tool_choice=none／parallel_tool_calls=false／store=false。全件取得まで原票を維持する。

構造的な理由欠損だけ各採点バッチ最大1補完。初回・補完・差分・予定外ラベル変更を保存し、欠損が残れば固定分母の未確定へ。生成修復、意味修正の再採点、非空理由の書き直し、追加N、モデル変更はしない。3400秒又は残り200秒未満で新発行停止、総上限100要求。入力256KiB、SSE4MiB、本文64KiB。受信120秒、CLI180秒、外側190秒＋終了最大5秒。経路・入力・封印・保存の異常は停止。生成不成立なら採点に進まない。

## レビュー

status、review-bundle、review-templateを排他保存する。主値は全件レビュー封印までnull。未開始／未閉鎖／INCONCLUSIVE_ROUTE／INCONCLUSIVE_GENERATION／PENDING_SEMANTIC_REVIEWを区別する。

全20採点バッチの全6件と四理由を最後まで読み、読了範囲を別途reading-recordに記録する。全120票にlabel／quote／adoption／alternative／uncertainty／change／changes、未選択、具体的noteを記す。全60原文にrole_reference、noteと、event_target・fact_groundingの二欄を必須保存。二欄はverdict、原explanationの連続引用quote、fact_ids、具体的reason。

事実ID：E2-INTRO、E2-P、E2-C-POSITION、E2-C-BUTTON、E2-LIMITATIONS、E1-MEMO-P、E1-MEMO-C、OLD-ONLY、NONE。重複・未知・空集合を拒否し、NONEは単独。event_targetのFAIL/UNRESOLVEDはfact_groundingにも同じ値を要求する。対象PASSでも観測対応は別判定。

E1-MEMOは過去比較の追跡用。例えば「先月は入口、今回は画面上の位置」は明示的類推として許容し、「動画が多いのは入口に近い机だったから」は旧事実の混入として非PASS。単語一致で意味を決めず、全文の参照関係を読む。仮説と観測済み断定を分け、有効な未選択OTHERも許容する。実因果の正解は要求しない。root非盲検レビューは独立正解ではない。

120票・60原文の予定キー完全一致、引用実在、原文・取得・履歴層・材料・入力契約（メモ込み）・割付・レビュー契約・分析契約hashが保存条件。submit-reviewで一度だけ封印し、その後に条件集計する。意味の曖昧さで再生成・再採点・指示改訂へ戻らない。

## 解析・別検算・記録

H_C=K_C,TIME−K_C,TYPE、H_DROP=D_TIME−D_TYPE、G_C=H_C−H_DROP。メモPC/CPを等重み。主H_Cは回答自体のC方向移動、主G_Cは会話履歴なしで生じる移動を差し引いた分。両者を別々に出し、和を成功指標にしない。理論範囲H_C±2、G_C±4。

label／quote／adoption、原文二欄の非PASS、採点欠測・UNSCORABLEは原文ごとにx∈{−1,0,+1}。両採点法・51指標で共通とし、DROPを複製せず全60の予定分母を保つ。旧TRANSFER-01の未確定原文は継承しない。理由品質だけの非PASSは分類から切り離して記録。原ラベルの参考範囲は主要判定に使わない。

両主下限>0はC_REPLY_SHIFT_BEYOND_DROP、G_Cだけ>0はRELATIVE_CONTRAST_ONLY、H_Cだけ>0はC_REPLY_SHIFT_ONLY、その他C_SHIFT_NOT_ESTABLISHED。負の成分は必ず併記。両採点法が違えばRATER_DEPENDENT。T_C_TYPEの水準方向も別記し、両主正でもDROPよりC側にあるとは限らない。メモ順別は記述で、順序単独の因果推定をしない。

元SSE・送信境界・二段SQLite・初回／補完・原ラベル・レビューから別コードで検算する。保存した合成verifierは入力再構成・数式の参考になるが、実測に使う際はsyntheticメタデータの条件と欠測候補の読込みを実観測に合わせて監査用の別名コードへ移し、合成証拠を実機証拠へ改名しない。

全原文・全票、各履歴／役名配置／レイアウト／メモ順、生ラベル、未選択、preference、品質・欠測・新旧事実の対応を保存。reviewed-result、結果レポート、completionを封印し、throughline台帳・PROJECT・Study 2 README・pointerを更新。過去証拠を書き換えない。p値・CI・人格・内部記憶・NPP・意味距離の純粋機序を認定しない。

保持期限2026-10-12 17:41:23 JST、dir0700/file0600。取得後の全件レビュー・解析・別検算・記帳はモデル60分の外で完了する。追加実験・HANDOFF・予約は自動で作らない。
