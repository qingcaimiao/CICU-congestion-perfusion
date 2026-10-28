# -*- coding: utf-8 -*-
"""第六轮核查：转移模型参数基数 / 时间验证样本 / eICU 完整案例外部性能 /
   'flushed' 与水肿亚类敏感性 / 院级表现 / 四字段完整取值频数"""
import duckdb, numpy as np, pandas as pd, json, warnings
warnings.filterwarnings('ignore')
import statsmodels.api as sm
from scipy import stats

F = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58'
D = F + '/T2_data'
OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
E = 'D:/shujuku/EICU 2.0'
c = duckdb.connect(); c.execute('PRAGMA threads=8')
R = lambda p: "read_csv_auto('%s',header=true,strict_mode=false,ignore_errors=true)" % p
NL = chr(10)
TRANS18 = ['age', 'hr_min', 'hr_max', 'sbp_min', 'map_min', 'rr_max', 'spo2_min', 'adm_weight',
           'cr_max', 'bun_max', 'na_min', 'k_max', 'cl_min', 'hco3_min', 'hgb_min', 'wbc_max', 'plt_min', 'glu_max']


def num(s):
    return pd.to_numeric(pd.Series(s).astype(str).str.replace('>', '', regex=False).str.strip(), errors='coerce')


def auc(y, p):
    y = np.asarray(y).astype(int); p = np.asarray(p, dtype=float)
    r = pd.Series(p).rank().values; n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


res = {}

# ================= 1. 转移模型参数基数 & EPV =================
mm = c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()
ee = c.execute(f"SELECT * FROM read_parquet('{D}/eicu_cp.parquet')").df().rename(columns={'admissionweight': 'adm_weight'})
ee['cong_any'] = ((ee.edema_pos.fillna(0) == 1) | (ee.jvd_pos.fillna(0) == 1) | (ee.crackles.fillna(0) == 1)).astype(int)
sub = ee[(ee[['edema_doc', 'jvd_doc', 'lungs_doc']].fillna(0).sum(axis=1) > 0) & (ee.perf_doc.fillna(0) == 1)].copy()
sub['quad'] = np.where((sub.cong_any == 1) & (sub.hypoperf.fillna(0) == 1), 'WetCold',
              np.where((sub.cong_any == 1) & (sub.hypoperf.fillna(0) == 0), 'WetWarm',
              np.where((sub.cong_any == 0) & (sub.hypoperf.fillna(0) == 1), 'DryCold', 'DryWarm')))


def frame(d):
    X = pd.DataFrame(index=d.index)
    for v in TRANS18:
        X[v] = num(d[v])
    X['female'] = pd.Series(d.gender).astype(str).str.upper().str.startswith('F').astype(int).values
    for k in ['WetWarm', 'DryCold', 'WetCold']:
        X[k] = (d.quad == k).astype(int)
    return X


Xm = frame(mm); Xe = frame(sub)
keep = (Xe[TRANS18].notna().mean(axis=1) >= 0.6).values
med = Xm.median(); sd = Xm.std().replace(0, 1)
Zm = (Xm.fillna(med) - med) / sd
Zek = (Xe.loc[keep].fillna(med) - med) / sd
yk = sub.loc[keep, 'died'].values.astype(int)
fit = sm.Logit(mm.died.values.astype(int), sm.add_constant(Zm)).fit(disp=0)
pe = fit.predict(sm.add_constant(Zek)).values
z = np.log(np.clip(pe, 1e-9, 1 - 1e-9) / (1 - np.clip(pe, 1e-9, 1 - 1e-9)))
rec = sm.Logit(yk, sm.add_constant(pd.Series(z, index=range(len(yk))), has_constant='add')).fit(disp=0)
pr = np.asarray(rec.params).ravel()
n_par = Zm.shape[1]                       # 不含截距的参数个数
res['spec'] = dict(n_columns=int(n_par), n_continuous=18, plus_sex=1, plus_phenotype=3,
                   deaths=int(yk.sum()), epv_excl_intercept=round(int(yk.sum()) / n_par, 1),
                   epv_if_19=round(int(yk.sum()) / 19, 1),
                   external_auc=round(auc(yk, pe), 4), oe=round(yk.mean() / pe.mean(), 3),
                   slope=round(float(pr[1]), 3), intercept=round(float(pr[0]), 3),
                   n=int(len(yk)), mean_pred=round(100 * pe.mean(), 2), obs=round(100 * yk.mean(), 2))
print('== 1. 转移模型 ==')
print('  参数列数（不含截距）= %d  = 18 连续 + 性别 + 3 表型哑变量' % n_par)
print('  事件 %d → EPV = %.1f（若按 19 计则为 %.1f）' % (yk.sum(), yk.sum() / n_par, yk.sum() / 19))

