import geopandas as gpd, pandas as pd, numpy as np, os, sys
from pyogrio import list_layers
H=os.path.expanduser
SRC = H("~/roper_overlay/data/Datasets/ESRI/MTF_Roper.gdb")
HEX = H("~/nt_exposure/data/nt_hexgrid_10km.gpkg")
HEX_AREA_KM2 = 86.6

if not os.path.exists(SRC): print("Missing file:\n ", SRC); sys.exit(1)

print("=== LAYERS IN GDB ===")
info=list_layers(SRC); 
for row in info: print("  ", row)
names=[r[0] for r in info]

# pick the risk/biodiversity polygon layer
def score_name(n): 
    n=n.lower(); 
    return sum(k in n for k in ["risk","biod","assess","mtf","roper"]) - ("study_area" in n)*2
LYR=sorted(names, key=score_name, reverse=True)[0]
print("\nAUTO-SELECTED LAYER:", LYR, "  (override SRC/LYR if wrong)")

g=gpd.read_file(SRC, layer=LYR)
print("\n=== BASIC ===")
print("features:", len(g), "| native CRS:", g.crs)
print("geom types:", g.geom_type.value_counts().to_dict())
print("columns:", list(g.columns))

print("\n=== CANDIDATE SCORE/RANK FIELDS ===")
cand=[c for c in g.columns if any(k in c.lower() for k in
      ["score","rank","rat","risk","biod","signif","priorit","value","class","categ","threat","sens","cond","vuln","level"])]
print("candidates:", cand)
for c in cand:
    s=g[c]; print(f"\n-- {c} | dtype={s.dtype} | nunique={s.nunique(dropna=False)} | null={s.isna().sum()}")
    if pd.api.types.is_numeric_dtype(s):
        print("   ", s.describe()[["min","25%","50%","75%","max"]].round(3).to_dict())
    else:
        print(s.value_counts(dropna=False).head(15).to_string())

print("\n=== GEOMETRY HEALTH + SIZE (3577) ===")
g3=g.to_crs(3577); inv=(~g3.is_valid).sum(); print("invalid geoms:", inv)
if inv: g3["geometry"]=g3.buffer(0)
g3["__a_km2"]=g3.area/1e6; a=g3["__a_km2"]
print("polygon area km2 min/median/mean/max:",
      f"{a.min():.3f}/{a.median():.3f}/{a.mean():.3f}/{a.max():.3f}")
print("total assessed area km2:", round(a.sum(),1))
print("polygons < one hex (86.6):", int((a<HEX_AREA_KM2).sum()), f"({100*(a<HEX_AREA_KM2).mean():.1f}%)")

print("\n=== EXTENT vs HEX GRID ===")
hx=gpd.read_file(HEX).to_crs(3577)
print("roper bounds:", np.round(g3.total_bounds,0))
print("hex   bounds:", np.round(hx.total_bounds,0))
ru=g3.union_all(); hu=hx.union_all()
print("intersects grid:", ru.intersects(hu))
ia=ru.intersection(hu).area/1e6
print("roper∩grid km2:", round(ia,1), f"({100*ia/a.sum():.1f}% of assessed area on land-hex grid)")
cov=gpd.overlay(hx[["hex_id","geometry"]], gpd.GeoDataFrame(geometry=[ru],crs=3577), how="intersection")
print("hexes overlapping Roper:", cov["hex_id"].nunique(), "of", len(hx))

print("\n=== COMPARABILITY VERDICT ===")
med=a.median(); ratio=med/HEX_AREA_KM2
print(f"median Roper polygon={med:.2f} km2 ; hex={HEX_AREA_KM2} ; ratio={ratio:.3f}")
print("-> FINER, aggregate Roper up to hex (area-weighted)" if ratio<0.5 else
      "-> COARSER, polygon spans many hexes" if ratio>2 else
      "-> COMPARABLE scale; hex-level join feasible")
print("=== DONE ===")
