"""Read-only source audit; writes new descriptive outputs only beside this file.

No research runners, network calls, changes to original scores, or new p-values.
Run from anywhere: python3 /absolute/path/to/this/file
"""
from pathlib import Path
from itertools import product
from collections import Counter
from math import comb, fsum
import hashlib
import json
import sys
import scipy
from scipy.stats import beta, binomtest

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SOURCES = {
    'analysis': 'throughline/audits/paper-01-pair-resume1-20260921/combined-analysis.json',
    'materials': 'study2/designs/paper-01-pair-20260921/materials.json',
    'estimate': 'throughline/audits/paper-01-estimate-20260920/estimate.json',
}
data = {k: json.loads((ROOT / p).read_text()) for k, p in SOURCES.items()}
checks = []

def check(name, condition):
    checks.append({'name': name, 'pass': bool(condition)})
    if not condition:
        raise AssertionError(name)

def pmf(n, k, p):
    return comb(n, k) * p**k * (1-p)**(n-k)

def root_increasing(fn, target):
    lo, hi = 0., 1.
    for _ in range(80):
        mid = (lo+hi)/2
        if fn(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2

def cp_direct(k, n, confidence):
    """Invert exact binomial tails with stdlib only (independent of beta code)."""
    tail = (1-confidence)/2
    lo = 0. if k == 0 else root_increasing(
        lambda p: fsum(pmf(n, j, p) for j in range(k, n+1)), tail)
    # P(X <= k) = tail equals P(X >= k+1) = 1-tail.
    hi = 1. if k == n else root_increasing(
        lambda p: fsum(pmf(n, j, p) for j in range(k+1, n+1)), 1-tail)
    return [lo, hi]

def cp(k, n, confidence):
    direct = cp_direct(k, n, confidence)
    t = (1-confidence)/2
    beta_ci = [0. if k == 0 else float(beta.ppf(t, k, n-k+1)),
               1. if k == n else float(beta.ppf(1-t, k+1, n-k))]
    scipy_ci = list(binomtest(k, n).proportion_ci(confidence_level=confidence, method='exact'))
    check(f'CP n={n} k={k} c={confidence}: three implementations',
          max(abs(x-y) for pair in [beta_ci, scipy_ci] for x, y in zip(direct, pair)) < 1e-10)
    return direct

def completions(groups):
    ids = sorted(groups)
    options = [[(r, s) for r, s in product(
        [False, True] if groups[g]['REWRITE'] is None else [groups[g]['REWRITE']],
        [False, True] if groups[g]['SELECT'] is None else [groups[g]['SELECT']])]
        for g in ids]
    rows = []
    for pairs in product(*options):
        a = sum(s and not r for r, s in pairs)
        b = sum(r and not s for r, s in pairs)
        la, ua = cp(a, len(ids), .975)
        lb, ub = cp(b, len(ids), .975)
        rows.append({'unknown_assignments': {g: {'REWRITE': r, 'SELECT': s}
            for g, (r, s) in zip(ids, pairs) if None in groups[g].values()},
            'SELECT_only': a, 'REWRITE_only': b, 'SELECT_L': la, 'SELECT_U': ua,
            'REWRITE_L': lb, 'REWRITE_U': ub, 'delta': (a-b)/len(ids),
            'ci95': [la-ub, ua-lb]})
    return rows

result = {'status': 'POST_REVIEW_OFFLINE_AUDIT', 'python': sys.version,
          'scipy': scipy.__version__, 'new_research_requests': 0,
          'source_hashes': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES.values()}}
result['E1'] = {}
for mode in ['strict', 'content']:
    original = data['analysis']['analysis']['E1'][mode]
    rows = completions(original['groups'])
    envelope = [min(r['ci95'][0] for r in rows), max(r['ci95'][1] for r in rows)]
    bounds = [min(r['delta'] for r in rows), max(r['delta'] for r in rows)]
    check(mode+' interval unchanged', all(abs(a-b)<1e-10 for a,b in zip(envelope,original['statistics']['conservative_ci95'])))
    check(mode+' missing bounds unchanged', bounds == original['statistics']['delta_bounds'])
    check(mode+' formal p absent', original['statistics']['exact_mcnemar_two_sided_p'] is None)
    result['E1'][mode] = {'completions': rows, 'envelope': envelope, 'delta_bounds': bounds}

