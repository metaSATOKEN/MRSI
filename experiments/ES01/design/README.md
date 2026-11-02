# ES01：設計段階の材料表

**2026-09-28追記：承認後の実装固定を完了。** frozen-v0.1 (see the evidence index)に全文指示・schema・初回入力・予定ID・採点を保存。[一セル版の使い方](../../../docs/study2/experience-shared-01-connection-v0.1-2026-09-28.md)。材料表は不変、実モデル生成0。以下は設計時点の説明。

2026-09-28。実行入力のパッケージではなく、[設計書v0.1](../docs/experience-shared-01-plan-v0.1-2026-09-28.md)の数値と割付を点検する資料。

- [materials-proposal.json](materials-proposal.json)：8配置、経験4行ずつ、許容解集合、経験反転の対応、SELF16生成の二枝への共用、USEの条件順案。
- 算術・配置点検コード (see the evidence index)と結果 (see the evidence index)：経験の全反転、同点を含む割付、保留・不一致を合意へ変えないPLAN_FLIP、予定分母を検査。

このJSONには `expected_not_for_model` などの採点期待値がある。**ファイル全体をモデルへ渡さない。** 次工程で、経験行・本人の保存SELF・必要な共同記録だけを許可項目から組み立てる。条件名、プロフィール名、正解、集計・操作ラベルは送信しない。

SELFは2ブロック×2反復×2役×2本人経験の16件。同一の実SELFを相手経験の二条件へ分岐させる。共有前の経験応答は8比較、共有後は相手条件も含む各16比較である。条件の枝を独立した個体形成として数えない。

材料は合成経験で、同じIDの反転配置は別の仮想世界。異なる配置間で記録を統合しない。SELF/FORMのLLM生成、実行用指示・schema、採点実装、Colab接続は未実施。