# ================= 2. 时间验证样本 =================
# 时代映射走 hosp/patients.csv（零缺失）；旧实现误用另一课题的 mimic_T2.parquet，
# 只覆盖 9,715/12,052，把 2,337 例本队列患者误报为"无时代标注"
from _ayg import attach_ayg, split_era
d2 = attach_ayg(mm.copy(), con=c)
tr, te = split_era(d2)
miss = d2[d2.ayg.isna()]
print('== 2. 时间验证 ==')
print('  分析集 %d = 训练 %d + 测试 %d + anchor_year_group 缺失 %d' % (len(d2), len(tr), len(te), len(miss)))
for g, s in d2.groupby('ayg'):
    print('    %-14s n=%5d 死亡 %4d (%.2f%%)' % (g, len(s), int(s.died.sum()), 100 * s.died.mean()))
res['temporal'] = dict(total=int(len(d2)), train=int(len(tr)), test=int(len(te)), missing_group=int(len(miss)),
                       train_deaths=int(tr.died.sum()), test_deaths=int(te.died.sum()),
                       missing_deaths=int(miss.died.sum()),
                       missing_mortality_pct=(round(100 * miss.died.mean(), 2) if len(miss) else None),
                       groups={str(k): int(v) for k, v in d2.ayg.value_counts(dropna=False).items()})

# ================= 3. eICU 完整案例外部性能 =================
Xe_all = Xe.copy()
ok_all = Xe_all.notna().all(axis=1).values
Ze_c = (Xe_all.loc[ok_all].fillna(med) - med) / sd
yc = sub.loc[ok_all, 'died'].values.astype(int)
pe_c = fit.predict(sm.add_constant(Ze_c)).values
zc = np.log(np.clip(pe_c, 1e-9, 1 - 1e-9) / (1 - np.clip(pe_c, 1e-9, 1 - 1e-9)))
rc = sm.Logit(yc, sm.add_constant(pd.Series(zc, index=range(len(yc))), has_constant='add')).fit(disp=0)
pc = np.asarray(rc.params).ravel()
print('== 3. eICU 完整案例外部性能 ==')
print('  n=%d 死亡=%d  AUROC=%.3f  O:E=%.2f  斜率=%.3f' % (len(yc), yc.sum(), auc(yc, pe_c), yc.mean() / pe_c.mean(), pc[1]))
res['complete_case'] = dict(n=int(len(yc)), deaths=int(yc.sum()), auc=round(auc(yc, pe_c), 4),
                            oe=round(float(yc.mean() / pe_c.mean()), 3), slope=round(float(pc[1]), 3),
                            intercept=round(float(pc[0]), 3))

# ================= 4. 院级表现（逐院 AUROC）=================
sub2 = sub.loc[keep].copy(); sub2['pe'] = pe
hosp = []
for h, g in sub2.groupby('hospitalid'):
    if len(g) >= 20 and g.died.sum() >= 5:
        hosp.append(dict(hospital=int(h), n=len(g), deaths=int(g.died.sum()),
                         mortality=round(100 * g.died.mean(), 2), auc=round(auc(g.died.values, g.pe.values), 3)))
    else:
        hosp.append(dict(hospital=int(h), n=len(g), deaths=int(g.died.sum()),
                         mortality=round(100 * g.died.mean(), 2), auc=('n/a' if g.died.nunique() < 2 else 'unstable')))
pd.DataFrame(hosp).to_csv(OUT + '/TableS9E_per_hospital.csv', index=False)
print('== 4. 院级表现 ==')
print(pd.DataFrame(hosp).to_string(index=False))
res['per_hospital'] = hosp

