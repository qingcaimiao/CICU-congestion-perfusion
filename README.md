# Bedside congestion–perfusion phenotypes in the cardiac intensive care unit
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23310936.svg)](https://doi.org/10.5281/zenodo.23310936)

Analysis code and aggregate results for the study:

> **Nurse-Charted Congestion–Perfusion Phenotypes in the Cardiac Intensive Care Unit: Perfusion Replicates, Congestion Is Documentation-Dependent**
> Qingcai Miao, Jianhong Cen, Lu Chen, Runzhi Lu, Renjie Zhang
> Hebei North University; Handan First Hospital; Handan Key Laboratory of Cardiac Precision Medicine

---

## What this study asked

Cardiac intensive care unit (CICU) risk models are built on laboratory values, vital signs and severity scores. Two physical signs that critical care nurses already chart every shift — the **depth of pitting oedema** and the **capillary refill time** — had not been evaluated as a combined congestion–perfusion phenotype in the CICU, nor tested for transportability to a second hospital system.

Three questions were prespecified:

1. Do routinely documented oedema grade and capillary refill time define distinct congestion–perfusion phenotypes associated with in-hospital mortality?
2. Do they add discriminatory, calibration and decision-analytic value beyond routinely available clinical variables?
3. Is the phenotype reproducible in an external, multi-hospital database — and if only partly, what does that reveal about the transportability of bedside documentation?

## Headline results

| | MIMIC-IV v3.1 (development) | eICU-CRD v2.0 (replication) |
|---|---|---|
| Cohort | 20,806 first cardiac ICU stays | 27,757 cardiac ICU stays (208 hospitals; 36 contributed cardiac-ICU admissions, 6 contributed analysable cases) |
| Analysis set | 12,052 (both signs charted) | 1,555 (both signs documented) |
| In-hospital deaths | 758 (6.29%) | 156 (10.0%) |
| Phenotype mortality | dry-warm 4.10% → wet-cold 29.92% | dry-warm 4.53% → wet-cold 34.87% |
| Discrimination | AUROC 0.858 → **0.871** with phenotype | external AUROC **0.835** |
| Calibration on transfer | — | O:E 0.92, slope 0.79, intercept −0.44 |
| Axis contribution (ΔAUROC) | perfusion +0.0101; congestion +0.0038; both +0.0126 | perfusion +0.0128; congestion +0.0012 (95% CI −0.0011 to +0.0036, null); both +0.0142 |

* The transferred model is the **full congestion-perfusion model** (18 continuous variables, sex and three phenotype
  indicators; 22 parameters excluding the intercept), so its external AUROC is directly comparable with the
  development value; external EPV is 6.9. Per-centre AUROC and the complete eICU value domains are in
  `results/TableS9E_per_hospital.csv`.
* eICU-CRD `physicalExam` uses a **closed value domain** for these fields (jugular venous distension: 2 values; peripheral perfusion: 4; peripheral oedema: 12; pulmonary auscultation: 22), and contains no *not assessed / NA / unable to assess* value anywhere — so an unrecorded field is never coded as positive.
* Outcome is **in-hospital death** (MIMIC-IV `hospital_expire_flag`; eICU-CRD `hospitaldischargestatus`), not ICU-level death: 2,666 in-hospital deaths vs 1,727 unit-level deaths in the cardiac-ICU cohort.
* The **perfusion** axis transported almost exactly (6.24% vs 33.96%) and carried about four-fifths of the incremental discrimination in development; within eICU-CRD, congestion added no discrimination at all once perfusion was accounted for (`results/axis_contribution_eicu.csv`).
* The **specific** nurse-charted pitting-depth measurement does not exist in eICU-CRD, and none of the three alternative congestion signs available there reproduced the mortality gradient. On a like-for-like dichotomised comparison, prolonged capillary refill (adjusted OR 3.11) contributed about twice as much as oedema ≥6 mm (1.58).

## Repository contents

```
code/       analysis scripts (Python 3.13)
results/    aggregate outputs: every table value, confidence interval and model metric
docs/       data access notes and variable definitions
```

Every continuous covariate is summarised after a pre-specified physiological plausibility screen
(values outside an adult ICU range are treated as charting errors and set to missing before the
per-stay minimum, maximum or mean is taken), and the version of every principal analysis that uses
the values exactly as charted is reported alongside it (`results/sensitivity_raw_vs_screened.csv`,
`results/TableS7*`). Ranges, excluded record counts and the sensitivity comparison are in Table S7.

### `code/` — suggested execution order

| File | Role |
|---|---|
| `build_cp.py` | Build the MIMIC-IV development cohort (first cardiac ICU stay) and extract the bedside examination items (oedema `224862`, oedema location `224031`, capillary refill `223951`/`224308`) |
| `build_cp_eicu.py` | Build the eICU-CRD replication cohort and extract bedside signs from `physicalExam` (blood pressure from `nurseCharting`, haemoglobin from `labname = 'Hgb'`) |
| `patch_temp.py` | Temperature unit harmonisation (Fahrenheit → Celsius; implausible-value handling) |
| `_ayg.py` | **Era mapping for temporal validation.** Joins `anchor_year_group` from `hosp/patients.csv` on `subject_id`, with assertions on uniqueness and completeness; imported by every script that stratifies by era |
| `analyze_cp2.py` | **Primary analysis**: phenotypes, adjustment, discrimination, calibration, IDI/NRI, decision-curve analysis, temporal validation |
| `analyze_cp_eicu.py` | Replication using each individual congestion sign (single-sign sensitivity) |
| `analyze_cp_eicu2.py` | Replication using the composite congestion definition |
| `final_eicu_model.py` | Transferred model, external AUROC, observed-to-expected ratio, calibration intercept and slope |
| `analyze_cp_traj2.py` | Congestion trajectory (0–24 h vs 24–72 h) and its incremental value |
| `tables_cp.py`, `table1_cp.py` | Table 1 (baseline by phenotype) and Tables 2–4 |
| `figures_cp.py`, `fig3_redo.py` | Manuscript Figures 2–9 (400 dpi PNG) |
| `jcm_figures.py`, `jcm_fig_renumber.py` | Figure 1 (participant flow) and the graphical abstract; final figure numbering (nine main figures; the variable-importance panel is Supplementary Figure S1) and 600 dpi TIFF export |
| `critique_checks.py`, `fix_critique2c.py` | Pre-specified secondary analyses: oedema grade as indicator variables, like-for-like dichotomised comparison, external missingness, temperature-excluded sensitivity |
| `critique_eicu.py`, `calib_fix.py`, `mk_supp2.py` | Alternative congestion definitions, calibration on the correct analysis set, missingness, supplementary Tables S1–S3 |
| `verify_critique2.py` | Verification of the raw charted value domain of the oedema item (Table S4) |
| `verify_refs_cp.py`, `refs_final_cp.py`, `build_mdpi_refs.py` | Reference metadata verification (Europe PMC, Crossref, DataCite) |

**Paths.** Each script defines the location of the source databases and of the working directory at the top (`M`, `E`, `D`, `OUT`). Adjust these to your local installation before running.

## Data availability

MIMIC-IV v3.1 and the eICU Collaborative Research Database v2.0 were accessed from PhysioNet under credentialed data-use agreements:

* https://physionet.org/content/mimiciv/3.1/
* https://physionet.org/content/eicu-crd/2.0/

Access requires completion of the CITI "Data or Specimens Only Research" training and execution of a data use agreement.

**No row-level data are included in this repository, and none can be redistributed.** The data-use agreements for both databases prohibit sharing patient-level records. Accordingly, this repository contains only the cohort-definition and analysis code plus aggregate outputs. Running the code requires your own credentialed PhysioNet access.

## Reproducing the analysis

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

# adjust the database paths at the top of each script, then run in the order above
```

Exact package versions used for the submitted manuscript are listed in `requirements.txt`.

Four extraction issues were resolved during the analysis and are handled explicitly in the code, because all four would otherwise silently corrupt key covariates in eICU-CRD or silently drop patients from the MIMIC-IV cohort:

1. **Blood pressure.** `vitalPeriodic.systemicsystolic` and `systemicmean` are arterial-line values present in only about a quarter of stays. Systolic and mean arterial pressure are taken as the minimum across non-invasive (`nurseCharting`: `Non-Invasive BP Systolic`/`Mean`) and invasive (`Invasive BP Systolic`/`Mean`) sources.
2. **Haemoglobin.** Stored under `labname = 'Hgb'`, not `'hemoglobin'`.
3. **Temperature.** A small minority of eICU-CRD temperature records are in Fahrenheit or implausible; these are converted or discarded before averaging. In MIMIC-IV, Fahrenheit values are charted under a separate itemid (`223761`) and are converted before averaging.
4. **Era of admission.** `anchor_year_group` exists only in `hosp/patients.csv`, at patient level, and is populated for all 364,627 patients in MIMIC-IV v3.1. It must therefore be joined on `subject_id`. Joining it on `stay_id` through a stay-level intermediate table that covers a *different* cohort silently drops patients and biases the temporal-validation estimate: in this analysis that route retained 9,715 of 12,052 stays and returned AUROC 0.851, whereas the correct patient-level join retains all 12,052 and returns 0.867. `code/_ayg.py` performs the join with uniqueness and completeness assertions and is imported by every script that stratifies by era.

## How to cite

If you use this code or these aggregate results, please cite the archived release rather than the moving repository tip. The concept DOI below always resolves to the latest version; the version-specific DOI of the current release is `10.5281/zenodo.23720034` (v1.1.0); the earlier archive of v1.0.0 is `10.5281/zenodo.23310937`.

```
Miao Q, Cen J, Chen L, Lu R, Zhang R. Analysis code and aggregate results:
Nurse-charted congestion–perfusion phenotypes in the cardiac intensive care unit.
Zenodo. https://doi.org/10.5281/zenodo.23310936
```

Metadata for citation managers is provided in `CITATION.cff`.

## Licence

Code: MIT (see `LICENSE`). Aggregate results: CC BY 4.0.

## Contact

Renjie Zhang (corresponding author) — zhangrenjie725@sina.com
Qingcai Miao — 15511075821@163.com
