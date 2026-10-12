# -*- coding: utf-8 -*-
"""把生理合理性筛查一轮的更新同步到 GitHub 本地仓库副本（不推送）。"""
import io, os, shutil, subprocess

W = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58'
G = 'D:/桌面/workbuddyzuopin/CPxiangmu/06_GitHub_CP'
RES = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'

CODE = ['build_cp.py', 'build_cp_eicu.py', 'screen_features.py', 'screen_features_eicu.py',
        'screen_counts_eicu.py', 'fix_eicu_temp.py', 'patch_temp.py',
        'analyze_cp2.py', 'analyze_cp_eicu.py', 'analyze_cp_eicu2.py', 'analyze_cp_traj2.py',
        'tables_cp.py', 'table1_cp.py', 'rebuild_table1.py', 'mk_supp2.py',
        'final_eicu_model.py', 'tableS56.py', 'tableS5_pred_dist.py', 'tableS7.py',
        'calib_fix.py', 'critique_checks.py', 'critique_eicu.py', 'verify_critique2.py',
        'sensitivity_raw_vs_screened.py',
        'figures_cp.py', 'fig3_redo.py', 'jcm_figures.py', 'jcm_fig_renumber.py',
        'build_mdpi_refs.py', 'refs_final_cp.py', 'verify_refs_cp.py']

RESULTS = ['T_calibration.csv', 'T_calibration_eicu.csv', 'T_cong_any_eicu.csv', 'T_cr_mimic.csv',
           'T_dca.csv', 'T_edema_eicu.csv', 'T_edema_grade_adjusted_OR.csv', 'T_edema_mimic.csv',
           'T_edema_sev_eicu.csv', 'T_eicu_congestion_definitions.csv',
           'T_eicu_congestion_definitions_full.csv', 'T_eicu_single_sign.csv', 'T_jvd_eicu.csv',
           'T_missingness.csv', 'T_perf_eicu.csv', 'T_ppv_npv.csv', 'T_quadrant_eicu.csv',
           'T_quadrant_eicu_composite.csv', 'T_quadrant_mimic.csv', 'T_shap_importance.csv',
           'T_trajectory_outcome.csv', 'T_trajectory_profile.csv',
           'Table1_baseline_by_quadrant.csv', 'Table2_adjusted_OR.csv', 'Table3_model_performance.csv',
           'Table4_eicu_replication.csv', 'Table1_manuscript_rows_EN.md', 'Table1_manuscript_rows_ZH.md',
           'TableS1_mimic_missingness.csv', 'TableS1b_eicu_missingness.csv',
           'TableS3_eicu_definitions_full.csv', 'TableS3_final.csv', 'TableS4_edema_value_frequency.csv',
           'TableS5_predictor_distributions.csv', 'TableS6_full_model_coefficients.csv',
           'TableS7A_plausibility_screen.csv', 'TableS7B_sensitivity.csv', 'TableS7.md',
           'screening_counts_mimic.csv', 'screening_counts_eicu.csv',
           'screening_records_mimic.csv', 'screening_records_eicu.csv',
           'sensitivity_raw_vs_screened.csv', 'sensitivity_raw_vs_screened.json',
           'cp_core_results.json', 'cp_eicu_final.json', 'cp_likeforlike.json', 'cp_trajectory.json',
           'refs_final.json', 'refs_verified.json']

os.makedirs(G + '/code', exist_ok=True)
os.makedirs(G + '/results', exist_ok=True)
for f in CODE:
    src = W + '/' + f
    if os.path.exists(src):
        shutil.copy2(src, G + '/code/' + f)
    else:
        print('缺脚本:', f)
for f in RESULTS:
    src = RES + '/' + f
    if os.path.exists(src):
        shutil.copy2(src, G + '/results/' + f)
    else:
        print('缺结果:', f)

# 稿件表格行副本（供复现 Table 1）
for a, b in [('_table1_en.md', 'Table1_manuscript_rows_EN.md'), ('_table1_zh.md', 'Table1_manuscript_rows_ZH.md')]:
    if os.path.exists(RES + '/' + a):
        shutil.copy2(RES + '/' + a, G + '/results/' + b)

# ---------- README ----------
P = G + '/README.md'
r = io.open(P, encoding='utf-8').read()


def rep(s, old, new, tag):
    assert old in s, '未找到 ' + tag
    return s.replace(old, new)


r = rep(r, '| Discrimination | AUROC 0.858 → **0.870** with phenotype | external AUROC **0.856** |',
           '| Discrimination | AUROC 0.858 → **0.871** with phenotype | external AUROC **0.855** |', 'README 判别力')
r = rep(r, '| Calibration on transfer | — | O:E 0.65, slope 0.76, intercept −0.97 |',
           '| Calibration on transfer | — | O:E 0.66, slope 0.83, intercept −0.87 |', 'README 校准')
r = rep(r, 'prolonged capillary refill (adjusted OR 3.05) contributed about twice as much as oedema ≥6 mm (1.58)',
           'prolonged capillary refill (adjusted OR 3.11) contributed about twice as much as oedema ≥6 mm (1.58)', 'README like-for-like')
r = rep(r, '''```
code/       analysis scripts (Python 3.13)
results/    aggregate outputs: every table value, confidence interval and model metric
docs/       data access notes and variable definitions
```''',
        '''```
code/       analysis scripts (Python 3.13)
results/    aggregate outputs: every table value, confidence interval and model metric
docs/       data access notes and variable definitions
```

Every continuous covariate is summarised after a pre-specified physiological plausibility screen
(values outside an adult ICU range are treated as charting errors and set to missing before the
per-stay minimum, maximum or mean is taken), and the version of every principal analysis that uses
the values exactly as charted is reported alongside it (`results/sensitivity_raw_vs_screened.csv`,
`results/TableS7*`). Ranges, excluded record counts and the sensitivity comparison are in Table S7.''', 'README 说明')
io.open(P, 'w', encoding='utf-8').write(r)
print('README 已更新')

# ---------- 本地提交 ----------
def git(*a):
    p = subprocess.run(['git'] + list(a), cwd=G, capture_output=True, text=True)
    print('git', ' '.join(a), '->', (p.stdout or p.stderr).strip()[:400])
    return p

git('add', '-A')
git('-c', 'user.name=Qingcai Miao', '-c', 'user.email=qingcaimiao@users.noreply.github.com',
    'commit', '-m', 'Re-run all analyses after a pre-specified physiological plausibility screen\n\n'
                    '- screen every continuous covariate against adult ICU plausibility ranges before\n'
                    '  per-stay aggregation (MIMIC-IV 1,029 MAP / 4,243 RR / 264 HR records excluded;\n'
                    '  eICU-CRD 6,737 MAP / 42,809 RR / 159 WBC records excluded)\n'
                    '- primary results: AUROC 0.858 -> 0.871 (dAUC +0.0126), temporal 0.851,\n'
                    '  external AUROC 0.855, O:E 0.66, slope 0.83\n'
                    '- as-charted sensitivity analysis added (results/TableS7B_sensitivity.csv)\n'
                    '- supplementary Table S7 added; repository copy of README updated')
git('log', '--oneline', '-3')
