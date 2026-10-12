# -*- coding: utf-8 -*-
"""生成补充表 S9（第三轮稳健性分析 A–G）并追加到补充材料。"""
import io, os, shutil, json, pandas as pd

RES = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
JCM = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
rb = json.load(open(RES + '/R3_robustness.json'))
rc = json.load(open(RES + '/R3_robustness_C.json'))
rm = json.load(open(RES + '/R3_missing_data.json'))
tA = pd.read_csv(RES + '/R3_tableA_included_vs_excluded.csv')
tF = pd.read_csv(RES + '/R3_tableE_cutpoint.csv')
tT = pd.read_csv(RES + '/R3_tableE_time.csv')


def md(df):
    cols = list(df.columns)
    out = ['| ' + ' | '.join(cols) + ' |', '|' + '|'.join(['---'] * len(cols)) + '|']
    for _, r in df.iterrows():
        out.append('| ' + ' | '.join(str(r[c]) for c in cols) + ' |')
    return '\n'.join(out)


S = []
S.append('## Table S9. Additional robustness analyses\n')
S.append('**(A) Patients included in the analysis set versus those excluded.** Included = oedema grade and capillary refill time both charted within the −6 h to +24 h window (n = 12,052); excluded = all other first cardiac ICU stays (n = 8,754). Median values unless stated; p values from Mann–Whitney U or χ² tests.\n')
MAP = {'院内死亡 n (%)': 'In-hospital death, n (%)', '年龄 median': 'Age, years (median)',
       'ICU 住院时长 median': 'ICU length of stay, days (median)', '心率最高 median': 'Heart rate, maximum (median)',
       '肌酐最高 median': 'Creatinine, maximum (median)', '尿素氮最高 median': 'Urea nitrogen, maximum (median)',
       '有创机械通气 n (%)': 'Invasive mechanical ventilation, n (%)', '血管活性药 n (%)': 'Vasoactive drug infusion, n (%)',
       '心衰 n (%)': 'Congestive heart failure, n (%)', '慢性肾病 n (%)': 'Chronic kidney disease, n (%)'}
tA['变量'] = tA['变量'].map(lambda x: MAP.get(x, x))
tA['p'] = tA['p'].map(lambda x: '%.3f' % float(x) if float(x) >= 0.001 else ('%.1e' % float(x)).replace('e-0', ' × 10⁻').replace('e-', ' × 10⁻'))
tA = tA.rename(columns={'变量': 'Characteristic', '纳入组': 'Included (n = 12,052)', '排除组': 'Excluded (n = 8,754)', 'p': 'p'})
S.append(md(tA) + '\n')

S.append('**(B) E-values for the principal effect estimates.** E-values are approximate, treating the odds ratio as a risk ratio, and quantify how strong an unmeasured confounder would have to be, associated with both the sign and death, to explain the association away.\n')
ev = rb['E_values']
BN = {'湿冷型 OR 4.49': 'Wet-cold versus dry-warm (OR 4.49, development)',
      '干冷型 OR 3.20': 'Dry-cold versus dry-warm (OR 3.20, development)',
      '湿暖型 OR 1.63': 'Wet-warm versus dry-warm (OR 1.63, development)',
      '同尺度 CRT OR 3.11': 'Prolonged capillary refill, like-for-like (OR 3.11, development)',
      '外部迁移模型湿冷 OR 4.56': 'Wet-cold versus dry-warm, transferred model (OR 4.56, eICU-CRD)'}
rowsB = [{'Estimate': BN.get(k, k), 'E-value (point estimate)': v['point'], 'E-value (lower 95% CI bound)': v.get('ci', '—')} for k, v in ev.items()]
S.append(md(pd.DataFrame(rowsB)) + '\n')

