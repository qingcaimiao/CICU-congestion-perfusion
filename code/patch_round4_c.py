# -*- coding: utf-8 -*-
"""第四轮：正文修正（三）—— 切点措辞、EN/ZH 表 4、ZH 其余"""
import io, os

J = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
EN, ZH = 'Manuscript_JCM_EN.md', '稿件_充血灌注_中文版_JCM.md'
LOG = []


def sub(fn, pairs, tag):
    p = os.path.join(J, fn)
    s = io.open(p, encoding='utf-8').read()
    for old, new in pairs:
        n = s.count(old)
        if n == 0 and new in s:
            LOG.append('..  %-22s 已应用' % tag); continue
        assert n == 1, '[%s] 匹配 %d 次 -> %r' % (tag, n, old[:70])
        s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    LOG.append('ok  %-22s' % tag)


sub(EN, [
    ("The cut-point was not tuned to the outcome: redefining congestion at grade ≥2 or ≥4",
     "The cut-point was chosen on the basis of the mortality gradient, but the results were not sensitive to that choice: redefining congestion at grade ≥2 or ≥4"),
], 'EN 切点措辞')

sub(ZH, [
    ("切点并非按结局挑选：将充血改定义为 ≥2 级或 ≥4 级",
     "切点系依据死亡率梯度选定，但结论对该选择并不敏感：将充血改定义为 ≥2 级或 ≥4 级"),
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
], 'ZH 正文')

for fn, i_prefix, new_block in [
    (EN, '**Table 4.** External replication', [
        "**Table 4.** External replication in eICU-CRD (n = 1,555 stays with both congestion and perfusion documented; 156 in-hospital deaths). Congestion was defined by the composite of any documented peripheral oedema, jugular venous distension or pulmonary crackles; impaired perfusion as documented inadequate peripheral perfusion. Alternative congestion definitions are given in Table S3. Because the two cold cells are small, this four-phenotype replication is exploratory, and each cell is reported with its 95% confidence interval; the axis decomposition in Table S8 does not depend on cell size.",
        "", "| Phenotype | n | Deaths | Mortality, % (95% CI) |", "|---|---|---|---|",
        "| Dry-warm | 684 | 31 | 4.53 (3.21–6.36) |",
        "| Wet-warm | 659 | 53 | 8.04 (6.20–10.37) |",
        "| Dry-cold | 60 | 19 | 31.67 (21.31–44.23) |",
        "| Wet-cold | 152 | 53 | 34.87 (27.75–42.73) |"]),
    (ZH, '**表 4**', [
        "**表 4**　eICU-CRD 中的外部复现（两项体征均记录者 n = 1,555；院内死亡 156 例）。充血按「记录到外周水肿、颈静脉怒张或肺部啰音任一」的复合定义；灌注受损按记录为周围灌注不足。替代充血定义见补充表 S3。由于两个冷型单元格例数较少，该四型复现属**探索性**，每个单元格给出 95% 置信区间；补充表 S8 的轴分解不依赖单元格大小。",
        "", "| 表型 | n | 死亡 | 死亡率，%（95% CI） |", "|---|---|---|---|",
        "| 干暖型 | 684 | 31 | 4.53（3.21–6.36） |",
        "| 湿暖型 | 659 | 53 | 8.04（6.20–10.37） |",
        "| 干冷型 | 60 | 19 | 31.67（21.31–44.23） |",
        "| 湿冷型 | 152 | 53 | 34.87（27.75–42.73） |"]),
]:
    p = os.path.join(J, fn)
    L = io.open(p, encoding='utf-8').read().split('\n')
    i = [k for k, l in enumerate(L) if l.startswith(i_prefix)][0]
    hdr = new_block[2]
    if hdr == L[i + 2]:
        LOG.append('..  %-22s 表格块已更新' % fn[:2]); continue
    L[i:i + 8] = new_block
    io.open(p, 'w', encoding='utf-8').write('\n'.join(L))
    LOG.append('ok  %-22s 表格块' % fn[:2])

print('\n'.join(LOG))
