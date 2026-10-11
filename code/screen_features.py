# -*- coding: utf-8 -*-
"""MIMIC-IV 特征生理合理性筛查（pre-specified physiologic plausibility screen）

目的
----
在**记录级**对全部连续预测变量施加事先设定的生理窗口；窗口之外的值判为
录入/测量错误，置为缺失（不参与该住院的 min/max/mean 聚合）。
- 主分析用：T2_data/mimic_cp.parquet        → 筛查后
- 敏感性分析用：T2_data/mimic_cp_raw.parquet → 按原始记录值

窗口（成人 ICU 生理合理区间）
  心率 20–300 /min；呼吸 1–80 /min；SpO2 1–100 %；
  收缩压 20–300 mmHg；平均动脉压 20–250 mmHg；
  体温 25–45 °C（华氏先换算）；体重 20–400 kg；
  肌酐 0.05–50 mg/dL；尿素氮 0.5–300 mg/dL；钠 80–200 mmol/L；
  钾 1–15 mmol/L；氯 50–160 mmol/L；碳酸氢盐 1–60 mmol/L；
  血红蛋白 1–25 g/dL；白细胞 0.1–500 K/µL；血小板 1–3000 K/µL；
  血糖 10–4000 mg/dL；乳酸 0.1–40 mmol/L；胆红素 0.05–80 mg/dL。
"""
import duckdb, pandas as pd, os, shutil, time

c = duckdb.connect(); c.execute('PRAGMA threads=8')
D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
os.makedirs(OUT, exist_ok=True)
t0 = time.time()

# ---------- 0) 备份原始特征表 ----------
src, raw = D + '/mimic_cp.parquet', D + '/mimic_cp_raw.parquet'
if not os.path.exists(raw):
    shutil.copyfile(src, raw)
    print('[0] 已备份原始表 ->', raw, flush=True)
else:
    print('[0] 原始表备份已存在，跳过', flush=True)

CE = f"read_parquet('{D}/mimic_ce_f.parquet')"
LE = f"read_parquet('{D}/mimic_le_f.parquet')"
BASE = f"read_parquet('{D}/mimic_cp_raw.parquet')"

c.execute(f"CREATE OR REPLACE TABLE base AS SELECT * FROM {BASE}")
print('[1] 队列 n =', c.execute("SELECT count(*) FROM base").fetchone()[0], flush=True)

# ---------- 2) 生命体征 ----------
W = {220045: (20, 300), 220050: (20, 300), 220179: (20, 300),
     220052: (20, 250), 220181: (20, 250), 220210: (1, 80), 220277: (1, 100)}


def ok(itemids):
    """给定 itemid 集合的窗内条件"""
    ids = itemids if isinstance(itemids, (list, tuple)) else [itemids]
    return "(" + " OR ".join(f"(itemid={i} AND valuenum BETWEEN {W[i][0]} AND {W[i][1]})" for i in ids) + ")"


c.execute(f"""CREATE OR REPLACE TABLE vt AS
 SELECT ce.stay_id,
   min(CASE WHEN {ok(220045)} THEN valuenum END) hr_min,
   max(CASE WHEN {ok(220045)} THEN valuenum END) hr_max,
   min(CASE WHEN {ok([220050, 220179])} THEN valuenum END) sbp_min,
   max(CASE WHEN {ok([220050, 220179])} THEN valuenum END) sbp_max,
   min(CASE WHEN {ok([220052, 220181])} THEN valuenum END) map_min,
   max(CASE WHEN {ok(220210)} THEN valuenum END) rr_max,
   min(CASE WHEN {ok(220277)} THEN valuenum END) spo2_min
 FROM {CE} ce JOIN base b ON ce.stay_id=b.stay_id
 WHERE ce.itemid IN (220045,220050,220179,220052,220181,220210,220277) AND ce.valuenum IS NOT NULL
 GROUP BY 1""")

