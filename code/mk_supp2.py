# -*- coding: utf-8 -*-
"""补充表 S1–S4 重新生成 + like-for-like OR 复核（体温已从模型剔除）"""
import duckdb, numpy as np, pandas as pd, json
import statsmodels.api as sm
c = duckdb.connect(); c.execute('PRAGMA threads=8')
OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
SUB = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包'
def num(s): return pd.to_numeric(pd.Series(s).astype(str).str.replace('>','',regex=False).str.strip(), errors='coerce')

mm = c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()
MODEL18 = ['age','hr_min','hr_max','sbp_min','map_min','rr_max','spo2_min','adm_weight',
           'cr_max','bun_max','na_min','k_max','cl_min','hco3_min','hgb_min','wbc_max','plt_min','glu_max']
EXTRA = ['mv','vaso','chf','ckd']

# ---- Table S1: MIMIC missingness ----
rows = []
for v in MODEL18:
    rows.append(dict(Covariate=v, Missing=round(100*num(mm[v]).isna().mean(), 1)))
s1 = pd.DataFrame(rows)
s1.loc[len(s1)] = {'Covariate': 'temp_mean (screened, not in model)', 'Missing': round(100*num(mm['temp_mean']).isna().mean(), 1)}
s1.loc[len(s1)] = {'Covariate': 'oedema grade', 'Missing': round(100*mm.ew.isna().mean(), 1)}
s1.loc[len(s1)] = {'Covariate': 'capillary refill', 'Missing': round(100*mm.cr_abn.isna().mean(), 1)}
s1 = s1.sort_values('Missing', ascending=False)
s1.to_csv(OUT+'/TableS1_mimic_missingness.csv', index=False)
print('== Table S1 =='); print(s1.to_string(index=False))

# ---- like-for-like OR ----
d = mm.dropna(subset=['quad']).copy()
d['oed6'] = (pd.to_numeric(d.ew, errors='coerce') >= 3).astype(int)
d['cr'] = pd.to_numeric(d.cr_abn, errors='coerce').astype(int)
X = pd.DataFrame(index=d.index)
for v in MODEL18:
    if v in EXTRA or v == 'age':
        X[v] = num(d[v])
    else:
        X[v] = num(d[v])
X = X.drop(columns=[c2 for c2 in ['age'] if c2 not in MODEL18], errors='ignore')
X['female'] = d.gender.astype(str).str.upper().str.startswith('F').astype(int).values
X['oed6'] = d.oed6.values; X['cr'] = d.cr.values
med = X.median(); sd = X.std().replace(0,1)
Z = X.copy()
for c2 in [cc for cc in X.columns if cc not in ('female','oed6','cr')]:
    Z[c2] = (X[c2].fillna(med[c2]) - med[c2]) / sd[c2]
Z['oed6'] = X['oed6']; Z['cr'] = X['cr']
fit = sm.Logit(d.died.values.astype(int), sm.add_constant(Z)).fit(disp=0)
tb = fit.summary2().tables[1]
lfl = {}
for k in ['oed6','cr']:
    co, se = tb.loc[k,'Coef.'], tb.loc[k,'Std.Err.']
    lfl[k] = (round(np.exp(co),2), round(np.exp(co-1.96*se),2), round(np.exp(co+1.96*se),2), tb.loc[k,'P>|z|'])
print('\n== Like-for-like (oedema >=6mm dichotomised + prolonged CRT in one model) ==')
print('   oedema >=6 mm : OR %.2f (%.2f-%.2f) p=%.2g' % lfl['oed6'])
print('   prolonged CRT : OR %.2f (%.2f-%.2f) p=%.2g' % lfl['cr'])
print('   ratio of ORs  : %.2f' % (lfl['cr'][0]/lfl['oed6'][0]))

# ---- Table S1b / S3 / S4 ----
s1b = pd.read_csv(OUT+'/TableS1b_eicu_missingness.csv')
s3 = pd.read_csv(OUT+'/TableS3_eicu_definitions_full.csv')
s4 = pd.read_csv(OUT+'/TableS4_edema_value_frequency.csv', keep_default_na=False)
s2 = pd.read_csv(OUT+'/T_ppv_npv.csv')
print('\n== Table S1b =='); print(s1b.to_string(index=False))
print('\n== Table S3 =='); print(s3.to_string(index=False))
print('\n== Table S4 =='); print(s4.to_string(index=False))
print('\n== Table S2 =='); print(s2.to_string(index=False))

def md(df, cols=None):
    d = df if cols is None else df[cols]
    h = '| ' + ' | '.join(str(c) for c in d.columns) + ' |'
    sep = '|' + '|'.join(['---']*len(d.columns)) + '|'
    rows = ['| ' + ' | '.join('' if pd.isna(v) else str(v) for v in r) + ' |' for r in d.values]
    return '\n'.join([h, sep] + rows)

