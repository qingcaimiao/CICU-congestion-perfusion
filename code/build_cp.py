# -*- coding: utf-8 -*-
"""
充血-灌注（Bedside Congestion-Perfusion）研究 - 数据集构建
人群：MIMIC-IV 首个心内ICU住院（CVICU / CCU），成人
暴露：水肿分级(224862 Edema Amount, mm) + 毛细血管再充盈(223951/224308)
结局：院内死亡（主）；28/90 天死亡（次）
输出：T2_data/mimic_cp.parquet, T2_data/cp_exam_raw.parquet
"""
import duckdb, os, time, sys
c = duckdb.connect(); c.execute('PRAGMA threads=8')
M = 'D:/shujuku/mimic-iv-3.1'
D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
os.makedirs(D, exist_ok=True)
def R(p): return "read_csv_auto('%s',header=true,strict_mode=false,ignore_errors=true)" % p
def log(*a): print(*a, flush=True)
t0 = time.time()

# ---------- Stage 1: 队列（首个心内ICU住院） ----------
log('[1] cohort ...')
c.execute(f"""CREATE OR REPLACE TABLE icu AS
 SELECT stay_id, hadm_id, subject_id, first_careunit, intime, outtime, los,
   row_number() OVER (PARTITION BY subject_id ORDER BY intime) rn
 FROM {R(M+'/icu/icustays.csv')}
 WHERE lower(first_careunit) LIKE '%cvicu%' OR lower(first_careunit) LIKE '%ccu%'""")
c.execute(f"""CREATE OR REPLACE TABLE coh AS
 SELECT i.*, p.gender, p.anchor_age, p.dod, a.hospital_expire_flag AS died,
        a.admission_type, a.race
 FROM icu i
 JOIN {R(M+'/hosp/patients.csv')} p ON i.subject_id=p.subject_id
 JOIN {R(M+'/hosp/admissions.csv')} a ON i.hadm_id=a.hadm_id
 WHERE i.rn=1""")
n = c.execute("SELECT count(*) FROM coh").fetchone()[0]
log('    cohort n =', n)
log('    careunit:', c.execute("SELECT first_careunit, count(*) FROM coh GROUP BY 1").fetchall())
log('    age<18:', c.execute("SELECT count(*) FROM coh WHERE anchor_age<18").fetchone()[0])

# ---------- Stage 2: 查体（水肿 / 毛细血管再充盈）扫描 ----------
log('[2] scanning chartevents for exam itemids ...')
c.execute(f"""CREATE OR REPLACE TABLE exam_raw AS
 SELECT ce.stay_id, ce.itemid, ce.value, ce.valuenum, ce.charttime,
        date_diff('second', coh.intime, ce.charttime)/3600.0 AS off_h
 FROM {R(M+'/icu/chartevents.csv')} ce
 JOIN coh ON ce.stay_id=coh.stay_id
 WHERE ce.itemid IN (224862, 224031, 223951, 224308)""")
log('    exam rows:', c.execute("SELECT count(*) FROM exam_raw").fetchone()[0], '(%.0fs)' % (time.time()-t0))
c.execute(f"COPY exam_raw TO '{D}/cp_exam_raw.parquet' (FORMAT PARQUET)")

# ---------- Stage 3: 生命体征（复用 mimic_ce_f） ----------
log('[3] vitals from mimic_ce_f ...')
c.execute(f"""CREATE OR REPLACE TABLE vt AS
 SELECT ce.stay_id,
   min(CASE WHEN ce.itemid=220045 THEN ce.valuenum END) hr_min,
   max(CASE WHEN ce.itemid=220045 THEN ce.valuenum END) hr_max,
   min(CASE WHEN ce.itemid IN (220050,220179) THEN ce.valuenum END) sbp_min,
   max(CASE WHEN ce.itemid IN (220050,220179) THEN ce.valuenum END) sbp_max,
   min(CASE WHEN ce.itemid IN (220052,220181) THEN ce.valuenum END) map_min,
   max(CASE WHEN ce.itemid=220210 THEN ce.valuenum END) rr_max,
   min(CASE WHEN ce.itemid=220277 THEN ce.valuenum END) spo2_min,
   avg(CASE WHEN ce.itemid IN (223761,223762) THEN ce.valuenum END) temp_mean
 FROM read_parquet('{D}/mimic_ce_f.parquet') ce
 JOIN coh ON ce.stay_id=coh.stay_id
 WHERE ce.itemid IN (220045,220050,220179,220052,220181,220210,220277,223761,223762)
 GROUP BY 1""")
c.execute(f"""CREATE OR REPLACE TABLE wt AS
 SELECT stay_id,
   avg(CASE WHEN itemid=226512 THEN valuenum END) adm_weight,
   max(CASE WHEN itemid=224639 THEN valuenum END) daily_weight
 FROM read_parquet('{D}/mimic_ce_f.parquet') WHERE itemid IN (226512,224639) GROUP BY 1""")
log('    vt rows:', c.execute("SELECT count(*) FROM vt").fetchone()[0])

