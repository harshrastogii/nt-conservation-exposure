import geopandas as gpd, glob
f = glob.glob("data/capad/**/*.shp", recursive=True) + glob.glob("data/capad/**/*.gdb", recursive=True)
print("found:", f)
src = f[0]
import pyogrio
print("layers:", pyogrio.list_layers(src)[:,0].tolist() if src.endswith(".gdb") else "shapefile")
g = gpd.read_file(src, rows=5)
print("CRS:", g.crs)
print("columns:", list(g.columns))
print(g.drop(columns="geometry").head().to_string())
# find the state field + NT count without loading geometry-heavy full read
import pandas as pd
cols = [c for c in g.columns if g[c].dtype=='object']
print("\ncandidate text columns:", cols)
