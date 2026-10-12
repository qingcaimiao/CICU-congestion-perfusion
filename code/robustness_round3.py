# -*- coding: utf-8 -*-
"""第三轮外部意见要求的稳健性分析。

A. 纳入 vs 排除者比较 + E-value
B. 灌注轴 vs 充血轴的正式差异检验（Wald 检验 + 配对 bootstrap 差值）
C. eICU「未记录 ≠ 无充血」：三字段记录率矩阵 + 敏感性分析
D. 留一医院外推（6 家医院）
E. 水肿切点（≥3）的稳定性：替代切点（≥2/≥4）+ 跨时间分层
"""
import duckdb, numpy as np, pandas as pd, json
import statsmodels.api as sm

np.random.seed(20261012)
c = duckdb.connect(); c.execute('PRAGMA threads=8')
D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
R = lambda p: "read_csv_auto('%s',header=true,strict_mode=false,ignore_errors=true)" % p

CORE = ['hr_min', 'hr_max', 'sbp_min', 'map_min', 'rr_max', 'spo2_min', 'adm_weight',
        'cr_max', 'bun_max', 'na_min', 'k_max', 'cl_min', 'hco3_min', 'hgb_min',
        'wbc_max', 'plt_min', 'glu_max']
BASE = CORE + ['age', 'female', 'mv', 'vaso', 'chf', 'ckd']
TRANS18 = ['age', 'hr_min', 'hr_max', 'sbp_min', 'map_min', 'rr_max', 'spo2_min', 'adm_weight',
           'cr_max', 'bun_max', 'na_min', 'k_max', 'cl_min', 'hco3_min', 'hgb_min',
           'wbc_max', 'plt_min', 'glu_max']
res = {}


def frame(d, covs):
    Xx = pd.DataFrame(index=d.index)
    for v in covs:
        Xx[v] = num(d[v])
    Xx['female'] = pd.Series(d.gender).astype(str).str.upper().str.startswith('F').astype(int).values
    for k in ['WetWarm', 'DryCold', 'WetCold']:
        Xx[k] = (d['quad'] == k).astype(int)
    return Xx



def num(s):
    return pd.to_numeric(pd.Series(s).astype(str).str.replace('>', '', regex=False).str.strip(), errors='coerce')


def auc(y, p):
    y = np.asarray(y).astype(int); r = pd.Series(p).rank().values
    n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def evalue(or_, lo=None):
    """E-value（OR 近似为 RR）"""
    def f(x):
        return x + np.sqrt(x * (x - 1)) if x >= 1 else 1.0
    out = {'point': round(float(f(or_)), 2)}
    if lo is not None:
        out['ci'] = round(float(f(lo)), 2) if lo >= 1 else 1.0
    return out


# ===================================================== A
print('=' * 96); print('A. 纳入 vs 排除者（MIMIC-IV，20,806 首诊心内 ICU 住院）')
q = f"""
WITH e AS (SELECT stay_id, max(CASE trim(lower(value)) WHEN 'none' THEN 0 WHEN '2 mm' THEN 1 WHEN '4 mm' THEN 2
     WHEN '6 mm' THEN 3 WHEN '8 mm' THEN 4 WHEN 'anasarca' THEN 5 END) ew
   FROM read_parquet('{D}/cp_exam_raw.parquet') WHERE itemid=224862 AND off_h>=-6 AND off_h<=24 GROUP BY 1),
cr AS (SELECT stay_id, max(CASE WHEN trim(lower(value)) LIKE 'abnormal%' THEN 1 ELSE 0 END) cr
   FROM read_parquet('{D}/cp_exam_raw.parquet') WHERE itemid IN (223951,224308) AND off_h>=-6 AND off_h<=24 GROUP BY 1)
SELECT m.*, e.ew, cr.cr FROM read_parquet('{D}/mimic_cp.parquet') m LEFT JOIN e USING(stay_id) LEFT JOIN cr USING(stay_id)"""
mm = c.execute(q).df()
mm['included'] = (mm.ew.notna() & mm.cr.notna()).astype(int)
rows = []
for v, lab in [('died', '院内死亡 n (%)'), ('age', '年龄 median'), ('los', 'ICU 住院时长 median'),
               ('hr_max', '心率最高 median'), ('cr_max', '肌酐最高 median'), ('bun_max', '尿素氮最高 median'),
               ('mv', '有创机械通气 n (%)'), ('vaso', '血管活性药 n (%)'),
               ('chf', '心衰 n (%)'), ('ckd', '慢性肾病 n (%)')]:
    g = [num(mm.loc[mm.included == k, v]) if v not in ('died', 'mv', 'vaso', 'chf', 'ckd')
         else pd.to_numeric(mm.loc[mm.included == k, v], errors='coerce') for k in (1, 0)]
    if v in ('died', 'mv', 'vaso', 'chf', 'ckd'):
        a, b = 100 * g[0].mean(), 100 * g[1].mean()
        txt = '%.1f vs %.1f' % (a, b)
    else:
        txt = '%.1f vs %.1f' % (g[0].median(), g[1].median())
    from scipy import stats as st
    p = st.mannwhitneyu(g[0].dropna(), g[1].dropna()).pvalue if v not in ('died', 'mv', 'vaso', 'chf', 'ckd') \
        else st.chi2_contingency(pd.crosstab(mm.included, mm[v]))[1]
    rows.append(dict(变量=lab, 纳入组='', 排除组='', 值=txt, p=('%.2e' % p)))
