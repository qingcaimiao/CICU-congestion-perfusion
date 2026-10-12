# -*- coding: utf-8 -*-
"""第四轮最后三处：肾功能方向纠错、摘要与结论补入"开发队列充血信号真实"、中文同步"""
import io, os, shutil

J = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
NL = chr(10)
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
    LOG.append('ok  %-8s %d 处' % (tag, len(pairs)))


rep('Manuscript_JCM_EN.md', [
    ("had worse renal function (urea nitrogen 18 versus 21 mg/dL; creatinine 1.0 versus 1.1 mg/dL)",
     "had slightly **better** renal function (urea nitrogen 18 versus 21 mg/dL; creatinine 1.0 versus 1.1 mg/dL)"),
    ("but the transportable part of its value lies almost entirely in the perfusion axis. The congestion component is documentation-dependent and should not be assumed transferable.",
     "but its transportable value lies almost entirely in the perfusion axis. Congestion was prognostic in the development cohort yet is documentation-dependent, and it should not be assumed transferable."),
], 'EN')

rep('稿件_充血灌注_中文版_JCM.md', [
    ("肾功能更差（尿素氮 18 vs 21 mg/dL，肌酐 1.0 vs 1.1 mg/dL）",
     "肾功能反而略好（尿素氮 18 vs 21 mg/dL，肌酐 1.0 vs 1.1 mg/dL）"),
    ("但其中**能够跨数据库迁移的预后价值几乎全部来自灌注轴**。充血轴依赖记录习惯，因此床旁充血表型不应被假定可在不同电子病历系统之间迁移；",
     "但其中**能够跨数据库迁移的预后价值几乎全部来自灌注轴**。充血在开发队列中确有预后信号、却依赖记录习惯，因此床旁充血表型不应被假定可在不同电子病历系统之间迁移；"),
], 'ZH')

# 词数复核
p = os.path.join(J, 'Manuscript_JCM_EN.md')
L = io.open(p, encoding='utf-8').read().split(NL)
i = [k for k, l in enumerate(L) if l.strip() == '**Abstract**'][0]
j = [k for k, l in enumerate(L) if l.startswith('**Keywords')][0]
ab = ' '.join(L[i + 1:j]).replace('**', '')
tot = 0
for n in ['Background/Objectives:', 'Methods:', 'Results:', 'Conclusions:']:
    k = ab.index(n); nx = min([ab.index(x) for x in ['Methods:', 'Results:', 'Conclusions:'] if ab.index(x) > k] + [len(ab)])
    tot += len(ab[k:nx].split())
LOG.append('摘要 = %d 词' % tot)
print(NL.join(LOG))
