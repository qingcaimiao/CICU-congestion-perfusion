# -*- coding: utf-8 -*-
"""充血-灌注：完整分析 v2（可解释 OR + bootstrap + RCS + 校准 + DCA + 时间验证）"""
import duckdb, numpy as np, pandas as pd, json, os
import statsmodels.api as sm
from scipy import stats
np.random.seed(20261011)
D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
os.makedirs(OUT, exist_ok=True)
c = duckdb.connect(); c.execute('PRAGMA threads=8')

# ---------- 暴露 ----------
q = f"""
WITH e AS (
  SELECT stay_id,
    max(CASE trim(lower(value)) WHEN 'none' THEN 0 WHEN '2 mm' THEN 1 WHEN '4 mm' THEN 2
         WHEN '6 mm' THEN 3 WHEN '8 mm' THEN 4 WHEN 'anasarca' THEN 5 END) ed_win
  FROM read_parquet('{D}/cp_exam_raw.parquet') WHERE itemid=224862 AND off_h>=-6 AND off_h<=24 GROUP BY 1),
e2 AS (SELECT stay_id,
    max(CASE trim(lower(value)) WHEN 'none' THEN 0 WHEN '2 mm' THEN 1 WHEN '4 mm' THEN 2
         WHEN '6 mm' THEN 3 WHEN '8 mm' THEN 4 WHEN 'anasarca' THEN 5 END) ed_any,
    arg_min(CASE trim(lower(value)) WHEN 'none' THEN 0 WHEN '2 mm' THEN 1 WHEN '4 mm' THEN 2
         WHEN '6 mm' THEN 3 WHEN '8 mm' THEN 4 WHEN 'anasarca' THEN 5 END, off_h) ed_first
  FROM read_parquet('{D}/cp_exam_raw.parquet') WHERE itemid=224862 GROUP BY 1),
cr AS (SELECT stay_id, max(CASE WHEN trim(lower(value)) LIKE 'abnormal%' THEN 1 ELSE 0 END) cr_abn
  FROM read_parquet('{D}/cp_exam_raw.parquet') WHERE itemid IN (223951,224308) AND off_h>=-6 AND off_h<=24 GROUP BY 1)
SELECT m.*, e.ed_win, e2.ed_any, e2.ed_first, cr.cr_abn
FROM read_parquet('{D}/mimic_cp.parquet') m
LEFT JOIN e USING(stay_id) LEFT JOIN e2 USING(stay_id) LEFT JOIN cr USING(stay_id)"""
df = c.execute(q).df()
df['stay_id'] = df.stay_id.astype('int64')
ew = pd.to_numeric(df.ed_win, errors='coerce'); crv = pd.to_numeric(df.cr_abn, errors='coerce')
quad = pd.Series(np.nan, index=df.index, dtype=object); m0 = ew.notna() & crv.notna()
quad[m0 & (ew>=3) & (crv==1)] = 'WetCold'; quad[m0 & (ew>=3) & (crv==0)] = 'WetWarm'
quad[m0 & (ew<=2) & (crv==1)] = 'DryCold'; quad[m0 & (ew<=2) & (crv==0)] = 'DryWarm'
df['quad'] = quad; df['ew'] = ew; df['cr_abn'] = crv

print('n=%d  deaths=%d (%.2f%%)' % (len(df), df.died.sum(), 100*df.died.mean()))
for v in ['ew','cr_abn']:
    print('  覆盖 %-7s %d (%.1f%%)' % (v, df[v].notna().sum(), 100*df[v].notna().mean()))

d = df.dropna(subset=['quad']).copy()
print('\n样本(四象限可判定) n=%d, 死亡 %d (%.2f%%)' % (len(d), d.died.sum(), 100*d.died.mean()))

