# -*- coding: utf-8 -*-
"""把论文重心从"两轴表型"重定位为"灌注轴可迁移 / 充血轴依赖记录习惯"。

改动项：
1. 中英标题
2. 摘要 背景与目的 / 结果 / 结论（结果按"梯度→两轴分解→可迁移性"重排）
3. 3.3 增补"哪一轴承载增量"段（MIMIC 分解）
4. 3.6 增补 eICU 轴分解段
5. 讨论开篇增补一句
6. 局限：9 条 → 4 个主题段（内容不减）
7. 补充材料清单加入 Table S8
"""
import io, os, shutil, sys

JCM = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
EN = JCM + '/Manuscript_JCM_EN.md'
ZH = JCM + '/稿件_充血灌注_中文版_JCM.md'
LOG = []


def one(s, old, new, tag):
    if s.count(old) != 1:
        raise SystemExit('[%s] 匹配 %d 次' % (tag, s.count(old)))
    LOG.append('ok  ' + tag)
    return s.replace(old, new)


def para_replace(text, prefix, new_para, tag):
    """按段落首串定位并整体替换（段落以空行分隔）"""
    parts = text.split('\n\n')
    hit = [i for i, p in enumerate(parts) if p.startswith(prefix)]
    if len(hit) != 1:
        raise SystemExit('[%s] 段落匹配 %d 次' % (tag, len(hit)))
    parts[hit[0]] = new_para
    LOG.append('ok  ' + tag)
    return '\n\n'.join(parts)


def insert_after(text, prefix, new_block, tag):
    """在指定行之后插入新段落"""
    lines = text.split('\n')
    hit = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    if len(hit) != 1:
        raise SystemExit('[%s] 行匹配 %d 次' % (tag, len(hit)))
    lines.insert(hit[0] + 1, '\n' + new_block)
    LOG.append('ok  ' + tag)
    return '\n'.join(lines)


# ==================================================================== 英文
en = io.open(EN, encoding='utf-8').read()

en = one(en,
    '# Bedside Congestion–Perfusion Phenotypes from Routinely Documented Nursing Assessments and In-Hospital Mortality in the Cardiac Intensive Care Unit: Development in MIMIC-IV and External Replication in eICU',
    '# Bedside Congestion–Perfusion Phenotypes in the Cardiac Intensive Care Unit: The Perfusion Sign Replicates Across Databases While Nurse-Charted Congestion Does Not',
    'EN 标题')

en = one(en,
    'The two signs that critical care nurses chart most often — pitting-oedema depth and capillary refill time — have not been evaluated as a combined phenotype in the cardiac intensive care unit (CICU), nor tested for transportability.',
    'The two signs that critical care nurses chart most often — pitting-oedema depth and capillary refill time — have not been evaluated as a combined phenotype in the cardiac intensive care unit (CICU), nor has either axis been tested for transportability across electronic record systems. We therefore built a two-axis bedside phenotype and asked two questions prospectively: how much of its prognostic signal does each axis carry, and does each axis reproduce in an independent database?',
    'EN 摘要背景')

