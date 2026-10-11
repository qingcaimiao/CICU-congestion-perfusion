# -*- coding: utf-8 -*-
"""
eICU 外部复现：心内ICU 床旁充血-灌注表型
人群：unittype in ('Cardiac ICU','CCU-CTICU')
暴露：physicalExam 中的水肿 / JVD / 外周灌注 / 肺部啰音
输出：T2_data/eicu_cp.parquet
"""
import duckdb, os, time
c = duckdb.connect(); c.execute('PRAGMA threads=8')
E = 'D:/shujuku/EICU 2.0'
D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
def R(p): return "read_csv_auto('%s',header=true,strict_mode=false,ignore_errors=true)" % p
def log(*a): print(*a, flush=True)
t0 = time.time()

log('[1] eICU cardiac cohort ...')
c.execute(f"""CREATE OR REPLACE TABLE coh AS
 SELECT patientunitstayid, uniquepid, hospitalid, unittype, unitdischargeoffset,
   age, gender, admissionweight,
   CASE WHEN unitdischargestatus='Expired' THEN 1 ELSE 0 END AS died
 FROM {R(E+'/patient.csv')}
 WHERE unittype IN ('Cardiac ICU','CCU-CTICU')""")
log('    n =', c.execute("SELECT count(*) FROM coh").fetchone()[0])

log('[2] physicalExam scan (1.4GB) ...')
c.execute(f"""CREATE OR REPLACE TABLE exam AS
 SELECT coh.patientunitstayid, p.physicalexamoffset AS off, lower(p.physicalexampath) AS path,
        trim(lower(coalesce(p.physicalexamvalue,''))) AS val
 FROM coh JOIN {R(E+'/physicalExam.csv')} p ON coh.patientunitstayid=p.patientunitstayid
 WHERE p.physicalexamoffset>=-360 AND p.physicalexamoffset<=1440
   AND (lower(p.physicalexampath) LIKE '%extremities/edema%'
     OR lower(p.physicalexampath) LIKE '%neck/jvd%'
     OR lower(p.physicalexampath) LIKE '%extremities/perfusion%'
     OR lower(p.physicalexampath) LIKE '%pulmonary/auscultation%')""")
log('    exam rows:', c.execute("SELECT count(*) FROM exam").fetchone()[0], '(%.0fs)' % (time.time()-t0))
for x in c.execute("SELECT path, val, count(*) n FROM exam WHERE path LIKE '%edema%' GROUP BY 1,2 ORDER BY n DESC LIMIT 12").fetchall():
    log('      edema:', x)

c.execute("""CREATE OR REPLACE TABLE ex AS
 SELECT coh.patientunitstayid,
   max(CASE WHEN path LIKE '%%extremities/edema%%' THEN 1 ELSE 0 END) edema_doc,
   max(CASE WHEN (path LIKE '%%bilateral%%edema%%' AND val NOT LIKE '%%no %%')
              OR (path LIKE '%%severity%%' AND val IN ('1+','2+','3+','4+'))
              OR val LIKE '%%anasarca%%' THEN 1 ELSE 0 END) edema_pos,
   max(CASE WHEN (path LIKE '%%severity%%' AND val IN ('3+','4+')) OR val LIKE '%%anasarca%%' THEN 1 ELSE 0 END) edema_sev,
   max(CASE WHEN path LIKE '%%neck/jvd%%' THEN 1 ELSE 0 END) jvd_doc,
   max(CASE WHEN path LIKE '%%neck/jvd%%' AND val NOT LIKE '%%absent%%' AND val<>'no jvd' THEN 1 ELSE 0 END) jvd_pos,
   max(CASE WHEN path LIKE '%%extremities/perfusion%%' THEN 1 ELSE 0 END) perf_doc,
   max(CASE WHEN path LIKE '%%extremities/perfusion%%' AND val<>'adequate' AND val<>'' THEN 1 ELSE 0 END) hypoperf,
   max(CASE WHEN path LIKE '%%pulmonary/auscultation%%' THEN 1 ELSE 0 END) lungs_doc,
   max(CASE WHEN path LIKE '%%pulmonary/auscultation%%' AND (val LIKE '%%crackle%%' OR val LIKE '%%rales%%') THEN 1 ELSE 0 END) crackles
 FROM coh LEFT JOIN exam ON coh.patientunitstayid=exam.patientunitstayid
 GROUP BY 1""")

log('[3] vitals (vitalPeriodic 8GB) ...')
c.execute(f"""CREATE OR REPLACE TABLE vp AS
 SELECT coh.patientunitstayid,
   min(v.heartrate) hr_min, max(v.heartrate) hr_max,
   min(v.systemicsystolic) sbp_art, min(v.systemicmean) map_art,
   max(v.respiration) rr_max, min(v.sao2) spo2_min,
   avg(CASE WHEN v.temperature BETWEEN 90 AND 115 THEN (v.temperature-32)*5.0/9.0
            WHEN v.temperature BETWEEN 25 AND 45 THEN v.temperature END) temp_mean
 FROM coh JOIN {R(E+'/vitalPeriodic.csv')} v ON coh.patientunitstayid=v.patientunitstayid
 WHERE v.observationoffset>=-360 AND v.observationoffset<=1440
 GROUP BY 1""")
log('    vp rows:', c.execute("SELECT count(*) FROM vp").fetchone()[0], '(%.0fs)' % (time.time()-t0))

