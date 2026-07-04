import geopandas as gpd, pandas as pd, numpy as np
CRS=3577

sig=gpd.read_file("data/hex_significance.gpkg")[["hex_id","sig_combined_max","sig_combined_weighted","geometry"]]
conv=gpd.read_file("data/hex_convertibility.gpkg")[["hex_id","convertibility"]]
prot=gpd.read_file("data/hex_protection.gpkg")[["hex_id","protection_score"]]

h=sig.merge(conv,on="hex_id").merge(prot,on="hex_id")
# land mask: require all three present
h["land"]=h[["sig_combined_max","convertibility","protection_score"]].notna().all(axis=1)
print("land hexes:",h["land"].sum(),"| masked:",(~h["land"]).sum())

def exposure(sig_col):
    return (h[sig_col]*h["convertibility"]*(1-h["protection_score"]))
h["exposure"]=exposure("sig_combined_max").where(h["land"])
h["exposure_wt_sig"]=exposure("sig_combined_weighted").where(h["land"])   # alt significance
# normalise 0..1 for interpretability
for c in ["exposure","exposure_wt_sig"]:
    v=h[c]; h[c+"_n"]=((v-v.min())/(v.max()-v.min())).round(4)

h.to_file("data/hex_exposure.gpkg",driver="GPKG")
h.drop(columns="geometry").to_csv("data/hex_exposure_QA.csv",index=False)

print("\n=== exposure (MVP: sig_combined_max) ===")
print(h["exposure"].describe().round(4).to_string())
print("\ntop decile threshold:",round(h["exposure"].quantile(0.9),4))
print("corr(exposure, exposure_wt_sig):",round(h[["exposure","exposure_wt_sig"]].corr().iloc[0,1],3))
print("\nSaved: data/hex_exposure.gpkg, data/hex_exposure_QA.csv")
