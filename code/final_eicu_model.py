# -*- coding: utf-8 -*-
"""外部模型最终数值（体温含/不含两版）+ 校准 + 预测值导出"""
import duckdb, numpy as np, pandas as pd, json
import statsmodels.api as sm
c = duckdb.connect(); c.execute('PRAGMA threads=8')
D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
def num(s): return pd.to_numeric(pd.Series(s).astype(str).str.replace('>','',regex=False).str.strip(), errors='coerce')
def auc(y,p):
    y=np.asarray(y).astype(int); r=pd.Series(p).rank().values; n1=y.sum(); n0=len(y)-n1
    return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)

mm = c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()
ee = c.execute(f"SELECT * FROM read_parquet('{D}/eicu_cp.parquet')").df().rename(columns={'admissionweight':'adm_weight'})
tc = pd.read_csv(D+'/eicu_temp_clean.csv')
ee = ee.drop(columns=['temp_mean']).merge(tc, on='patientunitstayid', how='left').rename(columns={'temp_clean_c':'temp_mean'})
ee['cong_any'] = ((ee.edema_pos.fillna(0)==1)|(ee.jvd_pos.fillna(0)==1)|(ee.crackles.fillna(0)==1)).astype(int)
sub = ee[(ee[['edema_doc','jvd_doc','lungs_doc']].fillna(0).sum(axis=1) > 0) & (ee.perf_doc.fillna(0)==1)].copy()
sub['quad'] = np.where((sub.cong_any==1)&(sub.hypoperf.fillna(0)==1),'WetCold',
              np.where((sub.cong_any==1)&(sub.hypoperf.fillna(0)==0),'WetWarm',
              np.where((sub.cong_any==0)&(sub.hypoperf.fillna(0)==1),'DryCold','DryWarm')))

TRANS = ['age','hr_min','hr_max','sbp_min','map_min','rr_max','spo2_min','temp_mean','adm_weight',
         'cr_max','bun_max','na_min','k_max','cl_min','hco3_min','hgb_min','wbc_max','plt_min','glu_max']
def frame(d, covs):
    X = pd.DataFrame(index=d.index)
    for v in covs: X[v] = num(d[v])
    X['female'] = pd.Series(d.gender).astype(str).str.upper().str.startswith('F').astype(int).values
    for k in ['WetWarm','DryCold','WetCold']: X[k] = (d['quad'] == k).astype(int)
    return X

out = {}
for tag, covs in [('with temperature', TRANS), ('temperature excluded', [x for x in TRANS if x != 'temp_mean'])]:
    Xm = frame(mm, covs); Xe = frame(sub, covs)
    ok = Xe[covs].notna().mean(axis=1) >= 0.6          # ≥60% of transferable covariates available
    keep = ok.values
    medt = Xm.median(); sdt = Xm.std().replace(0, 1)
    Zm = (Xm.fillna(medt) - medt) / sdt
    Ze_all = (Xe.fillna(medt) - medt) / sdt
    Ze = Ze_all.loc[keep]
    assert Zm.notna().all().all() and Ze.notna().all().all()
    fit = sm.Logit(mm.died.values.astype(int), sm.add_constant(Zm)).fit(disp=0)
    pe = fit.predict(sm.add_constant(Ze)).values
    ye = sub.died.values[keep].astype(int)
    z = np.log(np.clip(pe,1e-9,1-1e-9)/(1-np.clip(pe,1e-9,1-1e-9)))
    rec = sm.Logit(ye, sm.add_constant(pd.Series(np.asarray(z).ravel(), index=range(len(ye))), has_constant='add')).fit(disp=0)
    pr = np.asarray(rec.params).ravel()
    pm = fit.predict(sm.add_constant(Zm)).values
    d = dict(apparent_auc=round(auc(mm.died.values, pm), 3), external_auc=round(auc(ye, pe), 3),
             oe=round(ye.mean()/max(pe.mean(),1e-9), 2), slope=round(float(pr[1]), 3), intercept=round(float(pr[0]), 3),
             n=int(len(ye)), deaths=int(ye.sum()), epv=round(int(ye.sum())/len(covs), 1), n_vars=len(covs),
             mean_pred=round(float(100*pe.mean()), 2), obs=round(float(100*ye.mean()), 2))
    out[tag] = d
    print('[%s] 变量 %d | 开发表观 AUC=%.3f | 外部 AUC=%.3f | O:E=%.2f | 斜率=%.3f 截距=%+.3f | EPV=%.1f | 预测均值 %.2f%% vs 实际 %.2f%%'
          % (tag, len(covs), d['apparent_auc'], d['external_auc'], d['oe'], d['slope'], d['intercept'], d['epv'], d['mean_pred'], d['obs']))
    if tag == 'temperature excluded':
        np.save(OUT+'/pred_eicu_clean.npy', pe)
        np.save(OUT+'/pred_mimic_apparent.npy', pm)
json.dump(out, open(OUT+'/cp_eicu_final.json', 'w'), indent=1)
print('\n->', OUT+'/cp_eicu_final.json')
