# -*- coding: utf-8 -*-
"""依据筛查后的分析集重建 Table 1（英文/中文两版 Markdown 行），避免手工转录错误。"""
import duckdb, numpy as np, pandas as pd
from scipy import stats

OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
c = duckdb.connect(); c.execute('PRAGMA threads=8')
mm = c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()
mm['female'] = mm.gender.astype(str).str.upper().str.startswith('F').astype(int)
ORDER = ['DryWarm', 'WetWarm', 'DryCold', 'WetCold']


def num(s):
    return pd.to_numeric(pd.Series(s).astype(str).str.replace('>', '', regex=False).str.strip(), errors='coerce')


SUP = str.maketrans('0123456789-+', '⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺')


def fmt_p(p):
    if p != p:
        return '-'
    if p >= 0.001:
        return '%.3f' % p
    if p < 1e-300:
        return '<0.001'
    s = '%.1e' % p                      # 1.1e-25
    m, e = s.split('e')
    ei = int(e)
    sign = '⁻' if ei < 0 else ''
    return '%s × 10%s' % (m, (sign + str(abs(ei))).translate(SUP))


ROWS = [
    ('age', 'Age, years', '年龄，岁', 'cont'),
    ('adm_weight', 'Admission weight, kg', '入院体重，kg', 'cont'),
    ('los', 'ICU length of stay, days', 'ICU 住院时长，天', 'cont'),
    ('hr_min', 'Heart rate, min, bpm', '心率最低，次/分', 'cont'),
    ('hr_max', 'Heart rate, max, bpm', '心率最高，次/分', 'cont'),
    ('sbp_min', 'Systolic blood pressure, min, mmHg', '收缩压最低，mmHg', 'cont'),
    ('map_min', 'Mean arterial pressure, min, mmHg', '平均动脉压最低，mmHg', 'cont'),
    ('rr_max', 'Respiratory rate, max, breaths/min', '呼吸频率最高，次/分', 'cont'),
    ('spo2_min', 'Oxygen saturation, min, %', '血氧饱和度最低，%', 'cont'),
    ('temp_mean', 'Temperature, mean, °C', '体温均值，°C', 'cont'),
    ('cr_max', 'Creatinine, max, mg/dL', '肌酐最高，mg/dL', 'cont'),
    ('bun_max', 'Urea nitrogen, max, mg/dL', '尿素氮最高，mg/dL', 'cont'),
    ('na_min', 'Sodium, min, mmol/L', '钠最低，mmol/L', 'cont'),
    ('k_max', 'Potassium, max, mmol/L', '钾最高，mmol/L', 'cont'),
    ('cl_min', 'Chloride, min, mmol/L', '氯最低，mmol/L', 'cont'),
    ('hco3_min', 'Bicarbonate, min, mmol/L', '碳酸氢盐最低，mmol/L', 'cont'),
    ('hgb_min', 'Haemoglobin, min, g/dL', '血红蛋白最低，g/dL', 'cont'),
    ('wbc_max', 'White cell count, max, K/µL', '白细胞最高，K/µL', 'cont'),
    ('plt_min', 'Platelet count, min, K/µL', '血小板最低，K/µL', 'cont'),
    ('glu_max', 'Glucose, max, mg/dL', '血糖最高，mg/dL', 'cont'),
    ('ew', 'Oedema grade (0–5)', '水肿等级（0–5）', 'cont'),
    ('female', 'Female sex', '女性', 'bin'),
    ('mv', 'Invasive mechanical ventilation', '有创机械通气', 'bin'),
    ('vaso', 'Vasoactive drug infusion', '血管活性药输注', 'bin'),
    ('chf', 'Congestive heart failure', '充血性心力衰竭', 'bin'),
    ('chd', 'Coronary heart disease', '冠心病', 'bin'),
    ('ckd', 'Chronic kidney disease', '慢性肾病', 'bin'),
    ('dm', 'Diabetes mellitus', '糖尿病', 'bin'),
    ('aki', 'Acute kidney injury', '急性肾损伤', 'bin'),
    ('cr_abn', 'Prolonged capillary refill', '毛细血管再充盈延长', 'bin'),
    ('died', '**In-hospital mortality**', '**院内死亡**', 'mort'),
]

out_en, out_zh = [], []
for k, en, zh, kind in ROWS:
    if kind == 'cont':
        v = num(mm[k]); grp = [v[mm.quad == o].dropna() for o in ORDER]
        p = stats.kruskal(*[g for g in grp if len(g) > 5]).pvalue
        cells = ['%.1f (%.1f–%.1f)' % (g.median(), g.quantile(.25), g.quantile(.75)) for g in grp]
    else:
        v = mm[k]
        p = stats.chi2_contingency(pd.crosstab(mm.quad, v))[1] if v.nunique() > 1 else np.nan
        if kind == 'mort':
            cells = ['%s (%.2f)' % (format(mm.loc[mm.quad == o, 'died'].sum(), ','), 100 * mm.loc[mm.quad == o, 'died'].mean())
                     for o in ORDER]
        else:
            cells = ['%s (%.1f)' % (format(mm.loc[mm.quad == o, k].sum(), ','), 100 * mm.loc[mm.quad == o, k].mean()) for o in ORDER]
    out_en.append('| %s | %s | %s |' % (en, ' | '.join(cells), fmt_p(p)))
    out_zh.append('| %s | %s | %s |' % (zh, ' | '.join(cells), fmt_p(p)))

open(OUT + '/_table1_en.md', 'w', encoding='utf-8').write('\n'.join(out_en) + '\n')
open(OUT + '/_table1_zh.md', 'w', encoding='utf-8').write('\n'.join(out_zh) + '\n')
print('\n'.join(out_en))
print()
print('\n'.join(out_zh))
