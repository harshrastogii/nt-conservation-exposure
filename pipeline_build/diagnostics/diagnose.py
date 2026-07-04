import geopandas as gpd
import pyogrio

CRS = 3577
BASE = "/Users/harshrastogi/ntgis_project/data"
coast_gdb = f"{BASE}/landmass/LandMass_NT_Coastline/Datasets/ESRI/NT_Coastline.gdb"

g = gpd.read_file(coast_gdb).to_crs(CRS)
print("=== coastline layer ===")
print("rows:", len(g))
print("columns:", list(g.columns))
print("geom types:", g.geom_type.value_counts().to_dict())
print("total area km2:", round(g.geometry.area.sum()/1e6))
# how many vertices? a rectangle has ~5; a real coastline has thousands
total_pts = sum(len(geom.exterior.coords) if geom.geom_type=="Polygon"
                else sum(len(p.exterior.coords) for p in geom.geoms)
                for geom in g.geometry)
print("total exterior vertices:", total_pts, "(rectangle≈5, real coastline≈thousands)")
print("bounds:", [round(b) for b in g.total_bounds])

# check against LUMP extent as a sanity cross-reference (you know LUMP is real NT)
lump = gpd.read_file(f"{BASE.replace('ntgis_project','roper_overlay')}/LandUseMapping/LUMP_2016_2024/Datasets/LUMP_2016_2024.gdb", layer="LandUseMapping", rows=1)
print("\n(LUMP loads OK for later cross-check)")
