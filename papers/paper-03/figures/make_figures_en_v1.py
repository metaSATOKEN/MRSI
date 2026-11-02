"""English figures for paper 3, based on finalized Japanese v0.2.

Offline matplotlib diagrams; no model calls, rescoring, or PDF generation.
Run with a Python environment containing matplotlib.
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
                     'svg.fonttype': 'path', 'svg.hashsalt': 'npp-paper03-en-v1',
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
    fig.savefig(OUT/(stem+'.png'),dpi=300,metadata={'Software':'NPP paper 3 figure source'})
    fig.savefig(OUT/(stem+'.svg'),metadata={'Date':None,'Creator':'NPP paper 3 figure source'})
    plt.close(fig)

fig,ax,checks=canvas(11.2)
text(ax,.45,10.84,'Execution paths and timing of computational support',21,'bold')
text(ax,.45,10.36,'ST01 / ST02  ·  Generated records are carried forward between fresh-context model calls.',13,color=MUTED)
box(ax,checks,1.0,9.20,5.95,.72,'Observations from roles A and B','record',14)
box(ax,checks,1.0,7.97,5.95,.85,"LLM · Form each role's own judgment\nSave the actual response",'model',14)
box(ax,checks,1.0,6.66,5.95,.85,'Researcher-fixed initial proposal\nOptimal / suboptimal / resource-violating','record',13.5)
box(ax,checks,1.0,5.34,5.95,.85,'LLM · Confirm the joint proposal\nACCEPT / COUNTER / HOLD','model',14)
box(ax,checks,1.0,3.62,5.95,.85,'LLM · Recheck once\nAccept or hold the counterproposal','model',14)
box(ax,checks,1.0,2.20,5.95,.82,'Save actual role-specific and joint records','record',13.5)
box(ax,checks,1.0,.72,5.95,.96,'LLM · Subsequent use by both roles\nOwn recommendation + agreed allocation\nDefer the joint task if no agreement exists','model',12.5)
for bottom,top in [(9.20,8.82),(7.97,7.51),(6.66,6.19),(3.62,3.02),(2.20,1.68)]:
    arrow(ax,[(3.975,bottom-.03),(3.975,top+.04)])
arrow(ax,[(3.975,5.31),(3.975,4.51)])
text(ax,4.18,4.94,'COUNTER only',12.5,va='center',color=MUTED)
arrow(ax,[(6.99,5.765),(7.62,5.765),(7.62,2.61),(6.99,2.61)])
text(ax,7.40,4.18,'ACCEPT / HOLD',12.5,ha='center',va='center',rotation=90,color=MUTED)
text(ax,8.20,9.84,'CODE-SUPPLIED EVIDENCE',14,'bold')
text(ax,8.20,9.36,'Own-experience summary',15,'bold')
x0,y0=8.20,8.37
widths=[2.15,1.62,1.62]; rows=[['Stage','LATE','EARLY'],['Formation','—','Supplied'],['Confirmation','—','Supplied'],['Recheck','—','Supplied'],['Use','Supplied','Supplied']]
for i,row in enumerate(rows):
    xx=x0; yy=y0-i*.61
    for j,(content,w) in enumerate(zip(row,widths)):
        ax.add_patch(Rectangle((xx,yy),w,.61,facecolor=COLORS['code'] if i==0 or content=='Supplied' else 'white',edgecolor='#b8c5bf',linewidth=.75))
        text(ax,xx+w/2,yy+.305,content,12.4,'bold' if i==0 else 'normal',ha='center',va='center')
        xx+=w
box(ax,checks,8.20,3.80,5.39,1.40,'Joint candidate totals\nBoth conditions: confirmation + recheck\nNot supplied at subsequent use','code',12.5)
text(ax,8.20,3.05,'Recheck is conditional.',14,'bold')
text(ax,8.20,2.65,'Only a counterproposal activates it.\nAcceptance of an initial proposal\nbypasses this stage.',13,color=MUTED)
text(ax,.45,.30,'Separate constructed-counterproposal diagnostics do not feed the execution paths shown here.',12,color=MUTED)
save(fig,ax,checks,'fig01-support-timing-en-v1')

fig,ax,checks=canvas(8.55)
text(ax,.45,8.18,'Two separate panels of fixed-input repetitions',21,'bold')
text(ax,.45,7.72,'JR01  ·  Original ST02 inputs are replayed; new formation outputs are not passed to confirmation.',12.5,color=MUTED)
ax.plot([7.25,7.25],[1.58,7.28],color='#a6b3be',linewidth=1.0,linestyle=(0,(4,5)))
for x,title,source,output in [
    (.60,'1 · Judgment formation','32 fixed ST02 inputs\n16 LATE + 16 EARLY\nOriginal experience and summary condition','96 new formation responses\nNew judgments stay within this panel'),
    (7.85,'2 · Joint confirmation','48 fixed ST02 confirmation inputs\n24 LATE + 24 EARLY\nIncludes original saved ST02 own notes','144 new confirmation responses\nOriginal own notes remain fixed')]:
    text(ax,x,7.12,title,17,'bold')
    box(ax,checks,x,5.43,6.0,1.14,source,'record',12.5)
    box(ax,checks,x,3.74,6.0,.95,'LLM · Three fresh seeds per input\nSame messages on every repetition','model',14)
    box(ax,checks,x,2.05,6.0,.95,output,'record',13.5)
    arrow(ax,[(x+3,5.39),(x+3,4.73)])
    arrow(ax,[(x+3,3.70),(x+3,3.04)])
text(ax,7.25,1.41,'80 fixed inputs  ×  3 repetitions  =  240 fresh responses',16,'bold',ha='center')
text(ax,7.25,.91,'No new formation-to-confirmation connection.',14,ha='center',color=MUTED)
text(ax,7.25,.49,'No recheck or subsequent-use calls are included in JR01.',13,ha='center',color=MUTED)
save(fig,ax,checks,'fig02-fixed-input-panels-en-v1')
(OUT/'layout-checks-en-v1.json').write_text(json.dumps(fit_checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'figures':len(fit_checks),'formats':['SVG','PNG'],'png_dpi':300,'layout':'PASS'}))
