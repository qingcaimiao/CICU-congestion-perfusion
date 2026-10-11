# -*- coding: utf-8 -*-
"""第二轮 critique 数据真实性硬核：水肿取值映射 / 部位 / CRT 左右一致 / 队列流程 / eICU 字段 / 温度单位"""
import duckdb, numpy as np, pandas as pd, json, os
c = duckdb.connect(); c.execute('PRAGMA threads=8')
M = 'D:/shujuku/mimic-iv-3.1'; E = 'D:/shujuku/EICU 2.0'
D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
def R(p): return "read_csv_auto('%s',header=true,strict_mode=false,ignore_errors=true)" % p
res = {}

print('#'*100)
print('# A. MIMIC itemid 224862 (Edema Amount) 原始取值频数表 —— 这是数据真实性的核心证据')
print('#'*100)
db = c.execute(f"SELECT itemid,label,linksto,category,unitname,param_type FROM {R(M+'/icu/d_items.csv')} WHERE itemid IN (224862,224031,223951,224308)").df()
print(db.to_string(index=False))
print()
vf = c.execute(f"""SELECT coalesce(trim(value),'<NULL>') AS raw_value, count(*) n,
   count(DISTINCT stay_id) n_stay, count(valuenum) n_num
 FROM read_parquet('{D}/cp_exam_raw.parquet') WHERE itemid=224862
 GROUP BY 1 ORDER BY n DESC""").df()
print('== itemid 224862 value 频数（全部取值）==')
print(vf.to_string(index=False))
tot = vf.n.sum(); mapped = vf[vf.raw_value.isin(['none','2 mm','4 mm','6 mm','8 mm','anasarca'])].n.sum()
print('\n总记录 %d；可精确映射 %d (%.2f%%)；未映射 %d (%.2f%%)' % (tot, mapped, 100*mapped/tot, tot-mapped, 100*(tot-mapped)/tot))
print('未映射取值:', vf[~vf.raw_value.isin(['none','2 mm','4 mm','6 mm','8 mm','anasarca'])].raw_value.tolist())

print()
print('#'*100)
print('# B. itemid 224031 (Edema Location) 取值与是否使用')
print('#'*100)
loc = c.execute(f"""SELECT coalesce(trim(value),'<NULL>') v, count(*) n, count(DISTINCT stay_id) ns
 FROM read_parquet('{D}/cp_exam_raw.parquet') WHERE itemid=224031 GROUP BY 1 ORDER BY n DESC LIMIT 15""").df()
print(loc.to_string(index=False))

print()
print('#'*100)
print('# C. CRT (223951/224308) 取值、左右一致率')
print('#'*100)
cr = c.execute(f"""SELECT itemid, coalesce(trim(value),'<NULL>') v, count(*) n, count(DISTINCT stay_id) ns
 FROM read_parquet('{D}/cp_exam_raw.parquet') WHERE itemid IN (223951,224308) GROUP BY 1,2 ORDER BY itemid, n DESC""").df()
print(cr.to_string(index=False))
pair = c.execute(f"""SELECT count(*) n_both FROM (
   SELECT stay_id FROM read_parquet('{D}/cp_exam_raw.parquet') WHERE itemid=223951 AND off_h>=-6 AND off_h<=24 GROUP BY 1
   INTERSECT
   SELECT stay_id FROM read_parquet('{D}/cp_exam_raw.parquet') WHERE itemid=224308 AND off_h>=-6 AND off_h<=24 GROUP BY 1)""").fetchone()[0]
disc = c.execute(f"""WITH l AS (SELECT stay_id, max(CASE WHEN trim(lower(value)) LIKE 'abnormal%' THEN 1 ELSE 0 END) a,
     count(*) na FROM read_parquet('{D}/cp_exam_raw.parquet') WHERE itemid=223951 AND off_h>=-6 AND off_h<=24 GROUP BY 1),
   r AS (SELECT stay_id, max(CASE WHEN trim(lower(value)) LIKE 'abnormal%' THEN 1 ELSE 0 END) a,
     count(*) na FROM read_parquet('{D}/cp_exam_raw.parquet') WHERE itemid=224308 AND off_h>=-6 AND off_h<=24 GROUP BY 1)
 SELECT count(*) n_both, sum(CASE WHEN l.a<>r.a THEN 1 ELSE 0 END) n_discordant FROM l JOIN r USING(stay_id)""").df()
