import geopandas as gpd, numpy as np, pandas as pd, glob
CRS = 3577

hexg = gpd.read_file("data/nt_hexgrid_10km.gpkg").to_crs(CRS)[["hex_id","geometry"]]
ntls = gpd.read_file("/Users/harshrastogi/ntgis_project/data/landsystems/NTLS_1M/Datasets/Av_Data/ntls_1m.shp").to_crs(CRS)
ntls["geometry"] = ntls.geometry.buffer(0)
socs = gpd.read_file(glob.glob("data/socs/**/*.shp", recursive=True)[0]).to_crs(CRS)
socs["geometry"] = socs.geometry.buffer(0)
print("hexes:", len(hexg), "| land systems:", len(ntls), "| socs:", len(socs))

# --- area-based rarity per CLASS ---
ntls["_a"] = ntls.geometry.area
class_area = ntls.groupby("CLASS")["_a"].sum()
frac = class_area/class_area.sum()
rarity = -np.log(frac)
rarity_n = (rarity-rarity.min())/(rarity.max()-rarity.min())
rar = pd.DataFrame({"class_area_km2":(class_area/1e6).round(1),"class_rarity":rarity_n.round(4)})
print("\nrarest 5:\n", rar.sort_values("class_rarity",ascending=False).head().to_string())
print("commonest 5:\n", rar.sort_values("class_rarity").head().to_string())
ntls = ntls.merge(rar, left_on="CLASS", right_index=True, how="left")

# --- land systems x hex, area-weighted rarity ---
li = gpd.overlay(ntls[["CLASS","class_area_km2","class_rarity","geometry"]], hexg, how="intersection", keep_geom_type=True)
li["piece_a"] = li.geometry.area
sig_ls = ((li["class_rarity"]*li["piece_a"]).groupby(li["hex_id"]).sum()
          / li["piece_a"].groupby(li["hex_id"]).sum()).rename("sig_landsystems")
dom = li.loc[li.groupby("hex_id")["piece_a"].idxmax(), ["hex_id","CLASS","class_area_km2","class_rarity"]]
dom = dom.rename(columns={"CLASS":"landsystem_class"}).set_index("hex_id")

# --- SOCS rating-weighted coverage ---
RATING_W = {"International":1.0,"National":0.7,"Regional":0.4}
socs["w"] = socs["SIG_RATING"].map(RATING_W).fillna(0.4)  # unknown -> Regional weight
hex_area = hexg.set_index("hex_id").geometry.area
si = gpd.overlay(socs[["w","geometry"]], hexg, how="intersection", keep_geom_type=True)
si["piece_a"] = si.geometry.area
# weighted covered area / hex area  (cap 1.0)
sig_socs = ((si["w"]*si["piece_a"]).groupby(si["hex_id"]).sum()/hex_area).clip(upper=1.0).rename("sig_socs")

# --- assemble ---
out = hexg.set_index("hex_id").join(dom).join(sig_ls).join(sig_socs)
out["sig_socs"] = out["sig_socs"].fillna(0.0)
v = out["sig_landsystems"]
out["sig_landsystems_n"] = ((v-v.min())/(v.max()-v.min())).round(4)
out["sig_combined_max"] = out[["sig_landsystems_n","sig_socs"]].max(axis=1).round(4)
out["sig_combined_weighted"] = (0.5*out["sig_landsystems_n"].fillna(0)+0.5*out["sig_socs"]).round(4)

out = out.reset_index()
out.to_file("data/hex_significance.gpkg", driver="GPKG")
out[["hex_id","landsystem_class","class_area_km2","class_rarity","sig_landsystems",
     "sig_landsystems_n","sig_socs","sig_combined_max","sig_combined_weighted"]].to_csv("data/hex_significance_QA.csv", index=False)

n_land = out["sig_landsystems"].notna().sum()
print(f"\nhexes: {len(out)} | with land: {n_land} | no-land: {len(out)-n_land}")
print("hexes touching SOCS:", (out['sig_socs']>0).sum())
print("\n=== sig_combined distributions ===")
print(out[["sig_combined_max","sig_combined_weighted"]].describe().round(3).to_string())
print("corr(max,weighted):", round(out[["sig_combined_max","sig_combined_weighted"]].corr().iloc[0,1],3))
print("\nSaved: data/hex_significance.gpkg, data/hex_significance_QA.csv")
