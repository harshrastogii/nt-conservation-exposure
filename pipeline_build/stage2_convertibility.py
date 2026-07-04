import geopandas as gpd, pandas as pd
CRS=3577
LUMP="/Users/harshrastogi/roper_overlay/data/LandUseMapping/LUMP_2016_2024/Datasets/LUMP_2016_2024.gdb"

SCORE={2:1.0,3:0.5,4:0.3,1:0.1,5:0.05}   # Water(6) excluded, not scored

hexg=gpd.read_file("data/nt_hexgrid_10km.gpkg").to_crs(CRS)[["hex_id","geometry"]]
lump=gpd.read_file(LUMP,layer="LandUseMapping").to_crs(CRS)
lump["geometry"]=lump.geometry.buffer(0)
lump=lump[lump["PRIM_NO"]!=6].copy()             # mask out Water entirely
lump["conv"]=lump["PRIM_NO"].map(SCORE)
print("lump rows (excl water):",len(lump),"| unmapped:",lump["conv"].isna().sum())

li=gpd.overlay(lump[["PRIM_NO","conv","geometry"]],hexg,how="intersection",keep_geom_type=True)
li["a"]=li.geometry.area
conv=((li["conv"]*li["a"]).groupby(li["hex_id"]).sum()/li["a"].groupby(li["hex_id"]).sum()).rename("convertibility")
dom=li.loc[li.groupby("hex_id")["a"].idxmax(),["hex_id","PRIM_NO"]].rename(columns={"PRIM_NO":"dom_landuse"}).set_index("hex_id")

out=hexg.set_index("hex_id").join(conv).join(dom).reset_index()  # all-water hexes -> NaN
out.to_file("data/hex_convertibility.gpkg",driver="GPKG")
out[["hex_id","dom_landuse","convertibility"]].to_csv("data/hex_convertibility_QA.csv",index=False)

n=out["convertibility"].notna().sum()
print(f"hexes:{len(out)} | with land-LUMP:{n} | no-land(all water/none):{len(out)-n}")
print("\nconvertibility distribution:\n",out["convertibility"].describe().round(3).to_string())
print("\ndominant land-use class counts:\n",out["dom_landuse"].value_counts().sort_index().to_string())
print("\nSaved: data/hex_convertibility.gpkg, data/hex_convertibility_QA.csv")
