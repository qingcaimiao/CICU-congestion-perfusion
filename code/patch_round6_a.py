# -*- coding: utf-8 -*-
"""第六轮：正文（中英）—— 转移模型参数基数/EPV、时间验证缺失时代、院级表现与六中心限定、
   摘要与结论精确化（灌注对比、7 倍梯度归属、"did not transport as measured"）"""
import io, os, shutil

J = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
EN, ZH = 'Manuscript_JCM_EN.md', '稿件_充血灌注_中文版_JCM.md'
NL = chr(10)
LOG = []
for f in (EN, ZH):
    p = os.path.join(J, f)
    if not os.path.exists(p + '.bak_r6'):
        shutil.copyfile(p, p + '.bak_r6')


def sub(fn, pairs, tag):
    p = os.path.join(J, fn)
    s = io.open(p, encoding='utf-8').read()
    for old, new in pairs:
        n = s.count(old)
        if n == 0 and new in s:
            continue
        assert n == 1, '[%s] 匹配 %d 次 -> %r' % (tag, n, old[:70])
        s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    LOG.append('ok  %-12s %d 处' % (tag, len(pairs)))


# ============================ EN ============================
EN_PAIRS = [
    # (1) 时间验证：补齐缺失时代的 2,337 例及其显著更高的死亡率
    ("In temporal validation, training on 2008–2013 admissions (n = 3,844) and testing on 2014–2022 admissions (n = 5,871) preserved discrimination (AUROC **0.851**).",
     "In temporal validation, training on 2008–2013 admissions (n = 3,844) and testing on 2014–2022 admissions (n = 5,871) preserved discrimination (AUROC **0.851**). The split could be applied to 9,715 of the 12,052 stays; the remaining 2,337 had no anchor-year group recorded and could not be assigned to an era. They were not a random subset — their in-hospital mortality was 14.7%, against 3.1–7.1% in the five eras — so the temporal estimate applies to the dated subset only (Section 4.2)."),
    # (2) 转移模型的参数构成（22 个参数，含 3 个表型哑变量）
    ("The transferred model therefore contained **19 covariates** (the 18 continuously measured variables plus sex); its complete specification is Table S6, Panel B.",
     "The transferred model therefore contained the 18 continuously measured variables, sex and the three phenotype indicators — **22 estimated parameters excluding the intercept** — so it is the full congestion–perfusion model rather than the routine-variable model, and the external AUROC reported below is directly comparable with the apparent AUROC of the same model in development. Every coefficient is listed in Table S6, Panel B."),
    # (3) 局限 (iii)：EPV 6.9、院级 AUROC、仅限六中心
    ("the transferred model (19 covariates: the 18 continuously measured variables plus sex), giving an external events-per-variable ratio of 8.0 (152 events over 19 covariates)",
     "the transferred congestion–perfusion model (22 estimated parameters excluding the intercept: the 18 continuously measured variables, sex and three phenotype indicators), giving an external events-per-variable ratio of **6.9** (152 events over 22 parameters)"),
    ("although excluding each hospital in turn left external discrimination between 0.786 and 0.846 (Table S9E).",
     "although excluding each hospital in turn left external discrimination between 0.786 and 0.846 (Table S9E). Estimated per centre, the AUROC was 0.858 in the largest hospital (n = 951, 105 deaths), 0.816 and 0.786 in the two intermediate centres, 0.643 in one small centre (n = 84, 10 deaths) and not estimable in the two smallest (n = 12 and n = 1). External performance therefore applies to these six contributing centres only and cannot be generalised to eICU-CRD as a whole."),
    # (4) 外部性能与开发表观的同源性
    ("gave an external AUROC of **0.835** (versus an apparent 0.871 in development)",
     "gave an external AUROC of **0.835** (versus an apparent 0.871 for the identical model in development)"),
    # (5) 摘要：灌注"对比"而非"整轴"迁移 + 具体护士记录项缺失
    ("Only the perfusion axis transported: the eICU-CRD gradient reproduced (6.24% vs. 33.96%; external AUROC 0.835, observed-to-expected ratio 0.92), whereas the nurse-charted congestion measurement is absent and congestion added no discrimination (+0.0012, 95% CI −0.0011 to +0.0036).",
     "The perfusion contrast transported (mortality 6.24% vs. 33.96%; transferred-model AUROC 0.835, observed-to-expected ratio 0.92), whereas the specific nurse-charted congestion measure was absent and alternative congestion definitions added no incremental discrimination (+0.0012, 95% CI −0.0011 to +0.0036)."),
    # (6) 摘要结论：7 倍梯度归属开发队列 + 六中心 + did not transport as measured
    ("Two routinely charted bedside signs define a 7-fold mortality gradient at no extra data-collection cost where they are already recorded, but the transportable part of that value lies almost entirely in the perfusion axis. Congestion was prognostic in development but is documentation-dependent and does not transfer.",
     "Two routinely charted bedside signs define a 7-fold mortality gradient in development at no extra data-collection cost where already recorded, but the contrast that transported was the perfusion one (6.24% vs. 33.96%, six contributing centres). Congestion was prognostic in development but is documentation-dependent and did not transport as measured."),
    # (7) 结论节：7 倍梯度归属 + 复现由灌注驱动 + 六中心
    ("define a congestion–perfusion phenotype in the cardiac intensive care unit that adds no data-collection cost where the two signs are already charted, with a 7-fold mortality gradient and modest incremental value beyond conventional variables.",
     "define a congestion–perfusion phenotype in the cardiac intensive care unit that adds no data-collection cost where the two signs are already charted, with a 7-fold mortality gradient across the four cells in the development cohort and modest incremental value beyond conventional variables."),
    ("and in the replication cohort congestion added nothing at all once perfusion was accounted for.",
     "and in the replication cohort the perfusion contrast (5.4-fold) carried the gradient while the composite congestion definition added no incremental discrimination once perfusion was accounted for; replication covered six contributing centres only."),
]
sub(EN, EN_PAIRS, 'EN 正文')

