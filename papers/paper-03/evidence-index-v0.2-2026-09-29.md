# 補足資料S1：第三報の証拠対応表

2026-09-29｜日本語草稿v0.2対応｜内部資料・非公開・削除期限なし

本文の主張から、固定計画、実回答、集計、照合へ進むための索引。相対リンクは現在の研究フォルダ内を指す。公開パッケージや永続識別子はまだ設けていない。

## 1. 主張と証拠

| 本文 | 根拠 | 直接確認できること |
|---|---|---|
| §3・表3 | [ST02固定計画](../../experiments/ST02/docs/summary-timing-02-plan-v0.1-2026-09-29.md) §3、[主表・事例の抽出JSON](evidence-extract-v0.1-2026-09-29.json) | N05の本人値17/27・18/20、共同45/37 |
| §4・図1・表4/5 | [ST01計画](../../experiments/ST01/docs/summary-timing-01-plan-v0.1-2026-09-29.md)、[ST02計画](../../experiments/ST02/docs/summary-timing-02-plan-v0.1-2026-09-29.md)、[JR01計画](../../experiments/JR01/docs/judgment-repeat-01-plan-v0.1-2026-09-29.md) | 入力差、形成の共用、工程の接続/非接続、採点単位、終了規則 |
| §4.1・図2 | [固定80入力](../../experiments/JR01/design/source-inputs.json)、[旧本人ノート](../../experiments/JR01/design/source-parent-evidence.json)、[240生成の予定](../../experiments/JR01/design/requests.json) | 両条件合計の本人形成32入力×3、共同確認48入力×3。本人形成から確認への新規接続なし |
| §5.1・表6 | [ST01再集計](../../experiments/ST01/expected-result.json)、[ST02再集計](../../experiments/ST02/expected-result.json) | `report.by_condition`のI/J/K/G/誤合意、各工程の回答 |
| §5.1・表7 | [JR01再集計](../../experiments/JR01/expected-result.json) | `report.by_repeat`の本人形成、`fixed_input_stability`の三反復分類 |
| §5.2・表8・JSON抜粋 | [ST02診断](../../supplements/summary-timing-02-20260929/diagnostics.json)、[ST02原文点検](../../supplements/summary-timing-02-20260929/reason-review.md) | EARLY N05 LOWERの入力、誤承認、直後の二役利用 |
| §5.3・表9/10 | [JR01全回答診断](../../supplements/judgment-repeat-01-20260929/diagnostics.json)、[JR01原文点検](../../supplements/judgment-repeat-01-20260929/reason-review.md) | N05 LOWER/DUPLICATE、N02 OPTIMALの全三回答と固定入力 |
| 付録B・表B1 | ST01/ST02再集計の`progression`、診断の`stage_components` | 人工診断、工学的進行目安、総合未達の内訳 |

抽出JSONは、主3試験の既存再集計・診断から作成した参照用コピーである。`tables`に主要集計、`examples`に該当回答・入力、`source_sha256`に元9ファイルのhashを持つ。再採点や新しい推定を行っていない。[抽出スクリプト](../../supplements/paper-03-draft-20260929/extract_evidence.py)も保存した。

## 2. 主実験の一次記録と固定設計

### 既知材料での供給時期比較：ST01

- [結果報告](../../experiments/ST01/docs/summary-timing-01-result-2026-09-29.md)／[固定計画](../../experiments/ST01/docs/summary-timing-01-plan-v0.1-2026-09-29.md)／[取得前カード](../../supplements/prereg/summary-timing-01-v0.1.md)。
- 結果MANIFEST (see the evidence index)／[再集計](../../experiments/ST01/expected-result.json)／[診断](../../supplements/summary-timing-01-20260929/diagnostics.json)。原ZIPの同一コピーは結果フォルダに保管。
- [別実装の照合コード](../../supplements/summary-timing-01-results-20260929/independent_check.py)／[照合結果](../../supplements/summary-timing-01-results-20260929/independent-check.json)。
- [原文点検](../../supplements/summary-timing-01-20260929/reason-review.md)／[点検完了記録](../../supplements/summary-timing-01-20260929/reason-review.json)。

### 未使用数値材料での供給時期比較：ST02

- [結果報告](../../experiments/ST02/docs/summary-timing-02-result-2026-09-29.md)／[固定計画](../../experiments/ST02/docs/summary-timing-02-plan-v0.1-2026-09-29.md)／[取得前カード](../../supplements/prereg/summary-timing-02-v0.1.md)。
- [原ZIP](../../experiments/ST02/archives/npp-st02-result-20260929-073815-2a1541bf.zip)／MANIFEST (see the evidence index)。原ZIP SHA256：`7086be6367b5e83f3ccefdb07ac95b36aad31623c95a08b9e52980dc4cd8a7a1`。
- [別実装の照合コード](../../supplements/summary-timing-02-results-20260929/independent_check.py)／[照合結果](../../supplements/summary-timing-02-results-20260929/independent-check.json)。
- [材料の未使用照合対象](../../supplements/summary-timing-02-design-20260929/prior-material-inventory.json)。N01〜N08は区分IDで、ST01の同名材料とは経験値・経験IDが異なる。

