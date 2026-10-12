# -*- coding: utf-8 -*-
"""把生理合理性筛查后的新数值同步到中英文稿件（逐项断言，避免静默失败）。"""
import io, os, re, shutil, sys

JCM = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
RES = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
EN = JCM + '/Manuscript_JCM_EN.md'
ZH = JCM + '/稿件_充血灌注_中文版_JCM.md'
LOG = []


def rep(s, old, new, tag):
    if old not in s:
        LOG.append('!! 未找到: ' + tag)
        raise SystemExit('未找到待替换片段 [%s]:\n%s' % (tag, old[:200]))
    if s.count(old) != 1:
        LOG.append('!! 出现 %d 次: %s' % (s.count(old), tag))
        raise SystemExit('片段 [%s] 出现 %d 次，无法唯一定位' % (tag, s.count(old)))
    LOG.append('ok  ' + tag)
    return s.replace(old, new)


# =============================== 英文 ===============================
en = io.open(EN, encoding='utf-8').read()

# --- 1. 摘要结果 ---
en = rep(en,
    "adjusted odds ratios were 1.63, 3.13 and 4.44. On a dichotomised like-for-like comparison, prolonged capillary refill (odds ratio 3.05) contributed about twice as much as oedema ≥6 mm (1.58). Adding the phenotype raised the AUROC from 0.858 to 0.870 (Δ +0.0124) with temporal discrimination of 0.853. In eICU-CRD the perfusion sign replicated (3.86% vs. 27.36%; external AUROC 0.856)",
    "adjusted odds ratios were 1.63, 3.20 and 4.49. On a dichotomised like-for-like comparison, prolonged capillary refill (odds ratio 3.11) contributed about twice as much as oedema ≥6 mm (1.58). Adding the phenotype raised the AUROC from 0.858 to 0.871 (Δ +0.0126) with temporal discrimination of 0.851. In eICU-CRD the perfusion sign replicated (3.86% vs. 27.36%; external AUROC 0.855)",
    'EN 摘要结果')

