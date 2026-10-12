# -*- coding: utf-8 -*-
"""充血轴 vs 灌注轴：各自对判别力的增量贡献（回答"卖点是否受影响"）

MIMIC-IV（开发队列，四象限可判定集）内部比较 4 个嵌套模型：
  M0 常规 23 变量
  M1 M0 + 灌注轴（CRT 延长）
  M2 M0 + 充血轴（水肿等级，每级 或 ≥3 级二分化）
  M3 M0 + 两轴（= 四象限表型）
eICU-CRD（复现队列）同样内部比较，充血用复合定义（任一水肿/JVD/啰音），灌注用 perfusion 字段。
另给出 eICU 外部迁移模型里两轴的系数与 ΔAUC。
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


def delong_ci(y, p_old, p_new, n=2000):
    idx = np.arange(len(y)); d = []
    for _ in range(n):
        b = np.random.choice(idx, len(idx), replace=True)
        if y[b].sum() < 5:
            continue
        d.append(auc(y[b], p_new[b]) - auc(y[b], p_old[b]))
    d = np.array(d)
    return np.percentile(d, 2.5), np.percentile(d, 97.5)


def fit_report(y, Z, extra, label, ref_p=None, rows=None):
    X = sm.add_constant(pd.concat([Z, extra], axis=1)) if extra is not None and extra.shape[1] else sm.add_constant(Z)
    m = sm.Logit(y, X).fit(disp=0)
    p = m.predict(X).values
    a = auc(y, p)
    line = {'model': label, 'n_par': X.shape[1] - 1, 'auc': a}
    if ref_p is not None:
        lo, hi = delong_ci(y, ref_p, p)
        line['dauc'] = a - auc(y, ref_p); line['dauc_lo'] = lo; line['dauc_hi'] = hi
    for k in (extra.columns if extra is not None else []):
        co, se = m.params[k], m.bse[k]
        line['OR_' + k] = float(np.exp(co)); line['OR_' + k + '_lo'] = float(np.exp(co - 1.96 * se))
        line['OR_' + k + '_hi'] = float(np.exp(co + 1.96 * se)); line['p_' + k] = float(m.pvalues[k])
    return line, p, m


# ================= MIMIC-IV =================
print('=' * 92)
print('A. MIMIC-IV 开发队列：两轴各自的增量判别力（n = 12,052，死亡 758）')
mm = c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()
mm['female'] = mm.gender.astype(str).str.upper().str.startswith('F').astype(int)
X = pd.DataFrame(index=mm.index)
for v in CORE + ['age']:
    X[v] = num(mm[v])
X['female'] = mm.female
for v in ['mv', 'vaso', 'chf', 'ckd']:
    X[v] = pd.to_numeric(mm[v], errors='coerce').fillna(0)
med = X.median(); Z = (X.fillna(med) - med) / X.std().replace(0, 1)
Zb = Z[BASE]
y = mm.died.values.astype(int)

perf = pd.DataFrame({'CRT_prolonged': pd.to_numeric(mm.cr_abn, errors='coerce').fillna(0).astype(int)}, index=mm.index)
cong_g = pd.DataFrame({'Oedema_grade': num(mm.ew).fillna(num(mm.ew).median()), 'Oedema_ge3': (num(mm.ew) >= 3).astype(int)}, index=mm.index)
both = pd.DataFrame({'WetWarm': (mm.quad == 'WetWarm').astype(int), 'DryCold': (mm.quad == 'DryCold').astype(int),
                     'WetCold': (mm.quad == 'WetCold').astype(int)}, index=mm.index)

rows = []
l0, p0, _ = fit_report(y, Zb, None, 'M0 常规变量（23）')
rows.append(l0)
l1, p1, _ = fit_report(y, Zb, perf, 'M1 常规 + 灌注（CRT）', p0)
rows.append(l1)
l2, p2, _ = fit_report(y, Zb, cong_g[['Oedema_ge3']], 'M2 常规 + 充血（水肿≥6mm）', p0)
rows.append(l2)
l2b, p2b, _ = fit_report(y, Zb, cong_g[['Oedema_grade']], 'M2b 常规 + 充血（水肿每级）', p0)
rows.append(l2b)
l3, p3, _ = fit_report(y, Zb, both, 'M3 常规 + 四象限表型', p0)
rows.append(l3)
# 增量：灌注之上再加充血
l4, p4, _ = fit_report(y, Zb, pd.concat([perf, cong_g[['Oedema_ge3']].rename(columns={'Oedema_ge3': 'Oedema_ge3_on_perf'})], axis=1),
                       'M4 常规 + 灌注 + 充血（同尺度）', p1)
rows.append(l4)
t = pd.DataFrame(rows)
cols = ['model', 'n_par', 'auc', 'dauc', 'dauc_lo', 'dauc_hi', 'OR_CRT_prolonged', 'OR_Oedema_ge3', 'OR_Oedema_grade']
print(t[[x for x in cols if x in t.columns]].round(4).to_string(index=False))
print('\n关键：M1（仅灌注）ΔAUC = %+.4f；M2（仅充血）ΔAUC = %+.4f；M3（两轴）ΔAUC = %+.4f'
      % (l1['dauc'], l2['dauc'], l3['dauc']))

# ================= eICU =================
print('=' * 92)
print('B. eICU-CRD 复现队列（内部拟合，探索性）：两轴各自的增量判别力')
ee = c.execute(f"SELECT * FROM read_parquet('{D}/eicu_cp.parquet')").df().rename(columns={'admissionweight': 'adm_weight'})
tc = pd.read_csv(D + '/eicu_temp_clean.csv')
ee = ee.drop(columns=['temp_mean']).merge(tc, on='patientunitstayid', how='left').rename(columns={'temp_clean_c': 'temp_mean'})
ee['cong_any'] = ((ee.edema_pos.fillna(0) == 1) | (ee.jvd_pos.fillna(0) == 1) | (ee.crackles.fillna(0) == 1)).astype(int)
sub = ee[(ee[['edema_doc', 'jvd_doc', 'lungs_doc']].fillna(0).sum(axis=1) > 0) & (ee.perf_doc.fillna(0) == 1)].copy()
sub['quad'] = np.where((sub.cong_any == 1) & (sub.hypoperf.fillna(0) == 1), 'WetCold',
              np.where((sub.cong_any == 1) & (sub.hypoperf.fillna(0) == 0), 'WetWarm',
              np.where((sub.cong_any == 0) & (sub.hypoperf.fillna(0) == 1), 'DryCold', 'DryWarm')))
Xe = pd.DataFrame(index=sub.index)
for v in TRANS18:
    Xe[v] = num(sub[v])
Xe['female'] = pd.Series(sub.gender).astype(str).str.upper().str.startswith('F').astype(int).values
ok = Xe[TRANS18].notna().mean(axis=1) >= 0.6
Xe = Xe.loc[ok]; sub = sub.loc[ok]
medt = Xe[TRANS18].median(); ZE = (Xe[TRANS18].fillna(medt) - medt) / Xe[TRANS18].std().replace(0, 1)
ZE['female'] = Xe['female']
ye = sub.died.values.astype(int)
print('   分析集 n = %d，死亡 %d' % (len(sub), ye.sum()))
pe = pd.DataFrame({'Perfusion': sub.hypoperf.fillna(0).astype(int)}, index=sub.index)
ce_ = pd.DataFrame({'Congestion': sub.cong_any.astype(int)}, index=sub.index)
bo = pd.DataFrame({'WetWarm': (sub.quad == 'WetWarm').astype(int), 'DryCold': (sub.quad == 'DryCold').astype(int),
                   'WetCold': (sub.quad == 'WetCold').astype(int)}, index=sub.index)
re = []
r0, q0, _ = fit_report(ye, ZE, None, 'R0 eICU 常规变量（18）'); re.append(r0)
r1, q1, _ = fit_report(ye, ZE, pe, 'R1 eICU + 灌注', q0); re.append(r1)
r2, q2, _ = fit_report(ye, ZE, ce_, 'R2 eICU + 充血（复合）', q0); re.append(r2)
r3, q3, _ = fit_report(ye, ZE, bo, 'R3 eICU + 四象限', q0); re.append(r3)
r4, q4, _ = fit_report(ye, ZE, pd.concat([pe, ce_], axis=1), 'R4 eICU + 灌注 + 充血', q0); re.append(r4)
te = pd.DataFrame(re)
cc = ['model', 'n_par', 'auc', 'dauc', 'dauc_lo', 'dauc_hi', 'OR_Perfusion', 'OR_Congestion', 'OR_WetWarm', 'OR_DryCold', 'OR_WetCold']
print(te[[x for x in cc if x in te.columns]].round(4).to_string(index=False))

t.to_csv(OUT + '/axis_contribution_mimic.csv', index=False)
te.to_csv(OUT + '/axis_contribution_eicu.csv', index=False)
json.dump({'mimic': {'m1_auc': float(l1['auc']), 'm1_dauc': float(l1['dauc']), 'm2_dauc': float(l2['dauc']),
                     'm3_dauc': float(l3['dauc']), 'm4_dauc_on_perf': float(l4['dauc'])},
           'eicu': {'r1_dauc': float(r1['dauc']), 'r2_dauc': float(r2['dauc']), 'r3_dauc': float(r3['dauc'])}},
          open(OUT + '/axis_contribution.json', 'w'), ensure_ascii=False, indent=1)
print('\n->', OUT + '/axis_contribution_mimic.csv / axis_contribution_eicu.csv')