en = one(en,
    'Of 20,806 first cardiac ICU stays, both signs were charted in 12,052 (758 deaths). Mortality was 4.10%, 8.19%, 20.94% and 29.92% across the dry-warm, wet-warm, dry-cold and wet-cold phenotypes; adjusted odds ratios were 1.63, 3.20 and 4.49. On a dichotomised like-for-like comparison, prolonged capillary refill (odds ratio 3.11) contributed about twice as much as oedema ≥6 mm (1.58). Adding the phenotype raised the AUROC from 0.858 to 0.871 (Δ +0.0126) with temporal discrimination of 0.851. In eICU-CRD the perfusion sign replicated (3.86% vs. 27.36%; external AUROC 0.855) whereas no congestion definition reproduced the gradient.',
    'Of 20,806 first cardiac ICU stays, both signs were charted in 12,052 (758 deaths). Mortality was 4.10%, 8.19%, 20.94% and 29.92% across the dry-warm, wet-warm, dry-cold and wet-cold phenotypes (7.3-fold), and on a dichotomised like-for-like comparison prolonged capillary refill (adjusted odds ratio 3.11) contributed about twice as much as oedema ≥6 mm (1.58). Adding the phenotype raised the AUROC from 0.858 to 0.871 (Δ +0.0126; temporal validation 0.851), but the increment came mainly from one axis: added alone, impaired perfusion gave ΔAUROC +0.0101 (95% CI +0.0054 to +0.0149) whereas congestion gave +0.0038 (+0.0010 to +0.0069), and congestion added on top of perfusion gave only +0.0025 (+0.0006 to +0.0045). **Only the perfusion axis transported.** In eICU-CRD, impaired perfusion reproduced its gradient (3.86% vs. 27.36% mortality; external AUROC 0.855; internal incremental ΔAUROC +0.0155, 95% CI +0.0030 to +0.0301), whereas the nurse-charted congestion measurement does not exist in that database, none of three alternative congestion signs reproduced the gradient, and congestion added no discrimination (incremental ΔAUROC +0.0008, 95% CI −0.0018 to +0.0035).',
    'EN 摘要结果')

en = one(en,
    'Routinely charted capillary refill time and oedema grade define a zero-cost congestion–perfusion phenotype whose prognostic signal is carried predominantly by the perfusion axis. Because the nurse-charted congestion measurement did not transport, bedside congestion phenotypes should be regarded as documentation-dependent.',
    'Two routinely charted bedside signs define a zero-cost congestion–perfusion phenotype with a 7-fold mortality gradient, but the part of its prognostic value that transports across databases resides almost entirely in the perfusion axis. The congestion component is documentation-dependent, so bedside congestion phenotypes should not be assumed to transfer between electronic record systems; studies proposing them should report documentation rates and test transportability explicitly.',
    'EN 摘要结论')

en = insert_after(en,
    'Adding the phenotype to a model containing 23 conventional variables increased discrimination',
    '**Which axis carries the increment?** The gain was not divided evenly (Table S8). Added individually to the 23 routine variables, impaired perfusion raised the AUROC from 0.858 to 0.869 (ΔAUROC **+0.0101**, 95% CI +0.0054 to +0.0149; adjusted odds ratio 3.24) whereas congestion raised it only to 0.862 (ΔAUROC **+0.0038**, +0.0010 to +0.0069; adjusted odds ratio 1.77 for oedema ≥6 mm), and entering congestion on top of perfusion added a further +0.0025 (+0.0006 to +0.0045). The perfusion sign therefore accounted for about four-fifths of the total incremental discrimination, and the four-phenotype structure improved on the perfusion sign alone only marginally.',
    'EN 3.3 轴分解段')

en = insert_after(en,
    'Of the 1,555 stays in which both axes were documented',
    'The same decomposition can be performed within the replication cohort (exploratory, by refitting in eICU-CRD rather than transferring coefficients; Table S8). Impaired perfusion alone raised the AUROC from 0.861 to 0.877 (ΔAUROC +0.0155, 95% CI +0.0030 to +0.0301), whereas the composite congestion definition alone raised it to 0.862 (ΔAUROC +0.0008, 95% CI −0.0018 to +0.0035, i.e. no discrimination at all); in a model containing both, the perfusion odds ratio was 3.24 (95% CI 1.92 to 5.47) and the congestion odds ratio 1.07 (0.63 to 1.80). Essentially all of the transportable incremental value therefore came from the perfusion axis.',
    'EN 3.6 轴分解段')

en = one(en,
    'and added modest but consistent information beyond 23 conventional variables.',
    'and added modest but consistent information beyond 23 conventional variables — of which, however, almost all came from the perfusion axis (Table S8).',
    'EN 讨论开篇')