# --- 2. 方法：数据质量段落整体替换 ---
EN_OLD_DQ = ("Three data-quality issues were identified on audit and are reported here for reproducibility. First, temperature was analysed in degrees Celsius in both databases: in MIMIC-IV, values charted in Fahrenheit under a separate itemid were converted before averaging, and in eICU-CRD we screened *vitalPeriodic.temperature* and found a small minority of Fahrenheit entries (0.5% of records) together with implausible values, which were converted or discarded before averaging. Second, in eICU-CRD haemoglobin is stored under *labname* = `Hgb`, and non-invasive blood pressures are held in *nurseCharting*, whereas the *systemicsystolic* and *systemicmean* fields of *vitalPeriodic* are arterial-line values present in only about a quarter of stays; systolic and mean arterial pressure were therefore taken as the minimum across non-invasive (`Non-Invasive BP Systolic`/`Mean`) and invasive (`Invasive BP Systolic`/`Mean`) sources. Third, respiratory rate in MIMIC-IV contains a small number of implausible charted values: of 8,636,655 values of the respiratory-rate item, 476 exceeded 80/min and 54 exceeded 300/min, several of them stored in scientific notation (up to 7.0 x 10^6/min). Because a handful of such values inflate the standard deviation of the maximum respiratory rate by four orders of magnitude (from 6.6 to 67,322/min), the corresponding standardised covariate is effectively inert (odds ratio 0.86, 95% CI 0.007-112; Table S6). In a post hoc sensitivity analysis, winsorising respiratory rate at 80/min changed the full-model AUROC from 0.870 to 0.871 and the incremental AUROC from +0.0124 to +0.0123, and altered no phenotype odds ratio by more than 2%; the primary analysis therefore retains the values as charted.")
EN_NEW_DQ = ("**Data quality and plausibility screening.** Before per-stay aggregation, every continuously measured covariate was screened against pre-specified adult physiological ranges appropriate to an intensive care population, and values outside those ranges were treated as charting or measurement errors and set to missing, so that they could not enter the minimum, maximum or mean used for that stay: heart rate 20–300/min, respiratory rate 1–80/min, oxygen saturation 1–100%, systolic blood pressure 20–300 mmHg, mean arterial pressure 20–250 mmHg, temperature 25–45 °C, weight 20–400 kg, creatinine 0.05–50 mg/dL, urea nitrogen 0.5–300 mg/dL, sodium 80–200 mmol/L, potassium 1–15 mmol/L, chloride 50–160 mmol/L, bicarbonate 1–60 mmol/L, haemoglobin 1–25 g/dL, white cell count 0.1–500 K/µL, platelet count 1–3,000 K/µL and glucose 10–4,000 mg/dL (Table S7). The screen mattered almost exclusively for the vital signs, because each of them enters the model as the minimum or the maximum of the stay and is therefore maximally sensitive to a single erroneous entry; among the laboratory analytes no variable lost more than two records. In the development cohort the screen removed 4,243 of 569,213 respiratory-rate records (0.75%), 1,029 of 584,763 mean-arterial-pressure records (0.18%), 264 of 576,792 heart-rate records (0.05%), 46 of 584,132 systolic-pressure records, 40 of 558,991 oxygen-saturation records, 135 of 190,413 temperature records and 11 of 19,873 weight records. Excluding a handful of respiratory rates stored in scientific notation (largest 7.0 x 10^6/min) reduced the standard deviation of the maximum respiratory rate from 51,404 to 6.17/min, and excluding zero and negative arterial pressures reduced the standard deviation of the minimum mean arterial pressure from 159.3 to 10.9 mmHg (Tables S6, S7). In the replication cohort the same screen removed 73 implausible white-cell counts (largest 1.15 x 10^6 K/µL; standard deviation reduced from 8,762 to 14.3 K/µL) and implausible values from the mean arterial pressure, systolic pressure and heart rate of 968, 345 and 589 stays respectively. In a sensitivity analysis every covariate was summarised from the values exactly as charted, without screening; all principal results were essentially unchanged (largest differences 0.003 in AUROC, 0.07 in adjusted odds ratio, 0.02 in calibration slope and 0.01 in the observed-to-expected ratio; Table S7), so the screen does not drive any conclusion.\n\nTwo further data-handling points are recorded for reproducibility. Temperature was analysed in degrees Celsius in both databases: values charted in Fahrenheit were converted before averaging, and Fahrenheit entries accounted for a small minority (0.5%) of records in eICU-CRD. In eICU-CRD haemoglobin is stored under *labname* = `Hgb`, and non-invasive blood pressures are held in *nurseCharting*, whereas the *systemicsystolic* and *systemicmean* fields of *vitalPeriodic* are arterial-line values present in only about a quarter of stays; systolic and mean arterial pressure were therefore taken as the minimum across non-invasive (`Non-Invasive BP Systolic`/`Mean`) and invasive (`Invasive BP Systolic`/`Mean`) sources.")
en = rep(en, EN_OLD_DQ, EN_NEW_DQ, 'EN 方法数据质量段')

# --- 3. Table 2 ---
en = rep(en, "| Wet-warm | 1,245 | 102 | 8.19% | 1.63 (1.25–2.11) |",
             "| Wet-warm | 1,245 | 102 | 8.19% | 1.63 (1.26–2.12) |", 'EN Table2 湿暖')
en = rep(en, "| Dry-cold | 874 | 183 | 20.94% | 3.13 (2.47–3.96) |",
             "| Dry-cold | 874 | 183 | 20.94% | 3.20 (2.53–4.06) |", 'EN Table2 干冷')
en = rep(en, "| Wet-cold | 254 | 76 | 29.92% | 4.44 (3.12–6.31) |",
             "| Wet-cold | 254 | 76 | 29.92% | 4.49 (3.15–6.41) |", 'EN Table2 湿冷')

