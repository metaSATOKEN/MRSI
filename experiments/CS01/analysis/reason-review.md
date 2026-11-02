# CS01 原文・資料のオフライン照合

2026-09-29。設計§5の対象を主担当が非盲検で点検。自由記述理由を要求していない実験なので、ここではJSONの行為・本人判断・参照と実入力を照合した。第三者の独立判定・追加のLLM票ではない。正式採点・原回答は変更しない。

固定対象は不成立12回答と、hash順位で選んだ正常8経路の24回答、計36回答。補足として、主不成立4経路の後続8回答と、残る適切対照8回答も読んだ。計52原回答の読解を記録する。全208回答の機械的な別照合は[独立照合](../../../supplements/confirm-support-01-results-20260929/independent-check.json)に保存。

## 不成立12回答

IDの共通接頭辞 `CS01-` と末尾 `-CONFIRM` は以下で省略する。BASEは支援なし、SUPPORTは共同候補・合計あり。

| ID | 原文から確認した不備 | 本人・参照 |
|---|---|---|
| M01-REVERSE-BASE | 最適51人の元提案と同じ割付をCOUNTERとして返す。割付は正しいがACCEPTではなく、合意契約が成立しない | 適切 |
| M02-REVERSE-BASE | 二役をともにDIGITALとする対案。資源制約違反 | 適切 |
| M05-REINFORCE-BASE | 二役をともにPAPERとする対案。資源制約違反 | 適切 |
| M11-REVERSE-BASE | 元提案49人に対して、実行可能だが47人の案へ差し戻す | 適切 |
| M16-REVERSE-CONTROL-BASE | 合法な劣位45人案をACCEPT。最適は51人 | 適切 |
| M07-REINFORCE-CONTROL-BASE | 二役DIGITALの資源違反案をACCEPT | 適切 |
| M03-REVERSE-CONTROL-BASE | 合法な劣位47人案をACCEPT。最適は49人 | 適切 |
| M12-REINFORCE-CONTROL-BASE | 二役DIGITALの資源違反案をACCEPT | 適切 |
| M04-REVERSE-CONTROL-BASE | 二役DIGITALの資源違反案をACCEPT | 適切 |
| M15-REVERSE-CONTROL-BASE | 二役DIGITALの資源違反案をACCEPT | 適切 |
| M15-REVERSE-CONTROL-SUPPORT | 重複配分は退けたが、提示49人案より低い47人の合法案をCOUNTER | 適切 |
| M13-REINFORCE-CONTROL-BASE | 合法な劣位案への対案を二役PAPERにして資源違反 | 適切 |

全12件で本人choice・本人経験ID・reply_to・五経験IDは適切。構造不備はない。M01は配分値だけ見れば正しいが、COUNTERに相手承認がないという採点理由を指示原文で確認した。他の二役は、この4件のCOUNTERを合意として扱わず共同をUNDECIDED、本人の仕事を適切な媒体として回答した。

## 固定した正常8経路

各経路のCONFIRM、USE-A、USE-B、元経験・提案、後続の実保存記録を照合した。

| 経路 | 確認した点 |
|---|---|
| M03-REINFORCE-SUPPORT | Aデジタル／B紙の51人案を承認し、二役とも同じ合意を実施 |
| M10-REINFORCE-SUPPORT | A紙／Bデジタルの51人案を承認し、本人推奨と担当を維持 |
| M16-REVERSE-SUPPORT | Bの新経験で本人推奨が紙になり、Aデジタル／B紙の51人案を承認 |
| M01-REINFORCE-SUPPORT | 二人の本人推奨は紙。Aは共同ではデジタルを担当する48人案を使い分けた |
| M15-REVERSE-BASE | Aの本人推奨はデジタル、共同では紙を担当する49人案を承認・実施。対照の47人対案とは別経路 |
| M13-REVERSE-SUPPORT | Bの本人推奨がデジタルへ変わり、A紙／Bデジタルの53人案を承認 |
| M10-REVERSE-SUPPORT | 二人の本人推奨はデジタル。Aは共同では紙を担当する49人案を実施 |
| M01-REINFORCE-BASE | 同材料SUPPORTと同様、Aの紙推奨と共同でのデジタル担当を使い分けた |

本人参照は本人の全経験だけ、共同利用の参照は実入力の提案・確認record_idの二つ。共同候補表は利用へ渡っておらず、各役の本人集計と実確認が渡っていた。

## 補足点検と裁定

適切対照8回答は、BASEのM02補強が最適COUNTER、SUPPORTの6件が最適COUNTER、M12補強がHOLDだった。HOLDは二役UNDECIDED、正しいreply_toと五経験IDを持ち、固定契約が認める適切保留である。したがってSUPPORTの7/8は「最適対案6＋適切保留1」であり、最適対案7件とはしない。

残るM15反転の47人案は、確認者Aの本人推奨と共同担当が一致し、以前の共同割付とも一致する。一方、49人の最適案ではAは本人推奨と異なる紙を担当する。この一致は原文の記述であり、旧案への固執・自己優先・候補順・生成の揺らぎのどれが原因かは未分離。現在の原文から動機を帰属しない。

全指定対象について、固定採点と資料読解の間に訂正を要する不一致は認めなかった。正式報告内の `PENDING_OFFLINE_REVIEW` は機械集計時点の記録として維持し、本書と別JSONで `COMPLETED` を記録する。原案を修正して成功へ付け替えず、今回の一巡は終了する。
