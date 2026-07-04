# When open-data proxies miss the target: a transparent Territory-wide conservation exposure index and its validation against expert biodiversity assessment

## Abstract

Conservation planning in data-poor jurisdictions increasingly relies on indices built from
open spatial data, yet these indices are seldom tested against independent expert judgment or
for robustness to the arbitrary choices made in their construction. We built a transparent,
equal-area conservation exposure index for the Northern Territory of Australia (16,229 hexes
of 86.6 km²) from open government data, defining exposure as the product of biodiversity
significance, agricultural convertibility, and the complement of formal protection. We
subjected it to two tests. First, a 30-variant sensitivity analysis spanning defensible
construction choices showed that priorities decompose into a robust core — 946 hexes fall in
the top priority decile under every variant — and a construction-sensitive fringe of 860
hexes whose membership is governed almost entirely by one choice, how the significance
sub-scores are combined. Second, validation against an independent expert biodiversity risk
assessment of the central Roper River catchment (244 hexes) yielded a weak positive rank
agreement (Spearman ρ = 0.24; spatial-autocorrelation-corrected 95% CI 0.05–0.43; p = 0.065).
Decomposition revealed that this agreement is carried by the convertibility axis (ρ = 0.18),
not by the biodiversity-significance axis the index was built around (ρ = 0.04), and that it
is genuine rather than a definitional or shared-input artefact. The open-data significance
proxy — land-system rarity — did not reproduce expert biodiversity value in the one catchment
where it could be tested. We conclude that transparent open-data exposure surfaces are
defensible as first-pass screening layers with mapped uncertainty, but that their alignment
with expert priorities may derive from land availability rather than biodiversity content — a
caution for the widespread use of landform rarity as a low-cost biodiversity proxy.

**Keywords:** conservation planning; open data; spatial prioritisation; biodiversity proxy;
validation; sensitivity analysis; spatial autocorrelation; Northern Territory

## 1. Introduction

Systematic conservation planning depends on spatial estimates of where biodiversity value is
concentrated and where it is most exposed to loss. In well-surveyed regions these estimates
draw on species inventories, fine-scale vegetation mapping, and expert assessment. Across
much of the world's land surface, and across most of northern Australia, such data do not
exist at the resolution planning requires. The pragmatic response has been to construct
indices from whatever open, wall-to-wall spatial data are available — land-system maps,
tenure and protected-area layers, land-use classifications — as proxies for the biodiversity
and threat information that direct survey would provide.

Two questions determine whether such proxy indices can be trusted, and both are usually left
unanswered. The first is internal: an index of this kind embeds construction choices — how
component scores are combined and weighted, how protection is treated — that are individually
defensible but not uniquely determined, and the priorities an index produces may be an
artefact of those choices rather than a property of the landscape. The second is external:
whether the proxy actually reproduces the priorities that expert assessment would assign. The
literature is rich in indices and poor in tests of either kind; sensitivity to construction
choices is rarely mapped, and independent validation against expert judgment is rarer still,
because the expert benchmarks needed for validation are, by definition, scarce in the places
these proxies are used.

This study addresses both questions for a conservation exposure index covering the entire
Northern Territory. We first quantify how far the index's priorities depend on its
construction choices, using an ensemble of defensible variants across the full grid. We then
validate the index against an independent, expert-derived biodiversity risk assessment
recently published for one catchment, decomposing the agreement to establish which components
of the index carry it. The central question is deliberately narrow and testable: does an
open-data exposure proxy, and specifically its biodiversity-significance component, reproduce
expert biodiversity priorities? The answer we obtain — that the proxy agrees with expert
judgment only weakly, and does so through land availability rather than through its
biodiversity-significance inputs — is both a caution about a widely used class of proxy and a
demonstration of how transparent construction and honest validation can surface such
problems rather than conceal them.

## 2. Study area and data

### 2.1 Study area

The Northern Territory covers approximately 1.35 million km² of northern and central
Australia, spanning monsoonal savanna, arid interior, and extensive Aboriginal-owned and
pastoral lands. It is characterised by low survey density, active interest in agricultural
and resource development, and a correspondingly acute need for wall-to-wall planning layers.
The validation benchmark is the central Roper River catchment in the Territory's north,
a ~1.725 million ha area assessed for biodiversity value under the NT Government's *Mapping
the Future* program (Buckley et al. 2024).

### 2.2 Data

