# -*- coding: utf-8 -*-
"""第四轮：同步 GitHub 本地副本（结果表、脚本、README 数字）并提交"""
import io, os, shutil, subprocess

W = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58'
G = 'D:/桌面/workbuddyzuopin/CPxiangmu/06_GitHub_CP'
RES = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
NL = chr(10)

SCRIPTS = ['round4_group_tables.py', 'fix_eicu_outcome.py', 'robustness_round3.py',
           'robustness_C.py', 'robustness_missing.py', 'tableS9.py', 'axis_contribution.py']
TABLES = ['T_edema_mimic.csv', 'T_cr_mimic.csv', 'T_quadrant_mimic_ci.csv', 'T_quadrant_eicu_composite.csv',
          'TableS3_final.csv', 'TableS3_eicu_definitions_full.csv', 'Table4_eicu_replication.csv',
          'T_eicu_single_sign.csv', 'eicu_documentation_rates.json', 'axis_contribution_eicu.csv',
          'TableS7B_sensitivity.csv', 'TableS9.md', 'TableS8.md', 'TableS7.md',
          'TableS7A_plausibility_screen.csv', 'screening_records_mimic.csv']
for f in SCRIPTS:
    if os.path.exists(W + '/' + f):
        shutil.copy2(W + '/' + f, G + '/code/' + f)
for f in TABLES:
    if os.path.exists(RES + '/' + f):
        shutil.copy2(RES + '/' + f, G + '/results/' + f)

p = G + '/README.md'
r = io.open(p, encoding='utf-8').read()
reps = [
    ('| Discrimination | AUROC 0.858 → **0.871** with phenotype | external AUROC **0.855** |',
     '| Discrimination | AUROC 0.858 → **0.871** with phenotype | external AUROC **0.835** |'),
    ('| Calibration on transfer | — | O:E 0.66, slope 0.83, intercept −0.87 |',
     '| Calibration on transfer | — | O:E 0.92, slope 0.79, intercept −0.44 |'),
    ('* The **perfusion** axis transported almost exactly (3.86% vs 27.36%)',
     '* The **perfusion** axis transported almost exactly (6.24% vs 33.96%)'),
]
for a, b in reps:
    if a in r:
        r = r.replace(a, b)
    else:
        print('  （跳过，未找到）', a[:50])
# 结局口径说明
anchor = '* The **perfusion** axis transported'
add = ('* Outcome is **in-hospital death** (MIMIC-IV `hospital_expire_flag`; eICU-CRD `hospitaldischargestatus`), '
       'not ICU-level death: 2,666 in-hospital deaths vs 1,727 unit-level deaths in the cardiac-ICU cohort.' + NL)
if 'not ICU-level death' not in r:
    r = r.replace(anchor, add + anchor)
io.open(p, 'w', encoding='utf-8').write(r)
print('README 已更新')


def git(*a):
    q = subprocess.run(['git'] + list(a), cwd=G, capture_output=True, text=True)
    print('git', ' '.join(a[:3]), '->', (q.stdout or q.stderr).strip()[:200])


git('add', '-A')
git('-c', 'user.name=Qingcai Miao', '-c', 'user.email=qingcaimiao@users.noreply.github.com', 'commit', '-m',
    'Align all derived tables with the hospital-level outcome\n\n'
    '- restate the MIMIC-IV oedema-grade and capillary-refill mortality on the primary\n'
    '  analysis set (n=12,052) instead of the wider sign-documented sets\n'
    '- rebuild supplementary Table S3 (four congestion definitions) and Table S8 panel B\n'
    '  from the hospital-level deaths; Table S7B sensitivity refreshed\n'
    '- document the transferred-model covariate count (19: 18 continuous + sex) and the four\n'
    '  covariates that were not transportable\n'
    '- add per-cell 95% CIs and the exploratory label to the eICU four-phenotype table')
git('log', '--oneline', '-3')
