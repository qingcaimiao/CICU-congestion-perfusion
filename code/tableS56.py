# -*- coding: utf-8 -*-
"""Generate two supplementary tables required by TRIPOD+AI.

Table S5 (item 20c): distribution of the transferable predictors in the development
                     and replication analysis sets.
Table S6 (item 22) : full specification of the transferred model - standardisation
                     constants, coefficients and odds ratios - so that third parties
                     can reproduce predictions.

Cohort definitions and the >=60% covariate-availability filter are identical to
final_eicu_model.py.
"""
import duckdb
import numpy as np
import pandas as pd
import statsmodels.api as sm

c = duckdb.connect(); c.execute('PRAGMA threads=8')
D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
COVS = ['age', 'hr_min', 'hr_max', 'sbp_min', 'map_min', 'rr_max', 'spo2_min', 'adm_weight',
        'cr_max', 'bun_max', 'na_min', 'k_max', 'cl_min', 'hco3_min', 'hgb_min', 'wbc_max',
        'plt_min', 'glu_max']
PHEN = ['WetWarm', 'DryCold', 'WetCold']       # reference: DryWarm
NICE = {'age': 'Age (years)', 'hr_min': 'Heart rate, minimum (bpm)', 'hr_max': 'Heart rate, maximum (bpm)',
        'sbp_min': 'Systolic BP, minimum (mmHg)', 'map_min': 'Mean arterial pressure, minimum (mmHg)',
        'rr_max': 'Respiratory rate, maximum (breaths/min)', 'spo2_min': 'Oxygen saturation, minimum (%)',
        'adm_weight': 'Admission weight (kg)', 'cr_max': 'Creatinine, maximum (mg/dL)',
        'bun_max': 'Urea nitrogen, maximum (mg/dL)', 'na_min': 'Sodium, minimum (mmol/L)',
        'k_max': 'Potassium, maximum (mmol/L)', 'cl_min': 'Chloride, minimum (mmol/L)',
        'hco3_min': 'Bicarbonate, minimum (mmol/L)', 'hgb_min': 'Haemoglobin, minimum (g/dL)',
        'wbc_max': 'White cell count, maximum (K/uL)', 'plt_min': 'Platelets, minimum (K/uL)',
        'glu_max': 'Glucose, maximum (mg/dL)', 'female': 'Female sex',
        'WetWarm': 'Wet-warm phenotype (vs dry-warm)', 'DryCold': 'Dry-cold phenotype (vs dry-warm)',
        'WetCold': 'Wet-cold phenotype (vs dry-warm)', 'In-hospital death': 'In-hospital death'}


def num(s):
    return pd.to_numeric(pd.Series(s).astype(str).str.replace('>', '', regex=False).str.strip(),
                         errors='coerce')


mm = c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()
ee = c.execute(f"SELECT * FROM read_parquet('{D}/eicu_cp.parquet')").df().rename(
    columns={'admissionweight': 'adm_weight'})
tc = pd.read_csv(D + '/eicu_temp_clean.csv')
ee = ee.drop(columns=['temp_mean']).merge(tc, on='patientunitstayid', how='left') \
       .rename(columns={'temp_clean_c': 'temp_mean'})
ee['cong_any'] = ((ee.edema_pos.fillna(0) == 1) | (ee.jvd_pos.fillna(0) == 1) |
                  (ee.crackles.fillna(0) == 1)).astype(int)
sub = ee[(ee[['edema_doc', 'jvd_doc', 'lungs_doc']].fillna(0).sum(axis=1) > 0) &
         (ee.perf_doc.fillna(0) == 1)].copy()
sub['quad'] = np.where((sub.cong_any == 1) & (sub.hypoperf.fillna(0) == 1), 'WetCold',
              np.where((sub.cong_any == 1) & (sub.hypoperf.fillna(0) == 0), 'WetWarm',
              np.where((sub.cong_any == 0) & (sub.hypoperf.fillna(0) == 1), 'DryCold', 'DryWarm')))


def build(d):
    X = pd.DataFrame(index=d.index)
    for v in COVS:
        X[v] = num(d[v])
    X['female'] = pd.Series(d.gender).astype(str).str.upper().str.startswith('F').astype(int).values
    for k in PHEN:
        X[k] = (d['quad'] == k).astype(int)
    return X


Xm, Xe = build(mm), build(sub)
ok = Xe[COVS].notna().mean(axis=1) >= 0.6
Xe = Xe.loc[ok]
mm_died = mm['died'].astype(int).values
ee_died = sub['died'].astype(int).values[ok.values]
Xm['In-hospital death'] = mm_died
Xe['In-hospital death'] = ee_died
print('development n=%d deaths=%d | replication (model set) n=%d deaths=%d'
      % (len(Xm), mm_died.sum(), len(Xe), ee_died.sum()))

# ---------------- Table S5 ----------------
def smd_cont(a, b):
    a, b = a.dropna(), b.dropna()
    s = np.sqrt((a.std() ** 2 + b.std() ** 2) / 2)
    return (a.mean() - b.mean()) / s if s > 0 else np.nan


