#!/usr/bin/env bash
# Reproduce the full evidence base. Requires hex_master.gpkg and roper_intersection.gpkg.
set -euo pipefail
HEX="${1:-data/hex_master.gpkg}"
ROP="${2:-data/roper_intersection.gpkg}"
echo "[1/4] Step 1 — construction sensitivity"
python sensitivity_analysis.py --master "$HEX" --outdir outputs_sensitivity
echo "[2/4] Step 3 — Roper validation + circularity checks"
python roper_validation.py         # paths hard-set inside; edit if relocating inputs
echo "[3/4] Step 2 — spatial-autocorrelation correction"
python spatial_correction.py
echo "[4/4] publication figures"
python make_figures.py
echo "DONE — see outputs_sensitivity/, outputs_roper/, figures_paper/"
