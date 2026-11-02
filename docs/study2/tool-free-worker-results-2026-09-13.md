# TOOL-FREE-WORKER-01：今回の設定ではツール定義が残る

2026-09-13。**今回の候補を「ツールを最初から提供しないworker」として採用することはできなかった。** shell等を無効にしても、CLIが送信する要求内に`functions.exec`・`functions.wait`・`functions.request_user_input`の3つのスキーマが残り、execの説明には`apply_patch`の呼出し定義も含まれていた。これはツールの提供が残る証拠であり、操作が実行可能だった／実行されたという証拠ではない。

ユーザーは、この構成の確認を明示承認した。固定カード (see the evidence index)に基づき、まずモデルを呼ばないローカル輸送fixtureで要求本体を捕捉した。受け口は認証不要・127.0.0.1限定で、外部へ転送しない。既存Lunaカタログ項目を値を変えずに固定し、通常ユーザー設定を読み込まず、shell／統合exec／apps／plugins／multi-agent／画像／browser／computer／goals／sleep／skill search等を無効にした。設定 (see the evidence index)と捕捉コード (see the evidence index)を保存した。

| 確認対象 | 観測 |
| --- | --- |
| 最上位の`tools` | 欄そのものが省略されていた |
| `input`内の`additional_tools` | 1項目。functions名前空間に3ツールのスキーマが存在 |
| exec内の操作案内 | `apply_patch(input: string)`の定義が存在 |
| Code Mode実行ホスト | 無効化されており、CLIに「使用不可・fail closed」の通知が1件出た |
| 操作実行 | fixtureは操作を要求しない固定応答。操作イベント0。実行能力は試していない |
| 実モデル | 0セッション。TF01／TF02はゲート未通過で未発行 |

一次証拠は受信要求全文 (see the evidence index)。ツール定義の抽出 (see the evidence index)は要求のhashと原スキーマを保持する。`functions.exec`内に登場する一般的な使用例の全名称を、提供された個別ツールとして数えてはいない。3つのスキーマと、その説明にあるapply_patchの宣言を分けて報告する。

**事前の主判定はINCONCLUSIVEのまま保持する。** 私が作ったカードは最上位の`tools`配列だけを前提にし、欄が欠けた場合をINCONCLUSIVEとしていた。実際には別の`input.additional_tools`に定義が載る形式だったため、事前の観測契約が不十分だった。要求全体を読んだ後の補足点検ではNONEMPTY_TOOL_DEFINITIONSを確認した。主判定を後付けでPASSへ変更せず、この候補は不採用として閉じた。判定と訂正記録 (see the evidence index)

途中の説明でも「ツール定義が含まれていない」と広く述べたが、正しくは「最上位のtools欄がない」だけだった。別の格納場所を発見した直後に訂正した。空のツール集合を確認したとする説明は撤回し、合格認定・モデル発行には使っていない。比較用ローカル要求も、定義の残存が見つかったため追加していない。

準備時には、`debug prompt-input`がmessage配列しか返さず、ツール一覧の証拠に使えなかった。sandbox内の最初の診断はCLI初期化権限不足で終了し、通常の初期化権限で同じ診断を取得した。いずれもモデル生成ではない。輸送fixtureの初回はstrict configが`tools.view_image`を未対応として起動前に拒否し、受信0件。元設定とエラーを保持し、この重複キーだけを取り除いた。対応する`features.view_image=false`は維持した。公式設定資料の記載と、このインストール済みバージョンの受理が一致しなかった。[公式設定リファレンス](https://learn.chatgpt.com/docs/config-file/config-reference)

修正後のローカル捕捉は18:47:39.586〜18:47:41.318 JST、約1.731秒で1要求を受信し正常終了。Authorizationヘッダーなし、要求モデルはgpt-5.6-luna・medium。受け口が返した`LOCAL_FIXTURE_ONLY`は固定の模擬応答で、Lunaの応答・研究標本・有料API生成には数えない。外部モデル呼出し・追加支払い・研究再走・永続設定変更は0。新規CLIの実際の認証済みモデル要求と同じツール集合であるとまでは認定しない。

別実装照合 (see the evidence index)は213項目通過・失敗0 (see the evidence index)。旧MEMORY-OWNERと前回実ホスト小試験のrun・結果・pointer計176ファイルが不変。CLI／固定カタログ／カード／設定修正差分／原要求／抽出スキーマ／未発行を照合した。前回のFAIL_ENFORCEMENT、MEMORY-OWNERのINCONCLUSIVEと主要ΔのNAは保持する。

次に試すなら、**ツールを受け付けない生成専用の経路を選び、その要求全体を点検する設計**が候補。既存CLIのこの設定だけでツール0を保証できるとは扱わず、Code Modeを壊して操作不能にする構成も採用しない。どの経路が既存ログイン・Luna／Sol・費用条件を満たすかは未確認で、今回新たな実装・実モデル試験はしていない。

集計 (see the evidence index)・完了記録 (see the evidence index)・最終保存照合 (see the evidence index)。台帳はthroughlineの§61 (see the evidence index)へ追記した。
