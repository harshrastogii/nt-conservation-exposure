import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import force_2d, make_valid, get_num_interior_rings
import matplotlib.pyplot as plt

CRS = 3577
BASE = "/Users/harshrastogi/ntgis_project/data"
TARGET_AREA_KM2 = 86.6
s = np.sqrt(TARGET_AREA_KM2 / (3*np.sqrt(3)/2)) * 1000.0
print(f"hex s = {s:.0f} m -> area = {(3*np.sqrt(3)/2)*(s/1000)**2:.1f} km2")

coast_gdb = f"{BASE}/landmass/LandMass_NT_Coastline/Datasets/ESRI/NT_Coastline.gdb"
coast = gpd.read_file(coast_gdb).to_crs(CRS).reset_index(drop=True)

# CRITICAL FIX: the layer contains one inverse-EXTENT polygon (~302k km2, 5.4M vtx,
# 1238 interior rings, MAPUNIT mislabelled 'Land') whose outer ring is the sea
# boundary and whose 1238 holes are the landmasses. Unioning it fills the Gulf and
# every embayment -> trapezoid. Genuine land features have 0 interior rings here.
def n_int(g):
    parts = g.geoms if hasattr(g, "geoms") else [g]
    return sum(get_num_interior_rings(p) for p in parts)
coast["int_rings"] = coast.geometry.apply(n_int)
before = len(coast)
coast = coast[coast["int_rings"] == 0].copy()
print(f"dropped {before - len(coast)} extent feature(s); land features: {len(coast)}")

coast["geometry"] = force_2d(coast.geometry)
coast["geometry"] = make_valid(coast.geometry)
boundary = unary_union(coast.geometry.values)
nt = gpd.GeoDataFrame(geometry=[boundary], crs=CRS)
nparts = len(boundary.geoms) if hasattr(boundary, "geoms") else 1
print("boundary type:", boundary.geom_type, "| parts:", nparts)
print("NT LAND area km2:", round(nt.geometry.area.sum()/1e6))
print("convex-hull ratio:", round(boundary.area/boundary.convex_hull.area, 3))

minx, miny, maxx, maxy = nt.total_bounds
dx = np.sqrt(3) * s; dy = 1.5 * s
def hexagon(cx, cy, s):
    return Polygon([(cx + s*np.cos(a), cy + s*np.sin(a))
                    for a in np.radians([0,60,120,180,240,300])])
cols = int((maxx-minx)/dx)+2; rows = int((maxy-miny)/dy)+2
hexes=[]
for r in range(rows):
    cy=miny+r*dy; xoff=(dx/2) if (r%2) else 0
    for c in range(cols):
        hexes.append(hexagon(minx+c*dx+xoff, cy, s))
grid = gpd.GeoDataFrame(geometry=hexes, crs=CRS); grid["hex_id"]=range(len(grid))
print("hexes before clip:", len(grid))
keep = gpd.sjoin(grid, nt, how="inner", predicate="intersects").drop(columns="index_right")
keep = keep.drop_duplicates("hex_id").reset_index(drop=True)
print("hexes intersecting NT land:", len(keep))
keep.to_file("/Users/harshrastogi/nt_exposure/data/nt_hexgrid_10km.gpkg", driver="GPKG")
nt.to_file("/Users/harshrastogi/nt_exposure/data/nt_boundary.gpkg", driver="GPKG")
fig,ax=plt.subplots(figsize=(10,11))
keep.plot(ax=ax, linewidth=0.1, edgecolor="#aaa", facecolor="#eef3ee")
nt.boundary.plot(ax=ax, linewidth=0.4, color="black")
ax.set_title(f"NT ~10km hex grid - {len(keep):,} hexes (~{TARGET_AREA_KM2:.0f} km2 each)")
ax.set_axis_off(); plt.tight_layout()
plt.savefig("/Users/harshrastogi/nt_exposure/data/nt_hexgrid_10km.png", dpi=180, bbox_inches="tight")
print("Saved."); plt.close("all")
