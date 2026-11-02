# 多者系の故障学・設計論：日本語v0.6の編集照合

2026-10-13。ユーザーが改訂方針を承認し、日本語稿の改訂を依頼した。既存二者稿を基に、第四報の三者の観測を統合した。新しいモデル実験や正式採点の変更は行っていない。

## 成果物

- [日本語v0.6](../../papers/two-role-failure-design/manuscript-ja-v0.6-2026-10-13.md)
- [証拠索引](../../papers/two-role-failure-design/evidence-index-v0.6-2026-10-13.md)
- [改訂記録](../../papers/two-role-failure-design/revision-notes-v0.6-2026-10-13.md)
- [単独実行コード](../../papers/two-role-failure-design/examples/design_samples_complete_v0_2.py)
- [図ソースの案内](../../papers/two-role-failure-design/figures/README.md)

六つの観測と七原則で構成し、二者の誤承認と三者の誤保留を同じ論点へ配置した。新しい観測節は、TAR01における未返答から明示保留への取り違えである。案の評価、実票、集団合意、実行許可を別々に記録する設計例を示す。TAR01の観測終点はREAD回答であり、その回答の保存・再投入を測ったとは記さない。

## 照合内容

最終照合は332項目すべてPASS。確認結果は[verification.json](verification.json)を正本とする。照合コードはverify_revision.py (source not bundled)、本文の変更差分はmanuscript.diff (source not bundled)に保存する。

- 保護対象22ファイルのhashを編集前manifestと比較。旧日本語・英語・PDF、元論文資料、旧コードと原結果を保持した。
- 第四報の原資料26件のhashを照合。TB01・TAR01の17抜粋について、原ZIPの入力と回答を再読し一致を確認。経験資料から候補合計を分数で再計算し、本文の事例と対応させた。
- TB01、TAR01、TCV01、TCV02の集計と新表4を照合。TAR01の固定キーが三軸を含む点を保持し、合意・実行のみの正しさと承認状態の正しさを区別した。
- 既存§4.1–4.3の本文、旧§4.5から移した§4.6の本文を保持。旧観測選択関数をASTで照合した。
- 付録Dと単独コードの全文一致、本文の三つの抜粋と関数の一致を確認。付録から抽出したコードだけを一時ディレクトリで実行し、18テストと例示結果を点検した。
- 日本語図二点は本文内Mermaidと添付ソースの一致を確認。図1は従来構成を保持し、図2を更新した。既存英語PNG/SVGの再描画は今回の対象外。
- 参照リンク、Markdown表、コードブロック、台帳の追記のみという条件を確認した。

これは同一プロジェクト内の編集照合と合成コードテストであり、追加のLLM成績や第三者再現には数えない。

## 記録と再実行

初回の機械照合は、作成途中だった本READMEへの二リンクだけを未成立とした。その結果はverification-before-close.json (source not bundled)に保持する。本READMEと台帳を整えた後の結果は`verification.json`に記録する。

研究ルートから次を実行すると、原資料を照合し、付録コードを抽出してテストする。GPU・モデル・ネットワークは使用しない。

```sh
python3 throughline/audits/multi-role-failure-design-ja-20261013/verify_revision.py
```

revision-plan.md (source not bundled)は作業範囲、source-manifest-before.json (source not bundled)は保護対象の編集前hash、`before/`は更新した案内・台帳の編集前コピーである。revise.py (source not bundled)は旧日本語稿と最新版コードから改訂稿を生成する。最終成果物のhashは`final-manifest.json`に記録する。

旧日本語v0.5、従来二者版の英語v0.2・PDF、第一〜第四報、原実験、GitHub公開候補を保持した。フォルダ名は既存リンクのため`two-role-failure-design`を継続する。英訳、組版用figureの更新、PDF化は後続工程とする。
