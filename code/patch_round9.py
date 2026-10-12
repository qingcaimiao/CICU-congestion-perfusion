# -*- coding: utf-8 -*-
"""第九轮外部意见：只落实两条真实可改项。
1) 摘要中 "impaired perfusion capillary refill >3 s" 缺谓语（第八轮压缩时删掉了 a/time 造成）→ 修复为完整句；
   同时压缩一处冗余词，使英文摘要仍 ≤250 词。
2) 正文与补充材料中仅存的 ASCII 比较符 ">=" 统一为 Unicode "≥"（与全稿他处 "≥6 mm" 保持一致）。
其余指控回源文件实测均不成立。
"""
import io

J = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
EN = J + '/Manuscript_JCM_EN.md'
SUP = J + '/Supplementary_Tables_JCM.md'
LOG = []


def one(s, old, new, tag, cnt=1):
    n = s.count(old)
    assert n == cnt, '%s: 出现 %d 次（期望 %d）' % (tag, n, cnt)
    LOG.append('ok  ' + tag)
    return s.replace(old, new)


# ---------- 1) 摘要：修复缺谓语 ----------
s = io.open(EN, encoding='utf-8').read()
s = one(s, 'Congestion was the worst oedema grade charted within 24 h (ordinal 0–5), impaired perfusion capillary refill >3 s, and the outcome in-hospital death.',
        'Congestion was the worst oedema grade charted within 24 h (ordinal 0–5), impaired perfusion was a capillary refill time >3 s, and the outcome in-hospital death.',
        'EN 摘要-补谓语')
# 为守词数上限，压缩一处冗余形容词
s = one(s, 'alternative congestion definitions added no incremental discrimination',
        'alternative congestion definitions added no discrimination', 'EN 摘要-压缩')

# ---------- 2) 比较符统一 ----------
s = one(s, 'sensitivity analyses at grade >=2 and >=4 were consistent',
        'sensitivity analyses at grade \u22652 and \u22654 were consistent', 'EN 正文-比较符')

io.open(EN, 'w', encoding='utf-8').write(s)

# 复核词数
L = s.split('\n')
i = [k for k, l in enumerate(L) if l.strip() == '**Abstract**'][0]
j = [k for k, l in enumerate(L) if l.startswith('**Keywords')][0]
ab = ' '.join(L[i + 1:j]).replace('**', '')
tot = 0
for n in ['Background/Objectives:', 'Methods:', 'Results:', 'Conclusions:']:
    k = ab.index(n)
    nx = min([ab.index(x) for x in ['Methods:', 'Results:', 'Conclusions:'] if ab.index(x) > k] + [len(ab)])
    tot += len(ab[k:nx].split())
print('英文摘要 = %d 词（JCM 上限约 250）' % tot)
assert tot <= 250, '摘要超限：%d' % tot

# 补充材料比较符
t = io.open(SUP, encoding='utf-8').read()
t = one(t, 'Oedema >=6 mm, like-for-like', 'Oedema \u22656 mm, like-for-like', 'S9B-比较符')
io.open(SUP, 'w', encoding='utf-8').write(t)

print('\n'.join(LOG))
print('全部完成')
