# integrate_index.py — join all core layers, correlations, provisional exposure
# WRITES : hex_master.gpkg  +  hex_master_qa.csv
import geopandas as gpd, pandas as pd, numpy as np, os, sys
H = os.path.expanduser; D = H("~/nt_exposure/data/")
def p(f): return os.path.join(D,f)

# --- resolve significance structure: prefer combined, else separate ---
SIG_COMBINED = os.path.exists(p("hex_significance.gpkg"))
sig_files = (["hex_significance.gpkg"] if SIG_COMBINED
             else ["hex_significance_socs.gpkg","hex_significance_landsys.gpkg"])

REQUIRED = ["nt_hexgrid_10km.gpkg","hex_convertibility.gpkg",
            "hex_protection.gpkg"] + sig_files

# --- validate existence before any read ---
missing = [f for f in REQUIRED if not os.path.exists(p(f))]
if missing:
    print("Missing file:")
    for f in missing: print(" ", p(f))
    sys.exit(1)

# --- load + schema (with CRS) ---
print("=== SCHEMAS ===")
gdfs = {}
for f in REQUIRED:
    g = gpd.read_file(p(f)); gdfs[f]=g
    print(f"{f:34s} rows={len(g):6d}  CRS={str(g.crs):12s}  "
          f"cols={[c for c in g.columns if c!='geometry']}")

# --- auto-detect score column ---
def pick(g, prefer):
    cols=[c for c in g.columns if c!="geometry"]
    for n in prefer:
        if n in cols: return n
    num=[c for c in cols if c!="hex_id" and pd.api.types.is_numeric_dtype(g[c])
         and not any(s in c.lower() for s in ["area","count","_km2"])]
    return num[0] if num else None

# master geometry from grid
grid = gdfs["nt_hexgrid_10km.gpkg"]
master = grid[["hex_id","geometry"]].copy()
assert master["hex_id"].is_unique, "hex_id not unique in grid"

# --- choose score columns per component ---
SCORE = {}
SCORE["conv_score"] = (gdfs["hex_convertibility.gpkg"],
                       pick(gdfs["hex_convertibility.gpkg"],
                            ["conv_score","convertibility","conv"]))
if SIG_COMBINED:
    sg = gdfs["hex_significance.gpkg"]
    SCORE["sig_socs"]    = (sg, pick(sg,["sig_socs","socs_score"]))
    SCORE["sig_landsys"] = (sg, pick(sg,["sig_landsys","sig_landsystems","rarity_score","landsys_score"]))
else:
    SCORE["sig_socs"]    = (gdfs["hex_significance_socs.gpkg"],
                            pick(gdfs["hex_significance_socs.gpkg"],["sig_socs","socs_score"]))
    SCORE["sig_landsys"] = (gdfs["hex_significance_landsys.gpkg"],
                            pick(gdfs["hex_significance_landsys.gpkg"],
                                 ["sig_landsys","sig_landsystems","rarity_score","landsys_score"]))
SCORE["prot_frac"] = (gdfs["hex_protection.gpkg"], "prot_frac")

print("\n=== SELECTED SCORE COLUMNS ===")
for tgt,(g,col) in SCORE.items(): print(f"  {tgt:12s} <- {col}")
missing_col=[t for t,(g,c) in SCORE.items() if c is None]
if missing_col:
    print("\nCould not detect column(s):", missing_col); sys.exit(1)

# --- join on hex_id ---
for tgt,(g,col) in SCORE.items():
    sub=g[["hex_id",col]].rename(columns={col:tgt})
    sub=sub.drop_duplicates("hex_id")
    before=len(master); master=master.merge(sub,on="hex_id",how="left")
    assert len(master)==before, f"{tgt} join changed row count"
if "iucn_frac" in gdfs["hex_protection.gpkg"].columns:
    master=master.merge(gdfs["hex_protection.gpkg"][["hex_id","iucn_frac"]].drop_duplicates("hex_id"),
                        on="hex_id",how="left")

cols=["conv_score","sig_socs","sig_landsys","prot_frac"]
print("\n=== JOIN COVERAGE (non-null) ===")
for c in cols:
    nn=master[c].notna().sum(); print(f"  {c:12s}: {nn:6d}/{len(master)}  null={len(master)-nn}")

# --- correlations ---
print("\n=== CORRELATION MATRIX (Pearson, pairwise) ===")
print(master[cols].corr().round(3).to_string())
sp=master[["sig_socs","sig_landsys"]].dropna()
print(f"\nsig_socs vs sig_landsys: Pearson={sp['sig_socs'].corr(sp['sig_landsys']):.3f}  "
      f"Spearman={sp['sig_socs'].corr(sp['sig_landsys'],method='spearman'):.3f}  n={len(sp)}")

# --- PROVISIONAL exposure (significance=MAX placeholder; NOT locked) ---
m=master.copy()
for c in cols: m[c]=m[c].fillna(0)
m["significance_prov"]=m[["sig_socs","sig_landsys"]].max(axis=1)
m["exposure_prov"]=m["significance_prov"]*m["conv_score"]*(1-m["prot_frac"])
master["significance_prov"]=m["significance_prov"]; master["exposure_prov"]=m["exposure_prov"]

print("\n=== PROVISIONAL EXPOSURE (significance=MAX placeholder; NOT a locked decision) ===")
e=m["exposure_prov"]
print(f"  min/mean/median/max : {e.min():.3f}/{e.mean():.3f}/{e.median():.3f}/{e.max():.3f}")
print(f"  zero-exposure hexes : {(e==0).sum()}  ({100*(e==0).mean():.1f}%)")
for q in [0.5,0.75,0.9,0.95,0.99]:
    print(f"  p{int(q*100):02d}                 : {e.quantile(q):.3f}")

# --- write + validate ---
master.to_file(p("hex_master.gpkg"),driver="GPKG")
master.drop(columns="geometry").to_csv(p("hex_master_qa.csv"),index=False)
print("\n=== VALIDATION ===")
print(f"  master rows       : {len(master)} (expect 16229)")
print(f"  hex_id unique     : {master['hex_id'].is_unique}")
print(f"  any NaN in scores : {master[cols].isna().any().any()}")
print(f"  exposure_prov NaN : {master['exposure_prov'].isna().sum()}")
print(f"  significance src  : {'COMBINED hex_significance.gpkg' if SIG_COMBINED else 'SEPARATE socs+landsys'}")
print("  wrote: hex_master.gpkg, hex_master_qa.csv")