def smd_bin(p1, p2):
    s = np.sqrt((p1 * (1 - p1) + p2 * (1 - p2)) / 2)
    return (p1 - p2) / s if s > 0 else np.nan


rows, done = [], set()
for v in COVS + ['female'] + PHEN + ['In-hospital death']:
    if v in done:
        continue
    done.add(v)
    a, b = Xm[v], Xe[v]
    if v in ('female', 'In-hospital death') or v in PHEN:
        p1, p2 = a.mean(), b.mean()
        rows.append(dict(Variable=NICE.get(v, v), Type='n (%)',
                         Development='%d (%.1f)' % (int(a.sum()), 100 * p1),
                         Replication='%d (%.1f)' % (int(b.sum()), 100 * p2),
                         SMD=round(float(smd_bin(p1, p2)), 2)))
    else:
        rows.append(dict(Variable=NICE.get(v, v), Type='median (IQR)',
                         Development='%.1f (%.1f–%.1f)' % (a.median(), a.quantile(.25), a.quantile(.75)),
                         Replication='%.1f (%.1f–%.1f)' % (b.median(), b.quantile(.25), b.quantile(.75)),
                         SMD=round(float(smd_cont(a, b)), 2)))
t5 = pd.DataFrame(rows)
t5.to_csv(OUT + '/TableS5_predictor_distributions.csv', index=False)
print('\n--- Table S5 ---')
print(t5.to_string(index=False))

# ---------------- Table S6 (two panels) ----------------
# Panel A: development model, 23 covariates + phenotype dummies (the specification
#          used for the incremental-value analysis and for Table 2).
# Panel B: transferred model, 18 covariates + phenotype dummies (the specification
#          applied unchanged to eICU-CRD; this is the deployable model).
DEV_EXTRA = ['mv', 'vaso', 'chf', 'ckd']


def fit_panel(cols, extra=None, tag=''):
    """Continuous covariates are standardised; binary indicators and phenotype
    dummies are entered untransformed, exactly as described in Section 2.6."""
    Xc = pd.DataFrame(index=mm.index)
    for v in cols:
        Xc[v] = num(mm[v])
    med = Xc.median(); sd = Xc.std().replace(0, 1)
    Zc = (Xc.fillna(med) - med) / sd
    Xb = pd.DataFrame(index=mm.index)
    Xb['female'] = pd.Series(mm.gender).astype(str).str.upper().str.startswith('F').astype(int).values
    for v in (extra or []):
        Xb[v] = pd.to_numeric(mm[v], errors='coerce').fillna(0)
    for k in PHEN:
        Xb[k] = (mm['quad'] == k).astype(int)
    Z = pd.concat([Zc, Xb], axis=1)
    fit = sm.Logit(mm_died, sm.add_constant(Z)).fit(disp=0)
    ci = fit.conf_int()
    out = []
    for v in ['const'] + list(Zc.columns) + list(Xb.columns):
        b, se, p = float(fit.params[v]), float(fit.bse[v]), float(fit.pvalues[v])
        lo, hi = float(ci.loc[v, 0]), float(ci.loc[v, 1])
        label = {'const': '(intercept)', 'female': 'Female sex (male = 0)',
                 'mv': 'Invasive mechanical ventilation (0/1)',
                 'vaso': 'Any vasoactive drug infusion (0/1)',
                 'chf': 'Congestive heart failure (0/1)',
                 'ckd': 'Chronic kidney disease (0/1)'}.get(v, NICE.get(v, v))
        is_cont = v in Zc.columns
        out.append(dict(Panel=tag, Term=label, Coding='per 1 SD' if is_cont else 'per unit (0/1)',
                        Median=(round(float(med[v]), 2) if is_cont else '—'),
                        SD=(round(float(sd[v]), 2) if is_cont else '—'),
                        beta=round(b, 4), SE=round(se, 4),
                        OR=('—' if v == 'const' else round(np.exp(b), 3)),
                        OR_low=('—' if v == 'const' else round(np.exp(lo), 3)),
                        OR_high=('—' if v == 'const' else round(np.exp(hi), 3)),
                        p=('%.3g' % p if p >= 1e-4 else '<1e-4')))
    return out


COVS_BASE = [c for c in COVS if c != 'rr_max'] + ['rr_max']   # keep original ordering
t6 = pd.DataFrame(fit_panel(COVS_BASE, DEV_EXTRA, 'A. Development model (23 covariates, MIMIC-IV)')
                  + fit_panel(COVS, None, 'B. Transferred model (18 covariates, applied to eICU-CRD)'))
t6.to_csv(OUT + '/TableS6_full_model_coefficients.csv', index=False)
print('\n--- Table S6 ---')
print(t6.to_string(index=False))
print('\n-> ', OUT + '/TableS5_predictor_distributions.csv')
print('-> ', OUT + '/TableS6_full_model_coefficients.csv')
