import geopandas as gpd
import numpy as np
import pandas as pd
from shapely import make_valid
import time

CRS = 3577
HEX = "/Users/harshrastogi/nt_exposure/data/nt_hexgrid_10km.gpkg"
LUMP = "/Users/harshrastogi/roper_overlay/data/LandUseMapping/LUMP_2016_2024/Datasets/LUMP_2016_2024.gdb"
OUT = "/Users/harshrastogi/nt_exposure/data/hex_convertibility.gpkg"

# ---- locked scoring scheme (PRIM_NO -> convertibility) -------------------
SCORE = {1: 0.1, 2: 1.0, 3: 0.4, 4: 0.2, 5: 0.0}   # 6 (Water) deliberately absent -> no-data
DESC  = {1:"Conservation and natural environments",
         2:"Production from relatively natural environments",
         3:"Production from dryland agriculture and plantations",
         4:"Production from irrigated agriculture and plantations",
         5:"Intensive uses", 6:"Water"}

t0 = time.time()
hexes = gpd.read_file(HEX).to_crs(CRS)[["hex_id","geometry"]]
hexes["geometry"] = make_valid(hexes.geometry)
print("hexes:", len(hexes))

lump = gpd.read_file(LUMP, layer="LandUseMapping").to_crs(CRS)[["PRIM_NO","geometry"]]
inv = (~lump.geometry.is_valid).sum()
lump["geometry"] = make_valid(lump.geometry)
print(f"lump polygons: {len(lump)} (repaired {inv} invalid)")

print("running overlay (this is the slow step)...")
inter = gpd.overlay(hexes, lump, how="intersection", keep_geom_type=True)
inter["piece_km2"] = inter.geometry.area / 1e6
print(f"intersection pieces: {len(inter)}  | elapsed {time.time()-t0:.0f}s")

# ---- per-hex aggregation -------------------------------------------------
inter["is_water"] = inter["PRIM_NO"] == 6
inter["score"] = inter["PRIM_NO"].map(SCORE)            # NaN for water (class 6)

g = inter.groupby("hex_id")
land  = inter[~inter.is_water].groupby("hex_id")["piece_km2"].sum()
water = inter[ inter.is_water].groupby("hex_id")["piece_km2"].sum()

# area-weighted mean over scored (non-water) classes only
scored = inter.dropna(subset=["score"]).copy()
scored["wscore"] = scored["score"] * scored["piece_km2"]
num = scored.groupby("hex_id")["wscore"].sum()
den = scored.groupby("hex_id")["piece_km2"].sum()       # == valid_lump_area
conv = (num / den)

# dominant class by area (water included, so all-water hex reports 6)
dom = (inter.groupby(["hex_id","PRIM_NO"])["piece_km2"].sum()
             .reset_index()
             .sort_values("piece_km2")
             .drop_duplicates("hex_id", keep="last")
             .set_index("hex_id")["PRIM_NO"])

out = hexes.copy()
out["land_area_km2"]       = out.hex_id.map(land).fillna(0.0)
out["water_area_km2"]      = out.hex_id.map(water).fillna(0.0)
out["valid_lump_area_km2"] = out.hex_id.map(den).fillna(0.0)
out["dominant_PRIM_NO"]    = out.hex_id.map(dom)
out["dominant_PRIM_DESC"]  = out["dominant_PRIM_NO"].map(DESC)
out["convertibility"]      = out.hex_id.map(conv)        # NaN where no valid land
out.loc[out["valid_lump_area_km2"] <= 0, "convertibility"] = np.nan

# ---- report -------------------------------------------------------------
n = len(out); nan = out["convertibility"].isna().sum()
print(f"\nhexes: {n} | convertibility NaN (no-data): {nan} ({100*nan/n:.1f}%)")
print("convertibility summary:\n", out["convertibility"].describe().round(3))
print("\ndominant class distribution:\n",
      out["dominant_PRIM_NO"].value_counts(dropna=False).sort_index())
# coverage sanity: total valid land vs known LUMP land area
print("\nsum valid_lump_area_km2:", round(out["valid_lump_area_km2"].sum()))
print("sum water_area_km2:", round(out["water_area_km2"].sum()))

out.to_file(OUT, driver="GPKG")
print(f"\nSaved {OUT}  | total elapsed {time.time()-t0:.0f}s")
