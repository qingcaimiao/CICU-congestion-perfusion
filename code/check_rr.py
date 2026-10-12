import duckdb, pandas as pd
c = duckdb.connect(); c.execute('PRAGMA threads=8')
M = 'D:/shujuku/mimic-iv-3.1'
def R(p): return "read_csv_auto('%s',header=true,strict_mode=false,ignore_errors=true)" % p
print('=== MIMIC chartevents RR(220210) valuenum 概览 ===', flush=True)
q = '''SELECT count(*) n, min(valuenum) mn, max(valuenum) mx,
 sum(CASE WHEN valuenum>80 THEN 1 ELSE 0 END) gt80,
 sum(CASE WHEN valuenum>300 THEN 1 ELSE 0 END) gt300,
 sum(CASE WHEN valuenum>1000 THEN 1 ELSE 0 END) gt1000
 FROM %s WHERE itemid=220210 AND valuenum IS NOT NULL''' % R(M+'/icu/chartevents.csv')
print(' ', c.execute(q).fetchone(), flush=True)
print('=== valuenum>300 的原始行 ===', flush=True)
q2 = '''SELECT stay_id, valuenum, value, valueuom, warning FROM %s
 WHERE itemid=220210 AND valuenum>300 ORDER BY valuenum DESC LIMIT 10''' % R(M+'/icu/chartevents.csv')
for r in c.execute(q2).fetchall(): print('  ', r, flush=True)
print('=== 同时检查 224690(RR total) ===', flush=True)
q3 = '''SELECT count(*) n, max(valuenum) mx, sum(CASE WHEN valuenum>300 THEN 1 ELSE 0 END) gt300
 FROM %s WHERE itemid=224690 AND valuenum IS NOT NULL''' % R(M+'/icu/chartevents.csv')
print(' ', c.execute(q3).fetchone(), flush=True)
