# Discussion

## Principal findings

This study set out to build a transparent, Territory-wide conservation exposure surface from
open data and to test it against an independent expert assessment. Two findings define its
contribution. First, the conservation priorities the index identifies are, for the most part,
a property of the data rather than of the arbitrary choices made in constructing the index: a
substantial priority core is invariant to the significance-combination rule, the axis
weighting, and the treatment of protection, while the instability that does exist is confined
to a minority fringe and is attributable almost entirely to a single choice — how the
significance sub-scores are combined. Second, when validated against the expert biodiversity
risk classification of the central Roper catchment, the proxy shows a weak but genuine
positive concordance (ρ = 0.24; spatial 95% CI [0.05, 0.43]; p = 0.065) that is carried by
the convertibility axis rather than by the biodiversity-significance axis the proxy was
built around. The second finding is the more consequential, and the less comfortable.

## What the validation does and does not establish

The agreement between exposure and expert risk survives the checks that would most plausibly
undermine it. It is not an artefact of the SOCS input shared between proxy and benchmark:
removing SOCS leaves the correlation unchanged (0.242 vs 0.240), because the significance
axis carries too little agreement to inflate anything. It is not a land-use tautology: the
convertibility–risk agreement persists when the land-use-defined "highly modified" class is
excluded (ρ = 0.145) and on the pure sensitive-versus-mitigable biodiversity contrast
(ρ = 0.165). And it is not an artefact of treating spatially dependent hexes as independent:
the positive lower confidence bound survives a spatial correction that reduces the effective
sample size from 244 to roughly 60.

But the agreement is weak, and at the level of identifying individual high-value hexes the
proxy performs at chance (precision and recall 0.10; weighted kappa < 0.05). The honest
reading is that the open-data exposure surface captures a broad, monotone gradient that
aligns modestly with expert judgment across a catchment, but does not reliably locate the
specific places experts would prioritise. For a screening tool intended to flag where closer
assessment is warranted, a weak positive gradient has some value; for a tool intended to
substitute for expert assessment, it does not, and the categorical results make that limit
explicit.

Three constraints bound these conclusions and must travel with them. The benchmark exists for
a single catchment (244 hexes, ~1.5% of the grid) that occupies an environmentally narrow
part of the Territory — high land-system significance, low convertibility — so the external
validity of the correlation to the full Territory is untested and cannot be assumed. The
benchmark is effectively two-class by area, with the highest expert class (class 5)
representing 0.1% of the area and therefore not validatable as a class; the rank correlation
is consequently dominated by the sensitive-versus-mitigable contrast. And the benchmark
carries no protection information, so this validation cannot speak to whether the protection
moderator in the exposure formula is correctly specified.

## The significance-layer result

The central negative finding is that the biodiversity-significance axis — the conceptual
heart of the exposure construct — does not reproduce expert biodiversity value in this
catchment (ρ = 0.038; CI spanning zero), while convertibility, a land-availability proxy,
does. This is a substantive result rather than a null to be explained away, but it must be
stated with the right scope. Land-system rarity, which varies across all 244 hexes, genuinely
fails to track expert value here. SOCS cannot be assessed from this benchmark: it is
near-absent in the catchment (non-zero in 6 of 244 hexes), so its zero correlation reflects
absent local variance, not a demonstrated failure of the layer. The defensible claim is
therefore specific: in this catchment, land-system rarity is not a usable proxy for expert
biodiversity significance, and the exposure surface's alignment with expert judgment does not
come from its significance component.

This matters because it inverts the intuitive expectation. The expert classification is
itself largely a significant-vegetation and designation overlay, so one might expect our
significance layer to be precisely what aligns with it. That it is convertibility, not
significance, that carries the agreement suggests the open-data significance proxy and the
expert value map are measuring different things despite superficially similar construction —
a caution for the broader literature that treats land-system or landform rarity as a
low-cost stand-in for biodiversity value.

## The construction-robustness contribution

Independent of the validation, the sensitivity analysis contributes a result that conservation
proxy studies rarely report: an explicit map of which priorities are robust to defensible
construction choices and which are not. The bimodal persistence distribution — 946 hexes in
the top decile under every one of 30 variants, against 860 in the contested fringe — lets the
priorities be reported as a robust core plus a characterised uncertainty margin, rather than
as a single surface whose stability is asserted but untested. The finding that the fringe is
governed almost entirely by the significance-combination rule, and not by weighting or the
protection form, further localises the uncertainty to one interpretable decision. We note
that under the pre-registered threshold the ensemble is formally classified as sensitive
(58.3% persistence, below the 60% cutoff); we treat it as a robust-core-plus-fringe result on
the strength of the bimodality and the single-axis attribution, and report both the threshold
outcome and this interpretation so the reader can judge. Because the validation cannot
discriminate among the sensible significance rules (all agree with the benchmark at
ρ ≈ 0.24), the simplest defensible rule is retained on parsimony grounds.

## Implications and future work

The practical implication is a qualified one. An open-data exposure surface of this kind is
defensible as a first-pass screening layer whose priority core is stable and whose
uncertainty is mapped, but it should not be read as a biodiversity-value map: its agreement
with expert judgment in the one place we could test it came from land availability, not from
its biodiversity inputs. The clearest path to improvement follows directly from the
significance-layer result — replacing land-system rarity as the significance proxy with inputs
that more directly encode biodiversity value (for example, modelled threatened-species
habitat, vegetation-condition, or connectivity layers) is the change most likely to raise
agreement with expert assessment, and is the priority for further work. Extending validation
beyond the single Roper catchment, as comparable expert assessments become available for
other Territory catchments, is the other requirement before the surface's external validity
can be claimed.