c.execute(f"""CREATE OR REPLACE TABLE wt AS
 SELECT ce.stay_id,
   avg(CASE WHEN ce.itemid=226512 AND ce.valuenum BETWEEN 20 AND 400 THEN ce.valuenum END) adm_weight,
   max(CASE WHEN ce.itemid=224639 AND ce.valuenum BETWEEN 20 AND 400 THEN ce.valuenum END) daily_weight
 FROM {CE} ce JOIN base b ON ce.stay_id=b.stay_id
 WHERE ce.itemid IN (226512,224639) GROUP BY 1""")

c.execute(f"""CREATE OR REPLACE TABLE tp AS
 SELECT stay_id, avg(v) AS temp_mean FROM (
   SELECT ce.stay_id, ce.valuenum AS v FROM {CE} ce JOIN base b ON ce.stay_id=b.stay_id WHERE ce.itemid=223762
   UNION ALL
   SELECT ce.stay_id, (ce.valuenum-32)*5.0/9.0 AS v FROM {CE} ce JOIN base b ON ce.stay_id=b.stay_id WHERE ce.itemid=223761
 ) WHERE v BETWEEN 25 AND 45 GROUP BY stay_id""")
print('[2] 生命体征/体重/体温 完成 (%.0fs)' % (time.time() - t0), flush=True)

# ---------- 3) 化验 ----------
LAB = {50912: (0.05, 50), 51006: (0.5, 300), 50983: (80, 200), 50971: (1, 15),
       50902: (50, 160), 50882: (1, 60), 51222: (1, 25), 51301: (0.1, 500),
       51265: (1, 3000), 50931: (10, 4000), 50813: (0.1, 40), 50930: (0.05, 80)}


def labok(itemid):
    lo, hi = LAB[itemid]
    return f"(itemid={itemid} AND valuenum BETWEEN {lo} AND {hi})"


c.execute(f"""CREATE OR REPLACE TABLE lb AS
 SELECT le.stay_id,
   max(CASE WHEN {labok(50912)} THEN valuenum END) cr_max,
   max(CASE WHEN {labok(51006)} THEN valuenum END) bun_max,
   min(CASE WHEN {labok(50983)} THEN valuenum END) na_min,
   max(CASE WHEN {labok(50971)} THEN valuenum END) k_max,
   min(CASE WHEN {labok(50902)} THEN valuenum END) cl_min,
   min(CASE WHEN {labok(50882)} THEN valuenum END) hco3_min,
   min(CASE WHEN {labok(51222)} THEN valuenum END) hgb_min,
   max(CASE WHEN {labok(51301)} THEN valuenum END) wbc_max,
   min(CASE WHEN {labok(51265)} THEN valuenum END) plt_min,
   max(CASE WHEN {labok(50931)} THEN valuenum END) glu_max,
   max(CASE WHEN {labok(50813)} THEN valuenum END) lac_max,
   max(CASE WHEN {labok(50930)} THEN valuenum END) bili_max
 FROM {LE} le JOIN base b ON le.stay_id=b.stay_id
 WHERE le.itemid IN (50912,51006,50983,50971,50902,50882,51222,51301,51265,50931,50813,50930)
 GROUP BY 1""")
print('[3] 化验 完成 (%.0fs)' % (time.time() - t0), flush=True)

# ---------- 4) 组装：列名与列序与原始表完全一致 ----------
c.execute(f"""COPY (
 SELECT b.stay_id, b.hadm_id, b.subject_id, b.died, b.los, b.age, b.gender, b.admission_type, b.race,
   vt.hr_min, vt.hr_max, vt.sbp_min, vt.sbp_max, vt.map_min, vt.rr_max, vt.spo2_min,
   coalesce(w.adm_weight, w.daily_weight) AS adm_weight,
   lb.cr_max, lb.bun_max, lb.na_min, lb.k_max, lb.cl_min, lb.hco3_min, lb.hgb_min,
   lb.wbc_max, lb.plt_min, lb.glu_max, lb.lac_max, lb.bili_max,
   b.mv, b.vaso, b.chf, b.chd, b.ckd, b.dm, b.aki, tp.temp_mean
 FROM base b
 LEFT JOIN vt ON b.stay_id=vt.stay_id
 LEFT JOIN wt w ON b.stay_id=w.stay_id
 LEFT JOIN lb ON b.stay_id=lb.stay_id
 LEFT JOIN tp ON b.stay_id=tp.stay_id
) TO '{D}/mimic_cp.parquet' (FORMAT PARQUET)""")
print('[4] 已写出筛查后特征表', flush=True)

