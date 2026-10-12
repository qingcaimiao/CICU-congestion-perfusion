import duckdb, numpy as np, pandas as pd, statsmodels.api as sm
c=duckdb.connect(); c.execute('PRAGMA threads=8')
OUT='D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
def num(s): return pd.to_numeric(pd.Series(s).astype(str).str.replace('>','',regex=False).str.strip(), errors='coerce')
def auc(y,p):
    y=np.asarray(y).astype(int); r=pd.Series(p).rank().values; n1=y.sum(); n0=len(y)-n1
    return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)
df=c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()
d=df.dropna(subset=['quad']).copy()
CORE=['hr_min','hr_max','sbp_min','map_min','rr_max','spo2_min','adm_weight','cr_max','bun_max',
      'na_min','k_max','cl_min','hco3_min','hgb_min','wbc_max','plt_min','glu_max']
base_cols=CORE+['age','female','mv','vaso','chf','ckd']
def run(clip):
    X=pd.DataFrame(index=d.index)
    for v in CORE+['age']: X[v]=num(d[v])
    if clip: X['rr_max']=X['rr_max'].clip(upper=80)
    X['female']=d.gender.astype(str).str.upper().str.startswith('F').astype(int)
    for v in ['mv','vaso','chf','ckd']: X[v]=pd.to_numeric(d[v],errors='coerce').fillna(0)
    med=X.median(); Z=(X.fillna(med)-med)/X.std().replace(0,1)
    DUM=pd.DataFrame({'WetWarm':(d.quad=='WetWarm').astype(int),'DryCold':(d.quad=='DryCold').astype(int),
                      'WetCold':(d.quad=='WetCold').astype(int)}, index=d.index)
    y=d.died.values.astype(int)
    m1=sm.Logit(y, sm.add_constant(Z[base_cols])).fit(disp=0)
    X2=sm.add_constant(pd.concat([Z[base_cols],DUM],axis=1)); m2=sm.Logit(y,X2).fit(disp=0)
    a1,a2=auc(y,m1.predict(sm.add_constant(Z[base_cols])).values), auc(y,m2.predict(X2).values)
    ors={k: float(np.exp(m2.params[k])) for k in ['WetWarm','DryCold','WetCold']}
    return a1,a2,ors,m2
r=[]
for tag,clip in [('原样（rr_max 含极端值）',False),('rr_max 截断 ≤80',True)]:
    a1,a2,ors,m2=run(clip)
    r.append((tag,a1,a2,ors))
    print('%-22s 常规 AUC=%.4f | 常规+表型 AUC=%.4f | ΔAUC=%+.4f | OR 湿暖=%.3f 干冷=%.3f 湿冷=%.3f'
          % (tag,a1,a2,a2-a1,ors['WetWarm'],ors['DryCold'],ors['WetCold']))
print()
print('截断前后的绝对差：AUC1 %.5f  AUC2 %.5f' % (abs(r[0][1]-r[1][1]), abs(r[0][2]-r[1][2])))
print('对稿件三位小数的影响：%s' % ('无（数字不变）' if abs(r[0][1]-r[1][1])<0.0005 and abs(r[0][2]-r[1][2])<0.0005 else '有'))
