# -*- coding: utf-8 -*-
"""第六轮：补充材料与 TRIPOD —— 迁移模型 22 参数口径、院级 AUROC、完整案例外部性能、
   flushed/局限水肿敏感性、Table S3 说明"""
import io, os, shutil, json
import pandas as pd

J = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
RES = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
S = 'Supplementary_Tables_JCM.md'
NL = chr(10)
LOG = []
p = os.path.join(J, S)
s = io.open(p, encoding='utf-8').read()
if not os.path.exists(p + '.bak_r6'):
    shutil.copyfile(p, p + '.bak_r6')

r6 = json.load(open(RES + '/round6_checks.json'))
cc = r6['complete_case']
ph = pd.read_csv(RES + '/TableS9E_per_hospital.csv')

# ---- 1. 参数基数（19 → 22）----
pairs = [
    ("The transferred model contains 19 covariates (the 18 continuously measured variables plus sex).",
     "The transferred model contains 22 estimated parameters excluding the intercept (the 18 continuously measured variables, sex and the three phenotype indicators)."),
    ("B. Transferred model (19 covariates: 18 continuous variables plus sex)",
     "B. Transferred model (congestion–perfusion model: 18 continuous variables, sex and three phenotype indicators; 22 parameters excluding the intercept)"),
    ("| External AUROC (19 covariates) | 0.835 | 0.832 | 0.002 |",
     "| External AUROC (transferred congestion–perfusion model) | 0.835 | 0.832 | 0.002 |"),
    ("The transferred 19-covariate model, applied unchanged",
     "The transferred congestion–perfusion model (22 parameters excluding the intercept), applied unchanged"),
]
for old, new in pairs:
    n = s.count(old)
    if n == 0 and new in s:
        continue
    assert n >= 1, '未匹配 -> %r' % old[:70]
    s = s.replace(old, new)
LOG.append('ok  参数基数 19→22')

# ---- 2. Table S9(E)：逐院 AUROC ----
i = s.index('**(E) Leave-one-hospital-out external performance (eICU-CRD).**')
j = s.index(NL + NL + '**(F)', i)
block = ['**(E) External performance, leave-one-out, and per-centre estimates (eICU-CRD).** The transferred '
         'congestion–perfusion model (22 parameters excluding the intercept), applied unchanged; hospitals are identified '
         'by their eICU-CRD hospital identifier. Per-centre AUROC is given where at least 5 deaths occurred in that centre; '
         'the two smallest centres (n = 12 with 2 deaths and n = 1 with 0 deaths) do not support an estimate.',
         '',
         '| Hospital | Stays | Deaths | Mortality (%) | AUROC (per centre) |',
         '|---|---|---|---|---|']


def phcell(v):
    return 'not estimable' if isinstance(v, str) else ('%.3f' % float(v))


for r in ph.itertuples():
    block.append('| %d | %d | %d | %.2f | %s |' % (r.hospital, r.n, r.deaths, r.mortality, phcell(r.auc)))
block += ['| All six (n = 1,541) | 1,541 | 152 | 9.86 | 0.835 |',
          '| Leave-one-hospital-out range | — | — | — | 0.786–0.846 (median 0.835) |', '']
s = s[:i] + NL.join(block) + s[j:]
LOG.append('ok  表 S9E 逐院 AUROC')

# ---- 3. Table S9(G)：完整案例下的迁移模型外部性能 ----
old_g = '| Replication — complete cases | 1432 | 136 | — | 0.85 | — |'
assert s.count(old_g) == 1, 'S9G 行未匹配'
s = s.replace(old_g,
              '| Replication — complete cases (refit within eICU-CRD) | 1432 | 136 | — | 0.85 | — |' + NL
              + '| Replication — complete cases, **transferred model** | 1432 | 136 | 0.836 | 0.836 | — |')
old_note = ('For the replication cohort the AUROC shown is from a model refitted within eICU-CRD using the '
            'development-cohort standardisation constants; it is given only to compare the two missing-data strategies '
            'and is not the performance of the transferred model (Table 3).')
assert s.count(old_note) == 1
s = s.replace(old_note,
              'For the replication cohort the third row is from a model refitted within eICU-CRD using the development-cohort '
              'standardisation constants and is given only to compare the two missing-data strategies; the fourth row is the '
              '**transferred congestion–perfusion model** evaluated in the 1,432 complete cases, giving an external AUROC of '
              '0.836 and an observed-to-expected ratio of 0.88 (versus 0.835 and 0.92 in the primary ≥60%-availability set). '
              'Multiple imputation was not performed; the two missing-data strategies therefore agree closely, but a residual '
              'bias from the pragmatic availability rule cannot be excluded.')
LOG.append('ok  表 S9G 完整案例外部性能')

# ---- 4. Table S3：flushed / 局限水肿的敏感性说明 ----
old_tail = ('Perfusion was documented in %.1f%% of stays.')
i2 = s.index('Only stays in which congestion and perfusion were both *documented* are included.')
j2 = s.index(NL + NL, i2)
s = s[:j2] + s[j2:].replace(NL + NL, NL + NL, 1)
anchor = 'The penultimate column isolates the congestion effect with perfusion held adequate'
add = ('Two definitional sensitivities were quantified. First, "extremities flushed" counts as impaired perfusion in the '
       'primary analysis, although it is vasodilatation rather than hypoperfusion; it occurred in exactly 1 of the 1,558 '
       'perfusion-documented stays in the window (Table S10), and removing it changed the perfusion contrast from 5.43-fold '
       '(33.96% vs. 6.25%) to 5.46-fold (34.12% vs. 6.25%) and the four-cell mortalities from 4.53/8.03/31.67/35.10 from '
       '4.53/8.04/31.67/34.87. Second, "localized swelling" and unilateral or upper-extremity oedema are counted as negative '
       'in the primary analysis (they are not bilateral pitting oedema); 10 stays were affected, and counting them as positive '
       'changed the four-cell mortalities only to 4.43/8.10/32.20/34.87. Neither choice materially affects the results. ')
assert s.count(anchor) == 1
s = s.replace(anchor, add + anchor)
LOG.append('ok  表 S3 敏感性说明')
io.open(p, 'w', encoding='utf-8').write(s)

# ---- 5. TRIPOD ----
p = os.path.join(J, 'TRIPOD_AI_Checklist.md')
t = io.open(p, encoding='utf-8').read()
if not os.path.exists(p + '.bak_r6'):
    shutil.copyfile(p, p + '.bak_r6')
tp = [
    ("and 8.0 for the transferred model (19 covariates: the 18 continuously measured variables plus sex)",
     "and 6.9 for the transferred congestion-perfusion model (22 parameters excluding the intercept: the 18 continuously measured variables, sex and three phenotype indicators)"),
    ("the transferred model (19 covariates: 18 continuous variables plus sex, panel B)",
     "the transferred congestion-perfusion model (22 parameters excluding the intercept: 18 continuous variables, sex and three phenotype indicators, panel B)"),
]
for old, new in tp:
    n = t.count(old)
    if n == 0 and new in t:
        continue
    assert n >= 1, '[TRIPOD] 未匹配 -> %r' % old[:70]
    t = t.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(t)
LOG.append('ok  TRIPOD')

print(NL.join(LOG))
print('S9E 行数:', len(ph))