EN_LIM = """Four groups of limitations should be considered.

**(i) Ascertainment.** Documentation of bedside signs is incomplete and non-random. The analysis set requiring both signs comprised 12,052 of 20,806 stays (57.9%), and patients who were examined are likely to have been sicker than those who were not, so selection bias cannot be excluded, although non-differential charting would be expected to bias estimates towards the null rather than away from it. Documentation differed by more than an order of magnitude between the two databases (oedema depth 69.1% versus 7.5% within the exposure window), and the same sparsity restricted the congestion-trajectory analysis to 6,942 of 20,806 stays (33.4%) in MIMIC-IV and made it impossible in eICU-CRD [28]; the trajectory findings are therefore hypothesis-generating.

**(ii) Measurement.** Both oedema depth and capillary refill time are subjective bedside gradings and inter-rater reliability was not measured; in our own data both capillary refill sides were recorded in 16,032 stays and disagreed in 1.55% (Cohen κ 0.90), but this reflects within-patient, same-shift documentation rather than independent observers, and non-differential misclassification from inconsistent grading would be expected to attenuate the observed associations. We also had no echocardiographic, natriuretic peptide or invasive haemodynamic reference, so "congestion" is defined only by physical signs, and objective measures such as the venous excess ultrasound score may classify patients differently [9].

**(iii) Transportability and precision.** MIMIC-IV is a single centre. In eICU-CRD the subset with both axes documented comprised 1,555 stays (110 deaths), of which 1,541 (108 deaths) were used to evaluate the transferred 18-covariate model, giving an external events-per-variable ratio of 6.0; those stays came from only 6 of the 36 hospitals that contributed cardiac-ICU admissions, so hospital-level variation in performance could not be examined and confidence intervals are correspondingly wide. The transferred model over-predicted risk by roughly 50% (observed-to-expected ratio 0.66) and would require local recalibration before use. Temperature — a pre-specified candidate covariate, available in only 31.1% of the replication set — was excluded from the transferable set, so the external estimate does not include its contribution.

**(iv) Interpretation and scope.** This is an observational study, so the associations are not causal and reverse causation cannot be excluded, either for the cross-sectional phenotype or for the trajectory analysis. Patients with missing covariates were excluded from the primary model, although missingness was low (below 4% for every covariate except temperature). We did not examine model performance or phenotype prevalence by sex, age or any other sociodemographic subgroup and no fairness analysis was undertaken; because the two databases also differ in healthcare system, documentation practice and case mix, subgroup transportability remains untested."""

en = para_replace(en, 'Several limitations must be acknowledged.', EN_LIM, 'EN 局限重组')

en = one(en,
    'Table S7: pre-specified physiological plausibility ranges, the number of values excluded from each covariate, and a sensitivity analysis comparing the screened analysis with an analysis of the values exactly as charted.',
    'Table S7: pre-specified physiological plausibility ranges, the number of values excluded from each covariate, and a sensitivity analysis comparing the screened analysis with an analysis of the values exactly as charted. Table S8: contribution of each axis of the phenotype to discrimination, in the development cohort and by refitting within the replication cohort.',
    'EN 补充清单')

# ==================================================================== 中文
zh = io.open(ZH, encoding='utf-8').read()

zh = one(zh,
    '# 常规护理记录中的床旁充血—灌注表型与心脏重症监护病房院内死亡：MIMIC-IV 开发与 eICU 外部复现',
    '# 心脏重症监护病房的床旁充血—灌注表型：灌注体征可跨数据库复现，而护士记录的充血测量不能',
    'ZH 标题')

zh = one(zh,
    '尚未在心脏重症监护病房（CICU）中作为联合表型被评价，也未经跨机构可迁移性检验。',
    '尚未在心脏重症监护病房（CICU）中作为联合表型被评价，两轴也均未经跨电子病历系统的可迁移性检验。为此我们构建了一个两轴床旁表型，并预设了要回答的两个问题：其预后信号分别有多少由哪一轴承载？两轴是否都能在独立数据库中复现？',
    'ZH 摘要背景')

