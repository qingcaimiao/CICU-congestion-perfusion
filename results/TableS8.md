## Table S8. Contribution of each axis of the phenotype to discrimination

Each row is a separate model fitted on top of the routine covariate set; ΔAUROC is relative to that set, except where stated. Confidence intervals are percentile bootstrap intervals from 2,000 resamples. The four-phenotype row reproduces the estimate given in Table 3.

**Panel A. Development cohort (MIMIC-IV; n = 12,052; 758 deaths).** The routine covariate set comprises the 23 variables listed in Section 2.5.

| Model | Predictors | AUROC | ΔAUROC (95% CI) | Adjusted OR for the added term(s) (95% CI) |
|---|---|---|---|---|
| Routine variables only | 23 | 0.858 | — | — |
| + impaired perfusion (capillary refill >3 s) | 24 | 0.869 | +0.0101 (+0.0054 to +0.0149) | 3.24 (2.64–3.98) |
| + congestion, dichotomised (oedema ≥6 mm) | 24 | 0.862 | +0.0038 (+0.0010 to +0.0069) | 1.77 (1.43–2.20) |
| + congestion, ordinal (oedema grade, per level) | 24 | 0.864 | +0.0054 (+0.0019 to +0.0093) | 1.26 (1.17–1.36) |
| + both axes (four phenotypes) | 26 | 0.871 | +0.0126 (+0.0074 to +0.0186) | see Table 2 |
| + congestion added on top of perfusion | 25 | 0.871 | +0.0025† (+0.0006 to +0.0045) | 1.56 (1.25–1.94) |

† Increment relative to the model containing impaired perfusion alone.

**Panel B. Replication cohort (eICU-CRD; n = 1,541; 152 in-hospital deaths).** Because the development-cohort congestion measurement is absent from this database and the alternative signs are different instruments, these models were fitted *within* eICU-CRD rather than by transferring coefficients, and are therefore exploratory. The routine covariate set comprises the 18 transferable variables plus sex, i.e. 19 predictors.

| Model | Predictors | AUROC | ΔAUROC (95% CI) | Adjusted OR for the added term(s) (95% CI) |
|---|---|---|---|---|
| Routine variables only | 19 | 0.834 | — | — |
| + impaired perfusion (documented inadequate perfusion) | 20 | 0.847 | +0.0128 (+0.0015 to +0.0259) | 3.18 (2.04-4.96) |
| + congestion (composite: oedema, jugular venous distension or crackles) | 20 | 0.835 | +0.0012 (-0.0011 to +0.0036) | 1.21 (0.80-1.85) |
| + both axes (four phenotypes) | 22 | 0.848 | +0.0142 (+0.0029 to +0.0266) | wet-warm 1.27 (0.76-2.11); dry-cold 4.55 (2.11-9.81); wet-cold 3.41 (1.88-6.19) |
| + both axes, as single terms | 21 | 0.847 | +0.0136 (+0.0021 to +0.0268) | perfusion 3.15 (2.02-4.93); congestion 1.09 (0.71-1.68) |

Once perfusion was accounted for, congestion retained a small but statistically significant increment in the development cohort (+0.0025 ΔAUROC; adjusted odds ratio 1.56, 95% CI 1.25 to 1.94) but contributed no increment in the replication cohort (odds ratio 1.09, 95% CI 0.71-1.68; AUROC 0.834 → 0.847 on adding the congestion term to a model already containing perfusion), a null increment whose confidence interval crosses zero.