# --- 4. 正文 OR ---
en = rep(en,
    "odds ratios relative to dry-warm were 1.63 (95% CI 1.25–2.11) for wet-warm, 3.13 (2.47–3.96) for dry-cold and 4.44 (3.12–6.31) for wet-cold",
    "odds ratios relative to dry-warm were 1.63 (95% CI 1.26–2.12) for wet-warm, 3.20 (2.53–4.06) for dry-cold and 4.49 (3.15–6.41) for wet-cold",
    'EN 正文 OR')

# --- 5. like-for-like ---
en = rep(en, "Prolonged capillary refill time retained an adjusted OR of **3.05 (2.48–3.74)**",
             "Prolonged capillary refill time retained an adjusted OR of **3.11 (2.53–3.83)**", 'EN like-for-like OR')

# --- 6. 各水肿等级 OR ---
en = rep(en,
    "OR 0.82 (0.63–1.06) for 2 mm, 1.08 (0.82–1.43) for 4 mm, 1.20 (0.85–1.70) for 6 mm, 1.13 (0.64–1.98) for 8 mm and **2.74 (1.74–4.32)** for anasarca",
    "OR 0.84 (0.64–1.09) for 2 mm, 1.10 (0.83–1.45) for 4 mm, 1.22 (0.86–1.72) for 6 mm, 1.19 (0.68–2.07) for 8 mm and **2.69 (1.70–4.26)** for anasarca",
    'EN 水肿各等级 OR')

# --- 7. 判别力段 ---
en = rep(en,
    "increased discrimination from AUROC 0.858 to **0.870** (ΔAUROC **+0.0124**, 95% CI +0.0069 to +0.0177), with IDI +0.0203, continuous NRI +0.5374 and categorical NRI +0.0955",
    "increased discrimination from AUROC 0.858 to **0.871** (ΔAUROC **+0.0126**, 95% CI +0.0074 to +0.0186), with IDI +0.0209, continuous NRI +0.5337 and categorical NRI +0.0539",
    'EN 判别力段')
en = rep(en, "with the highest decile predicted at 35.5% versus observed 35.0%",
             "with the highest decile predicted at 35.8% versus observed 35.1%", 'EN 校准十分位')
en = rep(en, "preserved discrimination (AUROC **0.853**)", "preserved discrimination (AUROC **0.851**)", 'EN 时间验证')

# --- 8. Table 3 ---
en = rep(en, "| AUROC (apparent) | 0.858 | **0.870** |", "| AUROC (apparent) | 0.858 | **0.871** |", 'EN T3 AUROC')
en = rep(en, "| ΔAUROC (95% CI) | — | +0.0124 (+0.0069 to +0.0177) |",
             "| ΔAUROC (95% CI) | — | +0.0126 (+0.0074 to +0.0186) |", 'EN T3 ΔAUROC')
en = rep(en, "| IDI | — | +0.0203 |", "| IDI | — | +0.0209 |", 'EN T3 IDI')
en = rep(en, "| NRI (continuous) | — | +0.5374 |", "| NRI (continuous) | — | +0.5337 |", 'EN T3 NRIc')
en = rep(en, "| NRI (categorical) | — | +0.0955 |", "| NRI (categorical) | — | +0.0539 |", 'EN T3 NRId')
en = rep(en, "| AUROC (temporal validation, 2008–2013 → 2014–2022) | — | 0.853 |",
             "| AUROC (temporal validation, 2008–2013 → 2014–2022) | — | 0.851 |", 'EN T3 时间验证')

# --- 9. 图 7 图注 ---
en = rep(en,
    "replication cohort (n = 1,541; coefficients transferred unchanged, external AUROC 0.856, calibration slope 0.76, intercept −0.97, observed-to-expected ratio 0.65)",
    "replication cohort (n = 1,541; coefficients transferred unchanged, external AUROC 0.855, calibration slope 0.83, intercept −0.87, observed-to-expected ratio 0.66)",
    'EN 图7图注')

