# -*- coding: utf-8 -*-
"""eICU-CRD 特征生理合理性筛查（与 MIMIC 侧同一套生理窗口）

- 主分析用：T2_data/eicu_cp.parquet        → 筛查后
- 敏感性分析用：T2_data/eicu_cp_raw.parquet → 按原始记录值
- 同时重写 T2_data/eicu_temp_clean.csv（记录级窗口后的体温均值）

窗口与 MIMIC 侧一致：
  心率 20–300；呼吸 1–80；SpO2 1–100；收缩压 20–300；平均动脉压 20–250；
  体温 25–45 ℃（华氏 90–115 ℉ 换算）；体重 20–400 kg；
  肌酐 0.05–50；尿素氮 0.5–300；钠 80–200；钾 1–15；氯 50–160；
  碳酸氢盐 1–60；血红蛋白 1–25；白细胞 0.1–500；血小板 1–3000；
  血糖 10–4000；乳酸 0.1–40。
"""
import duckdb, os, shutil, time

c = duckdb.connect(); c.execute('PRAGMA threads=8')
E = 'D:/shujuku/EICU 2.0'
D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
os.makedirs(OUT, exist_ok=True)
t0 = time.time()


def R(p):
    return "read_csv_auto('%s',header=true,strict_mode=false,ignore_errors=true)" % p


def log(*a):
    print('[%6.0fs]' % (time.time() - t0), *a, flush=True)


# ---------- 0) 备份 ----------
src, raw = D + '/eicu_cp.parquet', D + '/eicu_cp_raw.parquet'
if not os.path.exists(raw):
    shutil.copyfile(src, raw)
    log('已备份原始表 ->', raw)
c.execute(f"CREATE OR REPLACE TABLE base AS SELECT * FROM read_parquet('{raw}')")
log('队列 n =', c.execute("SELECT count(*) FROM base").fetchone()[0])

# ---------- 1) vitalPeriodic（记录级筛查后聚合） ----------
log('读取 vitalPeriodic (7.9GB) ...')
c.execute(f"""CREATE OR REPLACE TABLE vp AS
 SELECT b.patientunitstayid,
   min(CASE WHEN v.heartrate BETWEEN 20 AND 300 THEN v.heartrate END) hr_min,
   max(CASE WHEN v.heartrate BETWEEN 20 AND 300 THEN v.heartrate END) hr_max,
   min(CASE WHEN v.respiration BETWEEN 1 AND 80 THEN v.respiration END) rr_lo,
   max(CASE WHEN v.respiration BETWEEN 1 AND 80 THEN v.respiration END) rr_max,
   min(CASE WHEN v.sao2 BETWEEN 1 AND 100 THEN v.sao2 END) spo2_min,
   min(CASE WHEN v.systemicsystolic BETWEEN 20 AND 300 THEN v.systemicsystolic END) sbp_art,
   min(CASE WHEN v.systemicmean BETWEEN 20 AND 250 THEN v.systemicmean END) map_art,
   avg(CASE WHEN v.temperature BETWEEN 90 AND 115 THEN (v.temperature-32)*5.0/9.0
            WHEN v.temperature BETWEEN 25 AND 45 THEN v.temperature END) temp_c
 FROM base b JOIN {R(E+'/vitalPeriodic.csv')} v ON b.patientunitstayid=v.patientunitstayid
 WHERE v.observationoffset>=-360 AND v.observationoffset<=1440
 GROUP BY 1""")
log('vp rows:', c.execute("SELECT count(*) FROM vp").fetchone()[0], '| temp 非空:',
    c.execute("SELECT count(temp_c) FROM vp").fetchone()[0])

# ---------- 2) nurseCharting 血压 ----------
log('读取 nurseCharting (11.5GB) ...')
c.execute(f"""CREATE OR REPLACE TABLE nb AS
 SELECT b.patientunitstayid,
   min(CASE WHEN n.nursingchartcelltypevalname IN ('Non-Invasive BP Systolic','Invasive BP Systolic')
            AND TRY_CAST(n.nursingchartvalue AS DOUBLE) BETWEEN 20 AND 300
            THEN TRY_CAST(n.nursingchartvalue AS DOUBLE) END) sbp_nb,
   min(CASE WHEN n.nursingchartcelltypevalname IN ('Non-Invasive BP Mean','Invasive BP Mean')
            AND TRY_CAST(n.nursingchartvalue AS DOUBLE) BETWEEN 20 AND 250
            THEN TRY_CAST(n.nursingchartvalue AS DOUBLE) END) map_nb
 FROM base b JOIN {R(E+'/nurseCharting.csv')} n ON b.patientunitstayid=n.patientunitstayid
 WHERE n.nursingchartcelltypevalname IN ('Non-Invasive BP Systolic','Invasive BP Systolic',
        'Non-Invasive BP Mean','Invasive BP Mean')
   AND n.nursingchartoffset>=-360 AND n.nursingchartoffset<=1440
 GROUP BY 1""")
