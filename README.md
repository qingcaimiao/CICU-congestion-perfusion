# Bedside congestion–perfusion phenotypes in the cardiac intensive care unit

Analysis code and aggregate results for the study:

> **Bedside Congestion–Perfusion Phenotypes from Routinely Documented Nursing Assessments and In-Hospital Mortality in the Cardiac Intensive Care Unit: Development in MIMIC-IV and External Replication in eICU**
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
| Cohort | 20,806 first cardiac ICU stays | 27,757 cardiac ICU stays (208 hospitals) |
| Analysis set | 12,052 (both signs charted) | 1,555 (both signs documented) |
| In-hospital deaths | 758 (6.29%) | 110 (7.1%) |
| Phenotype mortality | dry-warm 4.10% → wet-cold 29.92% | dry-warm 2.92% → wet-cold 28.29% |
| Discrimination | AUROC 0.858 → **0.870** with phenotype | external AUROC **0.856** |
| Calibration on transfer | — | O:E 0.65, slope 0.76, intercept −0.97 |

* The **perfusion** axis transported almost exactly (3.86% vs 27.36%).
* The **specific** nurse-charted pitting-depth measurement does not exist in eICU-CRD, and none of the three alternative congestion signs available there reproduced the mortality gradient. On a like-for-like dichotomised comparison, prolonged capillary refill (adjusted OR 3.05) contributed about twice as much as oedema ≥6 mm (1.58).

## Repository contents

```
code/       analysis scripts (Python 3.13)
results/    aggregate outputs: every table value, confidence interval and model metric
docs/       data access notes and variable definitions
```

### `code/` — suggested execution order

| File | Role |
|---|---|
| `build_cp.py` | Build the MIMIC-IV development cohort (first cardiac ICU stay) and extract the bedside examination items (oedema `224862`, oedema location `224031`, capillary refill `223951`/`224308`) |
| `build_cp_eicu.py` | Build the eICU-CRD replication cohort and extract bedside signs from `physicalExam` |
| `analyze_cp2.py` | Primary analysis: phenotypes, adjustment, discrimination, calibration, IDI/NRI, decision-curve analysis, temporal validation |
| `analyze_cp_eicu.py` | Replication using each individual congestion sign (single-sign sensitivity) |
| `analyze_cp_eicu2.py` | Replication using the composite congestion definition |
| `final_eicu_model.py` | Transferred model, external AUROC, observed-to-expected ratio, calibration intercept and slope |
| `analyze_cp_traj2.py` | Congestion trajectory (0–24 h vs 24–72 h) and its incremental value |
| `tables_cp.py`, `table1_cp.py` | Table 1 (baseline by phenotype) and Tables 2–4 |
| `figures_cp.py`, `fig3_redo.py` | All manuscript figures (400 dpi PNG) |
| `critique_eicu.py`, `calib_fix.py`, `mk_supp2.py` | Pre-specified secondary and sensitivity analyses: alternative congestion definitions, calibration on the correct analysis set, missingness, like-for-like comparison |
| `patch_temp.py` | Temperature unit harmonisation (Fahrenheit → Celsius; implausible-value handling) |
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

Two extraction issues were resolved during the analysis and are handled explicitly in the code, because both would otherwise silently corrupt key covariates in eICU-CRD:

1. **Blood pressure.** `vitalPeriodic.systemicsystolic` and `systemicmean` are arterial-line values present in only about a quarter of stays. Systolic and mean arterial pressure are taken as the minimum across non-invasive (`nurseCharting`: `Non-Invasive BP Systolic`/`Mean`) and invasive (`Invasive BP Systolic`/`Mean`) sources.
2. **Haemoglobin.** Stored under `labname = 'Hgb'`, not `'hemoglobin'`.
3. **Temperature.** A small minority of eICU-CRD temperature records are in Fahrenheit or implausible; these are converted or discarded before averaging. In MIMIC-IV, Fahrenheit values are charted under a separate itemid (`223761`) and are converted before averaging.

## Licence

Code: MIT (see `LICENSE`). Aggregate results: CC BY 4.0.

## Contact

Renjie Zhang (corresponding author) — zhangrenjie725@sina.com
Qingcai Miao — 15511075821@163.com
