# -*- coding: utf-8 -*-
"""修正 eICU 结局定义：院内死亡 = hospitaldischargestatus='Expired'

原实现误用 unitdischargestatus（ICU 死亡，1,727 例），而 MIMIC 侧用
hospital_expire_flag（院内死亡）。两者不同源，导致外部验证的结局定义不一致。

本脚本：
1. 在 eicu_cp_raw.parquet 与 eicu_cp.parquet 中重算 died = hospitaldischargestatus='Expired'
2. 同时保留 died_union（ICU 死亡 ∪ 院内死亡）与 died_unit 供敏感性分析
3. 打印新旧口径对照
"""
import duckdb, shutil, os

c = duckdb.connect(); c.execute('PRAGMA threads=8')
E = 'D:/shujuku/EICU 2.0'
D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
R = lambda p: "read_csv_auto('%s',header=true,strict_mode=false,ignore_errors=true)" % p

for f in ['eicu_cp.parquet', 'eicu_cp_raw.parquet']:
    p = D + '/' + f
    if not os.path.exists(p + '.bak_unit_outcome'):
        shutil.copyfile(p, p + '.bak_unit_outcome')

c.execute(f"""CREATE OR REPLACE TABLE oc AS
 SELECT patientunitstayid,
   CASE WHEN hospitaldischargestatus='Expired' THEN 1 ELSE 0 END AS died_hosp,
   CASE WHEN unitdischargestatus='Expired' THEN 1 ELSE 0 END AS died_unit,
   CASE WHEN unitdischargestatus='Expired' OR hospitaldischargestatus='Expired' THEN 1 ELSE 0 END AS died_union,
   CASE WHEN hospitaldischargestatus IS NULL OR hospitaldischargestatus='' THEN 1 ELSE 0 END AS hosp_status_unknown
 FROM {R(E+'/patient.csv')}
 WHERE unittype IN ('Cardiac ICU','CCU-CTICU')""")

for f in ['eicu_cp.parquet', 'eicu_cp_raw.parquet']:
    p = D + '/' + f
    cols = [d[0] for d in c.execute(f"DESCRIBE SELECT * FROM read_parquet('{p}')").fetchall()]
    extra = [x for x in ['died_hosp', 'died_unit', 'died_union', 'hosp_status_unknown'] if x not in cols]
    keep = ', '.join('b.' + x for x in cols if x != 'died')
    newc = ''.join(',\n   oc.%s' % x for x in extra)
    c.execute(f"""COPY (
     SELECT {keep}, oc.died_hosp AS died{newc}
     FROM read_parquet('{p}') b JOIN oc USING(patientunitstayid)
    ) TO '{p}' (FORMAT PARQUET)""")
    print('已重写', f, '新增列:', extra)

print()
print('=== 新旧结局对照（全部心内 ICU 住院）===')
print(c.execute(f"""SELECT count(*) n, sum(died_unit) icu_death, sum(died_hosp) hosp_death,
      sum(died_union) union_death, sum(hosp_status_unknown) status_unknown,
      round(100.0*sum(died_unit)/count(*),2) rate_unit, round(100.0*sum(died_hosp)/count(*),2) rate_hosp
    FROM read_parquet('{D}/eicu_cp.parquet')""").df().to_string(index=False))
print()
print('=== 两轴可判定子集（暴露可判定）===')
print(c.execute(f"""SELECT count(*) n, sum(died_unit) icu_death, sum(died_hosp) hosp_death, sum(died_union) union_death
 FROM read_parquet('{D}/eicu_cp.parquet')
 WHERE (coalesce(edema_doc,0)+coalesce(jvd_doc,0)+coalesce(lungs_doc,0))>0 AND coalesce(perf_doc,0)=1""").df().to_string(index=False))
