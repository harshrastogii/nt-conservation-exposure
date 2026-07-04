import geopandas as gpd
import numpy as np
import pandas as pd
from shapely import make_valid
import glob

CRS = 3577
HEX  = "/Users/harshrastogi/nt_exposure/data/nt_hexgrid_10km.gpkg"
SOCS = glob.glob("/Users/harshrastogi/nt_exposure/data/socs/**/Sites_Conservation_Significance.shp", recursive=True)[0]
OUT  = "/Users/harshrastogi/nt_exposure/data/hex_significance_socs.gpkg"

RATING_SCORE = {"International": 1.0, "National": 0.7}
RATING_RANK  = {"International": 2, "National": 1}   # for max-grade selection

hexes = gpd.read_file(HEX).to_crs(CRS)[["hex_id","geometry"]]
hexes["geometry"] = make_valid(hexes.geometry)
hexes["hex_km2"] = hexes.geometry.area/1e6
print("hexes:", len(hexes))

socs = gpd.read_file(SOCS).to_crs(CRS)[["SIG_RATING","REGION","geometry"]]
socs["geometry"] = make_valid(socs.geometry)
socs["rank"] = socs["SIG_RATING"].map(RATING_RANK)
print("socs sites:", len(socs), "| ratings:", socs.SIG_RATING.value_counts().to_dict())

# intersection -> per-piece area, rating, region
inter = gpd.overlay(hexes[["hex_id","geometry"]], socs, how="intersection", keep_geom_type=True)
inter["piece_km2"] = inter.geometry.area/1e6
print("intersection pieces:", len(inter))

# max grade per hex (designation logic: highest rating wins, not diluted)
idx_max = inter.groupby("hex_id")["rank"].idxmax()
top = inter.loc[idx_max, ["hex_id","SIG_RATING","REGION"]].set_index("hex_id")

# fraction of hex under ANY socs site (QA; dissolve overlaps per hex first)
frac = inter.groupby("hex_id")["piece_km2"].sum()  # sites don't overlap each other

out = hexes.copy()
out["socs_rating"] = out.hex_id.map(top["SIG_RATING"])
out["socs_region"] = out.hex_id.map(top["REGION"])
out["socs_frac"]   = (out.hex_id.map(frac) / out["hex_km2"]).fillna(0.0).clip(upper=1.0)
out["sig_socs"]    = out["socs_rating"].map(RATING_SCORE).fillna(0.0)

n_hit = (out["sig_socs"] > 0).sum()
print(f"\nhexes intersecting SOCS: {n_hit} ({100*n_hit/len(out):.1f}%)")
print("sig_socs distribution:\n", out["sig_socs"].value_counts().sort_index())
print("\nsocs_rating breakdown:\n", out["socs_rating"].value_counts(dropna=False))
print("\nby region (hexes hit):\n", out.loc[out.sig_socs>0,"socs_region"].value_counts())
print("\nsocs_frac (hit hexes) summary:\n",
      out.loc[out.sig_socs>0,"socs_frac"].describe().round(3))
print("\ntotal SOCS-covered hex area km2:", round((out['socs_frac']*out['hex_km2']).sum()))

out.drop(columns="hex_km2").to_file(OUT, driver="GPKG")
print(f"\nSaved {OUT}")
