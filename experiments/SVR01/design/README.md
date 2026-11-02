# SAVED-READOUT-01 固定資料

2026-09-25。実保存26入力、DIRECT／EXTRACTの各2反復＝104回答。モデル実行前の固定資料。

原入力と親saved-memoryの対応・hashを照合。両方式の案内根拠はGROUPのみ。主16材料はRS01既使用16材料と診断10材料から独立。診断は既知の古い全10保存物を採用。

| ID | 集合 | 元PROBE ID | 役 | GROUP案内 | 最新案内 | 古い観測者 |
| --- | --- | --- | --- | --- | --- | --- |
| SVR01-M01 | MAIN | XM01-R1-E1-G54-REWRITE-PROBE-A | A | PAPER | PAPER | なし |
| SVR01-M02 | MAIN | XM01-R3-E1-G12-REWRITE-PROBE-A | A | PAPER | PAPER | なし |
| SVR01-M03 | MAIN | XM01-R1-E1-G43-REWRITE-PROBE-A | A | DIGITAL | DIGITAL | なし |
| SVR01-M04 | MAIN | XM01-R1-E1-G57-REWRITE-PROBE-A | A | DIGITAL | DIGITAL | なし |
| SVR01-M05 | MAIN | XM01-R2-E1-G01-REWRITE-PROBE-B | B | PAPER | PAPER | なし |
| SVR01-M06 | MAIN | XM01-R2-E1-G49-REWRITE-PROBE-B | B | PAPER | PAPER | なし |
| SVR01-M07 | MAIN | XM01-R1-E1-G37-REWRITE-PROBE-B | B | DIGITAL | DIGITAL | なし |
| SVR01-M08 | MAIN | XM01-R3-E1-G33-REWRITE-PROBE-B | B | DIGITAL | DIGITAL | なし |
| SVR01-M09 | MAIN | XM01-R3-E1-G39-SELECT-PROBE-A | A | PAPER | PAPER | なし |
| SVR01-M10 | MAIN | XM01-R3-E1-G38-SELECT-PROBE-A | A | PAPER | PAPER | なし |
| SVR01-M11 | MAIN | XM01-R2-E1-G50-SELECT-PROBE-A | A | DIGITAL | DIGITAL | なし |
| SVR01-M12 | MAIN | XM01-R1-E1-G26-SELECT-PROBE-A | A | DIGITAL | DIGITAL | なし |
| SVR01-M13 | MAIN | XM01-R1-E1-G17-SELECT-PROBE-B | B | PAPER | PAPER | なし |
| SVR01-M14 | MAIN | XM01-R1-E1-G27-SELECT-PROBE-B | B | PAPER | PAPER | なし |
| SVR01-M15 | MAIN | XM01-R2-E1-G23-SELECT-PROBE-B | B | DIGITAL | DIGITAL | なし |
| SVR01-M16 | MAIN | XM01-R3-E1-G08-SELECT-PROBE-B | B | DIGITAL | DIGITAL | なし |
| SVR01-S01 | STALE | XM01-R2-E1-G48-REWRITE-PROBE-B | B | DIGITAL | PAPER | A |
| SVR01-S02 | STALE | XM01-R3-E1-G31-SELECT-PROBE-B | B | UNKNOWN | DIGITAL | B |
| SVR01-S03 | STALE | XM01-R1-E1-G55-SELECT-PROBE-B | B | UNKNOWN | DIGITAL | A |
| SVR01-S04 | STALE | XM01-R3-E1-G11-SELECT-PROBE-B | B | DIGITAL | DIGITAL | A |
| SVR01-S05 | STALE | XM01-R3-E1-G58-SELECT-PROBE-B | B | DIGITAL | PAPER | A |
| SVR01-S06 | STALE | XM01-R2-E1-G30-SELECT-PROBE-B | B | UNKNOWN | PAPER | A |
| SVR01-S07 | STALE | XM01-R3-E1-G02-SELECT-PROBE-B | B | UNKNOWN | DIGITAL | A |
| SVR01-S08 | STALE | XM01-R1-E1-G62-REWRITE-PROBE-A | A | UNKNOWN | DIGITAL | B |
| SVR01-S09 | STALE | XM01-R1-E1-G60-SELECT-PROBE-B | B | UNKNOWN | PAPER | A |
| SVR01-S10 | STALE | XM01-R2-E1-G40-SELECT-PROBE-B | B | PAPER | PAPER | A |

GROUP四値を完全に読んだ場合、診断20回答のGROUP一致は20、最新一致は4となる。これは取得前に計算できる期待値であり実測ではない。G31/Bの個別欄のみ最新という競合も原入力のまま保持する。

- [設計書](../docs/saved-readout-01-plan-v0.1-2026-09-25.md)
- [全240件の選定母集団・26入力・親hash・割付・二基準](design.json)
- [実際にモデルへ渡す104入力](requests.json)
- [DIRECT指示](prompt-direct.txt)／[EXTRACT指示](prompt-extract.txt)
- [固定した設計・採点コード](saved_readout_01_design.py)／[継承した採点部品](readout_split_01_scoring.py)
- [点検・hash](verification.json)

採点部品を含めて本番1セルへ組み込む作業は次の接続準備で行う。ここにColab実行用セルは含まれない。
