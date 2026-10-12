# -*- coding: utf-8 -*-
"""充血-灌注：投稿级图表（400 dpi, Arial, 英文）"""
import duckdb, numpy as np, pandas as pd, os, json, warnings
warnings.filterwarnings('ignore')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import statsmodels.api as sm
from sklearn.cluster import KMeans
plt.rcParams.update({'font.family':'Arial','font.size':9,'axes.linewidth':0.8,
                     'xtick.major.width':0.8,'ytick.major.width':0.8,'axes.spines.top':False,'axes.spines.right':False})
D  = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT= 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
FIG= 'D:/桌面/workbuddyzuopin/CPxiangmu/04_图'
os.makedirs(FIG, exist_ok=True)
c = duckdb.connect(); c.execute('PRAGMA threads=8')
mm = c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()
ee = c.execute(f"SELECT * FROM read_parquet('{D}/eicu_cp.parquet')").df().rename(columns={'admissionweight':'adm_weight'})   # 与 final_eicu_model.py 对齐列名，否则可得性筛查会少算一个变量
CRED, CBLU, CGRY = '#B23A3A', '#2F5D8A', '#8A8A8A'

# ---------- Fig 1 四象限梯度 ----------
def quad_tab(d, col='quad'):
    t = d.groupby(col).agg(n=('died','size'), pct=('died', lambda s: 100*s.mean()))
    return t.reindex(['DryWarm','WetWarm','DryCold','WetCold'])
t_m = quad_tab(mm)
doc = (ee.edema_doc.fillna(0)+ee.jvd_doc.fillna(0)+ee.lungs_doc.fillna(0))
e2 = ee[(doc>0)&(ee.perf_doc.fillna(0)==1)].copy()
e2['cong'] = ((e2.edema_pos.fillna(0)==1)|(e2.jvd_pos.fillna(0)==1)|(e2.crackles.fillna(0)==1)).astype(int)
e2['quad'] = np.where((e2.cong==1)&(e2.hypoperf.fillna(0)==1),'WetCold',
             np.where((e2.cong==1)&(e2.hypoperf.fillna(0)==0),'WetWarm',
             np.where((e2.cong==0)&(e2.hypoperf.fillna(0)==1),'DryCold','DryWarm')))