tA = pd.DataFrame(rows)
tA['纳入组'] = [x.split(' vs ')[0] for x in tA.值]
tA['排除组'] = [x.split(' vs ')[1] for x in tA.值]
tA = tA[['变量', '纳入组', '排除组', 'p']]
print('纳入 %d 例 / 排除 %d 例' % (mm.included.sum(), (1 - mm.included).sum()))
print(tA.to_string(index=False))
tA.to_csv(OUT + '/R3_tableA_included_vs_excluded.csv', index=False, encoding='utf-8-sig')
res['A_included'] = int(mm.included.sum()); res['A_excluded'] = int((1 - mm.included).sum())

print()
print('E-value（近似，OR 视为 RR）：')
main = {'湿冷型 OR 4.49': (4.49, 3.15), '干冷型 OR 3.20': (3.20, 2.53), '湿暖型 OR 1.63': (1.63, 1.26),
        '同尺度 CRT OR 3.11': (3.11, 2.53), '外部迁移模型湿冷 OR 4.56': (4.56, 3.20)}
ev = {k: evalue(*v) for k, v in main.items()}
for k, v in ev.items():
    print('  %-24s 点估计 E=%.2f  CI下限 E=%.2f' % (k, v['point'], v.get('ci', float('nan'))))
res['E_values'] = ev

# ===================================================== B
print(); print('=' * 96); print('B. 两轴效应差异的正式检验（MIMIC-IV）')
mm2 = c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()
mm2 = mm2.dropna(subset=['quad']).copy()
mm2['female'] = mm2.gender.astype(str).str.upper().str.startswith('F').astype(int)
X = pd.DataFrame(index=mm2.index)
for v in CORE + ['age']:
    X[v] = num(mm2[v])
X['female'] = mm2.female
for v in ['mv', 'vaso', 'chf', 'ckd']:
    X[v] = pd.to_numeric(mm2[v], errors='coerce').fillna(0)
med = X.median(); Z = (X.fillna(med) - med) / X.std().replace(0, 1)
Zb = Z[BASE]; y = mm2.died.values.astype(int)
perf = pd.to_numeric(mm2.cr_abn, errors='coerce').fillna(0).astype(int)
cong = (num(mm2.ew) >= 3).astype(int)
M = sm.Logit(y, sm.add_constant(pd.concat([Zb, pd.DataFrame({'CRT': perf, 'Oedema_ge3': cong})], axis=1))).fit(disp=0)
wald = M.wald_test('CRT = Oedema_ge3', scalar=True)
print('  同尺度模型：CRT OR=%.2f  水肿≥6mm OR=%.2f' % (np.exp(M.params['CRT']), np.exp(M.params['Oedema_ge3'])))
print('  Wald 检验 H0: β_CRT = β_oedema≥3 : chi2=%.2f, p=%.4f' % (float(np.atleast_1d(wald.statistic)[0]), float(wald.pvalue)))
b_ratio = np.exp(M.params['CRT'] - M.params['Oedema_ge3'])
lo = np.exp((M.params['CRT'] - M.params['Oedema_ge3']) - 1.96 * np.sqrt(M.bse['CRT'] ** 2 + M.bse['Oedema_ge3'] ** 2 - 2 * M.cov_params().loc['CRT', 'Oedema_ge3']))
hi = np.exp((M.params['CRT'] - M.params['Oedema_ge3']) + 1.96 * np.sqrt(M.bse['CRT'] ** 2 + M.bse['Oedema_ge3'] ** 2 - 2 * M.cov_params().loc['CRT', 'Oedema_ge3']))
print('  OR 比值 (CRT / 水肿) = %.2f (95%%CI %.2f–%.2f)' % (b_ratio, lo, hi))
res['B_wald'] = {'chi2': float(np.atleast_1d(wald.statistic)[0]), 'p': float(wald.pvalue),
                 'or_ratio': float(b_ratio), 'or_ratio_ci': [float(lo), float(hi)]}

