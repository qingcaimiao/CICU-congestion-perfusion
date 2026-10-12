# -*- coding: utf-8 -*-
"""第五轮核查 C：eICU 外周水肿阳性定义 —— 稿件文字 vs 实际编码"""
import duckdb

E = 'D:/shujuku/EICU 2.0'
D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
c = duckdb.connect(); c.execute('PRAGMA threads=8')
R = lambda p: "read_csv_auto('%s',header=true,strict_mode=false,ignore_errors=true)" % p

c.execute(f"""CREATE OR REPLACE TABLE ex AS
SELECT patientunitstayid,
  max(CASE WHEN lower(physicalexampath) LIKE '%extremities/edema/bilateral%'
             AND lower(trim(physicalexamvalue)) NOT LIKE 'no %' THEN 1 ELSE 0 END) p_bilateral,
  max(CASE WHEN lower(physicalexampath) LIKE '%extremities/edema/severity/%' THEN 1 ELSE 0 END) p_severity,
  max(CASE WHEN lower(trim(physicalexamvalue)) LIKE '%anasarca%' THEN 1 ELSE 0 END) p_anasarca,
  max(CASE WHEN lower(physicalexampath) LIKE '%extremities/edema%' THEN 1 ELSE 0 END) p_any
FROM {R(E + '/physicalExam.csv')} GROUP BY 1""")

print('=== 全库层面（27,757 心内 ICU 住院中）===')
print(c.execute("""SELECT
  count(*) n,
  sum(p_any) doc_any,
  sum(p_bilateral) bilateral,
  sum(p_severity) severity,
  sum(p_anasarca) anasarca,
  sum(CASE WHEN p_severity=1 AND p_bilateral=0 AND p_anasarca=0 THEN 1 ELSE 0 END) severity_only
FROM ex e JOIN (SELECT patientunitstayid FROM read_parquet('%s/eicu_cp.parquet')) t USING(patientunitstayid)""" % D
).df().to_string(index=False))

print('\n=== 现编码 edema_pos 与各种口径对比（心内 ICU 队列）===')
print(c.execute("""SELECT
  sum(CASE WHEN e.p_bilateral=1 OR e.p_anasarca=1 THEN 1 ELSE 0 END) coded_pos_now,
  sum(CASE WHEN e.p_bilateral=1 OR e.p_anasarca=1 OR e.p_severity=1 THEN 1 ELSE 0 END) pos_if_severity_included,
  sum(CASE WHEN e.p_severity=1 AND e.p_bilateral=0 AND e.p_anasarca=0 THEN 1 ELSE 0 END) extra_stays
FROM ex e JOIN (SELECT patientunitstayid FROM read_parquet('%s/eicu_cp.parquet')) t USING(patientunitstayid)""" % D
).df().to_string(index=False))

print('\n=== 两轴均记录的 1,555 子集内，阳性数变化 ===')
print(c.execute("""SELECT
  count(*) n,
  sum(CASE WHEN e.p_bilateral=1 OR e.p_anasarca=1 THEN 1 ELSE 0 END) now,
  sum(CASE WHEN e.p_bilateral=1 OR e.p_anasarca=1 OR e.p_severity=1 THEN 1 ELSE 0 END) expanded
FROM ex e JOIN (SELECT patientunitstayid, edema_doc, jvd_doc, lungs_doc, perf_doc
                FROM read_parquet('%s/eicu_cp.parquet')) t USING(patientunitstayid)
WHERE coalesce(t.edema_doc,0)+coalesce(t.jvd_doc,0)+coalesce(t.lungs_doc,0)>0 AND coalesce(t.perf_doc,0)=1""" % D
).df().to_string(index=False))