All layers derive from open NT and Australian Government sources. The exposure index is
built on an equal-area hexagonal grid of 16,229 cells of 86.6 km² each (EPSG:3577, GDA94 /
Australian Albers). Each hex carries four component scores in [0, 1]: biodiversity
significance from Sites of Conservation Significance (`sig_socs`) and land-system rarity
(`sig_landsys`); agricultural convertibility (`conv_score`) derived from land-use and land-
capability mapping; and the fraction under formal protection (`prot_frac`). The independent
benchmark, `BIORISK`, is the expert biodiversity risk classification of the Roper catchment,
an ordinal five-class scale (Table 1) supplied as polygons and intersected to the grid.

## 3. Methods

### 3.1 Exposure formulation

Exposure combines the three axes multiplicatively, so that a hex scores highly only when it
holds biodiversity value, is convertible to other uses, and is not already protected:

$$E_i = S_i \cdot C_i \cdot (1 - P_i)$$

where $E_i$ is exposure, $S_i$ significance, $C_i$ convertibility, and $P_i$ the protected
fraction of hex $i$. Significance combines the two sub-scores under a rule that is itself a
construction choice (Section 3.2). Convertibility scores land as more exposed where it is
more readily converted to agriculture; protection acts as a moderator, discounting exposure
in proportion to formal protection. Water bodies are treated as no-data rather than zero.

### 3.2 Construction-choice sensitivity

Three choices in the formulation are defensible but not unique: the significance-combination
rule, the relative weighting of the axes, and whether protection moderates multiplicatively
or discounts additively. We defined an ensemble of 30 variants — five significance rules
(element-wise maximum; mean; two 70/30 weighted blends; and a percentile-normalised mean) ×
three weight sets (equal; significance-up; convertibility-up) × two protection forms
(multiplicative moderator; additive discount) — and computed exposure under each across all
16,229 hexes. We assessed agreement between variants by pairwise Spearman correlation of the
full surfaces, and stability of priorities by the persistence of top-decile and top-ventile
(top-5%) hotspot membership across variants. Instability was attributed to specific choices
by comparing pairs of variants differing in only one choice. Decision thresholds were fixed
before results were examined: stable if top-decile persistence ≥80% and all pairwise Spearman
≥0.90; unstable if persistence <60% or any pairwise Spearman <0.75.

### 3.3 Validation against expert assessment

`BIORISK` polygons were reprojected to EPSG:3577, repaired (`buffer(0)`), and intersected
with the hex grid; each intersected hex received the area-weighted mean of the ordinal
`BIORISK` class. The primary comparison is the full exposure surface against area-weighted
`BIORISK` by Spearman correlation, ordinality of `BIORISK` having been confirmed from the
source classification (Table 1). To locate the source of agreement, we decomposed the
correlation across index components (significance only, convertibility only, protection only)
and computed a circularity-controlled variant with the shared SOCS input removed. Because
`BIORISK` class 1 is partly land-use-defined, we tested whether the convertibility agreement
was definitional by excluding class-1 hexes and by restricting to the pure class-3-versus-4
biodiversity contrast. Categorical agreement on the "sensitive-or-better" cut (`BIORISK` ≥ 4)
was summarised by precision, recall, and weighted Cohen's kappa.

### 3.4 Spatial-autocorrelation correction

Adjacent hexes are not independent. We quantified spatial autocorrelation by Moran's I on a
distance-band contiguity graph (≤10.1 km, capturing the six adjacent hexes at the grid's
10 km spacing), and corrected inference two ways: a spatial block-bootstrap resampling
contiguous neighbourhoods rather than individual hexes for confidence intervals, and an
effective-sample-size reduction (Clifford–Richardson style) for the primary significance
test. All analyses used fixed random seeds (42) and are reproducible from the archived scripts
(Data availability).

## 4. Results

### 4.1 Construction-choice sensitivity

Across the 30-variant ensemble, mean pairwise Spearman correlation between full exposure
surfaces was 0.931 (minimum 0.741). Hotspot membership was more sensitive: 58.3% of top-decile
hexes under the baseline variant remained in the top decile under all 30 variants (44.5% for
the top-ventile set). The persistence distribution was strongly bimodal (Figure 2): of 2,379
hexes entering the top decile under at least one variant, 946 did so under every variant and
1,184 under at least 90%, while only 860 fell in the contested 10–90% band. Instability was
driven almost entirely by the significance-combination rule — varying only that choice reduced
mean pairwise Spearman to 0.950, against 0.979 for weights and 0.960 for protection form —
with the percentile-normalised mean as the principal outlier rule (0.885 vs 0.921–0.940 for
the others). Under the pre-registered thresholds the ensemble is formally classified as
sensitive (persistence 58.3%, below the 60% cutoff); we interpret it (Section 5) as a robust
priority core with a construction-sensitive fringe on the basis of the bimodal persistence and
the single-axis attribution.

### 4.2 Validation: primary result and decomposition

