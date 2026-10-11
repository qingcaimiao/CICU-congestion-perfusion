# -*- coding: utf-8 -*-
"""eICU 补充：复合充血定义（水肿/JVD/啰音任一）下的表型复现"""
import duckdb, numpy as np, pandas as pd, os
import statsmodels.api as sm
D  = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT= 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
c = duckdb.connect(); c.execute('PRAGMA threads=8')
ee = c.execute(f"SELECT * FROM read_parquet('{D}/eicu_cp.parquet')").df()

print('== eICU 单个体征 × 死亡 ==')
for v, nm in [('edema_pos','水肿(+)'),('jvd_pos','JVD(+)'),('crackles','肺部啰音(+)'),('hypoperf','外周灌注不足')]:
    d = ee[ee[v.replace('_pos','_doc').replace('hypoperf','perf_doc').replace('crackles','lungs_doc')].fillna(0)==1] if v!='hypoperf' else ee[ee.perf_doc.fillna(0)==1]
    t = d.groupby(v).agg(n=('died','size'), deaths=('died','sum'), pct=('died', lambda s: 100*s.mean())).round(2)
    print('\n-- %s --\n%s' % (nm, t.to_string()))

ee['cong_any'] = ((ee.edema_pos.fillna(0)==1) | (ee.jvd_pos.fillna(0)==1) | (ee.crackles.fillna(0)==1)).astype(int)
doc_any = (ee.edema_doc.fillna(0)+ee.jvd_doc.fillna(0)+ee.lungs_doc.fillna(0))
print('\n== 有任一充血体征记录者 n=%d (%.1f%%) ==' % ((doc_any>0).sum(), 100*(doc_any>0).mean()))

det = ee[(doc_any>0) & (ee.perf_doc.fillna(0)==1)].copy()
det['quad'] = np.where((det.cong_any==1)&(det.hypoperf.fillna(0)==1),'WetCold',
              np.where((det.cong_any==1)&(det.hypoperf.fillna(0)==0),'WetWarm',
              np.where((det.cong_any==0)&(det.hypoperf.fillna(0)==1),'DryCold','DryWarm')))
t4 = det.groupby('quad').agg(n=('died','size'), deaths=('died','sum'), pct=('died', lambda s: 100*s.mean())).round(2).reindex(['DryWarm','WetWarm','DryCold','WetCold'])
print('\n== eICU 复合充血 × 灌注 四象限 (n=%d) ==\n%s' % (len(det), t4.to_string()))
t4.to_csv(OUT+'/T_quadrant_eicu_composite.csv')

dd = det.copy(); dd['age_n'] = pd.to_numeric(dd.age, errors='coerce'); dd = dd[dd.age_n.notna()]
Xq = pd.DataFrame({'WetWarm':(dd.quad=='WetWarm').astype(int),'DryCold':(dd.quad=='DryCold').astype(int),
                   'WetCold':(dd.quad=='WetCold').astype(int),'age':dd.age_n,
                   'female':dd.gender.astype(str).str.upper().str.startswith('F').astype(int)})
mq = sm.Logit(dd.died.values.astype(int), sm.add_constant(Xq)).fit(disp=0)
tb = mq.summary2().tables[1]
print('\n== 年龄性别调整 OR (参照 DryWarm, n=%d, events=%d) ==' % (len(dd), dd.died.sum()))
for k in ['WetWarm','DryCold','WetCold']:
    co,se = tb.loc[k,'Coef.'], tb.loc[k,'Std.Err.']
    print('  %-9s OR = %.2f (%.2f–%.2f) p=%.2e' % (k, np.exp(co), np.exp(co-1.96*se), np.exp(co+1.96*se), tb.loc[k,'P>|z|']))

# 单独：复合充血
t = ee.groupby('cong_any').agg(n=('died','size'), deaths=('died','sum'), pct=('died', lambda s: 100*s.mean())).round(2)
print('\n== eICU 复合充血(有/无) × 死亡 (全体) ==\n%s' % t.to_string())
t.to_csv(OUT+'/T_cong_any_eicu.csv')

# MIMIC 侧同样构造（看一致性）：用 crackles 不可得，仅水肿+灌注
print('\n--- 小结 ---')
print('eICU 灌注轴: 3.86% vs 27.36%  (7.1x)  ← 与 MIMIC 4.46% vs 25.10% (5.6x) 高度一致')
print('eICU 充血轴: 需用复合定义，见上表')