groups = data['analysis']['analysis']['E1']['strict']['groups']
result['label_strata'] = {}
for axis, component in [('scene_name', 0), ('area', 1)]:
    labels = sorted({data['materials'][g]['scene'].split('・')[component] for g in groups})
    strata = []
    for label in labels:
        selected = {g:v for g,v in groups.items() if data['materials'][g]['scene'].split('・')[component] == label}
        counts = Counter()
        for v in selected.values():
            r, s = v['REWRITE'], v['SELECT']
            counts['unknown' if r is None or s is None else 'both' if r and s else 'REWRITE_only' if r else 'SELECT_only' if s else 'neither'] += 1
        strata.append({'label':label, 'n':len(selected), 'groups':list(selected),
                       **{k:counts[k] for k in ['both','REWRITE_only','SELECT_only','neither','unknown']}})
    check(axis+' partition', len(strata)==8 and all(r['n']==8 for r in strata))
    check(axis+' totals', [sum(r[k] for r in strata) for k in ['both','REWRITE_only','SELECT_only','neither','unknown']] == [54,5,4,0,1])
    result['label_strata'][axis] = strata

scores = data['analysis']['slot_scores']
result['shared_row_groups'] = {}
for method in ['REWRITE','SELECT']:
    method_groups = {}
    for g in groups:
        values = [scores[f'{g}-{method}-MERGE-{role}']['parts'][f'shared_note.coverage.{owner}']['strict']
                  for role in ['A','B'] for owner in ['A','B']]
        method_groups[g] = False if False in values else None if None in values else True
    result['shared_row_groups'][method] = {'groups': method_groups, 'pass': sum(v is True for v in method_groups.values()),
        'fail': [g for g,v in method_groups.items() if v is False], 'unknown': [g for g,v in method_groups.items() if v is None]}
check('shared groups REWRITE',result['shared_row_groups']['REWRITE']['pass']==61)
check('shared groups SELECT',result['shared_row_groups']['SELECT']['pass']==64)

result['E2_nominal_descriptive_intervals'] = []
for cell, metrics in data['analysis']['analysis']['E2'].items():
    row = {'cell':cell}
    for metric, rec in metrics.items():
        check(cell+'/'+metric+' observed eight', len(rec['groups'])==8 and all(type(v) is bool for v in rec['groups'].values()))
        k = sum(rec['groups'].values())
        row[metric] = {'k':k, 'n':8, 'cp95':cp(k, 8, .95)}
    result['E2_nominal_descriptive_intervals'].append(row)

# Re-enumerate pre-existing power scenarios; no observed-power estimate.
def exact_power(n, delta, q):
    probabilities = [(q+delta)/2, (q-delta)/2, 1-q]
    total = []
    for a in range(n+1):
        for b in range(n-a+1):
            m = a+b
            p = min(1., 2*sum(comb(m,k) for k in range(min(a,b)+1))/2**m)
            if p <= .05:
                total.append(comb(n,a)*comb(n-a,b)*probabilities[0]**a*probabilities[1]**b*probabilities[2]**(n-a-b))
    return fsum(total)

result['preexisting_power'] = [r for r in data['estimate']['power_scenarios']
    if r['groups']==64 and (r['delta'],r['discordance']) in [(.2,.3),(.2,.4),(.1,.3)]]
for r in result['preexisting_power']:
    check('prior power '+str((r['delta'],r['discordance'])), abs(exact_power(64,r['delta'],r['discordance'])-r['power'])<1e-10)
result['checks'] = checks
(OUT/'numerical-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')

