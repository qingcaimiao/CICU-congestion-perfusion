# -*- coding: utf-8 -*-
"""第五轮核查 B：eICU 充血/灌注取值映射与稿件定义是否一致"""
import duckdb

E = 'D:/shujuku/EICU 2.0'
D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
c = duckdb.connect(); c.execute('PRAGMA threads=8')
R = lambda p: "read_csv_auto('%s',header=true,strict_mode=false,ignore_errors=true)" % p

print('=== 每条 physicalExam path 的实际形态（edema / jvd / perfusion）===')
q = f"""
SELECT lower(pe.physicalexampath) AS path, lower(trim(pe.physicalexamvalue)) AS val, count(*) n
FROM {R(E + '/physicalExam.csv')} pe
WHERE lower(pe.physicalexampath) LIKE '%extremities/edema%'
   OR lower(pe.physicalexampath) LIKE '%neck/jvd%'
   OR lower(pe.physicalexampath) LIKE '%extremities/perfusion%'
GROUP BY 1,2 ORDER BY 1, 3 DESC
"""
df = c.execute(q).df()
print('distinct paths:', df.path.nunique())
for p in df.path.unique():
    sub = df[df.path == p]
    print('\n  PATH:', p)
    print(sub[['val', 'n']].head(15).to_string(index=False))

print('\n=== eicu_cp.parquet 中的暴露分布 ===')
print(c.execute(f"""SELECT count(*) n, sum(edema_doc) edema_doc, sum(edema_pos) edema_pos,
   sum(edema_sev) edema_sev, sum(jvd_doc) jvd_doc, sum(jvd_pos) jvd_pos,
   sum(perf_doc) perf_doc, sum(hypoperf) hypoperf, sum(lungs_doc) lungs_doc, sum(crackles) crackles
   FROM read_parquet('{D}/eicu_cp.parquet')""").df().to_string(index=False))

print('\n=== 按取值反查 edema_pos 命中情况（阳性病例中出现的取值）===')
q2 = f"""
WITH coh AS (SELECT patientunitstayid FROM read_parquet('{D}/eicu_cp.parquet') WHERE edema_pos=1),
     vals AS (SELECT DISTINCT pe.patientunitstayid, lower(trim(pe.physicalexamvalue)) val
              FROM {R(E + '/physicalExam.csv')} pe JOIN coh USING(patientunitstayid)
              WHERE lower(pe.physicalexampath) LIKE '%extremities/edema%')
SELECT val, count(*) n FROM vals GROUP BY 1 ORDER BY 2 DESC
"""
print(c.execute(q2).df().to_string(index=False))
