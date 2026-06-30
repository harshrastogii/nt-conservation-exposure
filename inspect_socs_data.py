import geopandas as gpd, glob, pyogrio
CRS = 3577
shp = glob.glob("/Users/harshrastogi/nt_exposure/data/socs/**/*.shp", recursive=True)
print("shapefiles found:", shp)
g = gpd.read_file(shp[0])
print("features:", len(g), "| native CRS:", g.crs)
print("columns:", list(g.columns))
print("\n--- per-column unique values (<=12) ---")
for c in g.columns:
    if c == "geometry": continue
    nun = g[c].nunique(dropna=False)
    if nun <= 12:
        vc = g[c].value_counts(dropna=False).to_dict()
        print(f"  {c} ({nun}): {vc}")
    else:
        print(f"  {c}: {nun} unique")
# look specifically for a significance/level/rank field
print("\n--- candidate grading fields (first 5 rows) ---")
cand = [c for c in g.columns if any(k in c.lower()
        for k in ("sig","level","rank","class","tier","status","nat","int","cons"))]
print("candidates:", cand)
if cand:
    print(g[cand].head().to_string())
g = g.to_crs(CRS)
print("\ntotal SOCS area km2:", round(g.geometry.area.sum()/1e6))
print("invalid geoms:", (~g.geometry.is_valid).sum())
