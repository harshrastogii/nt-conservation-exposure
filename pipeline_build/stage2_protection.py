import geopandas as gpd, glob, numpy as np
CRS=3577
shp=glob.glob("data/capad/**/*.shp",recursive=True)[0]

hexg=gpd.read_file("data/nt_hexgrid_10km.gpkg").to_crs(CRS)[["hex_id","geometry"]]
cap=gpd.read_file(shp)
cap=cap[cap["STATE"]=="NT"].to_crs(CRS)
cap["geometry"]=cap.geometry.buffer(0)
print("NT protected areas:",len(cap),"| IUCN cats:",sorted(cap['IUCN'].dropna().unique().tolist()))
print("governance counts:\n",cap['GOVERNANCE'].value_counts().to_string())

# land mask per hex = LUMP-derived land area (reuse convertibility coverage as the land denominator)
conv=gpd.read_file("data/hex_convertibility.gpkg")[["hex_id","convertibility","geometry"]]
# land area per hex from LUMP intersection
LUMP="/Users/harshrastogi/roper_overlay/data/LandUseMapping/LUMP_2016_2024/Datasets/LUMP_2016_2024.gdb"
lump=gpd.read_file(LUMP,layer="LandUseMapping").to_crs(CRS)
lump["geometry"]=lump.geometry.buffer(0)
lump=lump[lump["PRIM_NO"]!=6]
land=gpd.overlay(lump[["geometry"]],hexg,how="intersection",keep_geom_type=True)
land_area=land.geometry.area.groupby(land["hex_id"]).sum().rename("land_m2")

# protected area per hex (dissolve PAs first to avoid double-count)
pa=gpd.GeoDataFrame(geometry=[cap.geometry.union_all()],crs=CRS)
pi=gpd.overlay(pa,hexg,how="intersection",keep_geom_type=True)
prot_area=pi.geometry.area.groupby(pi["hex_id"]).sum().rename("prot_m2")

out=hexg.set_index("hex_id").join(land_area).join(prot_area)
out["prot_m2"]=out["prot_m2"].fillna(0.0)
out["protected_area_km2"]=(out["prot_m2"]/1e6).round(3)
out["protected_fraction"]=(out["prot_m2"]/out["land_m2"]).clip(upper=1.0)   # NaN where no land
out["protection_score"]=out["protected_fraction"]   # MVP: score = fraction
out=out.reset_index()

out.to_file("data/hex_protection.gpkg",driver="GPKG")
out[["hex_id","protected_area_km2","protected_fraction","protection_score"]].to_csv("data/hex_protection_QA.csv",index=False)

n=out["protected_fraction"].notna().sum()
print(f"\nhexes:{len(out)} | with land:{n} | no-land:{len(out)-n}")
print("hexes with any protection:",(out['protected_fraction']>0).sum())
print("\nprotected_fraction distribution:\n",out["protected_fraction"].describe().round(3).to_string())
print("mean protected_fraction (land hexes):",round(out["protected_fraction"].mean(),3))
print("\nSaved: data/hex_protection.gpkg, data/hex_protection_QA.csv")
