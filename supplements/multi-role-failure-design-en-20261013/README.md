# 多者系の故障学・設計論：英語v0.3とfigureの作成

2026-10-13。ユーザーが日本語v0.6を確認し、英語MDとfigureの作成を依頼した。PDF化は別工程の指定。

## 成果物

- [英語MD](../../papers/two-role-failure-design/manuscript-en-v0.3-2026-10-13.md)
- [英語S1](../../papers/two-role-failure-design/evidence-index-en-v0.3-2026-10-13.md)
- [PDF班向け引継ぎ](../../papers/two-role-failure-design/translation-notes-en-v0.3-2026-10-13.md)
- [図版](../../papers/two-role-failure-design/figures/README.md)
- [単独コード](../../papers/two-role-failure-design/examples/design_samples_complete_en_v0_2.py)

## 作成方針と実施

translation-plan.md (source not bundled)に範囲を記録。既存英語v0.2を再利用し、日本語v0.6の差分を本文・表・付録へ反映した。旧版と日本語確定版は保持。translate.py (source not bundled)は改訂差分と英語docstringを保存した作成コードである。

図1と描画ヘルパーは旧版から再利用。図2は案の評価、実票、集団合意、実行許可を分離する新構成へ変更し、PNG 300 dpi／SVGを作成した。日本語Mermaidの接続を保持し、英語Mermaidも添付した。描画済み二図を目視し、文字・矢印・分岐の配置を確認した。図2の外周線は本人判断を共同担当の利用へ渡す接続である。

付録Dは新しい多者設計コードの全文。説明docstringのみ英訳し、関数・データ・18テストを維持した。英語稿は合意の事実と管理側の実行許可を分け、未返答を明示保留と扱わない。三者実験のREAD終点、構成したHOLD、27入力・18対応組という単位を保持した。

## 確認

verify_translation.py (source not bundled)で日英の表と数値、コードAST、付録から抽出した独立実行と出力一致、図の辺・文字枠、参照とリンクを照合する。最終693項目すべてPASS。結果は[verification.json](verification.json)。元資料18件のhashと台帳追記のみの条件も確認する。日本語の数値・原ZIP対応は前工程の[332項目照合](../multi-role-failure-design-ja-20261013/README.md)を継承する。

図版・新規の三者記述・設計原則・付録を日英で読み合わせ、実験結果と設計例の区別、数字の単位、本人情報と実票の扱いを点検した。これは同一プロジェクト内の編集照合であり、第三者追試や追加LLM実験ではない。

`source-manifest-before.json`は保護対象、`before/`は案内と台帳の編集前コピー。最終hashは`final-manifest.json`へ記録する。新しい英訳は日本語v0.6に対応し、英語v0.2とそのPDFは従来二者版として保持。原四報・原実験・GitHub公開候補は変更しない。

初回照合は、漢数字と英語数詞、`both`・不定冠詞・数値の語順、IDのコード書式を数値差として検出し、未作成の結果ファイルへの参照も検出した。初回結果を`verification-first-pass.json`へ保持し、日英の該当セルを直接確認した。数詞の同義表現を正規化し、票一件・結果一つの英語表現を明示して再照合した。原実験の数値や日本語本文は変更していない。