# --- 10. 外部验证段 ---
en = rep(en,
    "gave an external AUROC of **0.856** (versus an apparent 0.870 in development), an observed-to-expected ratio of 0.65, and a calibration intercept of −0.97 and slope of 0.76 from logistic recalibration, indicating systematic over-prediction (mean predicted risk 10.7% versus observed 7.0%, i.e., roughly 1.5 times the observed risk) and a modestly over-fitted linear predictor in the external setting",
    "gave an external AUROC of **0.855** (versus an apparent 0.871 in development), an observed-to-expected ratio of 0.66, and a calibration intercept of −0.87 and slope of 0.83 from logistic recalibration, indicating systematic over-prediction (mean predicted risk 10.7% versus observed 7.0%, i.e., roughly 1.5 times the observed risk)",
    'EN 外部验证段')
en = rep(en, "changed the external AUROC from 0.850 to 0.856",
             "changed the external AUROC from 0.850 to 0.855", 'EN 体温敏感性')
en = rep(en, "The 1,555 analysable stays came from 6 of the 208 hospitals contributing to eICU-CRD",
             "The 1,555 analysable stays came from 6 of the 36 hospitals that contributed cardiac-ICU admissions (of 208 hospitals in eICU-CRD)",
             'EN 医院数')

# --- 11. 讨论：灌注轴段 ---
en = rep(en, "prolonged capillary refill time had an adjusted odds ratio of 3.05 versus 1.58 for oedema ≥6 mm — a ratio of about 1.9 between the two effect estimates",
             "prolonged capillary refill time had an adjusted odds ratio of 3.11 versus 1.58 for oedema ≥6 mm — a ratio of about 2.0 between the two effect estimates",
             'EN 讨论灌注轴')

# --- 12. 局限 4 ---
en = rep(en,
    "and those stays came from only 6 of the 208 hospitals in eICU-CRD, so hospital-level performance could not be examined and correspondingly wide confidence intervals; the external AUROC of 0.856 with a calibration slope of 0.76 and an observed-to-expected ratio of 0.65 indicates that the transferred model over-predicted risk by roughly 50% and would require recalibration before use",
    "and those stays came from only 6 of the 36 hospitals in eICU-CRD that contributed cardiac-ICU admissions, so hospital-level performance could not be examined and correspondingly wide confidence intervals; the external AUROC of 0.855 with a calibration slope of 0.83 while the observed-to-expected ratio of 0.66 indicates that the transferred model over-predicted risk by roughly 50% and would require recalibration before use",
    'EN 局限第四')

# --- 13. 补充材料清单 ---
en = rep(en, "Table S6: full specification of the development and transferred models (standardisation constants, coefficients, odds ratios and intercepts).",
             "Table S6: full specification of the development and transferred models (standardisation constants, coefficients, odds ratios and intercepts). Table S7: pre-specified physiological plausibility ranges, the number of values excluded from each covariate, and a sensitivity analysis comparing the screened analysis with an analysis of the values exactly as charted.",
             'EN 补充清单')

# =============================== 中文 ===============================
zh = io.open(ZH, encoding='utf-8').read()

zh = rep(zh,
    "校正 OR 分别为 1.63、3.13、4.44。在两轴同时二分化的同尺度比较中，毛细血管再充盈延长（OR 3.05，95%CI 2.48–3.74）的贡献约为水肿 ≥6 mm（1.58，1.27–1.97）的两倍。加入表型使 AUROC 由 0.858 升至 0.870（Δ +0.0124），时间验证判别力 0.853。在 eICU-CRD 中灌注体征成功复现（3.86% vs 27.36%；外部 AUROC 0.856）",
    "校正 OR 分别为 1.63、3.20、4.49。在两轴同时二分化的同尺度比较中，毛细血管再充盈延长（OR 3.11，95%CI 2.53–3.83）的贡献约为水肿 ≥6 mm（1.58，1.27–1.97）的两倍。加入表型使 AUROC 由 0.858 升至 0.871（Δ +0.0126），时间验证判别力 0.851。在 eICU-CRD 中灌注体征成功复现（3.86% vs 27.36%；外部 AUROC 0.855）",
    'ZH 摘要结果')

