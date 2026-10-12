# -*- coding: utf-8 -*-
"""C 段扩展：eICU 中「三个充血字段全部有记录」子集内，充血轴是否仍有信号。

（独立脚本，避免与主稳健性脚本的作用域互相污染）
"""
import duckdb, numpy as np, pandas as pd, json, statsmodels.api as sm

c = duckdb.connect(); c.execute('PRAGMA threads=8')
D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
TRANS18 = ['age', 'hr_min', 'hr_max', 'sbp_min', 'map_min', 'rr_max', 'spo2_min', 'adm_weight',
           'cr_max', 'bun_max', 'na_min', 'k_max', 'cl_min', 'hco3_min', 'hgb_min',
           'wbc_max', 'plt_min', 'glu_max']
num = lambda s: pd.to_numeric(pd.Series(s).astype(str).str.replace('>', '', regex=False).str.strip(), errors='coerce')


def auc(y, p):
    y = np.asarray(y).astype(int); r = pd.Series(p).rank().values
    n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def boot_ci(y, p_new, p_old, n=2000):
    idx = np.arange(len(y)); d = []
    for _ in range(n):
        b = np.random.choice(idx, len(idx), replace=True)
        if y[b].sum() < 5:
            continue
        d.append(auc(y[b], p_new[b]) - auc(y[b], p_old[b]))
    d = np.array(d)
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


mm = c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df().dropna(subset=['quad']).copy()
ee = c.execute(f"SELECT * FROM read_parquet('{D}/eicu_cp.parquet')").df().rename(columns={'admissionweight': 'adm_weight'})
ee['n_doc'] = ee[['edema_doc', 'jvd_doc', 'lungs_doc']].fillna(0).astype(int).sum(axis=1)
ee['cong_any'] = ((ee.edema_pos.fillna(0) == 1) | (ee.jvd_pos.fillna(0) == 1) | (ee.crackles.fillna(0) == 1)).astype(int)
ee['hypo'] = ee.hypoperf.fillna(0).astype(int)


def frame(d):
    X = pd.DataFrame(index=d.index)
    for v in TRANS18:
        X[v] = num(d[v])
    X['female'] = pd.Series(d.gender).astype(str).str.upper().str.startswith('F').astype(int).values
    return X


def run(sub, tag):
    sub = sub.copy()
    sub['quad'] = np.where((sub.cong_any == 1) & (sub.hypo == 1), 'WetCold',
                  np.where((sub.cong_any == 1) & (sub.hypo == 0), 'WetWarm',
                  np.where((sub.cong_any == 0) & (sub.hypo == 1), 'DryCold', 'DryWarm')))
    Xm, Xe = frame(mm), frame(sub)
    ok = Xe[TRANS18].notna().mean(axis=1) >= 0.6
    Xe, sub = Xe.loc[ok], sub.loc[ok]
    med, sd = Xm.median(), Xm.std().replace(0, 1)
    Ze = (Xe.fillna(med) - med) / sd
    y = sub.died.values.astype(int)
    X0 = sm.add_constant(Ze)
    m0 = sm.Logit(y, X0).fit(disp=0); p0 = m0.predict(X0).values
    out = {'tag': tag, 'n': int(len(y)), 'deaths': int(y.sum()), 'auc_base': round(float(auc(y, p0)), 4)}
    for nm, vec in [('congestion', np.asarray(sub.cong_any)), ('perfusion', np.asarray(sub.hypo))]:
        Xa = sm.add_constant(pd.concat([Ze.reset_index(drop=True),
                                        pd.DataFrame({nm: vec})], axis=1))
        ma = sm.Logit(y, Xa).fit(disp=0); pa = ma.predict(Xa).values
        b, se = float(ma.params[nm]), float(ma.bse[nm])
        out[nm] = {'auc': round(float(auc(y, pa)), 4), 'dauc': round(float(auc(y, pa) - auc(y, p0)), 4),
                   'dauc_ci': [round(x, 4) for x in boot_ci(y, pa, p0)],
                   'or': round(float(np.exp(b)), 2),
                   'or_ci': [round(float(np.exp(b - 1.96 * se)), 2), round(float(np.exp(b + 1.96 * se)), 2)],
                   'p': round(float(ma.pvalues[nm]), 4)}
        print('  [%s] %-11s ΔAUROC=%+.4f (95%%CI %+.4f~%+.4f)  OR=%.2f (%.2f–%.2f)  p=%.4f'
              % (tag, nm, out[nm]['dauc'], out[nm]['dauc_ci'][0], out[nm]['dauc_ci'][1],
                 out[nm]['or'], out[nm]['or_ci'][0], out[nm]['or_ci'][1], out[nm]['p']))
    for q_ in ['DryWarm', 'WetWarm', 'DryCold', 'WetCold']:
        g = sub[sub.quad == q_]
        print('     %-8s n=%4d 死亡 %5.2f%%' % (q_, len(g), 100 * g.died.mean()))
        out['quad_' + q_] = {'n': int(len(g)), 'mort': round(float(100 * g.died.mean()), 2)}
    return out


print('=' * 90)
print('C1. 预先设定的主口径：三个充血字段中至少一个被记录（n 约 1,555）')
r1 = run(ee[(ee.perf_doc.fillna(0) == 1) & (ee.n_doc > 0)], 'any-field')
print()
print('=' * 90)
print('C2. 敏感性分析：三个充血字段全部有记录（消除"未记录 = 无充血"错分）')
r2 = run(ee[(ee.perf_doc.fillna(0) == 1) & (ee.n_doc == 3)], 'all-three-fields')
print()
print('文档完整度分布（27,757 例心内 ICU 住院中，三个充血字段被记录的个数）：')
print(ee.n_doc.value_counts().sort_index().rename_axis('fields_documented').to_frame('n').T.to_string())
json.dump({'any_field': r1, 'all_three': r2}, open(OUT + '/R3_robustness_C.json', 'w'), ensure_ascii=False, indent=1)
print('\n-> R3_robustness_C.json')
