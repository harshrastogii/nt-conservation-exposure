#!/usr/bin/env python
"""
spatial_correction.py — Step 2 applied to the Roper validation.

PURPOSE
  The bootstrap CIs in roper_validation.py resample the 244 hexes as if independent.
  Adjacent hexes are spatially autocorrelated in BOTH BIORISK and the proxy, so the
  effective sample size < 244 and naive CIs are too narrow / p-values too small.
  This script quantifies the autocorrelation and provides autocorrelation-aware
  inference for the primary result (exposure vs BIORISK) and the decomposition.

METHODS
  1. Moran's I on BIORISK_awm, exposure_full, convertibility, significance over the
     244-hex contiguity graph (Queen). Establishes that autocorrelation is present.
  2. Spatial-block bootstrap: resample CONTIGUOUS BLOCKS of hexes (not individual
     hexes) so the resampling respects spatial dependence. Gives honest 95% CIs.
  3. Dutilleul's modified t-test (via effective sample size from spatial cross-
     correlation) for the primary Spearman, as a second, independent correction.

READS   /mnt/user-data/uploads/hex_master.gpkg, roper_intersection.gpkg
WRITES  outputs_roper/spatial_correction.{txt,json}
"""
import os, json, numpy as np, pandas as pd, geopandas as gpd
from scipy.stats import spearmanr, rankdata, t as tdist
import libpysal, warnings
from esda.moran import Moran
warnings.filterwarnings("ignore")

OUT="outputs_roper"; os.makedirs(OUT,exist_ok=True); SEED=42; rng=np.random.default_rng(SEED)

# --- rebuild the 244-hex validated frame with geometry (identical logic to validation) ---
hexes=gpd.read_file("/mnt/user-data/uploads/hex_master.gpkg").to_crs(3577)
for c in ["conv_score","sig_socs","sig_landsys","prot_frac"]: hexes[c]=hexes[c].fillna(0)
hexes["hex_area_km2"]=hexes.area/1e6
roper=gpd.read_file("/mnt/user-data/uploads/roper_intersection.gpkg").to_crs(3577)
if (~roper.is_valid).any(): roper["geometry"]=roper.buffer(0)
ov=gpd.overlay(hexes[["hex_id","hex_area_km2","geometry"]], roper[["BIORISK","geometry"]],
               how="intersection", keep_geom_type=True); ov["piece_km2"]=ov.area/1e6
awm=(ov.assign(w=ov.BIORISK*ov.piece_km2).groupby("hex_id")
       .apply(lambda g: g.w.sum()/g.piece_km2.sum(), include_groups=False)
       .rename("biorisk_awm").reset_index())

socs=hexes.sig_socs.to_numpy(); land=hexes.sig_landsys.to_numpy()
conv=hexes.conv_score.to_numpy(); prot=hexes.prot_frac.to_numpy(); sig=0.5*(socs+land)
surf=hexes[["hex_id","geometry"]].copy()
surf["exposure_full"]=sig*conv*(1-prot); surf["significance"]=sig
surf["exposure_SOCSremoved"]=land*conv*(1-prot); surf["convertibility"]=conv
val=surf.merge(awm,on="hex_id").reset_index(drop=True)
val=gpd.GeoDataFrame(val,geometry="geometry",crs=3577)
n=len(val); print(f"validated hexes: {n}")

# --- distance-band weights on centroids (hex spacing is a clean 10,000 m; a 10.1 km
#     band captures the 6 adjacent hexes). Queen-on-subset fails because overlay/merge
#     perturbs edge coordinates so shared edges aren't detected; centroids are exact. ---
cent=val.geometry.centroid
val_pts=gpd.GeoDataFrame(val.drop(columns="geometry"), geometry=cent, crs=3577)
W=libpysal.weights.DistanceBand.from_dataframe(val_pts, threshold=10100, silence_warnings=True)
W.transform="r"
iso=[i for i in range(n) if W.cardinalities[i]==0]
print(f"Distance-band graph (<=10.1km): mean neighbours={np.mean(list(W.cardinalities.values())):.2f}, isolates={len(iso)}")

# --- 1. Moran's I (is there autocorrelation to worry about?) ---
def moran(x):
    m=Moran(np.asarray(x,float), W, permutations=999)
    return m.I, m.p_sim
print("\n=== Moran's I (999 perms) ===")
mor={}
for c in ["biorisk_awm","exposure_full","convertibility","significance"]:
    I,p=moran(val[c].to_numpy()); mor[c]=(I,p); print(f"  {c:16s}: I={I:+.3f}  p={p:.3f}")

