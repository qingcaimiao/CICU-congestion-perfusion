# -*- coding: utf-8 -*-
"""生成补充表 S7：预设定生理合理区间、被剔除的数值，以及"筛查后 vs 按原始记录值"的敏感性对照。"""
import pandas as pd, numpy as np, io

RES = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'

# itemid → 变量（与窗口定义一致）
SPEC = [
    # (label_en, unit, low, high, mimic_keys, eicu_keys)
    ('Heart rate', '/min', 20, 300, ['hr'], ['hr']),
    ('Respiratory rate', '/min', 1, 80, ['rr'], ['rr']),
    ('Oxygen saturation', '%', 1, 100, ['spo2'], ['spo2']),
    ('Systolic blood pressure', 'mmHg', 20, 300, ['sbp'], ['sbp(arterial)', 'sbp(nurseCharting)']),
    ('Mean arterial pressure', 'mmHg', 20, 250, ['map'], ['map(arterial)', 'map(nurseCharting)']),
    ('Temperature', '°C', 25, 45, ['temp'], ['temp']),
    ('Body weight', 'kg', 20, 400, ['weight'], []),
    ('Creatinine (max)', 'mg/dL', 0.05, 50, ['cr'], ['cr']),
    ('Urea nitrogen (max)', 'mg/dL', 0.5, 300, ['bun'], ['bun', 'urea']),
    ('Sodium (min)', 'mmol/L', 80, 200, ['na'], ['na']),
    ('Potassium (max)', 'mmol/L', 1, 15, ['k'], ['k']),
    ('Chloride (min)', 'mmol/L', 50, 160, ['cl'], ['cl']),
    ('Bicarbonate (min)', 'mmol/L', 1, 60, ['hco3'], ['hco3']),
    ('Haemoglobin (min)', 'g/dL', 1, 25, ['hgb'], ['hgb', 'hgb(alt)']),
    ('White cell count (max)', 'K/µL', 0.1, 500, ['wbc'], ['wbc', 'wbc(alt)']),
    ('Platelet count (min)', 'K/µL', 1, 3000, ['plt'], ['plt']),
    ('Glucose (max)', 'mg/dL', 10, 4000, ['glu'], ['glu']),
    ('Lactate (max)', 'mmol/L', 0.1, 40, ['lac'], ['lac']),
]
# 变量键 → 受影响例数（screening_counts_*.csv 的 variable 列）
STAY_KEY = {'hr': ['hr_min', 'hr_max'], 'rr': ['rr_max'], 'spo2': ['spo2_min'], 'sbp': ['sbp_min'],
            'map': ['map_min'], 'temp': ['temp_mean'], 'weight': ['adm_weight', 'admissionweight'],
            'cr': ['cr_max'], 'bun': ['bun_max'], 'na': ['na_min'], 'k': ['k_max'], 'cl': ['cl_min'],
            'hco3': ['hco3_min'], 'hgb': ['hgb_min'], 'wbc': ['wbc_max'], 'plt': ['plt_min'],
            'glu': ['glu_max'], 'lac': ['lac_max']}

rm = pd.read_csv(RES + '/screening_records_mimic.csv').rename(
    columns={'变量': 'variable', '记录数': 'records', '越界记录': 'out_of_range', '越界占比': 'pct'})
# 体温需先做华氏换算再判窗，内联脚本按原始单位统计有误，此处用修正值 135/190,413
rm.loc[rm.variable == 'temp', 'out_of_range'] = 135
rm.loc[rm.variable == 'temp', 'pct'] = round(100 * 135 / 190413, 4)
rm.loc[rm.variable == 'bili', ['records', 'out_of_range']] = [np.nan, np.nan]
re_ = pd.read_csv(RES + '/screening_records_eicu.csv')
cm = pd.read_csv(RES + '/screening_counts_mimic.csv')
ce = pd.read_csv(RES + '/screening_counts_eicu.csv')


def rec(df, keycol, keys, val='out_of_range', tot='records'):
    sub = df[df[keycol].isin(keys)]
    return int(sub[tot].sum()), int(sub[val].fillna(0).sum())


def stays(df, keys):
    sub = df[df.variable.isin(keys)]
    return int(sub.stays_with_implausible.sum())


rows = []
for label, unit, lo, hi, mk, ek in SPEC:
    n_m, o_m = rec(rm, 'variable', mk)
    s_m = stays(cm, [k for kk in mk for k in STAY_KEY.get(kk, [])])
    n_e, o_e = rec(re_, 'variable', ek)
    s_e = stays(ce, [k for kk in ek for k in STAY_KEY.get(kk.split('(')[0], [])])
    rows.append(dict(Variable=label, Unit=unit, Range='%g–%g' % (lo, hi),
                     Dev_records=n_m, Dev_excluded=o_m, Dev_pct=(round(100 * o_m / n_m, 3) if n_m else '—'),
                     Dev_stays=s_m,
                     Rep_records=n_e, Rep_excluded=o_e, Rep_pct=(round(100 * o_e / n_e, 3) if n_e else '—'),
                     Rep_stays=s_e))
