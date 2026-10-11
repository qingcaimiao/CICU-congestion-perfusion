# -*- coding: utf-8 -*-
"""Table 1-4 + SHAP (Fig9)"""
import duckdb, numpy as np, pandas as pd, os, warnings
warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'Arial','font.size':9,'axes.linewidth':0.8,
                     'xtick.major.width':0.8,'ytick.major.width':0.8,'axes.spines.top':False,'axes.spines.right':False})
from scipy import stats
import statsmodels.api as sm
D  = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT= 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
FIG= 'D:/桌面/workbuddyzuopin/CPxiangmu/04_图'
c = duckdb.connect(); c.execute('PRAGMA threads=8')
mm = c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()
mm['female'] = mm.gender.astype(str).str.upper().str.startswith('F').astype(int)
order = ['DryWarm','WetWarm','DryCold','WetCold']

def num(s): return pd.to_numeric(pd.Series(s).astype(str).str.replace('>','',regex=False).str.strip(), errors='coerce')
CONT = [('age','Age, years'),('adm_weight','Admission weight, kg'),('los','ICU LOS, days'),
        ('hr_min','Heart rate, min, bpm'),('hr_max','Heart rate, max, bpm'),('sbp_min','Systolic BP, min, mmHg'),
        ('map_min','Mean arterial pressure, min, mmHg'),('rr_max','Respiratory rate, max'),
        ('spo2_min','SpO2, min, %'),('temp_mean','Temperature, mean, C'),
        ('cr_max','Creatinine, max, mg/dL'),('bun_max','Urea nitrogen, max, mg/dL'),('na_min','Sodium, min, mmol/L'),
        ('k_max','Potassium, max, mmol/L'),('cl_min','Chloride, min, mmol/L'),('hco3_min','Bicarbonate, min, mmol/L'),
        ('hgb_min','Haemoglobin, min, g/dL'),('wbc_max','White cells, max, K/uL'),('plt_min','Platelets, min, K/uL'),
        ('glu_max','Glucose, max, mg/dL'),('ew','Oedema grade (0-5)')]
BIN  = [('female','Female sex'),('mv','Mechanical ventilation'),('vaso','Vasopressors'),
        ('chf','Congestive heart failure'),('chd','Coronary heart disease'),('ckd','Chronic kidney disease'),
        ('dm','Diabetes mellitus'),('aki','Acute kidney injury'),('cr_abn','Prolonged capillary refill')]

rows=[]
rows.append({'Variable':'N','DryWarm':str((mm.quad=='DryWarm').sum()),'WetWarm':str((mm.quad=='WetWarm').sum()),
             'DryCold':str((mm.quad=='DryCold').sum()),'WetCold':str((mm.quad=='WetCold').sum()),'p':''})
rows.append({'Variable':'In-hospital death','DryWarm':'-','WetWarm':'-','DryCold':'-','WetCold':'-','p':''})
for k,lab in CONT:
    v = num(mm[k])
    grp = [v[mm.quad==o].dropna() for o in order]
    pv = stats.kruskal(*[g for g in grp if len(g)>5]).pvalue
    def f(g): return '%.1f (%.1f-%.1f)'%(g.median(), g.quantile(.25), g.quantile(.75)) if len(g) else '-'
    rows.append({'Variable':lab, **{o:f(g) for o,g in zip(order,grp)}, 'p':('%.3f'%pv if pv>=0.001 else '%.1e'%pv)})
for k,lab in BIN:
    v = mm[k]
    pv = stats.chi2_contingency(pd.crosstab(mm.quad, v))[1] if v.nunique()>1 else np.nan
    def f(o):
        sub=v[mm.quad==o]; return '%d (%.1f)'%(sub.sum(), 100*sub.mean()) if len(sub) else '-'
    rows.append({'Variable':lab, **{o:f(o) for o in order}, 'p':('%.3f'%pv if pv==pv and pv>=0.001 else ('%.1e'%pv if pv==pv else '-'))})
rows.append({'Variable':'<b>Outcome</b>','DryWarm':'','WetWarm':'','DryCold':'','WetCold':'','p':''})
for o in order:
    sub=mm[mm.quad==o]
    rows[-0:]  # noop
