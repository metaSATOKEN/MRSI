# 第四報・証拠対応索引

2026-10-13｜v0.1｜[日本語校了版](MRSI_Paper4-ja-v1.0.md)

本索引は本文の表・具体例から原記録へ降りる入口である。課題、材料、採点、反復単位は本文と付録へ収めた。原ZIPと固定設計・実行コードはそのまま保持しており、この稿のためにモデルを呼び出したり正式成績を変更したりしていない。

## 1. 知見と証拠

| 本文の位置 | 確認内容 | 一次記録・集計への入口 |
|---|---|---|
| 表6、図2、§5.1 | 高合計案への誤HOLDと、その後の正しい未合意 | [TB01報告](../../experiments/TB01/docs/three-role-boundary-01-result-2026-10-13.md)、[再集計](../../experiments/TB01/expected-result.json) |
| §5.1の反復 | 同じ18入力の三回、誤保留・誤承認 | [TVR01報告](../../experiments/TVR01/docs/three-role-vote-repeat-01-result-2026-10-13.md)、[再集計](../../experiments/TVR01/expected-result.json) |
| 表7–8、§5.2 | 未返答／HOLD／ACCEPT、六軸と対応組 | [TAR01報告](../../experiments/TAR01/docs/three-role-approval-readout-01-result-2026-10-13.md)、[再集計](../../experiments/TAR01/expected-result.json)、[取得後の補足](../../experiments/TAR01/analysis/supplementary-analysis.json) |
| 表9–10、§5.3 | 比較欄の有無・54対応対 | [TCV01報告](../../experiments/TCV01/docs/three-role-comparison-vote-01-result-2026-10-13.md)、[再集計](../../experiments/TCV01/expected-result.json) |
| 表9–10、§5.3 | 新数値材料・同じ二条件 | [TCV02報告](../../experiments/TCV02/docs/three-role-comparison-vote-02-result-2026-10-13.md)、[再集計](../../experiments/TCV02/expected-result.json) |
| 付録A–C | 回答数、全六材料、生成設定 | [本文用データ](paper-data-v0.1-2026-10-13.json)の各試験summary・case_inputs・model |

本文用データは既存再集計の抽出と、原ZIPのresponse.jsonからの費用計数を含む。原結果のSHA-256は`sources`に収録。459は完走回答の目録総数であり、独立標本数や一つの成功率の分母にはしない。

## 2. 原ZIPと取得前固定

| 試験 | 原ZIP | 取得前カード | ローカル集計コード |
|---|---|---|---|
| TB01 | [完走原ZIP](../../experiments/TB01/archives/npp-tb01-result-20261013-041945-c6e2c94d.zip) | [カード](../../experiments/TB01/docs/three-role-boundary-01-v0.1-2026-10-13.md) | [集計器](../../reference-code/aggregate_three_role_boundary_01.py) |
| TVR01 | [原ZIP](../../experiments/TVR01/archives/npp-tvr01-result-20261013-045940-cf404568.zip) | [カード](../../experiments/TVR01/docs/three-role-vote-repeat-01-v0.1-2026-10-13.md) | [集計器](../../reference-code/aggregate_three_role_vote_repeat_01.py) |
| TCV01 | [原ZIP](../../experiments/TCV01/archives/npp-tcv01-result-20261013-053413-76c1649c.zip) | [カード](../../experiments/TCV01/docs/three-role-comparison-vote-01-v0.1-2026-10-13.md) | [集計器](../../reference-code/aggregate_three_role_comparison_vote_01.py) |
| TCV02 | [原ZIP](../../experiments/TCV02/archives/npp-tcv02-result-20261013-061923-878369ad.zip) | [カード](../../experiments/TCV02/docs/three-role-comparison-vote-02-v0.1-2026-10-13.md) | [集計器](../../reference-code/aggregate_three_role_comparison_vote_02.py) |
| TAR01 | [原ZIP](../../experiments/TAR01/archives/npp-tar01-result-20261013-071229-08c825b9.zip) | [カード](../../experiments/TAR01/docs/three-role-approval-readout-01-v0.1-2026-10-13.md) | [集計器](../../reference-code/aggregate_three_role_approval_readout_01.py) |

TB01の初回準備失敗も[別ZIP](../../experiments/TB01/preparation-attempt/archives/npp-tb01-result-20261013-035934-aaa05b73.zip)として保存。生成0のため完走126回答には含めない。

各ZIPの`frozen/`に取得前の設計、`code/`に配布コード、`responses/`に実入力・原回答・保存物がある。検算時は信頼済みのローカル集計器と配布時payloadを用い、返送ZIPのコードは実行しない。

## 3. 具体例の照合

[証拠抜粋](evidence-extract-v0.1-2026-10-13.json)は取得後の説明用選択である。

- **TB01：** T02の高合計案・第1反復の全9投票／読出しと、第2反復のCの投票・三票時点の読出し、計11件。原経験、合計90/84、C本人DIGITAL、HOLDの実票、後続三人のPENDINGを確認できる。
- **TAR01：** N01をAが読む三状態×二反復の全6件。第1反復のMISSINGとHOLDが同じJSON値であること、第2反復のMISSINGが正しいこと、ACCEPT時に本人DIGITALと共同PAPERが併存することを確認できる。

各項目は元のinput.json全体、そこから解釈したuser payload、原answer.txt、JSON値、正式採点を持ち、ZIPとメンバーの相対位置を記す。原回答の文字列そのものは変更していない。本文のJSON例だけは表示用に空白を整えた。

表9の二入力の両方式・全三反復は、既存の[TCV01抜粋](../../experiments/TCV01/analysis/evidence-extract.json)で追える。TAR01の[反復照合](../../experiments/TAR01/analysis/repeat-comparison.json)には全27入力の比較がある。

## 4. 指標名の読み違いを防ぐ対応

| 保存済みキー | 含むもの | 草稿での値・呼称 |
|---|---|---|
| `metrics.approval_state` | 一回答のA/B/C全員の状態 | 53/54回答 |
| `triplet_totals` | 三状態それぞれの六軸 | 17/18対応組 |
| `paired_metrics.agreement_execution_all_states` | 承認状態＋合意＋実行の三軸 | 17/18。合意・実行だけとは書かない |
| 補足`agreement_and_execution_only_triplets` | 合意＋実行の二軸だけ | 18/18。取得後の補足集計 |

正式のキーや成績は変更しない。HOLD票を構成した18回答と、実票の部分／全提示36回答も区別する。

## 5. 再計算

26件の収録資料から本文用データと事例抜粋を再生成する。[再計算コード](../../tools/rebuild_paper04_data.py)・[実行手順](../../RUNNING.md)
