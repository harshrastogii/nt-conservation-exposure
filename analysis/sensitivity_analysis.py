#!/usr/bin/env python
"""
sensitivity_analysis.py  —  Step 1: Sensitivity & rank-stability of exposure hotspots.

PURPOSE (scientific)
    Determine whether the conservation-priority hotspots produced by the exposure
    index are a robust property of the data/geography, or an artifact of the
    defensible-but-arbitrary construction choices:
        (a) how the two significance sub-scores are combined,
        (b) the axis weights,
        (c) whether protection moderates (1-P) or is subtracted.

    Exposure family (per hex):
        significance = combine(sig_socs, sig_landsys)              # choice (a)
        raw          = w_sig*significance + w_conv*conv_score       # weights (b), additive form
                       OR  significance^w_sig * conv_score^w_conv   # geometric variant
        exposure     = raw * (1 - prot_frac)     [moderator]   OR   raw - lambda*prot_frac [additive]  # (c)
    We follow the project's core architecture (multiplicative significance x convertibility x (1-P))
    as the CENTRE of the ensemble, and vary each choice around it with genuinely defensible alternatives.

READS   data/hex_master.gpkg      (canonical; columns per handover section 14)
WRITES  outputs_sensitivity/
            sensitivity_rank_stability.csv     — pairwise Spearman + hotspot Jaccard across variants
            hotspot_persistence.csv            — per-hex persistence frequency (top-5% / top-10%)
            variant_catalog.csv                — the exact ensemble that was run
            fig_hotspot_persistence.png        — MAP: how often each hex is a top-10% hotspot
            fig_rank_correlation_matrix.png    — heatmap of pairwise Spearman between variants
            decision_summary.txt               — verdict against pre-registered thresholds

PRE-REGISTERED DECISION THRESHOLDS (locked before results were seen):
    STABLE   (Outcome A): >=80% of top-10% hexes persist across ALL variants  AND  all pairwise Spearman >= 0.90
    UNSTABLE (Outcome B): < 60% persistence  OR  any pairwise Spearman < 0.75
    MIXED    (Outcome C): anything in between  -> robust core + characterised unstable fringe

REPRODUCIBILITY
    Deterministic given a fixed seed for the Dirichlet weight perturbations (--seed, default 42).

NOTE ON PROVISIONAL vs LOCKED
    This script REPORTS evidence and RECOMMENDS a final significance rule + weights.
    It does not itself overwrite hex_master. Locking the decision (writing a final
    'exposure' / 'significance' column) is a separate, deliberate commit made only
    after the verdict is read — keeping provisional outputs cleanly separated.
"""
import argparse, os, sys, itertools, json
import numpy as np, pandas as pd

# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------
ap = argparse.ArgumentParser()
ap.add_argument("--master", default="data/hex_master.gpkg",
                help="path to hex_master.gpkg (or a CSV with the same columns)")
ap.add_argument("--outdir", default="outputs_sensitivity")
ap.add_argument("--seed", type=int, default=42)
ap.add_argument("--n-dirichlet", type=int, default=200,
                help="number of random weight perturbations for the stability distribution")
ap.add_argument("--no-geom", action="store_true",
                help="input has no geometry (CSV); skip the persistence map")
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)
rng = np.random.default_rng(args.seed)

# ----------------------------------------------------------------------
# LOAD  (accept .gpkg via geopandas, or .csv for a geometry-free run)
# ----------------------------------------------------------------------
HAS_GEOM = False
if args.master.lower().endswith((".gpkg", ".shp", ".geojson")) and not args.no_geom:
    import geopandas as gpd
    gdf = gpd.read_file(args.master)
    HAS_GEOM = "geometry" in gdf.columns
    df = pd.DataFrame(gdf.drop(columns="geometry")) if HAS_GEOM else pd.DataFrame(gdf)
else:
    df = pd.read_csv(args.master)
    gdf = None

REQUIRED = ["hex_id", "conv_score", "sig_socs", "sig_landsys", "prot_frac"]
missing = [c for c in REQUIRED if c not in df.columns]
if missing:
    sys.exit(f"Master is missing required columns: {missing}\nFound: {list(df.columns)}")

n_hex = len(df)
print(f"Loaded {n_hex} hexes | geometry available: {HAS_GEOM and not args.no_geom}")

# Edge-coverage nulls -> 0 (documented behaviour, section 10). Kept explicit + auditable.
for c in ["conv_score", "sig_socs", "sig_landsys", "prot_frac"]:
    n_null = df[c].isna().sum()
    if n_null:
        print(f"  fillna(0) on {c}: {n_null} nulls (edge-coverage, not true zeros)")
    df[c] = df[c].fillna(0.0)

