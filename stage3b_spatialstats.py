import geopandas as gpd, numpy as np, pandas as pd
from libpysal.weights import Queen
from esda.moran import Moran
from esda.getisord import G_Local
CRS=3577

h=gpd.read_file("data/hex_exposure.gpkg")
h=h[h["exposure"].notna()].reset_index(drop=True)   # land hexes only
print("land hexes:",len(h))

# spatial weights (contiguity on the hex grid), row-standardised
w=Queen.from_dataframe(h,use_index=False)
w.transform="r"
print("avg neighbours:",round(np.mean([len(n) for n in w.neighbors.values()]),2),
      "| islands:",len(w.islands))

y=h["exposure"].values
# --- global Moran's I ---
mi=Moran(y,w,permutations=999)
print(f"\nMoran's I = {mi.I:.4f} | E[I] = {mi.EI:.4f} | p(sim) = {mi.p_sim:.4f} | z = {mi.z_sim:.2f}")

# --- Getis-Ord Gi* (star = include self) ---
gi=G_Local(y,w,star=True,permutations=999)
h["gi_z"]=gi.Zs
h["gi_p"]=gi.p_sim
# classify hot/cold spots at 95% (|z|>1.96 & p<0.05)
def cls(r):
    if r["gi_p"]<0.05 and r["gi_z"]>1.96: return "hot"
    if r["gi_p"]<0.05 and r["gi_z"]<-1.96: return "cold"
    return "ns"
h["gi_class"]=h.apply(cls,axis=1)
print("\nGi* hot/cold spot counts:\n",h["gi_class"].value_counts().to_string())

h.to_file("data/hex_exposure_gi.gpkg",driver="GPKG")
h[["hex_id","exposure","exposure_n","gi_z","gi_p","gi_class"]].to_csv("data/hex_exposure_gi_QA.csv",index=False)
print("\nSaved: data/hex_exposure_gi.gpkg, data/hex_exposure_gi_QA.csv")
