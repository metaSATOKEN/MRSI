# READOUT-SPLIT-01 固定材料と条件

実モデル未実行。前回16入力を全て保持し、新しい割付・seedで96回答を比較する。

| 入力 | 元の入力 | 主／境界 | 担当役 | 案内正解 | A紙 | Aデジタル | B紙 | Bデジタル |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RS01-M01 | RL01-M01 | MAIN | A | PAPER | ALL | NOT_ALL | ALL | ALL |
| RS01-M02 | RL01-M02 | MAIN | A | PAPER | ALL | ALL | ALL | NOT_ALL |
| RS01-M03 | RL01-M03 | MAIN | A | PAPER | ALL | NOT_ALL | ALL | NOT_ALL |
| RS01-M04 | RL01-M04 | MAIN | B | PAPER | ALL | NOT_ALL | ALL | ALL |
| RS01-M05 | RL01-M05 | MAIN | B | PAPER | ALL | ALL | ALL | NOT_ALL |
| RS01-M06 | RL01-M06 | MAIN | B | PAPER | ALL | NOT_ALL | ALL | NOT_ALL |
| RS01-M07 | RL01-M07 | MAIN | A | DIGITAL | NOT_ALL | ALL | ALL | ALL |
| RS01-M08 | RL01-M08 | MAIN | A | DIGITAL | ALL | ALL | NOT_ALL | ALL |
| RS01-M09 | RL01-M09 | MAIN | A | DIGITAL | NOT_ALL | ALL | NOT_ALL | ALL |
| RS01-M10 | RL01-M10 | MAIN | B | DIGITAL | NOT_ALL | ALL | ALL | ALL |
| RS01-M11 | RL01-M11 | MAIN | B | DIGITAL | ALL | ALL | NOT_ALL | ALL |
| RS01-M12 | RL01-M12 | MAIN | B | DIGITAL | NOT_ALL | ALL | NOT_ALL | ALL |
| RS01-B01 | RL01-B01 | ZERO | A | UNKNOWN | ALL | NOT_ALL | NOT_ALL | ALL |
| RS01-B02 | RL01-B02 | ZERO | B | UNKNOWN | ALL | NOT_ALL | NOT_ALL | ALL |
| RS01-B03 | RL01-B03 | TWO | A | UNKNOWN | ALL | ALL | ALL | ALL |
| RS01-B04 | RL01-B04 | TWO | B | UNKNOWN | ALL | ALL | ALL | ALL |

DIRECTとEXTRACTのノート本文は同一。RULEではcoverageの四値だけを渡す。モデル入力へ正解・仮説・採点を添えず、他の回答も引き継がない。

RULEは主6種類＋境界2種類＝8種類の同一入力パターンで、各4回生成する。元の入力16件や回答32件を16／32個の独立論理問題にしない。

| 四値パターン（A紙、Aデジタル、B紙、Bデジタル） | 元の入力数 | RULE回答数 |
| --- | ---: | ---: |
| ALL、ALL、ALL、ALL | 2 | 4 |
| ALL、ALL、ALL、NOT_ALL | 2 | 4 |
| ALL、ALL、NOT_ALL、ALL | 2 | 4 |
| ALL、NOT_ALL、ALL、ALL | 2 | 4 |
| ALL、NOT_ALL、ALL、NOT_ALL | 2 | 4 |
| ALL、NOT_ALL、NOT_ALL、ALL | 2 | 4 |
| NOT_ALL、ALL、ALL、ALL | 2 | 4 |
| NOT_ALL、ALL、NOT_ALL、ALL | 2 | 4 |

- [設計書](../docs/readout-split-01-plan-v0.1-2026-09-25.md)
- [設計・正解・割付](design.json)
- [実メッセージ96件](requests.json)
- [DIRECT指示](prompt-direct.txt)／[EXTRACT指示](prompt-extract.txt)／[RULE指示](prompt-rule.txt)
- [オフライン点検](verification.json)
- 合成回答の採点記録 (see the evidence index)

実行用Colabセルは次工程で作成する。ここにあるPython写しは設計証拠で、現行の構築元はscripts/readout_split_01_design.py。
