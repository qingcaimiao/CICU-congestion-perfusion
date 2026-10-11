# -*- coding: utf-8 -*-
"""eICU 单体征敏感性 + 校准斜率（logistic 重校准）"""
import duckdb, numpy as np, pandas as pd, json, warnings
warnings.filterwarnings('ignore')
import statsmodels.api as sm
D  = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT= 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
c=duckdb.connect(); c.execute('PRAGMA threads=8')
ee=c.execute(f"SELECT * FROM read_parquet('{D}/eicu_cp.parquet')").df()

print('== eICU 单体征死亡率梯度（不使用复合定义）==')
rows=[]
defs=[('edema_pos','edema_doc','Peripheral oedema only'),
      ('jvd_pos','jvd_doc','Jugular venous distension only'),
      ('crackles','lungs_doc','Pulmonary crackles only'),
      ('hypoperf','perf_doc','Impaired peripheral perfusion')]
for pos,doc,lab in defs:
    d=ee[ee[doc].fillna(0)==1]
    a=d[d[pos].fillna(0)==1]; b=d[d[pos].fillna(0)==0]
    if len(a)>0 and len(b)>0:
        print('   %-32s (+) n=%5d mort=%5.2f%% | (-) n=%5d mort=%5.2f%% | ratio %.2f' % (
            lab, len(a), 100*a.died.mean(), len(b), 100*b.died.mean(),
            (a.died.mean()/max(b.died.mean(),1e-9))))
        rows.append({'definition':lab,'n_pos':int(len(a)),'mort_pos':round(100*a.died.mean(),2),
                     'n_neg':int(len(b)),'mort_neg':round(100*b.died.mean(),2),
                     'ratio':round(a.died.mean()/max(b.died.mean(),1e-9),2)})
pd.DataFrame(rows).to_csv(OUT+'/T_eicu_single_sign.csv',index=False)

# 每一种单体征作为"充血"定义的四象限复现
print('\n== eICU：不同充血定义下的四象限梯度 ==')
out=[]
for cong_col,cong_doc,lab in [('edema_pos','edema_doc','oedema only'),
                              ('jvd_pos','jvd_doc','JVD only'),
                              ('crackles','lungs_doc','crackles only'),
                              ('cong_any',None,'composite (oedema/JVD/crackles)')]:
    if cong_col=='cong_any':
        ee['cong_any']=((ee.edema_pos.fillna(0)==1)|(ee.jvd_pos.fillna(0)==1)|(ee.crackles.fillna(0)==1)).astype(int)
    d=ee[(ee[cong_doc].fillna(0)==1 if cong_doc else (ee.edema_doc.fillna(0)+ee.jvd_doc.fillna(0)+ee.lungs_doc.fillna(0))>0) & (ee.perf_doc.fillna(0)==1)].copy()
    d['q']=np.where((d[cong_col]==1)&(d.hypoperf.fillna(0)==1),'WetCold',
          np.where((d[cong_col]==1)&(d.hypoperf.fillna(0)==0),'WetWarm',
          np.where((d[cong_col]==0)&(d.hypoperf.fillna(0)==1),'DryCold','DryWarm')))
    t=d.groupby('q').agg(n=('died','size'),mort=('died',lambda s:100*s.mean())).round(2)
    t=t.reindex(['DryWarm','WetWarm','DryCold','WetCold'])
    spread = (t.mort.max()-t.mort.min()) if t.mort.notna().sum()>1 else np.nan
    print('   [%s] n=%d  DryWarm=%.2f WetWarm=%.2f DryCold=%.2f WetCold=%.2f  (spread %.1f)' % (
        lab, len(d), t.mort.get('DryWarm',np.nan), t.mort.get('WetWarm',np.nan),
        t.mort.get('DryCold',np.nan), t.mort.get('WetCold',np.nan), spread))
    out.append({'definition':lab,'n':int(len(d)),'DryWarm':t.mort.get('DryWarm'),'WetWarm':t.mort.get('WetWarm'),
                'DryCold':t.mort.get('DryCold'),'WetCold':t.mort.get('WetCold'),'spread':spread,
                'wet_minus_dry_at_normal_perfusion': (t.mort.get('WetWarm',np.nan)-t.mort.get('DryWarm',np.nan))})