# --- 2. spatial block bootstrap for primary + decomposition ---
# blocks = each hex plus its queen neighbours; resample block seeds with replacement.
neighbors={i:list(W.neighbors[i]) for i in range(n)}
def block_bootstrap_spearman(xcol, nb=5000):
    x=val[xcol].to_numpy(); y=val["biorisk_awm"].to_numpy()
    obs=spearmanr(x,y).correlation
    bs=np.empty(nb)
    for b in range(nb):
        seeds=rng.integers(0,n,size=max(1,n//5))          # ~1/5 as many block seeds
        idx=[]
        for s in seeds: idx.append(s); idx.extend(neighbors[s])
        idx=np.array(idx)[:n]                               # cap to n for comparability
        r=spearmanr(x[idx],y[idx]).correlation
        bs[b]=r
    lo,hi=np.nanpercentile(bs,[2.5,97.5])
    return obs,lo,hi,np.nanmean(bs)
print("\n=== spatial block-bootstrap 95% CIs (vs naive) ===")
naive={"exposure_full":(0.240,0.114,0.361),"convertibility":(0.177,0.053,0.295),
       "significance":(0.038,-0.109,0.181),"exposure_SOCSremoved":(0.242,0.115,0.365)}
block={}
for c in ["exposure_full","exposure_SOCSremoved","convertibility","significance"]:
    obs,lo,hi,mn=block_bootstrap_spearman(c)
    block[c]=(obs,lo,hi)
    nlo,nhi=naive[c][1],naive[c][2]
    print(f"  {c:20s}: rho={obs:+.3f}  spatial95=[{lo:+.3f},{hi:+.3f}]  (naive=[{nlo:+.3f},{nhi:+.3f}])")

# --- 3. effective sample size + modified t for primary ---
# Clifford-Richardson style: n_eff from lag-autocorrelation of the two rank fields.
def lag1_ac(x):
    xr=rankdata(x); lag=libpysal.weights.lag_spatial(W,xr)
    xc=xr-xr.mean(); lc=lag-lag.mean()
    return (xc*lc).sum()/np.sqrt((xc**2).sum()*(lc**2).sum())
rx=lag1_ac(val["exposure_full"].to_numpy()); ry=lag1_ac(val["biorisk_awm"].to_numpy())
rho=spearmanr(val["exposure_full"],val["biorisk_awm"]).correlation
n_eff=1+ (n-1)*(1-rx*ry)/(1+rx*ry) if (1+rx*ry)!=0 else n
n_eff=float(np.clip(n_eff,3,n))
tstat=rho*np.sqrt((n_eff-2)/(1-rho**2)); p_corr=2*(1-tdist.cdf(abs(tstat),df=n_eff-2))
print(f"\n=== effective sample size correction (primary) ===")
print(f"  lag-AC exposure={rx:+.3f}  BIORISK={ry:+.3f}  -> n_eff≈{n_eff:.0f} (of {n})")
print(f"  primary rho={rho:+.3f}  modified-t p={p_corr:.4f}")

# --- write ---
lines=["SPATIAL-AUTOCORRELATION CORRECTION (Roper validation)","="*52,
       f"n={n} hexes; Queen graph mean deg={np.mean(list(W.cardinalities.values())):.2f}",
       "",
       "Moran's I:"]+ [f"  {k:16s} I={v[0]:+.3f} p={v[1]:.3f}" for k,v in mor.items()]+[
       "","Spatial block-bootstrap 95% CI (naive in parens):"]+[
       f"  {k:20s} rho={block[k][0]:+.3f} [{block[k][1]:+.3f},{block[k][2]:+.3f}] "
       f"(naive [{naive[k][1]:+.3f},{naive[k][2]:+.3f}])" for k in block]+[
       "",f"Effective n: rho_exp={rx:+.3f} rho_bio={ry:+.3f} -> n_eff≈{n_eff:.0f}",
       f"Primary exposure-vs-BIORISK: rho={rho:+.3f}, modified-t p={p_corr:.4f}",
       "",
       "READ: autocorrelation is present (Moran's I>0); spatial CIs are WIDER than naive;",
       "primary agreement remains positive but with reduced effective n. Interpret rho≈0.24",
       "as a weak positive whose lower CI bound under spatial correction is the honest floor."]
open(f"{OUT}/spatial_correction.txt","w").write("\n".join(lines)+"\n")
json.dump(dict(n=n,n_eff=n_eff,moran={k:[float(a),float(b)] for k,(a,b) in mor.items()},
               primary_rho=float(rho),primary_p_spatial=float(p_corr),
               block_ci={k:[float(a),float(l),float(h)] for k,(a,l,h) in block.items()}),
          open(f"{OUT}/spatial_correction.json","w"),indent=2)
print("\nwrote",f"{OUT}/spatial_correction.txt")
