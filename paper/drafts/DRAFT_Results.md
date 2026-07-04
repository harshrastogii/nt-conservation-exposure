# Results

> **Provenance note (delete before submission).** Every quantitative claim below is
> traceable to a reproducible output file. Source files are cited inline in
> `[brackets]`. The three scripts that regenerate all outputs are
> `sensitivity_analysis.py`, `roper_validation.py`, and `spatial_correction.py`;
> inputs are `hex_master.gpkg` (16,229 hexes) and `roper_intersection.gpkg`.
> Numbers are reported to the precision stored in the output files.

## 1. Construction-choice sensitivity of the exposure surface

The exposure index requires three construction choices that are individually defensible
but not uniquely determined: how the two significance sub-scores are combined, how the
value and convertibility axes are weighted, and whether protection acts as a multiplicative
moderator or an additive discount. To establish whether the resulting conservation
priorities are a property of the data rather than of these choices, we computed exposure
under an ensemble of 30 defensible variants (five significance rules × three weight sets ×
two protection forms) across all 16,229 Territory hexes and compared the resulting
rankings [`outputs_sensitivity/sensitivity_rank_stability.csv`].

Across the ensemble, full-surface rank agreement was high on average but not uniform: the
mean pairwise Spearman correlation between variants was 0.931, with a minimum of 0.741
[`outputs_sensitivity/verdict.json`]. Hotspot membership was more sensitive than the
full-surface correlations imply. Of the top-decile (top-10%) priority hexes under the
baseline variant, 58.3% remained in the top decile under *all* 30 variants
[`outputs_sensitivity/verdict.json`, `persistence_top10`]; the equivalent figure for the
top-5% set was 44.5%.

The distribution of hotspot persistence was strongly bimodal rather than diffuse
[`outputs_sensitivity/core_fringe_summary.csv`]. Of 2,379 hexes that entered the top decile
under at least one variant, 946 did so under every variant and 1,184 under at least 90% of
variants, while only 860 fell in the contested band between 10% and 90% of variants. That
is, roughly half of any single top-decile priority set is stable to all reasonable
construction choices, and the instability is concentrated in a minority fringe rather than
spread across the surface. Figure S1 maps this persistence across the Territory
[`outputs_sensitivity/fig_hotspot_persistence.png`].

Attribution of the instability to specific choices shows that it is driven almost entirely
by the significance-combination rule [`outputs_sensitivity/axis_attribution.csv`]. Holding
all else fixed, varying only the significance rule reduced mean pairwise Spearman to 0.950
(minimum 0.806), whereas varying only the axis weights or only the protection form left it
at 0.979 and 0.960 respectively. Within the significance rules, the percentile-normalised
mean was the principal outlier (mean 0.885 versus all others; the four remaining rules
clustered at 0.921–0.940) [`outputs_sensitivity/sig_rule_attribution.csv`].

Under the analysis's pre-registered thresholds (stable if ≥80% persistence and minimum
Spearman ≥0.90; unstable if <60% persistence or any Spearman <0.75), the ensemble is
formally classified as sensitive [`outputs_sensitivity/verdict.json`, `verdict =
B_UNSTABLE`], as the 58.3% persistence falls just below the 60% cutoff. The bimodal
persistence distribution and the concentration of instability in a single construction
axis are the basis on which this is interpreted, in the Discussion, as a robust priority
core with a construction-sensitive fringe rather than a globally unstable surface.

## 2. Validation against the expert biodiversity assessment

### 2.1 Data and aggregation

The independent benchmark is the expert biodiversity risk classification (`BIORISK`) of the
central Roper River catchment (NT Government Technical Report 14/2024). `BIORISK` is an
ordinal five-class scale (1 Nil → 5 High biodiversity value); classes present in the mapped
data are {1, 3, 4, 5}, class 2 being undistinguished from class 3 in the source. By assessed
area the classification is effectively two-class: class 3 (Mitigable) covers 76.9% and class
4 (Sensitive/significant vegetation) 22.6%, with classes 1 and 5 covering 0.5% and 0.1%
respectively [`outputs_roper/circularity_biorisk_x_alum_km2.csv`, row sums]. The assessment
polygons were aggregated to the exposure hex grid, yielding 244 validated hexes (1.5% of the
Territory grid), of which 196 have at least 50% areal coverage by the assessment
[`outputs_roper/verdict.json`, `n`, `n_cov50`]. Per-hex `BIORISK` was computed as the
area-weighted mean of the ordinal class.

### 2.2 Primary result: exposure versus expert risk

