# -*- coding: utf-8 -*-
"""eICU 外部复现：表型梯度 + 可迁移模型的跨库验证"""
import duckdb, numpy as np, pandas as pd, json, os
import statsmodels.api as sm
from scipy import stats
np.random.seed(20261011)
D  = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT= 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
os.makedirs(OUT, exist_ok=True)
c = duckdb.connect(); c.execute('PRAGMA threads=8')

mm = c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()
ee = c.execute(f"SELECT * FROM read_parquet('{D}/eicu_cp.parquet')").df()
print('MIMIC 分析集 n=%d (死亡 %d)' % (len(mm), mm.died.sum()))
print('eICU  n=%d (死亡 %d, %.2f%%)' % (len(ee), ee.died.sum(), 100*ee.died.mean()))

print('\n== eICU 查体可得率 ==')
for v in ['edema_doc','edema_pos','edema_sev','jvd_doc','jvd_pos','perf_doc','hypoperf','lungs_doc','crackles']:
    print('  %-10s %5d (%.1f%%)' % (v, ee[v].fillna(0).sum(), 100*ee[v].fillna(0).mean()))

def tab(name, g, out):
    t = ee.groupby(g).agg(n=('died','size'), deaths=('died','sum'), pct=('died', lambda s: 100*s.mean())).round(2)
    print('\n== %s ==\n%s' % (name, t.to_string()))
    t.to_csv(OUT+'/'+out)
    return t

ee['edema_any'] = ee.edema_pos.fillna(0).astype(int)
ee['edema_sev'] = ee.edema_sev.fillna(0).astype(int)
sub = ee[ee.edema_doc.fillna(0)==1]
tab('eICU 水肿(有/无) × 死亡', 'edema_any', 'T_edema_eicu.csv')
tab('eICU 水肿严重度(3+/4+/anasarca) × 死亡', 'edema_sev', 'T_edema_sev_eicu.csv')
subp = ee[ee.perf_doc.fillna(0)==1]
t = subp.groupby('hypoperf').agg(n=('died','size'), deaths=('died','sum'), pct=('died', lambda s: 100*s.mean())).round(2)
print('\n== eICU 外周灌注 × 死亡 (n=%d) ==\n%s' % (len(subp), t.to_string())); t.to_csv(OUT+'/T_perf_eicu.csv')
subj = ee[ee.jvd_doc.fillna(0)==1]
t = subj.groupby('jvd_pos').agg(n=('died','size'), deaths=('died','sum'), pct=('died', lambda s: 100*s.mean())).round(2)
print('\n== eICU JVD × 死亡 ==\n%s' % t.to_string()); t.to_csv(OUT+'/T_jvd_eicu.csv')

# 四象限复现（充血=水肿3+/JVD阳性；灌注=外周灌注不足）
ee['cong'] = ((ee.edema_sev==1) | (ee.jvd_pos.fillna(0)==1)).astype(int)
ee['hypo'] = ee.hypoperf.fillna(0).astype(int)
det = ee[((ee.edema_doc.fillna(0)+ee.jvd_doc.fillna(0))>0) & (ee.perf_doc.fillna(0)==1)].copy()
det['quad'] = np.where((det.cong==1)&(det.hypo==1),'WetCold', np.where((det.cong==1)&(det.hypo==0),'WetWarm',
               np.where((det.cong==0)&(det.hypo==1),'DryCold','DryWarm')))
t4 = det.groupby('quad').agg(n=('died','size'), deaths=('died','sum'), pct=('died', lambda s: 100*s.mean())).round(2)
print('\n== eICU 四象限复现 (n=%d) ==\n%s' % (len(det), t4.to_string()))
t4.to_csv(OUT+'/T_quadrant_eicu.csv')

# 年龄性别调整 OR
try:
    dd = det.copy()
    dd['age_n'] = pd.to_numeric(dd.age, errors='coerce')
    dd = dd[dd.age_n.notna()]
    Xq = pd.DataFrame({'WetWarm':(dd.quad=='WetWarm').astype(int),'DryCold':(dd.quad=='DryCold').astype(int),
                       'WetCold':(dd.quad=='WetCold').astype(int),'age':dd.age_n,'female':(dd.gender.astype(str).str.upper().str.startswith('F')).astype(int)})
    mq = sm.Logit(dd.died.values.astype(int), sm.add_constant(Xq)).fit(disp=0)
    tb = mq.summary2().tables[1]
    print('\n== eICU 四象限 年龄性别调整 OR (参照 DryWarm, n=%d) ==' % len(dd))
    for k in ['WetWarm','DryCold','WetCold']:
        co,se = tb.loc[k,'Coef.'], tb.loc[k,'Std.Err.']
        print('  %-9s OR = %.2f (%.2f–%.2f) p=%.3f' % (k, np.exp(co), np.exp(co-1.96*se), np.exp(co+1.96*se), tb.loc[k,'P>|z|']))