zh = one(zh,
    '20,806 例首次心脏 ICU 住院中，两项体征均有记录者 12,052 例（死亡 758 例）。干暖、湿暖、干冷、湿冷四型死亡率分别为 4.10%、8.19%、20.94%、29.92%；校正 OR 分别为 1.63、3.20、4.49。在两轴同时二分化的同尺度比较中，毛细血管再充盈延长（OR 3.11，95%CI 2.53–3.83）的贡献约为水肿 ≥6 mm（1.58，1.27–1.97）的两倍。加入表型使 AUROC 由 0.858 升至 0.871（Δ +0.0126），时间验证判别力 0.851。在 eICU-CRD 中灌注体征成功复现（3.86% vs 27.36%；外部 AUROC 0.855），而**没有任何一种充血定义能复现梯度**。',
    '20,806 例首次心脏 ICU 住院中，两项体征均有记录者 12,052 例（死亡 758 例）。干暖、湿暖、干冷、湿冷四型死亡率分别为 4.10%、8.19%、20.94%、29.92%（跨度 7.3 倍）；在两轴同时二分化的同尺度比较中，毛细血管再充盈延长（校正 OR 3.11）的贡献约为水肿 ≥6 mm（1.58）的两倍。加入表型使 AUROC 由 0.858 升至 0.871（Δ +0.0126；时间验证 0.851），但增量主要来自其中一轴：单独加入灌注受损 ΔAUROC 为 **+0.0101**（95%CI +0.0054~+0.0149），单独加入充血仅 +0.0038（+0.0010~+0.0069），而在灌注之上再加充血仅 +0.0025（+0.0006~+0.0045）。**只有灌注轴实现了迁移。** 在 eICU-CRD 中，灌注受损复现了梯度（死亡率 3.86% vs 27.36%；外部 AUROC 0.855；内部增量 ΔAUROC +0.0155，95%CI +0.0030~+0.0301）；而护士记录的充血测量在该库中根本不存在，三种替代充血体征均未复现梯度，充血也未带来任何判别力增量（ΔAUROC +0.0008，95%CI −0.0018~+0.0035）。',
    'ZH 摘要结果')

zh = one(zh,
    '常规记录的毛细血管再充盈时间与水肿等级，在心脏 ICU 中构成一个零成本的充血—灌注表型，其预后信号**以灌注轴为主**。由于护士记录的那个具体充血测量未能在第二个数据库中迁移，床旁充血表型应被视为**依赖记录习惯**的表型。',
    '常规记录的两项床旁体征构成一个零成本、死亡率跨度 7 倍的充血—灌注表型，但其中**能够跨数据库迁移的预后价值几乎全部来自灌注轴**。充血轴依赖记录习惯，因此床旁充血表型不应被假定可在不同电子病历系统之间迁移；提出此类表型的研究应明确报告记录率，并对可迁移性做直接检验。',
    'ZH 摘要结论')

zh = insert_after(zh,
    '在含 23 项常规变量的模型基础上加入表型',
    '**增量由哪一轴承载？** 两部分并不均等（补充表 S8）。在 23 项常规变量之上单独加入灌注受损，AUROC 由 0.858 升至 0.869（ΔAUROC **+0.0101**，95%CI +0.0054~+0.0149；校正 OR 3.24）；单独加入充血仅升至 0.862（ΔAUROC **+0.0038**，+0.0010~+0.0069；水肿 ≥6 mm 的校正 OR 1.77）；在灌注之上再加入充血仅再增 +0.0025（+0.0006~+0.0045）。因此灌注体征承载了总增量判别力的约五分之四，四型结构相对"仅灌注体征"的提升十分有限。',
    'ZH 3.3 轴分解段')

zh = insert_after(zh,
    '两轴均被记录的 1,555 例中',
    '在复现队列中可以完成同样的分解（探索性，做法是在 eICU-CRD 内部重新拟合而非迁移系数；补充表 S8）。单独加入灌注受损使 AUROC 由 0.861 升至 0.877（ΔAUROC +0.0155，95%CI +0.0030~+0.0301），而单独加入复合充血定义仅升至 0.862（ΔAUROC +0.0008，95%CI −0.0018~+0.0035，即**毫无判别力**）；两者同时纳入时，灌注的 OR 为 3.24（95%CI 1.92~5.47）、充血的 OR 为 1.07（0.63~1.80）。可见**可迁移的增量价值几乎全部来自灌注轴**。',
    'ZH 3.6 轴分解段')

