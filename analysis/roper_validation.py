#!/usr/bin/env python
"""
roper_validation.py — Step 3: validate the open-data exposure proxy against the
expert BIORISK assessment (central Roper catchment), per the LOCKED design.

LOCKED HIERARCHY
  Primary contribution : transparent Territory-wide conservation EXPOSURE framework.
  Primary validation   : full exposure vs BIORISK (Spearman, area-weighted, ordinal).
  Mandatory decomposition (defends the primary, quantifies shared-input inflation):
      - significance-only            vs BIORISK
      - SOCS-removed exposure        vs BIORISK   (circularity-controlled result)
      - convertibility-only          vs BIORISK   (reference floor)
      - protection-only              vs BIORISK   (reference floor)
  Categorical robustness : weighted kappa + confusion matrix; imbalance-aware
                           precision/recall on the "class-4-and-above" cut.

LOCKED CAVEATS (surfaced in output, not deferred)
  n=244 hexes, one catchment; BIORISK effectively 2-class by area (3=77%, 4=23%;
  class 5 = 0.1% km2, NOT validatable as a class); BIORISK carries no protection
  content (so agreement cannot confirm the (1-P) moderator); SOCS is a shared input.

EXPOSURE FORMULATION (matches Step-1 ensemble; equal weights => plain product)
  significance = combine(sig_socs, sig_landsys)         # candidate rules
  exposure     = significance * conv_score * (1 - prot_frac)   # locked architecture

IMPLEMENTATION DECISIONS (documented; none change the scientific conclusion):
  D1. BIORISK geometry is recovered from roper_intersection.gpkg (the risk x land-use
      intersection); the raw MTF_Roper.gdb was not provided. Verified: total area
      17,254.1 km2 == report's 1,725,411 ha; 244 hexes overlap; classes {1,3,4,5}.
  D2. Partial-coverage hexes: PRIMARY uses all 244 hexes, area-weighting BIORISK over
      whatever assessed area falls in each hex. A >=50%-coverage subset is reported as
      a sensitivity check so the coverage choice is shown not to drive the result.
  D3. Per-hex BIORISK aggregation: area-weighted MEAN of the ordinal class (primary,
      valid because classes are ordered 1<3<4<5) AND area-majority class (categorical).
  D4. Significance rule for the PRIMARY exposure = 'mean' (the Step-1 standing candidate:
      parsimonious, inside the agreeing cluster). All candidate rules are ALSO reported
      so the choice is transparent and Roper's (in)ability to discriminate is visible.
  D5. Spearman is computed on the hex-level pairs; bootstrap CIs by resampling hexes
      (n=244) 5,000x. Spatial autocorrelation is NOT corrected here (that is Step-2);
      CIs are therefore optimistic and this is stated.

READS  /mnt/user-data/uploads/hex_master.gpkg, /mnt/user-data/uploads/roper_intersection.gpkg
WRITES outputs_roper/  (tables, confusion matrix, decomposition, bootstrap, summary, verdict.json)
"""
import os, json, itertools
import numpy as np, pandas as pd, geopandas as gpd
from scipy.stats import spearmanr

OUT = "outputs_roper"; os.makedirs(OUT, exist_ok=True)
HEX = "/mnt/user-data/uploads/hex_master.gpkg"
ROP = "/mnt/user-data/uploads/roper_intersection.gpkg"
SEED = 42; rng = np.random.default_rng(SEED)

# ----------------------------------------------------------------------
# LOAD + PREP
# ----------------------------------------------------------------------
hexes = gpd.read_file(HEX).to_crs(3577)
for c in ["conv_score", "sig_socs", "sig_landsys", "prot_frac"]:
    hexes[c] = hexes[c].fillna(0.0)
hexes["hex_area_km2"] = hexes.area / 1e6

roper = gpd.read_file(ROP).to_crs(3577)
if (~roper.is_valid).any():
    roper["geometry"] = roper.buffer(0)

# ----------------------------------------------------------------------
# EXPOSURE FAMILY
# ----------------------------------------------------------------------
def combine_sig(socs, land, rule):
    if rule == "max":   return np.maximum(socs, land)
    if rule == "mean":  return 0.5 * (socs + land)
    if rule == "w70_socs": return 0.7*socs + 0.3*land
    if rule == "w70_land": return 0.3*socs + 0.7*land
    if rule == "pctnorm_mean":
        return 0.5*(pd.Series(socs).rank(pct=True).to_numpy()
                    + pd.Series(land).rank(pct=True).to_numpy())
    raise ValueError(rule)

