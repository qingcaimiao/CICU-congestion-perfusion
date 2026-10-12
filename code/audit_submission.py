# -*- coding: utf-8 -*-
"""全稿逐项核对（只读，不改稿）：
① 内容：中英关键数字一致性、图号/表号引用完整性
② 图片：9 主图 + 1 补充图的存在、图注编号、内嵌路径可解析、dpi/色彩
③ 表格：Table 1–4 与 S1–S10 是否齐全、表头格式
④ JCM 符合性：摘要词数、关键词数、参考文献体例、声明章节、清单
⑤ AI 写作残留：零宽字符、NBSP、LaTeX 残留、异常连字符、占位符、乱码
"""
import io, os, re, glob
from PIL import Image

D = 'D:/桌面/workbuddyzuopin/CPxiangmu'
JCM = D + '/02_投稿包_JCM'
EN = JCM + '/Manuscript_JCM_EN.md'
ZH = JCM + '/稿件_充血灌注_中文版_JCM.md'
SUP = JCM + '/Supplementary_Tables_JCM.md'
en = io.open(EN, encoding='utf-8').read()
zh = io.open(ZH, encoding='utf-8').read()
sup = io.open(SUP, encoding='utf-8').read()

print('=' * 72)
print('① 内容与编号完整性')
print('=' * 72)
for tag, s in (('EN', en), ('ZH', zh)):
    caps = re.findall(r'^\*\*(Figure|图)\s*(\d+)\.?\*\*', s, flags=re.M)
    nums = [int(x[1]) for x in caps]
    print('%s 图注编号: %s （共 %d 个，连续=%s）' % (tag, nums, len(nums), nums == list(range(1, len(nums) + 1))))
    cites = sorted(set(int(m) for m in re.findall(r'(?:Figure|图)\s*(\d+)', s)))
    print('%s 正文/图注中出现的图号集合: %s' % (tag, cites))
    print('%s 是否残留 Figure 10 / 图 10: %s' % (tag, ('Figure 10' in s) or ('图 10' in s)))
    print('%s 补充图引用 (S1/补充图 S1): %s' % (tag, ('Figure S1' in s) or ('补充图 S1' in s)))
    embeds = re.findall(r'!\[[^\]]*\]\(([^")\s]+)', s)
    miss = [e for e in embeds if not os.path.exists(e)]
    print('%s 内嵌图片 %d 张，路径缺失 %d 张 %s' % (tag, len(embeds), len(miss), miss if miss else ''))
    print()

print('表格编号：')
for tag, s in (('EN', en), ('ZH', zh)):
    main = sorted(set(int(m) for m in re.findall(r'^\*\*Table (\d)\.', s, flags=re.M)))
    print('  %s 主表: %s' % (tag, main))
sup_tabs = sorted(set(int(m) for m in re.findall(r'^## Table S(\d+[a-z]?)\.', sup, flags=re.M)),
                  key=lambda x: (int(re.sub(r'\D', '', str(x))), str(x)))
print('  补充表（正文文件内）: %s' % sorted(set(re.findall(r'Table S\d+[a-z]?', en))))
print('  补充材料文件内的表: %s' % sup_tabs)
print('  补充材料新增图: %s' % re.findall(r'^## Figure S\d+\.', sup, flags=re.M))

print()
print('=' * 72)
print('② 图片文件与属性')
print('=' * 72)
figs = sorted(glob.glob(JCM + '/Figures/*.tif'))
print('投稿包主图: %d 张' % len(figs))
for f in figs:
    im = Image.open(f)
    print('  %-40s %s %s dpi=%s' % (os.path.basename(f), im.size, im.mode, im.info.get('dpi')))
supfig = sorted(glob.glob(D + '/04_图/补充图/*'))
print('补充图: %s' % [os.path.basename(x) for x in supfig])
ga = D + '/02_投稿包_JCM/Graphical_Abstract.tif'
im = Image.open(ga)
print('图文摘要: %s %s dpi=%s' % (im.size, im.mode, im.info.get('dpi')))