# 配对 bootstrap：ΔAUROC(灌注) − ΔAUROC(充血)
def fit_p(Zb, extra):
    Xx = sm.add_constant(pd.concat([Zb, extra], axis=1)) if extra is not None and extra.shape[1] else sm.add_constant(Zb)
    m = sm.Logit(y, Xx).fit(disp=0)
    return m.predict(Xx).values
M0 = fit_p(Zb, None)
Mp = fit_p(Zb, pd.DataFrame({'CRT': perf}, index=mm2.index))
Mc = fit_p(Zb, pd.DataFrame({'Oed': cong}, index=mm2.index))
d_p, d_c = auc(y, Mp) - auc(y, M0), auc(y, Mc) - auc(y, M0)
idx = np.arange(len(y)); dif = []
for _ in range(2000):
    b = np.random.choice(idx, len(idx), replace=True)
    if y[b].sum() < 5:
        continue
    dif.append((auc(y[b], Mp[b]) - auc(y[b], M0[b])) - (auc(y[b], Mc[b]) - auc(y[b], M0[b])))
dif = np.array(dif)
print('  ΔAUC(灌注)=%+.4f  ΔAUC(充血)=%+.4f  差值=%+.4f (95%%CI %+.4f ~ %+.4f)' %
      (d_p, d_c, d_p - d_c, np.percentile(dif, 2.5), np.percentile(dif, 97.5)))
res['B_dauc_diff'] = {'perfusion': float(d_p), 'congestion': float(d_c), 'diff': float(d_p - d_c),
                      'ci': [float(np.percentile(dif, 2.5)), float(np.percentile(dif, 97.5))]}

# ===================================================== C
print(); print('=' * 96); print('C. eICU「未记录 ≠ 无充血」')
ee = c.execute(f"SELECT * FROM read_parquet('{D}/eicu_cp.parquet')").df()
ee['n_doc'] = ee[['edema_doc', 'jvd_doc', 'lungs_doc']].fillna(0).astype(int).sum(axis=1)
print('  27,757 例心内 ICU 住院中三个充血字段的记录个数分布：')
print(ee.n_doc.value_counts().sort_index().to_frame('n').T.to_string())
perf_ok = ee.perf_doc.fillna(0) == 1
print('  其中灌注也有记录者（现纳入条件）n=%d' % int((perf_ok & (ee.n_doc > 0)).sum()))
for k in [1, 2, 3]:
    s = perf_ok & (ee.n_doc == k)
    print('   充血字段记录数=%d：n=%d，院内死亡 %d (%.2f%%)' % (k, s.sum(), ee.loc[s, 'died'].sum(), 100 * ee.loc[s, 'died'].mean()))
sub_all = ee[perf_ok & (ee.n_doc == 3)].copy()
sub_any = ee[perf_ok & (ee.n_doc > 0)].copy()
def composite(s):
    s = s.copy()
    s['cong_any'] = ((s.edema_pos.fillna(0) == 1) | (s.jvd_pos.fillna(0) == 1) | (s.crackles.fillna(0) == 1)).astype(int)
    return s
