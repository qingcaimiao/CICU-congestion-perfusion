# -*- coding: utf-8 -*-
"""eICU 体温口径与 MIMIC 对齐：华氏(50–115℉)换算为摄氏，摄氏(25–45℃)直接取，
换算/取值后只保留 25–45℃ 的记录，再按住院取均值。保持覆盖口径（全住院观察）。"""
import duckdb
c = duckdb.connect(); c.execute('PRAGMA threads=8')
E = 'D:/shujuku/EICU 2.0'; D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
def R(p): return "read_csv_auto('%s',header=true,strict_mode=false,ignore_errors=true)" % p
c.execute(f"""COPY (
 SELECT patientunitstayid, avg(t) AS temp_clean_c FROM (
   SELECT p.patientunitstayid, v.temperature AS t
   FROM {R(E+'/patient.csv')} p JOIN {R(E+'/vitalPeriodic.csv')} v ON p.patientunitstayid=v.patientunitstayid
   WHERE p.unittype IN ('Cardiac ICU','CCU-CTICU') AND v.temperature BETWEEN 25 AND 45
   UNION ALL
   SELECT p.patientunitstayid, (v.temperature-32)*5.0/9.0 AS t
   FROM {R(E+'/patient.csv')} p JOIN {R(E+'/vitalPeriodic.csv')} v ON p.patientunitstayid=v.patientunitstayid
   WHERE p.unittype IN ('Cardiac ICU','CCU-CTICU') AND v.temperature BETWEEN 50 AND 115
 ) WHERE t BETWEEN 25 AND 45 GROUP BY patientunitstayid
) TO '{D}/eicu_temp_clean.csv' (HEADER, DELIMITER ',')""")
print('new :', c.execute(f"SELECT count(*) , count(temp_clean_c), round(min(temp_clean_c),2), round(max(temp_clean_c),2) FROM read_csv_auto('{D}/eicu_temp_clean.csv')").fetchone())
print('prev:', c.execute(f"SELECT count(*) , count(temp_clean_c), round(min(temp_clean_c),2), round(max(temp_clean_c),2) FROM read_csv_auto('{D}/eicu_temp_clean_prev.csv')").fetchone())
print('两版差异（绝对值>0.05 例数）:', c.execute(f"""SELECT count(*) FROM
 read_csv_auto('{D}/eicu_temp_clean.csv') a JOIN read_csv_auto('{D}/eicu_temp_clean_prev.csv') b USING(patientunitstayid)
 WHERE abs(a.temp_clean_c-b.temp_clean_c)>0.05""").fetchone())
