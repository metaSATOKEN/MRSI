# MEMORY-OWNER-03 v0.1 実行手順

対象は修正版の未実行run (see the evidence index)。最初のprepared-20260913は状態表示修正前の証拠として保存し、発行には使わない。実モデルの承認はまだなく、ここに示す発行コマンドはGO後だけ実行する。

固定カード (see the evidence index)／[準備結果](memory-owner-03-ready-v0.1-2026-09-13.md)／[元設計](memory-owner-03-plan-2026-09-13.md)。

## 発行前

1. ユーザーが新しい48生成＋12初回採点、理由欠欄だけ最大12追加＝最大72要求、逐次・モデル60分という範囲を承認したことを、発言原文とともに新しいauthorization-context.jsonへ記録する。現在の「接続準備」の承認だけでこの手順へ進まない。
2. runのconfiguration-seal、preparation-completion-seal、frozenファイル、CLI binary hashとChatGPT login statusを再確認する。authorization／execution-start／acquisitionが未作成で、generations／batches／sender／dispatchが空であることを確認。元の割付・指示・モデル・期限を変更しない。
3. authorization.jsonを排他的に新規作成する。内容はapproved=true、configuration_sha256=対象configuration.jsonのSHA-256、max_model_requests=72、max_seconds=3600、destination=https://chatgpt.com/backend-api/codex/responses。承認の記録は認証情報ではなく、APIキー・支払い設定を変更しない。
4. 対象run内の凍結コードを1回起動する。作成済みのexecution-startがある場合は、成否にかかわらず同じrunを再起動しない。

```sh
python3 -B /Users/user/Desktop/Recync系/NPP/study2/runs/memory-owner-03-prepared-20260913-r2/frozen/memory_owner_v3.py acquire /Users/user/Desktop/Recync系/NPP/study2/runs/memory-owner-03-prepared-20260913-r2
```

48生成・12初回採点の順序と最大12再提出枠は固定。初期r0の12wireは準備済み。r1の12wire、比較の24wire、採点の12初回wireは、前段の完全な原出力を受けて段階全体を封印してから送る。発行直前にも原文と固定仕様から要求を再構築して照合する。

モデルへ操作ツールは渡さず、実送信本文は専用senderの二段検査を通す。予定外ID・追加呼出し・不明送信の再試行は拒否する。理由が空でない意味上の不備や分類未裁定への再提出は行わない。

## 状態と停止

statusコマンドは同じ凍結コードで取得する。主区間は、観測と所定レビューの完了までnull。

```sh
python3 -B /Users/user/Desktop/Recync系/NPP/study2/runs/memory-owner-03-prepared-20260913-r2/frozen/memory_owner_v3.py status /Users/user/Desktop/Recync系/NPP/study2/runs/memory-owner-03-prepared-20260913-r2
```

- DISPATCH_PREPARED_AWAITING_GO：未実行。
- ACQUISITION_STARTED_NOT_CLOSED：実行開始記録はあるが取得を閉じていない。進行中か中断かは原プロセスと記録で確認し、自動再開しない。
- INCONCLUSIVE_OBSERVATION：生成・入力・経路等が不成立。予定分母を残し、主要区間はnull。
- PENDING_SEMANTIC_REVIEW：取得は成立し、レビュー待ち。採点だけの欠損は保持する。
- COMPLETE_SENSITIVITY：レビュー記録が揃い、主要分類の未確定を含む区間を計算済み。全域正、全域負、0を含む区間、基準差なしを分けて読む。

モデル発行〜返却の上限は60分。開始56分40秒以降、または残り200秒未満なら発行しない。原SSE4 MiB、復元本文64 KiB、入力256 KiB、各要求の受信・CLI・外側待ちの既存上限を維持する。時間超過、入力・出力gate、保存・hash、送信状態不明は停止し、成功するまで繰り返さない。

## 取得後のレビューと解析

1. acquisitionと全段階・原SSE・journalの封印を確認する。観測不成立なら取得済みの原文・欠損を記録して終了し、部分的に成立した組へ分母を減らさない。
2. `review-bundle RUN`で、全72予定評価について匿名説明、候補原票、7項目の観点、再提出差分、候補hashを読み出す。24履歴の本文も示される。`review-template RUN`は未記入値nullの雛形を返すので、雛形をPASS票として使わない。
3. rootが全72行を一巡し、label／quote／adoption／alternative／uncertainty／change／changesをPASS・FAIL・UNRESOLVEDで記録。主説明未選択をYES・NO・UNRESOLVEDで別記する。候補がない行は全てUNRESOLVEDで、原因をnoteへ残す。主説明を採用したP/C/MIXEDを支持する行では未選択はNO。OTHERでもP/C以外を主因とした場合は未選択NOとなる。
4. 24履歴の原文内の役名参照をPRESENT・ABSENT・UNRESOLVEDと具体的なnoteで記録する。原文を修理せず、該当履歴を含む比較入力へのフラグとして伝える。
5. 完全なJSONをrun外の一時ファイルへ書き、`submit-review RUN JSON_FILE`で一度だけ登録する。候補・差分・取得封印と72行／24履歴のID完全一致が必須。これは非盲検の仕様点検であり、独立した意味正解の保証ではない。既存のbatch別full-quality exportは変更・利用しない。
6. 再度statusを読み、返された区間・全条件内訳・端点・未確定ID・支持票の解放・品質・犬猫選択をreviewed-result.jsonとして排他的に保存する。新しい本文の原票から別実装で計算と出所を照合する。今回の合成ラベルや合成レビューを流用しない。

レビューJSONにはレビュー者名、blind=false、取得封印hash、各候補・差分hashを含める。未記入のままの登録は拒否するが、記録されたFAIL／UNRESOLVEDは再裁定を求めず固定の利用条件で感度分析へ渡す。片方に主要分類の未確定がある原説明は両者共通の変数にし、基準側のH/Lも全組合せで点検する。理由の他欄だけの不備は品質フラグとして保持する。

最後に研究結果文書・throughline台帳・現在地・03専用pointerを更新し、実行原文と完了封印を残す。旧01／02・旧事後解析は変更しない。dir0700/file0600、保持期限2026-10-12 17:41:23 JST。新HANDOFF・予約は終了の依頼がない限り作らない。