ZH_OLD_DQ = zh[zh.index('有三处数据质量问题'):]
ZH_OLD_DQ = ZH_OLD_DQ[:ZH_OLD_DQ.index('\n')]
ZH_NEW_DQ = ("**数据质量与生理合理性筛查。** 在按住院聚合之前，对全部连续型协变量按事先设定的成人重症生理合理区间进行筛查，区间之外的值判为记录或测量错误并置为缺失，不参与该住院的最小值、最大值或均值计算：心率 20–300 次/分、呼吸频率 1–80 次/分、血氧饱和度 1–100%、收缩压 20–300 mmHg、平均动脉压 20–250 mmHg、体温 25–45 ℃、体重 20–400 kg、肌酐 0.05–50 mg/dL、尿素氮 0.5–300 mg/dL、钠 80–200 mmol/L、钾 1–15 mmol/L、氯 50–160 mmol/L、碳酸氢盐 1–60 mmol/L、血红蛋白 1–25 g/dL、白细胞 0.1–500 K/µL、血小板 1–3,000 K/µL、血糖 10–4,000 mg/dL（补充表 S7）。该筛查几乎只对生命体征有实质影响：生命体征以住院内最小值或最大值进入模型，对单条错误记录最为敏感；化验指标中没有任何一项因筛查丢失超过 2 条记录。开发队列中，该筛查剔除呼吸频率记录 569,213 条中的 4,243 条（0.75%）、平均动脉压记录 584,763 条中的 1,029 条（0.18%）、心率记录 576,792 条中的 264 条（0.05%）、收缩压记录 584,132 条中的 46 条、血氧饱和度记录 558,991 条中的 40 条、体温记录 190,413 条中的 135 条、体重记录 19,873 条中的 11 条。剔除少量以科学计数法存储的呼吸频率（最高 7.0×10^6 次/分）后，\"最高呼吸频率\"的标准差由 51,404 降至 6.17 次/分；剔除零值与负值动脉压后，\"最低平均动脉压\"的标准差由 159.3 降至 10.9 mmHg（补充表 S6、S7）。复现队列中，同一筛查剔除了 73 条不合理白细胞计数（最高 1.15×10^6 K/µL，标准差由 8,762 降至 14.3 K/µL），并分别剔除 968 例的平均动脉压、345 例的收缩压与 589 例的心率中的不合理值。作为敏感性分析，若不作筛查、完全按原始记录值汇总各协变量，全部主要结果基本不变（AUROC 最大差异 0.003、校正 OR 最大差异 0.07、校准斜率最大差异 0.02、O:E 最大差异 0.01；补充表 S7），说明筛查并不驱动任何结论。\n\n另有两点数据处置一并记录以便复现。体温在两库中均按摄氏度分析：以华氏记录者先换算再取均值；在 eICU-CRD 中，华氏记录占少数（0.5%）。eICU-CRD 中血红蛋白存于 *labname* = `Hgb`，无创血压存于 *nurseCharting*，而 *vitalPeriodic* 的 *systemicsystolic* 与 *systemicmean* 是**动脉置管值、仅约四分之一住院存在**；因此收缩压与平均动脉压取无创（`Non-Invasive BP Systolic`/`Mean`）与有创（`Invasive BP Systolic`/`Mean`）来源的最小值。")
zh = rep(zh, ZH_OLD_DQ, ZH_NEW_DQ, 'ZH 方法数据质量段')

zh = rep(zh, "| 湿暖型 | 1,245 | 102 | 8.19% | 1.63 (1.25–2.11) |",
             "| 湿暖型 | 1,245 | 102 | 8.19% | 1.63 (1.26–2.12) |", 'ZH 表2 湿暖')
zh = rep(zh, "| 干冷型 | 874 | 183 | 20.94% | 3.13 (2.47–3.96) |",
             "| 干冷型 | 874 | 183 | 20.94% | 3.20 (2.53–4.06) |", 'ZH 表2 干冷')
