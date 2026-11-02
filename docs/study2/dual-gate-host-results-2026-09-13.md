# 二段ゲートの実機接続小試験

2026-09-13、DUAL-GATE-HOST-01。**接続点検はPASS_HOST_GATE_CONNECTION。研究用の現CLI経路はROUTE_INCOMPATIBLE、実LLMの試行は未実施。** 実CLIから届いた要求を門番が拒否し、故障時も転送しなかった。正常系と応答側は、実HTTPを通す固定fixtureで確認した。

事前カード (see the evidence index)／実行記録 (see the evidence index)／原ログの別照合 (see the evidence index)。ユーザーの実機小試験GOを受け、試行順・上限・期待状態を実行前に固定した。

## 観測

| 試行 | 入力・故障 | 実測状態 | 上流fixture受信 |
| --- | --- | --- | ---: |
| H01 | 実CLI → 正常な入力gate | INPUT_REJECTED：TOOL_DEFINITIONS_PRESENT | 0 |
| H02 | 実CLI → 入力gateのexit 1 | GATE_UNAVAILABLE：GATE_EXIT_FAILURE | 0 |
| H03 | 実CLI → 入力gateのtimeout | GATE_UNAVAILABLE：GATE_TIMEOUT | 0 |
| H04 | 正常な固定HTTP要求 → text応答 | ACCEPTED：送信bytes・応答文字列とも不変 | 1 |
| H05 | 正常な固定HTTP要求 → function_call応答 | TOOL_REQUEST_BLOCKED：原応答の放出0 | 1 |
| H06 | 正常な固定HTTP要求 → 出力gateのexit 1 | GATE_UNAVAILABLE：原応答の放出0 | 1 |
| H04再送 | 別gatewayプロセス＋同じ永続claim | REPLAY_BLOCKED：追加転送0 | 追加0 |

7チェックポイントは6つの試行IDと1つの再送確認であり、独立な研究Nではない。19:21:05.463〜19:21:14.110 JST、約8.647秒、逐次実行。CLI起動3、局所HTTPクライアント4、上流fixtureの実受信3。CLIはいずれも要求1件の後に失敗状態で終了（終了コード1）、timeoutなし。これはゲートの403／503がCLIへ届いた観測であり、モデル回答の欠損ではない。

H01の実要求 (see the evidence index)には、input.additional_toolsに定義が残った。受け口はこれを削って通さず、原bytesを保存して拒否した。H02／H03では同じCLI構成の要求に対し、故障子プロセスの起動とGATE_EXIT_FAILURE／GATE_TIMEOUTを記録した。入力自体も不適合なので、これらだけで「本来通るCLI要求に対する故障の追加効果」を測ったとはしない。

H04〜H06は独自の最小形式を送るHTTPクライアントと、固定応答を返すローカルサーバーによる接続試験。上流の受信bytes・SQLiteの保存bytes・予定bytesが一致した。H04のcat／true／tools／犬・猫と二重空白は保持され、文字列の実行や意味による修理はなかった。H05のfunction_callとH06の原textは台帳に保存され、クライアントへは本文を含まない失敗通知だけが届いた。H04再送は別プロセスでも永続claimで拒否された。

## 検算と訂正

別スクリプトが実装をimportせず、原ファイル・SQLiteを読取専用で照合し、最終**422通過・失敗0**。元3実験と直近のローカル実装・証拠を含む241ファイルのhash、対象ディレクトリのファイル集合が不変だった。実行前にCLI・カタログ・gate・harness・入力・fixture・カードを固定した。

最初の検算は416通過・3誤警告。「item.completedが一つもない」を条件にしたため、CLI起動時のCode Mode無効通知（item.type=error）を生成結果と誤認した。全3件が同じ既知の起動通知だったことを原ログで確認し、型と通知本文を区別して修正した。元の検算 (see the evidence index)・元スクリプト・訂正 (see the evidence index)を保存し、実験・事前基準・原ログは変更していない。Code Mode無効の通知自体も消していない。

## 到達点と残る境界

今回確認したのは、**選んだlocalhost受け口に届く要求への実CLI接続と、局所HTTP経路の前後ゲート**。gatewayには外部転送先・認証情報処理・操作executorを配線していない。本文の放出0を、実Codexの全tool dispatcherやOS全体の迂回不能の証明にはしない。ホスト全体の通信をパケット監査した試験でもない。

CLIのgpt-5.6-luna／medium指定は要求の構成条件で、fixtureはLunaの回答ではない。実モデル推論・研究生成／採点・追加支払い・直接課金API・永続設定変更は0。通常の認証済みモデル接続と、今回の認証不要カスタムproviderは区別する。旧CLI設定は使い回してツールなしworkerに認定せず、旧FAIL_ENFORCEMENT・INCONCLUSIVEを保持する。

次は**本文と履歴だけから最終要求を組み立てる専用送信経路**の適合確認が必要。現CLIの生成機能をそのまま入口へ置くと、門番は正しく止まるが研究応答を得られない。既存ChatGPT認証をproxyで使う構成自体は[公式認証資料](https://learn.chatgpt.com/docs/auth)に記載があるが、今回その方式で接続・転送はしていない。今後採用する場合も、最終wire形式・認証の扱い・モデル到達・費用条件を先に具体化する。

記録先：throughline台帳§64 (see the evidence index)。新HANDOFF・予約は作成していない。
