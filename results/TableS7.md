### Table S7. Pre-specified physiological plausibility screen and sensitivity analysis

**(A)** Ranges applied to every continuously measured covariate before per-stay aggregation. Values outside a range were treated as charting or measurement errors and set to missing, so that they could not enter the minimum, maximum or mean used for that stay. "Stays affected" counts stays whose summary statistic changed as a result of the screen. Temperature was converted from Fahrenheit before screening. The same conversion window, and therefore the same screen, was already in force in the preceding version of the pipeline in MIMIC-IV, which is why no development-cohort stay changed; in eICU-CRD the Fahrenheit acceptance window was harmonised with the development cohort, changing the mean temperature of 13 stays by more than 0.05 °C. Body weight in eICU-CRD is a single value per stay rather than a charted series, so no record-level counts are available there. Where a laboratory analyte is held under more than one labname, the counts are pooled.

| Variable | Unit | Range | Development: records screened | Development: excluded n | Development: excluded % | Development: stays affected | Replication: records screened | Replication: excluded n | Replication: excluded % | Replication: stays affected |
|---|---|---|---|---|---|---|---|---|---|---|
| Heart rate | /min | 20–300 | 576,792 | 264 | 0.046 | 184 | 6,793,485 | 1,824 | 0.027 | 591 |
| Respiratory rate | /min | 1–80 | 569,213 | 4,243 | 0.745 | 51 | 5,908,131 | 42,809 | 0.725 | 418 |
| Oxygen saturation | % | 1–100 | 558,991 | 40 | 0.007 | 22 | 6,120,083 | 137 | 0.002 | 57 |
| Systolic blood pressure | mmHg | 20–300 | 584,132 | 46 | 0.008 | 30 | 2,121,791 | 1,094 | 0.052 | 345 |
| Mean arterial pressure | mmHg | 20–250 | 584,763 | 1,029 | 0.176 | 426 | 2,031,295 | 6,737 | 0.332 | 968 |
| Temperature | °C | 25–45 | 190,413 | 135 | 0.071 | 0 | 2,033,103 | 2,811 | 0.138 | 13 |
| Body weight | kg | 20–400 | 19,873 | 11 | 0.055 | 11 | — | — | — | — |
| Creatinine (max) | mg/dL | 0.05–50 | 48,191 | 1 | 0.002 | 0 | 50,064 | 0 | 0.0 | 0 |
| Urea nitrogen (max) | mg/dL | 0.5–300 | 48,042 | 0 | 0.0 | 0 | 49,694 | 0 | 0.0 | 0 |
| Sodium (min) | mmol/L | 80–200 | 46,150 | 0 | 0.0 | 0 | 62,304 | 0 | 0.0 | 0 |
| Potassium (max) | mmol/L | 1–15 | 50,604 | 1 | 0.002 | 1 | 69,210 | 0 | 0.0 | 0 |
| Chloride (min) | mmol/L | 50–160 | 51,115 | 0 | 0.0 | 0 | 50,011 | 1 | 0.002 | 0 |
| Bicarbonate (min) | mmol/L | 1–60 | 47,484 | 0 | 0.0 | 0 | 48,268 | 1 | 0.002 | 0 |
| Haemoglobin (min) | g/dL | 1–25 | 55,902 | 0 | 0.0 | 0 | 53,986 | 2 | 0.004 | 1 |
| White cell count (max) | K/µL | 0.1–500 | 54,387 | 0 | 0.0 | 0 | 46,518 | 159 | 0.342 | 73 |
| Platelet count (min) | K/µL | 1–3000 | 56,040 | 0 | 0.0 | 0 | 46,920 | 1 | 0.002 | 1 |
| Glucose (max) | mg/dL | 10–4000 | 38,373 | 0 | 0.0 | 0 | 54,365 | 0 | 0.0 | 0 |
| Lactate (max) | mmol/L | 0.1–40 | 63,520 | 2 | 0.003 | 1 | 16,207 | 1 | 0.006 | 1 |

**(B)** Sensitivity analysis. The primary analysis summarises each covariate after the screen (left column); the right column repeats every principal analysis using the values exactly as charted.

| Metric | Screened (primary) | As charted (sensitivity) | Absolute difference |
|---|---|---|---|
| Development cohort, routine-variable model, AUROC | 0.858 | 0.858 | 0.000 |
| Development cohort, routine + phenotype, AUROC | 0.871 | 0.870 | 0.001 |
| ΔAUROC | +0.0126 | +0.0124 | +0.0002 |
| ΔAUROC, lower 95% CI limit | +0.0074 | +0.0072 | +0.0002 |
| ΔAUROC, upper 95% CI limit | +0.0186 | +0.0177 | +0.0009 |
| IDI | +0.0209 | +0.0203 | +0.0005 |
| Temporal validation AUROC | 0.851 | 0.854 | 0.003 |
| Adjusted OR, wet-warm | 1.633 | 1.628 | 0.005 |
| Adjusted OR, dry-cold | 3.201 | 3.127 | 0.074 |
| Adjusted OR, wet-cold | 4.494 | 4.435 | 0.059 |
| External AUROC (18 covariates) | 0.855 | 0.852 | 0.002 |
| External calibration slope | 0.826 | 0.810 | 0.016 |
| External calibration intercept | -0.870 | -0.903 | +0.033 |
| External observed-to-expected ratio | 0.66 | 0.65 | 0.01 |
| External mean predicted risk (%) | 10.67 | 10.77 | 0.10 |
