# UPDATE-READOUT-01 固定資料

18実保存入力、REWRITE/SELECT×2反復、UPDATE72＋条件付きREAD72＝最大144回答。新規生成0。

元の保存物を保持したまま通知を一件追加。REPAIRは最新通知の再配送、GUARDは低revision通知の遅配。両条件の更新入力は同一。READは生成した実保存物から構成するため、72件の完成したREAD本文は事前には存在しない。

| ID | 集合 | 元材料／保持役 | 元保存方式 | 通知 | 通知の版→期待最新の版 | 通知の候補位置 | 最新案内 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| UR01-R01 | REPAIR | E1-G60/B | SELECT | A (PARTNER) | 3→3 | C1 | PAPER |
| UR01-R02 | REPAIR | E1-G31/B | SELECT | B (SELF) | 2→2 | C2 | DIGITAL |
| UR01-R03 | REPAIR | E1-G62/A | REWRITE | B (PARTNER) | 2→2 | C3 | DIGITAL |
| UR01-R04 | REPAIR | E1-G02/B | SELECT | A (PARTNER) | 4→4 | C4 | DIGITAL |
| UR01-R05 | REPAIR | E1-G58/B | SELECT | A (PARTNER) | 3→3 | C1 | PAPER |
| UR01-R06 | REPAIR | E1-G11/B | SELECT | A (PARTNER) | 2→2 | C2 | DIGITAL |
| UR01-R07 | REPAIR | E1-G30/B | SELECT | A (PARTNER) | 2→2 | C3 | PAPER |
| UR01-R08 | REPAIR | E1-G48/B | REWRITE | A (PARTNER) | 3→3 | C4 | PAPER |
| UR01-R09 | REPAIR | E1-G55/B | SELECT | A (PARTNER) | 4→4 | C1 | DIGITAL |
| UR01-R10 | REPAIR | E1-G40/B | SELECT | A (PARTNER) | 4→4 | C2 | PAPER |
| UR01-G01 | GUARD | E1-G12/A | REWRITE | A (SELF) | 1→2 | C1 | PAPER |
| UR01-G02 | GUARD | E1-G43/A | REWRITE | B (PARTNER) | 2→4 | C2 | DIGITAL |
| UR01-G03 | GUARD | E1-G01/B | REWRITE | A (PARTNER) | 3→4 | C3 | PAPER |
| UR01-G04 | GUARD | E1-G33/B | REWRITE | B (SELF) | 1→4 | C4 | DIGITAL |
| UR01-G05 | GUARD | E1-G39/A | SELECT | A (SELF) | 1→3 | C1 | PAPER |
| UR01-G06 | GUARD | E1-G26/A | SELECT | B (PARTNER) | 1→2 | C2 | DIGITAL |
| UR01-G07 | GUARD | E1-G27/B | SELECT | A (PARTNER) | 1→2 | C3 | PAPER |
| UR01-G08 | GUARD | E1-G08/B | SELECT | B (SELF) | 2→3 | C4 | DIGITAL |

REPAIR 10件の保持役A1/B9、通知SELF1/PARTNER9。GUARDは元保存方式・保持役・最新媒体の8層各一件でSELF4/PARTNER4。REPAIRの元10件は全件採用し、SVR01の新回答・成否で材料を選んでいない。

同版・同人物の候補は全欄同じ。位置IDの正解は一つに限定せず、選択後の内容で採点する。通知位置はREPAIR各位置3/3/2/2、GUARD各2。原資料54ファイルの参照hashは各caseに保存。

- [設計書](../docs/update-readout-01-plan-v0.1-2026-09-25.md)
- [固定資料・割付](design.json)
- [初回72メッセージ](update-requests.json)
- [実保存物からのREAD構築・保存・採点のコード](update_readout_01_design.py)
- [hashと検証](verification.json)

実モデル設定はSVR01と同一。最大144生成・準備込み90分・追加再生成0。全文1セル、Driveなし、結果ZIPで回収する本番コードは次の接続準備で作る。