print()
print('=' * 72)
print('③ JCM 投稿硬指标')
print('=' * 72)
L = en.split('\n')
i = [k for k, l in enumerate(L) if l.strip() == '**Abstract**'][0]
j = [k for k, l in enumerate(L) if l.startswith('**Keywords')][0]
ab = ' '.join(L[i + 1:j]).replace('**', '')
tot = 0
for n in ['Background/Objectives:', 'Methods:', 'Results:', 'Conclusions:']:
    k = ab.index(n)
    nx = min([ab.index(x) for x in ['Methods:', 'Results:', 'Conclusions:'] if ab.index(x) > k] + [len(ab)])
    tot += len(ab[k:nx].split())
kw = [x.strip() for x in L[j].replace('**Keywords:**', '').split(';') if x.strip()]
print('英文摘要词数 = %d （JCM ≤250）' % tot)
print('关键词 = %d 个（JCM ≤6）: %s' % (len(kw), '; '.join(kw)))
print('参考文献条数 = %d' % len(re.findall(r'^[0-9]+\. ', en, flags=re.M)))
print('参考文献含 et al. 的条数 = %d （MDPI 允许全列）' % len(re.findall(r'et al\.', en)))
decls = ['Author Contributions', 'Funding', 'Institutional Review Board Statement', 'Informed Consent Statement',
         'Data Availability Statement', 'Conflicts of Interest', 'Abbreviations', 'Acknowledgments',
         'Supplementary Materials']
print('必备章节:', {d: ('## ' + d) in en for d in decls})
print('标题词数 = %d' % len(en.split('\n')[0].lstrip('# ').split()))

print()
print('=' * 72)
print('④ AI 写作残留 / 特殊符号扫描')
print('=' * 72)
PATTERNS = {
    '零宽字符 (U+200B/200C/200D/FEFF)': r'[\u200b\u200c\u200d\ufeff]',
    '不换行空格 U+00A0': r'\u00a0',
    '行/段分隔符 U+2028/2029': r'[\u2028\u2029]',
    'LaTeX 残留 (\\textbackslash/\\geq/\\leq/\\times)': r'\\textbackslash|\\geq|\\leq|\\times',
    'HTML 实体 (&nbsp;/*&#)': r'&nbsp;|&#\d+;',
    '占位符 (TODO/TBD/XXX/待补/???)': r'\bTODO\b|\bTBD\b|XXX|\?\?\?',
    '乱码 (Ã/â€/ï¿½)': r'Ã|â€|ï¿½',
    '三重以上星号': r'\*{3,}',
    '连续两个空格(正文)': r'[A-Za-z,;)] {2,}[A-Za-z(]',
    '中文里夹半角标点 (,.;:?!)': r'[\u4e00-\u9fff][,.;:?!][\u4e00-\u9fff]',
    'ASCII 比较符 >= <= !=': r'>=|<=|!=',
    '空链接/空图片': r'!\[\]\(\)|\[\]\(\)',
    '残留补丁标记': r'\.bak_|_r\d+\b|patch_',
}
for name, pat in PATTERNS.items():
    hits = []
    for tag, s in (('EN', en), ('ZH', zh), ('SUP', sup)):
        for m in re.finditer(pat, s):
            seg = s[max(0, m.start() - 30):m.end() + 30].replace('\n', ' ')
            hits.append('%s: …%s…' % (tag, seg))
    print('%-46s %d 处' % (name, len(hits)))
    for h in hits[:4]:
        print('      %s' % h)

# 全角/半角与符号一致性
print()
print('Unicode 符号使用：')
for sym, nm in [('≥', '≥'), ('≤', '≤'), ('–', 'en dash'), ('—', 'em dash'), ('−', 'minus U+2212'), ('-', 'hyphen')]:
    print('  %-14s EN:%4d  ZH:%4d' % (nm, en.count(sym), zh.count(sym)))
