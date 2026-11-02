# 直接サブエージェント採点の補助経路 v0.1

2026-09-15。状態：**PREPARED_OFFLINE_ONLY**。ユーザーの直接サブエージェント採点案に対する exporter/importer と局所検証。実LLM採点・ネット通信・再委任は行っていない。元の `INCONCLUSIVE_ACQUISITION`、封印済みrun、既存の採点・報告書を変更しない。

実装は judge_subagent_fallback_v1.py (see the evidence index)、fixtureは test_judge_subagent_fallback_v1.py (see the evidence index)。準備先は `study2/runs/history-stability-01-subagent-fallback-prepared-20260915`。このexportを正本候補として固定した。実発行のclaimは0件。

## 位置づけと不変条件

主経路のResponses API再取得と、この補助経路は別の観測である。常に `route=direct_subagent` と記録する。`primary_missing_filled=false`、`mixed_route_aggregation_allowed=false`、`primary_ratings=[]` を固定し、元の研究採点枠の欠損を埋めた扱いにしない。元の主経路と混ぜて主指標・ラベル率・一致率を計算しない。

`collaboration.spawn_agent` の公開schemaには `tools=[]` やツール無効化の引数がない。`fork_turns="none"` は親の会話履歴を渡さない指定だが、system/developer instructionsの除去を保証しない。元wireのモデル・effortはspawn引数で同じ値を要求できる一方、元APIのraw SSE・応答ID・完了イベント・ツール不使用の機械的な証拠は得られない。この経路を、元の隔離環境と同等と表現しない。

受取agent ID・spawn結果原文・final原文を保存するが、これらは呼出側が渡した記録であり、提供者が署名した由来証明ではない。hashは保存後の改変を検出するもので、未知の外部発行や受取前の改変を証明できない。モデル・effortについても、保存された要求引数と提供された記録の範囲で扱う。

