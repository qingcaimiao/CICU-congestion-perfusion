# -*- coding: utf-8 -*-
"""缺失数据处置的敏感性分析：中位数插补（主分析）vs 完整案例（complete case）。

MIMIC-IV：主分析对协变量做中位数插补（分析集限定为暴露可判定者）。
eICU-CRD：主分析用「≥60% 可迁移协变量可得 + 中位数插补」；此处改为完整案例。
"""
import duckdb, numpy as np, pandas as pd, json, statsmodels.api as sm

np.random.seed(20261012)
c = duckdb.connect(); c.execute('PRAGMA threads=8')
D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
CORE = ['hr_min', 'hr_max', 'sbp_min', 'map_min', 'rr_max', 'spo2_min', 'adm_weight',
        'cr_max', 'bun_max', 'na_min', 'k_max', 'cl_min', 'hco3_min', 'hgb_min',
        'wbc_max', 'plt_min', 'glu_max']
BASE = CORE + ['age', 'female', 'mv', 'vaso', 'chf', 'ckd']
TRANS18 = ['age', 'hr_min', 'hr_max', 'sbp_min', 'map_min', 'rr_max', 'spo2_min', 'adm_weight',
           'cr_max', 'bun_max', 'na_min', 'k_max', 'cl_min', 'hco3_min', 'hgb_min',
           'wbc_max', 'plt_min', 'glu_max']
num = lambda s: pd.to_numeric(pd.Series(s).astype(str).str.replace('>', '', regex=False).str.strip(), errors='coerce')


def auc(y, p):
    y = np.asarray(y).astype(int); r = pd.Series(p).rank().values
    n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def bci(y, p_new, p_old, n=2000):
    idx = np.arange(len(y)); d = []
    for _ in range(n):
        b = np.random.choice(idx, len(idx), replace=True)
        if y[b].sum() < 5:
            continue
        d.append(auc(y[b], p_new[b]) - auc(y[b], p_old[b]))
    d = np.array(d)
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


res = {}

# ---------------- MIMIC ----------------
mm = c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df().dropna(subset=['quad']).copy()
mm['female'] = mm.gender.astype(str).str.upper().str.startswith('F').astype(int)
X = pd.DataFrame(index=mm.index)
for v in CORE + ['age']:
    X[v] = num(mm[v])
X['female'] = mm.female
for v in ['mv', 'vaso', 'chf', 'ckd']:
    X[v] = pd.to_numeric(mm[v], errors='coerce').fillna(0)
DUM = pd.DataFrame({'WetWarm': (mm.quad == 'WetWarm').astype(int), 'DryCold': (mm.quad == 'DryCold').astype(int),
                    'WetCold': (mm.quad == 'WetCold').astype(int)}, index=mm.index)

def mim(tag, keep):
    Z = X.loc[keep]; D2 = DUM.loc[keep]; y = mm.loc[keep, 'died'].values.astype(int)
    med = Z.median(); Zs = (Z.fillna(med) - med) / Z.std().replace(0, 1)
    m0 = sm.Logit(y, sm.add_constant(Zs[BASE])).fit(disp=0)
    X2 = sm.add_constant(pd.concat([Zs[BASE], D2], axis=1)); m1 = sm.Logit(y, X2).fit(disp=0)
    p0 = m0.predict(sm.add_constant(Zs[BASE])).values; p1 = m1.predict(X2).values
    lo, hi = bci(y, p1, p0)
    ors = {k: round(float(np.exp(m1.params[k])), 3) for k in ['WetWarm', 'DryCold', 'WetCold']}
    r = {'n': int(keep.sum()), 'deaths': int(y.sum()), 'auc_base': round(float(auc(y, p0)), 4),
         'auc_pheno': round(float(auc(y, p1)), 4), 'dauc': round(float(auc(y, p1) - auc(y, p0)), 4),
         'dauc_ci': [round(lo, 4), round(hi, 4)], 'OR': ors}
    print('  %-22s n=%5d 死亡=%4d  AUROC %.4f→%.4f  Δ=%+.4f (%+.4f~%+.4f)  OR 湿暖/干冷/湿冷 = %.2f/%.2f/%.2f'
          % (tag, r['n'], r['deaths'], r['auc_base'], r['auc_pheno'], r['dauc'], lo, hi,
             ors['WetWarm'], ors['DryCold'], ors['WetCold']))
    return r

