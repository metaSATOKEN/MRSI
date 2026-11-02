# READOUT-LOAD-01 固定入力・割付

設計用の材料と合成検証。実モデル回答は未取得。FULLの指示はXM01のPROBEと同一、入力本文は三条件で同一。

| 入力 | 集合 | 元材料 | 担当役 | 犬猫 | 共同案内の正解 | 不採用媒体の制約者／境界 |
| --- | --- | --- | --- | --- | --- | --- |
| RL01-M01 | MAIN | E1-G59 | A | DOG | PAPER | A |
| RL01-M02 | MAIN | E1-G28 | A | DOG | PAPER | B |
| RL01-M03 | MAIN | E1-G41 | A | CAT | PAPER | AB |
| RL01-M04 | MAIN | E1-G07 | B | CAT | PAPER | A |
| RL01-M05 | MAIN | E1-G35 | B | CAT | PAPER | B |
| RL01-M06 | MAIN | E1-G18 | B | DOG | PAPER | AB |
| RL01-M07 | MAIN | E1-G05 | A | DOG | DIGITAL | A |
| RL01-M08 | MAIN | E1-G62 | A | CAT | DIGITAL | B |
| RL01-M09 | MAIN | E1-G21 | A | CAT | DIGITAL | AB |
| RL01-M10 | MAIN | E1-G24 | B | CAT | DIGITAL | A |
| RL01-M11 | MAIN | E1-G56 | B | DOG | DIGITAL | B |
| RL01-M12 | MAIN | E1-G55 | B | DOG | DIGITAL | AB |
| RL01-B01 | BOUNDARY | E1-G40 | A | DOG | UNKNOWN | ZERO |
| RL01-B02 | BOUNDARY | E1-G20 | B | CAT | UNKNOWN | ZERO |
| RL01-B03 | BOUNDARY | E1-G53 | A | CAT | UNKNOWN | TWO |
| RL01-B04 | BOUNDARY | E1-G10 | B | DOG | UNKNOWN | TWO |

主12材料は紙／デジタル各6、A/B各6、DOG/CAT各6。不採用媒体の制約者はAのみ／Bのみ／両方各4。主集合の犬猫は各媒体・役内3対3、各観測パターン内2対2。役×媒体の各3材料にも犬猫双方を含める。境界は犬猫2対2で、主指標へ混ぜない。

全16入力×3条件×2反復＝96予定回答。主比較72、補助境界24。同じ入力・反復内の三条件には共通seed、反復間は別seed。主集合の条件位置は各反復で厳密均衡。

入力ノートは固定材料の最新観測から構成した制御入力であり、モデルが生成した記憶ではない。モデルにはrequests.jsonの各messagesだけを渡し、design.jsonのgold・条件名・仮説・採点結果は渡さない。

- [設計書](../docs/readout-load-01-plan-v0.1-2026-09-25.md)
- [設計・正解・割付](design.json)
- [送信メッセージ](requests.json)
- [FULL指示](prompt-full.txt)／[DUAL指示](prompt-dual.txt)／[CHANNEL指示](prompt-channel.txt)
- [オフライン検証](verification.json)
- 合成回答の採点結果 (see the evidence index)

Colabの実行器は未実装。現時点のコードは設計構成・採点・合成fixture用の標準ライブラリのみ。
