# MEMORY-OWNER-04 v0.1 実行手順

対象は`study2/runs/memory-owner-04-prepared-20260914`。研究条件は固定カード (see the evidence index)と[設計](memory-owner-04-plan-2026-09-14.md)を参照。**接続準備へのGOだけでは発行しない。** 未発行runを上書き・再抽選・再起動しない。

## 発行前

1. 新48回答＋Sol/Lunaの16初回採点、理由構造欠損のみ最大16追加＝上限80要求、通常64、逐次・モデル60分について明示GOを受け、発言と日時をauthorization-context.jsonに保存する。固定4履歴への追試、レビューはモデル時間枠外、架空材料のみ、利用枠消費・追加支払い設定なし、保存期限を含む範囲を維持する。
2. configuration-seal、preparation-completion-seal、frozenとinherited、48入力のhash、CLI binary hashとChatGPT login statusを再確認する。authorization／execution-start／acquisitionがなく、generations／batches／sender／dispatchが空であることを確認する。合成runの認証・HTTP・プロセス情報をlive証拠に使わない。
3. authorization.jsonを排他作成する。`approved=true`、対象configuration.jsonの`configuration_sha256`、`max_model_requests=80`、`max_seconds=3600`、`destination=https://chatgpt.com/backend-api/codex/responses`の5欄のみ。これには認証値を入れず、APIキー・課金設定を変更しない。
4. 下記を一度だけ起動する。失敗を含めexecution-startがある同runを再起動しない。

```sh
python3 -B /Users/user/Desktop/Recync系/NPP/study2/runs/memory-owner-04-prepared-20260914/frozen/memory_owner_v4.py acquire /Users/user/Desktop/Recync系/NPP/study2/runs/memory-owner-04-prepared-20260914
```

## 実行中

48新回答の全入力は準備済みで、各発行直前に旧原履歴と指示から再構築して設計bytesに照合する。旧24原履歴と基準24票はinheritedに分離され、今回の新生成・採点には数えない。両条件で同じ研究用IDを再使用せず、SHORTにも新しく回答させる。

全48生成が有効な場合だけ、匿名8バッチ×2採点者の16初回要求を一括固定する。本文は原生成のexplanationだけを渡し、条件・履歴・役・preference・研究用ID・仮説は渡さない。v0.4採点指示を維持する。対象バッチの構造欠損だけ最大1再提出し、初回・最終候補・すべての差分を保存する。非空な理由の意味不足や分類未確定には再提出しない。

予定順・親要求・最大80枠を照合し、発行記録を先に保存する。開始3400秒以後、または残り200秒未満では新規発行しない。各senderは受信120秒／CLI180秒／外側190秒＋終了最大5秒。tools=[]、tool_choice=none。原SSE4 MiB／本文64 KiB／入力256 KiBの上限を継承する。

生成形式不正だけなら48生成段階の残りを閉じ、採点へ進まない。採点の構造不正だけなら正常な経路の他の初回を閉じ、該当6原文は測定未確定にする。誤入力、gate・経路・保存・hash異常、送信不明では即時新規発行停止。欠けた生成や経路異常を分類未確定で埋めて主比較を出さない。

## 状態

```sh
python3 -B /Users/user/Desktop/Recync系/NPP/study2/runs/memory-owner-04-prepared-20260914/frozen/memory_owner_v4.py status /Users/user/Desktop/Recync系/NPP/study2/runs/memory-owner-04-prepared-20260914
```

- DISPATCH_PREPARED_AWAITING_GO：未実行。
- ACQUISITION_STARTED_NOT_CLOSED：取得を開始したが未閉鎖。自動再開しない。
- INCONCLUSIVE_OBSERVATION：生成・経路等が不成立。主区間はnull。
- PENDING_SEMANTIC_REVIEW：取得閉鎖、レビュー未登録。主区間はnull。
- COMPLETE_SENSITIVITY：レビュー固定後に分類感度区間を計算済み。方向や効果の有無とは別の完了状態。

## 取得後

1. acquisitionと原SSE・SQLite・段階sealを照合する。観測不成立なら原文・欠損・停止理由を保存し、成立した部分だけで予定分母を変更しない。
2. `review-bundle RUN`、`review-template RUN`を別ファイルへ保存。新96評価と新48原文の参照注記が対象。旧基準24票のhashがレビューに束縛され、旧票の再裁定欄は設けない。
3. rootが新96行について原説明・ラベル・引用・adoption／alternative／uncertainty／change・再提出差分を一巡し、PASS／FAIL／UNRESOLVED、未選択YES／NO／UNRESOLVED、具体的理由を記入する。新48原文の役名参照を注記。未記入テンプレート、予定外ID、候補hash不一致は拒否される。非盲検の仕様点検であり独立した意味正解保証ではない。
4. `submit-review RUN JSON_FILE`で一度だけ登録。レビュー原文と候補・取得・旧基準のhashを保存。意味の曖昧さが残っていても記録が完結したら分析する。意味の再提出・モデル追加をしない。
5. `status RUN`からreviewed-result.jsonを排他保存。主範囲はΔ_FACTS、analysis内にΔ_SHORTとD。旧基準の同一変数が両条件へ使われること、端点の実現例、全4組・自己役・条件・採点法別内訳を別実装で照合する。
6. 未選択、OTHER、犬猫preference、測定未確定、理由品質、役名参照を分けて報告。全正／全負／0を含む方向を区別し、0を含むことを消失・同等の証明にしない。分類区間をp値や信頼区間に置き換えない。
7. 新結果とcompletionを封印し、throughline研究台帳・PROJECT・Study 2 README・04 pointerへ接続。元03の結果とpointer、元02のNA、BAR台帳は保持する。

全成果物dir0700/file0600、保持期限2026-10-12 17:41:23 JST。新たな意味レビューや別の対照条件は自動追加しない。
