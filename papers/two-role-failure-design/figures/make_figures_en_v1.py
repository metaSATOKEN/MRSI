"""Redraw the two Japanese v0.4 Mermaid graphs; PNG/SVG only, no new data."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path as PlotPath

OUT = Path(__file__).resolve().parent
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 13,
                     'svg.fonttype': 'path', 'svg.hashsalt': 'two-role-design-en-v1',
                     'savefig.facecolor': 'white'})
INK = '#20354a'
MUTED = '#536879'
COLORS = {'record': '#f0f4f7', 'model': '#e6eef8', 'code': '#e5f2ec', 'hold': '#fff1d9'}
REPORT = []


def canvas(w, h, title, subtitle):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.set(xlim=(0, w), ylim=(0, h)); ax.axis('off')
    ax.text(.45, h-.33, title, color=INK, fontsize=19, weight='bold', va='top')
    ax.text(.45, h-.82, subtitle, color=MUTED, fontsize=12.3, va='top')
    return fig, ax, [], []


def box(ax, checks, x, y, w, h, label, kind='record', size=13.5):
    patch = FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.015,rounding_size=0.07',
                          facecolor=COLORS[kind], edgecolor='#8da0ae', linewidth=1.05)
    ax.add_patch(patch)
    t = ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=size,
                linespacing=1.32,color=INK)
    checks.append((patch,t))


def edge(ax, edges, source, target, points, dashed=False):
    path = PlotPath(points,[PlotPath.MOVETO]+[PlotPath.LINETO]*(len(points)-1))
    ax.add_patch(FancyArrowPatch(path=path,arrowstyle='-|>',mutation_scale=15,
                               linewidth=1.2,linestyle=(0,(3,3)) if dashed else '-',color=MUTED))
    edges.append([source,target])


def label(ax, x, y, text, size=11.5):
    ax.text(x,y,text,ha='center',va='center',fontsize=size,color=MUTED,
            bbox={'facecolor':'white','edgecolor':'none','pad':1})


def save(fig,ax,checks,edges,stem):
    fig.canvas.draw(); renderer=fig.canvas.get_renderer(); results=[]
    for patch,t in checks:
        p=patch.get_window_extent(renderer); b=t.get_window_extent(renderer)
        results.append({'text':t.get_text(),'inside_box':bool(p.x0+3<b.x0 and b.x1<p.x1-3 and p.y0+3<b.y0 and b.y1<p.y1-3)})
    for t in ax.texts:
        b=t.get_window_extent(renderer); frame=fig.bbox
        results.append({'text':t.get_text(),'inside_canvas':bool(frame.contains(b.x0,b.y0) and frame.contains(b.x1,b.y1))})
    assert all(r.get('inside_box',r.get('inside_canvas')) for r in results),results
    fig.savefig(OUT/(stem+'.png'),dpi=300,metadata={'Software':'NPP technical synthesis'})
    fig.savefig(OUT/(stem+'.svg'),metadata={'Date':None,'Creator':'NPP technical synthesis'})
    REPORT.append({'figure':stem,'edges':edges,'layout_checks':results,
                   'size_inches':list(fig.get_size_inches()),'dpi':300})
    plt.close(fig)


fig,ax,checks,edges=canvas(10.2,8.8,'Trace records across stage boundaries',
    'Observation framework  |  Separate generation, saved state, and subsequent use.')
ys=[6.62,5.57,4.52,3.47,2.42,1.37]
nodes=[('I','Input materials + previous saved artifacts','record'),
       ('P','Model-generated proposal','model'),
       ('T','Checks, transformations,\nand storage decisions','code'),
       ('S','Actual saved state','record'),
       ('N','Input supplied to the next stage','record'),
       ('U','Subsequent judgment and use','model')]
for y,(key,content,kind) in zip(ys,nodes):
    box(ax,checks,.5,y,5.25,.76,content,kind,13.3)
for i in range(5):
    edge(ax,edges,nodes[i][0],nodes[i+1][0],[(3.125,ys[i]-.025),(3.125,ys[i+1]+.79)])
ax.text(8.0,6.69,'CORRESPONDENCE AUDIT',fontsize=13,weight='bold',ha='center',color=INK)
audit_labels=['Retain the raw proposal',
              'Log transformations and\nexecution / inapplicability',
              'Record saved contents',
              'Match input to its parent record',
              'Evaluate for the intended use']
for y,(key,_,_),content in zip(ys[1:],nodes[1:],audit_labels):
    box(ax,checks,6.3,y,3.45,.76,content,'record',11.9)
    edge(ax,edges,key,'A',[(5.79,y+.38),(6.27,y+.38)],True)
ax.text(.5,.83,'Solid arrows: material passed onward     Dashed arrows: records used in the audit',
        fontsize=11.7,color=MUTED)
ax.text(.5,.40,'Distinguish a defect inherited from a saved artifact from a new error introduced downstream.',
        fontsize=11.7,color=MUTED)
save(fig,ax,checks,edges,'fig01-record-trace-en-v1')

fig,ax,checks,edges=canvas(11.2,14.5,'Two boundaries: record updates and agreement commitment',
    'Proposed architecture  |  The complete connected system has not been evaluated.')
box(ax,checks,1.35,12.30,7.8,.82,'Input materials\nTarget, origin ID, and revision')
box(ax,checks,2.85,11.00,4.8,.75,'LLM update proposal','model')
box(ax,checks,1.35,9.65,7.8,.90,'Pre-storage checks\nSelect and copy rows in the designated fields','code',14)
box(ax,checks,.9,8.25,3.5,.85,'Separate private states\nfor roles A and B')
box(ax,checks,5.0,8.25,3.5,.85,'Shared observations')
box(ax,checks,.9,6.85,7.6,.85,'Purpose-specific own-experience summaries\nand joint candidate tables','code',14)
box(ax,checks,.9,5.45,3.5,.90,"Each role's own judgment",'model',13.2)
box(ax,checks,5.0,5.45,3.5,.90,'Joint proposal\nand peer response','model')
box(ax,checks,5.125,4.05,3.25,.90,'Common check before\nagreement commitment','code',13.2)
box(ax,checks,1.35,2.65,6.7,.90,'Agreement bound to proposal version,\nevidence, and confirmation','record',14)
box(ax,checks,1.35,1.25,6.7,.85,'Subsequent use for the intended purpose','model',14)
box(ax,checks,1.35,.15,6.7,.65,'Compare actual use with intended use','code',13.5)
box(ax,checks,8.65,6.50,1.70,1.30,'Unresolved\nitems and\nhold reasons','hold',12.6)
edge(ax,edges,'I','U',[(5.25,12.275),(5.25,11.78)])
edge(ax,edges,'U','W',[(5.25,10.975),(5.25,10.58)])
edge(ax,edges,'I','W',[(1.32,12.71),(.45,12.71),(.45,10.10),(1.32,10.10)])
edge(ax,edges,'W','P',[(2.65,9.625),(2.65,9.13)])
edge(ax,edges,'W','S',[(6.75,9.625),(6.75,9.13)])
edge(ax,edges,'W','H',[(9.18,10.10),(9.50,10.10),(9.50,7.83)])
edge(ax,edges,'P','D',[(2.65,8.225),(2.65,7.73)])
edge(ax,edges,'S','D',[(6.75,8.225),(6.75,7.73)])
edge(ax,edges,'D','J',[(2.65,6.825),(2.65,6.38)])
edge(ax,edges,'D','Q',[(6.75,6.825),(6.75,6.38)])
edge(ax,edges,'J','Q',[(4.43,5.90),(4.97,5.90)])
edge(ax,edges,'Q','G',[(6.75,5.425),(6.75,4.98)])
edge(ax,edges,'G','A',[(6.75,4.025),(6.75,3.58)])
label(ax,7.20,3.79,'Pass')
edge(ax,edges,'G','H',[(8.405,4.50),(9.50,4.50),(9.50,6.47)])
label(ax,9.50,4.95,'Hold')
edge(ax,edges,'A','R',[(4.70,2.625),(4.70,2.13)])
edge(ax,edges,'J','R',[(.87,5.90),(.45,5.90),(.45,1.675),(1.32,1.675)])
edge(ax,edges,'H','R',[(10.38,7.15),(10.70,7.15),(10.70,1.675),(8.08,1.675)])
edge(ax,edges,'R','V',[(4.70,1.225),(4.70,.83)])
ax.text(8.50,3.00,'Hold state is carried\nforward to delimit\nusable work.\nIt does not authorize\nthe deferred task.',
        fontsize=11.5,color=MUTED,ha='left',va='top',linespacing=1.4)
save(fig,ax,checks,edges,'fig02-reference-architecture-en-v1')
(OUT/'layout-checks-en-v1.json').write_text(json.dumps(REPORT,indent=2)+'\n')
print('Saved two PNG/SVG figures; all text-containment checks passed.')
