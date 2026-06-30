# attribute_protection.py — Protection component (MVP, NT Parks only)
# READS : ~/nt_exposure/data/nt_hexgrid_10km.gpkg
#         ~/ntgis_project/data/parks/Data/ESRI/NT_Parks_g94.shp
# WRITES: ~/nt_exposure/data/hex_protection.gpkg
import geopandas as gpd, pandas as pd, numpy as np, os
H = os.path.expanduser
HEX  = H("~/nt_exposure/data/nt_hexgrid_10km.gpkg")
PARK = H("~/ntgis_project/data/parks/Data/ESRI/NT_Parks_g94.shp")
OUT  = H("~/nt_exposure/data/hex_protection.gpkg")

hx = gpd.read_file(HEX).to_crs(3577)
assert "hex_id" in hx.columns, hx.columns.tolist()
hx["hex_area_km2"] = hx.area/1e6

pk = gpd.read_file(PARK).to_crs(3577)
pk["geometry"] = pk.buffer(0)
STRICT = {"IA","IB","II","III","IV","V","VI"}
pk["__iucn_strict"] = pk["IUCN"].astype(str).str.upper().str.strip().isin(STRICT)

try:    geom_all = pk.union_all()
except AttributeError: geom_all = pk.unary_union
try:    geom_strict = pk[pk["__iucn_strict"]].union_all()
except AttributeError: geom_strict = pk[pk["__iucn_strict"]].unary_union

prot_all    = gpd.GeoDataFrame(geometry=[geom_all],    crs=3577)
prot_strict = gpd.GeoDataFrame(geometry=[geom_strict], crs=3577)
prot_all["geometry"]    = prot_all.buffer(0)
prot_strict["geometry"] = prot_strict.buffer(0)

def hex_area(hexgdf, surface):
    i = gpd.overlay(hexgdf[["hex_id","geometry"]], surface,
                    how="intersection", keep_geom_type=True)
    if len(i)==0: return pd.Series(dtype=float)
    i["__a"] = i.area/1e6
    return i.groupby("hex_id")["__a"].sum()

hx = hx.merge(hex_area(hx, prot_all).rename("prot_area_km2"), on="hex_id", how="left")
hx = hx.merge(hex_area(hx, prot_strict).rename("__strict_km2"), on="hex_id", how="left")
hx[["prot_area_km2","__strict_km2"]] = hx[["prot_area_km2","__strict_km2"]].fillna(0.0)

hx["prot_frac"] = (hx["prot_area_km2"]/hx["hex_area_km2"]).clip(0,1)
hx["iucn_frac"] = (hx["__strict_km2"]/hx["hex_area_km2"]).clip(0,1)

out = hx[["hex_id","prot_frac","iucn_frac","prot_area_km2","hex_area_km2","geometry"]].copy()
out.to_file(OUT, driver="GPKG")

tot_src  = (geom_all.area)/1e6
tot_attr = out["prot_area_km2"].sum()
print("=== PROTECTION VALIDATION ===")
print(f"source dissolved area km2 : {tot_src:,.1f}")
print(f"attributed area km2       : {tot_attr:,.1f}  (clip loss expected: parks offshore/outside land hexes)")
print(f"reconciliation ratio      : {tot_attr/tot_src:.4f}")
print(f"hexes total               : {len(out)}")
print(f"hexes with any protection : {(out.prot_frac>0).sum()}  ({100*(out.prot_frac>0).mean():.1f}%)")
print(f"fully protected hexes     : {(out.prot_frac==1).sum()}")
print(f"partially protected hexes : {((out.prot_frac>0)&(out.prot_frac<1)).sum()}")
print(f"prot_frac  min/mean/max   : {out.prot_frac.min():.3f}/{out.prot_frac.mean():.3f}/{out.prot_frac.max():.3f}")
print(f"iucn_frac  min/mean/max   : {out.iucn_frac.min():.3f}/{out.iucn_frac.mean():.3f}/{out.iucn_frac.max():.3f}")
print(f"prot_frac > 1.0 (should be 0): {(out.prot_frac>1.0).sum()}")
print(f"NaNs (should be 0)          : {out[['prot_frac','iucn_frac']].isna().sum().sum()}")
print("wrote:", OUT)
