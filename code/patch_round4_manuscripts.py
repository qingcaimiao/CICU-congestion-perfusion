# -*- coding: utf-8 -*-
"""第四轮：正文（中英）修正 —— 全部分母统一、单调性、缺失数据、协变量数、校准解释、零成本限定、表 4 置信区间"""
import io, shutil, os

J = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
EN, ZH = 'Manuscript_JCM_EN.md', '稿件_充血灌注_中文版_JCM.md'
LOG = []
for f in (EN, ZH):
    p = os.path.join(J, f)
    if not os.path.exists(p + '.bak_r4'):
        shutil.copyfile(p, p + '.bak_r4')


def sub(fn, pairs, tag):
    p = os.path.join(J, fn)
    s = io.open(p, encoding='utf-8').read()
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, '[%s] 匹配 %d 次 -> %r' % (tag, n, old[:80])
        s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    LOG.append('ok  %-28s %d 处' % (tag, len(pairs)))


def replace_block(fn, start_line_idx, n_lines, new_lines, tag):
    """按行号区间替换（用于含中文引号的表格块）"""
    p = os.path.join(J, fn)
    L = io.open(p, encoding='utf-8').read().split('\n')
    old = L[start_line_idx:start_line_idx + n_lines]
    assert old and old[0].startswith('**表 4**') or old[0].startswith('**Table 4.**'), old[0][:40]
    L[start_line_idx:start_line_idx + n_lines] = new_lines
    io.open(p, 'w', encoding='utf-8').write('\n'.join(L))
    LOG.append('ok  %-28s 表格块 %d 行' % (tag, n_lines))


# ======================= EN =======================
EN_PAIRS = [
    ("The unadjusted gradient across grades (6.63%, 5.26%, 7.93%, 8.92%, 15.36% and 26.95%; trend χ² *p* = 1.4 × 10⁻⁴⁶)",
     "The unadjusted gradient across grades (6.05%, 4.47%, 6.97%, 8.66%, 12.68% and 27.36%; trend χ² *p* = 4.3 × 10⁻⁴⁵)"),
    ("Mortality was 4.46% with normal capillary refill and 25.10% when prolonged (*p* = 2.3 × 10⁻²⁰⁶; Figure 3).",
     "Mortality was 4.57% (499 of 10,924) with normal capillary refill and 22.96% (259 of 1,128) when prolonged (*p* = 5.7 × 10⁻¹²⁹; Figure 3)."),
    ("compared with 4.46% and 25.10% (5.6-fold) in MIMIC-IV.",
     "compared with 4.57% and 22.96% (5.0-fold) in MIMIC-IV."),
    ("The unadjusted mortality gradient across oedema grades was monotone, but after adjustment only anasarca remained",
     "The unadjusted mortality gradient across oedema grades was steep overall but **not monotone at the lower end** (mortality at 2 mm, 4.47%, lay slightly below that of no oedema, 6.05%), and after adjustment only anasarca remained"),
    ("Considered alone, peripheral oedema was associated with a mortality of 9.23% versus 12.67% (ratio 1.37)",
     "Considered alone, mortality was 12.67% when peripheral oedema **was** documented versus 9.23% when it was not (ratio 1.37)"),
    ("then held fixed in the replication cohort without re-optimisation.",
     "then held fixed in the replication cohort without re-optimisation; sensitivity analyses at cut-points of ≥2 and ≥4 showed that the incremental AUROC was not materially sensitive to this choice (Table S9F)."),
    ("the version including it reported as a sensitivity analysis.",
     "the version including it reported as a sensitivity analysis. Four further covariates of the primary model — invasive mechanical ventilation, any vasoactive drug infusion, congestive heart failure and chronic kidney disease — were also not carried into the transferred model, because eICU-CRD records ventilation and vasoactive therapy in treatment tables and comorbidity in free-text diagnosis strings, in neither case directly comparable to the MIMIC-IV items used here. The transferred model therefore contained **19 covariates** (the 18 continuously measured variables plus sex); its complete specification is Table S6, Panel B."),
    ("so absolute risk was well calibrated despite the case-mix shift (mean predicted risk 10.7% versus observed 9.9%) (Figure 7B).",
     "so average absolute risk was well estimated despite the case-mix shift (mean predicted risk 10.7% versus observed 9.9%); a calibration slope below 1 nevertheless indicates that the transferred model spread predicted risks somewhat too widely at both ends of the distribution (Figure 7B)."),
    ("the transferred 18-covariate model, giving an external events-per-variable ratio of 8.4",
     "the transferred model (19 covariates: the 18 continuously measured variables plus sex), giving an external events-per-variable ratio of 8.0 (152 events over 19 covariates)"),
    ("Patients with missing covariates were excluded from the primary model, although missingness was low (below 4% for every covariate except temperature).",
     "Missing covariate values were imputed to the median rather than the patient being excluded, and missingness was low (below 4.0% for every covariate in the primary model); a complete-case analysis gave materially identical estimates (Table S9G). Multiple imputation was not performed."),
    ("so the estimates reported here apply to the examined subgroup rather than to all cardiac ICU admissions.",
     "so the estimates reported here apply to the examined subgroup rather than to all cardiac ICU admissions. The pattern within these figures — more organ support but lower mortality — is most plausibly explained by the timing of assessment: the two nursing items are charted at routine examination, so patients who died very early in the admission, or whose care was redirected to comfort measures before a full assessment, were less likely to contribute both signs. The higher rate of organ support in the analysis set therefore reflects the intensity of monitoring received by patients who lived long enough to be assessed, rather than a healthier case mix."),
    ("The phenotype requires no equipment, no laboratory test and no additional data collection: it uses information already recorded and can be applied at the bedside as a four-cell card.",
     "Where these two signs are already charted, the phenotype requires no equipment, no laboratory test and no additional data collection, and can be applied at the bedside as a four-cell card. It is not cost-free where they are absent: in eICU-CRD the relevant fields were present in only 5–9% of stays, so adoption in a setting that does not chart them routinely would require a deliberate, standardised bedside assessment and the training to support it."),
    ("Panel B shows that absolute risk was well calibrated in the replication setting despite the case-mix shift.",
     "Panel B shows that average absolute risk was well estimated in the replication setting despite the case-mix shift, although the slope below 1 indicates that predicted risks were spread somewhat too widely."),
]
sub(EN, EN_PAIRS, 'EN 正文')

