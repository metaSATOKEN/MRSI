# HISTORY-STABILITY-02：全件レビューの保存契約

2026-09-15。採点LLMの意味基準は旧v0.4をそのまま使う。本書は操作者の受け口と対象IDを新設計へ接続するもので、生成・判定プロンプトには渡さない。

全720原文・Sol/Lunaの1,440予定評価枠をレビューする。形成144原文／288枠、プローブ576原文／1,152枠。6窓の各々で、形成24原文／48枠を閉じてからプローブ96原文／192枠へ進み、その全レビューを閉じて次窓へ進む。途中は取得・レビュー進捗だけを返し、全件封印前にS・CI・pを計算しない。

意味基準・原文側のevent_target／fact_grounding／role_reference・判定側の7基準とnonselectionは、別保存した `previous-review-contract.md` の定義・境界例を継承する。同書の108／216、M1/M2、x∈{−1,0,+1}という旧実験の件数と分析表現は本実験へ引き継がない。

原文IDは固定割付の720個、事実IDはM01〜M12・OLD/NEW・INTRO/P/C/LIMIT。形成では同材料OLDのみ、プローブでは同材料OLD/NEWを参照できる。対応事実なしはNONEを単独使用。全原文のhash、連続引用、具体的理由、各欄PASS/FAIL/UNRESOLVEDを必須とする。全文で対象が分かれば特定語の反復は要求せず、根拠が曖昧なら未裁定を残す。

判定候補はrater/source_id/candidate_attempt/candidate_raw_sha256/diff_sha256で結合する。label・quote・adoptionの支持、alternative・uncertainty・change・changesの品質、nonselectionと具体的noteを別欄に記録。候補なしは全基準・nonselectionをUNRESOLVED。原ラベルの置換や再採点はしない。NULL理由だけの最大1回差し戻しは別の既存機械規則に従う。

各プローブの主分類がどちらかの採点法で未支持、または原文event_target/fact_groundingが非PASSなら、両採点法に共通の未知4分類 {P,C,MIXED,OTHER} とする。予定分母6・15ペアを維持する。主指標は4分類一致率であり、MIXEDとOTHERを同じものにしない。副次の方向得点のみP=+1/C=−1/MIXED=OTHER=0を使う。

形成の意味フラグは形成品質として保存し、それだけで実際の全6発言を取り除いたり、群やプローブを未知にしたりしない。構造上有効なら全群P等でも次へ進む。全6発言を取得できなければ代筆・短縮・再形成せず取得不成立で止める。

rootのレビューは非盲検で、独立した正解ではない。合成テスト用のPASS・引用・理由は保存経路のfixtureであり、意味精度の証拠として扱わない。全12レビュー区間を封印した後のみ、12材料単位の固定式で解析を公開する。
