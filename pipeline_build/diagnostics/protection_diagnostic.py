import geopandas as gpd, pandas as pd, numpy as np, os
from pyogrio import list_layers
pd.set_option("display.max_rows", 60); pd.set_option("display.width", 140)

SRC = os.path.expanduser("~/ntgis_project/data/parks/Data/ESRI/NT_Parks_g94.shp")
HEX = os.path.expanduser("~/nt_exposure/data/nt_hexgrid_10km.gpkg")

try: layers = [l[0] for l in list_layers(SRC)]; print("LAYERS:", layers)
except Exception as e: layers = [None]; print("single-layer:", e)
LYR = layers[0] if layers and layers[0] else None
g = gpd.read_file(SRC, layer=LYR) if LYR else gpd.read_file(SRC)

print("\nfeatures:", len(g), "| native CRS:", g.crs)
print("geom types:", g.geom_type.value_counts().to_dict())
print("columns:", list(g.columns))

cand = [c for c in g.columns if any(k in c.lower() for k in
        ["type","class","tier","iucn","tenure","categ","status","desig","prot","estate","name","ipa","capad"])]
for c in cand:
    print(f"\n-- {c} ({g[c].nunique(dropna=False)} unique) --")
    print(g[c].value_counts(dropna=False).head(25))

g3 = g.to_crs(3577)
inv = (~g3.is_valid).sum(); print("\ninvalid geoms:", inv)
if inv: g3["geometry"] = g3.buffer(0)
g3["__a_km2"] = g3.area/1e6
print("total area km2 (pre-dissolve):", round(g3["__a_km2"].sum(),1))
if cand:
    tcol = cand[0]; print("area by", tcol, ":")
    print(g3.groupby(tcol)["__a_km2"].sum().sort_values(ascending=False).head(15).round(1))

hx = gpd.read_file(HEX).to_crs(3577)
print("\nprotection bounds:", np.round(g3.total_bounds,0))
print("hexgrid   bounds:", np.round(hx.total_bounds,0))
print("intersects hex grid:", g3.unary_union.intersects(hx.unary_union))
print("DONE")
