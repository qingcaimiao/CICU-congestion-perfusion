# -*- coding: utf-8 -*-
"""敏感性分析：生理合理性筛查后（主分析） vs 按原始记录值（as-charted）

- 开发队列：mimic_cp.parquet（筛查后） vs mimic_cp_raw.parquet（原始）
- 复现队列：eicu_cp.parquet（筛查后） vs eicu_cp_raw.parquet（原始）
输出：03_结果/sensitivity_raw_vs_screened.csv / .md
"""
import duckdb, numpy as np, pandas as pd, json
import statsmodels.api as sm

np.random.seed(20261011)
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


def num(s):
    return pd.to_numeric(pd.Series(s).astype(str).str.replace('>', '', regex=False).str.strip(), errors='coerce')


def auc(y, p):
    y = np.asarray(y).astype(int); r = pd.Series(p).rank().values
    n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


# ---------------- 开发队列 ----------------
def build_dev(feat_parquet):
    q = f"""
    WITH e AS (
      SELECT stay_id,
        max(CASE trim(lower(value)) WHEN 'none' THEN 0 WHEN '2 mm' THEN 1 WHEN '4 mm' THEN 2
             WHEN '6 mm' THEN 3 WHEN '8 mm' THEN 4 WHEN 'anasarca' THEN 5 END) ed_win
      FROM read_parquet('{D}/cp_exam_raw.parquet') WHERE itemid=224862 AND off_h>=-6 AND off_h<=24 GROUP BY 1),
    cr AS (SELECT stay_id, max(CASE WHEN trim(lower(value)) LIKE 'abnormal%' THEN 1 ELSE 0 END) cr_abn
      FROM read_parquet('{D}/cp_exam_raw.parquet') WHERE itemid IN (223951,224308) AND off_h>=-6 AND off_h<=24 GROUP BY 1)
    SELECT m.*, e.ed_win, cr.cr_abn
    FROM read_parquet('{feat_parquet}') m
    LEFT JOIN e USING(stay_id) LEFT JOIN cr USING(stay_id)"""
    df = c.execute(q).df()
    df['stay_id'] = df.stay_id.astype('int64')
    ew = pd.to_numeric(df.ed_win, errors='coerce'); crv = pd.to_numeric(df.cr_abn, errors='coerce')
    quad = pd.Series(np.nan, index=df.index, dtype=object); m0 = ew.notna() & crv.notna()
    quad[m0 & (ew >= 3) & (crv == 1)] = 'WetCold'; quad[m0 & (ew >= 3) & (crv == 0)] = 'WetWarm'
    quad[m0 & (ew <= 2) & (crv == 1)] = 'DryCold'; quad[m0 & (ew <= 2) & (crv == 0)] = 'DryWarm'
    df['quad'] = quad
    return df.dropna(subset=['quad']).copy()