try:
    from scipy import stats as st
    s3 = composite(sub_all)
    print('  敏感性：仅三字段全部有记录者 n=%d，死亡 %d (%.2f%%)' % (len(s3), s3.died.sum(), 100 * s3.died.mean()))
    for nm, mask in [('充血(+)', s3.cong_any == 1), ('充血(-)', s3.cong_any == 0)]:
        g = s3.loc[mask]
        print('     %s n=%d 死亡 %.2f%%' % (nm, len(g), 100 * g.died.mean()))
    tab = pd.crosstab(s3.cong_any, s3.died)
    print('     充血-死亡 chi2 p = %.3f' % st.chi2_contingency(tab)[1])
    res['C_all3'] = {'n': int(len(s3)), 'deaths': int(s3.died.sum()),
                     'mort_pos': float(100 * s3.loc[s3.cong_any == 1, 'died'].mean()),
                     'mort_neg': float(100 * s3.loc[s3.cong_any == 0, 'died'].mean())}
    # 全字段子集内的四象限、校正 OR 与 ΔAUROC（按同一可迁移协变量集）
    s3 = s3.rename(columns={'admissionweight': 'adm_weight'})
    s3['quad'] = np.where((s3.cong_any == 1) & (s3.hypoperf.fillna(0) == 1), 'WetCold',
                 np.where((s3.cong_any == 1) & (s3.hypoperf.fillna(0) == 0), 'WetWarm',
                 np.where((s3.cong_any == 0) & (s3.hypoperf.fillna(0) == 1), 'DryCold', 'DryWarm')))
    for q_, g_ in s3.groupby('quad'):
        print('     %-8s n=%4d 死亡 %5.2f%%' % (q_, len(g_), 100 * g_.died.mean()))
    Xm3 = frame(mm2, TRANS18)
    Xe3 = frame(s3, TRANS18)
    ok3 = Xe3[TRANS18].notna().mean(axis=1) >= 0.6
    s3, Xe3 = s3.loc[ok3], Xe3.loc[ok3]
    med3 = Xm3.median(); sd3 = Xm3.std().replace(0, 1)
    Zm3 = (Xm3.fillna(med3) - med3) / sd3
    Ze3 = (Xe3.fillna(med3) - med3) / sd3
    dead_cols = [cc for cc in Ze3.columns if Ze3[cc].std(skipna=True) == 0 or Ze3[cc].isna().all()]
    if dead_cols:
        print('     子集内删除零方差列:', dead_cols)
        Ze3 = Ze3.drop(columns=dead_cols)
    y3 = s3.died.values.astype(int)
    cg = pd.DataFrame({'Congestion': np.asarray(s3.cong_any.astype(int))}, index=s3.index)
    pf = pd.DataFrame({'Perfusion': np.asarray(s3.hypoperf.fillna(0).astype(int))}, index=s3.index)
    def fit3(extra):
        Xx = sm.add_constant(pd.concat([Ze3, extra], axis=1)) if extra is not None and extra.shape[1] else sm.add_constant(Ze3)
        mm3 = sm.Logit(y3, Xx).fit(disp=0); return mm3.predict(Xx).values, mm3
    q0, _ = fit3(None); qc, mc = fit3(cg); qp, _ = fit3(pf)
    print('     全字段子集（n=%d，死亡 %d）：仅充血 ΔAUROC=%+.4f（OR=%.2f, %.2f–%.2f）；仅灌注 ΔAUROC=%+.4f'
          % (len(y3), y3.sum(), auc(y3, qc) - auc(y3, q0), np.exp(mc.params['Congestion']),
             np.exp(mc.params['Congestion'] - 1.96 * mc.bse['Congestion']),
             np.exp(mc.params['Congestion'] + 1.96 * mc.bse['Congestion']), auc(y3, qp) - auc(y3, q0)))
    res['C_all3_constr'] = {'n': int(len(y3)), 'deaths': int(y3.sum()),
                            'dauc_cong': float(auc(y3, qc) - auc(y3, q0)),
                            'or_cong': float(np.exp(mc.params['Congestion'])),
                            'or_cong_ci': [float(np.exp(mc.params['Congestion'] - 1.96 * mc.bse['Congestion'])),
                                           float(np.exp(mc.params['Congestion'] + 1.96 * mc.bse['Congestion']))],
                            'dauc_perf': float(auc(y3, qp) - auc(y3, q0))}
except Exception as ex:
    print('  C 段异常:', ex)

# ===================================================== D
print(); print('=' * 96); print('D. 留一医院外推（eICU）')
sub = ee[perf_ok & (ee.n_doc > 0)].copy().rename(columns={'admissionweight': 'adm_weight'})
sub['cong_any'] = ((sub.edema_pos.fillna(0) == 1) | (sub.jvd_pos.fillna(0) == 1) | (sub.crackles.fillna(0) == 1)).astype(int)
sub['quad'] = np.where((sub.cong_any == 1) & (sub.hypoperf.fillna(0) == 1), 'WetCold',
              np.where((sub.cong_any == 1) & (sub.hypoperf.fillna(0) == 0), 'WetWarm',
              np.where((sub.cong_any == 0) & (sub.hypoperf.fillna(0) == 1), 'DryCold', 'DryWarm')))
