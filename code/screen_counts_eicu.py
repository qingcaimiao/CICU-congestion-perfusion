# -*- coding: utf-8 -*-
"""eICU-CRD 记录级筛查计数（与 screen_features_eicu.py 同一窗口），用于补充表 S7。"""
import duckdb, pandas as pd
c = duckdb.connect(); c.execute('PRAGMA threads=8')
E = 'D:/shujuku/EICU 2.0'; D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
def R(p): return "read_csv_auto('%s',header=true,strict_mode=false,ignore_errors=true)" % p
c.execute(f"CREATE OR REPLACE TABLE coh AS SELECT patientunitstayid FROM read_parquet('{D}/eicu_cp_raw.parquet')")
rows = []

def add(name, cn, n, out, lo, hi):
    rows.append(dict(variable=name, cn=cn, lo=lo, hi=hi, records=n, out_of_range=out,
                     pct=round(100 * (out or 0) / max(n, 1), 4)))
    print(rows[-1], flush=True)

# 生命体征
V = [('heartrate', 'hr', 20, 300), ('respiration', 'rr', 1, 80), ('sao2', 'spo2', 1, 100),
     ('systemicsystolic', 'sbp(arterial)', 20, 300), ('systemicmean', 'map(arterial)', 20, 250)]
q = " UNION ALL ".join(
    f"""SELECT '{nm}' AS v, count({col}) n, sum(CASE WHEN {col} IS NOT NULL AND ({col}<{lo} OR {col}>{hi}) THEN 1 ELSE 0 END) o
        FROM {R(E+'/vitalPeriodic.csv')} x JOIN coh USING(patientunitstayid)
        WHERE x.observationoffset>=-360 AND x.observationoffset<=1440""" for col, nm, lo, hi in V)
for r in c.execute(q).fetchall():
    add(r[0], r[0], r[1], r[2], [x for x in V if x[1] == r[0]][0][2], [x for x in V if x[1] == r[0]][0][3])

# 无创/有创血压
for nm, vals, lo, hi in [('sbp(nurseCharting)', "'Non-Invasive BP Systolic','Invasive BP Systolic'", 20, 300),
                         ('map(nurseCharting)', "'Non-Invasive BP Mean','Invasive BP Mean'", 20, 250)]:
    n, o = c.execute(f"""SELECT count(TRY_CAST(y.nursingchartvalue AS DOUBLE)), sum(CASE WHEN TRY_CAST(y.nursingchartvalue AS DOUBLE) IS NOT NULL
        AND (TRY_CAST(y.nursingchartvalue AS DOUBLE)<{lo} OR TRY_CAST(y.nursingchartvalue AS DOUBLE)>{hi}) THEN 1 ELSE 0 END)
      FROM {R(E+'/nurseCharting.csv')} y JOIN coh USING(patientunitstayid)
      WHERE y.nursingchartcelltypevalname IN ({vals}) AND y.nursingchartoffset>=-360 AND y.nursingchartoffset<=1440""").fetchone()
    add(nm, nm, n, o, lo, hi)

# 化验
L = [('creatinine', 'cr', 0.05, 50), ('sodium', 'na', 80, 200), ('potassium', 'k', 1, 15),
     ('chloride', 'cl', 50, 160), ('Hgb', 'hgb', 1, 25), ('hemoglobin', 'hgb(alt)', 1, 25),
     ('glucose', 'glu', 10, 4000), ('lactate', 'lac', 0.1, 40)]
for lab, nm, lo, hi in L:
    n, o = c.execute(f"""SELECT count(z.labresult), sum(CASE WHEN z.labresult IS NOT NULL AND (z.labresult<{lo} OR z.labresult>{hi}) THEN 1 ELSE 0 END)
      FROM {R(E+'/lab.csv')} z JOIN coh USING(patientunitstayid)
      WHERE lower(z.labname)=lower('{lab}') AND z.labresultoffset>=-360 AND z.labresultoffset<=1440""").fetchone()
    add(nm, nm, n, o, lo, hi)
for pat, nm, lo, hi in [('%bun%', 'bun', 0.5, 300), ('%urea%', 'urea', 0.5, 300),
                        ('%bicarbonate%', 'hco3', 1, 60), ('%wbc%', 'wbc', 0.1, 500),
                        ('%white blood%', 'wbc(alt)', 0.1, 500), ('%platelet%', 'plt', 1, 3000)]:
    n, o = c.execute(f"""SELECT count(z.labresult), sum(CASE WHEN z.labresult IS NOT NULL AND (z.labresult<{lo} OR z.labresult>{hi}) THEN 1 ELSE 0 END)
      FROM {R(E+'/lab.csv')} z JOIN coh USING(patientunitstayid)
      WHERE lower(z.labname) LIKE '{pat}' AND z.labresultoffset>=-360 AND z.labresultoffset<=1440""").fetchone()
    add(nm, nm, n, o, lo, hi)

# 体温
n, o = c.execute(f"""SELECT count(x.temperature), sum(CASE WHEN x.temperature IS NOT NULL AND
      ((x.temperature BETWEEN 25 AND 45) = FALSE) AND ((x.temperature BETWEEN 50 AND 115) = FALSE) THEN 1 ELSE 0 END)
      FROM {R(E+'/vitalPeriodic.csv')} x JOIN coh USING(patientunitstayid) WHERE x.temperature IS NOT NULL""").fetchone()
add('temp', 'temp', n, o, '25-45 C / 50-115 F', '')

df = pd.DataFrame(rows)
df.to_csv(OUT + '/screening_records_eicu.csv', index=False, encoding='utf-8-sig')
print('\n->', OUT + '/screening_records_eicu.csv')
