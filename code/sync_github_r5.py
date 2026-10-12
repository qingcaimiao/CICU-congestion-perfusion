# -*- coding: utf-8 -*-
"""第五轮：同步 GitHub 本地副本（脚本、结果、图件说明）并提交"""
import io, os, shutil, subprocess

W = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58'
G = 'D:/桌面/workbuddyzuopin/CPxiangmu/06_GitHub_CP'
RES = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
NL = chr(10)

for f in ['figures_cp.py', 'fig3_redo.py', 'tables_cp.py', 'jcm_figures.py', 'jcm_fig_renumber.py',
          'build_cp_eicu.py', 'redraw_shap.py', 'round5_check_a.py', 'round5_check_b.py', 'round5_check_c.py']:
    if os.path.exists(W + '/' + f):
        shutil.copy2(W + '/' + f, G + '/code/' + f)
for f in ['TableS3_final.csv', 'TableS3_eicu_definitions_full.csv', 'Table4_eicu_replication.csv',
          'T_eicu_single_sign.csv', 'eicu_documentation_rates.json', '_eicu_indeterminate_values.csv',
          'T_shap_importance.csv', 'TableS9.md']:
    if os.path.exists(RES + '/' + f):
        shutil.copy2(RES + '/' + f, G + '/results/' + f)

p = G + '/README.md'
r = io.open(p, encoding='utf-8').read()
add = ('* eICU-CRD `physicalExam` uses a **closed value domain** for these fields (jugular venous distension: 2 values; '
       'peripheral perfusion: 4; peripheral oedema: 12; pulmonary auscultation: 22), and contains no *not assessed / NA / '
       'unable to assess* value anywhere — so an unrecorded field is never coded as positive.' + NL)
if 'closed value domain' not in r:
    anchor = '* Outcome is **in-hospital death**'
    r = r.replace(anchor, add + anchor)
io.open(p, 'w', encoding='utf-8').write(r)
print('README ok')


def git(*a):
    q = subprocess.run(['git'] + list(a), cwd=G, capture_output=True, text=True)
    print('git', ' '.join(a[:3]), '->', (q.stdout or q.stderr).strip()[:220])


git('add', '-A')
git('-c', 'user.name=Qingcai Miao', '-c', 'user.email=qingcaimiao@users.noreply.github.com', 'commit', '-m',
    'Fix the calibration panel and harden the exposure definitions\n\n'
    '- figures_cp.py: the external calibration panel used 1,555 stays instead of 1,541 because the\n'
    '  availability screen ran after median imputation and because the eICU weight column was\n'
    '  named admissionweight rather than adm_weight; the screen now runs before imputation and two\n'
    '  assertions pin the panel to the saved predictions (n = 1,541, external AUROC 0.835)\n'
    '- jcm_fig_renumber.py is now non-destructive: it stages all ten final names before replacing\n'
    '  anything, so re-running it can no longer delete the finished figures\n'
    '- document that the eICU-CRD physicalExam value domains are closed and contain no indeterminate\n'
    '  category, and that seven prespecified covariates did not enter the transferred model')
git('log', '--oneline', '-3')