def dev_metrics(d):
    X = pd.DataFrame(index=d.index)
    for v in CORE + ['age']:
        X[v] = num(d[v])
    X['female'] = d.gender.astype(str).str.upper().str.startswith('F').astype(int)
    for v in ['mv', 'vaso', 'chf', 'ckd']:
        X[v] = pd.to_numeric(d[v], errors='coerce').fillna(0)
    med = X.median(); Z = (X.fillna(med) - med) / X.std().replace(0, 1)
    DUM = pd.DataFrame({'WetWarm': (d.quad == 'WetWarm').astype(int), 'DryCold': (d.quad == 'DryCold').astype(int),
                        'WetCold': (d.quad == 'WetCold').astype(int)}, index=d.index)
    y = d.died.values.astype(int)
    m1 = sm.Logit(y, sm.add_constant(Z[BASE])).fit(disp=0)
    X2 = sm.add_constant(pd.concat([Z[BASE], DUM], axis=1)); m2 = sm.Logit(y, X2).fit(disp=0)
    p1 = m1.predict(sm.add_constant(Z[BASE])).values; p2 = m2.predict(X2).values
    a1, a2 = auc(y, p1), auc(y, p2)
    boot = []
    for _ in range(500):
        b = np.random.choice(len(y), len(y), replace=True)
        if y[b].sum() < 5:
            continue
        boot.append(auc(y[b], p2[b]) - auc(y[b], p1[b]))
    boot = np.array(boot)
    ev, ne = y == 1, y == 0
    idi = (p2[ev].mean() - p1[ev].mean()) - (p2[ne].mean() - p1[ne].mean())
    r = {'dev_n': len(d), 'dev_deaths': int(y.sum()), 'dev_auc_routine': a1, 'dev_auc_pheno': a2,
         'dev_dauc': a2 - a1, 'dev_dauc_lo': np.percentile(boot, 2.5), 'dev_dauc_hi': np.percentile(boot, 97.5),
         'dev_idi': idi}
    for k in ['WetWarm', 'DryCold', 'WetCold']:
        co, se = m2.params[k], m2.bse[k]
        r['OR_' + k] = np.exp(co); r['OR_' + k + '_lo'] = np.exp(co - 1.96 * se); r['OR_' + k + '_hi'] = np.exp(co + 1.96 * se)
    # 时间验证：时代映射走 hosp/patients.csv（零缺失），不用另一课题的 mimic_T2.parquet
    from _ayg import attach_ayg, split_era
    d = attach_ayg(d.copy(), con=c)
    tr, te = split_era(d)

    def prep(x):
        Xx = pd.DataFrame(index=x.index)
        for v in CORE + ['age']:
            Xx[v] = num(x[v])
        Xx['female'] = x.gender.astype(str).str.upper().str.startswith('F').astype(int)
        for v in ['mv', 'vaso', 'chf', 'ckd']:
            Xx[v] = pd.to_numeric(x[v], errors='coerce').fillna(0)
        return Xx
    Xtr, Xte = prep(tr), prep(te)
    medt = Xtr.median(); Ztr = (Xtr.fillna(medt) - medt) / Xtr.std().replace(0, 1)
    Zte = (Xte.fillna(medt) - medt) / Xtr.std().replace(0, 1)
    Dtr = pd.DataFrame({'WetWarm': (tr.quad == 'WetWarm').astype(int), 'DryCold': (tr.quad == 'DryCold').astype(int),
                        'WetCold': (tr.quad == 'WetCold').astype(int)})
    Dte = pd.DataFrame({'WetWarm': (te.quad == 'WetWarm').astype(int), 'DryCold': (te.quad == 'DryCold').astype(int),
                        'WetCold': (te.quad == 'WetCold').astype(int)})
    mt = sm.Logit(tr.died.values.astype(int), sm.add_constant(pd.concat([Ztr[BASE], Dtr], axis=1))).fit(disp=0)
    pt = mt.predict(sm.add_constant(pd.concat([Zte[BASE], Dte], axis=1)))
    r['dev_temporal_auc'] = auc(te.died.values, pt)
    r['dev_temporal_n'] = len(te)
    r['_mm'] = d
    return r


# ---------------- 复现队列 ----------------
def eicu_set(feat_parquet):
    ee = c.execute(f"SELECT * FROM read_parquet('{feat_parquet}')").df().rename(columns={'admissionweight': 'adm_weight'})
    tc = pd.read_csv(D + '/eicu_temp_clean.csv')
    ee = ee.drop(columns=['temp_mean']).merge(tc, on='patientunitstayid', how='left').rename(columns={'temp_clean_c': 'temp_mean'})
    ee['cong_any'] = ((ee.edema_pos.fillna(0) == 1) | (ee.jvd_pos.fillna(0) == 1) | (ee.crackles.fillna(0) == 1)).astype(int)
    sub = ee[(ee[['edema_doc', 'jvd_doc', 'lungs_doc']].fillna(0).sum(axis=1) > 0) & (ee.perf_doc.fillna(0) == 1)].copy()
    sub['quad'] = np.where((sub.cong_any == 1) & (sub.hypoperf.fillna(0) == 1), 'WetCold',
                  np.where((sub.cong_any == 1) & (sub.hypoperf.fillna(0) == 0), 'WetWarm',
                  np.where((sub.cong_any == 0) & (sub.hypoperf.fillna(0) == 1), 'DryCold', 'DryWarm')))
    return sub


def ext_metrics(mm, sub):
    def frame(d, covs):
        X = pd.DataFrame(index=d.index)
        for v in covs:
            X[v] = num(d[v])
        X['female'] = pd.Series(d.gender).astype(str).str.upper().str.startswith('F').astype(int).values
        for k in ['WetWarm', 'DryCold', 'WetCold']:
            X[k] = (d['quad'] == k).astype(int)
        return X
    covs = TRANS18
    Xm, Xe = frame(mm, covs), frame(sub, covs)
    ok = Xe[covs].notna().mean(axis=1) >= 0.6
    medt = Xm.median(); sdt = Xm.std().replace(0, 1)
    Zm = (Xm.fillna(medt) - medt) / sdt
    Ze = ((Xe.fillna(medt) - medt) / sdt).loc[ok]
    fit = sm.Logit(mm.died.values.astype(int), sm.add_constant(Zm)).fit(disp=0)
    pe = fit.predict(sm.add_constant(Ze)).values
    ye = sub.died.values[ok.values].astype(int)
    z = np.log(np.clip(pe, 1e-9, 1 - 1e-9) / (1 - np.clip(pe, 1e-9, 1 - 1e-9)))
    rec = sm.Logit(ye, sm.add_constant(pd.Series(np.asarray(z).ravel(), index=range(len(ye))), has_constant='add')).fit(disp=0)
    pr = np.asarray(rec.params).ravel()
    return {'ext_n': int(len(ye)), 'ext_deaths': int(ye.sum()), 'ext_auc': auc(ye, pe),
            'ext_oe': ye.mean() / max(pe.mean(), 1e-9), 'ext_slope': float(pr[1]),
            'ext_intercept': float(pr[0]), 'ext_mean_pred': 100 * pe.mean(), 'ext_obs': 100 * ye.mean()}


