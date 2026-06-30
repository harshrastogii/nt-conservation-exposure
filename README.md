# NT Conservation Exposure Index

A transparent, Territory-wide proxy index of conservation exposure for the Northern
Territory, built entirely from open government spatial data, with a validation
framework demonstrated in the central Roper River catchment.

**Status:** MVP checkpoint — all core layers built, integrated, QA'd, visualised.
Exposure is currently *provisional* (placeholder significance-combination); the
validation and final-index methodology are the next research phase.

## Concept

Conservation exposure is modelled as the intersection of three axes on an
equal-area hex grid (86.6 km², EPSG:3577, clipped to NT land; 16,229 hexes):

    Exposure  =  Significance  ×  Convertibility  ×  (1 − Protection)

- **Significance** — conservation value, from formal designations (SOCS) plus a
  land-system rarity proxy. Sub-scores kept separate and auditable.
- **Convertibility** — availability for agricultural conversion (area-weighted
  ALUM-class score from the NT Land Use Mapping Project). Continuous; near-binary
  in practice due to class 1/2 dominance.
- **Protection** — fraction of each hex within the gazetted conservation estate
  (NT Parks & Reserves). Acts as a moderator, not an additive component.

The current implementation operationalises one conversion-threat pathway
(agricultural). Other pathways (fire, mining, infrastructure) are future extensions.

## Canonical pipeline (run in order)

| Stage | Script | Reads | Writes |
|------|--------|-------|--------|
| 1 | `build_hexgrid.py` | NT coastline | `nt_hexgrid_10km.gpkg`, `nt_boundary.gpkg` |
| 2 | `attribute_convertibility.py` | hex grid, LUMP | `hex_convertibility.gpkg` |
| 3 | `stage2_significance.py` | hex grid, SOCS, NT Land Systems | `hex_significance.gpkg` |
| 4 | `attribute_protection.py` | hex grid, NT Parks | `hex_protection.gpkg` |
| 5 | `integrate_index.py` | all of the above | `hex_master.gpkg`, `hex_master_qa.csv` |
| 6 | `scripts_visualise.py` | `hex_master.gpkg` | `figures/*.png` |

**Note on script duplicates:** earlier prototype scripts exist in this folder
(`stage2_convertibility.py`, `attribute_socs.py`, `attribute_landsys.py`,
`stage2_protection.py` [an unfinished CAPAD/IPA attempt — basis for future IPA work],
`stage3_exposure.py`, `stage3b_spatialstats.py`, and various `inspect_*`/`diag_*`
one-offs). These are superseded; the table above lists the authoritative script for
each stage. The legacy `hex_exposure.gpkg` and `hex_significance_socs/_landsys.gpkg`
outputs are likewise superseded by `hex_master.gpkg` and `hex_significance.gpkg`.

## External datasets (not redistributed — obtain from source)

All are openly licensed NT/Australian government layers. Paths below are the local
locations used during development; substitute your own after downloading.

- **NT Coastline / Land Mass** — NT Government (data.nt.gov.au).
  `NT_Coastline.gdb`, layer `NorthernTerritory`.
- **NT Land Use Mapping Project (LUMP) 2016–2024** — NT Government / ABARES ALUM.
  `LUMP_2016_2024.gdb`. Convertibility derives from the ALUM `PRIM_NO` classes.
- **Sites of Conservation Significance (SOCS)** — NT Government. Graded by
  `SIG_RATING` (International 1.0 / National 0.7).
- **NT Land Systems (1M)** — NT Government. Rarity = log-inverse mapped area of
  `LANDSYSTEM`.
- **NT Parks & Reserves** — NT Government. `NT_Parks_g94.shp`. Protected fraction
  per hex; `IUCN` retained as QA.
- **Validation — Risk to Biodiversity, central Roper River catchment (2024)** —
  NT Government "Mapping the Future" assessment. `MTF_Roper.gdb`, layer
  `Roper_biodiversity_risks` (`BIORISK` ordinal). Used for the validation phase.

## Reproduce

```bash
conda env create -f environment.yml   # creates env "geo"
conda activate geo
# place datasets per paths in each script's header, then:
python build_hexgrid.py
python attribute_convertibility.py
python stage2_significance.py
python attribute_protection.py
python integrate_index.py
python scripts_visualise.py
```

`data/` is gitignored (licensed source layers + large outputs). Figures and the QA
CSV are tracked as small derived artefacts.

## Locked methodology decisions

CRS EPSG:3577 for all area math; hex 86.6 km² clipped to NT land (16,229 hexes);
area-weighted overlay for attribution except SOCS (max-rule designation logic);
significance sub-scores kept separate; protection as moderator; equal weights as a
stated, sensitivity-tested prior. See `docs/METHODS.md` (to be written in the
research phase) for full justification.