print('=' * 100); print('MIMIC-IV 缺失数据处理敏感性')
keep_imp = pd.Series(True, index=mm.index)
keep_cc = X[BASE].notna().all(axis=1)
res['mimic_imputed'] = mim('中位数插补（主分析）', keep_imp)
res['mimic_complete'] = mim('完整案例', keep_cc)

# ---------------- eICU ----------------
ee = c.execute(f"SELECT * FROM read_parquet('{D}/eicu_cp.parquet')").df().rename(columns={'admissionweight': 'adm_weight'})
ee['cong_any'] = ((ee.edema_pos.fillna(0) == 1) | (ee.jvd_pos.fillna(0) == 1) | (ee.crackles.fillna(0) == 1)).astype(int)
sub = ee[((ee[['edema_doc', 'jvd_doc', 'lungs_doc']].fillna(0).sum(axis=1) > 0) & (ee.perf_doc.fillna(0) == 1))].copy()
sub['quad'] = np.where((sub.cong_any == 1) & (sub.hypoperf.fillna(0) == 1), 'WetCold',
              np.where((sub.cong_any == 1) & (sub.hypoperf.fillna(0) == 0), 'WetWarm',
              np.where((sub.cong_any == 0) & (sub.hypoperf.fillna(0) == 1), 'DryCold', 'DryWarm')))

def ef(v):
    Xx = pd.DataFrame(index=v.index)
    for k in TRANS18:
        Xx[k] = num(v[k])
    Xx['female'] = pd.Series(v.gender).astype(str).str.upper().str.startswith('F').astype(int).values
    for k in ['WetWarm', 'DryCold', 'WetCold']:
        Xx[k] = (v['quad'] == k).astype(int)
    return Xx

Xm = ef(mm); Xe = ef(sub)
med = Xm.median(); sd = Xm.std().replace(0, 1)

def eicu_run(tag, keep):
    Xk = Xe.loc[keep]; y = sub.loc[keep, 'died'].values.astype(int)
    Z = (Xk[TRANS18].fillna(med) - med) / sd
    Z2 = pd.DataFrame({**{k: Z[k] for k in TRANS18}, **{'female': Xk['female']}})
    Z2 = pd.concat([Z2, Xk[['WetWarm', 'DryCold', 'WetCold']]], axis=1)
    m = sm.Logit(y, sm.add_constant(Z2)).fit(disp=0)
    p = m.predict(sm.add_constant(Z2)).values
    ors = {k: round(float(np.exp(m.params[k])), 3) for k in ['WetWarm', 'DryCold', 'WetCold']}
    r = {'n': int(keep.sum()), 'deaths': int(y.sum()), 'auc': round(float(auc(y, p)), 4), 'OR': ors}
    print('  %-30s n=%5d 死亡=%4d  eICU 内部拟合 AUROC=%.4f  OR 湿暖/干冷/湿冷 = %.2f/%.2f/%.2f'
          % (tag, r['n'], r['deaths'], r['auc'], ors['WetWarm'], ors['DryCold'], ors['WetCold']))
    return r

print(); print('=' * 100); print('eICU-CRD 缺失数据处理敏感性（在 eICU 内拟合、用 MIMIC 的标准化常数；仅用于对照两种缺失处理，非迁移模型性能）')
keep60 = Xe[TRANS18].notna().mean(axis=1) >= 0.6
keep_cc_e = Xe[TRANS18].notna().all(axis=1)
res['eicu_ge60'] = eicu_run('≥60% 可得 + 中位数插补（主分析）', keep60)
res['eicu_complete'] = eicu_run('完整案例', keep_cc_e)

json.dump(res, open(OUT + '/R3_missing_data.json', 'w'), ensure_ascii=False, indent=1)
print('\n-> R3_missing_data.json')
