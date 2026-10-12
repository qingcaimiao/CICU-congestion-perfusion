# -*- coding: utf-8 -*-
"""第三轮意见核实后的稿件同步（英文稿，第二批：结果/讨论/局限/摘要/图注/补充清单）。"""
import io

JCM = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
EN = JCM + '/Manuscript_JCM_EN.md'
LOG = []


def one(s, old, new, tag):
    if s.count(old) != 1:
        raise SystemExit('[%s] 匹配 %d 次\n%s' % (tag, s.count(old), old[:160]))
    LOG.append('ok  ' + tag)
    return s.replace(old, new)


en = io.open(EN, encoding='utf-8').read()

# ---------- 1. §3.6 充血段整体重写 ----------
old_cong = en.split('\n\n')
hit = [i for i, p in enumerate(old_cong) if p.startswith('Congestion, by contrast, could not be tested')]
assert len(hit) == 1, '充血段定位失败'
old_cong[hit[0]] = (
 'Congestion, by contrast, could not be tested in the same form. eICU-CRD contains no nurse-charted pitting-depth scale '
 'equivalent to the MIMIC-IV item, so the identical measurement is simply absent (Table 4, Table S3). Of the three alternative '
 'congestion signs available there, none reproduced the development-cohort gradient. Considered alone, peripheral oedema was '
 'associated with a mortality of 9.23% versus 12.67% (ratio 1.37), jugular venous distension with 9.18% versus 17.95% (1.95) and '
 'pulmonary crackles with 8.20% versus 14.61% (1.78) — all far weaker than the perfusion signal (5.44). Within the four-phenotype '
 'structure the congestion contrast was unstable across definitions: with oedema used to define congestion, mortality was 6.39% in '
 'dry-warm and 5.94% in wet-warm (difference −0.45 percentage points); with jugular venous distension, 5.52% and 15.46% (+9.94); with '
 'crackles, 5.35% and 9.07% (+3.72); and with the composite definition, 4.53% and 8.04% (+3.51). The contrast attributable to '
 'congestion therefore ranged from −0.45 to +9.94 percentage points and had no consistent direction of effect, whereas the contrast '
 'attributable to perfusion with congestion held absent was large and consistent under every definition (+26.9 to +30.6 percentage '
 'points). The 2 × 2 structure discriminated far better when driven by perfusion than by congestion.\n\n'
 'Part of this failure is misclassification rather than absence of signal. Because an undocumented congestion field cannot be '
 'distinguished from one that was examined and found negative, the composite definition assigns "no congestion" to patients in whom '
 'the relevant sign was never assessed; only 1,323 of the 27,757 cardiac ICU stays (4.8%) had all three fields recorded. When the '
 'analysis was restricted to the 954 stays with all three congestion fields documented — eliminating this source of error — the '
 'crude congestion contrast roughly doubled, from 8.12% versus 4.42% mortality to 9.13% versus 3.68%, and the adjusted odds ratio for '
 'congestion rose from 1.21 (95% CI 0.80 to 1.85) to 1.48 (0.85 to 2.59); the incremental AUROC nonetheless remained small and '
 'non-significant (+0.0032, 95% CI −0.0021 to +0.0085, versus +0.0012, −0.0011 to +0.0036, in the full analysable set) (Table S9D). '
 'Documentation incompleteness therefore attenuates but does not explain the failure of the congestion axis to transport.')
en = '\n\n'.join(old_cong)
LOG.append('ok  §3.6 充血段重写')

# ---------- 2. §3.6 轴分解段 ----------
en = one(en,
    'The same decomposition can be performed within the replication cohort (exploratory, by refitting in eICU-CRD rather than transferring coefficients; Table S8). Impaired perfusion alone raised the AUROC from 0.861 to 0.877 (ΔAUROC +0.0155, 95% CI +0.0030 to +0.0301), whereas the composite congestion definition alone raised it to 0.862 (ΔAUROC +0.0008, 95% CI −0.0018 to +0.0035, i.e. no discrimination at all); in a model containing both, the perfusion odds ratio was 3.24 (95% CI 1.92 to 5.47) and the congestion odds ratio 1.07 (0.63 to 1.80). Essentially all of the transportable incremental value therefore came from the perfusion axis.',
    'The same decomposition can be performed within the replication cohort (exploratory, by refitting in eICU-CRD rather than '
    'transferring coefficients; Table S8). Impaired perfusion alone raised the AUROC from 0.834 to 0.847 (ΔAUROC +0.0128, 95% CI '
    '+0.0015 to +0.0259), whereas the composite congestion definition alone raised it to 0.835 (ΔAUROC +0.0012, 95% CI −0.0011 to '
    '+0.0036, i.e. no discrimination); in a model containing both, the perfusion odds ratio was 3.15 and the congestion odds ratio '
    '1.09. Essentially all of the transportable incremental value therefore came from the perfusion axis.',
    '§3.6 轴分解段')

