import geopandas as gpd, numpy as np, pandas as pd
from shapely import make_valid

CRS = 3577
HEX  = "/Users/harshrastogi/nt_exposure/data/nt_hexgrid_10km.gpkg"
NTLS = "/Users/harshrastogi/ntgis_project/data/landsystems/NTLS_1M/Datasets/Av_Data/ntls_1m.shp"
OUT  = "/Users/harshrastogi/nt_exposure/data/hex_significance_landsys.gpkg"

hexes = gpd.read_file(HEX).to_crs(CRS)[["hex_id","geometry"]]
hexes["geometry"] = make_valid(hexes.geometry); hexes["hex_km2"]=hexes.geometry.area/1e6
ls = gpd.read_file(NTLS).to_crs(CRS)[["LANDSYSTEM","CLASS","geometry"]]
ls["geometry"] = make_valid(ls.geometry)
ls = ls[~ls["LANDSYSTEM"].isna()].copy()

# NT-wide area per LANDSYSTEM -> log-inverse rarity in [0,1]
ls["a"] = ls.geometry.area/1e6
A = ls.groupby("LANDSYSTEM")["a"].sum()
la = np.log(A); rar = 1 - (la - la.min())/(la.max()-la.min())
rarity = rar.to_dict()
print("land systems:", len(A), "| area range km2:", round(A.min(),2), "-", round(A.max()))
print("rarity range:", round(rar.min(),3), "-", round(rar.max(),3))

inter = gpd.overlay(hexes[["hex_id","geometry"]], ls[["LANDSYSTEM","CLASS","geometry"]],
                    how="intersection", keep_geom_type=True)
inter["piece_km2"] = inter.geometry.area/1e6
inter["rarity"] = inter["LANDSYSTEM"].map(rarity)
print("intersection pieces:", len(inter))

# area-weighted rarity per hex
inter["w"] = inter["rarity"]*inter["piece_km2"]
num = inter.groupby("hex_id")["w"].sum(); den = inter.groupby("hex_id")["piece_km2"].sum()
sig = num/den

# QA: dominant CLASS + dominant LANDSYSTEM by area
def dom(col):
    return (inter.groupby(["hex_id",col])["piece_km2"].sum().reset_index()
            .sort_values("piece_km2").drop_duplicates("hex_id",keep="last")
            .set_index("hex_id")[col])
out = hexes.copy()
out["sig_landsys"]      = out.hex_id.map(sig)
out["dominant_LANDSYS"] = out.hex_id.map(dom("LANDSYSTEM"))
out["dominant_CLASS"]   = out.hex_id.map(dom("CLASS"))
out["ls_area_km2"]      = out.hex_id.map(den).fillna(0.0)
out.loc[out["ls_area_km2"]<=0,"sig_landsys"]=np.nan

n=len(out); nan=out["sig_landsys"].isna().sum()
print(f"\nhexes: {n} | NaN: {nan} ({100*nan/n:.1f}%)")
print("sig_landsys summary:\n", out["sig_landsys"].describe().round(3))
print("sum ls_area_km2:", round(out["ls_area_km2"].sum()))
out.drop(columns="hex_km2").to_file(OUT, driver="GPKG")
print("Saved", OUT)