The primary comparison is the full exposure surface against area-weighted `BIORISK` over the
244 hexes. The Spearman rank correlation was ρ = 0.240
[`outputs_roper/verdict.json`, `primary_spearman`]. Because adjacent hexes are strongly
autocorrelated in both the proxy and the benchmark (Moran's I = 0.761 for exposure and 0.406
for `BIORISK`, both p = 0.001) [`outputs_roper/spatial_correction.json`, `moran`], inference
was corrected for spatial dependence. A spatial block-bootstrap 95% confidence interval was
[0.051, 0.428], and an effective-sample-size correction (n_eff ≈ 60 of 244) gave a modified
t-test p = 0.065 [`outputs_roper/spatial_correction.json`]. The agreement is therefore a
weak positive whose lower confidence bound remains above zero but which is only marginally
significant once spatial dependence is accounted for. For comparison, the uncorrected
(independence-assuming) bootstrap interval was [0.114, 0.361]
[`outputs_roper/decomposition_spearman.csv`, `subset = all_244`]; the spatial correction
widens the interval substantially, as expected. Restricting to hexes with ≥50% coverage
raised the point estimate to ρ = 0.315 [`outputs_roper/decomposition_spearman.csv`, `subset
= cov>=50%`].

### 2.3 Decomposition: where the agreement comes from

To determine which components of the exposure index carry the agreement, each component and
a circularity-controlled variant were correlated against `BIORISK`
[`outputs_roper/decomposition_spearman.csv`; `outputs_roper/verdict.json`]:

| Surface | Spearman vs BIORISK | Spatial 95% CI |
|---|---|---|
| Full exposure | 0.240 | [0.051, 0.428] |
| Exposure, SOCS removed | 0.242 | [0.053, 0.431] |
| Convertibility only | 0.177 | [0.028, 0.371] |
| Significance only | 0.038 | [−0.225, 0.281] |
| Protection only | −0.013 | — |

Source: point estimates `outputs_roper/verdict.json`; spatial CIs
`outputs_roper/spatial_correction.json`, `block_ci`.

Three features stand out. First, the agreement is carried by the convertibility axis
(ρ = 0.177), while the biodiversity-significance axis contributes essentially nothing in
rank terms (ρ = 0.038, confidence interval spanning zero). Second, removing the SOCS input —
the layer shared between the proxy and the assessment, and the source of the anticipated
circularity — left the exposure agreement unchanged (0.242 versus 0.240, a retention of
101%) [`outputs_roper/verdict.json`, `retention`], indicating that shared-input inflation is
not operating: the significance axis carries too little agreement to inflate anything.
Third, protection alone is uncorrelated with `BIORISK` (ρ = −0.013), consistent with the
benchmark carrying no protection information.

### 2.4 Is the convertibility agreement genuine or definitional?

Because `BIORISK` class 1 ("Highly modified") is partly defined by land use, the
convertibility–`BIORISK` agreement could in principle be tautological. Three checks indicate
it is not [`outputs_roper/circularity_convertibility_check.csv`;
`outputs_roper/circularity_biorisk_x_alum_km2.csv`]. Class 1 accounts for only 77 km² of the
17,254 km² assessed (0.5%). Excluding all 57 hexes touching any class-1 area left the
correlation clearly positive (ρ = 0.145, n = 187). Restricting to the pure class-3-versus-4
biodiversity contrast — Mitigable woodland versus sensitive/significant vegetation, with no
highly-modified or land-use-definitional component — retained ρ = 0.165. The convertibility
agreement therefore reflects a genuine, if modest, correspondence between low agricultural
convertibility and higher expert-assessed biodiversity value, not a definitional artefact.

### 2.5 Categorical agreement and rule discrimination

At the level of identifying the specific hexes experts flagged as sensitive or better
(`BIORISK` ≥ 4; 29 of 244 hexes), the proxy performed near chance: precision and recall were
both 0.10, and weighted kappa was 0.024 (linear) / 0.049 (quadratic)
[`outputs_roper/verdict.json`; confusion matrix in
`outputs_roper/confusion_matrix_class4plus.csv`]. This is consistent with the weak rank
correlation: a modest monotone trend exists across the bulk of the catchment, but the proxy
does not pinpoint the high-value minority.

The validation could not discriminate among the candidate significance rules. Full-exposure
agreement with `BIORISK` was 0.240–0.243 for the four sensible rules (max, mean, and the two
70/30 blends) and lower only for the percentile-normalised mean (0.171)
[`outputs_roper/rule_discrimination.csv`], because the agreement resides in the shared
convertibility factor rather than in the significance term that distinguishes the rules.

### 2.6 Scope and inference caveats

These results are subject to constraints recorded with the analysis
[`outputs_roper/decision_summary.txt`]: a single catchment of 244 hexes (effective n ≈ 60
after spatial correction), a benchmark that is effectively two-class by area with class 5
(0.1%) not validatable as a class, a benchmark carrying no protection information (so the
agreement cannot confirm the protection moderator), and a catchment that occupies an
environmentally narrow slice of the Territory (high land-system significance, low
convertibility). SOCS is near-absent in this catchment (non-zero in 6 of 244 hexes), so the
near-zero SOCS correlation reflects low local variance rather than a general failure of the
SOCS layer.