S.append('**(C) Formal comparison of the two axes (development cohort).** In a single model containing both signs as binary terms, with the same 23 routine covariates.\n')
wb = rb['B_wald']; db = rb['B_dauc_diff']
rowsC = [{'Quantity': 'Wald test, H₀: β(capillary refill) = β(oedema ≥6 mm)', 'Value': 'χ² = %.1f, p < 0.0001' % wb['chi2']},
         {'Quantity': 'Ratio of odds ratios (perfusion / congestion)', 'Value': '%.2f (95%% CI %.2f–%.2f)' % (wb['or_ratio'], wb['or_ratio_ci'][0], wb['or_ratio_ci'][1])},
         {'Quantity': 'ΔAUROC, perfusion alone', 'Value': '%+.4f' % db['perfusion']},
         {'Quantity': 'ΔAUROC, congestion alone', 'Value': '%+.4f' % db['congestion']},
         {'Quantity': 'Difference between the two incremental AUROCs (paired bootstrap, 2,000 replicates)', 'Value': '%+.4f (95%% CI %+.4f to %+.4f)' % (db['diff'], db['ci'][0], db['ci'][1])}]
S.append(md(pd.DataFrame(rowsC)) + '\n')

S.append('**(D) Completeness of congestion documentation in eICU-CRD, and the resulting sensitivity analysis.** An undocumented field cannot be distinguished from a field that was examined and found negative; the pre-specified composite definition therefore treats it as negative.\n')
rowsD = [{'Quantity': 'Cardiac ICU stays', 'Value': '27,757'},
         {'Quantity': '→ none of the three congestion fields recorded', 'Value': '25,064 (90.3%)'},
         {'Quantity': '→ one field recorded', 'Value': '565 (2.0%)'},
         {'Quantity': '→ two fields recorded', 'Value': '805 (2.9%)'},
         {'Quantity': '→ all three fields recorded', 'Value': '1,323 (4.8%)'},
         {'Quantity': 'Analysable set (perfusion + ≥1 congestion field), n / deaths', 'Value': '%d / %d' % (rc['any_field']['n'], rc['any_field']['deaths'])},
         {'Quantity': '　mortality, congestion present vs absent', 'Value': '%.2f%% vs %.2f%%' % (rc['any_field']['quad_WetWarm']['mort'], rc['any_field']['quad_DryWarm']['mort'])},
         {'Quantity': '　congestion, ΔAUROC (95% CI)', 'Value': '%+.4f (%+.4f to %+.4f)' % (rc['any_field']['congestion']['dauc'], rc['any_field']['congestion']['dauc_ci'][0], rc['any_field']['congestion']['dauc_ci'][1])},
         {'Quantity': '　congestion, adjusted OR (95% CI)', 'Value': '%.2f (%.2f–%.2f), p = %.3f' % (rc['any_field']['congestion']['or'], rc['any_field']['congestion']['or_ci'][0], rc['any_field']['congestion']['or_ci'][1], rc['any_field']['congestion']['p'])},
         {'Quantity': 'Restricted set (all three fields recorded), n / deaths', 'Value': '%d / %d' % (rc['all_three']['n'], rc['all_three']['deaths'])},
         {'Quantity': '　mortality, congestion present vs absent', 'Value': '%.2f%% vs %.2f%%' % (rc['all_three']['quad_WetWarm']['mort'], rc['all_three']['quad_DryWarm']['mort'])},
         {'Quantity': '　congestion, ΔAUROC (95% CI)', 'Value': '%+.4f (%+.4f to %+.4f)' % (rc['all_three']['congestion']['dauc'], rc['all_three']['congestion']['dauc_ci'][0], rc['all_three']['congestion']['dauc_ci'][1])},
         {'Quantity': '　congestion, adjusted OR (95% CI)', 'Value': '%.2f (%.2f–%.2f), p = %.3f' % (rc['all_three']['congestion']['or'], rc['all_three']['congestion']['or_ci'][0], rc['all_three']['congestion']['or_ci'][1], rc['all_three']['congestion']['p'])}]
