# Variable definitions

## Exposure

### Congestion (MIMIC-IV)

Nursing assessment item **Edema Amount** (itemid `224862`). The charted value domain contains **exactly six** options, verified directly against the database (96,368 records in the cohort; 0 records outside the mapping):

| Charted value | Ordinal grade | Records | % of records | Stays |
|---|---|---|---|---|
| `None` | 0 | 12,729 | 13.21 | 6,225 |
| `2 mm` | 1 | 45,402 | 47.11 | 12,205 |
| `4 mm` | 2 | 24,678 | 25.61 | 7,138 |
| `6 mm` | 3 | 8,077 | 8.38 | 2,994 |
| `8 mm` | 4 | 1,807 | 1.88 | 822 |
| `Anasarca` | 5 | 3,675 | 3.81 | 828 |

No free-text parsing and no unit assumptions are involved. The **worst** grade within the exposure window is used.

*Edema Location* (itemid `224031`) was extracted for completeness (documented in 98.4% of stays, most often `General`) but was **not** used in any model, because the `Anasarca` category already encodes generalisation.

### Perfusion (both databases)

MIMIC-IV: nursing items *Capillary Refill R* (`223951`) and *Capillary Refill L* (`224308`), each recorded as `<3 s` (normal) or `>3 s` (prolonged). A stay is classified as impaired if either side is prolonged within the window. Both sides were recorded in 16,032 stays and disagreed in 249 (1.55%; raw agreement 98.45%, Cohen kappa 0.90), computed in this dataset.

### Phenotypes

Congestion cut-point: grade >= 3 (pitting depth >= 6 mm or anasarca). Fixed in the development cohort and held constant in replication without re-optimisation.

| Phenotype | Oedema grade | Capillary refill |
|---|---|---|
| Dry-warm | <= 2 | normal |
| Wet-warm | >= 3 | normal |
| Dry-cold | <= 2 | prolonged |
| Wet-cold | >= 3 | prolonged |

### Exposure window

From **6 h before** to **24 h after** ICU admission.

## Outcome

In-hospital death over the **entire hospitalisation** (not restricted to the ICU stay).

* MIMIC-IV: `admissions.hospital_expire_flag`
* eICU-CRD: unit discharge status

Because death is ascertained after ICU discharge, ICU discharge is not a competing event.

## Replication exposure definitions (eICU-CRD)

eICU-CRD has no equivalent of `Edema Amount`. Bedside signs are stored in the `physicalExam` table as free-text path/value pairs. All `physicalExampath` values carry the prefix `notes/progress notes/physical exam/physical exam/`; only the distinguishing suffix is given below.

| Definition | Path suffix | Positive rule |
|---|---|---|
| Peripheral oedema only | `extremities/edema` | bilateral oedema, severity 1+ to 4+, or anasarca; "no edema" = negative |
| Jugular venous distension only | `neck/jvd` | any value other than "absent" / "no jvd" |
| Pulmonary crackles only | `pulmonary/auscultation` | value contains "crackle" or "rales" |
| Composite | any of the three | any of the above positive |
| Impaired perfusion (identical in all definitions) | `extremities/perfusion` | any value other than "adequate" |

Replication analyses are restricted to stays in which congestion **and** perfusion were both *documented* (these fields are recorded in only 5-9% of stays), so the exposure is never imputed.

## Transferable covariates

Retained only if available in >= 60% of the replication set. Temperature failed this criterion (31.1% available in eICU-CRD vs 91.1% in development) and was excluded from the primary transferred model; the version including it is reported as a sensitivity analysis (external AUROC 0.850 vs 0.856).

## Unit harmonisation

Three extraction issues were resolved on audit and are handled explicitly in the code:

1. **Temperature.** In MIMIC-IV, Fahrenheit values are charted under a separate itemid (`223761`) and are converted before averaging. In eICU-CRD, `vitalPeriodic.temperature` contains a small minority of Fahrenheit records (0.5%) together with implausible values; these are converted or discarded before averaging.
2. **Haemoglobin (eICU-CRD).** Stored under `labname = 'Hgb'`, not `'hemoglobin'`.
3. **Blood pressure (eICU-CRD).** `vitalPeriodic.systemicsystolic` and `systemicmean` are arterial-line values present in only about a quarter of stays. Systolic and mean arterial pressure are taken as the minimum across non-invasive (`nurseCharting`: `Non-Invasive BP Systolic` / `Non-Invasive BP Mean`) and invasive (`Invasive BP Systolic` / `Invasive BP Mean`) sources.