log('nb rows:', c.execute("SELECT count(*) FROM nb").fetchone()[0])

# ---------- 3) lab ----------
log('读取 lab (2.4GB) ...')
c.execute(f"""CREATE OR REPLACE TABLE lb AS
 SELECT b.patientunitstayid,
   max(CASE WHEN lower(l.labname)='creatinine' AND l.labresult BETWEEN 0.05 AND 50 THEN l.labresult END) cr_max,
   max(CASE WHEN (lower(l.labname) LIKE '%bun%' OR lower(l.labname)='urea nitrogen')
             AND l.labresult BETWEEN 0.5 AND 300 THEN l.labresult END) bun_max,
   min(CASE WHEN lower(l.labname)='sodium' AND l.labresult BETWEEN 80 AND 200 THEN l.labresult END) na_min,
   max(CASE WHEN lower(l.labname)='potassium' AND l.labresult BETWEEN 1 AND 15 THEN l.labresult END) k_max,
   min(CASE WHEN lower(l.labname)='chloride' AND l.labresult BETWEEN 50 AND 160 THEN l.labresult END) cl_min,
   min(CASE WHEN lower(l.labname) LIKE '%bicarbonate%' AND l.labresult BETWEEN 1 AND 60 THEN l.labresult END) hco3_min,
   min(CASE WHEN (lower(l.labname)='hgb' OR lower(l.labname)='hemoglobin')
            AND l.labresult BETWEEN 1 AND 25 THEN l.labresult END) hgb_min,
   max(CASE WHEN (lower(l.labname) LIKE '%wbc%' OR lower(l.labname) LIKE '%white blood%')
            AND l.labresult BETWEEN 0.1 AND 500 THEN l.labresult END) wbc_max,
   min(CASE WHEN lower(l.labname) LIKE '%platelet%' AND l.labresult BETWEEN 1 AND 3000 THEN l.labresult END) plt_min,
   max(CASE WHEN lower(l.labname)='glucose' AND l.labresult BETWEEN 10 AND 4000 THEN l.labresult END) glu_max,
   max(CASE WHEN lower(l.labname)='lactate' AND l.labresult BETWEEN 0.1 AND 40 THEN l.labresult END) lac_max
 FROM base b JOIN {R(E+'/lab.csv')} l ON b.patientunitstayid=l.patientunitstayid
 WHERE l.labresultoffset>=-360 AND l.labresultoffset<=1440
   AND (lower(l.labname) IN ('creatinine','sodium','potassium','chloride','hgb','hemoglobin','glucose','lactate')
     OR lower(l.labname) LIKE '%bun%' OR lower(l.labname) LIKE '%urea%' OR lower(l.labname) LIKE '%bicarbonate%'
     OR lower(l.labname) LIKE '%wbc%' OR lower(l.labname) LIKE '%white blood%' OR lower(l.labname) LIKE '%platelet%')
 GROUP BY 1""")
log('lb rows:', c.execute("SELECT count(*) FROM lb").fetchone()[0])

# ---------- 4) 组装（列名/列序与原始表一致） ----------
c.execute(f"""COPY (
 SELECT b.patientunitstayid, b.hospitalid, b.died, b.los, b.age, b.gender,
   CASE WHEN b.admissionweight BETWEEN 20 AND 400 THEN b.admissionweight END AS admissionweight,
   b.edema_doc, b.edema_pos, b.edema_sev, b.jvd_doc, b.jvd_pos, b.perf_doc, b.hypoperf,
   b.lungs_doc, b.crackles,
   vp.hr_min, vp.hr_max, vp.rr_max, vp.spo2_min, vp.temp_c AS temp_mean,
   lb.cr_max, lb.bun_max, lb.na_min, lb.k_max, lb.cl_min, lb.hco3_min, lb.hgb_min,
   lb.wbc_max, lb.plt_min, lb.glu_max, lb.lac_max,
   least(coalesce(nb.sbp_nb, 9999), coalesce(vp.sbp_art, 9999)) AS sbp_min_raw,
   least(coalesce(nb.map_nb, 9999), coalesce(vp.map_art, 9999)) AS map_min_raw
 FROM base b LEFT JOIN vp ON b.patientunitstayid=vp.patientunitstayid
 LEFT JOIN nb ON b.patientunitstayid=nb.patientunitstayid
 LEFT JOIN lb ON b.patientunitstayid=lb.patientunitstayid
) TO '{D}/_eicu_screened_stage.parquet' (FORMAT PARQUET)""")