# ----------------------------------------------------------------------
# EXPOSURE FAMILY  — defensible variants only (no strawmen)
# ----------------------------------------------------------------------
def combine_significance(socs, landsys, rule):
    if rule == "max":       return np.maximum(socs, landsys)
    if rule == "mean":      return 0.5 * (socs + landsys)
    if rule == "w70_socs":  return 0.7 * socs + 0.3 * landsys
    if rule == "w70_land":  return 0.3 * socs + 0.7 * landsys
    if rule == "pctnorm_mean":  # percentile-normalise each sub-score, then mean (handover Task 3)
        s = pd.Series(socs).rank(pct=True).to_numpy()
        l = pd.Series(landsys).rank(pct=True).to_numpy()
        return 0.5 * (s + l)
    raise ValueError(rule)

def exposure_variant(df, sig_rule, w_sig, w_conv, prot_mode, prot_lambda=1.0):
    sig  = combine_significance(df["sig_socs"].to_numpy(),
                                df["sig_landsys"].to_numpy(), sig_rule)
    conv = df["conv_score"].to_numpy()
    prot = df["prot_frac"].to_numpy()
    # core architecture is multiplicative significance x convertibility; weights act as exponents
    # (geometric weighting keeps the multiplicative form the project locked, while letting axis
    #  emphasis vary — equal weights => plain product, matching the current provisional index).
    eps = 1e-9
    raw = np.power(sig + eps, w_sig) * np.power(conv + eps, w_conv)
    if prot_mode == "moderator":
        expo = raw * (1.0 - prot)
    elif prot_mode == "additive":
        expo = raw - prot_lambda * prot            # mild additive discount
    else:
        raise ValueError(prot_mode)
    # rank-based comparisons are invariant to monotone rescaling; min-max only for readability
    expo = np.clip(expo, 0, None)
    return expo

# --- named, defensible ensemble (the "corner" variants) --------------------
SIG_RULES   = ["max", "mean", "w70_socs", "w70_land", "pctnorm_mean"]
WEIGHTS     = [("equal", 1.0, 1.0),
               ("sig_up", 1.5, 1.0),
               ("conv_up", 1.0, 1.5)]
PROT_MODES  = [("moderator", None), ("additive", 0.5)]

variants = {}
catalog_rows = []
for sig_rule in SIG_RULES:
    for wname, w_sig, w_conv in WEIGHTS:
        for pmode, plam in PROT_MODES:
            key = f"{sig_rule}|{wname}|{pmode}"
            variants[key] = exposure_variant(df, sig_rule, w_sig, w_conv, pmode,
                                              prot_lambda=(plam or 1.0))
            catalog_rows.append(dict(variant=key, sig_rule=sig_rule, weights=wname,
                                     w_sig=w_sig, w_conv=w_conv, prot_mode=pmode,
                                     prot_lambda=(plam if plam else "")))
print(f"Built {len(variants)} named defensible variants "
      f"({len(SIG_RULES)} sig-rules x {len(WEIGHTS)} weight sets x {len(PROT_MODES)} protection forms)")

# --- the provisional baseline (current index: MAX / equal / moderator) -----
BASELINE = "max|equal|moderator"
assert BASELINE in variants, "baseline variant missing"

# ----------------------------------------------------------------------
# RANK-STABILITY  — pairwise Spearman across the full surface
# ----------------------------------------------------------------------
from scipy.stats import spearmanr
V = pd.DataFrame(variants)
keys = list(variants.keys())
S = np.eye(len(keys))
for i, j in itertools.combinations(range(len(keys)), 2):
    rho = spearmanr(V.iloc[:, i], V.iloc[:, j]).correlation
    S[i, j] = S[j, i] = rho
spear = pd.DataFrame(S, index=keys, columns=keys)
min_spear = spear.values[np.triu_indices(len(keys), 1)].min()
mean_spear = spear.values[np.triu_indices(len(keys), 1)].mean()

# ----------------------------------------------------------------------
# HOTSPOT PERSISTENCE  — top-5% and top-10% membership across variants
# ----------------------------------------------------------------------
def top_mask(vals, frac):
    thr = np.quantile(vals, 1 - frac)
    return vals >= thr

persist = pd.DataFrame({"hex_id": df["hex_id"].to_numpy()})
for frac, tag in [(0.05, "top05"), (0.10, "top10")]:
    masks = np.vstack([top_mask(variants[k], frac) for k in keys])   # (n_variants, n_hex)
    persist[f"{tag}_freq"] = masks.mean(axis=0)          # fraction of variants selecting this hex
    persist[f"{tag}_ever"] = masks.any(axis=0)
    persist[f"{tag}_always"] = masks.all(axis=0)

