# Validation & sensitivity analysis — reproducible evidence base

This directory contains the analytical pipeline for the conservation exposure validation.
All quantitative claims in the manuscript trace to files produced here.

## Inputs (not redistributed; licensed NT Government layers)
- `hex_master.gpkg` — 16,229-hex Territory grid (EPSG:3577) with `conv_score`, `sig_socs`,
  `sig_landsys`, `prot_frac`, and provisional exposure fields.
- `roper_intersection.gpkg` — expert BIORISK × land-use intersection, central Roper catchment.
  Verified: total area 17,254.1 km² = report's 1,725,411 ha; 244 hexes overlap the grid.

## Pipeline (frozen)
| Script | Produces | Key outputs |
|---|---|---|
| `sensitivity_analysis.py` | construction-choice robustness | `outputs_sensitivity/{verdict.json, sensitivity_rank_stability.csv, hotspot_persistence.csv, axis_attribution.csv, sig_rule_attribution.csv, core_fringe_summary.csv, fig_hotspot_persistence.png}` |
| `roper_validation.py` | exposure vs BIORISK + decomposition + circularity | `outputs_roper/{verdict.json, decomposition_spearman.csv, rule_discrimination.csv, circularity_convertibility_check.csv, circularity_biorisk_x_alum_km2.csv, confusion_matrix_class4plus.csv}` |
| `spatial_correction.py` | Moran's I, effective-n, spatial CIs | `outputs_roper/{spatial_correction.json, spatial_correction.txt}` |
| `make_figures.py` | publication figures | `figures_paper/{fig1_decomposition.png, fig2_persistence.png, fig3_morans_i.png}` |

## Reproduce
```bash
pip install -r requirements-analysis.txt
./run_all.sh path/to/hex_master.gpkg path/to/roper_intersection.gpkg
```
Seeds fixed at 42. `roper_validation.py` and `spatial_correction.py` currently read inputs
from `/mnt/user-data/uploads/`; edit the paths at the top of each if relocating.

## Headline results (all traceable)
- **Sensitivity:** min pairwise Spearman 0.741, mean 0.931; top-decile persistence 58.3%
  (formal verdict B_UNSTABLE); bimodal — 946 core hexes (all 30 variants) vs 860 fringe;
  instability driven by the significance-combination rule (mean Spearman 0.950 vs 0.979/0.960).
- **Validation:** exposure vs BIORISK ρ = 0.240, spatial 95% CI [0.051, 0.428], p = 0.065
  (n_eff ≈ 60). Carried by convertibility (0.177), not significance (0.038). SOCS-removal
  retention 101% (no shared-input inflation). Convertibility agreement genuine, not
  definitional (0.145 excl. class-1; 0.165 on 3-vs-4 contrast). Categorical: precision/recall
  0.10, weighted kappa < 0.05.

## Caveats (carried with all results)
n = 244 (one catchment, n_eff ≈ 60); BIORISK 2-class by area, class 5 (0.1%) not validatable;
no protection content in benchmark; SOCS near-absent locally (6/244 hexes); catchment
environmentally atypical (high significance, low convertibility).
