# -*- coding: utf-8 -*-
"""第八轮外部意见：仅落实三条可加固项（其余全部回源文件证实不成立）。
1) 摘要补入时间验证的排除细节（2,337 例无时代标注、死亡率 14.7%）——同时压缩 5 个词以守住 JCM 约 250 词上限；
2) 讨论中切点乐观性补一句"未做 bootstrap 乐观性校正"；
3) Figure 9 图注与图内标题统一（mean |SHAP|）。
每条替换都做唯一性断言。
"""
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


# ---------- 1) 英文摘要 ----------
s = io.open(EN, encoding='utf-8').read()

s = one(s, 'Adding the phenotype raised the AUROC from 0.858 to 0.871 (Δ +0.0126; temporal validation 0.851, dated stays only)',
        'The phenotype raised AUROC from 0.858 to 0.871 (Δ +0.0126; temporal validation 0.851 in 9,715 dated stays, '
        'excluding 2,337 undated stays with 14.7% mortality)', 'EN 摘要-时间验证')

s = one(s, 'impaired perfusion a capillary refill time >3 s',
        'impaired perfusion capillary refill >3 s', 'EN 摘要-压缩(灌注定义)')

s = one(s, 'the contrast that transported was the perfusion one (6.24% vs. 33.96%, six contributing centres)',
        'the contrast that transported was perfusion (6.24% vs. 33.96%, six contributing centres)',
        'EN 摘要-压缩(结论句)')

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

# ---------- 2) 中文摘要 ----------
z = io.open(ZH, encoding='utf-8').read()
z = one(z, '时间验证 0.851，仅限有时代标注的子集',
        '时间验证 0.851（12,052 例中仅 9,715 例有时代标注，另 2,337 例无标注、死亡率 14.7%，未纳入）',
        'ZH 摘要-时间验证')
io.open(ZH, 'w', encoding='utf-8').write(z)

# ---------- 3) 切点乐观性补 bootstrap 说明 ----------
s = io.open(EN, encoding='utf-8').read()
s = one(s,
        'the apparent increment of +0.0126 may be optimistic even though the sensitivity analyses at grade >=2 and >=4 were consistent (Table S9F).',
        'the apparent increment of +0.0126 may be optimistic even though the sensitivity analyses at grade >=2 and >=4 were '
        'consistent (Table S9F); a bootstrap-corrected estimate of this increment was not computed.',
        'EN 切点乐观性')
io.open(EN, 'w', encoding='utf-8').write(s)

z = io.open(ZH, encoding='utf-8').read()
z = one(z,
        '表观的 +0.0126 增量**可能偏乐观**，尽管 ≥2 级与 ≥4 级的敏感性分析结果一致（补充表 S9F）。',
        '表观的 +0.0126 增量**可能偏乐观**，尽管 ≥2 级与 ≥4 级的敏感性分析结果一致（补充表 S9F）；'
        '未对该增量做 bootstrap 乐观性校正。',
        'ZH 切点乐观性')
io.open(ZH, 'w', encoding='utf-8').write(z)

# ---------- 4) Figure 9 图注与图内标题统一 ----------
s = io.open(EN, encoding='utf-8').read()
s = one(s,
        '**Figure 9.** Variable importance by mean absolute SHAP value, from a random forest including the two bedside signs.',
        '**Figure 9.** Variable importance (mean |SHAP|; that is, mean absolute SHAP value), from a random forest including the two bedside signs.',
        'EN 图9图注')
io.open(EN, 'w', encoding='utf-8').write(s)

z = io.open(ZH, encoding='utf-8').read()
z = one(z,
        '**图 9**　随机森林（含两项床旁体征）平均绝对 SHAP 值的变量重要性。',
        '**图 9**　变量重要性（平均 |SHAP|，即平均绝对 SHAP 值；随机森林含两项床旁体征）。',
        'ZH 图9图注')
io.open(ZH, 'w', encoding='utf-8').write(z)

print('\n'.join(LOG))
print('全部完成')
