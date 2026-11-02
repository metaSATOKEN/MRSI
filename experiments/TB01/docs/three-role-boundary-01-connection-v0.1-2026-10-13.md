> 公開版の実行案内（2026-10-29）：現在は可読ファイルと明示実行のランチャーを使います。[現行手順](../../../docs/READABLE_GENERATION.md)を参照してください。以下の一セル記述は取得当時の記録です。

# TB01 — Colabで三者の境界を点検する

**更新：初回実行で入力整形の誤拒否を確認したため、現在は[実装v0.1.1の説明](three-role-boundary-01-connection-v0.1.1-2026-10-13.md)と同リンクの修正版セルを使用する。** 以下は最初の準備時点の記録。27合成テストではこの実tokenizerの処理差を捉えられなかった。

2026-10-13。**設計・一セルコード・モデルなし検証を完了。実モデルによる成績は未取得。**

## 実行するファイル

**[Readable code and current instructions](../generation/README.md)** を開き、先頭から最後までColabの一つのコードセルへコピーして実行する。長い埋込み部分も含める。旧結果ZIPやローカルのscriptsフォルダをアップロードする必要はない。

- GPU：A100 80GB、またはRTX PRO 6000 Blackwell級。モデル読込み前にVRAM・BF16を点検する。
- モデル：前回と同じQwen3.5-27B、固定revision、BF16・non-thinking。既存の成功した生成コードをそのまま同梱。
- 件数：本人形成18＋個別投票36＋二/三票時の読出し72＝通常・最大126回答。
- 時間：仮見積もり15〜30分、初回ダウンロード・準備込み45分上限。初回の約56GBの重み取得は回線に依存する。
- Drive接続、HF Secret設定、追加有料API、設定の手編集は不要。固定モデルは公開取得経路を使用する。
- Colab以外ではモデル取得・ロードの前に停止する。

終了時に **`npp-tb01-result-日時-ID.zip`** のダウンロードを要求する。ブラウザが遮断した場合は、Colab左のFilesから `/content/` 内の同名ZIPを保存する。このZIPを返送すれば、原回答・実入力・保存物・コードから照合できる。

## 実行中の表示と停止時

`1/126 FORM ...` のように予定回答数で進捗が出る。`strict=False` はその回答に意味不成立があるという記録であり、実行エラーではない。`FORMAT_REJECT` は形式不備、`DEPENDENCY_MISSING` は必要な親の形式不備等で実行できない子を指す。他の実行可能な入力は続ける。

OOM・生成例外・時間上限では残りを未実行／依存欠測として閉じ、回収する。正答が出るまでの再試行はない。21予定回答ごとに部分ZIPも `/content/npp_tb01_runs/` へ保存する。GPUプロセスの停止からは親プロセスが回収を試みるが、ランタイム全体の消失後は自動DLできないため、見える部分ZIPを保存する。

同じランタイムでセルを再クリックした場合、既存証拠の照合・ZIP回収だけを行い、生成を追加しない。実行中のロックが残っていれば重複実行を拒否する。エラー時は設定やモデルを変更してやり直す前にZIPを返送する。

## 実装と検証の範囲

[設計書](three-role-boundary-01-plan-v0.1-2026-10-13.md)と[取得前固定](three-role-boundary-01-v0.1-2026-10-13.md)に、材料・割付・予想・採点・終了規則を保存した。

既存XM01/JR01のモデル取得・tokenizer/EOS・生成、immutable保存、JSON解析、外枠正規化を再利用した。三者用の材料、依存関係、厳密schema、原経験からの採点、集計を追加した。各回答の入力は実際に保存された親を使い、意味不成立を正解に置換しない。モデルには合意の正解を渡さず、実票から判断させる。個別票のsenderは呼出しの役に結び付ける。

27 CPUテストがPASS。完全経路、二票の合意捏造、他役の根拠混入、未返答／別proposal、誤った全員承認、本人推奨と共同担当の混同、JSON破損、意味不成立の実際の受渡し、依存先のみの欠測、時間上限・生成例外・途中停止、再実行での追加生成防止、ZIP再集計、別プロセス照合を含む。配布セル内の既存4モジュールはJR01配布版とbyte一致。**これは実装の合成検査であり、三者のLLMが成功した成績ではない。** Colabでの実際のロード・GPU生成・所要時間は今回まだ確認していない。

## コードと記録の入口

| 役割 | ファイル |
|---|---|
| 固定材料・プロンプト・依存関係 | design (source not bundled) |
| 厳密schemaと原経験からの採点 | scoring (source not bundled) |
| 実入力／親hash／原回答の保存と実行 | runtime (source not bundled) |
| Colab準備・中断時回収 | bootstrap (source not bundled) |
| 一セルの再生成 | builder (source not bundled) |
| 返送ZIPのローカル照合 | [aggregator](../../../reference-code/aggregate_three_role_boundary_01.py) |
| 合成テスト | tests (source not bundled) |
| 配布hash・継承対応・検証記録 | 準備監査 (source not bundled) |

ローカルでの再集計例（モデルは読み込まない）：

```bash
python3 scripts/aggregate_three_role_boundary_01.py /path/to/npp-tb01-result-example.zip --output /path/to/new-analysis.json
```

この入口は今回の固定payloadを使い、ZIP内のコードを実行しない。既存の出力分析は上書きしない。
