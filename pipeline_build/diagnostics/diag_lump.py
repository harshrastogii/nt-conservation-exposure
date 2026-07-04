import geopandas as gpd
import pyogrio

CRS = 3577
lump_gdb = "/Users/harshrastogi/roper_overlay/data/LandUseMapping/LUMP_2016_2024/Datasets/LUMP_2016_2024.gdb"
print("layers:", pyogrio.list_layers(lump_gdb))

lump = gpd.read_file(lump_gdb, layer="LandUseMapping")
print("features:", len(lump), "| native CRS:", lump.crs)
print("columns:", list(lump.columns))

# PRIM_NO distribution by count and by area
lump = lump.to_crs(CRS)
lump["area_km2"] = lump.geometry.area/1e6
print("\nPRIM_NO counts:\n", lump["PRIM_NO"].value_counts(dropna=False).sort_index())
print("\nPRIM_NO area km2:\n",
      lump.groupby("PRIM_NO")["area_km2"].sum().round(0).sort_index())
print("\ntotal LUMP area km2:", round(lump["area_km2"].sum()))

# sanity: PRIM_NO vs PRIM_DESC mapping (use PRIM_NO, but check labels)
print("\nPRIM_NO -> PRIM_DESC (first label seen per class):")
for n, g in lump.groupby("PRIM_NO"):
    desc = str(g["PRIM_DESC"].iloc[0]).replace("\r"," ").replace("\n"," ").strip()
    print(f"  {n}: {desc[:70]}")

# geometry validity (will matter for the area-weighted overlay)
inv = (~lump.geometry.is_valid).sum()
print("\ninvalid geometries:", inv)
