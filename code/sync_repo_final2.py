# -*- coding: utf-8 -*-
"""GitHub 仓库同步（第 12 轮后）：
1) CITATION.cff 标题改为新标题，更新发布日期；
2) README 的图件说明改为"9 张主图 + 补充图 S1"；
3) 补齐工作目录中尚未进仓库的分析/校验脚本（排除以 _ 开头的临时调试脚本）。
"""
import io, os, shutil, filecmp

W = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58'
G = 'D:/桌面/workbuddyzuopin/CPxiangmu/06_GitHub_CP'
NEW = ('Nurse-Charted Congestion–Perfusion Phenotypes in the Cardiac Intensive Care Unit: '
       'Perfusion Replicates, Congestion Is Documentation-Dependent')

# ---------- 1) CITATION.cff ----------
p = G + '/CITATION.cff'
s = io.open(p, encoding='utf-8').read()


def one(t, a, b, tag):
    n = t.count(a)
    assert n == 1, '%s: %d' % (tag, n)
    print('  ok', tag)
    return t.replace(a, b)


s = one(s,
        'title: "Analysis code and aggregate results: Bedside Congestion–Perfusion Phenotypes from Routinely Documented Nursing Assessments and In-Hospital Mortality in the Cardiac Intensive Care Unit (development in MIMIC-IV, external replication in eICU)"',
        'title: "Analysis code and aggregate results: %s"' % NEW,
        'CITATION 标题')
s = one(s, 'date-released: "2026-10-11"', 'date-released: "2026-10-12"', 'CITATION 发布日期')
io.open(p, 'w', encoding='utf-8').write(s)

# ---------- 2) README ----------
p = G + '/README.md'
s = io.open(p, encoding='utf-8').read()
s = one(s, '| `figures_cp.py`, `fig3_redo.py` | Manuscript Figures 2–10 (400 dpi PNG) |',
        '| `figures_cp.py`, `fig3_redo.py` | Manuscript Figures 2–9 (400 dpi PNG) |', 'README 图范围')
s = one(s, '| `jcm_figures.py`, `jcm_fig_renumber.py` | Figure 1 (participant flow) and the graphical abstract; final figure numbering and 600 dpi TIFF export |',
        '| `jcm_figures.py`, `jcm_fig_renumber.py` | Figure 1 (participant flow) and the graphical abstract; final figure numbering (nine main figures; the variable-importance panel is Supplementary Figure S1) and 600 dpi TIFF export |',
        'README 图件说明')
io.open(p, 'w', encoding='utf-8').write(s)

# ---------- 3) 补齐脚本 ----------
copied = []
for fn in sorted(os.listdir(W)):
    if not fn.endswith('.py') or fn.startswith('_'):
        continue
    src, dst = os.path.join(W, fn), os.path.join(G, 'code', fn)
    if not os.path.exists(dst):
        shutil.copy2(src, dst); copied.append(fn)
    elif not filecmp.cmp(src, dst, shallow=False):
        shutil.copy2(src, dst); copied.append(fn + ' (updated)')
print('  code/ 新增或更新 %d 个：' % len(copied))
for f in copied:
    print('    +', f)
