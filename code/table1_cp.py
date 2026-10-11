# -*- coding: utf-8 -*-
"""Table 1 干净版"""
import duckdb, numpy as np, pandas as pd
from scipy import stats
D  = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT= 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
c=duckdb.connect()
mm=c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()
mm['female']=mm.gender.astype(str).str.upper().str.startswith('F').astype(int)
order=['DryWarm','WetWarm','DryCold','WetCold']
def num(s): return pd.to_numeric(pd.Series(s).astype(str).str.replace('>','',regex=False).str.strip(),errors='coerce')
def pf(p): return '%.3f'%p if p>=0.001 else '%.1e'%p
CONT=[('age','Age, years'),('adm_weight','Admission weight, kg'),('los','ICU length of stay, days'),
 ('hr_min','Heart rate, minimum, bpm'),('hr_max','Heart rate, maximum, bpm'),
 ('sbp_min','Systolic blood pressure, minimum, mmHg'),('map_min','Mean arterial pressure, minimum, mmHg'),
 ('rr_max','Respiratory rate, maximum, breaths/min'),('spo2_min','Oxygen saturation, minimum, %'),
 ('temp_mean','Temperature, mean, °C'),('cr_max','Creatinine, maximum, mg/dL'),('bun_max','Urea nitrogen, maximum, mg/dL'),
 ('na_min','Sodium, minimum, mmol/L'),('k_max','Potassium, maximum, mmol/L'),('cl_min','Chloride, minimum, mmol/L'),
 ('hco3_min','Bicarbonate, minimum, mmol/L'),('hgb_min','Haemoglobin, minimum, g/dL'),
 ('wbc_max','White blood cells, maximum, K/µL'),('plt_min','Platelets, minimum, K/µL'),
 ('glu_max','Glucose, maximum, mg/dL'),('ew','Oedema grade (0–5)')]
BIN=[('female','Female sex'),('mv','Invasive mechanical ventilation'),('vaso','Vasopressors'),
 ('chf','Congestive heart failure'),('chd','Coronary heart disease'),('ckd','Chronic kidney disease'),
 ('dm','Diabetes mellitus'),('aki','Acute kidney injury'),('cr_abn','Prolonged capillary refill (>3 s)')]
rows=[]
rows.append(dict(Variable='N', **{o:f'{int((mm.quad==o).sum()):,}' for o in order}, p=''))
for k,lab in CONT:
    v=num(mm[k]); grp=[v[mm.quad==o].dropna() for o in order]
    p=stats.kruskal(*[g for g in grp if len(g)>5]).pvalue
    rows.append(dict(Variable=lab, **{o:(f'{g.median():.1f} ({g.quantile(.25):.1f}–{g.quantile(.75):.1f})' if len(g) else '–') for o,g in zip(order,grp)}, p=pf(p)))
for k,lab in BIN:
    v=pd.to_numeric(mm[k],errors='coerce').fillna(0)
    p=stats.chi2_contingency(pd.crosstab(mm.quad,v))[1]
    rows.append(dict(Variable=lab, **{o:(f'{int(v[mm.quad==o].sum())} ({100*v[mm.quad==o].mean():.1f})' if (mm.quad==o).sum() else '–') for o in order}, p=pf(p)))
rows.append(dict(Variable='In-hospital mortality, n (%)',
                 **{o:f'{int(mm[mm.quad==o].died.sum())} ({100*mm[mm.quad==o].died.mean():.2f})' for o in order}, p='<0.001'))
t=pd.DataFrame(rows)
t.to_csv(OUT+'/Table1_baseline_by_quadrant.csv', index=False)
print(t.to_string(index=False, max_colwidth=34))
