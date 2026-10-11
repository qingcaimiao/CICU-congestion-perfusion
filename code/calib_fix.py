# -*- coding: utf-8 -*-
"""校准斜率（修正：限定于四象限可判定集 n=1555，与外部复现一致）"""
import duckdb, numpy as np, pandas as pd, json, warnings
warnings.filterwarnings('ignore')
import statsmodels.api as sm
D  = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT= 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
c=duckdb.connect(); c.execute('PRAGMA threads=8')
ee=c.execute(f"SELECT * FROM read_parquet('{D}/eicu_cp.parquet')").df()
mm=c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()
ee['cong_any']=((ee.edema_pos.fillna(0)==1)|(ee.jvd_pos.fillna(0)==1)|(ee.crackles.fillna(0)==1)).astype(int)
sel = ((ee.edema_doc.fillna(0)+ee.jvd_doc.fillna(0)+ee.lungs_doc.fillna(0))>0) & (ee.perf_doc.fillna(0)==1)
d=ee[sel].copy()
print('eICU 四象限可判定 n =', len(d), ' deaths =', int(d.died.sum()), '(%.2f%%)'%(100*d.died.mean()))
def num(s): return pd.to_numeric(pd.Series(s).astype(str).str.replace('>','',regex=False).str.strip(),errors='coerce')
TRANS=['age','hr_min','hr_max','sbp_min','map_min','rr_max','spo2_min','temp_mean','adm_weight',
       'cr_max','bun_max','na_min','k_max','cl_min','hco3_min','hgb_min','wbc_max','plt_min','glu_max']
def build(x, quad):
    X=pd.DataFrame(index=x.index)
    for v in TRANS: X[v]=num(x[v]) if v in x.columns else np.nan
    X['female']=pd.Series(x.gender).astype(str).str.upper().str.startswith('F').astype(int).values
    for k in ['WetWarm','DryCold','WetCold']: X[k]=(quad==k).astype(int)
    return X
qm=mm['quad'].values
Xm=build(mm, pd.Series(qm, index=mm.index)); medt=Xm.median(); sdt=Xm.std().replace(0,1)
mt=sm.Logit(mm.died.values.astype(int), sm.add_constant(((Xm.fillna(medt)-medt)/sdt))).fit(disp=0)
qe=pd.Series(np.where((d.cong_any==1)&(d.hypoperf.fillna(0)==1),'WetCold',
             np.where((d.cong_any==1)&(d.hypoperf.fillna(0)==0),'WetWarm',
             np.where((d.cong_any==0)&(d.hypoperf.fillna(0)==1),'DryCold','DryWarm'))), index=d.index)
Xe=build(d, qe); Ze=(Xe.fillna(medt)-medt)/sdt
ok=Ze[TRANS].notna().mean(axis=1)>=0.6
Ze=Ze[ok]; ye=d.died.values[ok].astype(int)
pe=mt.predict(sm.add_constant(Ze)).values
z=np.log(np.clip(pe,1e-9,1-1e-9)/(1-np.clip(pe,1e-9,1-1e-9)))
rec=sm.Logit(ye, sm.add_constant(z)).fit(disp=0)
p=rec.params; a0=float(p.iloc[0] if hasattr(p,'iloc') else p[0]); a1=float(p.iloc[1] if hasattr(p,'iloc') else p[1])
def auc(y,pp):
    y=np.asarray(y).astype(int); r=pd.Series(pp).rank().values; n1=y.sum(); n0=len(y)-n1
    return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)
print('n = %d, events = %d' % (len(ye), ye.sum()))
print('  校准截距 = %+.3f' % a0)
print('  校准斜率 = %.3f' % a1)
print('  O:E = %.2f' % (ye.mean()/max(pe.mean(),1e-9)))
print('  外部 AUC = %.3f' % auc(ye,pe))
q=pd.qcut(pe,8,labels=False,duplicates='drop')
cal=pd.DataFrame({'p':pe,'y':ye,'b':q}).groupby('b').agg(pred=('p','mean'),obs=('y','mean'),n=('y','size')).round(4)
print('\n外部校准（8 分位）：'); print(cal.to_string())
cal.to_csv(OUT+'/T_calibration_eicu.csv')
json.dump({'n':int(len(ye)),'events':int(ye.sum()),'calib_intercept':a0,'calib_slope':a1,
           'oe':float(ye.mean()/max(pe.mean(),1e-9)),'external_auc':float(auc(ye,pe))},
          open(OUT+'/cp_eicu_calibration.json','w'), indent=1)
print('\nsaved')
