import geopandas as gpd
import numpy as np
from shapely.ops import unary_union, transform
from shapely import force_2d
import matplotlib.pyplot as plt

CRS = 3577
BASE = "/Users/harshrastogi/ntgis_project/data"
coast_gdb = f"{BASE}/landmass/LandMass_NT_Coastline/Datasets/ESRI/NT_Coastline.gdb"

coast = gpd.read_file(coast_gdb).to_crs(CRS)
print("raw features:", len(coast))
print("has_z:", coast.geometry.has_z.any())
print("raw total area km2:", round(coast.geometry.area.sum()/1e6))
print("raw bounds:", [round(v) for v in coast.total_bounds])

# strip Z FIRST, then repair, then union
coast2d = coast.copy()
coast2d["geometry"] = force_2d(coast2d.geometry)
print("after force_2d has_z:", coast2d.geometry.has_z.any())

b_raw = unary_union(coast2d.geometry.values)
print("\n2D RAW union -> type:", b_raw.geom_type,
      "| area km2:", round(b_raw.area/1e6),
      "| parts:", len(b_raw.geoms) if hasattr(b_raw,'geoms') else 1)

coast2d["geometry"] = coast2d.geometry.buffer(0)
b_buf = unary_union(coast2d.geometry.values)
print("2D BUF union -> type:", b_buf.geom_type,
      "| area km2:", round(b_buf.area/1e6),
      "| parts:", len(b_buf.geoms) if hasattr(b_buf,'geoms') else 1)

def vcount(geom):
    tot=0
    gs = geom.geoms if hasattr(geom,'geoms') else [geom]
    for g in gs:
        tot += len(g.exterior.coords) + sum(len(r.coords) for r in g.interiors)
    return tot
print("\n2D RAW union vertices:", vcount(b_raw))
print("2D BUF union vertices:", vcount(b_buf))
print("convex-hull ratio (raw):", round(b_raw.area/b_raw.convex_hull.area, 3))

# PLOT the dissolved boundary directly (this is the truth test)
nt = gpd.GeoDataFrame(geometry=[b_raw], crs=CRS)
fig, ax = plt.subplots(figsize=(9,11))
nt.boundary.plot(ax=ax, linewidth=0.4, color="black")
ax.set_title(f"Dissolved boundary: {nt.geometry.iloc[0].geom_type}, "
             f"{len(b_raw.geoms) if hasattr(b_raw,'geoms') else 1} parts")
ax.set_axis_off(); plt.tight_layout()
plt.savefig("/Users/harshrastogi/nt_exposure/data/diag_boundary.png", dpi=180, bbox_inches="tight")
print("\nSaved diag_boundary.png")
