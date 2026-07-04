# Change log — manuscript & repository preparation

## Audit batch 1 (manuscript assembly + consistency)
- Assembled full manuscript (`paper/MANUSCRIPT.md`) from frozen outputs: added Title,
  Abstract, Keywords, Introduction, Study area, Methods, Limitations, Future work,
  Conclusion, Tables 1–2, figure captions, Data availability. Results/Discussion folded in
  from prior drafts.
- Verified every reported number against output files in one pass (see README_analysis.md).
  No inconsistencies found; all figures match `verdict.json` / `spatial_correction.json`.
- Framed Introduction around the tested claim (does the significance proxy reproduce expert
  priorities?) so the negative result is the paper's spine, not a footnote.
- Reorganised repo: `paper/` (manuscript+figures), `analysis/` (frozen scripts+outputs),
  `docs/`. Added MIT-style code license note; input data remain licensed/not redistributed.

## Outstanding (require co-author/supervisor input)
- Full reference list: only the benchmark (Buckley et al. 2024) is complete; ~10 standard
  citations flagged as placeholders in References.
- B-vs-C interpretation: manuscript presents both the pre-registered B_UNSTABLE label and the
  core-plus-fringe reading; supervisor to confirm emphasis.
- Target journal not yet selected (affects length, figure format, reference style).