print('\n左右均有记录 stay =', pair)
print(disc.to_string(index=False))
res['crt_pairs'] = int(pair); res['crt_discordant'] = int(disc.n_discordant[0])
print('左右不一致率 = %.2f%%' % (100*disc.n_discordant[0]/max(pair, 1)))

print()
print('#'*100)
print('# D. 队列流程：从全部 ICU 到 20,806 的排除步骤')
print('#'*100)
flow = {}
flow['all_icustays'] = c.execute(f"SELECT count(*) FROM {R(M+'/icu/icustays.csv')}").fetchone()[0]
flow['cardiac_stays_all'] = c.execute(f"SELECT count(*) FROM {R(M+'/icu/icustays.csv')} WHERE lower(first_careunit) LIKE '%cvicu%' OR lower(first_careunit) LIKE '%ccu%'").fetchone()[0]
flow['cardiac_stays_by_unit'] = c.execute(f"SELECT first_careunit, count(*) FROM {R(M+'/icu/icustays.csv')} WHERE lower(first_careunit) LIKE '%cvicu%' OR lower(first_careunit) LIKE '%ccu%' GROUP BY 1").df().to_dict('records')
flow['cardiac_first_per_subject'] = c.execute(f"""SELECT count(*) FROM (SELECT row_number() OVER (PARTITION BY subject_id ORDER BY intime) rn,
   first_careunit FROM {R(M+'/icu/icustays.csv')} WHERE lower(first_careunit) LIKE '%cvicu%' OR lower(first_careunit) LIKE '%ccu%') WHERE rn=1""").fetchone()[0]
flow['repeat_cardiac_stays_excluded'] = flow['cardiac_stays_all'] - flow['cardiac_first_per_subject']
coh_age = c.execute(f"""WITH icu AS (SELECT stay_id, hadm_id, subject_id, intime,
     row_number() OVER (PARTITION BY subject_id ORDER BY intime) rn
   FROM {R(M+'/icu/icustays.csv')} WHERE lower(first_careunit) LIKE '%cvicu%' OR lower(first_careunit) LIKE '%ccu%')
 SELECT count(*) n, sum(CASE WHEN p.anchor_age<18 THEN 1 ELSE 0 END) under18,
   sum(CASE WHEN p.anchor_age IS NULL THEN 1 ELSE 0 END) age_missing
 FROM icu i JOIN {R(M+'/hosp/patients.csv')} p ON i.subject_id=p.subject_id WHERE i.rn=1""").df()
print('全部 ICU stays           :', flow['all_icustays'])
print('心内 ICU stays（全部）    :', flow['cardiac_stays_all'], flow['cardiac_stays_by_unit'])
print('心内 ICU 首诊（每人 1 次）:', flow['cardiac_first_per_subject'], ' → 排除重复住院 %d' % flow['repeat_cardiac_stays_excluded'])
print('其中 age<18:', int(coh_age.under18[0]), '| age 缺失:', int(coh_age.age_missing[0]))
res['flow'] = flow

print()
print('#'*100)
print('# E. eICU 充血/灌注字段定义与各定义的 n / deaths')
print('#'*100)
ec = c.execute(f"SELECT * FROM read_parquet('{D}/eicu_cp.parquet')").df()
print('eICU 心内ICU stays =', len(ec), '| 死亡 =', int(ec.died.sum()))
print('各体征记录率（原始 -6~24h 窗口）：')
for v in ['edema_doc','jvd_doc','perf_doc','lungs_doc']:
    print('   %-10s documented %d (%.2f%%) | 阳性 %d (%.2f%%)' % (v, ec[v].sum(), 100*ec[v].mean(),
          ec[v.replace('_doc','_pos')].sum() if v.replace('_doc','_pos') in ec else -1, 0))