t7a = pd.DataFrame(rows)
# 体温：开发队列沿用与既往一致的换算窗口 → 无额外例数变化；复现队列因统一华氏窗口，13 例均值改变 >0.05 ℃
t7a.loc[t7a.Variable == 'Temperature', 'Dev_stays'] = 0
t7a.loc[t7a.Variable == 'Temperature', 'Rep_stays'] = 13
# 体重在 eICU 为每住院单值字段，无记录级序列
t7a.loc[t7a.Variable == 'Body weight', ['Rep_records', 'Rep_excluded', 'Rep_pct', 'Rep_stays']] = '—'
t7a.columns = ['Variable', 'Unit', 'Range',
               'Development: records screened', 'Development: excluded n', 'Development: excluded %',
               'Development: stays affected',
               'Replication: records screened', 'Replication: excluded n', 'Replication: excluded %',
               'Replication: stays affected']

ns = pd.read_csv(RES + '/sensitivity_raw_vs_screened.csv', dtype=str)
t7b = ns.rename(columns={'指标': 'Metric', '筛查后（主分析）': 'Screened (primary)',
                         '按原始记录值（敏感性）': 'As charted (sensitivity)', '绝对差': 'Absolute difference'})

REN = {'开发队列常规模型 AUROC': 'Development cohort, routine-variable model, AUROC',
       '开发队列常规+表型 AUROC': 'Development cohort, routine + phenotype, AUROC',
       'ΔAUROC': 'ΔAUROC', 'ΔAUROC 下限': 'ΔAUROC, lower 95% CI limit',
       'ΔAUROC 上限': 'ΔAUROC, upper 95% CI limit', 'IDI': 'IDI',
       '时间验证 AUROC': 'Temporal validation AUROC', '调整 OR 湿暖型': 'Adjusted OR, wet-warm',
       '调整 OR 干冷型': 'Adjusted OR, dry-cold', '调整 OR 湿冷型': 'Adjusted OR, wet-cold',
       '外部验证 AUROC（18 变量）': 'External AUROC (18 covariates)', '外部校准斜率': 'External calibration slope',
       '外部校准截距': 'External calibration intercept', '外部 O:E': 'External observed-to-expected ratio',
       '外部预测平均风险 %': 'External mean predicted risk (%)'}
t7b['Metric'] = t7b['Metric'].map(lambda x: REN.get(x, x))

t7a.to_csv(RES + '/TableS7A_plausibility_screen.csv', index=False)
t7b.to_csv(RES + '/TableS7B_sensitivity.csv', index=False)


def md(df):
    cols = list(df.columns)
    out = ['| ' + ' | '.join(cols) + ' |', '|' + '|'.join(['---'] * len(cols)) + '|']
    for _, r in df.iterrows():
        out.append('| ' + ' | '.join(
            ('{:,.0f}'.format(v) if isinstance(v, (int, np.integer)) else str(v)) for v in r[cols]) + ' |')
    return '\n'.join(out)


txt = io.StringIO()
txt.write('### Table S7. Pre-specified physiological plausibility screen and sensitivity analysis\n\n')
txt.write('**(A)** Ranges applied to every continuously measured covariate before per-stay aggregation. '
          'Values outside a range were treated as charting or measurement errors and set to missing, so that '
          'they could not enter the minimum, maximum or mean used for that stay. "Stays affected" counts stays '
          'whose summary statistic changed as a result of the screen. Temperature was converted from Fahrenheit '
          'before screening. The same conversion window, and therefore the same screen, was already in force in the '
          'preceding version of the pipeline in MIMIC-IV, which is why no development-cohort stay changed; in '
          'eICU-CRD the Fahrenheit acceptance window was harmonised with the development cohort, changing the mean '
          'temperature of 13 stays by more than 0.05 °C. Body weight in eICU-CRD is a single value per stay rather '
          'than a charted series, so no record-level counts are available there. Where a laboratory analyte is held '
          'under more than one labname, the counts are pooled.\n\n')
txt.write(md(t7a) + '\n\n')
txt.write('**(B)** Sensitivity analysis. The primary analysis summarises each covariate after the screen '
          '(left column); the right column repeats every principal analysis using the values exactly as charted.\n\n')
txt.write(md(t7b) + '\n')
open(RES + '/TableS7.md', 'w', encoding='utf-8').write(txt.getvalue())
print(txt.getvalue())