# ---------- 5) 列一致性自检 ----------
cols_o = [r[0] for r in c.execute(f"DESCRIBE SELECT * FROM {BASE}").fetchall()]
cols_n = [r[0] for r in c.execute(f"SELECT * FROM read_parquet('{D}/mimic_cp.parquet') LIMIT 0").description]
assert cols_o == cols_n, ('列不一致!', cols_o, cols_n)
assert c.execute(f"SELECT count(*) FROM base").fetchone()[0] == \
       c.execute(f"SELECT count(*) FROM read_parquet('{D}/mimic_cp.parquet')").fetchone()[0], '行数变化!'
print('[5] 列名/列序/行数一致 ✓ 共 %d 列' % len(cols_n), flush=True)

# ---------- 6) 逐变量排除情况 ----------
MAPN = {'hr_min': '心率 min', 'hr_max': '心率 max', 'sbp_min': '收缩压 min', 'sbp_max': '收缩压 max',
        'map_min': '平均动脉压 min', 'rr_max': '呼吸频率 max', 'spo2_min': 'SpO2 min',
        'adm_weight': '入院体重', 'temp_mean': '体温 mean', 'cr_max': '肌酐 max', 'bun_max': '尿素氮 max',
        'na_min': '钠 min', 'k_max': '钾 max', 'cl_min': '氯 min', 'hco3_min': '碳酸氢盐 min',
        'hgb_min': '血红蛋白 min', 'wbc_max': '白细胞 max', 'plt_min': '血小板 min',
        'glu_max': '血糖 max', 'lac_max': '乳酸 max', 'bili_max': '胆红素 max'}
rows = []
for v in MAPN:
    r = c.execute(f"""SELECT
      (SELECT count(*) FROM base) ,
      (SELECT count(*) FROM base WHERE {v} IS NOT NULL),
      (SELECT count(*) FROM read_parquet('{D}/mimic_cp.parquet') WHERE {v} IS NOT NULL),
      (SELECT count(*) FROM base WHERE {v} IS NOT NULL AND {v} IS DISTINCT FROM
        (SELECT m.{v} FROM read_parquet('{D}/mimic_cp.parquet') m WHERE m.stay_id=base.stay_id))
    """).fetchone()
    rows.append(dict(variable=v, name=MAPN[v], n_cohort=r[0], nonnull_before=r[1],
                     nonnull_after=r[2], stays_with_implausible=r[3]))
sc = pd.DataFrame(rows)
sc.to_csv(OUT + '/screening_counts_mimic.csv', index=False)
print('\n== 有例数变化的变量 ==')
print(sc[sc.stays_with_implausible > 0].to_string(index=False))
print('\n== 筛查前后关键统计 ==')
q = " UNION ALL ".join(
    f"""SELECT '{v}' v, (SELECT min({v}) FROM base) mn_b, (SELECT max({v}) FROM base) mx_b,
      (SELECT stddev_samp({v}) FROM base) sd_b,
      (SELECT min({v}) FROM read_parquet('{D}/mimic_cp.parquet')) mn_a,
      (SELECT max({v}) FROM read_parquet('{D}/mimic_cp.parquet')) mx_a,
      (SELECT stddev_samp({v}) FROM read_parquet('{D}/mimic_cp.parquet')) sd_a"""
    for v in ['hr_min', 'hr_max', 'sbp_min', 'map_min', 'rr_max', 'spo2_min', 'adm_weight', 'k_max']) + " ORDER BY v"
print(c.execute(q).df().to_string(index=False))
print('\nDONE %.0fs' % (time.time() - t0))