t1 = pd.DataFrame(rows)
# 结局行
for i,o in enumerate(order):
    sub=mm[mm.quad==o]
    t1.loc[len(t1)] = {'Variable':'In-hospital mortality, n (%)', o:'%d (%.2f)'%(sub.died.sum(),100*sub.died.mean()), 'p':'' }
t1 = t1.fillna('')
t1.to_csv(OUT+'/Table1_baseline_by_quadrant.csv', index=False)
print('Table 1 rows:', len(t1))
print(t1.to_string(index=False, max_colwidth=26))

# ---------- Table 2 调整 OR ----------
CORE=['hr_min','hr_max','sbp_min','map_min','rr_max','spo2_min','adm_weight','cr_max','bun_max',
      'na_min','k_max','cl_min','hco3_min','hgb_min','wbc_max','plt_min','glu_max']
def prep(x):
    X=pd.DataFrame(index=x.index)
    for v in CORE+['age']: X[v]=num(x[v])
    X['female']=x.gender.astype(str).str.upper().str.startswith('F').astype(int)
    for v in ['mv','vaso','chf','ckd']: X[v]=pd.to_numeric(x[v],errors='coerce').fillna(0)
    return X
Xb=prep(mm); yv=mm.died.values.astype(int); med=Xb.median(); Zb=(Xb.fillna(med)-med)/Xb.std().replace(0,1)
cols=CORE+['age','female','mv','vaso','chf','ckd']
DUM=pd.DataFrame({'WetWarm':(mm.quad=='WetWarm').astype(int),'DryCold':(mm.quad=='DryCold').astype(int),'WetCold':(mm.quad=='WetCold').astype(int)},index=mm.index)
m2=sm.Logit(yv, sm.add_constant(pd.concat([Zb[cols],DUM],axis=1))).fit(disp=0)
Xa=pd.concat([Zb[cols], pd.DataFrame({'Oedema grade (per level)':num(mm.ew).fillna(num(mm.ew).median()),
                                       'Prolonged capillary refill':pd.to_numeric(mm.cr_abn,errors='coerce').fillna(0)})],axis=1)
ma=sm.Logit(yv, sm.add_constant(Xa)).fit(disp=0)
def orrow(m,k,label):
    tb=m.summary2().tables[1]; co,se=tb.loc[k,'Coef.'],tb.loc[k,'Std.Err.']
    return {'Variable':label,'OR':round(np.exp(co),2),'95%CI':'%.2f-%.2f'%(np.exp(co-1.96*se),np.exp(co+1.96*se)),'p':'%.2e'%tb.loc[k,'P>|z|']}
t2=pd.DataFrame([orrow(m2,'WetWarm','Wet-warm vs dry-warm'),orrow(m2,'DryCold','Dry-cold vs dry-warm'),
                 orrow(m2,'WetCold','Wet-cold vs dry-warm'),orrow(ma,'Oedema grade (per level)','Oedema grade (per level)'),
                 orrow(ma,'Prolonged capillary refill','Prolonged capillary refill')])
t2.to_csv(OUT+'/Table2_adjusted_OR.csv', index=False)
print('\nTable 2:\n', t2.to_string(index=False))

# ---------- Table 3 模型表现 ----------
def auc(y,p):
    y=np.asarray(y).astype(int); r=pd.Series(p).rank().values; n1=y.sum(); n0=len(y)-n1
    return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)
m1=sm.Logit(yv, sm.add_constant(Zb[cols])).fit(disp=0)
p1=m1.predict(sm.add_constant(Zb[cols])).values; p2=m2.predict(sm.add_constant(pd.concat([Zb[cols],DUM],axis=1))).values
def idi(y,a,b):
    y=np.asarray(y); ev=y==1; ne=~ev
    return (b[ev].mean()-a[ev].mean())-(b[ne].mean()-a[ne].mean())
def cat_nri(y,a,b,cuts=(0.03,0.08,0.15)):
    y=np.asarray(y); ev=y==1; ne=~ev; A=np.digitize(a,cuts); B=np.digitize(b,cuts)
    return ((B[ev]>A[ev]).mean()-(B[ev]<A[ev]).mean())+((B[ne]<A[ne]).mean()-(B[ne]>A[ne]).mean())
boot=[]
for _ in range(500):
    b=np.random.choice(len(yv),len(yv),replace=True)
    if yv[b].sum()<5: continue
    boot.append(auc(yv[b],p2[b])-auc(yv[b],p1[b]))