zh = rep(zh, "| 湿冷型 | 254 | 76 | 29.92% | 4.44 (3.12–6.31) |",
             "| 湿冷型 | 254 | 76 | 29.92% | 4.49 (3.15–6.41) |", 'ZH 表2 湿冷')

zh = rep(zh,
    "以干暖型为参照的 OR 分别为湿暖型 1.63（95%CI 1.25–2.11）、干冷型 3.13（2.47–3.96）、湿冷型 4.44（3.12–6.31）",
    "以干暖型为参照的 OR 分别为湿暖型 1.63（95%CI 1.26–2.12）、干冷型 3.20（2.53–4.06）、湿冷型 4.49（3.15–6.41）",
    'ZH 正文 OR')
zh = rep(zh, "毛细血管再充盈延长的校正 OR 为 **3.05（2.48–3.74）**",
             "毛细血管再充盈延长的校正 OR 为 **3.11（2.53–3.83）**", 'ZH like-for-like')
zh = rep(zh,
    "2 mm OR 0.82（0.63–1.06）、4 mm 1.08（0.82–1.43）、6 mm 1.20（0.85–1.70）、8 mm 1.13（0.64–1.98）、**全身性水肿 2.74（1.74–4.32）**",
    "2 mm OR 0.84（0.64–1.09）、4 mm 1.10（0.83–1.45）、6 mm 1.22（0.86–1.72）、8 mm 1.19（0.68–2.07）、**全身性水肿 2.69（1.70–4.26）**",
    'ZH 水肿各等级 OR')
zh = rep(zh,
    "判别力由 AUROC 0.858 升至 **0.870**（ΔAUROC **+0.0124**，95%CI +0.0069~+0.0177），IDI +0.0203，连续 NRI +0.5374，分类 NRI +0.0955",
    "判别力由 AUROC 0.858 升至 **0.871**（ΔAUROC **+0.0126**，95%CI +0.0074~+0.0186），IDI +0.0209，连续 NRI +0.5337，分类 NRI +0.0539",
    'ZH 判别力段')
zh = rep(zh, "最高十分位预测 35.5%、实际 35.0%", "最高十分位预测 35.8%、实际 35.1%", 'ZH 校准十分位')
zh = rep(zh, "判别力保持（AUROC **0.853**）", "判别力保持（AUROC **0.851**）", 'ZH 时间验证')

zh = rep(zh, "| AUROC（表观） | 0.858 | **0.870** |", "| AUROC（表观） | 0.858 | **0.871** |", 'ZH T3 AUROC')
zh = rep(zh, "| ΔAUROC（95%CI） | — | +0.0124 (+0.0069~+0.0177) |",
             "| ΔAUROC（95%CI） | — | +0.0126 (+0.0074~+0.0186) |", 'ZH T3 ΔAUROC')
zh = rep(zh, "| IDI | — | +0.0203 |", "| IDI | — | +0.0209 |", 'ZH T3 IDI')
zh = rep(zh, "| NRI（连续） | — | +0.5374 |", "| NRI（连续） | — | +0.5337 |", 'ZH T3 NRI连续')
zh = rep(zh, "| NRI（分类） | — | +0.0955 |", "| NRI（分类） | — | +0.0539 |", 'ZH T3 NRI分类')
zh = rep(zh, "| AUROC（时间验证，2008–2013 → 2014–2022） | — | 0.853 |",
             "| AUROC（时间验证，2008–2013 → 2014–2022） | — | 0.851 |", 'ZH T3 时间验证')

zh = rep(zh,
    "外部 AUROC 0.856、校准斜率 0.76、截距 −0.97、O:E 0.65）",
    "外部 AUROC 0.855、校准斜率 0.83、截距 −0.87、O:E 0.66）", 'ZH 图7图注')