t_e = quad_tab(e2)
fig, ax = plt.subplots(figsize=(5.4,3.0))
x = np.arange(4); w=0.38
b1 = ax.bar(x-w/2, t_m.pct.values, w, color=CBLU, label='MIMIC-IV (n=%s)'%f"{len(mm):,}")
b2 = ax.bar(x+w/2, t_e.pct.values, w, color=CRED, label='eICU-CRD (n=%s)'%f"{len(e2):,}")
for bs in (b1,b2):
    for r in bs:
        ax.text(r.get_x()+r.get_width()/2, r.get_height()+0.6, '%.1f'%r.get_height(), ha='center', fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(['Dry-warm\n(no congestion,\nnormal perfusion)','Wet-warm\n(congestion,\nnormal perfusion)',
    'Dry-cold\n(no congestion,\nimpaired perfusion)','Wet-cold\n(congestion,\nimpaired perfusion)'], fontsize=7.5)
ax.set_ylabel('In-hospital mortality (%)'); ax.set_ylim(0,36)
ax.legend(frameon=False, fontsize=8, loc='upper left')
ax.set_title('Congestion–perfusion phenotypes and in-hospital mortality', fontsize=9.5, loc='left')
plt.tight_layout(); plt.savefig(FIG+'/Fig1_quadrant_gradient.png', dpi=400); plt.close()

# ---------- Fig 2 水肿等级 & 毛细血管再充盈 ----------
fig, axs = plt.subplots(1,2, figsize=(6.6,2.9))
g = mm.dropna(subset=['ew']).groupby('ew').agg(n=('died','size'), pct=('died', lambda s:100*s.mean()))
ax = axs[0]
lbl = ['None','2 mm','4 mm','6 mm','8 mm','Anasarca']
ax.bar(range(len(g)), g.pct.values, color=[CBLU]*3+[CRED]*3)
for i,(v,n) in enumerate(zip(g.pct.values, g.n.values)):
    ax.text(i, v+0.7, '%.1f'%v, ha='center', fontsize=7.5); ax.text(i, 0.6, 'n=%d'%n, ha='center', fontsize=6.5, color='white')
ax.set_xticks(range(len(g))); ax.set_xticklabels(lbl, fontsize=7.5, rotation=20)
ax.set_ylabel('In-hospital mortality (%)'); ax.set_ylim(0,32)
ax.set_title('A  Peripheral oedema grade (worst, first 24 h)', fontsize=8.5, loc='left')
ax = axs[1]
h = mm.dropna(subset=['cr_abn']).groupby('cr_abn').agg(n=('died','size'), pct=('died', lambda s:100*s.mean()))
ax.bar([0,1], h.pct.values, color=[CBLU, CRED])
for i,(v,n) in enumerate(zip(h.pct.values, h.n.values)):
    ax.text(i, v+0.7, '%.1f'%v, ha='center', fontsize=8); ax.text(i, 0.5, 'n=%d'%n, ha='center', fontsize=6.5, color='white')
ax.set_xticks([0,1]); ax.set_xticklabels(['Normal\n(<3 s)','Prolonged\n(>3 s)'], fontsize=8)
ax.set_ylabel('In-hospital mortality (%)'); ax.set_ylim(0,32)
ax.set_title('B  Capillary refill time', fontsize=8.5, loc='left')
plt.tight_layout(); plt.savefig(FIG+'/Fig2_edema_cr.png', dpi=400); plt.close()

# ---------- Fig 3 RCS ----------
def rcs_basis(x, k):
    k=np.asarray(k,float); x=np.asarray(x,float); B=[x]
    for j in range(len(k)-2):
        t=k[j+2]
        B.append(((x-t).clip(0)**3 - ((x-k[-1]).clip(0)**3)*(k[-1]-t)/(k[-1]-k[-2])
                  + ((x-k[-2]).clip(0)**3)*(k[-2]-t)/(k[-1]-k[-2]))/(k[-1]-k[0])**2)
    return np.column_stack(B)
sub = mm.dropna(subset=['ew'])
kn = np.percentile(sub.ew,[10,50,90]); B = rcs_basis(sub.ew,kn)
cov = np.column_stack([pd.to_numeric(sub.age,errors='coerce').fillna(60).values,
                       sub.gender.astype(str).str.upper().str.startswith('F').astype(int).values])
mr = sm.Logit(sub.died.values.astype(int), sm.add_constant(np.column_stack([B,cov]))).fit(disp=0)
grid=np.linspace(0,5,51); Bg=rcs_basis(grid,kn); Xg=np.column_stack([Bg, np.tile(cov.mean(0),(len(grid),1))])
Xg=sm.add_constant(Xg, has_constant='add')
lin = Xg @ np.asarray(mr.params)
se = np.sqrt(np.einsum('ij,jk,ik->i', Xg, np.asarray(mr.cov_params()), Xg))
pv = 100/(1+np.exp(-lin)); lo = 100/(1+np.exp(-(lin-1.96*se))); hi = 100/(1+np.exp(-(lin+1.96*se)))
ci = np.column_stack([lo,hi])
fig, ax = plt.subplots(figsize=(3.5,3.0))
ax.plot(grid, pv, color=CRED, lw=1.8); ax.fill_between(grid, ci[:,0], ci[:,1], color=CRED, alpha=0.15, lw=0)
ax.set_xlabel('Oedema grade (pitting depth)'); ax.set_ylabel('Predicted in-hospital mortality (%)')
ax.set_xticks(range(6)); ax.set_xticklabels(['0\nNone','1\n2 mm','2\n4 mm','3\n6 mm','4\n8 mm','5\nAnasarca'], fontsize=7)
ax.set_title('Dose–response: oedema grade and mortality', fontsize=8.5, loc='left')
plt.tight_layout(); plt.savefig(FIG+'/Fig3_RCS.png', dpi=400); plt.close()

# ---------- 模型（供 Fig4/5/6） ----------
CORE=['hr_min','hr_max','sbp_min','map_min','rr_max','spo2_min','adm_weight','cr_max','bun_max',
      'na_min','k_max','cl_min','hco3_min','hgb_min','wbc_max','plt_min','glu_max']
def prep(x):
    X=pd.DataFrame(index=x.index)
    for v in CORE+['age']: X[v]=pd.to_numeric(x[v].astype(str).str.replace('>','',regex=False).str.strip(),errors='coerce')
    X['female']=x.gender.astype(str).str.upper().str.startswith('F').astype(int)
    for v in ['mv','vaso','chf','ckd']: X[v]=pd.to_numeric(x[v],errors='coerce').fillna(0)
    return X
def auc(y,p):
    y=np.asarray(y).astype(int); r=pd.Series(p).rank().values; n1=y.sum(); n0=len(y)-n1
    return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)
