# -*- coding: utf-8 -*-
"""TRIPOD+AI item 20c: comparison of the distribution of the transferable predictors
between the development (MIMIC-IV) and replication (eICU-CRD) analysis sets.

Uses exactly the same cohort definitions and the same 'keep' filter (>=60% of the
transferable covariates available) as final_eicu_model.py, so the numbers reconcile
with the reported external validation.
"""
import duckdb
import numpy as np
import pandas as pd

c = duckdb.connect(); c.execute('PRAGMA threads=8')
D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'


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

# covariates of the transferred model (temperature excluded from the primary model)
COVS = ['age', 'hr_min', 'hr_max', 'sbp_min', 'map_min', 'rr_max', 'spo2_min', 'adm_weight',
        'cr_max', 'bun_max', 'na_min', 'k_max', 'cl_min', 'hco3_min', 'hgb_min', 'wbc_max',
        'plt_min', 'glu_max']
PHEN = ['WetWarm', 'DryCold', 'WetCold']          # reference: DryWarm

Xm = pd.DataFrame(index=mm.index)
Xe = pd.DataFrame(index=sub.index)
for v in COVS:
    Xm[v] = num(mm[v]); Xe[v] = num(sub[v])
Xm['female'] = pd.Series(mm.gender).astype(str).str.upper().str.startswith('F').astype(int).values
Xe['female'] = pd.Series(sub.gender).astype(str).str.upper().str.startswith('F').astype(int).values
for k in PHEN:
    Xm[k] = (mm['quad'] == k).astype(int)
    Xe[k] = (sub['quad'] == k).astype(int)
Xm['In-hospital death'] = mm['died'].astype(int)
Xe['In-hospital death'] = sub['died'].astype(int)

# same availability filter as the external validation
ok = Xe[COVS].notna().mean(axis=1) >= 0.6
Xe = Xe.loc[ok]
print('development n = %d (deaths %d) | replication n = %d (deaths %d)'
      % (len(Xm), int(Xm['In-hospital death'].sum()), len(Xe), int(Xe['In-hospital death'].sum())))


def smd_cont(a, b):
    a = a.dropna(); b = b.dropna()
    if len(a) < 3 or len(b) < 3:
        return np.nan
    s = np.sqrt((a.std() ** 2 + b.std() ** 2) / 2)
    return (a.mean() - b.mean()) / s if s > 0 else np.nan


def smd_bin(p1, p2):
    s = np.sqrt((p1 * (1 - p1) + p2 * (1 - p2)) / 2)
    return (p1 - p2) / s if s > 0 else np.nan


rows = []
for v in ['age', 'female'] + COVS + PHEN + ['In-hospital death']:
    a, b = Xm[v], Xe[v]
    na, nb = a.notna().sum(), b.notna().sum()
    if v in ('female',) or v in PHEN or v == 'In-hospital death':
        p1, p2 = a.mean(), b.mean()
        rows.append(dict(Variable=v, Type='n (%)',
                         Development='%d (%.1f)' % (int(a.sum()), 100 * p1),
                         Replication='%d (%.1f)' % (int(b.sum()), 100 * p2),
                         SMD=round(float(smd_bin(p1, p2)), 2),
                         Development_n=int(na), Replication_n=int(nb)))
    else:
        rows.append(dict(Variable=v, Type='median (IQR)',
                         Development='%.1f (%.1f–%.1f)' % (a.median(), a.quantile(.25), a.quantile(.75)),
                         Replication='%.1f (%.1f–%.1f)' % (b.median(), b.quantile(.25), b.quantile(.75)),
                         SMD=round(float(smd_cont(a, b)), 2),
                         Development_n=int(na), Replication_n=int(nb)))

t = pd.DataFrame(rows)
t.to_csv(OUT + '/TableS5_predictor_distributions.csv', index=False)
print(t.to_string(index=False))
print('\n->', OUT + '/TableS5_predictor_distributions.csv')
print('\n|SMD| > 0.20 的变量:')
print(', '.join('%s (%.2f)' % (r.Variable, r.SMD) for r in t.itertuples()
                if r.Type == 'median (IQR)' and abs(r.SMD) > 0.20) or '(none)')