# ================= 5. flushed / 水肿亚类敏感性 =================
print('== 5. 暴露定义的敏感性 ==')
c.execute(f"""CREATE OR REPLACE TABLE exs AS
SELECT coh.patientunitstayid,
  max(CASE WHEN lower(p.physicalexampath) LIKE '%extremities/perfusion/extremities cool%'
             OR lower(p.physicalexampath) LIKE '%extremities/perfusion/extremities cold/dusky%' THEN 1 ELSE 0 END) hypoperf_strict,
  max(CASE WHEN lower(p.physicalexampath) LIKE '%extremities/perfusion/extremities flushed%' THEN 1 ELSE 0 END) flushed_any,
  max(CASE WHEN lower(p.physicalexampath) LIKE '%extremities/edema/localized swelling%'
             OR lower(p.physicalexampath) LIKE '%edema/location/upper extremity%'
             OR lower(p.physicalexampath) LIKE '%edema/location/lower extremity unilateral%' THEN 1 ELSE 0 END) edema_other,
  max(CASE WHEN (lower(p.physicalexampath) LIKE '%extremities/edema/bilateral%'
                 AND lower(trim(p.physicalexamvalue)) NOT LIKE 'no %')
             OR (lower(p.physicalexampath) LIKE '%extremities/edema/severity%'
                 AND lower(trim(p.physicalexamvalue)) IN ('1+','2+','3+','4+'))
             OR lower(trim(p.physicalexamvalue)) LIKE '%anasarca%' THEN 1 ELSE 0 END) edema_localised_pos
FROM (SELECT patientunitstayid FROM read_parquet('{D}/eicu_cp.parquet')) coh
JOIN {R(E + '/physicalExam.csv')} p ON coh.patientunitstayid=p.patientunitstayid
WHERE p.physicalexamoffset>=-360 AND p.physicalexamoffset<=1440
  AND (lower(p.physicalexampath) LIKE '%extremities/edema%'
    OR lower(p.physicalexampath) LIKE '%extremities/perfusion%')
GROUP BY 1""")
xs = c.execute("SELECT * FROM exs").df()
sub3 = sub.merge(xs, on='patientunitstayid', how='left')
bronze = sub3[sub3.perf_doc.fillna(0) == 1]
print('  仅 flushed 而被判为 impaired 的住院：analy­sable 子集中 %d 例' % int((bronze.hypoperf.fillna(0) == 1).sum() - (bronze.hypoperf_strict.fillna(0) == 1).sum()))
print('  仅有 localized/unilateral/upper-extremity 水肿记录且被判为阴性：%d 例' % int(((bronze.edema_pos.fillna(0) == 0) & (bronze.edema_other.fillna(0) == 1)).sum()))

# 5a. 灌注轴：flushed 是否计入
for lab, col in [('灌注=任何非 adequate（主分析）', 'hypoperf'), ('灌注=仅 cool/cold-dusky（排除 flushed）', 'hypoperf_strict')]:
    a = bronze[bronze[col].fillna(0) == 1]; b = bronze[bronze[col].fillna(0) == 0]
    print('  %-38s (+) %.2f%% (n=%d) vs (-) %.2f%% (n=%d)  ratio %.2f'
          % (lab, 100 * a.died.mean(), len(a), 100 * b.died.mean(), len(b), a.died.mean() / max(b.died.mean(), 1e-9)))
    res.setdefault('perfusion_def', {})[col] = dict(pos_n=int(len(a)), pos_pct=round(100 * a.died.mean(), 2),
                                                    neg_n=int(len(b)), neg_pct=round(100 * b.died.mean(), 2))

# 5b. 复合四格：flushed 口径 + 水肿亚类口径
for lab, pcol, ecol in [('flushed 计入（主分析）', 'hypoperf', 'edema_pos'),
                        ('flushed 排除', 'hypoperf_strict', 'edema_pos'),
                        ('flushed 排除 + localized/unilateral 计入阳性', 'hypoperf_strict', 'edema_pos_broad')]:
    t = sub3.copy()
    if ecol == 'edema_pos_broad':
        t['edema_pos_broad'] = np.where((t.edema_pos.fillna(0) == 1) | (t.edema_other.fillna(0) == 1), 1, 0)
    t = t[t.perf_doc.fillna(0) == 1].copy()
    t['c'] = np.where(((t[ecol].fillna(0) == 1) | (t.jvd_pos.fillna(0) == 1) | (t.crackles.fillna(0) == 1)), 1, 0)
    t['q'] = np.where((t.c == 1) & (t[pcol].fillna(0) == 1), 'WetCold',
             np.where((t.c == 1) & (t[pcol].fillna(0) == 0), 'WetWarm',
             np.where((t.c == 0) & (t[pcol].fillna(0) == 1), 'DryCold', 'DryWarm')))
    g = t.groupby('q').agg(n=('died', 'size'), deaths=('died', 'sum'))
    g['pct'] = (100 * g.deaths / g.n).round(2)
    g = g.reindex(['DryWarm', 'WetWarm', 'DryCold', 'WetCold'])
    print('  [%s] n=%d | DW %.2f WW %.2f DC %.2f WC %.2f' % (lab, len(t), g.pct.DryWarm, g.pct.WetWarm, g.pct.DryCold, g.pct.WetCold))
    res.setdefault('quad_def', {})[lab] = {k: float(v) for k, v in g.pct.items()}

json.dump(res, open(OUT + '/round6_checks.json', 'w'), ensure_ascii=False, indent=1, default=str)
print(NL + '-> round6_checks.json')