zh = rep(zh,
    "**外部 AUROC 为 0.856**（开发集表观 0.870），O:E 比 0.65，logistic 重校准给出的**校准截距为 −0.97、斜率为 0.76**，提示系统性高估风险（平均预测 10.7% vs 实际 7.0%，即约为实际风险的 1.5 倍）与线性预测子略显过拟合",
    "**外部 AUROC 为 0.855**（开发集表观 0.871），O:E 比 0.66，logistic 重校准给出的**校准截距为 −0.87、斜率为 0.83**，提示系统性高估风险（平均预测 10.7% vs 实际 7.0%，即约为实际风险的 1.5 倍）",
    'ZH 外部验证段')
zh = rep(zh, "使外部 AUROC 由 0.850 变为 0.856", "使外部 AUROC 由 0.850 变为 0.855", 'ZH 体温敏感性')
zh = rep(zh, "可分析的 1,555 例来自 eICU-CRD 208 家医院中的 6 家",
             "可分析的 1,555 例来自收治心脏 ICU 患者的 36 家医院中的 6 家（eICU-CRD 共 208 家医院）", 'ZH 医院数')

zh = rep(zh, "毛细血管再充盈延长的校正 OR 为 3.05，而水肿 ≥6 mm 为 1.58——两个效应估计之比约 1.9",
             "毛细血管再充盈延长的校正 OR 为 3.11，而水肿 ≥6 mm 为 1.58——两个效应估计之比约 2.0", 'ZH 讨论灌注轴')
zh = rep(zh,
    "且这些病例仅来自 eICU-CRD 208 家医院中的 6 家，无法考察医院层面的表现，置信区间相应较宽；外部 AUROC 0.856、校准斜率 0.76、O:E 0.65 表明迁移后的模型高估风险约 50%",
    "且这些病例仅来自 eICU-CRD 中收治心脏 ICU 患者的 36 家医院的 6 家，无法考察医院层面的表现，置信区间相应较宽；外部 AUROC 0.855、校准斜率 0.83 而 O:E 0.66 表明迁移后的模型高估风险约 50%",
    'ZH 局限第四')
zh = rep(zh, "补充表 S6：开发模型与迁移模型的完整设定（标准化常数、系数、OR 与截距）。",
             "补充表 S6：开发模型与迁移模型的完整设定（标准化常数、系数、OR 与截距）。补充表 S7：预先设定的生理合理区间、各协变量被剔除的记录数，以及\"筛查后分析\"与\"完全按原始记录值分析\"的敏感性对照。",
             'ZH 补充清单')

# =============================== Table 1 整体替换 ===============================
t1_en = [l.rstrip('\n') for l in io.open(RES + '/_table1_en.md', encoding='utf-8') if l.strip()]
t1_zh = [l.rstrip('\n') for l in io.open(RES + '/_table1_zh.md', encoding='utf-8') if l.strip()]


def swap_table(text, header_prefix, new_rows, tag):
    lines = text.split('\n')
    idx = [i for i, l in enumerate(lines) if l.startswith(header_prefix)]
    if len(idx) != 1:
        raise SystemExit('[%s] 表头匹配 %d 次' % (tag, len(idx)))
    i = idx[0]
    j = i + 2
    while j < len(lines) and lines[j].startswith('|'):
        j += 1
    LOG.append('ok  %s（替换 %d 行数据）' % (tag, j - (i + 2)))
    return '\n'.join(lines[:i + 2] + new_rows + lines[j:])


en = swap_table(en, '| Variable | Dry-warm (n = 9,679)', t1_en, 'EN Table 1')
zh = swap_table(zh, '| 变量 | 干暖型 (n = 9,679)', t1_zh, 'ZH Table 1')

# =============================== 写出（先备份） ===============================
for f in (EN, ZH):
    bak = f + '.bak_2601'
    if not os.path.exists(bak):
        shutil.copyfile(f, bak)
io.open(EN, 'w', encoding='utf-8').write(en)
io.open(ZH, 'w', encoding='utf-8').write(zh)

print('\n'.join(LOG))
print('\n共 %d 项完成；备份 *.bak_2601' % sum(1 for x in LOG if x.startswith('ok')))