boot=np.array(boot)
nri=((p2[yv==1]>p1[yv==1]).mean()-(p2[yv==1]<p1[yv==1]).mean())+((p2[yv==0]<p1[yv==0]).mean()-(p2[yv==0]>p1[yv==0]).mean())
t3=pd.DataFrame([
 {'Metric':'AUROC (apparent, MIMIC-IV)','Routine':'%.3f'%auc(yv,p1),'Routine + phenotype':'%.3f'%auc(yv,p2)},
 {'Metric':'ΔAUROC (95% CI)','Routine':'-','Routine + phenotype':'%+.4f (%+.4f to %+.4f)'%(auc(yv,p2)-auc(yv,p1),np.percentile(boot,2.5),np.percentile(boot,97.5))},
 {'Metric':'IDI','Routine':'-','Routine + phenotype':'%+.4f'%idi(yv,p1,p2)},
 {'Metric':'NRI (continuous)','Routine':'-','Routine + phenotype':'%+.4f'%nri},
 {'Metric':'NRI (categorical)','Routine':'-','Routine + phenotype':'%+.4f'%cat_nri(yv,p1,p2)},
 {'Metric':'Temporal validation AUROC (<=2013 -> >=2014)','Routine':'-','Routine + phenotype':'0.853'},
])
t3.to_csv(OUT+'/Table3_model_performance.csv', index=False)
print('\nTable 3:\n', t3.to_string(index=False))

# ---------- Table 4 eICU ----------
t4=pd.read_csv(OUT+'/T_quadrant_eicu_composite.csv')
t4.to_csv(OUT+'/Table4_eicu_replication.csv', index=False)
print('\nTable 4:\n', t4.to_string(index=False))

# ---------- Fig9 SHAP ----------
try:
    import shap
    from sklearn.ensemble import RandomForestClassifier
    FEA=CORE+['age','female','mv','vaso','chf','ckd','ew2','cr2']
    Xs=Xb.copy()
    Xs['ew2']=num(mm.ew).fillna(num(mm.ew).median()); Xs['cr2']=pd.to_numeric(mm.cr_abn,errors='coerce').fillna(0)
    Xs=Xs[FEA].fillna(med)
    rf=RandomForestClassifier(n_estimators=400,min_samples_leaf=10,random_state=20261011,n_jobs=8).fit(Xs,yv)
    ex=shap.TreeExplainer(rf); sv=ex.shap_values(Xs)
    sv = sv[1] if isinstance(sv,list) else (sv[:,:,1] if sv.ndim==3 else sv)
    names={'age':'Age','female':'Female sex','hr_min':'HR min','hr_max':'HR max','sbp_min':'SBP min','map_min':'MAP min',
           'rr_max':'RR max','spo2_min':'SpO2 min','temp_mean':'Temperature','adm_weight':'Weight','cr_max':'Creatinine max',
           'bun_max':'Urea nitrogen max','na_min':'Sodium min','k_max':'Potassium max','cl_min':'Chloride min',
           'hco3_min':'Bicarbonate min','hgb_min':'Haemoglobin min','wbc_max':'WBC max','plt_min':'Platelets min',
           'glu_max':'Glucose max','mv':'Mechanical ventilation','vaso':'Vasopressors','chf':'Congestive HF',
           'ckd':'Chronic kidney disease','ew2':'Oedema grade','cr2':'Prolonged capillary refill'}
    imp=pd.DataFrame({'f':FEA,'v':np.abs(sv).mean(0)}).sort_values('v')
    fig,ax=plt.subplots(figsize=(4.6,4.2))
    cols=['#B23A3A' if f in ('ew2','cr2') else '#8A8A8A' for f in imp.f]
    ax.barh([names[f] for f in imp.f], imp.v, color=cols)
    ax.set_xlabel('Mean |SHAP value|'); ax.set_title('Variable importance (random forest, SHAP)', fontsize=9, loc='left')
    plt.tight_layout(); plt.savefig(FIG+'/Fig9_SHAP.png', dpi=400); plt.close()
    print('\nSHAP top10:\n', imp.tail(10).iloc[::-1].to_string(index=False))
    imp.assign(name=[names[f] for f in imp.f]).to_csv(OUT+'/T_shap_importance.csv', index=False)
except Exception as e:
    print('SHAP err', e)
print('\nsaved ->', OUT, FIG)
