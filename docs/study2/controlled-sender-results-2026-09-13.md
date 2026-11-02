# 専用送信経路：実LLMとの接続が成立

2026-09-13。**CONTROLLED-SENDER-02はPASS_CONTROLLED_SENDER_COMPATIBILITY。** CLIが追加するツール定義や文脈をモデル要求へ引き継がず、予定表で固定した本文と設定だけを送る経路を実装した。Luna・mediumの新規1要求J02で、入力gate → 実モデル応答 → 出力gate → CLIへの本文表示まで成立した。

初回CONTROLLED-SENDER-01は応答形式の互換性不足でINCONCLUSIVEのまま保持した。両runを合算して実モデル要求2・CLI起動3、認証確認から終了まで約3分56.259秒。追加支払い・APIキー作成・本研究再走・同IDの再送は0。

## 何を変えたか

新しい送信器v2 (see the evidence index)は、CLIを既存ChatGPT認証でlocalhostへ接続する役に使う。CLIが作る要求は認証中継を開始するための入力として別保存するだけで、そこから本文・履歴・ツール定義・会話IDをモデルへ転送しない。

モデルに送るのは、信頼するcontrollerが事前に凍結した要求bytes。model、developer/user各1メッセージ、tools=[]、tool_choice=none、parallel_tool_calls=false、reasoning.effort=medium、store=false、stream=trueだけを含む。wire gate v2 (see the evidence index)が形式・予定hash・段階を照合し、SQLiteの発行記録を確定してから同じbytesをHTTP送信する。

受信SSEは原保存後に構造を検査し、途中に操作item・未知event・欠落・不整合があれば本文を放出しない。通った最終textだけを別の配信用SSEへ入れてCLIに返す。元ストリームを直接CLIへ流す経路、操作executor、認証値の永続保存、任意接続先、リダイレクト、自動retryは設けていない。APIキーの作成・読取・流用は行わず、既存CLIのログイン管理を使用した。

## 実測と互換修正

| run／ID | 内容 | 結果 |
| --- | --- | --- |
| 01／P0 | 既存ログインのlocalhost中継 | AUTH_BOOTSTRAP_PASS。外部モデル要求0、固定fixture |
| 01／G01 | 犬／猫・cat／true／toolsを含む合成入力 | HTTP200、LunaのDOG_CAT_OKを原SSEに観測。ただし受理・放出せずSEND_UNCERTAIN |
| 01／J01 | 合成文の文字列点検 | 互換性不足を受けて未発行 |
| 02／J02 | 未発行J01と同じ要求bytesを新IDで実行 | ACCEPTED。LunaのBOTHをgateが受理しCLIにもBOTHを確認 |

G01で止まった理由は、接続先のContent-Typeヘッダーが欠落していたこと。さらにオフラインで原SSEを点検すると、本文はoutput_item.doneに存在する一方、response.completed.outputは空配列だった。公開Responses形式の説明から想定した重複した最終outputを、この実接続の全応答へ要求していた不足だった。初回は入力gateだけを通り、出力gateには届かず、CLIへ失敗通知を返した。HTTP200・原SSE・103トークンの使用量があるので、「モデル未呼出し」とは記録しない。

この観測を根拠に02の事前カード (see the evidence index)を追加。ヘッダー欠落時もSSE構造gateへ進める一方、明示された異なるContent-Typeは拒否するようにした。完了output空の形式は、連続したadded/done・id・本文part・text_done・deltaが全て対応する場合だけ受理する。通常形式の最終output一致検査も残す。文字列の修理・補完は行わない。

既知G01の原応答は互換診断fixtureとしてのみ使用し、成功試行へ格上げしていない。追加の実確認は当初2要求の上限に残る1件を使い、新runのJ02で行った。J02は約4.384秒、HTTP受信約1.285秒。応答は111トークン（入力105・出力6）。2要求のモデル応答が報告した使用量は計214トークンで、親タスク全体の消費量ではない。

## 照合

- 初版の合成9テスト通過。改訂版は通常／空の完了output、ヘッダー欠落の正例と異形式の負例、途中操作・不整合・故障・再発行を含む12テスト通過。初回9テスト記録はtool出力を実行後に転記したものと明示し、12テストは直接保存したstdout/stderrを使用。
- 別集計 (see the evidence index)は493通過・失敗0。実装をimportせず、原ファイル・SSE・SQLite・CLIログから確認した。旧実験と初版run・ソース等379ファイルのhashと対象ディレクトリ集合は不変。
- J02は凍結要求＝入力gate対象＝送信直前bytes＝SQLite保存bytes。管理用nonceやCLIのadditional_toolsは送信本文に含まれない。サーバー応答にもmodel=gpt-5.6-luna、tools=[]、tool_choice=none、previous_response_id=nullを確認した。
- 出力gateが原SSEのhashを指定してPASSを返し、保存された本文BOTHとCLIのagent_messageが一致。CLIの操作itemは0。従来のCode Mode無効の起動通知1件は別に保持した。
- 認証ヘッダーは存在だけを記録し、値を保存しない。原応答に認証値が反射した場合は保存しない処理も設けた。補助的なパターン照合でも新出力にtoken／APIキーらしい文字列は検出されなかった。このパターン照合だけを秘密不在の証明にはしない。

## 到達点の限界

解決したのは、**最終要求を自分たちで組み立て、ツール定義なしで実LLMへ送り、検査後の応答を受け取る経路**。CLI本体やOS全体の権限を封じたことではない。ログインと外部通信を持つcontrollerは引き続き信頼する側にあり、研究workerがそのコードや予定表を書き換えられる運用は契約外。

最終要求の局所bytesは照合できるが、サーバー内部promptを直接観測したわけではない。たとえば送信要求にはprompt_cache_keyを含めていないが、応答にはその値が返った。この事実を保存し、「サーバー側も全欄が無追加」とは主張しない。認証中継自体は[公式のcustom provider認証仕様](https://learn.chatgpt.com/docs/auth)を使用したが、backendの今回の応答形式は実測に基づく互換対応であり、将来も固定された公開契約だとはしない。

実測したモデルはLuna、改訂版で受理したライブ試行はJ02の1件。Sol・並列発行・研究サイズの履歴は未検証であり、MEMORY-OWNER-01等を再走していない。次の研究試験へ採用する場合は、この送信器で各workerの入力を凍結する設計へ接続する。旧研究結果・主要ΔのNAは保持。

01の完了記録 (see the evidence index)／02の完了記録 (see the evidence index)／最新pointer (see the evidence index)。throughline台帳§65に記録し、HANDOFF・予約は作成していない。
