import geopandas as gpd, pyogrio
CRS = 3577
SHP = "/Users/harshrastogi/ntgis_project/data/landsystems/NTLS_1M/Datasets/Av_Data/ntls_1m.shp"
g = gpd.read_file(SHP)
print("features:", len(g), "| native CRS:", g.crs)
print("columns:", list(g.columns))
print("\n--- per-column cardinality ---")
for c in g.columns:
    if c == "geometry": continue
    nun = g[c].nunique(dropna=False)
    if nun <= 15:
        print(f"  {c} ({nun}): {g[c].value_counts(dropna=False).to_dict()}")
    else:
        sample = g[c].dropna().astype(str).head(3).tolist()
        print(f"  {c}: {nun} unique | e.g. {sample}")
g = g.to_crs(CRS)
print("\ntotal area km2:", round(g.geometry.area.sum()/1e6))
print("invalid geoms:", (~g.geometry.is_valid).sum())
