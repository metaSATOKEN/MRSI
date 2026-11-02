# OS01 出力境界のオフライン監査

ユーザー承認された事後監査。原実験の正式未確定を保持し、別コピーの一欄隔離と意味評価を行った。原ZIP・既存コードへ書込みなし、新モデル0。

主報告：`study2/own-summary-01-boundary-audit-2026-09-28.md`（NPPルートから）。`scope.md` は今回の監査前に固定した範囲であり、元実験の事前登録ではない。`before-run.json` に監査前のコードhashと時刻を保存。

- `receiver_candidate.py`：USEの既知一欄のみを隔離する監査用候補。本番未配備。
- `test_receiver.py`：正常保持、拒否境界、意味不備温存の20合成テスト。`test-attempt-01.log` に初回結果。
- `audit.py`：原ZIP全件照合→限定隔離→旧意味採点→参考合算。利用の意味成分・合成指標は別計算で照合。提案・確認の意味は§325で独立照合した正式値を継承する。
- `analysis/candidates/`：56派生JSON。`analysis/quarantine/`：対応する未信頼の追加欄。原回答は元ZIPに保持。
- `analysis/per-response.json`：全384件の正式値、隔離trace、参考値。`analysis/reference-summary.json` は事後参考専用。
- `confirmation-arithmetic.json`：三確認不備×2Fの入力値・合法候補合計・実対案の対応。
- `protected-before.json`：不変確認した原資料39ファイル。`navigation-before/after` と台帳追記を別保存。

再計算はNPPルートから、まだ存在しない出力ディレクトリを指定する。ローカルモデルやネットワークを使わない。

```sh
python3 throughline/audits/posthoc/own-summary-01-boundary-20260928/audit.py /tmp/npp-os01-boundary-recheck
```

同じ出力先への再実行は拒否する。`MANIFEST.json` は自身とPythonキャッシュを除くこの監査の保存物を封印する。構造受理は意味の正しさを保証せず、参考集計は正式OS01の成績や進行許可を上書きしない。