# ---------- 表 ----------
quad_tab = d.groupby('quad').agg(n=('died','size'), deaths=('died','sum'), pct=('died', lambda s: 100*s.mean())).round(2)
quad_tab = quad_tab.reindex(['DryWarm','WetWarm','DryCold','WetCold'])
print('\n== 四象限 × 院内死亡 ==\n', quad_tab.to_string())
quad_tab.to_csv(OUT+'/T_quadrant_mimic.csv')
ed_tab = df.dropna(subset=['ew']).groupby('ew').agg(n=('died','size'), deaths=('died','sum'), pct=('died', lambda s: 100*s.mean())).round(2)
print('\n== 水肿等级 × 死亡 ==\n', ed_tab.to_string()); ed_tab.to_csv(OUT+'/T_edema_mimic.csv')
cr_tab = df.dropna(subset=['cr_abn']).groupby('cr_abn').agg(n=('died','size'), deaths=('died','sum'), pct=('died', lambda s: 100*s.mean())).round(2)
print('\n== 毛细血管再充盈 × 死亡 ==\n', cr_tab.to_string()); cr_tab.to_csv(OUT+'/T_cr_mimic.csv')
chi2, pchi, _, _ = stats.chi2_contingency(pd.crosstab(df.dropna(subset=['ew']).ew, df.dropna(subset=['ew']).died))
print('\n水肿等级 趋势 χ² p = %.2e' % pchi)
chi2b, pcr, _, _ = stats.chi2_contingency(pd.crosstab(df.dropna(subset=['cr_abn']).cr_abn, df.dropna(subset=['cr_abn']).died))
print('毛细血管再充盈 p = %.2e' % pcr)

# ---------- 模型 ----------
CORE = ['hr_min','hr_max','sbp_min','map_min','rr_max','spo2_min','adm_weight',
        'cr_max','bun_max','na_min','k_max','cl_min','hco3_min','hgb_min','wbc_max','plt_min','glu_max']
def prep(x):
    X = pd.DataFrame(index=x.index)
    for v in CORE+['age']:
        X[v] = pd.to_numeric(x[v].astype(str).str.replace('>','',regex=False).str.strip(), errors='coerce')
    X['female'] = x.gender.astype(str).str.upper().str.startswith('F').astype(int)
    for v in ['mv','vaso','chf','ckd']:
        X[v] = pd.to_numeric(x[v], errors='coerce').fillna(0)
    return X
def auc(y,p):
    y=np.asarray(y).astype(int); r=pd.Series(p).rank().values; n1=y.sum(); n0=len(y)-n1
    return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)

Xb = prep(d); yv = d.died.values.astype(int)
med = Xb.median(); Zb = (Xb.fillna(med)-med)/Xb.std().replace(0,1)
DUM = pd.DataFrame({'WetWarm':(d.quad=='WetWarm').astype(int), 'DryCold':(d.quad=='DryCold').astype(int),
                    'WetCold':(d.quad=='WetCold').astype(int)}, index=d.index)
Zfull = pd.concat([Zb, DUM], axis=1)
base_cols = CORE+['age','female','mv','vaso','chf','ckd']

m1 = sm.Logit(yv, sm.add_constant(Zb[base_cols])).fit(disp=0)
X2 = sm.add_constant(pd.concat([Zb[base_cols], DUM], axis=1))
m2 = sm.Logit(yv, X2).fit(disp=0)
p1 = m1.predict(sm.add_constant(Zb[base_cols])).values; p2 = m2.predict(X2).values
a1, a2 = auc(yv,p1), auc(yv,p2)
print('\n=== 判别力 ===')
print('  模型1 常规变量          AUC = %.3f' % a1)
print('  模型2 常规 + 四象限     AUC = %.3f   ΔAUC = %+.4f' % (a2, a2-a1))
# DeLong (近似: bootstrap)
boot = []
idx = np.arange(len(yv))
for _ in range(500):
    b = np.random.choice(idx, len(idx), replace=True)
    if yv[b].sum()<5: continue
    boot.append(auc(yv[b], p2[b]) - auc(yv[b], p1[b]))
boot = np.array(boot)
print('  ΔAUC 95%%CI (bootstrap) = %+.4f (%+.4f, %+.4f)' % (a2-a1, np.percentile(boot,2.5), np.percentile(boot,97.5)))