公式[サブエージェント文書](https://learn.chatgpt.com/docs/agent-configuration/subagents)も、子への権限・設定の継承を説明している。ただしこの環境で指定できる項目は実際の `collaboration.spawn_agent` schemaを優先して確認した。別のAPI製品にあるtools設定を、この呼出し口にもあるとは扱わない。

別経路が別の混雑容量を持つかは未確認であり、復旧を保証する予備回線ではない。また「1 agent発行」をプロバイダ内部の「1物理推論要求」とは数えられない。主経路の残55物理要求・約62分の枠へ自動で接続せず、実測時はagent発行数と観測可能な実行時間の範囲を明示する。主経路に正常応答があるものを、内容の良し悪しでこちらへ再採点させない。

## 入力の固定

元runは `study2/runs/history-stability-01-continuation1-20260915`。読み出しアンカーは元 `completion.json` のSHA-256：

```text
92cc187fa56f6d038edb508e1358af370a23c4ac110290fa95b415d2e697821b
```

exportはこのhashを引数に要求し、completionに封印されたconfiguration、後半acquisition、残件のplan・plan-seal・packet・initial-wireを照合する。後半の予定順に対して「成功prefixの直後のROUTE_FAILURE 1件＋未発行suffix」であることと、completionの残件数に一致することを検査する。ラベル・研究上の望ましさで残件を選ばない。

残25要求は先頭 `HS-B21-luna`、末尾 `HS-B31-luna`。各要求の6件・`i001`〜`i006`・説明原文・current_event・rubric・出力形式を保持する。元wireのuser本文bytesとpacket bytesが一致し、configurationの予定ID順とも完全一致することを要求する。原planに記録された決定論的parserのhashと、今回ロードするv1/v2/v3および既存snapshot parserのhashも照合する。

実際に渡せる `prompt.txt` は、元wireのdeveloper本文、改行2個、元wireのuser本文全文をそのまま連結する。パス参照や要約で代用しない。元wire全体もbytesのまま別保存する。元developer messageを新経路のユーザータスク本文へ移すため、**wire bytesが同一の再送ではない**。`source_id`対応、実験条件、過去の採点や正解は採点promptへ加えない。

元logical request ID、元initial request ID（`-a0`）、model、effort、packet/wire/prompt/plan hash、予定IDとsource ID対応を管理用planへ記録する。保持期限は元completionの `2026-10-12T17:41:23+09:00` を継承し、新しい保存先にも適用する。

## 単発の発行・受取手順

1. `export` で元run外の新規ディレクトリへ全残件を固定する。既存ディレクトリと元run配下への出力を拒否する。export自体は呼出しを行わない。
2. 将来この経路を実行する場合、主担当が一つのexportを正本として台帳へ固定し、実行範囲・要求数・時間枠・保持期限を確定する。同じ論理採点を別exportから発行し直さない。このv0.1は全workspaceにまたがる発行登録簿を持たず、独立したexportや外部ツールからの再発行を機械的には防げない。
3. 各要求のspawn前に `claim` を1回だけ実施する。前の要求のreceiptが封印されていなければ次をclaimできない。上限は1要求1試行、並列1。claimを削除・解除して再発行する機能はない。
4. 保存された `spawn-arguments.json` をそのまま使う。引数は `fork_turns="none"`、元モデル（Sol/Luna）、`reasoning_effort="medium"`、元payload全文のmessage。v0.1自体にはspawn操作を実装しない。公開schemaに存在しないtools引数は作らない。
5. 戻ったagent IDとspawnツールの原応答bytesを `register` で一度保存する。発行したか不明、agent IDを保存できなかった場合はclaimを残して停止する。
6. **最初に届いたfinal本文**をそのままbytesとして `import` する。Markdown除去・空白調整・JSON化・引用修復・再ラベル・本文の継ぎ合わせをしない。読み直して良い結果を選ぶための再採点・別agentへの再発行もしない。理由欄欠落を含め、この補助経路には再提出機能を置かない。
7. 不完全・拒否・missingもそのcompletion stateで保存する。raw finalを先に保存し、既存 `judge_transport_v3.evaluate` に渡した結果と判定を封印する。原文なしなら空bytesを保存してmissingとする。完了不明をcompletedへ読み替えない。
8. `inventory` で全予定要求・全予定IDを読む。未発行、claimのみ、agent登録済みでfinal未着、保存途中、final記録済みを区別する。受取途中の障害を別finalで上書きして救済しない。

同じexport内では、二重claim・二重agent登録・二重final受取を排他的な新規作成で拒否する。最初のfinalのラベルや形式に関係なく、この消費は維持される。発行前に同一exportを正本として固定する運用と、機械的に保証できる範囲を分けて記録する。

## 検証と欠損の読み手

元v3 validatorをそのまま使用する。全ID・出力構造が不正なら全件不受理。構造が正しく一部のquote/理由だけが不正なら、元v3と同じ項目単位の候補受理を維持する。`validator-result.json` は元parserの出力、`decision.json` は補助経路用の扱いであり、どちらも原文から再計数して照合する。元parserが診断用feedbackを返しても、それを使って再採点しない。

`auxiliary_candidate_ids` と `auxiliary_missing_ids` は全予定IDを分割する。`unscorable_ids` を別掲し、形式候補と分析可能性を混同しない。`primary_missing_ids` は補助候補が返っても全6件のまま。今回の補助範囲は25要求×6件＝150枠であり、元の取得済みバッチ内の既存quote不一致等はこの範囲へ追加しない。補助候補の意味妥当性も未審査のため `semantic_review=NOT_DONE` のままとし、研究用ratingsを解放するAPIは置かない。

読み手は次の `claim` と終了時 `inventory`。未取得・不受理・保存途中を集計側で消さない。主経路が後で復旧しても、補助finalを主経路のfinal/SSEとして取り込まず、主担当が経路を分けたまま保存する。

## オフライン確認

2026-09-15、合成fixtureの18テストが通過。正常受取のCRLFを含むraw bytes保存、全文payloadとモデル/effort、全欠損inventory、欠落/重複/余分ID、引用不一致、理由欠落、別agent、順序違反、二重claim/import/export、保存途中、missing/incomplete、入力・prompt・final改変、元のparser変更、予定IDとモデル/effortの不一致を確認した。

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_judge_subagent_fallback_v1.py' -v
```

さらに封印済み実入力を読み、一時ディレクトリへのexportとinventoryを確認した。25要求・150予定枠、Sol/Luna medium、prompt全文のサイズは12,807〜13,209 bytes、主経路欠損充足0、モデル呼出し0。一時成果物は確認後に削除した。これはローカルのexport/受取検証であり、subagentの実採点品質・隔離・無ツール実行・復旧率や本番接続を実証していない。

既存run、既存parser/runner、既存報告書は編集していない。新規3ファイルだけを今回の成果物とする。