log('[3b] nurseCharting blood pressure (11.5GB) ...')
c.execute(f"""CREATE OR REPLACE TABLE nb AS
 SELECT coh.patientunitstayid,
   min(CASE WHEN n.nursingchartcelltypevalname IN ('Non-Invasive BP Systolic','Invasive BP Systolic')
            THEN TRY_CAST(n.nursingchartvalue AS DOUBLE) END) sbp_min,
   min(CASE WHEN n.nursingchartcelltypevalname IN ('Non-Invasive BP Mean','Invasive BP Mean')
            THEN TRY_CAST(n.nursingchartvalue AS DOUBLE) END) map_min
 FROM coh JOIN {R(E+'/nurseCharting.csv')} n ON coh.patientunitstayid=n.patientunitstayid
 WHERE n.nursingchartcelltypevalname IN ('Non-Invasive BP Systolic','Invasive BP Systolic',
        'Non-Invasive BP Mean','Invasive BP Mean')
   AND n.nursingchartoffset>=-360 AND n.nursingchartoffset<=1440
 GROUP BY 1""")
log('    nb rows:', c.execute("SELECT count(*) FROM nb").fetchone()[0], '(%.0fs)' % (time.time()-t0))

log('[4] labs (lab.csv 2.3GB) ...')
c.execute(f"""CREATE OR REPLACE TABLE lb AS
 SELECT coh.patientunitstayid,
   max(CASE WHEN lower(l.labname)='creatinine' THEN l.labresult END) cr_max,
   max(CASE WHEN lower(l.labname) LIKE '%bun%' OR lower(l.labname)='urea nitrogen' THEN l.labresult END) bun_max,
   min(CASE WHEN lower(l.labname)='sodium' THEN l.labresult END) na_min,
   max(CASE WHEN lower(l.labname)='potassium' THEN l.labresult END) k_max,
   min(CASE WHEN lower(l.labname)='chloride' THEN l.labresult END) cl_min,
   min(CASE WHEN lower(l.labname) LIKE '%bicarbonate%' THEN l.labresult END) hco3_min,
   min(CASE WHEN lower(l.labname)='hgb' OR lower(l.labname)='hemoglobin' THEN l.labresult END) hgb_min,
   max(CASE WHEN lower(l.labname) LIKE '%wbc%' OR lower(l.labname) LIKE '%white blood%' THEN l.labresult END) wbc_max,
   min(CASE WHEN lower(l.labname) LIKE '%platelet%' THEN l.labresult END) plt_min,
   max(CASE WHEN lower(l.labname)='glucose' THEN l.labresult END) glu_max,
   max(CASE WHEN lower(l.labname)='lactate' THEN l.labresult END) lac_max
 FROM coh JOIN {R(E+'/lab.csv')} l ON coh.patientunitstayid=l.patientunitstayid
 WHERE l.labresultoffset>=-360 AND l.labresultoffset<=1440
   AND (lower(l.labname) IN ('creatinine','sodium','potassium','chloride','hgb','hemoglobin','glucose','lactate')
     OR lower(l.labname) LIKE '%bun%' OR lower(l.labname) LIKE '%urea%' OR lower(l.labname) LIKE '%bicarbonate%'
     OR lower(l.labname) LIKE '%wbc%' OR lower(l.labname) LIKE '%white blood%' OR lower(l.labname) LIKE '%platelet%')
 GROUP BY 1""")
log('    lb rows:', c.execute("SELECT count(*) FROM lb").fetchone()[0], '(%.0fs)' % (time.time()-t0))

log('[5] assemble ...')
c.execute(f"""COPY (
 SELECT coh.patientunitstayid, coh.hospitalid, coh.died, coh.unitdischargeoffset/1440.0 AS los,
   coh.age, coh.gender, coh.admissionweight,
   ex.edema_doc, ex.edema_pos, ex.edema_sev, ex.jvd_doc, ex.jvd_pos, ex.perf_doc, ex.hypoperf, ex.lungs_doc, ex.crackles,
   vp.hr_min, vp.hr_max,
   least(coalesce(nb.sbp_min, 9999), coalesce(vp.sbp_art, 9999)) AS sbp_min_raw,
   least(coalesce(nb.map_min, 9999), coalesce(vp.map_art, 9999)) AS map_min_raw,
   vp.rr_max, vp.spo2_min, vp.temp_mean,
   lb.cr_max, lb.bun_max, lb.na_min, lb.k_max, lb.cl_min, lb.hco3_min, lb.hgb_min, lb.wbc_max, lb.plt_min, lb.glu_max, lb.lac_max
 FROM coh LEFT JOIN ex ON coh.patientunitstayid=ex.patientunitstayid
 LEFT JOIN vp ON coh.patientunitstayid=vp.patientunitstayid
 LEFT JOIN nb ON coh.patientunitstayid=nb.patientunitstayid
 LEFT JOIN lb ON coh.patientunitstayid=lb.patientunitstayid
) TO '{D}/eicu_cp.parquet' (FORMAT PARQUET)""")
# 把 sentinel 9999 还原为缺失
c.execute(f"""CREATE OR REPLACE TABLE fin AS
 SELECT * EXCLUDE(sbp_min_raw, map_min_raw),
   CASE WHEN sbp_min_raw>=9999 THEN NULL ELSE sbp_min_raw END AS sbp_min,
   CASE WHEN map_min_raw>=9999 THEN NULL ELSE map_min_raw END AS map_min
 FROM read_parquet('{D}/eicu_cp.parquet')""")
c.execute(f"COPY fin TO '{D}/eicu_cp.parquet' (FORMAT PARQUET)")
log('    final:', c.execute(f"SELECT count(*), sum(died), sum(edema_doc), sum(jvd_doc), count(sbp_min), count(map_min), count(hgb_min), count(temp_mean) FROM read_parquet('{D}/eicu_cp.parquet')").fetchone())
log('DONE %.0fs' % (time.time()-t0))
