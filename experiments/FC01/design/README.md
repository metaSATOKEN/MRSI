# FC01 設計材料

[設計書](../docs/feasible-choice-01-plan-v0.1-2026-09-28.md)と取得前カード (see the evidence index)に対応する、実行前の材料表。全文指示・schema・実行器はまだ含まない。モデル生成0。

`materials-proposal.json` はEU01の全32出発資料、同一候補表によるDIRECT/SELECTの64経路、256予定IDと依存・seed、採点専用の算術を含む。**ファイル全体をモデルへ送らない。** `expected_not_for_model`、方式・条件名、旧成績、割付表は監査用。

提案へ送る資料は `holder / experiences / previous_private_judgments / previous_joint_records / candidates` のみ。前四項目はEU01の実PROPOSE入力から取得し、後一項目を両方式へ同じ形で加える。確認と利用には候補表を追加しない。

| 数える対象 | 数 |
|---|---:|
| 元出発点 | 16（8配置×元2履歴） |
| 経験条件を含む共通資料 | 32（本人推奨一致16、不一致16） |
| 方式別経路 | 64 |
| 初回／後続入力 | 64／192 |
| 最大生成 | 256 |
| 正解候補ID×表示位置 | 四通り各8 |

候補選択の正解はコードで供給しない。候補名の対応と表示順を決定論的に割り付けるだけで、合計点と正解IDは採点資料に隔離する。元ZIPへの参照は各共通資料の `source_input`、元資料との対応は `sources` にある。

再点検（標準Pythonのみ、ネット接続とモデルロードなし）：

```sh
python3 throughline/audits/feasible-choice-01-design-20260928/check_materials.py
```

これは提案材料を同じ内容で再生成する設計点検である。実行ランタイムや正式採点器ではない。元資料は読み取り専用。点検結果 (see the evidence index)は2,318 PASS、順序の内訳 (see the evidence index)も保存。

材料SHA256：`378accd0cbbc5f9377e4098bc6495a6296a2e38be0ac55e42b3803e6b9c62540`。
