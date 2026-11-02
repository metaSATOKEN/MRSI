# 関連研究と一次資料

## 2. 一次資料と、比較対象

番号は草稿の参考文献番号と共通。各研究の性能値は本稿の成績と横並びにしていない。

| 番号・研究 | 確認した一次資料と箇所 | 採用した記述 | 第四報との比較上の注意 |
|---|---|---|---|
| 1. Kaesberg et al., *Voting or Consensus?* | [ACL書誌](https://aclanthology.org/2025.findings-acl.606/)、[本文PDF](https://aclanthology.org/2025.findings-acl.606.pdf) §3.1–3.3、§4.1 | 三者の討論で、全員一致を含む合意方式と投票方式を比較 | 「既存は多数決だけ」と書かない。第四報は受領票の個別状態とその後の判断を対応させる |
| 2. Chen et al., *ReConcile* | [ACL書誌](https://aclanthology.org/2024.acl-long.381/)、[本文PDF](https://aclanthology.org/2024.acl-long.381.pdf) Introduction、方法の枠組み | 異なるLLMの回答・説明・確信度を参照して討論・集約する | 回答の合意形成と、指定案への各人の承認を読む課題を区別 |
| 3. Choi et al., *Debate or Vote* | [NeurIPS書誌](https://proceedings.neurips.cc/paper_files/paper/2025/hash/934252acd87f254d5d4672fbde283bd2-Abstract-Conference.html)、[arXiv v1本文](https://arxiv.org/html/2508.17536v1) §3.1ほか比較設計 | 初期回答の投票集約と、討論を行う条件を分ける | 「討論は常に無意味」という一般化や、本稿への効果量の移植はしない |
| 4. Zhou et al., *SOTOPIA* | [arXiv v2本文](https://arxiv.org/html/2310.11667v2) §2.1–2.2 | 役・社会的目標を持つ相互作用を多次元で評価 | 数値経験から定まる本人推奨は、人格・自由な社会的目標より狭い操作化 |
| 5. Bianchi et al., *NegotiationArena* | [arXiv v1本文](https://arxiv.org/html/2402.05863v1) §2–3 | 交換・分配・売買で提案・受諾と結果を評価 | 本稿は共同合計の最大化を共通目標とする。誤票だけから自己利益優先を推定しない |
| 6. Chu et al., *MASBench* | [書誌](https://arxiv.org/abs/2610.04672v1)、[v1本文](https://arxiv.org/html/2610.04672v1) §3–4、Appendix B.1、E.2 | 部分観測下の協調。日程調整で探索／検証、候補・拒否候補の記憶、段階別JSON投票を扱う | 状態管理とプロトコル比較に近い先行例。本稿は全資料を与えた固定候補で、一人の受領状態だけを対応させる |
| 7. Albayaydh & Zhao, *Do LLM Agents Negotiate Rationally?* | [書誌](https://arxiv.org/abs/2608.14613v1)、[v1 PDF](https://arxiv.org/pdf/2608.14613v1) §2.7、§4.3、§5–6 | schemaとプロトコル不変条件を検査する枠組みを提示 | 本稿の読出しはモデル回答を事後採点する構成。検証ミドルウェアの導入効果を今回測ったとはしない |
| 8. Zhu et al., *MultiAgentBench* | [ACL書誌](https://aclanthology.org/2025.acl-long.421/)、[本文PDF](https://aclanthology.org/2025.acl-long.421.pdf) §3.2–3.3 | 課題成績に加え、工程への貢献と協調過程を評価 | 工程別評価自体を本稿の独創としない。資料と出力欄の対応を具体化する |
| 9. Cemri et al., *Why Do Multi-Agent LLM Systems Fail?* | [arXiv v3本文](https://arxiv.org/html/2503.13657v3) §3、失敗分類と実行履歴 | 設計・役間の不整合・検証にまたがる失敗を分類 | 本稿の誤票・誤状態をMAST分類へ正式再ラベルしたわけではない |
| 10. Yao et al., *τ-bench* | [arXiv v1本文](https://arxiv.org/html/2406.12045v1) §3、§5.1 | 同一課題の反復成功をpass^kで評価 | 本稿の二／三反復は記述的点検。τ-benchの指標・推定値を算出したとはしない |

文献1–3・8は正式出版の書誌を優先し、内容照合に別のarXiv版を使った場合はその版を併記した。文献4のICLR表記と照合本文も区別した。2026年の近接文献6・7は指定版プレプリントとして扱う。文献7のページには識別子の年月と異なる提出月が表示されているため、公開日の先後を使う議論は行わず、著者・題名・指定版の確認と本文§4.3の枠組み記述に引用を限定した。
