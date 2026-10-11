# -*- coding: utf-8 -*-
"""水肿"充血消退"轨迹：早(0-24h) vs 晚(24-72h)，4 类；结局与增量"""
import duckdb, numpy as np, pandas as pd, json, os
import statsmodels.api as sm
from scipy import stats
D  = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT= 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
c = duckdb.connect(); c.execute('PRAGMA threads=8')

g = c.execute(f"""
 SELECT stay_id,
  max(CASE WHEN off_h>=0  AND off_h<24 THEN g END) g_early,
  max(CASE WHEN off_h>=24 AND off_h<72 THEN g END) g_late,
  min(CASE WHEN off_h>=0  AND off_h<24 THEN g END) g_early_min,
  count(CASE WHEN off_h>=24 AND off_h<72 THEN 1 END) n_late
 FROM (SELECT stay_id, off_h,
        CASE trim(lower(value)) WHEN 'none' THEN 0 WHEN '2 mm' THEN 1 WHEN '4 mm' THEN 2
             WHEN '6 mm' THEN 3 WHEN '8 mm' THEN 4 WHEN 'anasarca' THEN 5 END AS g
       FROM read_parquet('{D}/cp_exam_raw.parquet')
       WHERE itemid=224862 AND off_h>=0 AND off_h<72 AND value IS NOT NULL)
 GROUP BY stay_id""").df()
print('有 0-72h 记录者:', len(g))
g = g.dropna(subset=['g_early','g_late'])
print('早晚两窗均有记录:', len(g))

def cls(r):
    e, l = r.g_early, r.g_late
    if e>=3 and l>=3: return 'Persistent'
    if e>=3 and l<3:  return 'Resolved'
    if e<3  and l>=3: return 'Emerging'
    return 'Never'
g['traj'] = g.apply(cls, axis=1)
mm = c.execute(f"SELECT stay_id, died, ew, cr_abn, age, gender, los FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()
t = g.merge(mm, on='stay_id', how='inner')
tab = t.groupby('traj').agg(n=('died','size'), deaths=('died','sum'), pct=('died', lambda s: 100*s.mean()),
                            mean_early=('g_early','mean'), mean_late=('g_late','mean')).round(2)
tab = tab.reindex(['Never','Resolved','Emerging','Persistent'])
print('\n== 充血轨迹 × 院内死亡 (n=%d) ==\n%s' % (len(t), tab.to_string()))
tab.to_csv(OUT+'/T_trajectory_outcome.csv')
chi2,p,_,_ = stats.chi2_contingency(pd.crosstab(t.traj, t.died))
print('  χ² p = %.3e' % p)

d = t.dropna(subset=['age']).copy(); d['age_n']=pd.to_numeric(d.age,errors='coerce'); d=d[d.age_n.notna()]
X = pd.DataFrame({'age':d.age_n,'female':d.gender.astype(str).str.upper().str.startswith('F').astype(int)})
for k2 in ['Resolved','Emerging','Persistent']:
    X['traj_'+k2] = (d.traj==k2).astype(int)
m = sm.Logit(d.died.values.astype(int), sm.add_constant(X)).fit(disp=0)
tb = m.summary2().tables[1]
print('\n== 调整后 OR (参照 Never) n=%d events=%d ==' % (len(d), d.died.sum()))
for k2 in ['Resolved','Emerging','Persistent']:
    kk='traj_'+k2
    co,se=tb.loc[kk,'Coef.'],tb.loc[kk,'Std.Err.']
    print('  %-11s OR = %.2f (%.2f–%.2f) p=%.2e' % (k2, np.exp(co), np.exp(co-1.96*se), np.exp(co+1.96*se), tb.loc[kk,'P>|z|']))

# 轨迹是否在"入院水肿等级"之上提供增量
def auc(y,p):
    y=np.asarray(y).astype(int); r=pd.Series(p).rank().values; n1=y.sum(); n0=len(y)-n1
    return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)
y=d.died.values.astype(int)
base = pd.DataFrame({'age':d.age_n,'female':d.gender.astype(str).str.upper().str.startswith('F').astype(int),
                     'ew':pd.to_numeric(d.ew,errors='coerce')}).fillna(0)
m1 = sm.Logit(y, sm.add_constant(base)).fit(disp=0)
X2 = pd.concat([base, X[['traj_Resolved','traj_Emerging','traj_Persistent']]], axis=1)
m2 = sm.Logit(y, sm.add_constant(X2)).fit(disp=0)
p1 = m1.predict(sm.add_constant(base)).values; p2 = m2.predict(sm.add_constant(X2)).values
print('\n增量(在年龄+性别+入院水肿等级之上加入轨迹):')
print('  AUC %.4f → %.4f  (Δ %+.4f)' % (auc(y,p1), auc(y,p2), auc(y,p2)-auc(y,p1)))
def idi(y,a,b):
    y=np.asarray(y); ev=y==1; ne=~ev
    return (b[ev].mean()-a[ev].mean())-(b[ne].mean()-a[ne].mean())
print('  IDI = %+.4f' % idi(y,p1,p2))

# 与"只取最差水肿等级"相比的判别力
print('\n单变量 AUC: 入院水肿等级=%.3f | 轨迹分类=%.3f | 最差水肿等级=%.3f' % (
    auc(y, pd.to_numeric(d.ew,errors='coerce').fillna(0)), auc(y, d.traj.map({'Never':0,'Resolved':1,'Emerging':2,'Persistent':3}).values), auc(y, pd.to_numeric(d.ew,errors='coerce').fillna(0))))

json.dump({'n':int(len(t)),'table':tab.reset_index().to_dict('records'),
           'auc_add':[float(auc(y,p1)), float(auc(y,p2))]}, open(OUT+'/cp_trajectory.json','w'), ensure_ascii=False, indent=1)
t.to_csv(OUT+'/T_trajectory_rows.csv', index=False)
print('\nsaved ->', OUT)
