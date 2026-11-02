# 第四報・関連研究の焦点調査

2026-10-13｜v0.1｜日本語草稿 (source not bundled)の§2・参考文献に対応

## 1. 調査の問いと採用判断

対象は、①複数LLMの合意・投票、②役固有の目的と共同結果、③候補・承認状態の管理と検証、④工程別の失敗と反復信頼性である。一次本文を確認した10件を採用した。これは論文の主張を位置づける焦点調査であり、期間・データベース・採否を網羅的に固定したsystematic reviewではない。

**先行研究には、全員一致、構造化投票、候補と拒否の状態管理、工程別評価が既にある。第四報は、実票の後続利用と、同じ本人ノート・共同案に対する未返答／明示保留／承認の対応比較を結び付けることに焦点を置く。** 「三者にした」「最終正答だけでなく工程を見た」こと自体を初提案とはしない。

第三報の文献整理を起点に、次の語で追加検索し、著者・出版社のページと本文へ進んだ。

- `LLM multi agent consensus voting decision protocols unanimity approval benchmark`
- `LLM agents negotiation commitment protocol missing consent explicit agreement`
- `multi agent debate majority vote ACL 2025 voting consensus protocols`
- `LLM multi agent commitments consent protocol benchmark 2026 arxiv`
- ReConcileの論文名、FIPA Contract Netの公式仕様を対象とした検索

Hugging Face PapersのMarkdown取得は一件で取得エラーとなり、ACL Anthology、NeurIPS正式出版ページ、arXivの指定版HTML/PDFへ切り替えた。本文確認と書誌確認を分け、検索結果の要約だけを根拠にした記述は本文へ入れていない。

## 2. 一次資料と、草稿に採用した範囲

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

## 3. 草稿に反映した判断

### 3.1 強調する対応

- **投票の適切さと実票への忠実性：** TB01で実際に生成された不適切なHOLDを、後続が正しくHOLDとして扱う。同じ語の正誤を、工程と根拠の対応から説明する。
- **個別状態と全体判断：** TAR01で未返答をHOLDと取り違えても、未合意・実行保留が正しい例を示す。集約の非一意性という論理だけでなく、実回答と反復を根拠にする。
- **明示比較の成立範囲：** TCV01の2回答差とTCV02の差0を両方示す。方法全体の差、出力費用、比較欄に得られる診断情報を分ける。

### 3.2 採用しない言い方

「三者で初めて合意境界を測った」「先行研究は最終正答しか見ない」「比較欄が誤りを解消した」「三人になると合意が難しくなる」「未返答と拒否を区別する必要性を初発見した」は、現在の資料で支える主張としない。

また、TAR01の誤りはHOLDへの取り違えであり、未返答を承認へ変えたり、早まって実行した例ではない。実行保留が正しいことと、本人が保留を表明したという記録が正しいことを分けて述べる。

## 4. 今回の未採用・残項目

- FIPA Contract Netの公式HTMLは取得できず、今回確認できた一次本文として引用しなかった。古典的なコミットメント・プロトコルとの歴史的位置づけを広げる段階で再確認する。
- ProtocolBenchは検索で見つかったが、今回は通信形式・搬送費用の議論より受領状態の意味を優先し、本文未確認のまま採用しなかった。
- 近接研究の公開実装を再実行していない。文献比較は一次本文の課題・測定単位・構成の照合であり、性能再現の報告ではない。
- 公開版ではリンク・正式出版への更新、第四報の固定公開資料、資金・利益相反の著者確認を行う。今回の執筆を理由に新規モデル実験を追加しない。
