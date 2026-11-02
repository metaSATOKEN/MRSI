# §4.4の入力記述の訂正 / Correction to the Section 4.4 Input Description

2026-09-30。著者が共有した指摘を、元ZIPの実入力、第三報の抽出JSON、元診断と照合し、採用した。

対象は`ST02-EARLY-N05-LOWER-CONFIRM`。元ZIPの`responses/ST02-EARLY-N05-LOWER-CONFIRM/input.json`に保存されたモデル向けメッセージでは、`experiences`がAの3経験・Bの2経験を含む一方、`own_judgment`は著者・対象ともBの一件だけである。その本人判断はDIGITALで、本人集計もB、共同候補は45と37だった。Aが著者の別記録は`initial_proposal`で、Aの本人ノートではない。

実行管理の親参照にはA/B双方の形成記録があるが、それを両方の本人ノートがモデル入力へ含まれることと同一視しない。今回、実際の`messages`内の資料JSONを直接点検した。

**日本語訂正後：** 役Bの入力には、両役の経験資料、役B自身の正しい本人ノート、本人集計、45と37の共同候補表が揃っていた。

**Corrected English:** The input contained experience records for both roles, role B's own correct judgment note, B's own-experience summary, and the joint candidate table showing 45 and 37.

旧版の「両役の正しい本人ノート / both roles' correct own notes」は供給範囲を広く書きすぎていた。日本語v0.2からv0.4、英語v0.1に継承され、過去の編集照合でも見落としていた記述を訂正する。旧稿と既存監査は履歴として保持し、台帳§356から§352〜355を参照して訂正を記録する。

This is a source-description correction. The observed acceptance of the total-37 proposal, scoring, quantitative results, figures, and code are unchanged. Earlier manuscripts and verification records are retained as history rather than silently overwritten.

- [訂正版・日本語v0.5](manuscript-ja-v0.5-2026-09-30.md)
- [Corrected English v0.2](manuscript-en-v0.2-2026-09-30.md)
- [証拠照合 / Source check](../../supplements/two-role-failure-design-input-correction-20260930/README.md)
- [第三報の抽出JSON](../paper-03/evidence-extract-v0.1-2026-09-29.json)
