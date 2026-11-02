# 第三報の関連研究調査と位置づけ

2026-09-29｜一次資料の本文に基づく執筆用メモ｜新規モデル実験0

## 1. 調査の結論

**第三報の位置づけは、本人の経験に基づく判断と共同の担当を別々に出力させ、その保存・利用・反復を対応付けた小規模比較に置く。** 工程別評価、役ごとの目標、コードへの計算分担、反復信頼性には既存研究がある。その上で、本稿は次の組合せを具体的な実記録から示す。

- 最後に本人判断が正しくても、途中の保存判断の適合は異なる。
- 本人判断が安定して正しくても、同じ共同の誤承認が繰り返される。
- 総合指標が同じ不成立でも、本人欄と共同欄の不備が反復ごとに入れ替わる。
- 低品質な合意が、正しく保存されて忠実に利用される実経路がある。

これらは今回の実験を統合して読む観点である。先行研究全体に同様の観測がないという優先権の主張は置かない。

## 2. 調査範囲と確認方法

検索軸は、(a) LLMの社会的相互作用・交渉、(b) 多主体の協調過程と故障診断、(c) 決定論的計算とLLM判断の分担、(d) 同一課題の反復信頼性。arXiv、ACL Anthology、PMLR、OpenReviewの一次資料を対象にした。

検索語には `LLM multi agent negotiation personal goals collective outcome`、`MultiAgentBench collaboration competition`、`Why Do Multi-Agent LLM Systems Fail`、`AgentBoard progress rate`、`PAL Program-aided Language Models`、`tau-bench reliability`、`LLM negotiation deterministic Offer Generator` を使用した。2026-09-29時点の焦点を絞った調査で、網羅的レビューや系統的レビューではない。

Hugging Face Papersのアクセス手順も参照したが、当該markdownページはブラウザ取得で未対応または取得不能だった。arXiv HTML/PDF、学会公開PDFへ切り替え、下表の記述に関わる節を実際に確認した。一部の推測したarXiv版URLは取得できなかったため、採用時には実在する版の書誌へ結び直した。ブログ・SNS・検索結果の要約だけを本文の根拠にしていない。今回の採用文献8本の確認箇所を以下に残す。

## 3. 採用文献と比較の境界

### R1. SOTOPIA

