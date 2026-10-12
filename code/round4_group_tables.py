# -*- coding: utf-8 -*-
"""第四轮修正：把水肿等级 / CRT / eICU 充血定义三层表统一到正确分母与院内死亡口径"""
import duckdb, numpy as np, pandas as pd, json
from scipy import stats
c = duckdb.connect(); c.execute('PRAGMA threads=8')
D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    den = 1 + z * z / n
    ctr = (p + z * z / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (round(100 * max(0.0, ctr - half), 2), round(100 * min(1.0, ctr + half), 2))


res = {}

# ================= 1. MIMIC 分析集（n = 12,052）内 =================
mm = c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()
assert len(mm) == 12052, len(mm)
ew = pd.to_numeric(pd.Series(mm.ew).astype(str).str.replace('>', '', regex=False).str.strip(), errors='coerce')
cr = pd.to_numeric(mm.cr_abn, errors='coerce')

rows = []
for g in range(6):
    s = mm[ew == g]
    k, n = int(s.died.sum()), len(s)
    lo, hi = wilson(k, n)
    rows.append(dict(grade=g, n=n, deaths=k, pct=round(100 * k / n, 2), ci_low=lo, ci_high=hi))
ed = pd.DataFrame(rows)
ed.to_csv(OUT + '/T_edema_mimic.csv', index=False)
chi2, p_ed, _, _ = stats.chi2_contingency(pd.crosstab(ew[ew.notna()], mm.died[ew.notna()]))
print('== MIMIC 分析集 水肿等级 ==')
print(ed.to_string(index=False))
print('  合计 n=%d deaths=%d  趋势 p=%.2e' % (ed.n.sum(), ed.deaths.sum(), p_ed))

rows = []
for v in [0, 1]:
    s = mm[cr == v]
    k, n = int(s.died.sum()), len(s)
    lo, hi = wilson(k, n)
    rows.append(dict(cr_abn=v, n=n, deaths=k, pct=round(100 * k / n, 2), ci_low=lo, ci_high=hi))
crt = pd.DataFrame(rows)
crt.to_csv(OUT + '/T_cr_mimic.csv', index=False)
chi2b, p_cr, _, _ = stats.chi2_contingency(pd.crosstab(cr[cr.notna()], mm.died[cr.notna()]))
print('\n== MIMIC 分析集 CRT ==')
print(crt.to_string(index=False))
print('  比值 = %.2f   p=%.2e' % (crt.pct[1] / crt.pct[0], p_cr))
print('  正常者死亡 %d/%d = %.2f%%；延长者 %d/%d = %.2f%%'
      % (crt.deaths[0], crt.n[0], crt.pct[0], crt.deaths[1], crt.n[1], crt.pct[1]))

# 四象限（MIMIC）带 CI
q = mm.groupby('quad').agg(n=('died', 'size'), deaths=('died', 'sum')).reindex(['DryWarm', 'WetWarm', 'DryCold', 'WetCold'])
q['pct'] = (100 * q.deaths / q.n).round(2)
q[['ci_low', 'ci_high']] = [wilson(int(r.deaths), int(r.n)) for r in q.itertuples()]
q.to_csv(OUT + '/T_quadrant_mimic_ci.csv')
print('\n== MIMIC 四象限（含 95% CI）=='); print(q.to_string())

# ================= 2. eICU：四种充血定义 × 四格 =================
ee = c.execute(f"SELECT * FROM read_parquet('{D}/eicu_cp.parquet')").df()
N = len(ee)
doc_ed = ee.edema_doc.fillna(0).astype(int)
doc_jv = ee.jvd_doc.fillna(0).astype(int)
doc_lu = ee.lungs_doc.fillna(0).astype(int)
doc_pf = ee.perf_doc.fillna(0).astype(int)
n_any = int(((doc_ed + doc_jv + doc_lu) > 0).sum())
n_all3 = int(((doc_ed + doc_jv + doc_lu) == 3).sum())
docrate = dict(n=N, edema=round(100 * doc_ed.mean(), 1), jvd=round(100 * doc_jv.mean(), 1),
               crackles=round(100 * doc_lu.mean(), 1), perfusion=round(100 * doc_pf.mean(), 1),
               any_congestion_field=round(100 * n_any / N, 1), any_congestion_field_n=n_any,
               all_three_fields=round(100 * n_all3 / N, 1), all_three_fields_n=n_all3,
               no_congestion_field=int(N - n_any))
json.dump(docrate, open(OUT + '/eicu_documentation_rates.json', 'w'), indent=1)
print('\n== eICU 记录率 =='); print(json.dumps(docrate, indent=1))

ee['cong_any'] = ((ee.edema_pos.fillna(0) == 1) | (ee.jvd_pos.fillna(0) == 1) | (ee.crackles.fillna(0) == 1)).astype(int)
DEFS = [('Composite (any of the three)', 'cong_any', (doc_ed + doc_jv + doc_lu) > 0),
        ('Jugular venous distension only', 'jvd_pos', doc_jv == 1),
        ('Peripheral oedema only', 'edema_pos', doc_ed == 1),
        ('Pulmonary crackles only', 'crackles', doc_lu == 1)]

full, summ = [], []
for lab, col, base in DEFS:
    d = ee[base & (doc_pf == 1)].copy()
    d['q'] = np.where((d[col].fillna(0) == 1) & (d.hypoperf.fillna(0) == 1), 'WetCold',
             np.where((d[col].fillna(0) == 1) & (d.hypoperf.fillna(0) == 0), 'WetWarm',
             np.where((d[col].fillna(0) == 0) & (d.hypoperf.fillna(0) == 1), 'DryCold', 'DryWarm')))
    t = d.groupby('q').agg(n=('died', 'size'), deaths=('died', 'sum')).reindex(['DryWarm', 'WetWarm', 'DryCold', 'WetCold'])
    t['mortality'] = (100 * t.deaths / t.n).round(2)
    for cell in t.index:
        lo, hi = wilson(int(t.loc[cell, 'deaths']), int(t.loc[cell, 'n']))
        full.append(dict(definition=lab, cell=cell, n=int(t.loc[cell, 'n']), deaths=int(t.loc[cell, 'deaths']),
                         mortality=float(t.loc[cell, 'mortality']), ci_low=lo, ci_high=hi))
    ww, dw = t.loc['WetWarm', 'mortality'], t.loc['DryWarm', 'mortality']
    dc = t.loc['DryCold', 'mortality']
    summ.append(dict(definition=lab, n=int(t.n.sum()), deaths=int(t.deaths.sum()),
                     dry_warm=float(dw), wet_warm=float(ww), dry_cold=float(dc),
                     wet_cold=float(t.loc['WetCold', 'mortality']),
                     wet_minus_dry_warm=round(ww - dw, 2), dry_cold_minus_dry_warm=round(dc - dw, 2)))
    print('  [%s] n=%d deaths=%d | DW %.2f WW %.2f DC %.2f WC %.2f | WW-DW %+.2f | DC-DW %+.2f'
          % (lab, t.n.sum(), t.deaths.sum(), dw, ww, dc, t.loc['WetCold', 'mortality'], ww - dw, dc - dw))

pd.DataFrame(full).to_csv(OUT + '/TableS3_eicu_definitions_full.csv', index=False)
sm = pd.DataFrame(summ)
sm.to_csv(OUT + '/TableS3_final.csv', index=False)
print('\n== Table S3（院内死亡口径，已重算）=='); print(sm.to_string(index=False))

# 单体征表（阳性/阴性）
rows = []
for pos, doc, lab in [('edema_pos', 'edema_doc', 'Peripheral oedema only'),
                      ('jvd_pos', 'jvd_doc', 'Jugular venous distension only'),
                      ('crackles', 'lungs_doc', 'Pulmonary crackles only'),
                      ('hypoperf', 'perf_doc', 'Impaired peripheral perfusion')]:
    d = ee[ee[doc].fillna(0) == 1]
    a, b = d[d[pos].fillna(0) == 1], d[d[pos].fillna(0) == 0]
    rows.append({'definition': lab, 'n_pos': int(len(a)), 'mort_pos': round(100 * a.died.mean(), 2),
                 'n_neg': int(len(b)), 'mort_neg': round(100 * b.died.mean(), 2),
                 'n_documented': int(len(d)), 'doc_pct_of_cohort': round(100 * len(d) / N, 1),
                 'ratio': round(a.died.mean() / max(b.died.mean(), 1e-9), 2)})
ss = pd.DataFrame(rows); ss.to_csv(OUT + '/T_eicu_single_sign.csv', index=False)
print('\n== eICU 单体征（阳性 vs 阴性）=='); print(ss.to_string(index=False))

# ================= 3. eICU 四格（复合定义）带 CI，供正文/表 4 用 =================
t4 = pd.DataFrame(full)
t4c = t4[t4.definition == 'Composite (any of the three)'].copy()
t4c.to_csv(OUT + '/Table4_eicu_replication.csv', index=False)
print('\n== Table 4（复合定义，含 CI）=='); print(t4c.to_string(index=False))
print('\nDONE')
