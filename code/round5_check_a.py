# -*- coding: utf-8 -*-
"""第五轮核查 A：eICU physicalExam 中是否存在 not assessed / unable to assess / NA 类取值；DOI 复核"""
import duckdb, json, urllib.request

E = 'D:/shujuku/EICU 2.0'
c = duckdb.connect(); c.execute('PRAGMA threads=8')
R = lambda p: "read_csv_auto('%s',header=true,strict_mode=false,ignore_errors=true)" % p

print('=== physicalExam 中与充血/灌注相关的 path 与取值（全库）===')
q = f"""
SELECT
  CASE
    WHEN lower(pe.physicalexampath) LIKE '%extremities/edema%'   THEN 'extremities/edema'
    WHEN lower(pe.physicalexampath) LIKE '%neck/jvd%'            THEN 'neck/jvd'
    WHEN lower(pe.physicalexampath) LIKE '%pulmonary/auscultation%' THEN 'pulmonary/auscultation'
    WHEN lower(pe.physicalexampath) LIKE '%extremities/perfusion%' THEN 'extremities/perfusion'
  END AS field,
  lower(trim(pe.physicalexamvalue)) AS val,
  count(*) n
FROM {R(E + '/physicalExam.csv')} pe
WHERE lower(pe.physicalexampath) LIKE '%extremities/edema%'
   OR lower(pe.physicalexampath) LIKE '%neck/jvd%'
   OR lower(pe.physicalexampath) LIKE '%pulmonary/auscultation%'
   OR lower(pe.physicalexampath) LIKE '%extremities/perfusion%'
GROUP BY 1,2 ORDER BY 1, 3 DESC
"""
df = c.execute(q).df()
for f in df.field.unique():
    sub = df[df.field == f]
    print('\n--- %s（%d 种取值，共 %d 条）' % (f, len(sub), sub.n.sum()))
    print(sub.head(40).to_string(index=False))

print('\n=== 含 "not assess"/"unable"/"n/a"/"unknown"/"deferred" 的取值 ===')
sus = df[df.val.fillna('').str.contains('not assess|unable|n/a|na$|unknown|defer|indetermin|not exam|cannot', regex=True)]
print(sus.to_string(index=False) if len(sus) else '  无')
sus.to_csv('D:/桌面/workbuddyzuopin/CPxiangmu/03_结果/_eicu_indeterminate_values.csv', index=False)

print('\n=== DOI 复核 ===')
for doi in ['10.2459/JCM.0000000000001907', '10.1093/ehjacc/zuae037', '10.1093/eurjcn/zvaf075']:
    try:
        m = json.load(urllib.request.urlopen('https://api.crossref.org/works/' + doi, timeout=25))['message']
        print(' ', doi, '->', (m.get('title') or [''])[0][:60], '|', (m.get('container-title') or [''])[0],
              '| v', m.get('volume'), '| p', m.get('page'))
    except Exception as e:
        print(' ', doi, 'ERR', e)
