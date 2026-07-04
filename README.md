# A transparent Territory-wide conservation exposure index and its validation against expert biodiversity assessment

Open-data conservation exposure surface for the Northern Territory (16,229 hexes, 86.6 sq km,
EPSG:3577), with a construction-choice sensitivity analysis and an independent validation
against the expert biodiversity risk assessment of the central Roper River catchment.

## Key finding

The exposure surface agrees only weakly with expert biodiversity risk (Spearman rho = 0.24;
spatial-autocorrelation-corrected 95% CI 0.05 to 0.43; p = 0.065), and that agreement is
carried by the convertibility axis, not by the biodiversity-significance axis the index was
built around. Priorities decompose into a robust core (946 hexes stable across all 30
construction variants) and a construction-sensitive fringe (860 hexes).

## Repository structure

- paper/            Manuscript (MANUSCRIPT.md), section drafts, and paper figures
- analysis/         Frozen validation pipeline: scripts, outputs, figures, README
- pipeline_build/   Scripts that built hex_master.gpkg (provenance)
- pipeline_build/diagnostics/   One-off data-inspection helpers (provenance)
- figures/          Component-layer figures (convertibility, significance, etc.)
- docs/             CHANGELOG and project documentation
- data/             Input layers (licensed NT/Aus Gov data; not redistributed)

## Reproduce the analysis

    pip install -r requirements.txt
    cd analysis
    ./run_all.sh ../data/hex_master.gpkg ../data/roper_intersection.gpkg

All outputs regenerate from the two input geopackages; random seeds fixed at 42.
See analysis/README_analysis.md for per-script provenance of every reported number.

## Manuscript

paper/MANUSCRIPT.md is the full draft. Every quantitative claim traces to a file in
analysis/outputs_*. Reference list and target-journal formatting are pending.

## Data availability

Input spatial layers are open NT and Australian Government data (licensed; not redistributed
here). Analysis code is released under the terms in LICENSE_CODE.txt.

## Validation benchmark

Buckley, K., Leiper, I., Nano, C., Wedd, D. and Wilson, D. (2024). Mapping the Future -
Biodiversity assessment of the central Roper River catchment. Technical Report 14/2024,
Department of Environment, Parks and Water Security, Northern Territory Government, Darwin.
