import geopandas as gpd
import numpy as np
from shapely import get_num_coordinates, get_num_interior_rings
from shapely.ops import unary_union
import matplotlib.pyplot as plt

CRS = 3577
BASE = "/Users/harshrastogi/ntgis_project/data"
gdb = f"{BASE}/landmass/LandMass_NT_Coastline/Datasets/ESRI/NT_Coastline.gdb"

coast = gpd.read_file(gdb).to_crs(CRS)
coast = coast.reset_index(drop=True)
coast["area_km2"] = coast.geometry.area/1e6
coast["vtx"] = get_num_coordinates(coast.geometry.values)
# interior rings per feature (summed across multipolygon parts)
def n_int(g):
    parts = g.geoms if hasattr(g,"geoms") else [g]
    return sum(get_num_interior_rings(p) for p in parts)
coast["int_rings"] = coast.geometry.apply(n_int)
coast["n_parts"] = coast.geometry.apply(lambda g: len(g.geoms) if hasattr(g,"geoms") else 1)

top = coast.sort_values("area_km2", ascending=False).head(6)
print("idx        area_km2        vtx   int_rings  n_parts  MAPUNIT")
for i, r in top.iterrows():
    print(f"{i:>4} {r['area_km2']:>14,.1f} {int(r['vtx']):>10} {int(r['int_rings']):>10} {int(r['n_parts']):>8}  {r['MAPUNIT']}")

# the two suspects
big   = coast.sort_values("area_km2", ascending=False).index[0]   # ~1.33M mainland
susp  = coast.sort_values("area_km2", ascending=False).index[1]   # ~302k, 5.4M vtx
print(f"\nmainland idx={big}, suspect idx={susp}")

# does the suspect CONTAIN the mainland? (extent-with-hole signature)
gb = coast.geometry.loc[big]; gs = coast.geometry.loc[susp]
print("suspect.contains(mainland centroid):", gs.contains(gb.representative_point()))
print("suspect bounds km:", [round(v/1000) for v in gs.bounds])
print("mainland bounds km:", [round(v/1000) for v in gb.bounds])
print("suspect area / suspect convex_hull:", round(gs.area/gs.convex_hull.area,3))
print("mainland area / mainland convex_hull:", round(gb.area/gb.convex_hull.area,3))

# union WITHOUT the suspect feature
land = coast.drop(index=susp)
b2 = unary_union(land.geometry.values)
nparts = len(b2.geoms) if hasattr(b2,"geoms") else 1
print(f"\nUNION minus suspect -> {b2.geom_type}, {nparts} parts, "
      f"area {b2.area/1e6:,.0f} km2, hull-ratio {b2.area/b2.convex_hull.area:.3f}")

nt = gpd.GeoDataFrame(geometry=[b2], crs=CRS)
fig,ax=plt.subplots(figsize=(9,11))
nt.boundary.plot(ax=ax, linewidth=0.3, color="black")
ax.set_title(f"Union WITHOUT suspect: {nparts} parts, "
             f"hull-ratio {b2.area/b2.convex_hull.area:.3f}")
ax.set_axis_off(); plt.tight_layout()
plt.savefig("/Users/harshrastogi/nt_exposure/data/diag_minus_suspect.png", dpi=180, bbox_inches="tight")
print("Saved diag_minus_suspect.png")