# ---------- 3. §3.6 外部模型段 ----------
old = [p for p in en.split('\n\n') if p.startswith('Of the 1,555 stays in which both axes were documented')]
assert len(old) == 1, '外部模型段定位失败'
new_par = (
 'Of the 1,555 stays in which both axes were documented (Table 4, Figure 2), 1,541 (152 in-hospital deaths) also met the '
 'pre-specified covariate-availability requirement and were used to evaluate the transferred model. Applying the MIMIC-IV '
 'coefficients unchanged to those 1,541 stays gave an external AUROC of **0.835** (versus an apparent 0.871 in development), an '
 'observed-to-expected ratio of **0.92**, and a calibration intercept of −0.44 and slope of 0.79 from logistic recalibration, so '
 'absolute risk was well calibrated despite the case-mix shift (mean predicted risk 10.7% versus observed 9.9%) (Figure 7B). '
 'Excluding temperature from the transferable set (the primary specification) rather than including it changed the external AUROC '
 'from 0.833 to 0.835. Discrimination was stable to the influence of individual centres: excluding each of the six contributing '
 'hospitals in turn moved the external AUROC between 0.786 and 0.846 (median 0.835), although one hospital (n = 84, 10 deaths) gave '
 '0.643 (Table S9E). The two analysis sets differed in case mix in ways relevant to the transferred model: the median minimum '
 'oxygen saturation was lower in the replication set (87% versus 93%), the maximum heart rate was higher (105 versus 95/min) and the '
 'phenotype was far more often classified as wet (wet-warm 42.4% versus 10.3%), reflecting the more sensitive composite congestion '
 'definition available in eICU-CRD (Table S5). The 1,555 analysable stays came from 6 of the 36 hospitals that contributed '
 'cardiac-ICU admissions (of 208 hospitals in eICU-CRD) (median 107 stays per hospital); because the analysable set is drawn from so '
 'few centres, hospital-level clustering is not modelled and hospital-level performance can only be described, not estimated '
 '(Table S9E).')
en = en.replace(old[0], new_par)
LOG.append('ok  §3.6 外部模型段')

# ---------- 4. 讨论开篇 ----------
en = one(en,
    'External replication, however, was **partial and informative**: the perfusion sign transported almost exactly, whereas the specific nurse-charted congestion measurement could not be reproduced — eICU-CRD simply does not contain it — and the alternative congestion signs available there did not reproduce the gradient.',
    'External replication, however, was **partial and informative**: the perfusion sign transported almost exactly, and the '
    'transferred model was well calibrated in the second database (observed-to-expected ratio 0.92); by contrast the specific '
    'nurse-charted congestion measurement could not be reproduced — eICU-CRD simply does not contain it — the alternative congestion '
    'signs available there gave inconsistent contrasts (from −0.45 to +9.94 percentage points) and congestion added no discrimination '
    'once perfusion was accounted for.',
    '讨论开篇')

# ---------- 5. 灌注轴段补检验 ----------
en = one(en,
    'obtained in a model in which the two signs were only weakly correlated (r = 0.10).',
    'obtained in a model in which the two signs were only weakly correlated (r = 0.10); the inequality of the two coefficients was '
    'formally confirmed (Wald χ² = 17.5, p < 0.0001; Table S9C).',
    '灌注轴段检验')

# ---------- 6. 记录依赖段补充 ----------
en = one(en,
    'We therefore suggest that bedside congestion phenotypes are *documentation-dependent*, and that apparent differences in prognostic performance between hospitals or datasets may reflect charting practice rather than biology.',
    'Two distinctions are worth drawing. First, our replication tested the construct of congestion with different instruments, and '
    'the failure could in principle lie in either. Because the crude and adjusted congestion contrasts roughly doubled — but the '
    'incremental discrimination did not become significant — once the analysis was restricted to stays in which all three congestion '
    'fields were actually documented (Table S9D), the results point to a contribution from both: incomplete documentation attenuates '
    'the measured association, yet a complete-but-different instrument still does not recover the development-cohort gradient. '
    'Second, a failure of the *congestion axis* to transport is not evidence that congestion is clinically unimportant; the '
    'development-cohort gradient is large and the wet-warm contrast is real there. We therefore suggest that bedside congestion '
    'phenotypes are *documentation-dependent*, and that apparent differences in prognostic performance between hospitals or datasets '
    'may reflect charting practice rather than biology.',
    '记录依赖段补充')

