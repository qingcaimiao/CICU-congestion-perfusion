# -*- coding: utf-8 -*-
"""第七轮：正文（中英）修正"""
import io, os, shutil

J = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
EN, ZH = 'Manuscript_JCM_EN.md', '稿件_充血灌注_中文版_JCM.md'
NL = chr(10)
LOG = []
for f in (EN, ZH):
    p = os.path.join(J, f)
    if not os.path.exists(p + '.bak_r7'):
        shutil.copyfile(p, p + '.bak_r7')


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


# ---------- 1) EN：删除讨论中重复两遍的切点句 ----------
CUT = ("Because the cut-point was selected in the development set, the apparent increment of +0.0126 may be optimistic "
       "even though the sensitivity analyses at grade >=2 and >=4 were consistent (Table S9F). ")
p = os.path.join(J, EN)
s = io.open(p, encoding='utf-8').read()
assert s.count(CUT) == 2, s.count(CUT)
io.open(p, 'w', encoding='utf-8').write(s.replace(CUT + CUT, CUT))
LOG.append('ok  EN 删重复   1 处')

# ---------- 2) EN 其余 ----------
sub(EN, [
    ("prolonged capillary refill (odds ratio 3.11) contributed twice as much",
     "prolonged capillary refill (adjusted odds ratio 3.11) contributed twice as much"),
    ("(Δ +0.0126; temporal validation 0.851), but the increment came mainly from perfusion:",
     "(Δ +0.0126; temporal validation 0.851, dated stays only), but the increment came mainly from perfusion:"),
    ("have not been combined into a phenotype in the cardiac intensive care unit (CICU) or tested for transportability.",
     "have not been combined into a cardiac-intensive-care phenotype or tested for transportability."),
    ("a calibration slope below 1 nevertheless indicates that the transferred model spread predicted risks somewhat too widely at both ends of the distribution (Figure 7B).",
     "a calibration slope below 1 nevertheless indicates that the transferred model spread predicted risks somewhat too widely at both ends of the distribution (Figure 7B). What this estimate replicates should be stated precisely: because eICU-CRD contains no pitting-depth scale, 0.835 is the transportability of the **whole congestion–perfusion model when the congestion axis is measured by a different instrument** (the composite of documented oedema, jugular venous distension and crackles). It is not a replication of the MIMIC-IV oedema measurement, so the gap between 0.835 and the developmental 0.871 reflects the change of instrument together with the seven covariates that could not be transferred, and the two components cannot be separated in this design."),
    ("We also had no echocardiographic, natriuretic peptide or invasive haemodynamic reference,",
     "Inter-observer reliability of capillary refill time is only moderate even after training in published series, so multicentre adoption of this phenotype would require a standardised assessment protocol and explicit reliability training rather than the bedside habit captured in these records. We also had no echocardiographic, natriuretic peptide or invasive haemodynamic reference,"),
    ("External performance therefore applies to these six contributing centres only and cannot be generalised to eICU-CRD as a whole.",
     "External performance therefore applies to these six contributing centres only and cannot be generalised to eICU-CRD as a whole. The temporal validation is limited in the same way: it could be performed in 9,715 of the 12,052 stays, because 2,337 stays had no anchor-year group and could not be assigned to an era, and those stays were not a random subset — their in-hospital mortality was 14.7%, against 3.1-7.1% in the five dated eras. Temporal stability was therefore assessed in a lower-mortality, dated subset and may be over-stated for the analysis set as a whole."),
], 'EN 正文')

# ---------- 3) ZH ----------
sub(ZH, [
    ("（Δ +0.0126；时间验证 0.851）", "（Δ +0.0126；时间验证 0.851，仅限有时代标注的子集）"),
    ("**只有灌注轴实现了迁移。** 在 eICU-CRD 中，灌注受损复现了梯度（死亡率 6.24% vs 33.96%；外部 AUROC 0.835，O:E 比 0.92；内部增量 ΔAUROC +0.0128，95%CI +0.0015~+0.0259）；而护士记录的充血测量在该库中根本不存在，替代体征方向不一致，充血也未带来任何判别力增量（ΔAUROC +0.0012，95%CI −0.0011~+0.0036）。",
     "**迁移的是灌注对比**（死亡率 6.24% vs 33.96%；迁移模型 AUROC 0.835、O:E 比 0.92；且仅来自 6 家贡献中心）；而那个具体的护士勾选式充血测量在该库中根本不存在，替代充血定义也未带来任何增量判别力（ΔAUROC +0.0012，95%CI −0.0011~+0.0036）。"),
    ("但校准斜率低于 1 说明迁移模型在风险分布两端把预测风险拉开得略宽（图 7B）。",
     "但校准斜率低于 1 说明迁移模型在风险分布两端把预测风险拉开得略宽（图 7B）。此处须说明 0.835 究竟验证了什么：由于 eICU-CRD 不含凹陷深度量表，它验证的是"
     "**整个充血—灌注模型在充血轴改用另一套测量工具时的可迁移性**（复合定义：记录到的水肿／颈静脉怒张／啰音任一），"
     "而非 MIMIC-IV 那个水肿测量的复制。因此 0.835 与开发队列 0.871 的差距，同时包含测量工具的改变与 7 项无法迁移的协变量这两个来源，"
     "本设计的样本量不足以把两者分开。"),
    ("本研究亦无超声、利钠肽或有创血流动力学参照",
     "已发表研究中，毛细血管再充盈时间的**评定者间信度即便经过培训也仅为中等**，因此本表型若要多中心推广，"
     "需要标准化的评估流程与明确的一致性培训，而不能依赖这些记录中体现出的床旁习惯。本研究亦无超声、利钠肽或有创血流动力学参照"),
    ("**因此外部性能仅代表这 6 家贡献中心，不能外推至整个 eICU-CRD。**",
     "**因此外部性能仅代表这 6 家贡献中心，不能外推至整个 eICU-CRD。** 时间验证的局限同源：12,052 例中仅 9,715 例可划分时代，"
     "其余 **2,337 例无 anchor_year_group**；且这 2,337 例并非随机子集——其院内死亡率为 **14.7%**，而五个有时代的分区为 3.1%~7.1%。"
     "因此时间稳定性是在一个**死亡率更低的有时代子集**中评估的，对整体分析集可能**高估**。"),
], 'ZH 正文')

# 摘要词数
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