# EN 表 4 块（按行替换）
p = os.path.join(J, EN)
L = io.open(p, encoding='utf-8').read().split('\n')
i = [k for k, l in enumerate(L) if l.startswith('**Table 4.** External replication')][0]
EN_T4 = [
    "**Table 4.** External replication in eICU-CRD (n = 1,555 stays with both congestion and perfusion documented; 156 in-hospital deaths). Congestion was defined by the composite of any documented peripheral oedema, jugular venous distension or pulmonary crackles; impaired perfusion as documented inadequate peripheral perfusion. Alternative congestion definitions are given in Table S3. Because the two cold cells are small, this four-phenotype replication is exploratory, and each cell is reported with its 95% confidence interval; the axis decomposition in Table S8 does not depend on cell size.",
    "",
    "| Phenotype | n | Deaths | Mortality, % (95% CI) |",
    "|---|---|---|---|",
    "| Dry-warm | 684 | 31 | 4.53 (3.21–6.36) |",
    "| Wet-warm | 659 | 53 | 8.04 (6.20–10.37) |",
    "| Dry-cold | 60 | 19 | 31.67 (21.31–44.23) |",
    "| Wet-cold | 152 | 53 | 34.87 (27.75–42.73) |",
]
assert L[i + 3].startswith('| Phenotype') or 'Phenotype' in L[i + 3]
L[i:i + 8] = EN_T4
io.open(p, 'w', encoding='utf-8').write('\n'.join(L))
LOG.append('ok  %-28s 表格块 8 行' % 'EN 表 4')

