#!/usr/bin/env python
"""make_figures.py — publication figures from frozen outputs. No new science."""
import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({"font.size":9,"font.family":"sans-serif","axes.spines.top":False,
                 "axes.spines.right":False,"figure.dpi":300})
OUT="figures_paper"; import os; os.makedirs(OUT,exist_ok=True)
R="outputs_roper"; S="outputs_sensitivity"
vj=json.load(open(f"{R}/verdict.json")); sc=json.load(open(f"{R}/spatial_correction.json"))
cf=pd.read_csv(f"{S}/core_fringe_summary.csv").iloc[0]
pers=pd.read_csv(f"{S}/hotspot_persistence.csv")

# --- Fig 1: decomposition forest plot (primary validation result) ---
rows=[("Full exposure","exposure_full"),("Exposure, SOCS removed","exposure_SOCSremoved"),
      ("Convertibility only","convertibility"),("Significance only","significance")]
fig,ax=plt.subplots(figsize=(6.3,2.8))
for i,(lab,key) in enumerate(rows):
    rho,lo,hi=sc["block_ci"][key]
    y=len(rows)-1-i
    ax.plot([lo,hi],[y,y],color="#333",lw=1.4,zorder=2)
    ax.scatter([rho],[y],s=42,color="#1f6f8b",zorder=3,edgecolor="white",linewidth=0.6)
    ax.text(hi+0.015,y,f"ρ={rho:.3f}",va="center",fontsize=8)
ax.axvline(0,color="#bbb",lw=0.9,ls="--",zorder=1)
ax.set_yticks(range(len(rows)));ax.set_yticklabels([r[0] for r in rows][::-1])
ax.set_xlabel("Spearman correlation with expert BIORISK (spatial 95% CI)")
ax.set_xlim(-0.30,0.55)
ax.set_title("Exposure–expert agreement decomposition (n=244; n_eff≈60)",fontsize=9.5)
fig.tight_layout();fig.savefig(f"{OUT}/fig1_decomposition.png",bbox_inches="tight");plt.close(fig)

# --- Fig 2: hotspot persistence distribution (core vs fringe) ---
f10=pers["top10_freq"];ever=f10[f10>0]
fig,ax=plt.subplots(figsize=(6.3,3.0))
ax.hist(ever,bins=np.linspace(0,1,21),color="#8fb8c9",edgecolor="white",linewidth=0.5)
ax.axvspan(0.9,1.0,color="#1f6f8b",alpha=0.12)
ax.axvspan(0.0,0.1,color="#c25b56",alpha=0.10)
ax.set_xlabel("Fraction of 30 construction variants ranking hex in top decile")
ax.set_ylabel("Number of hexes")
ax.set_title("Bimodal hotspot persistence: robust core vs contested fringe",fontsize=9.5)
ax.text(0.95,ax.get_ylim()[1]*0.9,f"core\n{int(cf.always_top10)} hexes\n(all 30)",
        ha="center",fontsize=7.5,color="#1f6f8b")
ax.text(0.05,ax.get_ylim()[1]*0.5,"near-\nzero",ha="center",fontsize=7.5,color="#c25b56")
ax.annotate(f"contested fringe: {int(cf.contested_fringe_10to90)} hexes",
            xy=(0.5,ax.get_ylim()[1]*0.15),ha="center",fontsize=7.5,color="#555")
fig.tight_layout();fig.savefig(f"{OUT}/fig2_persistence.png",bbox_inches="tight");plt.close(fig)

# --- Fig 3: Moran's I (autocorrelation justification) ---
mor=sc["moran"];labels={"biorisk_awm":"BIORISK","exposure_full":"Exposure",
    "convertibility":"Convertibility","significance":"Significance"}
ks=list(labels);vals=[mor[k][0] for k in ks]
fig,ax=plt.subplots(figsize=(4.6,2.8))
ax.barh(range(len(ks)),vals,color="#5b8c85",edgecolor="white")
ax.set_yticks(range(len(ks)));ax.set_yticklabels([labels[k] for k in ks])
for i,v in enumerate(vals): ax.text(v+0.01,i,f"{v:.2f}",va="center",fontsize=8)
ax.set_xlabel("Moran's I (all p=0.001)");ax.set_xlim(0,0.85)
ax.set_title("Spatial autocorrelation across layers",fontsize=9.5)
fig.tight_layout();fig.savefig(f"{OUT}/fig3_morans_i.png",bbox_inches="tight");plt.close(fig)
print("wrote fig1_decomposition, fig2_persistence, fig3_morans_i ->",OUT)