Xb=prep(mm); yv=mm.died.values.astype(int); med=Xb.median(); Zb=(Xb.fillna(med)-med)/Xb.std().replace(0,1)
DUM=pd.DataFrame({'WetWarm':(mm.quad=='WetWarm').astype(int),'DryCold':(mm.quad=='DryCold').astype(int),'WetCold':(mm.quad=='WetCold').astype(int)},index=mm.index)
cols=CORE+['age','female','mv','vaso','chf','ckd']
m1=sm.Logit(yv, sm.add_constant(Zb[cols])).fit(disp=0)
m2=sm.Logit(yv, sm.add_constant(pd.concat([Zb[cols],DUM],axis=1))).fit(disp=0)
p1=m1.predict(sm.add_constant(Zb[cols])).values; p2=m2.predict(sm.add_constant(pd.concat([Zb[cols],DUM],axis=1))).values

fig, ax = plt.subplots(figsize=(3.4,3.3))
for p,lab,col in [(p1,'Routine variables only (AUC %.3f)'%auc(yv,p1),CGRY),(p2,'+ congestion–perfusion phenotype (AUC %.3f)'%auc(yv,p2),CRED)]:
    o=np.argsort(-p); yy=yv[o]; tpr=np.cumsum(yy)/yy.sum(); fpr=np.cumsum(1-yy)/(1-yy).sum()
    ax.plot(np.r_[0,fpr], np.r_[0,tpr], color=col, lw=1.6, label=lab)
ax.plot([0,1],[0,1],'k--',lw=0.8)
ax.set_xlabel('1 − Specificity'); ax.set_ylabel('Sensitivity'); ax.legend(frameon=False, fontsize=7, loc='lower right')
ax.set_title('A  Discrimination (MIMIC-IV)', fontsize=8.5, loc='left')
plt.tight_layout(); plt.savefig(FIG+'/Fig4_ROC.png', dpi=400); plt.close()

fig, axs = plt.subplots(1,2, figsize=(6.4,2.9))
for ax,(p,y,nm) in zip(axs,[(p2,yv,'MIMIC-IV (development, n=%d)'%len(yv)),(None,None,'eICU-CRD (external)')]):
    pass
# MIMIC 校准
q=pd.qcut(p2,10,labels=False,duplicates='drop'); cl=pd.DataFrame({'p':p2,'y':yv,'b':q}).groupby('b').agg(pred=('p','mean'),obs=('y','mean'))
ax=axs[0]; ax.plot([0,0.4],[0,0.4],'k--',lw=0.8); ax.plot(cl.pred,cl.obs,'o-',color=CBLU,ms=3.5,lw=1.4)
ax.set_xlabel('Predicted mortality'); ax.set_ylabel('Observed mortality'); ax.set_title('A  MIMIC-IV, n=%s'%format(len(yv),','), fontsize=8.5, loc='left')
ax.set_xlim(0,0.42); ax.set_ylim(0,0.42)
# eICU 校准
TRANS=['age','hr_min','hr_max','sbp_min','map_min','rr_max','spo2_min','adm_weight','cr_max','bun_max','na_min','k_max','cl_min','hco3_min','hgb_min','wbc_max','plt_min','glu_max']
def num(s): return pd.to_numeric(pd.Series(s).astype(str).str.replace('>','',regex=False).str.strip(),errors='coerce')
def build(d):
    X=pd.DataFrame(index=d.index)
    for v in TRANS: X[v]=num(d[v]) if v in d.columns else np.nan
    X['female']=pd.Series(d.gender).astype(str).str.upper().str.startswith('F').astype(int).values
    for kk,qd in [('WetWarm','WetWarm'),('DryCold','DryCold'),('WetCold','WetCold')]: X[kk]=(d.quad==qd).astype(int).values
    return X
