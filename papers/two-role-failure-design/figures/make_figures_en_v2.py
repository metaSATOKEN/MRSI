"""Draw the two figures for the multi-role design synthesis."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path as PlotPath

OUT = Path(__file__).resolve().parent
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 13,
                     'svg.fonttype': 'path', 'svg.hashsalt': 'multi-role-design-en-v2',
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
save(fig,ax,checks,edges,'fig01-record-trace-en-v2')

fig,ax,checks,edges=canvas(12.6,16.0,'Separate actual approval from permission to execute',
    'Proposed architecture  |  Assess the proposal and preserve each received vote.')
box(ax,checks,3.4,14.15,5.8,.78,'Input materials: target, origin ID, revision',size=14)
box(ax,checks,4.0,12.95,4.6,.74,'LLM update proposal','model',14)
box(ax,checks,3.4,11.68,5.8,.84,'Pre-storage checks\nSelect and copy designated fields','code',14)
box(ax,checks,3.4,10.4,5.8,.84,'Per-role private states\nand shared observations',size=14)
box(ax,checks,3.4,9.1,5.8,.84,'Own-experience summaries\nand joint candidate table','code',14)
box(ax,checks,.65,7.62,4.,.84,"Each role's own judgment",'model',14)
box(ax,checks,5.3,7.62,4.,.84,'Joint proposal\nTarget and version','model',14)
box(ax,checks,.65,6.2,4.,.84,'Votes expressed by each role','model',13.7)
box(ax,checks,7.7,5.58,4.25,1.05,'Task assessment\nCandidates, resources, totals','code',14)
box(ax,checks,.65,4.75,5.45,1.06,'Original votes + per-role states\nMISSING / HOLD / ACCEPT',size=14)
box(ax,checks,2.4,3.38,3.7,.85,'Group agreement\nunder the specified rule','code',13.7)
box(ax,checks,7.7,3.38,4.25,.85,'Controller decision:\nauthorize execution?','code',14)
box(ax,checks,.65,1.86,5.45,1.0,'Unresolved items\nand target-specific reasons','hold',14)
box(ax,checks,7.7,1.86,4.25,1.0,'Use the authorized\njoint assignment','model',14)
box(ax,checks,3.45,.42,6.0,.84,'Evaluate own judgment, votes,\nagreement, and execution separately','code',14)

def e(s,t,ps):edge(ax,edges,s,t,ps)
e('I','U',[(6.3,14.12),(6.3,13.72)])
e('U','W',[(6.3,12.92),(6.3,12.55)])
e('I','W',[(3.37,14.54),(2.9,14.54),(2.9,12.10),(3.37,12.10)])
e('W','P',[(6.3,11.65),(6.3,11.27)])
e('W','H',[(3.37,12.10),(.4,12.10),(.4,2.38),(.62,2.38)])
e('P','D',[(6.3,10.37),(6.3,9.97)])
e('D','J',[(4.1,9.07),(4.1,8.76),(2.65,8.76),(2.65,8.49)])
e('D','Q',[(7.3,9.07),(7.3,8.49)])
e('J','V',[(2.65,7.59),(2.65,7.07)])
e('Q','V',[(5.27,8.04),(4.95,8.04),(4.95,6.62),(4.68,6.62)])
e('Q','C',[(9.33,8.04),(9.82,8.04),(9.82,6.66)])
e('D','C',[(9.23,9.52),(11.52,9.52),(11.52,6.66)])
e('V','L',[(2.65,6.17),(2.65,5.84)])
e('Q','L',[(7.3,7.59),(7.3,5.28),(6.13,5.28)])
e('L','A',[(4.25,4.72),(4.25,4.26)])
e('C','G',[(9.82,5.55),(9.82,4.26)])
e('A','G',[(6.13,3.80),(7.67,3.80)])
e('G','R',[(9.82,3.35),(9.82,2.89)])
label(ax,10.75,3.11,'Conditions met',11.7)
e('G','H',[(7.67,3.65),(6.78,3.65),(6.78,2.36),(6.13,2.36)])
label(ax,6.8,3.14,'Not met',11.4)
e('L','H',[(1.32,4.72),(1.32,2.89)])
# The own-judgment edge follows the outer margin to keep both central paths legible.
e('J','R',[(.62,8.04),(.16,8.04),(.16,1.56),(12.35,1.56),(12.35,2.36),(11.98,2.36)])
label(ax,8.1,1.57,'Retain own judgment',11.4)
e('H','E',[(3.37,1.83),(3.37,1.0),(3.42,1.0)])
e('R','E',[(9.82,1.83),(9.82,.84),(9.48,.84)])
ax.text(.65,.50,'Approval facts remain intact\neven when execution is deferred.',fontsize=11.4,color=MUTED,linespacing=1.4)
save(fig,ax,checks,edges,'fig02-reference-architecture-en-v2')
(OUT/'layout-checks-en-v2.json').write_text(json.dumps(REPORT,indent=2)+'\n')
print('Saved two 300-dpi PNGs and SVGs; containment checks passed.')