# ---------- Stage 4: 化验（复用 mimic_le_f, 前后 24h） ----------
log('[4] labs from mimic_le_f ...')
c.execute(f"""CREATE OR REPLACE TABLE lb AS
 SELECT le.stay_id,
   max(CASE WHEN le.itemid=50912 THEN le.valuenum END) cr_max,
   max(CASE WHEN le.itemid=51006 THEN le.valuenum END) bun_max,
   min(CASE WHEN le.itemid=50983 THEN le.valuenum END) na_min,
   max(CASE WHEN le.itemid=50971 THEN le.valuenum END) k_max,
   min(CASE WHEN le.itemid=50902 THEN le.valuenum END) cl_min,
   min(CASE WHEN le.itemid=50882 THEN le.valuenum END) hco3_min,
   min(CASE WHEN le.itemid=51222 THEN le.valuenum END) hgb_min,
   max(CASE WHEN le.itemid=51301 THEN le.valuenum END) wbc_max,
   min(CASE WHEN le.itemid=51265 THEN le.valuenum END) plt_min,
   max(CASE WHEN le.itemid=50931 THEN le.valuenum END) glu_max,
   max(CASE WHEN le.itemid=50813 THEN le.valuenum END) lac_max,
   max(CASE WHEN le.itemid=50930 THEN le.valuenum END) bili_max
 FROM read_parquet('{D}/mimic_le_f.parquet') le
 JOIN coh ON le.stay_id=coh.stay_id
 WHERE le.itemid IN (50912,51006,50983,50971,50902,50882,51222,51301,51265,50931,50813,50930)
 GROUP BY 1""")
log('    lb rows:', c.execute("SELECT count(*) FROM lb").fetchone()[0])

# ---------- Stage 5: 机械通气 / 血管活性药 ----------
log('[5] MV + vasopressors ...')
c.execute(f"""CREATE OR REPLACE TABLE mv AS
 SELECT stay_id, 1 AS mv FROM {R(M+'/icu/procedureevents.csv')}
 WHERE itemid=225792 GROUP BY 1""")
c.execute(f"""CREATE OR REPLACE TABLE vp AS
 SELECT stay_id, 1 AS vaso FROM {R(M+'/icu/inputevents.csv')}
 WHERE itemid IN (221906,221289,221662,221653,222315,221749,221986) GROUP BY 1""")
log('    mv rows:', c.execute("SELECT count(*) FROM mv").fetchone()[0], '| vaso rows:', c.execute("SELECT count(*) FROM vp").fetchone()[0])

# ---------- Stage 6: 合并症 ----------
log('[6] comorbidities ...')
c.execute(f"""CREATE OR REPLACE TABLE dx AS
 SELECT hadm_id,
   max(CASE WHEN icd_code LIKE 'I50%' THEN 1 ELSE 0 END) chf,
   max(CASE WHEN icd_code LIKE 'I25%' OR icd_code LIKE 'I21%' THEN 1 ELSE 0 END) chd,
   max(CASE WHEN icd_code LIKE 'N18%' OR icd_code LIKE '585%' THEN 1 ELSE 0 END) ckd,
   max(CASE WHEN icd_code LIKE 'E11%' OR icd_code LIKE '250%' THEN 1 ELSE 0 END) dm,
   max(CASE WHEN icd_code LIKE 'N17%' OR icd_code LIKE '584%' THEN 1 ELSE 0 END) aki
 FROM {R(M+'/hosp/diagnoses_icd.csv')} GROUP BY 1""")

# ---------- Stage 7: 汇总 ----------
log('[7] assemble ...')
c.execute(f"""COPY (
 SELECT coh.stay_id, coh.hadm_id, coh.subject_id, coh.died, coh.los,
   coh.anchor_age AS age, coh.gender, coh.admission_type, coh.race,
   coalesce(vt.hr_min,0) hr_min, vt.hr_max, vt.sbp_min, vt.sbp_max, vt.map_min, vt.rr_max, vt.spo2_min, vt.temp_mean,
   coalesce(vt2.adm_weight, vt2.daily_weight) adm_weight,
   lb.cr_max, lb.bun_max, lb.na_min, lb.k_max, lb.cl_min, lb.hco3_min, lb.hgb_min, lb.wbc_max, lb.plt_min, lb.glu_max, lb.lac_max, lb.bili_max,
   coalesce(mv.mv,0) mv, coalesce(vp.vaso,0) vaso,
   coalesce(dx.chf,0) chf, coalesce(dx.chd,0) chd, coalesce(dx.ckd,0) ckd, coalesce(dx.dm,0) dm, coalesce(dx.aki,0) aki
 FROM coh LEFT JOIN vt ON coh.stay_id=vt.stay_id
 LEFT JOIN wt vt2 ON coh.stay_id=vt2.stay_id
 LEFT JOIN lb ON coh.stay_id=lb.stay_id
 LEFT JOIN mv ON coh.stay_id=mv.stay_id
 LEFT JOIN vp ON coh.stay_id=vp.stay_id
 LEFT JOIN dx ON coh.hadm_id=dx.hadm_id
) TO '{D}/mimic_cp.parquet' (FORMAT PARQUET)""")
log('    final n =', c.execute(f"SELECT count(*), sum(died) FROM read_parquet('{D}/mimic_cp.parquet')").fetchone())
log('DONE %.0fs' % (time.time()-t0))