zh = one(zh,
    '并在 23 项常规变量之外提供幅度不大但一致的增量信息。',
    '并在 23 项常规变量之外提供幅度不大但一致的增量信息——不过这些增量几乎全部来自灌注轴（补充表 S8）。',
    'ZH 讨论开篇')

ZH_LIM = """应分四组考虑本研究的局限。

**（一）病例确认。** 床旁体征的记录不完整且非随机。要求两项体征兼有的分析集为 20,806 例中的 12,052 例（57.9%），被检查者很可能病情更重，因此选择偏倚不能排除，尽管非差异性记录更可能使估计**削弱**而非夸大所观察到的关联。两库记录率相差一个数量级以上（暴露窗口内水肿深度 69.1% vs 7.5%）；同样的稀疏使充血轨迹分析在 MIMIC-IV 中仅能覆盖 20,806 例中的 6,942 例（33.4%），在 eICU-CRD 中则根本无法进行[28]。因此轨迹结果应视为产生假设。

**（二）测量。** 水肿深度与毛细血管再充盈均为主观床旁分级，且本研究**未测量评定者间信度**；在我们的数据中，16,032 例双侧均有记录、1.55% 不一致（Cohen κ 0.90），但反映的是同一患者同一班次内的记录一致性，而非独立观察者之间的一致性；分级不一致导致的非差异性错分会削弱所观察到的关联。本研究亦无超声、利钠肽或有创血流动力学参照，"充血"仅由体征定义；静脉过剩超声评分等客观指标可能给出不同分类[9]。

**（三）可迁移性与精度。** MIMIC-IV 为单中心。eICU-CRD 中两轴均有记录的子集为 1,555 例（死亡 110 例），其中 1,541 例（死亡 108 例）用于评估迁移后的 18 协变量模型，**外部 EPV 仅 6.0**；这些病例仅来自收治心脏 ICU 患者的 36 家医院中的 6 家，无法考察医院层面的表现，置信区间相应较宽。迁移后的模型高估风险约 50%（O:E 0.66），临床使用前需本地重校准。作为预设候选协变量的体温在复现集中仅 31.1% 可得，故被移出迁移变量集，外部性能估计未包含其贡献。

**（四）解释与范围。** 本研究为观察性设计，关联不等于因果；无论横断面表型还是轨迹分析，均不能排除反向因果。主模型排除了协变量缺失者，尽管缺失率很低（除体温外各协变量均 <4%）。本研究未按性别、年龄或其他社会人口学亚组考察模型表现或表型患病率，也未开展公平性分析；由于两个数据库在医疗体系、记录习惯与病例构成上均有差异，亚组的可迁移性仍属未验证。"""

zh = para_replace(zh, '必须承认若干局限。', ZH_LIM, 'ZH 局限重组')

zh = one(zh,
    '补充表 S7：预先设定的生理合理区间、各协变量被剔除的记录数，以及"筛查后分析"与"完全按原始记录值分析"的敏感性对照。',
    '补充表 S7：预先设定的生理合理区间、各协变量被剔除的记录数，以及"筛查后分析"与"完全按原始记录值分析"的敏感性对照。补充表 S8：表型两轴各自对判别力的贡献（开发队列，以及在复现队列内部重新拟合的结果）。',
    'ZH 补充清单')

for f in (EN, ZH):
    if not os.path.exists(f + '.bak_reframe'):
        shutil.copyfile(f, f + '.bak_reframe')
io.open(EN, 'w', encoding='utf-8').write(en)
io.open(ZH, 'w', encoding='utf-8').write(zh)
print('\n'.join(LOG))
print('\n共 %d 项完成' % len(LOG))
