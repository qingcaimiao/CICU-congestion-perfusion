# -*- coding: utf-8 -*-
"""第五轮：补充材料 —— 表 S3 增加阳性/阴性/未记录三分类列；表 S9B 补 E 值"""
import io, os, shutil, json
import pandas as pd

J = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
RES = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
S = 'Supplementary_Tables_JCM.md'
NL = chr(10)
LOG = []
p = os.path.join(J, S)
s = io.open(p, encoding='utf-8').read()
if not os.path.exists(p + '.bak_r5'):
    shutil.copyfile(p, p + '.bak_r5')

doc = json.load(open(RES + '/eicu_documentation_rates.json'))
full = pd.read_csv(RES + '/TableS3_eicu_definitions_full.csv')
final = pd.read_csv(RES + '/TableS3_final.csv')

NOTREC = {'Composite (any of the three)': round(100 - doc['any_congestion_field'], 1),
          'Jugular venous distension only': round(100 - doc['jvd'], 1),
          'Peripheral oedema only': round(100 - doc['edema'], 1),
          'Pulmonary crackles only': round(100 - doc['crackles'], 1)}

rows = []
for r in final.itertuples():
    g = full[full.definition == r.definition].set_index('cell')
    pos = int(g.loc['WetWarm', 'n'] + g.loc['WetCold', 'n'])
    neg = int(g.loc['DryWarm', 'n'] + g.loc['DryCold', 'n'])
    rows.append([r.definition, format(r.n, ','), r.deaths, format(pos, ','), format(neg, ','),
                 '%.2f' % r.dry_warm, '%.2f' % r.wet_warm, '%.2f' % r.dry_cold, '%.2f' % r.wet_cold,
                 '%+.2f' % r.wet_minus_dry_warm, '%+.2f' % r.dry_cold_minus_dry_warm,
                 '%.1f' % NOTREC[r.definition]])
hdr = ['Definition of congestion', 'n', 'Deaths', 'Congestion positive, n', 'Congestion negative, n',
       'Dry-warm (%)', 'Wet-warm (%)', 'Dry-cold (%)', 'Wet-cold (%)',
       'Wet-warm minus dry-warm (pp)', 'Dry-cold minus dry-warm (pp)',
       'Congestion field not recorded (% of 27,757)']
tbl = ('| ' + ' | '.join(hdr) + ' |' + NL + '|' + '|'.join(['---'] * len(hdr)) + '|' + NL
       + NL.join('| ' + ' | '.join(str(c) for c in row) + ' |' for row in rows))
i = s.index('| Definition of congestion |')
j = s.index(NL + NL + '---', i)
s = s[:i] + tbl + s[j:]

# 表题补充说明
old_cap = 'The penultimate column isolates the congestion effect with perfusion held adequate'
new_cap = ('Congestion positive and negative counts are within the analysed set for that definition, i.e. stays in which the '
           'relevant congestion field and perfusion were both documented; the last column gives, for reference, the proportion '
           'of all 27,757 cardiac-ICU stays in which that congestion field was not recorded at all, which is the misclassification '
           'the pre-specified composite definition has to tolerate. The penultimate column isolates the congestion effect with '
           'perfusion held adequate')
assert s.count(old_cap) == 1
s = s.replace(old_cap, new_cap)
LOG.append('ok  表 S3 三分类列')

# ---- 表 S9B 补 E 值 ----
EV = [('Oedema >=6 mm, like-for-like (OR 1.58, development)', 1.58, 1.27),
      ('Congestion term in the transferred model (OR 1.09, eICU-CRD)', 1.09, 0.71)]


def ev(orv, lo):
    if orv < 1:
        orv = 1 / orv
    point = orv + (orv * (orv - 1)) ** 0.5
    if lo >= 1:
        ci = lo + (lo * (lo - 1)) ** 0.5
    elif lo > 0:
        ci = 1.0
    else:
        ci = 1.0
    return point, ci


anchor = '| Wet-cold versus dry-warm, transferred model (OR 4.56, eICU-CRD) | 8.59 | 5.85 |'
assert s.count(anchor) == 1
add = []
for lab, orv, lo in EV:
    pt, ci = ev(orv, lo)
    add.append('| %s | %.2f | %s |' % (lab, pt, ('—' if ci is None else ('%.2f' % ci if ci > 1 else '1.00 (CI includes the null)'))) )
s = s.replace(anchor, anchor + NL + NL.join(add))
LOG.append('ok  表 S9B 补 E 值')
io.open(p, 'w', encoding='utf-8').write(s)
print(NL.join(LOG))
print('S3 新表：')
print(tbl.split(NL)[0][:200])
print(tbl.split(NL)[2])
