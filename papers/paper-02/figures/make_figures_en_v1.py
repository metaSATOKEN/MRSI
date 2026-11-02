"""Two English diagrams for paper 2, corresponding to finalized Japanese v0.4.

Offline drawing only. No model calls, rescoring, or PDF generation.
Requires matplotlib. Run: python3 make_figures_en_v1.py
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path as MPath

OUT = Path(__file__).resolve().parent
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 13,
                     'svg.fonttype': 'path', 'svg.hashsalt': 'npp-paper02-en-v1',
                     'savefig.facecolor': 'white'})
INK = '#213547'
MUTED = '#536574'
EDGE = '#8b9aa6'
COLORS = {'record': '#f1f4f7', 'model': '#e4eef9', 'code': '#e3f1e9', 'diagnostic': '#fff2dc'}
fit_checks = []

def canvas(h):
    fig, ax = plt.subplots(figsize=(14.5, h))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.set(xlim=(0, 14.5), ylim=(0, h)); ax.axis('off')
    return fig, ax, []

def text(ax, x, y, content, size=13, weight='normal', ha='left', va='top', color=INK):
    return ax.text(x, y, content, fontsize=size, color=color, weight=weight,
                   ha=ha, va=va, linespacing=1.4)

def box(ax, checks, x, y, w, h, content, kind='record', size=13):
    patch = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.08',
                          facecolor=COLORS[kind], edgecolor=EDGE, linewidth=1.1)
    ax.add_patch(patch)
    t = text(ax, x+w/2, y+h/2, content, size=size, ha='center', va='center')
    checks.append((patch, t, content))

def arrow(ax, points):
    # Corners and endpoints are explicit, preventing automatic routing through boxes.
    path = MPath(points, [MPath.MOVETO]+[MPath.LINETO]*(len(points)-1))
    ax.add_patch(FancyArrowPatch(path=path, arrowstyle='-|>', mutation_scale=15,
                                linewidth=1.45, color=MUTED))

def save(fig, ax, checks, name):
    fig.canvas.draw(); renderer = fig.canvas.get_renderer()
    rows = []
    for patch, t, label in checks:
        p = patch.get_window_extent(renderer); b = t.get_window_extent(renderer)
        ok = p.x0+5 < b.x0 and b.x1 < p.x1-5 and p.y0+4 < b.y0 and b.y1 < p.y1-4
        rows.append({'text': label, 'inside_box': bool(ok)})
    fit_checks.append({'figure': name, 'checks': rows})
    assert all(x['inside_box'] for x in rows), rows
    fig.savefig(OUT/(name+'.png'), dpi=300, metadata={'Software': 'NPP paper 2 figure source'})
    fig.savefig(OUT/(name+'.svg'), metadata={'Date': None, 'Creator': 'NPP paper 2 figure source'})
    plt.close(fig)

fig, ax, checks = canvas(10.1)
text(ax, .35, 9.78, 'Update control and subsequent use', 21, 'bold')
text(ax, .35, 9.35, 'One role shown. Each model call uses a fresh context.', 13, color=MUTED)
for x, label, kind in [(8.4,'LLM','model'),(10.25,'Code','code'),(12.0,'Record','record')]:
    box(ax, checks, x, 9.15, 1.55, .40, label, kind, 12)
text(ax, .35, 8.85, 'A  UPDATE AND SAVE', 13, 'bold')
box(ax, checks, 4.1, 7.55, 6.3, .95, 'Current input\nPreviously saved notes + current notice')
box(ax, checks, .35, 5.9, 3.95, 1.15, 'Generate\nan update proposal', 'model', 14)
box(ax, checks, 10.2, 5.9, 3.95, 1.15, 'Select latest rows\nwithin each observer\nfrom the current input only', 'code', 13)
box(ax, checks, .35, 4.55, 3.95, .90, 'Validate structure', 'code', 14)
box(ax, checks, 5.0, 4.15, 4.5, 1.25, 'Assemble notes\nKeep model-written customer field\nCopy rows in controlled fields', 'code', 12.5)
box(ax, checks, 5.0, 2.9, 4.5, .82, 'Actual saved notes', 'record', 14)
arrow(ax, [(5.5,7.55),(5.5,7.3),(2.325,7.3),(2.325,7.07)])
arrow(ax, [(9,7.55),(9,7.3),(12.175,7.3),(12.175,7.07)])
arrow(ax, [(2.325,5.9),(2.325,5.47)])
arrow(ax, [(4.32,5.0),(4.65,5.0),(4.98,4.8)])
arrow(ax, [(12.175,5.9),(12.175,4.775),(9.52,4.775)])
arrow(ax, [(7.25,4.15),(7.25,3.74)])
text(ax, .35, 3.9, 'Original response and\nsaved artifact are retained\nseparately.', 12, color=MUTED)
text(ax, .35, 2.55, 'B  REUSE THE SAVED NOTES', 13, 'bold')
box(ax, checks, .35, .9, 3.95, 1.12, 'Next update\nor exchange', 'record', 14)
box(ax, checks, 5.0, .9, 4.5, 1.12, 'Extract shared values and,\nwhen requested, customer\ninformation from saved notes', 'model', 12.5)
box(ax, checks, 10.2, .9, 3.95, 1.12, 'Use the extracted preference\nfor the design; compute the\nchannel from shared values', 'code', 12.5)
arrow(ax, [(7.25,2.9),(7.25,2.25),(2.325,2.25),(2.325,2.04)])
arrow(ax, [(7.25,2.9),(7.25,2.04)])
arrow(ax, [(9.52,1.46),(10.18,1.46)])
text(ax, .35, .48, 'OR01 varies control of own/shared observations. Customer information remains model-written.', 12, color=MUTED)
text(ax, .35, .21, 'Accepted updates shown. SX01 reads shared values only; RU01, SX02 and CU01 also read customer information.', 11.7, color=MUTED)
save(fig, ax, checks, 'fig01-update-control-en-v1')

fig, ax, checks = canvas(9.5)
text(ax, .35, 9.18, 'Saved-note continuity and diagnostic branches', 21, 'bold')
text(ax, .35, 8.72, 'The second cycle continues from actual saved notes, not from manipulated diagnostic inputs.', 13, color=MUTED)
box(ax, checks, .35, 7.05, 3.7, 1.05, 'New initial notes\n8 groups × 2 repetitions', 'record', 13)
box(ax, checks, 4.7, 7.05, 4.35, 1.05, 'First-cycle updates (SX01)\nUpdate → exchange → old notice', 'code', 12.5)
box(ax, checks, 9.7, 7.05, 4.45, 1.05, '32 saved role-specific note sets\n2 roles × 8 groups × 2 repetitions', 'record', 12.5)
arrow(ax, [(4.07,7.575),(4.68,7.575)])
arrow(ax, [(9.07,7.575),(9.68,7.575)])
# Three outgoing paths from the same artifacts.
box(ax, checks, 9.7, 5.4, 4.45, .95, 'First-cycle readout (SX01)\nShared information', 'model', 13)
box(ax, checks, 4.7, 3.55, 4.35, 1.4, 'Selective-use diagnostic (RU01)\nUnchanged / preference only /\nobservations only / both\nReadout after input manipulation', 'diagnostic', 12.5)
box(ax, checks, .35, 3.55, 3.7, 1.4, 'Second-cycle updates (SX02)\nFurther update\n→ exchange → old notice', 'code', 12.5)
box(ax, checks, .35, 2.05, 3.7, .95, 'Second-cycle readout\nCustomer + shared information', 'model', 12.5)
arrow(ax, [(11.925,7.05),(11.925,6.37)])
arrow(ax, [(11.925,6.7),(2.2,6.7),(2.2,4.97)])
arrow(ax, [(6.875,6.7),(6.875,4.97)])
arrow(ax, [(2.2,3.55),(2.2,3.02)])
text(ax, 4.9, 3.13, 'These manipulated notes do not\nfeed the second cycle.', 12.5, color=MUTED)
ax.plot([.35,14.15],[1.65,1.65],color='#bac5cd',linewidth=1.0)
text(ax, .35, 1.48, 'SEPARATE INITIAL STATES', 12, 'bold')
box(ax, checks, .35, .25, 4.35, .92, 'New customer-update cases\n8 groups × 2 repetitions', 'record', 13)
box(ax, checks, 5.65, .25, 8.5, .92, 'Customer-update diagnostic (CU01)\nNew preference → old notice → customer + shared readout', 'diagnostic', 13)
arrow(ax, [(4.72,.71),(5.63,.71)])
save(fig, ax, checks, 'fig02-study-connections-en-v1')
(OUT/'layout-checks-en-v1.json').write_text(json.dumps(fit_checks, indent=2)+'\n')
print(json.dumps({'figures':len(fit_checks),'all_box_text_fits':all(c['inside_box'] for f in fit_checks for c in f['checks']),'formats':['SVG','PNG'],'png_dpi':300}))