print('=' * 78)
print('A. 开发队列（MIMIC-IV）')
res = {}
for tag, f in [('筛查后（主分析）', 'mimic_cp.parquet'), ('按原始记录值', 'mimic_cp_raw.parquet')]:
    d = build_dev(D + '/' + f)
    r = dev_metrics(d); res[tag] = r
    print('%-16s n=%d 死亡=%d | 常规 AUC=%.4f | 常规+表型 AUC=%.4f | ΔAUC=%+.4f (%+.4f, %+.4f) | IDI=%+.4f | 时间验证=%.3f'
          % (tag, r['dev_n'], r['dev_deaths'], r['dev_auc_routine'], r['dev_auc_pheno'], r['dev_dauc'],
             r['dev_dauc_lo'], r['dev_dauc_hi'], r['dev_idi'], r['dev_temporal_auc']))
    print('%-16s OR 湿暖=%.2f (%.2f-%.2f) 干冷=%.2f (%.2f-%.2f) 湿冷=%.2f (%.2f-%.2f)'
          % ('', r['OR_WetWarm'], r['OR_WetWarm_lo'], r['OR_WetWarm_hi'],
             r['OR_DryCold'], r['OR_DryCold_lo'], r['OR_DryCold_hi'],
             r['OR_WetCold'], r['OR_WetCold_lo'], r['OR_WetCold_hi']))

print('=' * 78)
print('B. 复现队列（eICU-CRD，18 变量迁移模型）')
mm = res['筛查后（主分析）']['_mm']
for tag, f in [('筛查后（主分析）', 'eicu_cp.parquet'), ('按原始记录值', 'eicu_cp_raw.parquet')]:
    sub = eicu_set(D + '/' + f)
    e = ext_metrics(mm, sub); res[tag].update(e)
    print('%-16s 四象限可判定 n=%d | 迁移模型 n=%d 死亡=%d | 外部 AUC=%.3f | O:E=%.2f | 斜率=%.3f 截距=%+.3f'
          % (tag, len(sub), e['ext_n'], e['ext_deaths'], e['ext_auc'], e['ext_oe'], e['ext_slope'], e['ext_intercept']))

# ---------------- 输出对照表 ----------------
rows = []
def add(label, key, fmt='%.4f', scale=1.0):
    rows.append({'指标': label, '筛查后（主分析）': fmt % (scale * res['筛查后（主分析）'][key]),
                 '按原始记录值（敏感性）': fmt % (scale * res['按原始记录值'][key]),
                 '绝对差': fmt % abs(scale * res['筛查后（主分析）'][key] - scale * res['按原始记录值'][key])})
add('开发队列常规模型 AUROC', 'dev_auc_routine', '%.3f')
add('开发队列常规+表型 AUROC', 'dev_auc_pheno', '%.3f')
add('ΔAUROC', 'dev_dauc', '%+.4f')
add('ΔAUROC 下限', 'dev_dauc_lo', '%+.4f')
add('ΔAUROC 上限', 'dev_dauc_hi', '%+.4f')
add('IDI', 'dev_idi', '%+.4f')
add('时间验证 AUROC', 'dev_temporal_auc', '%.3f')
add('调整 OR 湿暖型', 'OR_WetWarm', '%.3f')
add('调整 OR 干冷型', 'OR_DryCold', '%.3f')
add('调整 OR 湿冷型', 'OR_WetCold', '%.3f')
add('外部验证 AUROC（18 变量）', 'ext_auc', '%.3f')
add('外部校准斜率', 'ext_slope', '%.3f')
add('外部校准截距', 'ext_intercept', '%+.3f')
add('外部 O:E', 'ext_oe', '%.2f')
add('外部预测平均风险 %', 'ext_mean_pred', '%.2f')
df = pd.DataFrame(rows)
df.to_csv(OUT + '/sensitivity_raw_vs_screened.csv', index=False, encoding='utf-8-sig')
print('\n' + '=' * 78)
print(df.to_string(index=False))
json.dump({'screened': {k: v for k, v in res['筛查后（主分析）'].items() if not k.startswith('_')},
           'as_charted': {k: v for k, v in res['按原始记录值'].items() if not k.startswith('_')}},
          open(OUT + '/sensitivity_raw_vs_screened.json', 'w'), ensure_ascii=False, indent=1)
print('\n->', OUT + '/sensitivity_raw_vs_screened.csv')
