# 06_visualise.py — publication figures from hex_master.gpkg (presentation only)
# READS : ~/nt_exposure/data/hex_master.gpkg (+ nt_boundary.gpkg)
# WRITES: ~/nt_exposure/figures/*.png
import geopandas as gpd, pandas as pd, numpy as np, os, matplotlib as mpl
mpl.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.patches import Patch
import matplotlib.cm as cm

# ============================== CONFIG ==============================
H=os.path.expanduser
DATA=H("~/nt_exposure/data/"); FIGS=H("~/nt_exposure/figures/")
BOUNDARY=os.path.join(DATA,"nt_boundary.gpkg")
MASTER=os.path.join(DATA,"hex_master.gpkg")
ROPER_GDB=H("~/roper_overlay/data/Datasets/ESRI/MTF_Roper.gdb")
CRS=3577
DPI=300
FIGSIZE=(7,7)
BOUND_KW=dict(color="#222222", linewidth=0.6, zorder=5)
FONT={"font.size":9,"axes.titlesize":12,"axes.titleweight":"bold",
      "figure.dpi":150,"savefig.dpi":DPI,"savefig.bbox":"tight","axes.edgecolor":"#444"}
LEGEND_KW=dict(loc="lower left", fontsize=7, frameon=True, framealpha=0.9)

# per-layer spec: col, title, cmap, mode ('quantile'|'bins'), bins (for 'bins'), file, provisional
LAYERS=[
 dict(col="conv_score", title="Convertibility", cmap="YlOrBr", mode="bins",
      bins=[0,0.15,0.50,0.99,1.001], file="fig_convertibility.png"),
 dict(col="sig_socs", title="Significance — SOCS", cmap="Greens", mode="bins",
      bins=[0,0.001,0.37,1.001], file="fig_significance_socs.png"),
 dict(col="sig_landsys", title="Significance — Land Systems", cmap="BuGn", mode="quantile",
      k=6, file="fig_significance_landsys.png"),
 dict(col="prot_frac", title="Protection (fraction)", cmap="Blues", mode="bins",
      bins=[0,0.001,0.25,0.75,1.001], file="fig_protection.png"),
 dict(col="exposure_prov", title="Conservation Exposure", cmap="magma", mode="quantile",
      k=6, file="fig_exposure_provisional.png", provisional=True),
]
CORR_COLS=["conv_score","sig_socs","sig_landsys","prot_frac"]
DIST_COLS=["conv_score","sig_socs","sig_landsys","prot_frac","exposure_prov"]
# ===================================================================

os.makedirs(FIGS, exist_ok=True)
plt.rcParams.update(FONT)
m=gpd.read_file(MASTER).to_crs(CRS)
bound=gpd.read_file(BOUNDARY).to_crs(CRS) if os.path.exists(BOUNDARY) else None
print("master cols:", [c for c in m.columns if c!="geometry"])
print("boundary:", "loaded" if bound is not None else "MISSING")

def fmt(a,b):
    # proper half-open interval notation; collapse trivial upper sentinel
    b=min(b,1.0)
    return f"[{a:.2f}, {b:.2f})" if b<1.0 else f"[{a:.2f}, 1.00]"

def basemap(ax):
    if bound is not None: bound.boundary.plot(ax=ax, **BOUND_KW)
    ax.set_axis_off()

def edges_quantile(s,k):
    qs=np.linspace(0,1,k+1)
    e=np.unique(np.quantile(s.dropna(),qs))
    if len(e)<3: e=np.unique(np.r_[s.min(),s.max()])  # degenerate fallback
    return e

def draw(spec):
    col=spec["col"]
    if col not in m.columns: print("skip:",col); return
    s=m[col]
    if spec["mode"]=="bins":
        edges=np.array(spec["bins"],float)
    else:
        edges=edges_quantile(s,spec.get("k",6))
    ncls=len(edges)-1
    cmap=plt.get_cmap(spec["cmap"], ncls)
    norm=BoundaryNorm(edges, ncls)
    fig,ax=plt.subplots(figsize=FIGSIZE)
    m.plot(column=col, cmap=cmap, norm=norm, ax=ax, linewidth=0)
    basemap(ax)
    # legend as discrete patches with interval labels
    handles=[Patch(facecolor=cmap(i), edgecolor="none",
                   label=fmt(edges[i],edges[i+1])) for i in range(ncls)]
    leg=ax.legend(handles=handles, title=col, **LEGEND_KW)
    leg.get_title().set_fontsize(8)
    ax.set_title(spec["title"]+("  [PROVISIONAL]" if spec.get("provisional") else ""))
    fig.savefig(os.path.join(FIGS,spec["file"])); plt.close(fig)
    print("wrote",spec["file"],"| classes:",ncls,"| edges:",np.round(edges,3).tolist())

for spec in LAYERS: draw(spec)

# distributions
dc=[c for c in DIST_COLS if c in m.columns]
fig,axes=plt.subplots(1,len(dc),figsize=(3.2*len(dc),3))
if len(dc)==1: axes=[axes]
for ax,c in zip(axes,dc):
    ax.hist(m[c].dropna(),bins=40,color="#3a7a5a",edgecolor="white",linewidth=0.3)
    ax.set_title(c+("  [PROV]" if c=="exposure_prov" else ""),fontsize=10); ax.set_yticks([])
fig.suptitle("Component distributions",fontweight="bold")
fig.savefig(os.path.join(FIGS,"fig_distributions.png")); plt.close(fig); print("wrote fig_distributions.png")

# correlation heatmap
cc=[c for c in CORR_COLS if c in m.columns]; corr=m[cc].corr()
fig,ax=plt.subplots(figsize=(5,4.2))
im=ax.imshow(corr,cmap="RdBu_r",vmin=-1,vmax=1)
ax.set_xticks(range(len(cc))); ax.set_xticklabels(cc,rotation=45,ha="right",fontsize=8)
ax.set_yticks(range(len(cc))); ax.set_yticklabels(cc,fontsize=8)
for i in range(len(cc)):
    for j in range(len(cc)):
        v=corr.iloc[i,j]; ax.text(j,i,f"{v:.2f}",ha="center",va="center",
            color="white" if abs(v)>0.5 else "#222",fontsize=8)
fig.colorbar(im,fraction=0.046,pad=0.04); ax.set_title("Cross-component correlation")
fig.savefig(os.path.join(FIGS,"fig_correlation.png")); plt.close(fig); print("wrote fig_correlation.png")

# Roper extent
if os.path.exists(ROPER_GDB):
    from pyogrio import list_layers
    lyr=[r[0] for r in list_layers(ROPER_GDB) if "risk" in r[0].lower()]
    if lyr:
        r=gpd.read_file(ROPER_GDB,layer=lyr[0]).to_crs(CRS); r["geometry"]=r.buffer(0)
        ext=gpd.GeoDataFrame(geometry=[r.union_all()],crs=CRS)
        hit=gpd.overlay(m[["geometry"]],ext,how="intersection")
        fig,ax=plt.subplots(figsize=FIGSIZE)
        m.plot(ax=ax,color="#eeeeee",linewidth=0)
        if bound is not None: bound.boundary.plot(ax=ax,**BOUND_KW)
        hit.plot(ax=ax,color="#d33333",linewidth=0)
        ax.set_title("Roper validation extent (244 hexes)"); ax.set_axis_off()
        fig.savefig(os.path.join(FIGS,"fig_roper_extent.png")); plt.close(fig); print("wrote fig_roper_extent.png")
print("DONE")