Xmm=build(mm); medt=Xmm.median(); sdt=Xmm.std().replace(0,1)
mtr=sm.Logit(yv, sm.add_constant((Xmm.fillna(medt)-medt)/sdt)).fit(disp=0)
Xee=build(e2)
# 顺序不可颠倒：必须先按 >=60% 可得性筛住院，再做中位数插补（先插补会把缺失填掉、使筛子失效）
keep=(Xee[TRANS].notna().mean(axis=1)>=0.6).values
Xee=Xee.loc[keep]; yee=e2.loc[keep,'died'].values.astype(int)
Zee=(Xee.fillna(medt)-medt)/sdt
pee=mtr.predict(sm.add_constant(Zee)).values
assert len(yee)==1541, '外部校准集 n 与 final_eicu_model.py 不一致：%d' % len(yee)
_ref=np.load(OUT+'/pred_eicu_clean.npy')
assert len(_ref)==len(pee) and np.allclose(np.sort(_ref), np.sort(pee), atol=1e-9), '校准面板预测值与 final_eicu_model.py 不一致'
print('calibration panel: n=%d deaths=%d AUC=%.4f' % (len(yee), yee.sum(), auc(yee,pee)))
q=pd.qcut(pee,8,labels=False,duplicates='drop'); cl2=pd.DataFrame({'p':pee,'y':yee,'b':q}).groupby('b').agg(pred=('p','mean'),obs=('y','mean'))
ax=axs[1]; ax.plot([0,0.45],[0,0.45],'k--',lw=0.8); ax.plot(cl2.pred,cl2.obs,'o-',color=CRED,ms=3.5,lw=1.4)
ax.set_xlabel('Predicted mortality'); ax.set_ylabel('Observed mortality'); ax.set_title('B  eICU-CRD, n=%s (AUC %.3f)'%(format(len(yee),','),auc(yee,pee)), fontsize=8.5, loc='left')
ax.set_xlim(0,0.46); ax.set_ylim(0,0.46)
plt.tight_layout(); plt.savefig(FIG+'/Fig5_calibration.png', dpi=400); plt.close()

# ---------- Fig 6 DCA ----------
def nb(y,p,t):
    y=np.asarray(y); n=len(y); tp=((p>=t)&(y==1)).sum()/n; fp=((p>=t)&(y==0)).sum()/n
    return tp-fp*t/(1-t)
ths=np.arange(0.01,0.31,0.005)
fig, ax = plt.subplots(figsize=(3.4,3.0))
ax.plot(ths,[nb(yv,p2,t) for t in ths], color=CRED, lw=1.6, label='Model (routine + phenotype)')
ax.plot(ths,[nb(yv,p1,t) for t in ths], color=CGRY, lw=1.4, ls='--', label='Routine variables only')
ax.plot(ths,[nb(yv,np.ones_like(p2),t) for t in ths], color='k', lw=0.9, ls=':', label='Treat all')
ax.axhline(0,color='k',lw=0.7)
ax.set_xlabel('Threshold probability'); ax.set_ylabel('Net benefit'); ax.set_ylim(-0.02,0.06); ax.set_xlim(0,0.30)
ax.legend(frameon=False, fontsize=7); ax.set_title('Decision curve analysis', fontsize=8.5, loc='left')
plt.tight_layout(); plt.savefig(FIG+'/Fig6_DCA.png', dpi=400); plt.close()

# ---------- Fig 7 轨迹 ----------
g=c.execute(f"""SELECT stay_id, max(CASE WHEN off_h>=0 AND off_h<24 THEN g END) g_early,
   max(CASE WHEN off_h>=24 AND off_h<72 THEN g END) g_late FROM
  (SELECT stay_id, off_h, CASE trim(lower(value)) WHEN 'none' THEN 0 WHEN '2 mm' THEN 1 WHEN '4 mm' THEN 2
   WHEN '6 mm' THEN 3 WHEN '8 mm' THEN 4 WHEN 'anasarca' THEN 5 END g
   FROM read_parquet('{D}/cp_exam_raw.parquet') WHERE itemid=224862 AND off_h>=0 AND off_h<72 AND value IS NOT NULL)
 GROUP BY stay_id HAVING g_early IS NOT NULL AND g_late IS NOT NULL""").df()