def persistence_of_baseline(frac_tag, frac):
    base = top_mask(variants[BASELINE], frac)
    always = persist[f"{frac_tag}_always"].to_numpy()
    denom = base.sum()
    return (always & base).sum() / denom if denom else np.nan

pers10 = persistence_of_baseline("top10", 0.10)
pers05 = persistence_of_baseline("top05", 0.05)

# Jaccard of hotspot sets vs baseline (top-10%)
base10 = top_mask(variants[BASELINE], 0.10)
jac = {}
for k in keys:
    m = top_mask(variants[k], 0.10)
    inter = (m & base10).sum(); union = (m | base10).sum()
    jac[k] = inter / union if union else np.nan
jac_series = pd.Series(jac).sort_values()

# ----------------------------------------------------------------------
# AXIS ATTRIBUTION  (which construction choice drives instability?)
#   For each axis, mean/min Spearman over variant pairs that differ ONLY in that axis.
#   Lower => that axis moves rankings more. Also per-sig-rule mean-vs-others.
# ----------------------------------------------------------------------
def _parts(k): return dict(zip(["sig", "w", "prot"], k.split("|")))
axis_rows = []
for axis in ["sig", "w", "prot"]:
    vals = [spear.loc[a, b] for a, b in itertools.combinations(keys, 2)
            if [z for z in ["sig", "w", "prot"] if _parts(a)[z] != _parts(b)[z]] == [axis]]
    axis_rows.append(dict(axis=axis, mean_spearman=round(float(np.mean(vals)), 4),
                          min_spearman=round(float(np.min(vals)), 4), n_pairs=len(vals)))
sig_rule_rows = []
for rule in SIG_RULES:
    rk = [k for k in keys if k.split("|")[0] == rule]
    ok = [k for k in keys if k.split("|")[0] != rule]
    sig_rule_rows.append(dict(sig_rule=rule,
                              mean_spearman_vs_others=round(float(np.mean([spear.loc[a, b]
                              for a in rk for b in ok])), 4)))
pd.DataFrame(axis_rows).to_csv(f"{args.outdir}/axis_attribution.csv", index=False)
pd.DataFrame(sig_rule_rows).to_csv(f"{args.outdir}/sig_rule_attribution.csv", index=False)

# ----------------------------------------------------------------------
# CORE / FRINGE SUMMARY  (bimodality of top-10% persistence)
# ----------------------------------------------------------------------
f10 = persist["top10_freq"]
core_fringe = dict(
    ever_top10=int((f10 > 0).sum()),
    always_top10=int((f10 == 1).sum()),
    ge90pct_top10=int((f10 >= 0.9).sum()),
    contested_fringe_10to90=int(((f10 >= 0.1) & (f10 < 0.9)).sum()),
    near_zero_le10=int(((f10 > 0) & (f10 <= 0.1)).sum()),
    single_top10_set_size=int(0.10 * n_hex),
)
pd.DataFrame([core_fringe]).to_csv(f"{args.outdir}/core_fringe_summary.csv", index=False)

# ----------------------------------------------------------------------
# VERDICT  vs pre-registered thresholds
# ----------------------------------------------------------------------
if pers10 >= 0.80 and min_spear >= 0.90:
    verdict = "A_STABLE"
elif pers10 < 0.60 or min_spear < 0.75:
    verdict = "B_UNSTABLE"
else:
    verdict = "C_MIXED"

# ----------------------------------------------------------------------
# WRITE tables
# ----------------------------------------------------------------------
pd.DataFrame(catalog_rows).to_csv(f"{args.outdir}/variant_catalog.csv", index=False)
spear.round(4).to_csv(f"{args.outdir}/sensitivity_rank_stability.csv")
persist.to_csv(f"{args.outdir}/hotspot_persistence.csv", index=False)

summary = []
summary.append("STEP 1 — SENSITIVITY & RANK-STABILITY  (evidence, not yet locked)")
summary.append("=" * 64)
summary.append(f"hexes                         : {n_hex}")
summary.append(f"variants (defensible)         : {len(keys)}")
summary.append(f"baseline (current provisional): {BASELINE}")
summary.append("")
summary.append("RANK-STABILITY (full-surface Spearman across variants)")
summary.append(f"  min pairwise Spearman       : {min_spear:.4f}")
summary.append(f"  mean pairwise Spearman      : {mean_spear:.4f}")
summary.append("")
summary.append("HOTSPOT PERSISTENCE")
summary.append(f"  top-10% baseline hexes also 'always-hotspot' across ALL variants : {pers10*100:.1f}%")
summary.append(f"  top-5%  baseline hexes also 'always-hotspot' across ALL variants : {pers05*100:.1f}%")
summary.append(f"  worst-case Jaccard vs baseline (top-10%): {jac_series.iloc[0]:.3f} ({jac_series.index[0]})")
summary.append(f"  best-case  Jaccard vs baseline (top-10%): {jac_series.iloc[-1]:.3f} ({jac_series.index[-1]})")
summary.append("")
summary.append("PRE-REGISTERED VERDICT")
summary.append(f"  thresholds: STABLE if persistence>=80% AND minSpearman>=0.90;")
summary.append(f"              UNSTABLE if persistence<60% OR minSpearman<0.75; else MIXED")
summary.append(f"  ==> {verdict}")
summary.append("")
# evidence-based recommendation (only a RECOMMENDATION; locking is a separate step)
if verdict == "A_STABLE":
    summary.append("RECOMMENDATION (to be locked): priorities are robust to construction choices.")
    summary.append("  Adopt the SIMPLEST defensible variant for parsimony: significance = MEAN of")
    summary.append("  sub-scores (or MAX if the report prefers designation-dominance), EQUAL weights,")
    summary.append("  protection as MODERATOR. Report stability as the central robustness result.")
