# -*- coding: utf-8 -*-
"""按 critique 补做的方法学分析 + 检查 RCS 结点退化"""
import duckdb, numpy as np, pandas as pd, os, json, warnings
warnings.filterwarnings('ignore')
import statsmodels.api as sm
D  = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT= 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
c=duckdb.connect(); c.execute('PRAGMA threads=8')
mm=c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()
mm['female']=mm.gender.astype(str).str.upper().str.startswith('F').astype(int)
def num(s): return pd.to_numeric(pd.Series(s).astype(str).str.replace('>','',regex=False).str.strip(),errors='coerce')
R={}

# ---------- 0. RCS 结点检查 ----------
ew = num(mm.ew).dropna()
kn = np.percentile(ew,[10,50,90])
print('== 0. RCS 结点检查 ==')
print('   ew 分位: p10=%.0f p50=%.0f p90=%.0f  -> knots=%s' % (kn[0],kn[1],kn[2],kn.tolist()))
print('   结点是否重复/退化:', 'YES — RCS 不适用' if len(set(kn))<3 or (kn[2]-kn[1])==0 else 'no')
R['rcs_knots']=kn.tolist(); R['rcs_degenerate']=bool(len(set(kn))<3)

# ---------- 1. 公平比较：水肿二分化 + CRT 同一模型 ----------
CORE=['hr_min','hr_max','sbp_min','map_min','rr_max','spo2_min','temp_mean','adm_weight','cr_max','bun_max',
      'na_min','k_max','cl_min','hco3_min','hgb_min','wbc_max','plt_min','glu_max']
cols=CORE+['age','female','mv','vaso','chf','ckd']
Xb=pd.DataFrame(index=mm.index)
for v in CORE+['age']: Xb[v]=num(mm[v])
Xb['female']=mm.female; 
for v in ['mv','vaso','chf','ckd']: Xb[v]=pd.to_numeric(mm[v],errors='coerce').fillna(0)
med=Xb.median(); sd=Xb.std().replace(0,1); Zb=(Xb.fillna(med)-med)/sd
yv=mm.died.values.astype(int)
ewv=num(mm.ew); crv=pd.to_numeric(mm.cr_abn,errors='coerce')
print('\n== 1. 公平比较（水肿二分化 vs CRT，同一模型）==')
Xf=pd.concat([Zb[cols], pd.DataFrame({'edema_ge3':(ewv>=3).astype(float).fillna(0), 'CRT_prolonged':crv.fillna(0)})],axis=1)
mf=sm.Logit(yv, sm.add_constant(Xf)).fit(disp=0)
tb=mf.summary2().tables[1]
for k in ['edema_ge3','CRT_prolonged']:
    co,se=tb.loc[k,'Coef.'],tb.loc[k,'Std.Err.']
    print('   %-14s OR = %.2f (%.2f–%.2f)  p = %.2e' % (k, np.exp(co), np.exp(co-1.96*se), np.exp(co+1.96*se), tb.loc[k,'P>|z|']))
    R[k+'_OR']=[float(np.exp(co)), float(np.exp(co-1.96*se)), float(np.exp(co+1.96*se))]

# 按级 OR（水肿作为分类变量）——替代 RCS
print('\n== 1b. 水肿按等级的分类 OR（参照 grade 0）==')
Xd=pd.concat([Zb[cols]],axis=1).copy()
gd=ewv.copy()
for g in [1,2,3,4,5]:
    Xd['ed_%d'%g]=(gd==g).astype(float)
Xd['CRT']=crv.fillna(0)
md=sm.Logit(yv, sm.add_constant(Xd)).fit(disp=0)
tbd=md.summary2().tables[1]
grade_rows=[]
for g in [1,2,3,4,5]:
    k='ed_%d'%g
    co,se=tbd.loc[k,'Coef.'],tbd.loc[k,'Std.Err.']
    row={'grade':g,'OR':round(float(np.exp(co)),2),'CI':'%.2f-%.2f'%(np.exp(co-1.96*se),np.exp(co+1.96*se)),'p':'%.3f'%tbd.loc[k,'P>|z|'] if tbd.loc[k,'P>|z|']>=0.001 else '%.1e'%tbd.loc[k,'P>|z|']}
    grade_rows.append(row); print('   grade %d: OR = %s (%s) p=%s'%(g,row['OR'],row['CI'],row['p']))
pd.DataFrame(grade_rows).to_csv(OUT+'/T_edema_grade_adjusted_OR.csv',index=False)

# ---------- 2. PPV / NPV ----------
print('\n== 2. PPV / NPV（表型作为筛查工具）==')
prev=mm.died.mean()
rows=[]
for grp,mask,lab in [('WetCold', mm.quad=='WetCold','湿冷型'),
                     ('Cold(any)', mm.quad.isin(['DryCold','WetCold']),'任一冷型'),
                     ('Congested(any)', mm.quad.isin(['WetWarm','WetCold']),'任一湿型')]:
    sub=mm[mask]
    tp=sub.died.sum(); n=len(sub); fn=mm[~mask].died.sum()
    ppv=100*tp/n; npv=100*(1-mm[~mask].died.mean())
    sens=100*tp/mm.died.sum()
    print('   %-14s n=%5d (%.1f%%)  死亡率=%.2f%%  PPV=%.1f%%  NPV=%.1f%%  敏感度=%.1f%%'%(lab,n,100*n/len(mm),100*sub.died.mean(),ppv,npv,sens))
    rows.append({'Rule':lab,'n':int(n),'pct_of_cohort':round(100*n/len(mm),1),'mortality':round(100*sub.died.mean(),2),
                 'PPV':round(ppv,1),'NPV':round(npv,1),'sensitivity':round(sens,1)})
pd.DataFrame(rows).to_csv(OUT+'/T_ppv_npv.csv',index=False)
R['ppv_npv']=rows

# ---------- 3. 缺失率 + EPV ----------
print('\n== 3. 协变量缺失率与 EPV ==')
n_all=len(mm); miss=[]
for v in ['age','gender','adm_weight','hr_min','hr_max','sbp_min','map_min','rr_max','spo2_min','temp_mean',
          'cr_max','bun_max','na_min','k_max','cl_min','hco3_min','hgb_min','wbc_max','plt_min','glu_max','ew','cr_abn']:
    col = num(mm[v]) if v not in ('gender',) else mm[v]
    m=100*col.isna().mean()
    miss.append({'variable':v,'missing_pct':round(m,1)})
md_=pd.DataFrame(miss).sort_values('missing_pct',ascending=False)
print(md_.to_string(index=False))
md_.to_csv(OUT+'/T_missingness.csv',index=False)
events=int(yv.sum()); npar=int(Xf.shape[1])
print('   EPV = events / parameters = %d / %d = %.1f' % (events, npar, events/npar))
print('   (四象限模型参数 %d -> EPV %.1f)' % (len(cols)+3, events/(len(cols)+3)))
R['epv']=round(events/npar,1); R['events']=events
json.dump(R, open(OUT+'/cp_critique_checks.json','w'), ensure_ascii=False, indent=1)
print('\nsaved ->', OUT)
