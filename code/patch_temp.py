# -*- coding: utf-8 -*-
"""修正体温单位：223762=摄氏, 223761=华氏(需转换)"""
import duckdb
D='D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
c=duckdb.connect(); c.execute('PRAGMA threads=8')
c.execute(f"""CREATE OR REPLACE TABLE t AS
 SELECT stay_id, avg(v) AS temp_c FROM (
   SELECT stay_id, valuenum AS v FROM read_parquet('{D}/mimic_ce_f.parquet') WHERE itemid=223762
   UNION ALL
   SELECT stay_id, (valuenum-32)*5.0/9.0 AS v FROM read_parquet('{D}/mimic_ce_f.parquet') WHERE itemid=223761
 ) WHERE v BETWEEN 25 AND 45 GROUP BY stay_id""")
c.execute(f"""CREATE OR REPLACE TABLE m AS SELECT * FROM read_parquet('{D}/mimic_cp.parquet')""")
c.execute("""CREATE OR REPLACE TABLE m2 AS
 SELECT m.* EXCLUDE(temp_mean), t.temp_c AS temp_mean FROM m LEFT JOIN t ON m.stay_id=t.stay_id""")
c.execute(f"COPY m2 TO '{D}/mimic_cp.parquet' (FORMAT PARQUET)")
print(c.execute(f"SELECT count(*) n, round(avg(temp_mean),1), round(min(temp_mean),1), round(max(temp_mean),1), count(temp_mean) FROM read_parquet('{D}/mimic_cp.parquet')").fetchone())
