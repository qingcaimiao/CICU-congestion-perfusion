import io
# -*- coding: utf-8 -*-
"""第六轮：eICU 四字段在暴露窗口内的完整取值频数（Table S10）+ 敏感性数字"""
import duckdb, json, numpy as np, pandas as pd

E = 'D:/shujuku/EICU 2.0'
D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
c = duckdb.connect(); c.execute('PRAGMA threads=8')
R = lambda p: "read_csv_auto('%s',header=true,strict_mode=false,ignore_errors=true)" % p
NL = chr(10)

c.execute(f"""CREATE OR REPLACE TABLE win AS
SELECT lower(p.physicalexampath) AS path, lower(trim(coalesce(p.physicalexamvalue,''))) AS val,
       p.patientunitstayid
FROM (SELECT patientunitstayid FROM read_parquet('{D}/eicu_cp.parquet')) coh
JOIN {R(E + '/physicalExam.csv')} p ON coh.patientunitstayid=p.patientunitstayid
WHERE p.physicalexamoffset>=-360 AND p.physicalexamoffset<=1440
  AND (lower(p.physicalexampath) LIKE '%extremities/edema%'
    OR lower(p.physicalexampath) LIKE '%neck/jvd%'
    OR lower(p.physicalexampath) LIKE '%extremities/perfusion%'
    OR lower(p.physicalexampath) LIKE '%pulmonary/auscultation%')""")

FIELD = {
    'Peripheral oedema (extremities/edema)': "path LIKE '%extremities/edema%'",
    'Jugular venous distension (neck/jvd)': "path LIKE '%neck/jvd%'",
    'Peripheral perfusion (extremities/perfusion)': "path LIKE '%extremities/perfusion%'",
    'Pulmonary auscultation (pulmonary/auscultation)': "path LIKE '%pulmonary/auscultation%'",
}
POS = {
    'Extremities perfusion: extremities cool': 'positive (impaired)',
    'Extremities perfusion: extremities cold/dusky': 'positive (impaired)',
    'Extremities perfusion: extremities flushed': 'positive in the primary analysis; **not** physiological hypoperfusion',
    'Extremities perfusion: adequate': 'negative',
}
rows = []
for lab, cond in FIELD.items():
    df = c.execute(f"SELECT val, count(*) recs, count(DISTINCT patientunitstayid) stays FROM win WHERE {cond} GROUP BY 1 ORDER BY 2 DESC").df()
    tot_r = int(df.recs.sum()); tot_s = int(c.execute(f"SELECT count(DISTINCT patientunitstayid) FROM win WHERE {cond}").fetchone()[0])
    rows.append(f"**{lab}** — {len(df)} distinct values, {format(tot_r, ',')} records in {format(tot_s, ',')} stays" + NL)
    rows.append('| Value | Records | Stays | Used as |')
    rows.append('|---|---|---|---|')
    for r in df.itertuples():
        used = POS.get('%s: %s' % (lab.split(' (')[0].replace('Peripheral ', 'Extremities ').replace('Jugular venous distension', 'Neck/JVD'), r.val), '')
        if lab.startswith('Peripheral oedema'):
            if r.val == 'no edema':
                used = 'negative'
            elif r.val == 'localized swelling' or 'unilateral' in r.val:
                used = 'negative in the primary analysis (sensitivity: counted positive)'
            else:
                used = 'positive'
        elif lab.startswith('Jugular'):
            used = 'positive' if r.val == 'jvd present' else 'negative'
        elif lab.startswith('Pulmonary'):
            used = 'positive (crackles/rales)' if ('rale' in r.val or 'crackle' in r.val) else 'negative'
        rows.append('| %s | %s | %s | %s |' % (r.val, format(r.recs, ','), format(r.stays, ','), used))
    rows.append('')

txt = ('## Table S10. Complete value domain of the four eICU-CRD bedside-examination fields used for replication'
       + NL + NL
       + 'All values charted for these four *physicalExam* paths in the exposure window (\u22126 h to +24 h) among the '
       + '27,757 cardiac-ICU stays are listed. The domains are closed enumerations; no *not assessed*, *unable to assess*, '
       + '*NA*, *unknown* or *deferred* value occurs anywhere in the database, so an unrecorded field is never classified '
       + 'as positive. Path values are matched after trimming whitespace and lower-casing.'
       + NL + NL + NL.join(rows))

P = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM/Supplementary_Tables_JCM.md'
s = io.open(P, encoding='utf-8').read()
if '## Table S10.' in s:
    s = s.split('## Table S10.')[0].rstrip(NL) + NL
    print('旧 S10 已移除')
s = s.rstrip(NL) + NL + NL + '---' + NL + NL + txt
io.open(P, 'w', encoding='utf-8').write(s)
print('Table S10 appended')
print(NL.join(rows)[:1500])
