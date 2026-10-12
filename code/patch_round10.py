# -*- coding: utf-8 -*-
"""第十轮外部意见：硬伤清单 0 条属实；唯一可改项是局限(三)同一段内把 EPV 重复陈述了两次
（第六轮补参数基数时留下），删去重复的第二次陈述，保留"置信区间宽 → 探索性"的结论。"""
import io

J = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
EN = J + '/Manuscript_JCM_EN.md'
ZH = J + '/稿件_充血灌注_中文版_JCM.md'
LOG = []


def one(s, old, new, tag, cnt=1):
    n = s.count(old)
    assert n == cnt, '%s: 出现 %d 次（期望 %d）' % (tag, n, cnt)
    LOG.append('ok  ' + tag)
    return s.replace(old, new)


s = io.open(EN, encoding='utf-8').read()
s = one(s,
        'With 152 events over 22 parameters the external events-per-variable ratio is 6.9 and the confidence '
        'intervals around the external estimates are correspondingly wide, so the external evaluation should be '
        'read as exploratory;',
        'With only 152 events the confidence intervals around the external estimates are correspondingly wide, '
        'so the external evaluation should be read as exploratory;',
        'EN 局限(三)-去 EPV 重复')
io.open(EN, 'w', encoding='utf-8').write(s)

z = io.open(ZH, encoding='utf-8').read()
z = one(z,
        '在 152 例事件 / 22 个参数的条件下，**外部 EPV 仅 6.9**，外部估计的置信区间相应较宽，'
        '故外部验证应视为**探索性**，',
        '在仅 152 例事件的条件下，外部估计的置信区间相应较宽，故外部验证应视为**探索性**，',
        'ZH 局限(三)-去 EPV 重复')
io.open(ZH, 'w', encoding='utf-8').write(z)

print('\n'.join(LOG))
print('完成')