def idi(y,p_old,p_new):
    y=np.asarray(y); ev=y==1; ne=~ev
    return (p_new[ev].mean()-p_old[ev].mean()) - (p_new[ne].mean()-p_old[ne].mean())
idi_v = idi(yv,p1,p2)
nri = ((p2[yv==1]>p1[yv==1]).mean()-(p2[yv==1]<p1[yv==1]).mean()) + ((p2[yv==0]<p1[yv==0]).mean()-(p2[yv==0]>p1[yv==0]).mean())
print('  IDI = %+.4f | NRI(continuous) = %+.4f' % (idi_v, nri))
# 分类NRI
def cat_nri(y,p_old,p_new,cuts=(0.03,0.08,0.15)):
    y=np.asarray(y); ev=y==1; ne=~ev
    a=np.digitize(p_old,cuts); b=np.digitize(p_new,cuts)
    return ( (b[ev]>a[ev]).mean() - (b[ev]<a[ev]).mean() ) + ( (b[ne]<a[ne]).mean() - (b[ne]>a[ne]).mean() )
print('  NRI(3 风险层 <3%%/3-8%%/8-15%%/>15%%) = %+.4f' % cat_nri(yv,p1,p2))

print('\n=== 四象限 调整后 OR (参照 DryWarm) ===')
tb = m2.summary2().tables[1]
for k in ['WetWarm','DryCold','WetCold']:
    coef, se = tb.loc[k,'Coef.'], tb.loc[k,'Std.Err.']
    print('  %-9s OR = %.2f (%.2f–%.2f)  p = %.2e' % (k, np.exp(coef), np.exp(coef-1.96*se), np.exp(coef+1.96*se), tb.loc[k,'P>|z|']))

print('\n=== 水肿等级(每+1级) / 毛细血管再充盈 单独效应 ===')
Xa = pd.concat([Zb[base_cols], pd.DataFrame({'ed_grade': d.ew.fillna(d.ew.median()), 'cr': d.cr_abn.fillna(0)}),], axis=1)
ma = sm.Logit(yv, sm.add_constant(Xa)).fit(disp=0)
tb2 = ma.summary2().tables[1]
for k in ['ed_grade','cr']:
    coef, se = tb2.loc[k,'Coef.'], tb2.loc[k,'Std.Err.']
    print('  %-9s OR = %.2f (%.2f–%.2f)  p = %.2e' % (k, np.exp(coef), np.exp(coef-1.96*se), np.exp(coef+1.96*se), tb2.loc[k,'P>|z|']))

# ---------- RCS ----------
def rcs_basis(x, knots):
    k = np.asarray(knots, float); x = np.asarray(x, float)
    B = [x]
    for j in range(len(k)-2):
        t = k[j+2]
        term = ((x-t).clip(0)**3 - ((x-k[-1]).clip(0)**3)*(k[-1]-t)/(k[-1]-k[-2])
                + ((x-k[-2]).clip(0)**3)*(k[-2]-t)/(k[-1]-k[-2])) / (k[-1]-k[0])**2
        B.append(term)
    return np.column_stack(B)
sub = d.dropna(subset=['ew'])
kn = np.percentile(sub.ew, [10,50,90])
B = rcs_basis(sub.ew, kn)
# 只调整年龄性别(便于展示暴露-反应)
cov = pd.DataFrame({'age':pd.to_numeric(sub.age,errors='coerce'),'female':sub.gender.astype(str).str.upper().str.startswith('F').astype(int)}, index=sub.index).fillna(0)
Xr = np.column_stack([B, cov.values.astype(float)])
mr = sm.Logit(sub.died.values.astype(int), sm.add_constant(Xr)).fit(disp=0)
grid = np.linspace(0,5,26); Bg = rcs_basis(grid, kn)
Xg = np.column_stack([Bg, np.tile(cov.mean().values, (len(grid),1))])
pred = mr.predict(sm.add_constant(Xg, has_constant='add'))
print('\n== RCS 水肿等级 → 预测死亡概率 ==')
print('  ' + '  '.join('%d级:%.1f%%' % (g, 100*pp) for g, pp in zip(grid[::5], pred[::5])))

