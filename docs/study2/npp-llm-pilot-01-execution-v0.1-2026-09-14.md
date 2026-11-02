# NPP-LLM-PILOT-01 実行手順 v0.1

2026-09-14。未発行run：`/Users/user/Desktop/Recync系/NPP/study2/runs/npp-llm-pilot-01-prepared-20260914`。本書作成中の実発行0。全工程は次の実測GO後に一度実行する。

## 入口

1. [準備完了文書](npp-llm-pilot-01-ready-v0.1-2026-09-14.md)の最終封印・旧保護・未発行状態を確認する。
2. ユーザーのGOを台帳へ原文で記録し、run/configuration.jsonのsha256に結びつけたauthorization.jsonを排他的に作成する。必須値はapproved=true、max_model_requests=180、max_requests_by_stage=[80,100]、max_active_seconds_per_stage=3600、destination=`https://chatgpt.com/backend-api/codex/responses`。構造はcontrollerのacquire_eventに固定済み。準備時にはこのファイルを作らない。
3. 新runの**frozen/npp_pilot_v1.py**を`python3 -B`で実行する。元scriptsを後から編集して実測途中へ入れ替えない。既存送信器がCLIのhashと機能制限を確認する。失敗時に別経路や別モデルへ逃がさない。

## 事象ごとの反復

E1からE8へ一方向に進む。各命令は上記frozen/npp_pilot_v1.pyへのサブコマンドで、RUNは上記絶対パス。

| タイミング | コマンドと作業 |
|---|---|
| E1〜E6の開始 | `acquire-event RUN EVENT_NUMBER`。その事象の生成と2採点法を一巡 |
| 各取得直後 | `review-bundle RUN EVENT_NUMBER`と`review-template RUN EVENT_NUMBER`を別ファイルへ保存 |
| 全件意味レビュー | 全予定票・全原文を読み、引用・理由・事実ID・欠測の各欄を埋める。UNRESOLVEDを許容し、既存票を上書きしない |
| レビュー保存 | `submit-review RUN EVENT_NUMBER REVIEW_JSON_PATH`。ID/hash/NULL/引用を検証し、原票から導いた記録と事象閉鎖を封印 |
| E6レビュー後 | `fit RUN`。E3〜E6だけでM0/M1を一度学習し、係数・出所・数値条件を封印 |
| E7開始前 | `forecast RUN 7`で全予測を封印してから`acquire-event RUN 7`。終了後に全件レビュー |
| E8開始前 | `forecast RUN 8`。E7までを過去stateへ追加するが係数は不変。その後`acquire-event RUN 8`、全件レビュー |
| 終了 | `status RUN`をreviewed-result.jsonへ排他的保存し、原票からの別照合・レポート・completion・台帳を閉じる |

出力ファイルが存在する時は上書きリダイレクトを使わない。各取得コマンドの標準出力／標準エラーは事象ごとの新ログへ残す。レビュー票は1事象あたり24票＋12原文、E7/E8では36票＋18原文。全イベント合計216票＋108原文。いずれも抜粋だけを読んで済ませず、全ID集合を確認する。レビューは非盲検と明記し、研究目的・群を知る担当者を独立の盲検採点者へ数えない。

E1入力12件は既存examplesと一致する。E2以後は、その群の終了済みKEEP原文から各事象の全入力を組み立て、生成前にrequest sealを作る。judgeも当該事象の全生成が整ってから、全バッチを先に用意・封印する。

## 途中の判定

段1の最大80要求と段2の最大100要求は独立の上限。取得関数内の実稼働時間を段ごとに累積し、3400秒で新規発行停止。レビューや予測計算のために同じ要求を再発行しない。別段へ時間・要求の未使用枠を移さない。

理由NULLのみ固定された1回の構造補完を許容する。2回目も欠損、または不正IDで候補を作れなければ票欠測としてレビューし、固定規則で先へ進む。生成のJSON不成立・ツール出力・送信不成立・時限超過はINCONCLUSIVE_PIPELINEで停止し、生成を修復しない。全学習target欠測や固定optimizer不収束も数値NAで停止する。

保存中断・封印変更・予測の時系列違反を検知した場合は、その例外と未取得IDを別の故障記録へ保存して終了する。整合性を取り戻すために旧原票・closure・configurationを作り直さない。途中の成果を効果0やCOMPLETEへ読み替えず、実行再開を自動で行わない。

## 終了報告

COMPLETE_PILOTまたはINCONCLUSIVE_PIPELINE、予定／実取得と欠測、各段時間、補完、各採点法のNPP_Brier、M0/M1損失、群×事象、共有DROP比較、支持／未裁定／品質フラグ、preferenceを記録する。未裁定範囲は固定学習に条件づけた分類感度で、CI・p値ではない。研究の独立群は4、未使用評価事象は2、補完のN追加は0。

正負・ゼロをまたぐ結果にかかわらず予定範囲で閉じる。完了後にだけ、追加確認研究を設計する価値と必要な規模を一度判断する。旧TRANSFER-02や旧進路pointerは保持し、パイロット専用pointerとthroughlineの台帳を更新する。HANDOFFはユーザーが区切りを求めた時に書く。
