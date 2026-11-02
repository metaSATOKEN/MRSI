# E1 原回答の工程別点検（事後・記述的）

2026-09-21。固定主量・採点・未確定の扱いは変更しない。第1〜4窓の原回答512件を対象とする。E2は事前固定の条件のまま取得中。以下の工程別切分けは追加の有意差検定ではない。

## 成分の観測

値は成立／既知の不成立／未確定。行成分を独立した標本数へ昇格しない。

| 成分 | REWRITE | SELECT |
| --- | --- | --- |
| 統合時の共同行・出典／現在参照込み（256行成分） | 253 / 3 / 0 | 256 / 0 / 0 |
| 統合時の共同行・内容のみ（256行成分） | 254 / 2 / 0 | 256 / 0 / 0 |
| 統合時の本人customer（128役回答） | 128 / 0 / 0 | 127 / 1 / 0 |
| 後続利用・出典込み（128役回答） | 124 / 3 / 1 | 123 / 5 / 0 |
| 後続利用・内容のみ（128役回答） | 124 / 3 / 1 | 126 / 2 / 0 |

全工程主量は両方式59/64組成立。REWRITEは4不成立＋1未確定、SELECTは5不成立。主差の欠測上下限は−1.5625〜0 percentage pointsで、主p値は事前規則により算出しない。工程別の数値を主量の代わりに採用しない。

## 全13非完全回答

| ID | 原文と入力の照合 |
| --- | --- |
| [E1-G11-REWRITE-MERGE-B]（原資料：`study2/runs/paper-01-pair-prepared-20260921/windows/W1/generations/E1-G11-REWRITE-MERGE-B-raw.txt`） | 共同B行の値・版・出典は正しいが、受領票にその値を支えない旧B行のPARTNER_GROUPも含めた。後続判断は成立。受領票自体は後続入力へ渡さない設計。 |
| [E1-G36-REWRITE-MERGE-A]（原資料：`study2/runs/paper-01-pair-prepared-20260921/windows/W2/generations/E1-G36-REWRITE-MERGE-A-raw.txt`） | 共同B行の最新出典・版を保ちつつ、paperをALLからNOT_ALLへ書き違えた。 |
| [E1-G36-REWRITE-PROBE-A]（原資料：`study2/runs/paper-01-pair-prepared-20260921/windows/W2/generations/E1-G36-REWRITE-PROBE-A-raw.txt`） | 前段の誤った共同B行が渡され、channelはUNKNOWN。正しい世界のPAPERとは不一致。 |
| [E1-G45-SELECT-PROBE-B]（原資料：`study2/runs/paper-01-pair-prepared-20260921/windows/W2/generations/E1-G45-SELECT-PROBE-B-raw.txt`） | 共同ノートは正しいが、channelをPAPERではなくDIGITALと回答し、根拠出典もBだけを挙げた。 |
| [E1-G03-SELECT-PROBE-B]（原資料：`study2/runs/paper-01-pair-prepared-20260921/windows/W2/generations/E1-G03-SELECT-PROBE-B-raw.txt`） | channelは正しいDIGITALだが、必要なA/Bの出典のうち一方のみを列挙。 |
| [E1-G49-SELECT-MERGE-B]（原資料：`study2/runs/paper-01-pair-prepared-20260921/windows/W3/generations/E1-G49-SELECT-MERGE-B-raw.txt`） | 共同行の選択・複製は成立。生成が残る本人customerの出典で、末尾の2が欠けた。 |
| [E1-G49-SELECT-PROBE-B]（原資料：`study2/runs/paper-01-pair-prepared-20260921/windows/W3/generations/E1-G49-SELECT-PROBE-B-raw.txt`） | 犬猫・案内の判断は正しいが、前段の本人customerの誤IDを引き継いだ。 |
| [E1-G23-REWRITE-PROBE-B]（原資料：`study2/runs/paper-01-pair-prepared-20260921/windows/W3/generations/E1-G23-REWRITE-PROBE-B-raw.txt`） | 末尾に余分な閉じ波括弧がありJSONのExtra data。補修せず、両主成分を未確定として保持。 |
| [E1-G02-REWRITE-PROBE-B]（原資料：`study2/runs/paper-01-pair-prepared-20260921/windows/W3/generations/E1-G02-REWRITE-PROBE-B-raw.txt`） | 正しい共同ノートから、DIGITALではなくPAPERと回答。 |
| [E1-G16-SELECT-PROBE-A]（原資料：`study2/runs/paper-01-pair-prepared-20260921/windows/W4/generations/E1-G16-SELECT-PROBE-A-raw.txt`） | DIGITALの判断は正しいが、Aの出典R577B7D5C976ACB6の末尾6が欠けた。 |
| [E1-G27-SELECT-PROBE-A]（原資料：`study2/runs/paper-01-pair-prepared-20260921/windows/W4/generations/E1-G27-SELECT-PROBE-A-raw.txt`） | 正しい共同ノートから、PAPERではなくDIGITALと回答。 |
| [E1-G06-REWRITE-MERGE-A]（原資料：`study2/runs/paper-01-pair-prepared-20260921/windows/W4/generations/E1-G06-REWRITE-MERGE-A-raw.txt`） | 共同B行に、入力にある版1の旧行を保存。正しい最新行は版4。 |
| [E1-G06-REWRITE-PROBE-A]（原資料：`study2/runs/paper-01-pair-prepared-20260921/windows/W4/generations/E1-G06-REWRITE-PROBE-A-raw.txt`） | 前段の旧B行が渡され、channelはUNKNOWN。正しい世界のPAPERとは不一致。 |

## 読み方

共同行の選択・複製が対象とする部分は今回保たれたが、本人customerの転記と、保存後の読み出しには生成が残る。G49の誤IDはその残った生成部分で観測され、正しい判断とともに次の回答へ残った。これは方式全体の一般的な優越性の証明ではなく、介入の適用範囲と故障の場所を示す記述である。

E2の撤回対象はcoverageである。今回のG49はcustomerの誤IDなので、E2の結果をその個別例の撤回失敗の直接検証として結び付けない。G36/G06の後続UNKNOWNは保存内容との整合と世界の正答を分けて読む。モデルがどの内部過程で誤ったかはこの原文から確定しない。

JSON不備を人手で直して再採点すること、主p値を出すために標本や分母を変えることはしていない。