def build_surfaces(df, sig_rule):
    socs, land = df["sig_socs"].to_numpy(), df["sig_landsys"].to_numpy()
    conv, prot = df["conv_score"].to_numpy(), df["prot_frac"].to_numpy()
    sig = combine_sig(socs, land, sig_rule)
    return {
        "exposure_full":  sig * conv * (1 - prot),
        "significance":   sig,
        "exposure_SOCSremoved": land * conv * (1 - prot),   # circularity-controlled
        "convertibility": conv,
        "protection":     prot,
        "sig_socs_only":  socs,
        "sig_landsys_only": land,
    }

PRIMARY_RULE = "mean"   # D4

# ----------------------------------------------------------------------
# AGGREGATE BIORISK -> HEX  (area-weighted mean + majority class + coverage)
# ----------------------------------------------------------------------
rd = roper[["BIORISK", "geometry"]].copy()
ov = gpd.overlay(hexes[["hex_id", "hex_area_km2", "geometry"]], rd,
                 how="intersection", keep_geom_type=True)
ov["piece_km2"] = ov.area / 1e6

# area-weighted mean ordinal BIORISK, coverage fraction, and majority class per hex
def agg_hex(g):
    tot = g["piece_km2"].sum()
    awm = np.average(g["BIORISK"], weights=g["piece_km2"])
    maj = g.groupby("BIORISK")["piece_km2"].sum().idxmax()
    return pd.Series({"biorisk_awm": awm, "biorisk_majority": maj,
                      "roper_km2": tot, "hex_area_km2": g["hex_area_km2"].iloc[0]})
agg = ov.groupby("hex_id").apply(agg_hex, include_groups=False).reset_index()
agg["coverage_frac"] = (agg["roper_km2"] / agg["hex_area_km2"]).clip(0, 1)

# attach proxy surfaces (primary rule) to the validated hexes
surf = build_surfaces(hexes, PRIMARY_RULE)
proxy = hexes[["hex_id"]].copy()
for k, v in surf.items():
    proxy[k] = v
val = agg.merge(proxy, on="hex_id", how="left")
n_all = len(val)
val50 = val[val["coverage_frac"] >= 0.5].copy()
print(f"validated hexes: {n_all}  (>=50% coverage: {len(val50)})")
print(f"BIORISK awm range: {val['biorisk_awm'].min():.2f}–{val['biorisk_awm'].max():.2f}")

# ----------------------------------------------------------------------
# SPEARMAN + BOOTSTRAP  (primary = exposure_full; full decomposition)
# ----------------------------------------------------------------------
DECOMP = ["exposure_full", "significance", "exposure_SOCSremoved",
          "convertibility", "protection", "sig_socs_only", "sig_landsys_only"]

def boot_spearman(x, y, nb=5000):
    x, y = np.asarray(x), np.asarray(y)
    n = len(x)
    obs = spearmanr(x, y).correlation
    idx = rng.integers(0, n, size=(nb, n))
    bs = np.array([spearmanr(x[i], y[i]).correlation for i in idx])
    lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    return obs, lo, hi

def run_block(df, tag):
    rows = []
    y = df["biorisk_awm"].to_numpy()
    for s in DECOMP:
        rho, lo, hi = boot_spearman(df[s].to_numpy(), y)
        rows.append(dict(surface=s, spearman=round(rho,4),
                         ci_lo=round(lo,4), ci_hi=round(hi,4),
                         n=len(df), subset=tag))
    return pd.DataFrame(rows)

res_all = run_block(val, "all_244")
res_50  = run_block(val50, "cov>=50%")
results = pd.concat([res_all, res_50], ignore_index=True)
results.to_csv(f"{OUT}/decomposition_spearman.csv", index=False)

# ----------------------------------------------------------------------
# CATEGORICAL ROBUSTNESS  (confusion + weighted kappa on class-4-and-above cut)
# ----------------------------------------------------------------------
from sklearn.metrics import cohen_kappa_score, confusion_matrix, precision_score, recall_score

# expert positive = "sensitive or better" (BIORISK majority >= 4); imbalance-aware
val["expert_pos"] = (val["biorisk_majority"] >= 4).astype(int)
# proxy positive = top-decile exposure within the validated set (matched prevalence-free)
thr = np.quantile(val["exposure_full"], 1 - val["expert_pos"].mean())
val["proxy_pos"] = (val["exposure_full"] >= thr).astype(int)
cm = confusion_matrix(val["expert_pos"], val["proxy_pos"])
prec = precision_score(val["expert_pos"], val["proxy_pos"], zero_division=0)
rec  = recall_score(val["expert_pos"], val["proxy_pos"], zero_division=0)
# weighted kappa on the ordinal majority class (rounded proxy tertiles -> ordinal)
val["proxy_ord"] = pd.qcut(val["exposure_full"].rank(method="first"),
                           q=[0,.5,.77,.99,1.0], labels=[1,3,4,5]).astype(int)