except Exception as e:
    print('  OR err', e)

# ---------- 可迁移模型：MIMIC 重训 → eICU 套用 ----------
TRANS = ['age','hr_min','hr_max','sbp_min','map_min','rr_max','spo2_min','temp_mean','adm_weight',
         'cr_max','bun_max','na_min','k_max','cl_min','hco3_min','hgb_min','wbc_max','plt_min','glu_max']
def num(s): return pd.to_numeric(pd.Series(s).astype(str).str.replace('>','',regex=False).str.strip(), errors='coerce')
def build(d):
    X = pd.DataFrame(index=d.index)
    for v in TRANS: X[v] = num(d[v]) if v in d.columns else np.nan
    X['female'] = pd.Series(d.gender).astype(str).str.upper().str.startswith('F').astype(int).values
    X['WetWarm'] = (d.quad=='WetWarm').astype(int).values
    X['DryCold'] = (d.quad=='DryCold').astype(int).values
    X['WetCold'] = (d.quad=='WetCold').astype(int).values
    return X
Xm = build(mm); ym = mm.died.values.astype(int)
med = Xm.median(); sd = Xm.std().replace(0,1)
Zm = (Xm.fillna(med)-med)/sd
mtr = sm.Logit(ym, sm.add_constant(Zm)).fit(disp=0)
p_in = mtr.predict(sm.add_constant(Zm)).values

det2 = det.copy(); det2['quad'] = det2['quad']
Xe = build(det2); Xe['age'] = num(det2.age)
Ze = (Xe.fillna(med)-med)/sd
# 只保留外库变量齐全者
ok = Ze[TRANS].notna().mean(axis=1) >= 0.6
Ze, ye, de = Ze[ok], det2.died.values[ok].astype(int), det2[ok]
pe = mtr.predict(sm.add_constant(Ze)).values
# 重校准（截距+斜率）
from numpy.linalg import lstsq
z = np.log(np.clip(pe,1e-6,1-1e-6)/(1-np.clip(pe,1e-6,1-1e-6)))
A = np.column_stack([np.ones_like(z), z])
cs = lstsq(A, ye, rcond=None)[0]
pre = 1/(1+np.exp(-(cs[0]+cs[1]*z)))
def auc(y,p):
    y=np.asarray(y).astype(int); r=pd.Series(p).rank().values; n1=y.sum(); n0=len(y)-n1
    return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)
print('\n=== 跨库模型迁移 (变量集 %d 项 + 四象限) ===' % len(TRANS))
print('  MIMIC 表观 AUC = %.3f (n=%d)' % (auc(ym,p_in), len(ym)))
print('  eICU 外部 n=%d, events=%d' % (len(ye), ye.sum()))
if len(ye)>30 and ye.sum()>10:
    print('  eICU 外部 AUC(原系数) = %.3f ; O:E = %.2f' % (auc(ye,pe), ye.mean()/max(pe.mean(),1e-9)))
    print('  外库重校准后 AUC = %.3f ; 校准斜率 = %.2f ; 截距 = %.2f' % (auc(ye,pre), cs[1], cs[0]))
    pr = pd.DataFrame({'p':pe,'y':ye}); pr['b']=pd.qcut(pr.p,8,labels=False,duplicates='drop')
    print('  外部校准(8 分位):'); print(pr.groupby('b').agg(pred=('p','mean'),obs=('y','mean'),n=('y','size')).round(4).to_string())
    pr.groupby('b').agg(pred=('p','mean'),obs=('y','mean'),n=('y','size')).round(4).to_csv(OUT+'/T_calibration_eicu.csv')
    # 仅常规变量（无四象限）
    Zq = Ze[[v for v in Ze.columns if v not in ['WetWarm','DryCold','WetCold']]]
    Xmq = Zm[[v for v in Zm.columns if v not in ['WetWarm','DryCold','WetCold']]]
    m0 = sm.Logit(ym, sm.add_constant(Xmq)).fit(disp=0)
    pe0 = m0.predict(sm.add_constant(Zq)).values
    print('  eICU 外部 AUC(不含四象限) = %.3f  → ΔAUC = %+.4f' % (auc(ye,pe0), auc(ye,pe)-auc(ye,pe0)))
json.dump({'eicu_n':int(len(ee)),'eicu_died':int(ee.died.sum()),
           'edema_doc':int(ee.edema_doc.fillna(0).sum()),'perf_doc':int(ee.perf_doc.fillna(0).sum()),
           'quadrant':t4.reset_index().to_dict('records')}, open(OUT+'/cp_eicu_results.json','w'), ensure_ascii=False, indent=1)
print('\nsaved ->', OUT)
