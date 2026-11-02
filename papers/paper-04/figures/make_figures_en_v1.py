"""English figures for Paper 4, from the finalized Japanese v0.2.

Drawing helpers adapted from Paper 3's working figure script.
Offline diagrams only: no experiments, rescoring, or PDF generation.
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.path import Path as MPath

OUT = Path(__file__).resolve().parent
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 13,
                     'svg.fonttype': 'path', 'svg.hashsalt': 'npp-paper04-en-v1',
                     'savefig.facecolor': 'white'})
INK, MUTED, EDGE = '#213547', '#536574', '#8b9aa6'
COLORS = {'record': '#f1f4f7', 'model': '#e4eef9', 'code': '#e3f1e9'}
fit_checks = []

def canvas(h):
    fig, ax = plt.subplots(figsize=(14.5, h))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.set(xlim=(0, 14.5), ylim=(0, h)); ax.axis('off')
    return fig, ax, []

def text(ax, x, y, content, size=13, weight='normal', ha='left', va='top', color=INK, **kw):
    return ax.text(x, y, content, fontsize=size, color=color, weight=weight,
                   ha=ha, va=va, linespacing=1.4, **kw)

def box(ax, checks, x, y, w, h, content, kind='record', size=13):
    patch=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.02,rounding_size=0.08',
                        facecolor=COLORS[kind],edgecolor=EDGE,linewidth=1.1)
    ax.add_patch(patch)
    t=text(ax,x+w/2,y+h/2,content,size,ha='center',va='center')
    checks.append((patch,t,content))

def arrow(ax, points):
    path=MPath(points,[MPath.MOVETO]+[MPath.LINETO]*(len(points)-1))
    ax.add_patch(FancyArrowPatch(path=path,arrowstyle='-|>',mutation_scale=16,
                               linewidth=1.5,color=MUTED))

def save(fig, ax, checks, stem):
    fig.canvas.draw(); renderer=fig.canvas.get_renderer(); rows=[]
    for patch,t,label in checks:
        p=patch.get_window_extent(renderer); b=t.get_window_extent(renderer)
        rows.append({'text':label,'inside_box':bool(p.x0+5<b.x0 and b.x1<p.x1-5 and p.y0+4<b.y0 and b.y1<p.y1-4)})
    frame=fig.bbox
    for t in ax.texts:
        b=t.get_window_extent(renderer)
        rows.append({'text':t.get_text(),'inside_canvas':bool(frame.contains(b.x0,b.y0) and frame.contains(b.x1,b.y1))})
    assert all(r.get('inside_box',r.get('inside_canvas')) for r in rows),rows
    fit_checks.append({'figure':stem,'checks':rows})
    fig.savefig(OUT/(stem+'.png'),dpi=300,metadata={'Software':'NPP paper 4 figure source'})
    fig.savefig(OUT/(stem+'.svg'),metadata={'Date':None,'Creator':'NPP paper 4 figure source'})
    plt.close(fig)

fig,ax,checks=canvas(10.6)
text(ax,.5,10.18,'Preserving judgments while reading actual votes',24,'bold')
text(ax,.5,9.70,'Same model, three roles; a fresh context for every LLM call.',16,color=MUTED)
box(ax,checks,.6,8.15,13.3,1.16,'Code supplies original experiences and numerical summaries\nFORM: own experience + summary\nVOTE / READ: all roles’ experiences + own summary + two candidate totals','code',16.5)
for x in [2.45,7.25,12.05]:
    arrow(ax,[(x,8.11),(x,7.02)])
box(ax,checks,.6,5.45,3.7,1.52,'LLM · FORM\nHolder + recommendation\nOwn evidence IDs','model',16.5)
box(ax,checks,5.4,5.45,3.7,1.52,'LLM · VOTE\nRetain own information\nACCEPT / HOLD on the proposal','model',16.5)
box(ax,checks,10.2,5.45,3.7,1.52,'LLM · READ\nOwn note + A/B/C states\nAgreement + execution','model',16.5)
arrow(ax,[(4.34,6.20),(5.36,6.20)])
text(ax,4.85,6.60,'Own\nnote',16,ha='center',va='center',color=MUTED)
box(ax,checks,5.4,3.55,8.5,1.03,'Code carries the actual votes forward\nSender + proposal ID + decision; no replacement by the expected vote','code',16.5)
arrow(ax,[(7.25,5.41),(7.25,4.62)])
arrow(ax,[(12.05,4.62),(12.05,5.41)])
box(ax,checks,.6,1.48,8.5,1.24,'Own note supplied at READ\nAlready voted: own fields from VOTE\nOtherwise: own fields from FORM','record',16.5)
arrow(ax,[(2.45,5.41),(2.45,2.76)])
arrow(ax,[(5.9,5.41),(5.9,5.00),(4.90,5.00),(4.90,3.06),(6.1,3.06),(6.1,2.76)])
arrow(ax,[(9.14,2.21),(14.13,2.21),(14.13,6.20),(13.94,6.20)])
text(ax,.6,1.20,'Matched approval-state comparison (TAR01)',17,'bold')
text(ax,.6,.80,'Reuse a fixed FORM own note and proposal; vary one received vote: MISSING / HOLD / ACCEPT.',16,color=MUTED)
text(ax,.6,.42,'Evaluate each READ response. Generated readout states are not fed into later stages.',16,color=MUTED)
save(fig,ax,checks,'figure-01-information-flow-en-v1')

fig,ax,checks=canvas(8.5)
text(ax,.5,8.10,'An incorrect vote can be read correctly',24,'bold')
text(ax,.5,7.61,'TB01 · Case T02, first technical replicate · Different stages use different reference evidence.',16,color=MUTED)
box(ax,checks,.7,5.56,5.8,1.38,'C’s own experience\nPAPER: 26 / 40     DIGITAL: 29 / 40\nOwn recommendation: DIGITAL','record',16.5)
box(ax,checks,8.0,5.56,5.8,1.38,'Two joint candidates\nA PAPER / B DIGITAL / C PAPER: 90\nA PAPER / B PAPER / C DIGITAL: 84','record',16.5)
box(ax,checks,.7,2.90,5.8,1.32,'C votes HOLD on the 90 proposal\nOwn recommendation + evidence: correct\nVote: incorrect for the numerical objective','model',16.5)
arrow(ax,[(3.6,5.52),(3.6,4.26)])
arrow(ax,[(10.9,5.52),(10.9,4.95),(5.9,4.95),(5.9,4.26)])
box(ax,checks,8.0,2.90,5.8,1.32,'Actual received votes\nA: ACCEPT     B: ACCEPT     C: HOLD\nThe recorded HOLD is carried forward','code',16.5)
arrow(ax,[(6.54,3.56),(7.96,3.56)])
box(ax,checks,.7,.55,13.1,1.29,'All three readers: C = HOLD; agreement = PENDING; execution = HOLD\nReadout is correct against the received votes. It does not revise the vote.','model',16.5)
arrow(ax,[(10.9,2.86),(10.9,1.88)])
save(fig,ax,checks,'figure-02-actual-vote-readout-en-v1')
(OUT/'layout-checks-en-v1.json').write_text(json.dumps(fit_checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'figures':len(fit_checks),'formats':['SVG','PNG'],'png_dpi':300,'layout':'PASS'}))