# ============================ ZH ============================
ZH_PAIRS = [
    ("时间验证中，以 2008–2013 年住院训练（n = 3,844）、2014–2022 年住院测试（n = 5,871），判别力保持（AUROC **0.851**）。",
     "时间验证中，以 2008–2013 年住院训练（n = 3,844）、2014–2022 年住院测试（n = 5,871），判别力保持（AUROC **0.851**）。"
     "该划分仅能覆盖 12,052 例中的 9,715 例，其余 **2,337 例无 anchor_year_group 记录**、无法归入任何时代；"
     "这 2,337 例并非随机子集——其院内死亡率为 **14.7%**，而五个时代分区为 3.1%~7.1%——"
     "故时间验证结果仅适用于有时代标注的子集（见 4.2 局限）。"),
    ("**因此迁移模型共含 19 个协变量**（18 个连续测量变量加性别），其完整设定见补充表 S6 面板 B。",
     "**因此迁移模型共含 22 个待估参数（不含截距）**——18 个连续测量变量、性别，以及 3 个表型指示变量，"
     "即它本身就是完整的充血—灌注模型（而非仅常规变量模型），故下文的外部 AUROC 与开发队列中同一模型的表观 AUROC 可直接比较。"
     "逐项系数见补充表 S6 面板 B。"),
    ("用于评估迁移后的模型（19 个协变量：18 个连续测量变量加性别），**外部 EPV 为 8.0**（152 例事件 / 19 个协变量）",
     "用于评估迁移后的充血—灌注模型（22 个待估参数、不含截距：18 个连续测量变量、性别与 3 个表型指示变量），"
     "**外部 EPV 为 6.9**（152 例事件 / 22 个参数）"),
    ("不过依次剔除任一医院后，外部判别力保持在 0.786~0.846（补充表 S9E）。",
     "不过依次剔除任一医院后，外部判别力保持在 0.786~0.846（补充表 S9E）。逐院估计：最大一家（n = 951，死亡 105 例）AUROC 0.858，"
     "两家中等规模医院为 0.816 与 0.786，一家小医院（n = 84，死亡 10 例）为 0.643，最小两家（n = 12 与 n = 1）无法估计。"
     "**因此外部性能仅代表这 6 家贡献中心，不能外推至整个 eICU-CRD。**"),
    ("将 MIMIC-IV 系数原样套用至这 1,541 例，**外部 AUROC 为 0.835**（开发集表观 0.871）",
     "将 MIMIC-IV 系数原样套用至这 1,541 例，**外部 AUROC 为 0.835**（开发队列中**同一模型**的表观值为 0.871）"),
    ("而单独加入复合充血定义仅升至 0.835（ΔAUROC +0.0012，95%CI −0.0011~+0.0036，即**毫无判别力**）",
     "而单独加入复合充血定义仅升至 0.835（ΔAUROC +0.0012，95%CI −0.0011~+0.0036，即**未带来增量判别力**）"),
    ("**结论：** 常规记录的两项床旁体征在**已被常规记录的场景下不增加数据采集成本**，其死亡率跨度达 7 倍，但**能够跨数据库迁移的预后价值几乎全部来自灌注轴**。充血在开发队列中确有预后信号、却依赖记录习惯，因此床旁充血表型不应被假定可在不同电子病历系统之间迁移；",
     "**结论：** 常规记录的两项床旁体征在**已被常规记录的场景下不增加数据采集成本**，在开发队列中构成死亡率跨度 7 倍的四格梯度；"
     "但能够跨数据库迁移的是**灌注对比**（6.24% vs 33.96%，且仅来自 6 家贡献中心），"
     "而那个具体的护士勾选式充血测量在 eICU-CRD 中根本不存在。充血在开发队列中确有预后信号、却依赖记录习惯，"
     "因此床旁充血表型不应被假定可在不同电子病历系统之间迁移；"),
    ("死亡梯度达 7 倍，并在常规变量之上带来幅度不大的增量价值。",
     "在开发队列中四格死亡梯度达 7 倍，并在常规变量之上带来幅度不大的增量价值。"),
    ("而在复现队列中，一旦校正灌注，充血未再带来任何增量。",
     "而在复现队列中，死亡梯度主要由**灌注对比（5.4 倍）**承载，一旦校正灌注，复合充血定义未再带来任何增量判别力；且复现仅覆盖 6 家贡献中心。"),
]
sub(ZH, ZH_PAIRS, 'ZH 正文')

# 摘要词数复核
p = os.path.join(J, EN)
L = io.open(p, encoding='utf-8').read().split(NL)
i = [k for k, l in enumerate(L) if l.strip() == '**Abstract**'][0]
j = [k for k, l in enumerate(L) if l.startswith('**Keywords')][0]
ab = ' '.join(L[i + 1:j]).replace('**', '')
tot = 0
for n in ['Background/Objectives:', 'Methods:', 'Results:', 'Conclusions:']:
    k = ab.index(n)
    nx = min([ab.index(x) for x in ['Methods:', 'Results:', 'Conclusions:'] if ab.index(x) > k] + [len(ab)])
    w = len(ab[k:nx].split()); tot += w
    LOG.append('   %-24s %d 词' % (n, w))
LOG.append('摘要合计 = %d 词' % tot)
print(NL.join(LOG))