s3p = s3.pivot(index='definition', columns='cell', values=['n','deaths','mortality'])
s3out = pd.DataFrame({
    'Definition of congestion': s3p.index,
    'n': [int(s3p.loc[i,('n','DryWarm')] + s3p.loc[i,('n','WetWarm')] + s3p.loc[i,('n','DryCold')] + s3p.loc[i,('n','WetCold')]) for i in s3p.index],
    'Deaths': [int(s3p.loc[i,('deaths','DryWarm')] + s3p.loc[i,('deaths','WetWarm')] + s3p.loc[i,('deaths','DryCold')] + s3p.loc[i,('deaths','WetCold')]) for i in s3p.index],
    'Dry-warm %': [s3p.loc[i,('mortality','DryWarm')] for i in s3p.index],
    'Wet-warm %': [s3p.loc[i,('mortality','WetWarm')] for i in s3p.index],
    'Dry-cold %': [s3p.loc[i,('mortality','DryCold')] for i in s3p.index],
    'Wet-cold %': [s3p.loc[i,('mortality','WetCold')] for i in s3p.index],
    'Wet-warm minus dry-warm (pp)': [s3.loc[s3.definition==i,'wet_minus_dry_warm'].iloc[0] for i in s3p.index],
    'Dry-cold minus dry-warm (pp)': [round(s3p.loc[i,('mortality','DryCold')]-s3p.loc[i,('mortality','DryWarm')],2) for i in s3p.index],
})
s3out.to_csv(OUT+'/TableS3_final.csv', index=False)
print('\n== 最终 Table S3 =='); print(s3out.to_string(index=False))

tx = ['# Supplementary tables', '',
 '## Table S1. Missingness of covariates in the primary analysis set (MIMIC-IV, n = 12,052)', '',
 'Percentage of stays with a missing value. The model contains 18 transferable covariates. Temperature was screened and excluded from the transferred model because it was available in only 31% of the replication set (Table S1b); its missingness in MIMIC-IV is shown for comparison. Oedema grade and capillary refill define the analysis set and are therefore complete by construction.', '',
 md(s1), '',
 '## Table S1b. Missingness of the same covariates in the external replication set (eICU-CRD, n = 1,555)', '',
 'Percentage of stays with a missing value. With the exception of temperature, all transferable covariates are ≥96% complete, so the transferred model is not driven by imputation.', '',
 md(s1b.rename(columns={'covariate':'Covariate','eicu_missing_pct':'Missing (%)'})[['Covariate','Missing (%)']]), '',
 '## Table S2. Performance of the phenotype used as a zero-cost screening rule (MIMIC-IV)', '',
 'PPV, positive predictive value; NPV, negative predictive value. Cohort event rate 6.29%.', '',
 md(s2), '',
 '## Table S3. External replication in eICU-CRD by definition of congestion', '',
 'Impaired perfusion was defined identically throughout (any value other than "adequate" in `physicalExam/extremities/perfusion`). Exposure fields: peripheral oedema `physicalExam/extremities/edema/...`; jugular venous distension `physicalExam/neck/jvd`; pulmonary crackles `physicalExam/pulmonary/auscultation`. Only stays in which congestion and perfusion were both *documented* (5–9% of stays) are included. The penultimate column isolates the congestion effect with perfusion held adequate (wet-warm minus dry-warm) and is small and inconsistent across definitions (−0.19 to +2.88 percentage points, i.e. no monotone or definition-robust congestion gradient), whereas the final column shows that the perfusion contrast with congestion held absent (dry-cold minus dry-warm) is large and consistent (+21 to +27 percentage points) under every definition. Note also that eICU-CRD contains no nurse-charted pitting-depth scale equivalent to MIMIC-IV itemid 224862, so these are different measurements of the same clinical construct rather than a replication of the same variable.', '',
 md(s3out), '',
 '## Table S4. Value domain of the MIMIC-IV Edema Amount item (itemid 224862)', '',
 'All values charted for itemid 224862 within the 20,806-stay cohort are listed. The domain contains only these six options, so the ordinal mapping required no free-text parsing and no unit assumptions; 0 records (0.00%) fell outside the mapped set.', '',
 md(s4.rename(columns={'raw_value':'Charted value','n':'Records','n_stay':'Stays','grade':'Ordinal grade','pct':'% of records'})[['Charted value','Ordinal grade','Records','% of records','Stays']]), '']
open(SUB+'/Supplementary_Tables.md', 'w', encoding='utf-8').write('\n'.join(tx))
print('\n-> Supplementary_Tables.md regenerated')
json.dump({'like_for_like': {k: list(v) for k, v in lfl.items()}}, open(OUT+'/cp_likeforlike.json','w'), indent=1)