eo=pd.DataFrame(out); eo.to_csv(OUT+'/T_eicu_congestion_definitions.csv',index=False)
print('\n   关键判读：若 WetWarm 与 DryWarm 几乎无差别，说明"充血轴"在 eICU 单独不成立。')

# ---------- 校准斜率（logistic 重校准） ----------
mm=c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()
ee2=ee[(ee.edema_doc.fillna(0)+ee.jvd_doc.fillna(0)+ee.lungs_doc.fillna(0))>0 & (ee.perf_doc.fillna(0)==1)].copy()
ee2['cong_any']=((ee2.edema_pos.fillna(0)==1)|(ee2.jvd_pos.fillna(0)==1)|(ee2.crackles.fillna(0)==1)).astype(int)
ee2['q']=np.where((ee2.cong_any==1)&(ee2.hypoperf.fillna(0)==1),'WetCold',
        np.where((ee2.cong_any==1)&(ee2.hypoperf.fillna(0)==0),'WetWarm',
        np.where((ee2.cong_any==0)&(ee2.hypoperf.fillna(0)==1),'DryCold','DryWarm')))
def num(s): return pd.to_numeric(pd.Series(s).astype(str).str.replace('>','',regex=False).str.strip(),errors='coerce')
TRANS=['age','hr_min','hr_max','sbp_min','map_min','rr_max','spo2_min','temp_mean','adm_weight',
       'cr_max','bun_max','na_min','k_max','cl_min','hco3_min','hgb_min','wbc_max','plt_min','glu_max']
def build(d):
    X=pd.DataFrame(index=d.index)
    for v in TRANS: X[v]=num(d[v]) if v in d.columns else np.nan
    X['female']=pd.Series(d.gender).astype(str).str.upper().str.startswith('F').astype(int).values
    for k,qd in [('WetWarm','WetWarm'),('DryCold','DryCold'),('WetCold','WetCold')]: X[k]=(d['quad'] if 'quad' in d.columns else d['q'])==qd
    return X
Xm=build(mm); medt=Xm.median(); sdt=Xm.std().replace(0,1)
mt=sm.Logit(mm.died.values.astype(int), sm.add_constant((Xm.fillna(medt)-medt)/sdt)).fit(disp=0)
Xe=build(ee2); Xe=Xe.rename(columns={}) ; Xe['age']=num(ee2.age)
Ze=(Xe.fillna(medt)-medt)/sdt
ok=Ze[TRANS].notna().mean(axis=1)>=0.6; Ze=Ze[ok]; ye=ee2.died.values[ok].astype(int)
pe=mt.predict(sm.add_constant(Ze)).values
z=np.log(np.clip(pe,1e-9,1-1e-9)/(1-np.clip(pe,1e-9,1-1e-9)))
rec=sm.Logit(ye, sm.add_constant(z)).fit(disp=0)
print('\n== 校准（logistic 重校准, eICU n=%d, events=%d）=='%(len(ye), ye.sum()))
print('   校准截距 = %+.3f ; 校准斜率 = %.3f' % (rec.params.iloc[0] if hasattr(rec.params,'iloc') else rec.params[0],
                                                  rec.params.iloc[1] if hasattr(rec.params,'iloc') else rec.params[1]))
print('   O:E = %.2f' % (ye.mean()/max(pe.mean(),1e-9)))
def auc(y,p):
    y=np.asarray(y).astype(int); r=pd.Series(p).rank().values; n1=y.sum(); n0=len(y)-n1
    return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)
pre=rec.predict(sm.add_constant(z))
print('   外部 AUC（原系数）= %.3f ; 重校准后 AUC（斜率校正，判别力不变）= %.3f' % (auc(ye,pe), auc(ye,pre)))
json.dump({'calib_intercept':float(rec.params.iloc[0] if hasattr(rec.params,'iloc') else rec.params[0]),
           'calib_slope':float(rec.params.iloc[1] if hasattr(rec.params,'iloc') else rec.params[1]),
           'oe':float(ye.mean()/max(pe.mean(),1e-9)),'external_auc':float(auc(ye,pe))},
          open(OUT+'/cp_eicu_calibration.json','w'), indent=1)
print('\nsaved ->', OUT)
