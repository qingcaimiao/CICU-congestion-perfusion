## Table S9. Additional robustness analyses

**(A) Patients included in the analysis set versus those excluded.** Included = oedema grade and capillary refill time both charted within the −6 h to +24 h window (n = 12,052); excluded = all other first cardiac ICU stays (n = 8,754). Median values unless stated; p values from Mann–Whitney U or χ² tests.

| Characteristic | Included (n = 12,052) | Excluded (n = 8,754) | p |
|---|---|---|---|
| In-hospital death, n (%) | 6.3 | 9.3 | 3.2 × 10⁻16 |
| Age, years (median) | 68.0 | 69.0 | 8.9 × 10⁻6 |
| ICU length of stay, days (median) | 2.0 | 1.8 | 2.6 × 10⁻30 |
| Heart rate, maximum (median) | 95.0 | 95.0 | 0.321 |
| Creatinine, maximum (median) | 1.0 | 1.1 | 4.8 × 10⁻16 |
| Urea nitrogen, maximum (median) | 18.0 | 21.0 | 8.1 × 10⁻38 |
| Invasive mechanical ventilation, n (%) | 61.8 | 36.7 | 1.2 × 10⁻279 |
| Vasoactive drug infusion, n (%) | 54.4 | 38.1 | 2.8 × 10⁻119 |
| Congestive heart failure, n (%) | 23.4 | 17.1 | 3.8 × 10⁻28 |
| Chronic kidney disease, n (%) | 22.5 | 24.7 | 3.8 × 10⁻4 |

**(B) E-values for the principal effect estimates.** E-values are approximate, treating the odds ratio as a risk ratio, and quantify how strong an unmeasured confounder would have to be, associated with both the sign and death, to explain the association away.

| Estimate | E-value (point estimate) | E-value (lower 95% CI bound) |
|---|---|---|
| Wet-cold versus dry-warm (OR 4.49, development) | 8.45 | 5.75 |
| Dry-cold versus dry-warm (OR 3.20, development) | 5.85 | 4.5 |
| Wet-warm versus dry-warm (OR 1.63, development) | 2.64 | 1.83 |
| Prolonged capillary refill, like-for-like (OR 3.11, development) | 5.67 | 4.5 |
| Wet-cold versus dry-warm, transferred model (OR 4.56, eICU-CRD) | 8.59 | 5.85 |

**(C) Formal comparison of the two axes (development cohort).** In a single model containing both signs as binary terms, with the same 23 routine covariates.

| Quantity | Value |
|---|---|
| Wald test, H₀: β(capillary refill) = β(oedema ≥6 mm) | χ² = 17.5, p < 0.0001 |
| Ratio of odds ratios (perfusion / congestion) | 1.98 (95% CI 1.44–2.73) |
| ΔAUROC, perfusion alone | +0.0101 |
| ΔAUROC, congestion alone | +0.0038 |
| Difference between the two incremental AUROCs (paired bootstrap, 2,000 replicates) | +0.0064 (95% CI +0.0016 to +0.0112) |

**(D) Completeness of congestion documentation in eICU-CRD, and the resulting sensitivity analysis.** An undocumented field cannot be distinguished from a field that was examined and found negative; the pre-specified composite definition therefore treats it as negative.

| Quantity | Value |
|---|---|
| Cardiac ICU stays | 27,757 |
| → none of the three congestion fields recorded | 25,064 (90.3%) |
| → one field recorded | 565 (2.0%) |
| → two fields recorded | 805 (2.9%) |
| → all three fields recorded | 1,323 (4.8%) |
| Analysable set (perfusion + ≥1 congestion field), n / deaths | 1541 / 152 |
| 　mortality, congestion present vs absent | 8.12% vs 4.42% |
| 　congestion, ΔAUROC (95% CI) | +0.0010 (-0.0014 to +0.0033) |
| 　congestion, adjusted OR (95% CI) | 1.21 (0.80–1.85), p = 0.366 |
| Restricted set (all three fields recorded), n / deaths | 954 / 99 |
| 　mortality, congestion present vs absent | 9.13% vs 3.68% |
| 　congestion, ΔAUROC (95% CI) | +0.0032 (-0.0021 to +0.0085) |
| 　congestion, adjusted OR (95% CI) | 1.48 (0.85–2.59), p = 0.168 |

**(E) Leave-one-hospital-out external performance (eICU-CRD).** The transferred 18-covariate model, applied unchanged; hospitals are identified by their eICU-CRD hospital identifier.

| Hospital | Deaths |
|---|---|
| 141 | 7 |
| 188 | 28 |
| 382 | 2 |
| 394 | 10 |
| 420 | 105 |
| 458 | 0 |
| All six (n = 1,541) | 152 |
| External AUROC, full set | 0.835 |
| External AUROC, leave-one-hospital-out range | 0.786–0.846 (median 0.835) |

**(F) Oedema cut-point sensitivity and temporal stability.**

| 切点 | ΔAUROC | 湿暖型 OR | 湿暖型 n |
|---|---|---|---|
| 水肿 ≥2 级 | 0.0122 | 1.42 | 3939 |
| 水肿 ≥3 级 | 0.0126 | 1.63 | 1245 |
| 水肿 ≥4 级 | 0.0136 | 2.25 | 322 |

| 时段 | n | ≥6mm 死亡% | ≥6mm n | <6mm 死亡% | 差(pp) |
|---|---|---|---|---|---|
| 2008 - 2010 | 1942 | 6.43 | 311 | 3.68 | 2.75 |
| 2011 - 2013 | 1902 | 6.21 | 290 | 3.41 | 2.79 |
| 2014 - 2016 | 2308 | 6.32 | 253 | 2.68 | 3.65 |
| 2017 - 2019 | 1989 | 9.52 | 189 | 3.39 | 6.13 |
| 2020 - 2022 | 1574 | 19.26 | 135 | 5.91 | 13.35 |

**(G) Missing-data handling.** Main analysis, median imputation for missing covariates (development) or ≥60% covariate availability with median imputation (replication); sensitivity, complete cases only.

| Analysis set | n | Deaths | AUROC, routine | AUROC, +phenotype | ΔAUROC (95% CI) |
|---|---|---|---|---|---|
| Development — median imputation (primary) | 12052 | 758 | 0.8584 | 0.871 | +0.0126 (+0.0074 to +0.0182) |
| Development — complete cases | 11266 | 636 | 0.8638 | 0.8763 | +0.0125 (+0.0071 to +0.0187) |
| Replication — ≥60% availability + imputation (primary) | 1541 | 152 | — | 0.848 | — |
| Replication — complete cases | 1432 | 136 | — | 0.85 | — |

For the replication cohort the AUROC shown is from a model refitted within eICU-CRD using the development-cohort standardisation constants; it is given only to compare the two missing-data strategies and is not the performance of the transferred model (Table 3).