Xuhui Zhou et al. *SOTOPIA: Interactive Evaluation for Social Intelligence in Language Agents.* ICLR 2024。初出2023、確認版はarXiv v2（2024-03-22）。[書誌](https://arxiv.org/abs/2310.11667v2)／[一次PDF](https://arxiv.org/pdf/2310.11667v2)。

**確認箇所：** §2.2と§3。役・目標を持つエージェントの相互作用と、目標達成、人物らしさ、関係性などの複数軸による評価を確認した。

**採用する位置づけ：** 役ごとの目標と相互作用を複数軸で評価する先行例。本稿の本人判断は、経験値から正解が定まる限定された推奨であり、人格への忠実性の指標ではない。社会的知性の評価を今回実施したとは書かない。

### R2. NegotiationArena

Federico Bianchi, Patrick John Chia, Mert Yuksekgonul, Jacopo Tagliabue, Dan Jurafsky, James Zou. 2024. *How Well Can LLMs Negotiate? NegotiationArena Platform and Analysis.* [arXiv v1](https://arxiv.org/abs/2402.05863v1)／[一次PDF](https://arxiv.org/pdf/2402.05863v1)。

**確認箇所：** §2.1–2.2。資源交換、複数ターンの分配、売買、受諾または回数上限による終了、構造化された提案の記録を確認した。

**採用する位置づけ：** 提案・受諾と配分結果を測る近接研究。本稿では共同の合計最大化を両役に明示し、本人の別業務に関する推奨を同時に出力する。役の推奨と共同担当の不一致を、利己的な交渉や不合理性の心理診断へ読み替えない。

### R3. MultiAgentBench

Kunlun Zhu et al. 2025. *MultiAgentBench: Evaluating the Collaboration and Competition of LLM agents.* ACL 2025, pp.8580–8622。[書誌・DOI](https://aclanthology.org/2025.acl-long.421/)／[一次PDF](https://aclanthology.org/2025.acl-long.421.pdf)。

**確認箇所：** §3.2–3.3。マイルストーンの達成と寄与主体、最終課題成績、通信・計画の評価を確認した。評価にはLLMによる判定と、課題に応じた規則ベースの採点がある。

**採用する位置づけ：** 最終成績と協調過程を分ける先行例。本稿は限定された二役課題で、本人欄・共同欄・保存記録を固定規則により対応付ける。既存ベンチマークを最終正答だけの評価と総称しない。

### R4. AgentBoard

Chang Ma et al. 2024. *AgentBoard: An Analytical Evaluation Board of Multi-turn LLM Agents.* NeurIPS 2024。[書誌v2](https://arxiv.org/abs/2401.13178v2)／[一次PDF](https://arxiv.org/pdf/2401.13178v2)。

**確認箇所：** §2.2、式(2)、§3.2。途中の目標到達をprogress rateとして評価し、最終成功だけでは見分けにくい部分達成を扱うことを確認した。

**採用する位置づけ：** 総合成否が局所的な達成を隠すという問題意識の先行例。本稿では、同じ固定入力に対する反復で不備位置が入れ替わった具体的な観測を加える。AND指標の論理的な性質自体を発見とはしない。

### R5. MAST

Mert Cemri et al. 2025. *Why Do Multi-Agent LLM Systems Fail?* [書誌v3](https://arxiv.org/abs/2503.13657v3)／[一次HTML](https://arxiv.org/html/2503.13657v3)。

**確認箇所：** §3–4、付録の分類一覧。実行履歴から14失敗様態を、システム設計、役間の不整合、検証の三群へ整理する。LLM注釈器と人手評価の対応も別途評価している。

**採用する位置づけ：** 失敗を工程・種類ごとに扱う近接研究。本稿の誤承認を広い意味で検証の問題として対照できるが、MASTの正式ラベルを全回答へ付与したわけではない。新しい故障分類の網羅性や根本原因の同定を主張しない。

### R6. τ-bench

Shunyu Yao, Noah Shinn, Pedram Razavi, Karthik Narasimhan. 2024. *τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains.* [書誌v1](https://arxiv.org/abs/2406.12045v1)／[一次HTML](https://arxiv.org/html/2406.12045v1)。

**確認箇所：** §1、§3、§5.1。API・ユーザー・方針に関わる課題で、最終データベース状態と、反復を通じた成功の一貫性pass^kを評価している。

**採用する位置づけ：** 一度の成功と反復信頼性を分ける先行例。JR01は三反復の工程別記述で、τ-benchの課題や推定量を適用したものではない。三回正しいことを真の成功率100%としない。

### R7. PAL

Luyu Gao et al. 2023. *PAL: Program-aided Language Models.* ICML 2023, PMLR 202, pp.10764–10799。[書誌](https://proceedings.mlr.press/v202/gao23f.html)／[一次PDF](https://proceedings.mlr.press/v202/gao23f/gao23f.pdf)。

**確認箇所：** §3、処理系との役割分担、実行をLMへ戻す分析。LLMがプログラムを生成し、計算を処理系へ委ねる構成を確認した。

**採用する位置づけ：** 言語処理と計算を分担する先行例。本稿はあらかじめ固定したコードで集計を作り、選択・承認をLLMへ残す。モデルによるプログラム生成能力の評価ではない。

### R8. OG-Narrator

Tian Xia, Zhiwei He, Tong Ren, Yibo Miao, Zhuosheng Zhang, Yang Yang, Rui Wang. 2024. *Measuring Bargaining Abilities of LLMs: A Benchmark and A Buyer-Enhancement Method.* Findings of ACL 2024, pp.3579–3602。[書誌・DOI](https://aclanthology.org/2024.findings-acl.213/)／[一次PDF](https://aclanthology.org/2024.findings-acl.213.pdf)。

**確認箇所：** PDF p.8、Figure 6周辺。決定論的なOffer Generatorが価格を生成し、LLMがその提案を自然言語化する処理を確認した。

**採用する位置づけ：** 共同・交渉場面でも生成処理を分担する直接的な先行例。本稿では候補の合計を供給した後の承認をまだLLMが行うため、支援をどこまで処理として確定するかという比較に接続する。決定論の導入自体を新規性としない。

## 4. 本文への反映

本文§2を「個々の目的と共同結果」「工程別評価と反復」「計算と判断の分担」の三つに整理し、比較表を設けた。文献の説明は今回の位置づけに必要な範囲に絞った。第一・第二報の記憶管理文献をそのまま大量に再掲せず、第三報の評価対象に近い文献を選んだ。

今回の主張は「本人判断の集計供給」「共同承認」「後続利用」「固定入力での変動」の対応に置く。本人集計が利己性を誘発した、LLMが数字を無視した、といった機構説明は書かない。本人・共同の欄を分けるだけで長期共存を達成した、という主張へも進めない。

## 5. 次の実験候補棚

第三報の草稿は現有証拠で閉じる。以下はその完了条件へ追加せず、次の研究判断の材料とする。

| 優先候補 | 今の証拠で不足していること | 小比較の方向 | 再開条件 |
|---|---|---|---|
| 本人ノート×本人集計の分離 | 共同確認の二条件は旧ノートも異なる | 同じ生経験・共同表・開始案の下で、ノートの正誤と集計の有無を交差させる | 誤承認の原因に関する主張へ進むとき |
| 合意確定前の決定論的検査 | 計算資料の供給だけでは誤承認が残った | LLMの承認をそのまま採用する条件と、不適合を検出して共同だけ保留する条件。誤案の自動置換は別条件 | 誤合意経路を抑える運用を比較するとき |
| 支援段階の分離 | 形成・確認・再確認へまとめて供給した | 形成のみ／確認以降のみ／全段階など、固定予算の交差比較 | 供給コストと必要段階を決めるとき |
| 期間・モデル・材料の拡張 | 単一モデル、短い経路、既知課題形式 | 更新と交換を複数巡にし、別モデルや実務型の材料で検証 | 本稿の局所的観測を運用上の一般則へ広げるとき |

関連研究から着想できる設計案と、今回実測した性能は区別する。外部研究の成功率を今回の効果量に足したり、次実験が成功する根拠として扱ったりしない。