# ======================= ZH =======================
ZH_PAIRS = [
    ("各等级未校正死亡率为 6.63%、5.26%、7.93%、8.92%、15.36%、26.95%（趋势 χ² *p* = 1.4 × 10⁻⁴⁶）",
     "各等级未校正死亡率为 6.05%、4.47%、6.97%、8.66%、12.68%、27.36%（趋势 χ² *p* = 4.3 × 10⁻⁴⁵）"),
    ("毛细血管再充盈正常者死亡率 4.46%、延长者 25.10%（*p* = 2.3 × 10⁻²⁰⁶；图 3）。",
     "毛细血管再充盈正常者死亡率为 4.57%（499/10,924）、延长者为 22.96%（259/1,128）（*p* = 5.7 × 10⁻¹²⁹；图 3）。"),
    ("与 MIMIC-IV 的 4.46% 与 25.10%（5.6 倍）同向且幅度可观。",
     "与 MIMIC-IV 的 4.57% 与 22.96%（5.0 倍）同向且幅度可观。"),
    ("各等级未校正死亡率呈单调梯度，但校正后**仅全身性水肿保持独立显著**",
     "各等级未校正死亡率整体陡峭，但**低端并不单调**（2 mm 的 4.47% 略低于无水肿者的 6.05%）；校正后**仅全身性水肿保持独立显著**"),
    ("单独考虑时，外周水肿死亡率为 12.67% vs 9.23%（比值 1.37）",
     "单独考虑时，记录到外周水肿者死亡率为 12.67%、未记录到者为 9.23%（比值 1.37）"),
    ("随后在复现队列中原样固定、不再优化。",
     "随后在复现队列中原样固定、不再优化；以 ≥2 级与 ≥4 级为切点的敏感性分析显示，增量 AUROC 对切点的选择并不敏感（补充表 S9F）。"),
    ("纳入该变量的版本作为敏感性分析报告。复现暴露与协变量可得性见补充表 S1b 与 S3。",
     "纳入该变量的版本作为敏感性分析报告。主模型中的另外四个协变量——有创机械通气、任何血管活性药输注、心力衰竭与慢性肾病——同样未进入迁移模型：eICU-CRD 把通气与血管活性治疗记录在治疗表、把合并症记录在自由文本诊断中，两者都与本文所用的 MIMIC-IV 条目不可直接对应。**因此迁移模型共含 19 个协变量**（18 个连续测量变量加性别），其完整设定见补充表 S6 面板 B。复现暴露与协变量可得性见补充表 S1b 与 S3。"),
    ("绝对风险仍校准良好（平均预测 10.7% vs 实际 9.9%）（图 7B）。",
     "**平均**绝对风险仍估计良好（平均预测 10.7% vs 实际 9.9%）；但校准斜率低于 1 说明迁移模型在风险分布两端把预测风险拉开得略宽（图 7B）。"),
    ("用于评估迁移后的18 协变量模型，**外部 EPV 为 8.4**",
     "用于评估迁移后的模型（19 个协变量：18 个连续测量变量加性别），**外部 EPV 为 8.0**（152 例事件 / 19 个协变量）"),
    ("主模型排除了协变量缺失者，尽管缺失率很低（除体温外各协变量均 <4%）。",
     "协变量缺失值采用中位数插补而非剔除该患者，且缺失率很低（主模型各协变量均 <4.0%）；完整案例分析给出实质一致的估计（补充表 S9G）。本研究未做多重插补。"),
    ("而非全部心脏 ICU 住院。",
     "而非全部心脏 ICU 住院。上述数字中有一个看似矛盾之处——器官支持更多、死亡率却更低——最可能的解释是**评估时点**：这两个护理项目在常规查体时勾选，因此入院后极早期即死亡、或在完成完整评估前已转为舒适治疗的患者，较少同时留下两项体征；分析集中器官支持比例更高，反映的是活到能被评估的患者接受了更密集的监测，而非病例构成更轻。"),
    ("该表型不需要设备、不需要化验、也不增加任何数据采集：它只用已记录的信息，可在床旁以一张四格卡片应用。",
     "**在两项体征已被常规记录的前提下**，该表型不需要设备、不需要化验、也不增加任何数据采集，可在床旁以一张四格卡片应用。**若所在机构不常规记录这两项体征，则并非零成本**：eICU-CRD 中相关字段仅 5–9% 的住院有记录，在这些场景推广需要有意为之的标准化床旁评估及相关培训。"),
    ("B 图显示，尽管病例构成发生偏移，复现场景中的绝对风险仍校准良好。",
     "B 图显示，尽管病例构成发生偏移，复现场景中的**平均**绝对风险仍估计良好；但斜率低于 1 说明预测风险在两端被拉开得略宽。"),
]
sub(ZH, ZH_PAIRS, 'ZH 正文')

p = os.path.join(J, ZH)
L = io.open(p, encoding='utf-8').read().split('\n')
i = [k for k, l in enumerate(L) if l.startswith('**表 4**')][0]
ZH_T4 = [
    "**表 4**　eICU-CRD 中的外部复现（两项体征均记录者 n = 1,555；院内死亡 156 例）。充血按「记录到外周水肿、颈静脉怒张或肺部啰音任一」的复合定义；灌注受损按记录为周围灌注不足。替代充血定义见补充表 S3。由于两个冷型单元格例数较少，该四型复现属**探索性**，每个单元格给出 95% 置信区间；补充表 S8 的轴分解不依赖单元格大小。",
    "",
    "| 表型 | n | 死亡 | 死亡率，%（95% CI） |",
    "|---|---|---|---|",
    "| 干暖型 | 684 | 31 | 4.53（3.21–6.36） |",
    "| 湿暖型 | 659 | 53 | 8.04（6.20–10.37） |",
    "| 干冷型 | 60 | 19 | 31.67（21.31–44.23） |",
    "| 湿冷型 | 152 | 53 | 34.87（27.75–42.73） |",
]
assert '表型' in L[i + 3], L[i + 3][:60]
L[i:i + 8] = ZH_T4
io.open(p, 'w', encoding='utf-8').write('\n'.join(L))
LOG.append('ok  %-28s 表格块 8 行' % 'ZH 表 4')

print('\n'.join(LOG))