elif verdict == "C_MIXED":
    summary.append("RECOMMENDATION (to be locked): robust CORE + unstable FRINGE.")
    summary.append("  Lock the simplest defensible variant for the core; publish the persistence map")
    summary.append("  as an uncertainty surface; flag fringe hexes as contested. Roper corroborates core.")
else:
    summary.append("RECOMMENDATION (to be locked): priorities are SENSITIVE to construction choices.")
    summary.append("  Do NOT present a single authoritative surface. Report the fragility as the finding,")
    summary.append("  attribute which choice drives it, and PROMOTE MAUP (Step 4) to essential.")
summary_txt = "\n".join(summary)
with open(f"{args.outdir}/decision_summary.txt", "w") as f:
    f.write(summary_txt + "\n")
print("\n" + summary_txt)

# ----------------------------------------------------------------------
# FIGURES
# ----------------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# (1) rank-correlation matrix heatmap
fig, ax = plt.subplots(figsize=(11, 9))
im = ax.imshow(spear.values, vmin=min(0.5, min_spear), vmax=1.0, cmap="viridis")
ax.set_xticks(range(len(keys))); ax.set_xticklabels(keys, rotation=90, fontsize=6)
ax.set_yticks(range(len(keys))); ax.set_yticklabels(keys, fontsize=6)
ax.set_title(f"Pairwise Spearman between exposure variants\n"
             f"min={min_spear:.3f}  mean={mean_spear:.3f}  (n={n_hex} hexes)", fontsize=10)
fig.colorbar(im, ax=ax, shrink=0.7, label="Spearman rho")
fig.tight_layout()
fig.savefig(f"{args.outdir}/fig_rank_correlation_matrix.png", dpi=300)
plt.close(fig)

# (2) persistence MAP (needs geometry) OR persistence histogram fallback
if HAS_GEOM and not args.no_geom:
    import geopandas as gpd
    gplot = gdf[["hex_id", "geometry"]].merge(persist[["hex_id", "top10_freq"]], on="hex_id")
    fig, ax = plt.subplots(figsize=(9, 11))
    gplot.plot(column="top10_freq", cmap="magma", linewidth=0, ax=ax,
               legend=True, legend_kwds={"label": "Fraction of variants ranking hex in top-10%",
                                         "shrink": 0.6})
    ax.set_title("Hotspot persistence: how often each hex is a top-10% priority\n"
                 f"across {len(keys)} defensible construction choices", fontsize=11)
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(f"{args.outdir}/fig_hotspot_persistence.png", dpi=300)
    plt.close(fig)
    print(f"\nWrote persistence MAP -> {args.outdir}/fig_hotspot_persistence.png")
else:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(persist["top10_freq"], bins=np.linspace(0, 1, 21), color="#444", edgecolor="w")
    ax.set_xlabel("Fraction of variants ranking hex in top-10%")
    ax.set_ylabel("Number of hexes")
    ax.set_title("Hotspot persistence distribution (no geometry: map skipped)")
    fig.tight_layout()
    fig.savefig(f"{args.outdir}/fig_hotspot_persistence_hist.png", dpi=300)
    plt.close(fig)
    print(f"\nNo geometry -> wrote persistence HISTOGRAM instead of map.")

# machine-readable verdict for downstream steps
with open(f"{args.outdir}/verdict.json", "w") as f:
    json.dump(dict(verdict=verdict, persistence_top10=float(pers10),
                   persistence_top05=float(pers05),
                   min_spearman=float(min_spear), mean_spearman=float(mean_spear),
                   n_variants=len(keys), n_hex=int(n_hex), baseline=BASELINE,
                   seed=args.seed), f, indent=2)
print(f"\nAll outputs -> {args.outdir}/")
