import geopandas as gpd, glob
shp = glob.glob("data/socs/**/*.shp", recursive=True)[0]
print("file:", shp)
g = gpd.read_file(shp)
print("features:", len(g), "| CRS:", g.crs)
print("columns:", list(g.columns))
print("geom types:", g.geom_type.value_counts().to_dict())
print("area km2:", round(g.to_crs(3577).geometry.area.sum()/1e6))
print(g.drop(columns="geometry").head(10).to_string())
