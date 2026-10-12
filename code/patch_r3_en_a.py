# -*- coding: utf-8 -*-
"""第三轮意见核实后的稿件同步（英文稿）。"""
import io, os, shutil

JCM = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
EN = JCM + '/Manuscript_JCM_EN.md'
LOG = []


def one(s, old, new, tag):
    if s.count(old) != 1:
        raise SystemExit('[%s] 匹配 %d 次\n%s' % (tag, s.count(old), old[:150]))
    LOG.append('ok  ' + tag)
    return s.replace(old, new)


def para(s, prefix, new_para, tag):
    parts = s.split('\n\n')
    hit = [i for i, p in enumerate(parts) if p.startswith(prefix)]
    if len(hit) != 1:
        raise SystemExit('[%s] 段落匹配 %d 次' % (tag, len(hit)))
    parts[hit[0]] = new_para
    LOG.append('ok  ' + tag)
    return '\n\n'.join(parts)


en = io.open(EN, encoding='utf-8').read()

# ---------- 1. 结局字段 ----------
en = one(en,
    'The primary outcome was **in-hospital death** (*hospital_expire_flag* in MIMIC-IV; unit discharge status in eICU-CRD), ascertained over the **entire hospitalisation**, not restricted to the ICU stay.',
    'The primary outcome was **in-hospital death** (*hospital_expire_flag* in MIMIC-IV; *hospitaldischargestatus* in eICU-CRD), ascertained over the **entire hospitalisation**, not restricted to the ICU stay.',
    '结局字段')
en = one(en,
    'Because death is ascertained after discharge from the ICU, ICU discharge is not a competing event for the primary outcome; this also makes the outcome free from the date-shifting applied to MIMIC timestamps.',
    'Because death is ascertained after discharge from the ICU, ICU discharge is not a competing event for the primary outcome; this also makes the outcome free from the date-shifting applied to MIMIC timestamps. In eICU-CRD the hospital-level discharge status was used rather than the unit-level status, so that the outcome is defined identically in the two databases; the 1,727 unit-level deaths were therefore superseded by the 2,666 hospital-level deaths.',
    '结局口径说明')

# ---------- 2. 协变量段 ----------
en = para(en, 'Covariates were selected a priori', (
 'Covariates were selected a priori and restricted to variables routinely available in the first 24 h in both databases. '
 'The primary model contained **23 covariates**: age, sex, admission weight, heart rate (minimum and maximum), systolic blood '
 'pressure (minimum), mean arterial pressure (minimum), respiratory rate (maximum), oxygen saturation (minimum), creatinine '
 '(maximum), urea nitrogen (maximum), sodium (minimum), potassium (maximum), chloride (minimum), bicarbonate (minimum), '
 'haemoglobin (minimum), white blood cell count (maximum), platelet count (minimum) and glucose (maximum), together with '
 'invasive mechanical ventilation, any vasoactive drug infusion, congestive heart failure and chronic kidney disease (ICD-9/10 '
 'codes). Temperature was prespecified as a candidate covariate but was excluded from the primary model because it was available '
 'in only 31.1% of the replication set; it is reported only in the sensitivity analysis of the transferable set. Coronary heart '
 'disease, diabetes mellitus and acute kidney injury were extracted but not retained, so that the development and transferable '
 'models share the same core; this leaves the adjustment set narrower than might be desired and is acknowledged as a limitation. '
 'The complete list of the 23 covariates, with standardisation constants and coefficients, is given in Table S6.'),
 '协变量段')

# ---------- 3. 缺失数据 ----------
en = one(en,
    'The main analysis used complete cases. Two-sided α was 0.05.',
    'Missing values among the model covariates were handled by median imputation in both databases (the largest missing fraction '
    'in the development analysis set was 4.0%). For the replication cohort a stay was retained if at least 60% of the transferable '
    'covariates were recorded, with median imputation for the remainder; this two-part rule is a pragmatic device to avoid dropping '
    'most of a sparse cohort, and it is not a standard missing-data method, so a complete-case analysis was performed in each '
    'database as a sensitivity analysis (Table S9G). Two-sided α was 0.05.',
    '缺失数据')

# ---------- 4. 新增统计方法说明 ----------
en = one(en,
    'because the spline and the categorical specification address different questions, both are reported and neither replaces the other.',
    'because the spline and the categorical specification address different questions, both are reported and neither replaces the '
    'other. The two axes were compared formally rather than by inspection of overlapping confidence intervals: in a model containing '
    'both signs as binary terms the equality of the two coefficients was tested with a Wald test, and the difference between their '
    'incremental AUROCs was estimated by paired bootstrap (2,000 replicates). E-values were calculated for the principal odds ratios '
    'as a quantified assessment of unmeasured confounding. As a secondary and purely descriptive check on variable importance, a '
    'random forest was fitted to the same covariates in the development set and features were ranked by mean absolute SHAP value '
    '(400 trees, minimum leaf size 10, fixed random seed); this analysis was not used for variable selection and contributes no '
    'performance estimate.',
    '统计方法补充')