Xm = frame(mm2, TRANS18)
Xe = frame(sub, TRANS18)
ok = Xe[TRANS18].notna().mean(axis=1) >= 0.6
sub = sub.loc[ok]; Xe = Xe.loc[ok]
medt = Xm.median(); sdt = Xm.std().replace(0, 1)
Zm = (Xm.fillna(medt) - medt) / sdt
Ze = (Xe.fillna(medt) - medt) / sdt
fit = sm.Logit(mm2.died.values.astype(int), sm.add_constant(Zm)).fit(disp=0)
pe = fit.predict(sm.add_constant(Ze)).values
ye = sub.died.values.astype(int)
print('  全队列 n=%d 死亡=%d 外部 AUC=%.3f' % (len(ye), ye.sum(), auc(ye, pe)))
print('  各医院 n / 死亡 / AUC：')
loos = []
for h, g in sub.groupby('hospitalid'):
    ii = sub.index.get_indexer(g.index)
    print('    hospital %-6s n=%5d  死亡=%3d  AUC=%s' % (h, len(g), int(ye[ii].sum()),
          ('%.3f' % auc(ye[ii], pe[ii])) if ye[ii].sum() >= 5 and (1 - ye[ii]).sum() >= 5 else '—'))
    keep = np.setdiff1d(np.arange(len(ye)), ii)
    loos.append(auc(ye[keep], pe[keep]))
print('  留一医院外推 AUC 范围: %.3f – %.3f（中位 %.3f）' % (min(loos), max(loos), float(np.median(loos))))
res['D_loo'] = {'full': float(auc(ye, pe)), 'min': float(min(loos)), 'max': float(max(loos)),
                'median': float(np.median(loos)),
                'hospitals': {int(h): int(g.died.sum()) for h, g in sub.groupby('hospitalid')}}

# ===================================================== E
print(); print('=' * 96); print('E. 水肿切点稳定性与替代切点')
def pheno_dauc(cut):
    ph = np.where((num(mm2.ew).fillna(0) >= cut) & (perf == 1), 'WetCold',
         np.where((num(mm2.ew).fillna(0) >= cut) & (perf == 0), 'WetWarm',
         np.where((num(mm2.ew).fillna(0) < cut) & (perf == 1), 'DryCold', 'DryWarm')))
    DUM = pd.DataFrame({'WetWarm': (ph == 'WetWarm').astype(int), 'DryCold': (ph == 'DryCold').astype(int),
                        'WetCold': (ph == 'WetCold').astype(int)}, index=mm2.index)
    p2 = fit_p(Zb, DUM)
    ww = float(np.exp(sm.Logit(y, sm.add_constant(pd.concat([Zb, DUM], axis=1))).fit(disp=0).params['WetWarm']))
    return auc(y, p2) - auc(y, M0), ww, int((ph == 'WetWarm').sum())
rows = []
for cut in [2, 3, 4]:
    d_, ww, nww = pheno_dauc(cut)
    rows.append({'切点': '水肿 ≥%d 级' % cut, 'ΔAUROC': '%+.4f' % d_, '湿暖型 OR': '%.2f' % ww, '湿暖型 n': nww})
tE = pd.DataFrame(rows); print(tE.to_string(index=False))
tE.to_csv(OUT + '/R3_tableE_cutpoint.csv', index=False, encoding='utf-8-sig')
# 跨时间分层：各 anchor_year_group 内 grade>=3 的死亡率差
tt = c.execute(f"SELECT stay_id, anchor_year_group FROM read_parquet('{D}/mimic_T2.parquet')").df()
mm2['ayg'] = mm2.stay_id.map(tt.set_index('stay_id')['anchor_year_group'].to_dict())
print('  跨时间分层（各时段内：水肿≥6mm vs <6mm 的院内死亡率）')
rows = []
for g, s in mm2.dropna(subset=['ayg']).groupby('ayg'):
    if len(s) < 400:
        continue
    hi = s[num(s.ew) >= 3]; lo2 = s[num(s.ew) < 3]
    rows.append({'时段': g, 'n': len(s), '≥6mm 死亡%': '%.2f' % (100 * hi.died.mean()), '≥6mm n': len(hi),
                 '<6mm 死亡%': '%.2f' % (100 * lo2.died.mean()), '差(pp)': '%+.2f' % (100 * (hi.died.mean() - lo2.died.mean()))})
tTi = pd.DataFrame(rows); print(tTi.to_string(index=False))
tTi.to_csv(OUT + '/R3_tableE_time.csv', index=False, encoding='utf-8-sig')

json.dump(res, open(OUT + '/R3_robustness.json', 'w'), ensure_ascii=False, indent=1, default=str)
print('\n-> R3_tableA/E/时间表 + R3_robustness.json')