kappa_lin = cohen_kappa_score(val["biorisk_majority"], val["proxy_ord"], weights="linear")
kappa_quad= cohen_kappa_score(val["biorisk_majority"], val["proxy_ord"], weights="quadratic")

np.savetxt(f"{OUT}/confusion_matrix_class4plus.csv", cm, fmt="%d", delimiter=",")

# ----------------------------------------------------------------------
# SUMMARY + VERDICT
# ----------------------------------------------------------------------
def g(df, s): return df.loc[df.surface==s, "spearman"].iloc[0]
prim   = g(res_all, "exposure_full")
socsrm = g(res_all, "exposure_SOCSremoved")
sigp   = g(res_all, "significance")
convp  = g(res_all, "convertibility")
protp  = g(res_all, "protection")

# does agreement survive SOCS removal? (retention ratio)
retention = socsrm / prim if prim else np.nan

L = []
L.append("STEP 3 — ROPER VALIDATION (exposure vs BIORISK)  [evidence]")
L.append("="*60)
L.append(f"validated hexes           : {n_all}  (>=50% coverage: {len(val50)})")
L.append(f"BIORISK by area           : cls3=76.9%  cls4=22.6%  cls1=0.5%  cls5=0.1% (2-class effective)")
L.append("")
L.append("PRIMARY (all 244, area-weighted Spearman, 95% bootstrap CI)")
for s in DECOMP:
    r=res_all[res_all.surface==s].iloc[0]
    L.append(f"  {s:22s}: rho={r.spearman:+.3f}  [{r.ci_lo:+.3f}, {r.ci_hi:+.3f}]")
L.append("")
L.append("CIRCULARITY DECOMPOSITION")
L.append(f"  full exposure vs BIORISK          : {prim:+.3f}")
L.append(f"  SOCS-removed exposure vs BIORISK  : {socsrm:+.3f}   (retention {retention*100:.0f}% of primary)")
L.append(f"  significance-only vs BIORISK      : {sigp:+.3f}")
L.append(f"  convertibility-only (floor)       : {convp:+.3f}")
L.append(f"  protection-only (floor)           : {protp:+.3f}")
L.append("")
L.append("CATEGORICAL ROBUSTNESS (class-4-and-above = 'sensitive or better')")
L.append(f"  expert-positive hexes     : {int(val['expert_pos'].sum())}/{n_all} ({100*val['expert_pos'].mean():.0f}%)")
L.append(f"  precision / recall        : {prec:.2f} / {rec:.2f}")
L.append(f"  weighted kappa lin / quad : {kappa_lin:.3f} / {kappa_quad:.3f}")
L.append(f"  confusion matrix          : {cm.tolist()}  (rows=expert 0/1, cols=proxy 0/1)")
L.append("")
L.append("LOCKED CAVEATS")
L.append("  n=244, one catchment; BIORISK 2-class by area; class 5 (0.1%) NOT validatable;")
L.append("  BIORISK has no protection content (cannot confirm (1-P)); SOCS is shared input;")
L.append("  CIs not spatial-autocorrelation-corrected (Step 2) -> optimistic.")
L.append("")
# interpretation flag (evidence-driven, not a lock)
if prim >= 0.3 and retention >= 0.7:
    verdict = "AGREEMENT_ROBUST"; note="Exposure agrees with expert risk; agreement largely survives SOCS removal."
elif prim >= 0.3 and retention < 0.7:
    verdict = "AGREEMENT_SOCS_DRIVEN"; note="Exposure agrees, but agreement is substantially SOCS-driven (shared input)."
elif prim < 0.3 and prim >= 0.15:
    verdict = "AGREEMENT_WEAK"; note="Weak agreement; interpret cautiously given imbalance/one-catchment."
else:
    verdict = "AGREEMENT_ABSENT"; note="Little to no rank agreement in this catchment."
L.append(f"EVIDENCE FLAG: {verdict} — {note}")
summary = "\n".join(L)
print("\n"+summary)
with open(f"{OUT}/decision_summary.txt","w") as f: f.write(summary+"\n")