hypo = ec[ec.perf_doc==1]
print('   灌注记录者 %d，其中异常 %d (%.2f%%)' % (len(hypo), hypo.hypoperf.sum(), 100*hypo.hypoperf.mean()))
print()
defs = {
 'oedema only':        ('edema_pos', 'hypoperf'),
 'JVD only':           ('jvd_pos', 'hypoperf'),
 'crackles only':      ('crackles', 'hypoperf'),
 'composite (any)':    (None, 'hypoperf'),
}
rows = []
for name, (cong, perf) in defs.items():
    sub = ec.copy()
    if cong is None:
        sub['cong'] = ((sub.edema_pos==1)|(sub.jvd_pos==1)|(sub.crackles==1)).astype(int)
    else:
        sub['cong'] = sub[cong]
    d = sub.dropna(subset=['cong','hypoperf'])
    for cl, cv in [('dry', 0), ('wet', 1)]:
        for pl, pv in [('warm', 0), ('cold', 1)]:
            s = d[(d.cong==cv) & (d.hypoperf==pv)]
            rows.append(dict(definition=name, cell=f'{cl}-{pl}', n=len(s), deaths=int(s.died.sum()),
                             mortality=round(100*s.died.mean(),2) if len(s) else np.nan))
dt = pd.DataFrame(rows)
piv = dt.pivot(index='definition', columns='cell', values=['n','deaths','mortality'])
print(piv.to_string())
dt.to_csv(OUT+'/T_eicu_congestion_definitions_full.csv', index=False)
res['eicu_cong_defs'] = dt.to_dict('records')
print()
print('总体的 n / deaths（四象限可判定，复合定义）：')
sub = ec.copy(); sub['cong'] = ((sub.edema_pos==1)|(sub.jvd_pos==1)|(sub.crackles==1)).astype(int)
d = sub.dropna(subset=['cong','hypoperf'])
print('   n =', len(d), ' deaths =', int(d.died.sum()), ' mortality = %.2f%%' % (100*d.died.mean()))
res['eicu_analysis_n'] = len(d); res['eicu_analysis_deaths'] = int(d.died.sum())

print()
print('#'*100)
print('# F. eICU 温度单位核查（vitalPeriodic.temperature）')
print('#'*100)
tp = c.execute(f"""SELECT count(*) n,
   sum(CASE WHEN v.temperature>50 THEN 1 ELSE 0 END) gt50,
   sum(CASE WHEN v.temperature>45 THEN 1 ELSE 0 END) gt45,
   min(v.temperature) mn, max(v.temperature) mx, avg(v.temperature) av
 FROM {R(E+'/patient.csv')} p JOIN {R(E+'/vitalPeriodic.csv')} v ON p.patientunitstayid=v.patientunitstayid
 WHERE p.unittype IN ('Cardiac ICU','CCU-CTICU')""").df()
print(tp.to_string(index=False))
print('→ 若 >50 的记录为 0，则温度统一为摄氏度，无需换算')
res['eicu_temp'] = tp.to_dict('records')[0]

print()
print('#'*100)
print('# G. 外部验证 EPV')
print('#'*100)
print('外部 n=%d, deaths=%d, 可迁移协变量 19 → EPV = %.1f' % (len(d), int(d.died.sum()), d.died.sum()/19))
res['eicu_epv'] = round(int(d.died.sum())/19, 1)
print('开发集 n=%d, deaths=%d, 26 参数 → EPV = %.1f' % (len(c.execute(f"SELECT * FROM read_parquet('{OUT}/cp_analysis_set.parquet')").df()), 
      c.execute(f"SELECT sum(died) FROM read_parquet('{OUT}/cp_analysis_set.parquet')").fetchone()[0],
      c.execute(f"SELECT sum(died) FROM read_parquet('{OUT}/cp_analysis_set.parquet')").fetchone()[0]/26))

json.dump(res, open(OUT+'/cp_critique2_checks.json','w'), indent=1, default=str, ensure_ascii=False)
print('\nDONE ->', OUT+'/cp_critique2_checks.json')