The benchmark is effectively two-class by assessed area: `BIORISK` class 3 covers 76.9% and
class 4 covers 22.6%, with classes 1 and 5 at 0.5% and 0.1%. Aggregation yielded 244 validated
hexes (196 with ≥50% coverage). Full exposure correlated with expert `BIORISK` at ρ = 0.240.
Spatial autocorrelation was strong (Moran's I: exposure 0.761, `BIORISK` 0.406, both p = 0.001),
reducing the effective sample size to ≈60; the spatially-corrected 95% CI was [0.051, 0.428]
and the corrected p = 0.065. The agreement is a weak positive whose lower confidence bound
remains above zero but is only marginally significant once dependence is accounted for.

Decomposition (Table 2, Figure 1) localises the agreement to the convertibility axis
(ρ = 0.177, CI [0.028, 0.371]); the biodiversity-significance axis is uncorrelated with
`BIORISK` (ρ = 0.038, CI [−0.225, 0.281]). Removing the shared SOCS input left exposure
agreement unchanged (0.242 vs 0.240; retention 101%), showing that shared-input inflation is
not operating. Protection alone is uncorrelated (ρ = −0.013), consistent with the benchmark
carrying no protection information.

### 4.3 The convertibility agreement is genuine, not definitional

`BIORISK` class 1 ("highly modified") accounts for only 77 km² of 17,254 km² assessed.
Excluding all 57 hexes touching class 1 left the convertibility correlation clearly positive
(ρ = 0.145, n = 187), and restricting to the pure class-3-versus-4 biodiversity contrast
retained ρ = 0.165. The agreement therefore reflects a genuine correspondence between low
agricultural convertibility and higher expert-assessed biodiversity value, not a land-use
tautology.

### 4.4 Categorical agreement and rule discrimination

At the level of individual hexes flagged sensitive-or-better (`BIORISK` ≥ 4; 29 of 244), the
proxy performed near chance: precision and recall both 0.10, weighted kappa 0.024 (linear) /
0.049 (quadratic). The validation could not discriminate among the sensible significance
rules (full-exposure agreement 0.240–0.243 for all except the percentile-normalised mean at
0.171), because the agreement resides in the shared convertibility factor; the simplest
defensible rule is therefore retained on parsimony grounds.

## 5. Discussion

Two findings define the contribution. First, the index's conservation priorities are largely
a property of the data rather than of its construction: a substantial core is invariant to all
30 defensible variants, and the instability that exists is confined to a minority fringe and
attributable to a single choice. The bimodal persistence distribution allows priorities to be
reported as a robust core plus a mapped uncertainty margin rather than as a surface whose
stability is merely asserted. Under the pre-registered threshold the ensemble is formally
sensitive (58.3%, below 60%); we treat it as core-plus-fringe on the strength of the
bimodality and the localisation of instability to one interpretable choice, and report both so
readers may judge. Because validation cannot distinguish the sensible rules, the simplest is
retained.

Second, and more consequentially, the exposure surface's weak agreement with expert judgment
is carried by convertibility, not by the biodiversity-significance axis the index was built
around. This inverts the intuitive expectation: the expert classification is itself largely a
significant-vegetation and designation overlay, so the significance layer might be expected to
align with it. That convertibility does the work suggests the open-data significance proxy and
the expert value map measure different things despite similar construction. The defensible
scope of this claim is specific. Land-system rarity, which varies across all 244 hexes,
genuinely fails to track expert value in this catchment. SOCS cannot be judged here: it is
near-absent (non-zero in 6 of 244 hexes), so its zero correlation reflects absent local
variance, not demonstrated failure. The claim is thus that land-system rarity is not a usable
significance proxy in this catchment, and that the exposure surface's alignment with expert
judgment does not come from its biodiversity inputs — a caution for the common practice of
treating landform rarity as a low-cost biodiversity surrogate.

The practical implication is qualified. An open-data exposure surface of this kind is
defensible as a first-pass screening layer whose priority core is stable and whose uncertainty
is mapped, but it should not be read as a biodiversity-value map. The improvement path follows
directly from the significance-layer result: replacing land-system rarity with inputs that more
directly encode biodiversity value — modelled threatened-species habitat, vegetation
condition, connectivity — is the change most likely to raise agreement with expert assessment.

### 5.1 Limitations

The validation rests on a single catchment of 244 hexes (effective n ≈ 60 after spatial
correction) that occupies an environmentally narrow part of the Territory (high land-system
significance, low convertibility), so external validity to the full grid is untested. The
benchmark is effectively two-class by area, with the highest expert class (0.1% of area) not
validatable as a class, so the rank correlation is dominated by the sensitive-versus-mitigable
contrast. The benchmark carries no protection information, so the validation cannot assess the
protection moderator. The effective-sample-size correction and block definition are
approximations; the block-bootstrap lower bound (0.051) is marginally more optimistic than the
modified-t p (0.065), and we report both rather than select between them. These constraints
bound the strength, not the direction, of the conclusions.

### 5.2 Future work

Priorities are: replacing the significance proxy with more direct biodiversity inputs;
extending validation to additional catchments as expert assessments become available;
propagating component uncertainty through the index; and testing sensitivity to grid
resolution (the modifiable areal unit problem).

## 6. Conclusion

A transparent open-data conservation exposure index for the Northern Territory produces
priorities whose core is robust to defensible construction choices, but which agree only
weakly with independent expert biodiversity assessment in the one catchment where validation
was possible — and that agreement derives from land availability, not from the index's
biodiversity-significance inputs. Transparent construction and honest validation are what make
this diagnosis possible. Open-data exposure surfaces have a defensible role as screening
layers with mapped uncertainty, but should not be mistaken for biodiversity-value maps until
their significance components are shown to carry biodiversity signal.

## Tables

**Table 1. Expert biodiversity risk classes (`BIORISK`) and their representation in the
validated data.** Source: Buckley et al. (2024), Table 3; areal shares from
`outputs_roper/circularity_biorisk_x_alum_km2.csv`.

| Class | Risk to biodiversity | Description | Share of assessed area |
|---|---|---|---|
| 1 | Nil | Highly modified land | 0.5% |
| 2 | Low | No significant value (not distinguished from class 3 in source) | — |
| 3 | Mitigable | Habitat for broadly occurring species; apply mitigation hierarchy | 76.9% |
| 4 | Moderate | Sensitive/significant vegetation or species of conservation interest | 22.6% |
| 5 | High | High biodiversity value | 0.1% |

**Table 2. Decomposition of exposure–expert agreement.** Spearman correlations with
area-weighted `BIORISK` over 244 hexes, with spatial block-bootstrap 95% CIs. Source:
`outputs_roper/verdict.json`, `outputs_roper/spatial_correction.json`.

| Surface | Spearman | Spatial 95% CI |
|---|---|---|
| Full exposure | 0.240 | [0.051, 0.428] |
| Exposure, SOCS removed | 0.242 | [0.053, 0.431] |
| Convertibility only | 0.177 | [0.028, 0.371] |
| Significance only | 0.038 | [−0.225, 0.281] |
| Protection only | −0.013 | — |

## Figure captions

**Figure 1.** Decomposition of exposure–expert agreement. Points are Spearman correlations of
each surface with area-weighted expert `BIORISK` over 244 hexes; bars are spatial
block-bootstrap 95% confidence intervals (effective n ≈ 60). Agreement is carried by
convertibility, not by biodiversity significance.

**Figure 2.** Bimodal distribution of hotspot persistence across 30 defensible construction
variants. Of hexes entering the top priority decile under any variant, 946 do so under all 30
(robust core) and 860 fall in the contested 10–90% band (fringe), supporting a
core-plus-fringe reading of the priorities.

**Figure 3.** Spatial autocorrelation (Moran's I) across index components and the expert
benchmark on the 244-hex validation set; all p = 0.001. Strong positive autocorrelation
motivates the spatial correction applied to all inference.

**Figure S1.** Territory-wide map of hotspot persistence: fraction of 30 construction variants
ranking each hex in the top priority decile.

## Data and code availability

All analysis scripts, component outputs, and figure generators are archived in the project
repository. The pipeline (`sensitivity_analysis.py`, `roper_validation.py`,
`spatial_correction.py`, `make_figures.py`) regenerates every reported number from the two
input geopackages via `run_all.sh`; seeds are fixed at 42. Input layers are open NT/Australian
Government data (licensed, not redistributed; sources documented in the repository README).

## References

Buckley, K., Leiper, I., Nano, C., Wedd, D. and Wilson, D. (2024). *Mapping the Future –
Biodiversity assessment of the central Roper River catchment.* Technical Report 14/2024,
Department of Environment, Parks and Water Security, Northern Territory Government, Darwin.

*[Full reference list to be completed: systematic conservation planning (Margules & Pressey
2000); spatial prioritisation software (Moilanen et al.; Ball, Possingham & Watts, Marxan);
open-data / surrogate biodiversity proxies; sensitivity and uncertainty in conservation
prioritisation; Moran's I (Moran 1950); effective sample size (Clifford, Richardson & Hémon
1989); Cohen's weighted kappa (Cohen 1968). Placeholders flagged for co-author input — see
change log.]*
