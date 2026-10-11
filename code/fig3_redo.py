# -*- coding: utf-8 -*-
"""重绘 Fig3：水肿等级 (A) 未校正死亡率 (B) 校正后 OR —— 替代原纯 RCS 图"""
import duckdb, numpy as np, pandas as pd, os, warnings
warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import statsmodels.api as sm
plt.rcParams.update({'font.family':'Arial','font.size':9,'axes.linewidth':0.8,
                     'xtick.major.width':0.8,'ytick.major.width':0.8,'axes.spines.top':False,'axes.spines.right':False})
OUT='D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'; FIG='D:/桌面/workbuddyzuopin/CPxiangmu/04_图'
c=duckdb.connect(); mm=c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()
mm['female']=mm.gender.astype(str).str.upper().str.startswith('F').astype(int)
def num(s): return pd.to_numeric(pd.Series(s).astype(str).str.replace('>','',regex=False).str.strip(),errors='coerce')
ew=num(mm.ew); cr=pd.to_numeric(mm.cr_abn,errors='coerce'); y=mm.died.values.astype(int)
lab=['None','2 mm','4 mm','6 mm','8 mm','Anasarca']
g=mm.dropna(subset=['ew']).groupby('ew').agg(n=('died','size'),mort=('died',lambda s:100*s.mean()),
                                             d=('died','sum'))
CORE=['hr_min','hr_max','sbp_min','map_min','rr_max','spo2_min','temp_mean','adm_weight','cr_max','bun_max',
      'na_min','k_max','cl_min','hco3_min','hgb_min','wbc_max','plt_min','glu_max']
X=pd.DataFrame(index=mm.index)
for v in CORE+['age']: X[v]=num(mm[v])
X['female']=mm.female
for v in ['mv','vaso','chf','ckd']: X[v]=pd.to_numeric(mm[v],errors='coerce').fillna(0)
med=X.median(); Z=(X.fillna(med)-med)/X.std().replace(0,1)
Xd=Z[CORE+['age','female','mv','vaso','chf','ckd']].copy()
for k in [1,2,3,4,5]: Xd['ed_%d'%k]=(ew==k).astype(float)
Xd['CRT']=cr.fillna(0)
m=sm.Logit(y, sm.add_constant(Xd)).fit(disp=0)
tb=m.summary2().tables[1]
ors=[]
for k in [1,2,3,4,5]:
    co,se=tb.loc['ed_%d'%k,'Coef.'],tb.loc['ed_%d'%k,'Std.Err.']
    ors.append((np.exp(co), np.exp(co-1.96*se), np.exp(co+1.96*se)))
ors=[(1.0,1.0,1.0)]+ors   # 参照 grade 0

fig, axs = plt.subplots(1,2, figsize=(6.8,3.0))
ax=axs[0]
cols=['#2F5D8A']*3+['#B23A3A']*3
ax.bar(range(6), g.mort.values, color=cols)
for i,(v,n) in enumerate(zip(g.mort.values, g.n.values)):
    ax.text(i, v+0.8, '%.1f'%v, ha='center', fontsize=7.5)
    ax.text(i, 0.7, 'n=%d'%n, ha='center', fontsize=6.2, color='white')
ax.set_xticks(range(6)); ax.set_xticklabels(lab, fontsize=7, rotation=20)
ax.set_ylabel('In-hospital mortality (%)'); ax.set_ylim(0,32)
ax.set_title('A  Unadjusted mortality by oedema grade', fontsize=8.5, loc='left')
ax=axs[1]
xs=np.arange(6)
for i,(o,lo,hi) in enumerate(ors):
    ax.plot([lo,hi],[i,i], color='#B23A3A' if i>=3 else '#2F5D8A', lw=1.6)
    ax.plot(o,i,'s', color='#B23A3A' if i>=3 else '#2F5D8A', ms=5.5)
ax.axvline(1,color='k',lw=0.8,ls='--')
ax.set_yticks(xs); ax.set_yticklabels(['0 (ref)']+lab[1:], fontsize=7.5)
ax.set_xscale('log'); ax.set_xlim(0.5,5); ax.set_xlabel('Adjusted odds ratio (95% CI)', fontsize=8)
ax.set_title('B  Multivariable-adjusted OR by grade', fontsize=8.5, loc='left')
plt.tight_layout(); plt.savefig(FIG+'/Fig3_edema_grade.png', dpi=400); plt.close()
os.remove(FIG+'/Fig3_RCS.png')
# TIFF
from PIL import Image
im=Image.open(FIG+'/Fig3_edema_grade.png').convert('RGB')
im.save(FIG+'/figures_TIFF600/Fig3_edema_grade_600dpi.tif','TIFF',compression='tiff_lzw',dpi=(600,600))
try: os.remove(FIG+'/figures_TIFF600/Fig3_RCS_600dpi.tif')
except: pass
print('OR by grade:')
for i,(o,lo,hi) in enumerate(ors):
    print('   grade %d: %.2f (%.2f-%.2f)'%(i,o,lo,hi))
print('regenerated Fig3_edema_grade (+600dpi TIFF)')