lines = ['# 外部査読に対する数値照合', '', '2026-09-22。結果取得後の補足。原判定・主解析は変更していない。', '',
    '## 1. E1の区間：全補完と各成分', '',
    '`a = SELECTのみ成立、b = REWRITEのみ成立、Δ = SELECT − REWRITE`。各食違い率の97.5% Clopper–Pearson区間を使い、差を `[La−Ub, Ua−Lb]` とする。周辺区間を同時に覆う確率はBonferroniにより少なくとも95%。各周辺は二項モデルを仮定し、組間独立同分布の作業仮定が必要。欠測については全補完の包絡を取る。表の数値はすべて百分率またはポイント。', '',
    '| 指標／G23 REWRITE補完 | a | b | La | Ua | Lb | Ub | 差の下限 | 差の上限 |',
    '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
for mode, rec in result['E1'].items():
    for r in rec['completions']:
        assignment = next(iter(r['unknown_assignments'].values()))['REWRITE']
        values = [r[k]*100 for k in ['SELECT_L','SELECT_U','REWRITE_L','REWRITE_U']] + [v*100 for v in r['ci95']]
        lines.append(f"| {mode}／{assignment} | {r['SELECT_only']} | {r['REWRITE_only']} | "+' | '.join(f'{v:.6f}' for v in values)+' |')
for mode, rec in result['E1'].items():
    lines.append(f"\n{mode}の包絡：{rec['envelope'][0]*100:.6f}〜{rec['envelope'][1]*100:.6f}ポイント。\n")
lines += ['', '主解析の包絡は−17.363690〜16.602039。事後の括弧補正はG23成立の行に対応し、−17.363690〜14.484426。下端が同じなのは、その補完が元から包絡の下端を与えていたため。周辺下限を0に置く計算ではない。原稿の数値訂正は不要で、内訳の追記が必要。正式主p値は未算出のまま。', '',
    '独立実装は二項確率の直接和を二分探索で反転したもの。元コードと同じbeta分位点およびSciPyのexact区間APIと1e-10以内で一致した。研究実行器をimportせず、保存済み採点を読む。', '',
    '## 2. 共同観測行だけの組単位集計', '',
    '両役×A/Bの共同観測4行がすべてstrict成立した組：REWRITE 61/64、SELECT 64/64。REWRITEの不成立はG06・G11・G36。これは既存成分採点を今回組単位に集約した事後の記述で、追加検定はしない。strictには内容・出典に加え今回入力への参照も含まれるため、純粋な複製操作の単独効果とは呼ばない。行数256を独立Nにもしない。', '',
    '原設計には工程別成分の副指標が既に存在する。「成分を評価すること」全体が事後に生まれたわけではなく、今回の集約・表示が事後である。', '',
    '## 3. 場面名と会場ラベル別の内訳', '',
    '材料は8場面名×8会場の交差配置で64組それぞれ別の観測値・出典を生成している。8個の親データから8回ずつ再測定した設計ではない。同じラベルや共通テンプレートの影響は残るため、独立性を立証する表ではない。8クラスタの頑健性を保証する追加検定やbootstrapは行わない。', '']
for axis, strata in result['label_strata'].items():
    lines += [f'### {axis}', '', '| ラベル | N | 両成立 | Rのみ | Sのみ | 両不成立 | 未確定 |', '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in strata:
        lines.append('| '+r['label']+' | '+' | '.join(str(r[k]) for k in ['n','both','REWRITE_only','SELECT_only','neither','unknown'])+' |')
    lines.append('')
lines += ['## 4. E2の記述用区間', '',
    '| 条件 | 完遂 | 完遂 CP95% | 根拠適合 | 根拠適合 CP95% |', '| --- | ---: | --- | ---: | --- |']
for r in result['E2_nominal_descriptive_intervals']:
    c,e=r['completion'],r['evidence_appropriate']
    fmt=lambda v: '〜'.join(f'{x*100:.2f}%' for x in v)
    lines.append(f"| {r['cell']} | {c['k']}/8 | {fmt(c['cp95'])} | {e['k']}/8 | {fmt(e['cp95'])} |")
lines += ['', '今回追加した名目95%の各セル区間であり、同時区間ではない。固定された8場面を、交換可能な独立Bernoulli試行とみなす場合の参考。六条件は同じ8場面を共有し、48独立場面にはならない。誤ID＋ID_ONLYの完遂0は採点契約で特定不能にした条件の帰結で、その0/8区間を未知の「解決能力」の推定と解釈しない。根拠適合8/8の観測は、これらの入力で対象を捏造せず保持・保留したことを表す。', '',
    '## 5. 事前の検出力検討の照合', '',
    '2026-09-20の見積りおよび9月21日の実行前計画に存在したシナリオ。独立の多項確率の和で再照合した。', '',
    '| N | 真差 | 食違い率 | 検出力 |', '| ---: | ---: | ---: | ---: |']
for r in result['preexisting_power']:
    lines.append(f"| 64 | {r['delta']*100:.0f}pt | {r['discordance']:.2f} | {r['power']*100:.2f}% |")
lines += ['', '固定N・欠測なし・組間独立同分布・両側exact McNemar α=.05という仮定。20ptは費用と検出解像度の折合いであり期待効果の実測推定ではない。本文へこの計画根拠を移す。実現した食違い9組から事後検出力を算出して事前検討を置き換えない。', '',
    '## 再計算', '', '`python3 throughline/audits/paper-01-major-review-20260922/calculate.py`', '',
    f"Python {sys.version.split()[0]} / SciPy {scipy.__version__}。入力ファイル・hash・非丸め値・検査結果は同じフォルダの numerical-audit.json。スクリプトは同フォルダの派生JSONと本メモのみ再生成する。", '']
(OUT/'numerical-audit.md').write_text('\n'.join(lines))
print(json.dumps({'checks':len(checks),'all_pass':all(c['pass'] for c in checks),'strict':result['E1']['strict']['envelope']},ensure_ascii=False))