# ---------- 7. 局限 (i) 与 (iii) ----------
old_i = [p for p in en.split('\n\n') if p.startswith('**(i) Ascertainment.**')]
assert len(old_i) == 1
en = en.replace(old_i[0], (
 '**(i) Ascertainment.** Documentation of bedside signs is incomplete and non-random. The analysis set requiring both signs '
 'comprised 12,052 of 20,806 stays (57.9%), and the patients who were examined were **not** the sicker ones: their in-hospital '
 'mortality was 6.3% versus 9.3% in those excluded, although they received more organ support (mechanical ventilation 61.8% versus '
 '36.7%) (Table S9A). Because the probability of being examined is itself related to the outcome, this is informative selection and '
 'can bias associations in either direction, so the estimates reported here apply to the examined subgroup rather than to all '
 'cardiac ICU admissions. Documentation differed by more than an order of magnitude between the two databases (oedema depth 69.1% '
 'versus 7.5% within the exposure window), and in eICU-CRD only 4.8% of stays had all three congestion fields recorded. The same '
 'sparsity restricted the congestion-trajectory analysis to 6,942 of 20,806 stays (33.4%) in MIMIC-IV and made it impossible in '
 'eICU-CRD [28]; because patients must survive long enough to have oedema documented in both the 0–24 h and the 24–72 h window, that '
 'analysis is additionally exposed to immortal-time bias, and its trajectory findings must be regarded as hypothesis-generating.'))
LOG.append('ok  局限(i)')

old_iii = [p for p in en.split('\n\n') if p.startswith('**(iii) Transportability and precision.**')]
assert len(old_iii) == 1
en = en.replace(old_iii[0], (
 '**(iii) Transportability and precision.** MIMIC-IV is a single centre. In eICU-CRD the subset with both axes documented comprised '
 '1,555 stays (156 deaths), of which 1,541 (152 deaths) were used to evaluate the transferred 18-covariate model, giving an external '
 'events-per-variable ratio of 8.4; those stays came from only 6 of the 36 hospitals that contributed cardiac-ICU admissions, so '
 'hospital-level clustering was not modelled and hospital-level variation could not be estimated, although excluding each hospital in '
 'turn left external discrimination between 0.786 and 0.846 (Table S9E). The transferred model was well calibrated overall '
 '(observed-to-expected ratio 0.92, calibration slope 0.79), but this is an average across six hospitals and does not establish '
 'calibration in any new centre. Temperature — a prespecified candidate covariate, available in only 31.1% of the replication set — '
 'was excluded from the transferable set, so the external estimate does not include its contribution. Three prespecified comorbidities '
 '(coronary heart disease, diabetes and acute kidney injury) were extracted but not carried into the model, so residual confounding by '
 'these conditions is possible.'))
LOG.append('ok  局限(iii)')

# ---------- 8. 补充材料清单 ----------
en = one(en,
    'Table S8: contribution of each axis of the phenotype to discrimination, in the development cohort and by refitting within the replication cohort.',
    'Table S8: contribution of each axis of the phenotype to discrimination, in the development cohort and by refitting within the '
    'replication cohort. Table S9: additional robustness analyses — (A) characteristics of included versus excluded patients, '
    '(B) E-values, (C) formal test of the difference between the two axes, (D) completeness of congestion documentation in eICU-CRD '
    'and the corresponding sensitivity analysis, (E) leave-one-hospital-out external performance, (F) oedema cut-point sensitivity and '
    'temporal stability, and (G) missing-data handling.',
    '补充清单')

# ---------- 9. 摘要 ----------
en = one(en,
    'Only the perfusion axis transported: in eICU-CRD the gradient reproduced (3.86% vs. 27.36%; external AUROC 0.855), whereas the nurse-charted congestion measurement is absent, no alternative congestion sign reproduced the gradient, and congestion added no discrimination (+0.0008, 95% CI −0.0018 to +0.0035).',
    'Only the perfusion axis transported: in eICU-CRD the gradient reproduced (6.24% vs. 33.96% mortality; external AUROC 0.835, '
    'observed-to-expected ratio 0.92), whereas the nurse-charted congestion measurement is absent there, the alternative congestion '
    'signs gave inconsistent contrasts, and congestion added no discrimination (+0.0012, 95% CI −0.0011 to +0.0036).',
    '摘要结果')

# ---------- 10. 图 7 图注 ----------
en = one(en,
    'replication cohort (n = 1,541; coefficients transferred unchanged, external AUROC 0.855, calibration slope 0.83, intercept −0.87, observed-to-expected ratio 0.66). Panel B shows systematic over-prediction in the replication setting.',
    'replication cohort (n = 1,541; coefficients transferred unchanged, external AUROC 0.835, calibration slope 0.79, '
    'intercept −0.44, observed-to-expected ratio 0.92). Panel B shows that absolute risk was well calibrated in the replication '
    'setting despite the case-mix shift.',
    '图7图注')

io.open(EN, 'w', encoding='utf-8').write(en)
print('\n'.join(LOG)); print('\n第二批 %d 项完成' % len(LOG))
