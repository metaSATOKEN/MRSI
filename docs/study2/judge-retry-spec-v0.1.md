# 理由欄の1回差し戻し・意味レビュー待ち仕様

2026-09-13。事前カード (see the evidence index)、controller (see the evidence index)。ユーザーが§72の方針と「埋まった理由も意味レビューする」条件を承認した別版。既存のjudge_transport_v2、ResponsesRunner、入力／出力gateを利用する。旧実験・旧dispatcherは変更しない。

## 動作

1. 初回の最終wire要求・元packet・モデル・設定・部品hash・バッチID・異なる初回／再提出ID・再提出上限1を保存し封印する。
2. runの実行権を新規ファイルの排他作成で取得する。同一バッチの別プロセス・同時起動・再起動による実行を拒否。途中停止後の自動再開も行わない。別バッチ作成や実験全体の割付管理は信頼する研究controller側の責任である。
3. 初回は予定bytesを既存の入力gate→永続claim→transport→原SSE保存→出力gateへ通す。ACCEPTEDの完了本文を原文で保存し、理由欄の構造を検査する。
4. 初回が完全なら追加要求0でPENDING_SEMANTIC_REVIEW。未完了・入力／経路不明・gate／保存故障では後続なし。理由4欄だけの欠欄・空・NULL等で、ID・引用・STATUS・他の構造に不正がないときにだけ差し戻す。コード名だけでなく原値も確認し、改行不正をNULL扱いしない。
5. 同じmodel／developer／reasoning／tools等を保ち、user本文だけをtask（元packet）、initial_response（初回原文）、format_feedback（不足ID／欄名／形式コード）、固定retry_instructionへ置き換える。初回回答は過去回答というデータとして囲む。期待ラベル・期待理由・仮説・他モデル票を追加しない。
6. 再提出要求のbytes・hashと親子IDを保存し、新IDの入力gateとclaimを通して最大1回送る。要求が既存容量を超えれば送らない。全ID・全欄を返させ、全欄を再検査。初回からラベル・引用・STATUS・記入済み理由が変われば差分を残す。
7. 再提出が不正ならUNRESOLVED_AFTER_RETRY。形式が完全でもPENDING_SEMANTIC_REVIEW。初回失敗を成功へ置き換えず、再々提出しない。

発行準備前と再提出要求作成後に、凍結したdeadline_seconds（既定600秒）の経過を点検する。個々の通信を強制終了するタイマーはtransport側の責任であり、この部品だけで任意のtransportのハングを止める保証はない。実送信への採用時は既存送信器の有界な通信／プロセス時間と結び付ける。

## 意味レビューが済むまで保留

構造判定のaccepted_ratingsは診断・レビュー対象であり、そのまま研究用の出力とはしない。controllerのfinal.jsonは常にresearch_ratings=[]で閉じる。正式な研究用取出し口export_ratingsだけが、対応する意味レビューを照合して票を返す。ファイルを直接読み出す他コード・OS全体への強制保証ではなく、下流はこの入口を使う必要がある。

review_bundleが返すものは、元課題、初回／最終候補原文、全候補票、全差分、候補attempt ID／raw hash／diff hash。意味レビューはこの束を対象に別途実施する。コードが自動でPASS票を作る処理は持たない。

レビューはreviewer、blind、candidate_attempt、candidate_raw_sha256、diff_sha256、rowsを持つ。rowsは予定ID全件各1回で、以下の7判定と具体的noteを必須とする。

| 判定キー | 確認すること |
| --- | --- |
| label | ラベルが原説明の採用内容と一致する |
| quote | 引用が原文にあり、記録された説明を支持する |
| adoption | 現在の採用／同等採用／未選択の説明が妥当 |
| alternative | 他方の扱いと適用STATUSが妥当 |
| uncertainty | 原因の確実性と採用の関係、適用STATUSが妥当 |
| change | 判断の変更前後、適用STATUSが妥当 |
| changes | 初回からの変更を確認した。変更なしならその事実も確認 |

各値はPASS／FAIL／UNRESOLVED。全ID・全7判定がPASSで、候補／差分hashが一致し、レビュー保存が封印されている場合だけREVIEWED_READYとなる。欠落・別候補・改変・未封印は取出し拒否、FAIL／UNRESOLVEDはHELD_SEMANTIC_CONCERNS。UNSCORABLEを含む場合はHELD_UNSCORABLEとしてフレームの強制補完をしない。

元ラベルを固定して理由の辻褄を合わせさせない。変更されたラベルも原説明に照らして確認する。コードが保証するのはレビュー記録の網羅性と出所の対応であり、レビュー者の意味判断が正しいこと自体ではない。

## 保存と利用API

公開する操作はprepare、run、review_bundle、submit_review、export_ratings。runに渡すtransportはsend(request_bytes)からraw SSE bytesを返す既存経路相当の部品で、認証・実HTTP処理はこのcontrollerに含めない。現行コードでの外向き接続は未実測。

```python
plan = judge_retry_v1.prepare(new_batch_directory, batch_id, frozen_wire_bytes)
outcome = judge_retry_v1.run(new_batch_directory, bounded_transport)
bundle = judge_retry_v1.review_bundle(new_batch_directory)
# 別途、原説明・原回答・差分を読んだ全件レビューを作る。
decision = judge_retry_v1.submit_review(new_batch_directory, completed_review)
ratings = judge_retry_v1.export_ratings(new_batch_directory)
```

runが候補を作れなければreview_bundleは拒否する。レビュー用の書出しはバッチ外へ保存する。バッチには封印済み入力・計画・claim、attemptごとの最終要求／SQLite原SSE／route、原回答receipt、差分、final、closureを保存し、後から加えるレビュー3ファイルだけを区別する。closureのhashだけでなく必須ファイルとファイル集合も確認する。

submit_reviewは上書きしない。修正が必要なら元レビューを消さず、追加の監査手順で扱う。途中で保存に失敗したレビューも未封印のまま保留される。

集計は初回充足、理由欄だけの差し戻し対象、実再提出、再提出後の構造充足、意味適合／保留、未解決を分離する。再提出による独立Nの追加は0。モデルへの実要求数とは別に数える。