# ---------- 校准 & DCA ----------
nbins=10; qs = pd.qcut(p2, nbins, labels=False, duplicates='drop')
cal = pd.DataFrame({'p':p2,'y':yv,'b':qs}).groupby('b').agg(pred=('p','mean'), obs=('y','mean'), n=('y','size')).round(4)
print('\n== 校准 (10 分位) ==\n', cal.to_string()); cal.to_csv(OUT+'/T_calibration.csv')
def net_benefit(y,p,pt):
    y=np.asarray(y); n=len(y)
    tp=((p>=pt)&(y==1)).sum()/n; fp=((p>=pt)&(y==0)).sum()/n
    return tp - fp*pt/(1-pt)
ths=np.arange(0.01,0.31,0.01)
dca=pd.DataFrame({'threshold':ths,'model':[net_benefit(yv,p2,t) for t in ths],
                  'treat_all':[net_benefit(yv,np.ones_like(p2),t) for t in ths]})
dca['treat_none']=0.0
print('\n== DCA 净获益 (抽样) ==\n', dca.iloc[::5].round(4).to_string(index=False))
dca.to_csv(OUT+'/T_dca.csv', index=False)

# ---------- 时间验证 ----------
# anchor_year_group 必须取自 hosp/patients.csv（零缺失）。旧实现从另一课题的
# T2_data/mimic_T2.parquet 做 stay_id 映射，与本队列只有 9,715/12,052 重叠，
# 会把 2,337 例误判为"无年代标注"，时间验证 AUROC 也因此被算成 0.851。
# 详见 _ayg.py 模块 docstring。
from _ayg import attach_ayg, split_era
d = attach_ayg(d, con=c)
tr, te = split_era(d)
if len(tr)>500 and len(te)>500:
    Xtr_b = prep(tr); Xte_b = prep(te)
    medt = Xtr_b.median(); Ztr = (Xtr_b.fillna(medt)-medt)/Xtr_b.std().replace(0,1)
    Zte = (Xte_b.fillna(medt)-medt)/Xtr_b.std().replace(0,1)
    Dtr = pd.DataFrame({'WetWarm':(tr.quad=='WetWarm').astype(int),'DryCold':(tr.quad=='DryCold').astype(int),'WetCold':(tr.quad=='WetCold').astype(int)})
    Dte = pd.DataFrame({'WetWarm':(te.quad=='WetWarm').astype(int),'DryCold':(te.quad=='DryCold').astype(int),'WetCold':(te.quad=='WetCold').astype(int)})
    mt = sm.Logit(tr.died.values.astype(int), sm.add_constant(pd.concat([Ztr[base_cols],Dtr],axis=1))).fit(disp=0)
    pt = mt.predict(sm.add_constant(pd.concat([Zte[base_cols],Dte],axis=1)))
    print('\n== 时间验证 (早段训练 n=%d → 晚段测试 n=%d) AUC = %.3f ==' % (len(tr), len(te), auc(te.died.values, pt)))
    print('   time groups present:', sorted([g for g in d.ayg.dropna().unique()]))

# ---------- 保存 ----------
c.register('dout', d)
c.execute(f"COPY dout TO '{OUT}/cp_analysis_set.parquet' (FORMAT PARQUET)")
json.dump({'n':int(len(d)),'deaths':int(yv.sum()),'auc_base':float(a1),'auc_quad':float(a2),
           'dAUC':float(a2-a1),'dAUC_ci':[float(np.percentile(boot,2.5)),float(np.percentile(boot,97.5))],
           'IDI':float(idi_v),'NRI':float(nri),
           'quadrant':quad_tab.reset_index().to_dict('records')},
          open(OUT+'/cp_core_results.json','w'), ensure_ascii=False, indent=1)
print('\nsaved ->', OUT)