with open(f"{OUT}/verdict.json","w") as f:
    json.dump(dict(verdict=verdict, n=n_all, n_cov50=len(val50),
                   primary_spearman=float(prim), socsremoved_spearman=float(socsrm),
                   retention=float(retention), significance_spearman=float(sigp),
                   convertibility_floor=float(convp), protection_floor=float(protp),
                   precision=float(prec), recall=float(rec),
                   kappa_linear=float(kappa_lin), kappa_quadratic=float(kappa_quad),
                   primary_rule=PRIMARY_RULE, seed=SEED), f, indent=2)

# candidate-rule discrimination: can Roper distinguish significance rules? (SOCS-removed is identical
# across rules, so this asks whether the SOCS-heavy rules gain agreement only via shared input)
rule_rows=[]
for rule in ["max","mean","w70_socs","w70_land","pctnorm_mean"]:
    s=build_surfaces(hexes, rule)
    p=hexes[["hex_id"]].copy(); p["exposure_full"]=s["exposure_full"]; p["significance"]=s["significance"]
    m=agg.merge(p,on="hex_id",how="left")
    r_exp=spearmanr(m["exposure_full"], m["biorisk_awm"]).correlation
    r_sig=spearmanr(m["significance"], m["biorisk_awm"]).correlation
    rule_rows.append(dict(rule=rule, exposure_vs_biorisk=round(r_exp,4), significance_vs_biorisk=round(r_sig,4)))
pd.DataFrame(rule_rows).to_csv(f"{OUT}/rule_discrimination.csv", index=False)
print("\nrule discrimination ->", f"{OUT}/rule_discrimination.csv")

# ----------------------------------------------------------------------
# CONVERTIBILITY CIRCULARITY CHECK
#   Is conv-vs-BIORISK agreement definitional via BIORISK class 1 (Highly modified,
#   land-use-defined)? Test: (a) BIORISK x ALUM area crosstab, (b) drop class-1-touching
#   hexes, (c) restrict to the pure 3-vs-4 biodiversity contrast. If agreement survives
#   (b) and (c), it is genuine, not a land-use tautology.
# ----------------------------------------------------------------------
ov_ba = gpd.overlay(hexes[["hex_id","hex_area_km2","geometry"]],
                    roper[["BIORISK","PRIM_NO","geometry"]], how="intersection",
                    keep_geom_type=True)
ov_ba["piece_km2"] = ov_ba.area/1e6
crosstab = (ov_ba.pivot_table(index="BIORISK", columns="PRIM_NO",
            values="piece_km2", aggfunc="sum").fillna(0).round(2))
crosstab.to_csv(f"{OUT}/circularity_biorisk_x_alum_km2.csv")

# per-hex flags: any class-1 area, and awm using only classes {3,4}
def _agg_c1(g):
    return pd.Series({"biorisk_awm": np.average(g["BIORISK"], weights=g["piece_km2"]),
                      "has_c1": bool((g["BIORISK"]==1).any())})
a_c1 = ov_ba.groupby("hex_id").apply(_agg_c1, include_groups=False).reset_index()
conv_col = hexes[["hex_id","conv_score"]]
m_c1 = a_c1.merge(conv_col, on="hex_id")
rho_all   = spearmanr(m_c1["conv_score"], m_c1["biorisk_awm"]).correlation
noc1      = m_c1[~m_c1["has_c1"]]
rho_noc1  = spearmanr(noc1["conv_score"], noc1["biorisk_awm"]).correlation
ov34 = ov_ba[ov_ba["BIORISK"].isin([3,4])]
a34 = (ov34.assign(w=ov34["BIORISK"]*ov34["piece_km2"]).groupby("hex_id")
       .apply(lambda g: g["w"].sum()/g["piece_km2"].sum(), include_groups=False)
       .rename("awm34").reset_index().merge(conv_col, on="hex_id"))
rho_34 = spearmanr(a34["awm34"], a34["conv_score"]).correlation
circ = dict(conv_vs_biorisk_all=round(float(rho_all),4),
            n_hexes_touching_class1=int(m_c1["has_c1"].sum()),
            conv_vs_biorisk_excl_class1=round(float(rho_noc1),4),
            n_excl_class1=int(len(noc1)),
            conv_vs_biorisk_3v4_only=round(float(rho_34),4),
            class1_total_km2=round(float(ov_ba.loc[ov_ba["BIORISK"]==1,"piece_km2"].sum()),2),
            interpretation="genuine if excl_class1 and 3v4_only remain clearly positive")
pd.DataFrame([circ]).to_csv(f"{OUT}/circularity_convertibility_check.csv", index=False)
print("circularity check ->", f"{OUT}/circularity_convertibility_check.csv")
print("all outputs ->", OUT)
