"""English v0.2 terminology: origin ID consistently names origin_id. Layout and observations retained."""
"""English figure edition, translated from make_e1_flow_v10.py; source observations unchanged."""
"""E1 workflow, drawn from the fixed design. No experimental data generated."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
OUT=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'svg.fonttype':'path','savefig.facecolor':'white'})
fig,ax=plt.subplots(figsize=(14,8.2))
ax.set(xlim=(0,14),ylim=(0,8.2));ax.axis('off')
ink='#203647';blue='#e6eff9';green='#e5f3eb';gray='#f0f2f4'
def box(x,y,w,h,text,fill=blue,size=12):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.08,rounding_size=0.08',lw=1,edgecolor='#93a1ad',facecolor=fill))
 ax.text(x+w/2,y+h/2,text,ha='center',va='center',color=ink,fontsize=size,linespacing=1.6)
def arrow(a,b,label=None,dashed=False):
 ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=15,lw=1.3,color='#536c7c',linestyle='--' if dashed else '-'))
 if label:ax.text((a[0]+b[0])/2,(a[1]+b[1])/2+.18,label,ha='center',fontsize=10,color=ink,bbox={'facecolor':'white','edgecolor':'none','pad':2})
ax.text(.3,7.9,'Figure 1  Two storage methods from identical inputs',fontsize=18,color=ink,weight='bold',va='top')
ax.text(.3,7.35,'E1, one role shown. Initial materials match; instructions and output schemas differ.',fontsize=11.5,color='#526270')
box(.35,3.05,2.5,2.5,'Initial materials\nOwn private note\nOwn shared copy\nPartner shared copy',gray)
ax.text(3.65,6.85,'REWRITE',fontsize=14,color=ink,weight='bold')
box(3.65,5.4,3,1.15,'Model writes\nPrivate note, shared rows,\nand evidence references',size=11)
box(7.65,5.4,2,1.15,'Save the\ngenerated notes',gray)
box(10.5,5.4,3,1.15,'Decision in a fresh context\nDog/cat, paper/digital,\nand provenance',size=11)
arrow((2.95,5.1),(3.55,5.98));arrow((6.75,5.98),(7.55,5.98));arrow((9.75,5.98),(10.4,5.98))
ax.text(3.65,4.7,'SELECT + copy',fontsize=14,color=ink,weight='bold')
box(3.65,3.05,3,1.3,'Model selects shared rows\nand writes private note\nand evidence references',size=11)
box(3.65,1.4,3,1,'Controller copies all fields\nof selected shared rows only',green,11)
box(7.65,2.35,2,1.5,'Save private note\nand copied\nshared rows',gray,11)
box(10.5,2.35,3,1.5,'Decision in a fresh context\nDog/cat, paper/digital,\nand provenance',size=11)
arrow((2.95,3.7),(3.55,3.7));arrow((5.15,2.95),(5.15,2.5),'Row locations')
arrow((6.75,3.72),(7.55,3.72),'Private note',True)
arrow((6.75,1.95),(7.55,2.8));arrow((9.75,3.1),(10.4,3.1))
ax.text(.35,2.55,'Fresh context for each call.\nThe partner\'s customer record\nis not supplied.',fontsize=10.5,color=ink,va='top',linespacing=1.7)
box(.35,.22,13.15,.68,'Both methods pass actual saved notes onward. Evidence references are saved separately, not passed to the next call.',gray,11)
for ext in ('png','svg'):fig.savefig(OUT/f'fig01-e1-flow-en-v2.{ext}',dpi=180,bbox_inches='tight',pad_inches=.16)
plt.close(fig)
print('Wrote E1 flow: PNG and SVG.')

# Translate the existing two-case trace without changing its observations.
fig,ax=plt.subplots(figsize=(14,8.2))
ax.set(xlim=(0,14),ylim=(0,8.2));ax.axis('off')
ax.text(.3,7.9,'Figure 2  Incorrect provenance persists alongside correct decisions',fontsize=18,color=ink,weight='bold',va='top')
ax.text(.3,7.35,'Separate trials using the same known materials; not a correction and rerun of a single error.',fontsize=11.5,color='#526270')
ax.text(.4,6.7,'Further update cycle (SM02): a stale origin ID is retained',fontsize=14,color=ink,weight='bold')
box(.4,4.9,3.6,1.35,'Input observation for A\nPaper NOT_ALL / digital ALL, rev. 3\nOrigin ID: SM2G3A',size=11)
box(5.1,4.9,3.6,1.35,'Saved observation for A\nCorrect values and revision\nOrigin ID: SM3A (stale)','#fce9e5',11)
box(9.8,4.9,3.6,1.35,'Both probes: DOG / DIGITAL\nCorrect decisions\nInherited origin ID: SM3A','#fce9e5',11)
arrow((4.1,5.575),(5,5.575));arrow((8.8,5.575),(9.7,5.575))
ax.text(.4,4.1,'Exploratory method comparison (RC01): an ID absent from the input',fontsize=14,color=ink,weight='bold')
box(.4,1.4,3.6,2,'Same pre-integration materials\nfor both methods\nCorrect origin ID: SM2G3A',size=11)
box(5.1,2.7,3.6,.95,'REWRITE\nOrigin ID: SM3G3A (not in input)','#fce9e5',11)
box(9.8,2.7,3.6,.95,'Correct: DOG / DIGITAL\nInherited origin ID: SM3G3A','#fce9e5',11)
box(5.1,1,3.6,.95,'SELECT + copy\nOrigin ID: SM2G3A (correct)',green,11)
box(9.8,1,3.6,.95,'Correct: DOG / DIGITAL\nCorrect origin ID: SM2G3A',green,11)
arrow((4.1,2.9),(5,3.175));arrow((4.1,1.8),(5,1.475))
arrow((8.8,3.175),(9.7,3.175));arrow((8.8,1.475),(9.7,1.475))
ax.text(.4,.3,'One affected group per trial. Inheritance of the same incorrect ID is not counted as a new independent ID error.',fontsize=11,color=ink)
for ext in ('png','svg'):fig.savefig(OUT/f'fig02-provenance-trace-en-v2.{ext}',dpi=180,bbox_inches='tight',pad_inches=.16)
plt.close(fig)
print('Wrote provenance trace: PNG and SVG.')