S.append(md(pd.DataFrame(rowsD)) + '\n')

S.append('**(E) Leave-one-hospital-out external performance (eICU-CRD).** The transferred 18-covariate model, applied unchanged; hospitals are identified by their eICU-CRD hospital identifier.\n')
lo = rb['D_loo']
rowsE = [{'Hospital': int(h), 'Deaths': int(n)} for h, n in lo['hospitals'].items()]
rowsE += [{'Hospital': 'All six (n = 1,541)', 'Deaths': 152},
          {'Hospital': 'External AUROC, full set', 'Deaths': '%.3f' % lo['full']},
          {'Hospital': 'External AUROC, leave-one-hospital-out range', 'Deaths': '%.3f–%.3f (median %.3f)' % (lo['min'], lo['max'], lo['median'])}]
S.append(md(pd.DataFrame(rowsE)) + '\n')

S.append('**(F) Oedema cut-point sensitivity and temporal stability.**\n')
S.append(md(tF) + '\n')
S.append(md(tT) + '\n')

S.append('**(G) Missing-data handling.** Main analysis, median imputation for missing covariates (development) or ≥60% covariate availability with median imputation (replication); sensitivity, complete cases only.\n')
rowsG = [{'Analysis set': 'Development — median imputation (primary)', 'n': rm['mimic_imputed']['n'], 'Deaths': rm['mimic_imputed']['deaths'],
          'AUROC, routine': rm['mimic_imputed']['auc_base'], 'AUROC, +phenotype': rm['mimic_imputed']['auc_pheno'],
          'ΔAUROC (95% CI)': '%+.4f (%+.4f to %+.4f)' % (rm['mimic_imputed']['dauc'], rm['mimic_imputed']['dauc_ci'][0], rm['mimic_imputed']['dauc_ci'][1])},
         {'Analysis set': 'Development — complete cases', 'n': rm['mimic_complete']['n'], 'Deaths': rm['mimic_complete']['deaths'],
          'AUROC, routine': rm['mimic_complete']['auc_base'], 'AUROC, +phenotype': rm['mimic_complete']['auc_pheno'],
          'ΔAUROC (95% CI)': '%+.4f (%+.4f to %+.4f)' % (rm['mimic_complete']['dauc'], rm['mimic_complete']['dauc_ci'][0], rm['mimic_complete']['dauc_ci'][1])},
         {'Analysis set': 'Replication — ≥60% availability + imputation (primary)', 'n': rm['eicu_ge60']['n'], 'Deaths': rm['eicu_ge60']['deaths'],
          'AUROC, routine': '—', 'AUROC, +phenotype': rm['eicu_ge60']['auc'], 'ΔAUROC (95% CI)': '—'},
         {'Analysis set': 'Replication — complete cases', 'n': rm['eicu_complete']['n'], 'Deaths': rm['eicu_complete']['deaths'],
          'AUROC, routine': '—', 'AUROC, +phenotype': rm['eicu_complete']['auc'], 'ΔAUROC (95% CI)': '—'}]
S.append(md(pd.DataFrame(rowsG)) + '\n')
S.append('For the replication cohort the AUROC shown is from a model refitted within eICU-CRD using the development-cohort standardisation constants; it is given only to compare the two missing-data strategies and is not the performance of the transferred model (Table 3).\n')

txt = '\n'.join(S)
open(RES + '/TableS9.md', 'w', encoding='utf-8').write(txt)

P = JCM + '/Supplementary_Tables_JCM.md'
sup = io.open(P, encoding='utf-8').read()
if not os.path.exists(P + '.bak_r3'):
    shutil.copyfile(P, P + '.bak_r3')
if 'Table S9.' not in sup:
    sup = sup.rstrip('\n') + '\n\n' + txt
    io.open(P, 'w', encoding='utf-8').write(sup)
    print('已追加 Table S9')
else:
    print('Table S9 已存在')
print(txt[:1500])