表8と抜粋は`ST02-EARLY-N05-LOWER-CONFIRM`、`ST02-EARLY-N05-LOWER-USE-A`、`ST02-EARLY-N05-LOWER-USE-B`に対応する。共同の開始記録IDは`Q4A67A15B6A`、確認記録IDは`Q906DCEFF8B`。再集計`by_slot`には保存回答と採点があり、原ZIPには描画済み入力・原回答が含まれる。JSON抜粋で省いた参照欄は完全回答へ残した。

§6.2の再確認省略は、同じ再集計の`ST02-EARLY-N05-LOWER-RECHECK`にある発動条件`reply.action == COUNTER`と状態`SKIPPED_BY_PROTOCOL`に対応する。これは欠測ではなく規則上の非適用である。[実行コード](../../reference-code/summary_timing_01_runtime.py)と[ST02採点コード](../../reference-code/summary_timing_02_scoring.py)にも同じ分岐がある。

### 固定入力三反復：JR01

- [結果報告](../../experiments/JR01/docs/judgment-repeat-01-result-2026-09-29.md)／[固定計画](../../experiments/JR01/docs/judgment-repeat-01-plan-v0.1-2026-09-29.md)／[取得前カード](../../supplements/prereg/judgment-repeat-01-v0.1.md)。
- [原ZIP](../../experiments/JR01/archives/npp-jr01-result-20260929-092936-6e2d67ef.zip)／MANIFEST (see the evidence index)。原ZIP SHA256：`520e0cd052adcd6c6da8927674db38341611963f76591362a7df90cbeb1cddb3`。
- [固定80入力](../../experiments/JR01/design/source-inputs.json)／[旧親記録](../../experiments/JR01/design/source-parent-evidence.json)／[240生成の予定](../../experiments/JR01/design/requests.json)。
- [別実装の照合コード](../../supplements/judgment-repeat-01-results-20260929/independent_check.py)／[照合結果](../../supplements/judgment-repeat-01-results-20260929/independent-check.json)。

該当回答IDは`JR01-R{1,2,3}-{EARLY,LATE}-N05-{LOWER,DUPLICATE}-CONFIRM`および`JR01-R{1,2,3}-{EARLY,LATE}-N02-OPTIMAL-CONFIRM`。診断JSONの`all_responses`には全240回答の原文、実payload、期待値、成分採点を収録している。本人形成の三反復は共同確認へ渡していない。旧ST02回答を新三回の分母へ加えていない。

## 3. 前段の探索の全入口

| 試験 | 固定結果 | 補足上の注意 |
|---|---|---|
| ES01 | [本人経験と共同記録](../../experiments/ES01/docs/experience-shared-01-result-2026-09-28.md) | 共同割付反転は診断用コピー。新しい再合意過程ではない |
| AC01 | [同点案の合意](../../experiments/AC01/docs/agreement-confirm-01-result-2026-09-28.md) | 本稿の主実験と往復・入力の契約を混同しない |
| EU01 | [経験更新](../../experiments/EU01/docs/experience-update-01-result-2026-09-28.md) | 本人更新と共同配分を別評価 |
| FC01 | [候補選択](../../experiments/FC01/docs/feasible-choice-01-result-2026-09-28.md) | 局所的な方式差 |
| FC02 | [新経験での候補選択](../../experiments/FC02/docs/feasible-choice-02-result-2026-09-28.md) | FC01の成績を新材料の対照に転用しない |
| CT01 | [共同候補の合計](../../experiments/CT01/docs/candidate-totals-01-result-2026-09-28.md) | 最適選択と本人欄・相手確認は別の点数 |
| OS01 | [本人用集計](../../experiments/OS01/docs/own-summary-01-result-2026-09-28.md)／[事後の境界監査](../../docs/study2/own-summary-01-boundary-audit-2026-09-28.md) | 正式56未確定と正規化参考評価を分離 |
| BJ01 | [境界judge](../../experiments/BJ01/docs/boundary-judge-01-result-2026-09-28.md) | judge較正の成績を研究本体の正答率へ合算しない |
| CS01 | [相手確認への支援](../../experiments/CS01/docs/confirm-support-01-result-2026-09-29.md) | 適切提案の主比較と誤提案の対照を分離 |
| CR01 | [対案の再確認](../../experiments/CR01/docs/counter-recheck-01-result-2026-09-29.md) | 最後の正答と途中の本人形成を区別 |

各結果報告から、その試験の固定計画、原ZIP、再集計、採点コード・照合へ進める。第一報・第二報の校了稿は変更していない。

## 4. 草稿作成と改訂で実施したこと

今回の日本語草稿は、正式結果の再配置・要約と一次文献調査である。新規モデル生成、追加N、採点規則変更、旧版結果の置換、公開は0。執筆開始前の主要資料hashと、編集後のリンク・表・旧資料不変の点検は[執筆監査](../../supplements/paper-03-draft-20260929/README.md)へ保存する。

v0.2は、共有された読後評を固定設計・再集計・実行分岐と照合し、中心命題の反復範囲、表6の採点注、図2、再確認の発動条件を明確にした。全表・JSON抜粋・参考文献と元資料は維持する。採否は[改訂メモ](revision-notes-v0.2-2026-09-29.md)、照合は[改訂監査](../../supplements/paper-03-revision-v02-20260929/README.md)を参照。読後評を第三者による原ZIP再採点とは扱わない。
