# -*- coding: utf-8 -*-
"""第四轮收尾：TRIPOD 与 Cover letter 中的 eICU 旧数值同步"""
import io, os, shutil

J = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
LOG = []


def rep(fn, pairs, tag):
    p = os.path.join(J, fn)
    t = io.open(p, encoding='utf-8').read()
    if not os.path.exists(p + '.bak_r4'):
        shutil.copyfile(p, p + '.bak_r4')
    for old, new in pairs:
        n = t.count(old)
        if n == 0 and new in t:
            continue
        assert n >= 1, '[%s] 未匹配 -> %r' % (tag, old[:70])
        t = t.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(t)
    LOG.append('ok  %-10s %d 组' % (tag, len(pairs)))


rep('TRIPOD_AI_Checklist.md', [
    ("replication 27,757 → 1,555 (110 deaths), of which 1,541 (108 deaths) entered the transferred-model evaluation",
     "replication 27,757 → 1,555 (156 deaths), of which 1,541 (152 deaths) entered the transferred-model evaluation"),
    ("phenotype-gradient replication 1,555 / 110 events; transferred-model evaluation 1,541 / 108 events",
     "phenotype-gradient replication 1,555 / 156 events; transferred-model evaluation 1,541 / 152 events"),
    ("the transferred model (18 covariates, panel B)",
     "the transferred model (19 covariates: 18 continuous variables plus sex, panel B)"),
], 'TRIPOD')

rep('Cover_Letter_JCM.md', [
    ("the perfusion sign replicated almost exactly (3.86% vs. 27.36%)",
     "the perfusion sign replicated almost exactly (6.24% vs. 33.96%)"),
    ("灌注体征几乎完全复现（3.86% vs 27.36%）",
     "灌注体征几乎完全复现（6.24% vs 33.96%）"),
], 'Cover')

# 补充材料中表 S5 表题的 108 -> 152（已在上一步处理）；复核
print('\n'.join(LOG))
