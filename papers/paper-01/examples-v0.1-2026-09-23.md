# 補足資料S2：本文の通し例と原資料

第一報v0.10の§3.4と§5.3で使った、取得済みの実回答・実保存物の対応を示す。新しく生成した例や、誤りを修正した出力ではない。本文のJSONは必要な欄を抜粋しており、完全回答は以下の資料を参照する。

## 担当客出典の末尾欠落と後続利用（E1-G49/B）

同じ初回資料を二方式へ与えた。選択＋複製の共同観測は、回答中の位置指定を保存器が実体化したものなので、モデル原回答と保存ノートを別に示す。

### 再記述

- MERGE：[入力](../../evidence/paper-01/data/pair/states/E1-G49-REWRITE-MERGE-B-incoming.json)
- MERGE：[モデル原回答](../../evidence/paper-01/data/pair/generations/E1-G49-REWRITE-MERGE-B-raw.txt)
- MERGE：[保存したノート](../../evidence/paper-01/data/pair/states/E1-G49-REWRITE-MERGE-B-saved.json)
- PROBE：[入力](../../evidence/paper-01/data/pair/states/E1-G49-REWRITE-PROBE-B-incoming.json)
- PROBE：[モデル原回答](../../evidence/paper-01/data/pair/generations/E1-G49-REWRITE-PROBE-B-raw.txt)

### 選択＋複製

- MERGE：[入力](../../evidence/paper-01/data/pair/states/E1-G49-SELECT-MERGE-B-incoming.json)
- MERGE：[モデル原回答](../../evidence/paper-01/data/pair/generations/E1-G49-SELECT-MERGE-B-raw.txt)
- MERGE：[保存したノート](../../evidence/paper-01/data/pair/states/E1-G49-SELECT-MERGE-B-saved.json)
- PROBE：[入力](../../evidence/paper-01/data/pair/states/E1-G49-SELECT-PROBE-B-incoming.json)
- PROBE：[モデル原回答](../../evidence/paper-01/data/pair/generations/E1-G49-SELECT-PROBE-B-raw.txt)

両方式で最新共同観測はA版3・B版4、紙ALL・デジタルNOT_ALLである。正答は猫／紙。再記述は担当客元ID `RAD9D1FEC60F1FA2` を保持し、選択＋複製の個別欄と後続回答は `RAD9D1FEC60F1FA` を含む。担当客欄は機械複製の対象外である。

## 対象不明を保留した回答（E2-G01-ABSENT-ID_ONLY-PROBE-A）

通知の対象を特定できないため、撤回した観測者を空の配列、案内判断をUNKNOWN、状態をPENDINGとし、未解決通知を残した。完全回答には担当客と有効観測も保持されている。

- [後続判断への入力](../../evidence/paper-01/data/pair/states/E2-G01-ABSENT-ID_ONLY-PROBE-A-incoming.json)
- [完全な原回答](../../evidence/paper-01/data/pair/generations/E2-G01-ABSENT-ID_ONLY-PROBE-A-raw.txt)

固定規則の採点は完遂=False、根拠適合=True。各欄の判定は[保存済み採点](../../evidence/paper-01/data/pair/analysis.json)の該当IDにあり、補足資料S1の再計算で照合できる。
