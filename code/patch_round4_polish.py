# -*- coding: utf-8 -*-
"""第四轮收尾润色：S3 表格空行、S8 句法、摘要压缩"""
import io, os, re

J = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
RES = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
LOG = []
NL = chr(10)


def fix_md_table(fn, header_prefix):
    p = os.path.join(J, fn)
    s = io.open(p, encoding='utf-8').read()
    i = s.index(header_prefix)
    j = s.index(NL + NL + '---', i)
    block = s[i:j]
    lines = [l for l in block.split(NL) if l.strip()]
    s = s[:i] + NL.join(lines) + s[j:]
    io.open(p, 'w', encoding='utf-8').write(s)


fix_md_table('Supplementary_Tables_JCM.md', '| Definition of congestion |')
LOG.append('ok  S3 表格空行')

p = os.path.join(J, 'Supplementary_Tables_JCM.md')
s = io.open(p, encoding='utf-8').read()
a = 'but contributed nothing in the replication cohort (odds ratio 1.09 (0.71-1.68); AUROC 0.8467 → 0.8474 on adding the congestion term to a model already containing perfusion).'
b = 'but contributed nothing in the replication cohort (odds ratio 1.09, 95% CI 0.71 to 1.68; AUROC 0.847 → 0.847 on adding the congestion term to a model already containing perfusion).'
assert s.count(a) == 1
io.open(p, 'w', encoding='utf-8').write(s.replace(a, b))
LOG.append('ok  S8 句法')

# ---- 摘要压缩至 ~245 词 ----
p = os.path.join(J, 'Manuscript_JCM_EN.md')
L = io.open(p, encoding='utf-8').read().split(NL)
i = [k for k, l in enumerate(L) if l.strip() == '**Abstract**'][0]
j = [k for k, l in enumerate(L) if l.startswith('**Keywords')][0]
REP = [
    ("Mortality was 4.10%, 8.19%, 20.94% and 29.92% across the four phenotypes, and prolonged capillary refill (adjusted odds ratio 3.11) contributed twice as much as oedema ≥6 mm (1.58).",
     "Mortality was 4.10%, 8.19%, 20.94% and 29.92% across the four phenotypes; prolonged capillary refill (adjusted odds ratio 3.11) contributed twice as much as oedema ≥6 mm (1.58)."),
    ("Because death is ascertained over the entire hospitalisation,",
     "Because death was ascertained over the whole hospitalisation,"),
]
for k in range(i + 1, j):
    for a2, b2 in REP:
        if a2 in L[k]:
            L[k] = L[k].replace(a2, b2)
            if a2.startswith("Mortality was 4.10"):
                pass
# 更实质的一处压缩：结果段去掉重复限定语
for k in range(i + 1, j):
    L[k] = L[k].replace("Only the perfusion axis transported: in eICU-CRD the gradient reproduced",
                        "Only the perfusion axis transported: the eICU-CRD gradient reproduced")
io.open(p, 'w', encoding='utf-8').write(NL.join(L))

s = io.open(p, encoding='utf-8').read().split(NL)
i = [k for k, l in enumerate(s) if l.strip() == '**Abstract**'][0]
j = [k for k, l in enumerate(s) if l.startswith('**Keywords')][0]
ab = ' '.join(s[i + 1:j]).replace('**', '')
tot = 0
for n in ['Background/Objectives:', 'Methods:', 'Results:', 'Conclusions:']:
    k = ab.index(n); nx = min([ab.index(x) for x in ['Methods:', 'Results:', 'Conclusions:'] if ab.index(x) > k] + [len(ab)])
    tot += len(ab[k:nx].split())
LOG.append('摘要 = %d 词' % tot)
print(NL.join(LOG))