# ---------- 5. §3.1 纳入 vs 排除 + E-value ----------
en = one(en,
    'With 758 events, the events per variable (EPV) was 29.2 for the phenotype model (26 covariates, excluding the intercept) and 33.0 for the routine-variable model (23 covariates, excluding the intercept).',
    'With 758 events, the events per variable (EPV) was 29.2 for the phenotype model (26 covariates, excluding the intercept) and '
    '33.0 for the routine-variable model (23 covariates, excluding the intercept). Patients in whom both signs were recorded differed '
    'from those in whom they were not: they were slightly younger (median 68 versus 69 years), had worse renal function (urea nitrogen '
    '18 versus 21 mg/dL; creatinine 1.0 versus 1.1 mg/dL) and were far more often mechanically ventilated (61.8% versus 36.7%) or '
    'receiving vasoactive drugs (54.4% versus 38.1%), yet their in-hospital mortality was **lower** (6.3% versus 9.3%; p = 3.2 × 10⁻¹⁶; '
    'Table S9A). Because the probability of being examined was related to the outcome, the analysis set is a selected subgroup whose '
    'associations need not generalise to unexamined patients. E-values for the principal estimates were 8.45 for the wet-cold phenotype, '
    '5.85 for dry-cold, 2.64 for wet-warm and 5.67 for prolonged capillary refill, so an unmeasured confounder would have to be '
    'associated with both the sign and death by a factor of at least 2.6–8.5 to explain these associations away (Table S9B).',
    '纳入vs排除+E值')

# ---------- 6. eICU 队列死亡数 ----------
en = one(en,
    'The replication cohort comprised **27,757** cardiac ICU stays in eICU-CRD with 1,727 in-hospital deaths (6.2%). Documentation of the same bedside signs was far less complete: oedema in 7.5%, jugular venous distension in 5.3%, peripheral perfusion in 5.6% and lung auscultation in 9.3%.',
    'The replication cohort comprised **27,757** cardiac ICU stays in eICU-CRD with **2,666 in-hospital deaths (9.6%)**. Documentation '
    'of the same bedside signs was far less complete: oedema in 7.5%, jugular venous distension in 5.3%, peripheral perfusion in 5.6% '
    'and lung auscultation in 9.3%. Of the three congestion fields, 25,064 stays (90.3%) had none recorded, 565 had one, 805 had two and '
    '1,323 (4.8%) had all three; because a field that was not recorded cannot be distinguished from a field that was examined and found '
    'negative, the pre-specified composite definition treats an undocumented field as negative and therefore misclassifies some patients '
    '(Table S9D).',
    'eICU 队列')

# ---------- 7. §3.2 切点稳健性 ----------
en = one(en,
    'for dry-cold and 4.49 (3.15–6.41) for wet-cold (Table 2, Figure 5).',
    'for dry-cold and 4.49 (3.15–6.41) for wet-cold (Table 2, Figure 5). The cut-point was not tuned to the outcome: redefining '
    'congestion at grade ≥2 or ≥4 changed the incremental AUROC only from +0.0126 (at ≥3) to +0.0122 and +0.0136, and the mortality '
    'difference between oedema ≥6 mm and <6 mm was positive in every era of the database (+2.8 to +13.4 percentage points; Table S9F).',
    '切点稳健性')

# ---------- 8. like-for-like 正式检验 ----------
en = one(en,
    'the perfusion axis remained approximately twice as strong on a like-for-like scale, although the gap is smaller than the ordinal comparison suggested.',
    'the perfusion axis remained approximately twice as strong on a like-for-like scale, although the gap is smaller than the ordinal '
    'comparison suggested; the inequality of the two coefficients was confirmed by a Wald test (χ² = 17.5, p < 0.0001; Table S9C).',
    'like-for-like 检验')

# ---------- 9. 轴分解段补正式检验 ----------
en = one(en,
    'The perfusion sign therefore accounted for about four-fifths of the total incremental discrimination, and the four-phenotype structure improved on the perfusion sign alone only marginally.',
    'The perfusion sign therefore accounted for about four-fifths of the total incremental discrimination, and the four-phenotype '
    'structure improved on the perfusion sign alone only marginally. The difference between the axes is statistically supported, not '
    'merely numerical: their odds ratios were unequal in the same model (ratio 1.98, 95% CI 1.44 to 2.73; Wald p < 0.0001) and the '
    'difference between their incremental AUROCs was +0.0064 (95% CI +0.0016 to +0.0112) (Table S9C).',
    '轴分解检验')

# ---------- 10. Table 4 ----------
en = one(en,
    '**Table 4.** External replication in eICU-CRD (n = 1,555 stays with both congestion and perfusion documented; 110 deaths).',
    '**Table 4.** External replication in eICU-CRD (n = 1,555 stays with both congestion and perfusion documented; 156 in-hospital deaths).',
    '表4题注')
en = one(en, '| Dry-warm | 684 | 20 | 2.92% |', '| Dry-warm | 684 | 31 | 4.53% |', '表4 干暖')
en = one(en, '| Wet-warm | 659 | 32 | 4.86% |', '| Wet-warm | 659 | 53 | 8.04% |', '表4 湿暖')
en = one(en, '| Dry-cold | 60 | 15 | 25.00% |', '| Dry-cold | 60 | 19 | 31.67% |', '表4 干冷')
en = one(en, '| Wet-cold | 152 | 43 | 28.29% |', '| Wet-cold | 152 | 53 | 34.87% |', '表4 湿冷')

io.open(EN, 'w', encoding='utf-8').write(en)
print('\n'.join(LOG)); print('\n第一部分 %d 项完成' % len(LOG))
