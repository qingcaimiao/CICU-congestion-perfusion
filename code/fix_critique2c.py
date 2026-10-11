# -*- coding: utf-8 -*-
"""保存清洗后 eICU 体温 + 外部缺失率 + 外部模型最终数值"""
import duckdb, numpy as np, pandas as pd, json
import statsmodels.api as sm
c = duckdb.connect(); c.execute('PRAGMA threads=8')
E = 'D:/shujuku/EICU 2.0'; D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
def R(p): return "read_csv_auto('%s',header=true,strict_mode=false,ignore_errors=true)" % p
def num(s): return pd.to_numeric(pd.Series(s).astype(str).str.replace('>','',regex=False).str.strip(), errors='coerce')
def auc(y,p):
    y=np.asarray(y).astype(int); r=pd.Series(p).rank().values; n1=y.sum(); n0=len(y)-n1
    return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)

# 1) 清洗后的 eICU 体温（华氏→摄氏；25–45 之外视为缺失）
c.execute(f"""COPY (SELECT p.patientunitstayid,
   avg(CASE WHEN v.temperature BETWEEN 90 AND 115 THEN (v.temperature-32)*5.0/9.0
            WHEN v.temperature BETWEEN 25 AND 45 THEN v.temperature END) AS temp_clean_c
 FROM {R(E+'/patient.csv')} p JOIN {R(E+'/vitalPeriodic.csv')} v ON p.patientunitstayid=v.patientunitstayid
 WHERE p.unittype IN ('Cardiac ICU','CCU-CTICU') GROUP BY 1)
 TO '{D}/eicu_temp_clean.csv' (HEADER, DELIMITER ',')""")
print('清洗后体温已保存 -> T2_data/eicu_temp_clean.csv')

mm = c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()
ee = c.execute(f"SELECT * FROM read_parquet('{D}/eicu_cp.parquet')").df()
ee = ee.rename(columns={'admissionweight':'adm_weight'})
tc = pd.read_csv(D+'/eicu_temp_clean.csv')
ee = ee.drop(columns=['temp_mean']).merge(tc, on='patientunitstayid', how='left').rename(columns={'temp_clean_c':'temp_mean'})
ee['cong_any'] = ((ee.edema_pos.fillna(0)==1)|(ee.jvd_pos.fillna(0)==1)|(ee.crackles.fillna(0)==1)).astype(int)
sub = ee[(ee[['edema_doc','jvd_doc','lungs_doc']].fillna(0).sum(axis=1) > 0) & (ee.perf_doc.fillna(0)==1)].copy()
sub['quad'] = np.where((sub.cong_any==1)&(sub.hypoperf.fillna(0)==1),'WetCold',
              np.where((sub.cong_any==1)&(sub.hypoperf.fillna(0)==0),'WetWarm',
              np.where((sub.cong_any==0)&(sub.hypoperf.fillna(0)==1),'DryCold','DryWarm')))
print('外部集 n=%d  deaths=%d  mortality=%.2f%%' % (len(sub), sub.died.sum(), 100*sub.died.mean()))

# 2) 外部缺失率（Table S1b）
TRANS = ['age','hr_min','hr_max','sbp_min','map_min','rr_max','spo2_min','temp_mean','adm_weight',
         'cr_max','bun_max','na_min','k_max','cl_min','hco3_min','hgb_min','wbc_max','plt_min','glu_max']
rows = []
for v in TRANS:
    miss = 100*num(sub[v]).isna().mean()
    rows.append(dict(covariate=v, eicu_n=len(sub), eicu_missing_pct=round(miss,1)))
ms = pd.DataFrame(rows).sort_values('eicu_missing_pct', ascending=False)
print('\n== 外部验证集协变量缺失率 ==')
print(ms.to_string(index=False))
ms.to_csv(OUT+'/TableS1b_eicu_missingness.csv', index=False)

# 3) 外部模型（清洗体温=主；剔除体温=敏感性）
Xm = pd.DataFrame(index=mm.index)
for v in TRANS: Xm[v] = num(mm[v])
Xm['female'] = mm.gender.astype(str).str.upper().str.startswith('F').astype(int).values
for k in ['WetWarm','DryCold','WetCold']: Xm[k] = (mm.quad==k)
medt = Xm.median(); sdt = Xm.std().replace(0,1)
mfit = sm.Logit(mm.died.values.astype(int), sm.add_constant((Xm.fillna(medt)-medt)/sdt)).fit(disp=0)
Xe0 = pd.DataFrame(index=sub.index)
for v in TRANS: Xe0[v] = num(sub[v])
Xe0['female'] = sub.gender.astype(str).str.upper().str.startswith('F').astype(int).values
for k in ['WetWarm','DryCold','WetCold']: Xe0[k] = (sub.quad==k)
out = {}
for tag, covs in [('main (with cleaned temperature)', TRANS), ('sensitivity (temperature excluded)', [x for x in TRANS if x!='temp_mean'])]:
    cols = covs + ['female','WetWarm','DryCold','WetCold']
    Zm = (Xm[cols].fillna(medt)-medt)/sdt
    dropp = [c for c in cols if float(Zm[c].std()) <= 1e-12]
    if dropp:
        print('  [warn] dropped zero-variance columns:', dropp)
        cols = [c for c in cols if c not in dropp]
        Zm = Zm[cols]
    Hm = sm.add_constant(Zm)
    fit = sm.Logit(mm.died.values.astype(int), Hm).fit(disp=0)
    Ze = ((Xe0[cols].fillna(medt)-medt)/sdt)[cols]
    pe = fit.predict(sm.add_constant(Ze)).values
    ye = sub.died.values.astype(int)
    z = np.log(np.clip(pe,1e-9,1-1e-9)/(1-np.clip(pe,1e-9,1-1e-9)))
    rec = sm.Logit(ye, sm.add_constant(pd.Series(np.asarray(z).ravel(), index=range(len(ye))), has_constant='add')).fit(disp=0)
    pr = np.asarray(rec.params).ravel()
    pm = fit.predict(Hm).values
    out[tag] = dict(apparent_auc=round(auc(mm.died.values, pm),3), external_auc=round(auc(ye, pe),3),
                    oe=round(ye.mean()/max(pe.mean(),1e-9),2), slope=round(float(pr[1]),3), intercept=round(float(pr[0]),3),
                    n=int(len(ye)), deaths=int(ye.sum()), epv=round(int(ye.sum())/len(covs),1), k_vars=len(covs))
    print('\n[%s]' % tag)
    print('   开发集表观 AUC=%.3f | 外部 AUC=%.3f | O:E=%.2f | 校准斜率=%.3f 截距=%+.3f | n=%d deaths=%d | EPV=%.1f'
          % (out[tag]['apparent_auc'], out[tag]['external_auc'], out[tag]['oe'], out[tag]['slope'], out[tag]['intercept'],
             out[tag]['n'], out[tag]['deaths'], out[tag]['epv']))
    if 'main' in tag:
        np.save(OUT+'/pred_eicu_clean.npy', pe)
json.dump(out, open(OUT+'/cp_eicu_final.json','w'), indent=1)
print('\n->', OUT+'/cp_eicu_final.json')