def cls(r):
    if r.g_early>=3 and r.g_late>=3: return 'Persistent'
    if r.g_early>=3 and r.g_late<3: return 'Resolved'
    if r.g_early<3 and r.g_late>=3: return 'Emerging'
    return 'Never'
g['traj']=g.apply(cls,axis=1)
t=g.merge(mm[['stay_id','died','los']],on='stay_id',how='inner')
order=['Never','Resolved','Emerging','Persistent']
tab=t.groupby('traj').agg(n=('died','size'),pct=('died',lambda s:100*s.mean()),
                          n_los=('los','median')).reindex(order)
prof=t.groupby('traj')[['g_early','g_late']].mean().reindex(order)
fig, axs = plt.subplots(1,2, figsize=(7.0,2.9), gridspec_kw={'width_ratios':[1,1]})
ax=axs[0]
cols=[CBLU,'#7FA8C9',CRED,'#7A1F1F']
for i,o in enumerate(order):
    ax.plot([0,1],[prof.loc[o,'g_early'],prof.loc[o,'g_late']],'o-',color=cols[i],lw=1.8,ms=4,label=o)
ax.set_xticks([0,1]); ax.set_xticklabels(['0–24 h','24–72 h'])
ax.set_ylabel('Mean oedema grade'); ax.set_ylim(0,4.5)
ax.legend(frameon=False, fontsize=7.5); ax.set_title('A  Congestion trajectory groups', fontsize=8.5, loc='left')
ax=axs[1]
ax.bar(range(4), tab.pct.values, color=cols)
for i,(v,n) in enumerate(zip(tab.pct.values, tab.n.values)):
    ax.text(i,v+0.3,'%.1f%%'%v,ha='center',fontsize=8); ax.text(i,0.35,'n=%d'%n,ha='center',fontsize=6.5,color='white')
ax.set_xticks(range(4)); ax.set_xticklabels(order, fontsize=8, rotation=15)
ax.set_ylabel('In-hospital mortality (%)'); ax.set_ylim(0,18)
ax.set_title('B  Mortality by trajectory (n=%d)'%len(t), fontsize=8.5, loc='left')
plt.tight_layout(); plt.savefig(FIG+'/Fig7_trajectory.png', dpi=400); plt.close()

# ---------- Fig 8 森林图 ----------
tb=m2.summary2().tables[1]
items=[('Wet-warm vs dry-warm','WetWarm'),('Dry-cold vs dry-warm','DryCold'),('Wet-cold vs dry-warm','WetCold')]
fig, ax = plt.subplots(figsize=(4.2,2.2))
for i,(lab,k) in enumerate(items):
    co,se=tb.loc[k,'Coef.'],tb.loc[k,'Std.Err.']; orv=np.exp(co)
    ax.plot([np.exp(co-1.96*se),np.exp(co+1.96*se)],[i,i],color=CRED,lw=1.6)
    ax.plot(orv,i,'s',color=CRED,ms=6)
    ax.text(np.exp(co+1.96*se)*1.06, i, '%.2f (%.2f–%.2f)'%(orv,np.exp(co-1.96*se),np.exp(co+1.96*se)), va='center', fontsize=7.5)
ax.axvline(1,color='k',lw=0.8,ls='--')
ax.set_yticks(range(3)); ax.set_yticklabels([a for a,_ in items], fontsize=8)
ax.set_xscale('log'); ax.set_xlim(0.8,16); ax.set_xlabel('Adjusted odds ratio (95% CI)', fontsize=8)
ax.set_title('Congestion–perfusion phenotype and in-hospital death\n(reference: dry-warm)', fontsize=8.5, loc='left')
plt.tight_layout(); plt.savefig(FIG+'/Fig8_forest_OR.png', dpi=400); plt.close()

print('figures ->', FIG)
for f in sorted(os.listdir(FIG)): print('  ', f, os.path.getsize(FIG+'/'+f)//1024, 'KB')
