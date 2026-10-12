# -*- coding: utf-8 -*-
"""第五轮：摘要与结论（零成本限定、轨迹降调）"""
import io, os

J = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
EN, ZH = 'Manuscript_JCM_EN.md', '稿件_充血灌注_中文版_JCM.md'
NL = chr(10)
LOG = []


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
    LOG.append('ok  %-10s %d 处' % (tag, len(pairs)))


sub(EN, [
    # 摘要：Methods 精简
    ("**Methods:** Retrospective cohort study of first cardiac ICU admissions in MIMIC-IV v3.1 (development) and eICU-CRD v2.0 (replication). Congestion was the worst oedema grade charted within 24 h (ordinal 0–5) and impaired perfusion a capillary refill time >3 s; the outcome was in-hospital death.",
     "**Methods:** Cohort study of first cardiac ICU admissions in MIMIC-IV v3.1 (development) and eICU-CRD v2.0 (replication). Congestion was the worst oedema grade charted within 24 h (ordinal 0–5), impaired perfusion a capillary refill time >3 s, and the outcome in-hospital death."),
    # 摘要：Results 精简
    ("(6.24% vs. 33.96% mortality; external AUROC 0.835, observed-to-expected ratio 0.92)",
     "(6.24% vs. 33.96%; external AUROC 0.835, observed-to-expected ratio 0.92)"),
    # 摘要：结论零成本限定
    ("**Conclusions:** Two routinely charted bedside signs define a zero-cost phenotype with a 7-fold mortality gradient, but its transportable value lies almost entirely in the perfusion axis. Congestion was prognostic in the development cohort yet is documentation-dependent, and it should not be assumed transferable.",
     "**Conclusions:** Two routinely charted bedside signs define a 7-fold mortality gradient at no extra data-collection cost where they are already recorded, but the transportable part of that value lies almost entirely in the perfusion axis. Congestion was prognostic in development but is documentation-dependent and does not transfer."),
    # 结论节：零成本限定 + 轨迹降调
    ("Routinely documented oedema grade and capillary refill time define a zero-cost congestion–perfusion phenotype in the cardiac intensive care unit, with a 7-fold mortality gradient and modest incremental value beyond conventional variables.",
     "Routinely documented oedema grade and capillary refill time define a congestion–perfusion phenotype in the cardiac intensive care unit that adds no data-collection cost where the two signs are already charted, with a 7-fold mortality gradient and modest incremental value beyond conventional variables."),
    ("The phenotype is also enriched by the trajectory of congestion over time.",
     "In an exploratory secondary analysis restricted to the one-third of stays with oedema charted in both windows, and which could not be replicated in eICU-CRD, mortality also rose across congestion trajectories; that finding is hypothesis-generating and requires prospective confirmation."),
], 'EN 摘要/结论')

sub(ZH, [
    ("**结论：** 常规记录的两项床旁体征构成一个零成本、死亡率跨度 7 倍的充血—灌注表型，但其中**能够跨数据库迁移的预后价值几乎全部来自灌注轴**。",
     "**结论：** 常规记录的两项床旁体征在**已被常规记录的场景下不增加数据采集成本**，其死亡率跨度达 7 倍，但**能够跨数据库迁移的预后价值几乎全部来自灌注轴**。"),
    ("常规记录的水肿等级与毛细血管再充盈时间，在心脏重症监护病房中构成一个零成本的充血—灌注表型，死亡梯度达 7 倍，并在常规变量之上带来幅度不大的增量价值。",
     "常规记录的水肿等级与毛细血管再充盈时间，在心脏重症监护病房中构成了一个**在两体征已被常规记录的场景下不增加任何数据采集成本**的充血—灌注表型，死亡梯度达 7 倍，并在常规变量之上带来幅度不大的增量价值。"),
    ("该表型亦因充血的随时间轨迹而增强。",
     "在仅覆盖约三分之一住院（两个窗口均有水肿记录）、且无法在 eICU-CRD 复现的**探索性次要分析**中，死亡率亦随充血轨迹上升；该结果属**产生假设**，需前瞻性研究确认。"),
], 'ZH 摘要/结论')

# 词数复核
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
