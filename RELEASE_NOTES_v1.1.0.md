# v1.1.0 — code and results corrected against the manuscript

This release makes the deposited analysis reproduce every number in the manuscript, and fixes three
substantive errors found while re-auditing it. No conclusion changes.

## Era mapping now joins on `subject_id`

Every script that stratified by era mapped `stay_id → anchor_year_group` through `T2_data/mimic_T2.parquet`,
an intermediate file belonging to a **different cohort** (15,699 stays, of which only 9,715 fall inside this
study's 12,052). That file was never part of this repository, so the deposited code could not be rerun by
anyone else; run locally it returned an AUROC of 0.851 rather than the published 0.867.

`hosp/patients.csv` carries `anchor_year_group` for all 364,627 patients in MIMIC-IV v3.1 with no missing
values. The new `code/_ayg.py` joins it on `subject_id`, asserts uniqueness and completeness, and is imported
by `analyze_cp2.py`, `robustness_round3.py`, `round6_checks.py` and `sensitivity_raw_vs_screened.py`.

Reproduces: 12,052 stays all dated; training 4,778 (277 deaths), test 7,274 (481 deaths); **AUROC 0.867**.

## eICU like-for-like models now adjust for age

`strength_analyses.py` used 17 laboratory and vital-sign variables plus sex but **not age**, whereas the
MIMIC-IV column of the same table starts from a set whose first term is age. The manuscript called both
columns "17 routinely measured covariates". Both now use the same 18 variables.

| Sign | n | Congestion OR | Capillary refill OR |
|---|---|---|---|
| Oedema (any) | 1,519 → 1,524 | 0.82 (0.52–1.30) → **0.77 (0.49–1.23)** | 3.54 (2.26–5.54) → **3.24 (2.06–5.08)** |
| Jugular venous distension | 959 → 962 | 1.35 (0.73–2.49) → **1.25 (0.68–2.33)** | 3.24 (1.87–5.60) → **2.93 (1.68–5.09)** |
| Pulmonary crackles | 1,443 → 1,449 | 0.93 (0.61–1.40) → **0.89 (0.59–1.36)** | 3.69 (2.37–5.76) → **3.35 (2.14–5.24)** |

All three congestion intervals still include 1; capillary refill remains the only sign that carries
information once perfusion is accounted for.

## New analyses

- **APACHE IV benchmark.** Paired bootstrap (1,000 replicates sharing one resampling index) for all three
  pairwise differences: phenotype − APACHE IV **−0.0086 (−0.0769 to +0.0544)**, combined − APACHE IV
  **+0.0392 (−0.0130 to +0.0887)**, combined − phenotype **+0.0478 (+0.0272 to +0.0684)**.
- **Optimism correction** for the incremental AUROC (500 replicates): **+0.0127** with the oedema cutpoint
  fixed and **+0.0123** with the cutpoint re-selected inside each replicate, against an apparent +0.0126.

## Figures

- Figure 1 printed 6.24% where the manuscript reports 6.25%, and the graphical abstract still carried the
  retired temporal AUROC of 0.851. Both corrected.
- Figure 1's exclusion boxes sat underneath the right-hand column and their text was clipped; the layout was
  rebuilt.

## Files

New: `code/_ayg.py`, `results/m1_time_validation.json`, `results/m2_apache_paired_ci.json`,
`results/m2b_eicu_age_adjusted.json`, `results/m2c_panelC_age.json`, `results/m5_optimism.json`,
`results/strength_results.json`.

Changed: `code/analyze_cp2.py`, `code/robustness_round3.py`, `code/round6_checks.py`,
`code/sensitivity_raw_vs_screened.py`, `code/strength_analyses.py`, `code/jcm_figures.py`,
`results/round6_checks.json`, `README.md`, `CITATION.cff`, `.zenodo.json`.

## Citation

Concept DOI (always resolves to the latest release): `10.5281/zenodo.23310936`
Version DOI for this release: minted by Zenodo on publication.