c.execute(f"""COPY (
 SELECT * EXCLUDE (sbp_min_raw, map_min_raw),
   CASE WHEN sbp_min_raw>=9999 THEN NULL ELSE sbp_min_raw END AS sbp_min,
   CASE WHEN map_min_raw>=9999 THEN NULL ELSE map_min_raw END AS map_min
 FROM read_parquet('{D}/_eicu_screened_stage.parquet')
) TO '{D}/eicu_cp.parquet' (FORMAT PARQUET)""")
os.remove(D + '/_eicu_screened_stage.parquet')
log('已写出筛查后 eICU 特征表')

# ---------- 5) 体温单独文件（记录级窗口） ----------
c.execute(f"""COPY (SELECT patientunitstayid, temp_c AS temp_clean_c FROM vp)
 TO '{D}/eicu_temp_clean.csv' (HEADER, DELIMITER ',')""")
log('已重写 eicu_temp_clean.csv')

# ---------- 6) 自检 ----------
cols_o = [r[0] for r in c.execute(f"DESCRIBE SELECT * FROM read_parquet('{raw}')").fetchall()]
cols_n = [r[0] for r in c.execute(f"SELECT * FROM read_parquet('{D}/eicu_cp.parquet') LIMIT 0").description]
assert cols_o == cols_n, ('列不一致!', cols_o, cols_n)
assert c.execute("SELECT count(*) FROM base").fetchone()[0] == \
       c.execute(f"SELECT count(*) FROM read_parquet('{D}/eicu_cp.parquet')").fetchone()[0], '行数变化!'
log('列名/列序/行数一致 ✓ %d 列' % len(cols_n))

# ---------- 7) 排除情况 ----------
MAPN = {'hr_min': '心率 min', 'hr_max': '心率 max', 'sbp_min': '收缩压 min', 'map_min': '平均动脉压 min',
        'rr_max': '呼吸频率 max', 'spo2_min': 'SpO2 min', 'temp_mean': '体温 mean',
        'admissionweight': '入院体重', 'cr_max': '肌酐 max', 'bun_max': '尿素氮 max', 'na_min': '钠 min',
        'k_max': '钾 max', 'cl_min': '氯 min', 'hco3_min': '碳酸氢盐 min', 'hgb_min': '血红蛋白 min',
        'wbc_max': '白细胞 max', 'plt_min': '血小板 min', 'glu_max': '血糖 max', 'lac_max': '乳酸 max'}
rows = []
for v in MAPN:
    r = c.execute(f"""SELECT
      (SELECT count(*) FROM base),
      (SELECT count(*) FROM base WHERE {v} IS NOT NULL),
      (SELECT count(*) FROM read_parquet('{D}/eicu_cp.parquet') WHERE {v} IS NOT NULL),
      (SELECT count(*) FROM base WHERE {v} IS NOT NULL AND {v} IS DISTINCT FROM
        (SELECT m.{v} FROM read_parquet('{D}/eicu_cp.parquet') m WHERE m.patientunitstayid=base.patientunitstayid))
    """).fetchone()
    rows.append(dict(variable=v, name=MAPN[v], n_cohort=r[0], nonnull_before=r[1],
                     nonnull_after=r[2], stays_with_implausible=r[3]))
import pandas as pd
sc = pd.DataFrame(rows)
sc.to_csv(OUT + '/screening_counts_eicu.csv', index=False)
log('\n== 有例数变化的变量 ==\n' + sc[sc.stays_with_implausible > 0].to_string(index=False))

q = " UNION ALL ".join(
    f"""SELECT '{v}' v, (SELECT min({v}) FROM base) mn_b, (SELECT max({v}) FROM base) mx_b,
      (SELECT stddev_samp({v}) FROM base) sd_b,
      (SELECT min({v}) FROM read_parquet('{D}/eicu_cp.parquet')) mn_a,
      (SELECT max({v}) FROM read_parquet('{D}/eicu_cp.parquet')) mx_a,
      (SELECT stddev_samp({v}) FROM read_parquet('{D}/eicu_cp.parquet')) sd_a"""
    for v in ['hr_min', 'hr_max', 'sbp_min', 'map_min', 'rr_max', 'spo2_min', 'wbc_max', 'admissionweight']) + " ORDER BY v"
log('\n== 筛查前后关键统计 ==\n' + c.execute(q).df().to_string(index=False))
log('DONE')
