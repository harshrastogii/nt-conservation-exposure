import geopandas as gpd
import numpy as np
from shapely import get_num_coordinates

CRS = 3577
BASE = "/Users/harshrastogi/ntgis_project/data"
gdb = f"{BASE}/landmass/LandMass_NT_Coastline/Datasets/ESRI/NT_Coastline.gdb"

coast = gpd.read_file(gdb).to_crs(CRS)
print("features:", len(coast))
print("geom types:", coast.geom_type.value_counts().to_dict())

# per-feature vertex counts -- where does detail actually live?
vc = get_num_coordinates(coast.geometry.values)
print("total vertices in layer:", int(vc.sum()))
print("max single-feature vertices:", int(vc.max()))
print("top 10 feature vertex counts:", sorted(vc.tolist(), reverse=True)[:10])

# area per feature, biggest first -- is one giant blob + tiny islands?
coast = coast.copy()
coast["area_km2"] = coast.geometry.area/1e6
coast["vtx"] = vc
top = coast.sort_values("area_km2", ascending=False).head(8)
print("\nlargest features (area_km2, vtx):")
for _, r in top.iterrows():
    print(f"  {r['area_km2']:>12,.1f}   {int(r['vtx']):>8}")

# what other fields/values exist -- MAPUNIT may separate land vs tidal vs sea
print("\ncolumns:", [c for c in coast.columns if c!='geometry'])
for col in coast.columns:
    if col in ('geometry','area_km2','vtx'): continue
    nun = coast[col].nunique()
    if nun <= 15:
        print(f"  {col} ({nun}):", coast[col].value_counts().to_dict())
    else:
        print(f"  {col}: {nun} unique values")
