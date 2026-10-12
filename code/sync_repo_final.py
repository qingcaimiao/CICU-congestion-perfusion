# -*- coding: utf-8 -*-
"""投稿前收尾：把交付目录 03_结果 的最终结果全量同步进 GitHub 仓库副本，
并修正 README / docs 中仍是"第三轮修正前"的旧数值。

背景：仓库 results/ 停留在 eICU 结局字段修正（unitdischargestatus → hospitaldischargestatus）之前，
README 仍写 eICU 死亡 110 / 旧表型死亡率 / 旧两轴贡献；稿件 Data Availability 指向本仓库，必须一致。
"""
import io, os, shutil, filecmp

RES = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
G = 'D:/桌面/workbuddyzuopin/CPxiangmu/06_GitHub_CP'
GRES = G + '/results'

SKIP_SUBSTR = ['DeepSeek反馈逐条核实表', '轮外部意见核实表', '.bak']
EXT = ('.csv', '.json', '.md')

copied, added, same = [], [], []
for fn in sorted(os.listdir(RES)):
    if fn.startswith('_') or not fn.endswith(EXT):
        continue
    if any(s in fn for s in SKIP_SUBSTR):
        continue
    src = os.path.join(RES, fn)
    dst = os.path.join(GRES, fn)
    if os.path.exists(dst):
        if filecmp.cmp(src, dst, shallow=False):
            same.append(fn)
        else:
            shutil.copy2(src, dst); copied.append(fn)
    else:
        shutil.copy2(src, dst); added.append(fn)

print('更新（内容变化）: %d' % len(copied))
for f in copied:
    print('   ~', f)
print('新增: %d' % len(added))
for f in added:
    print('   +', f)
print('已一致: %d' % len(same))

# ---------- README 数字修正 ----------
p = G + '/README.md'
s = io.open(p, encoding='utf-8').read()


def one(t, a, b, tag):
    assert t.count(a) == 1, '%s: %d' % (tag, t.count(a))
    print('   ok', tag)
    return t.replace(a, b)


s = one(s, '| In-hospital deaths | 758 (6.29%) | 110 (7.1%) |',
        '| In-hospital deaths | 758 (6.29%) | 156 (10.0%) |', 'README-死亡数')
s = one(s, '| Phenotype mortality | dry-warm 4.10% → wet-cold 29.92% | dry-warm 2.92% → wet-cold 28.29% |',
        '| Phenotype mortality | dry-warm 4.10% → wet-cold 29.92% | dry-warm 4.53% → wet-cold 34.87% |',
        'README-表型死亡率')
s = one(s, '| Axis contribution (ΔAUROC) | perfusion +0.0101; congestion +0.0038; both +0.0126 | perfusion +0.0155; congestion +0.0008 (null) |',
        '| Axis contribution (ΔAUROC) | perfusion +0.0101; congestion +0.0038; both +0.0126 | perfusion +0.0128; congestion +0.0012 (95% CI −0.0011 to +0.0036, null); both +0.0142 |',
        'README-两轴贡献')
s = one(s, '| Cohort | 20,806 first cardiac ICU stays | 27,757 cardiac ICU stays (208 hospitals) |',
        '| Cohort | 20,806 first cardiac ICU stays | 27,757 cardiac ICU stays (208 hospitals; 36 contributed cardiac-ICU admissions, 6 contributed analysable cases) |',
        'README-队列口径')
io.open(p, 'w', encoding='utf-8').write(s)

# ---------- docs 数字修正 ----------
p = G + '/docs/variable_dictionary.md'
s = io.open(p, encoding='utf-8').read()
s = one(s, '(external AUROC 0.850 vs 0.856)',
        '(external AUROC 0.833 when included vs 0.835 in the primary specification)', 'docs-AUROC')
io.open(p, 'w', encoding='utf-8').write(s)
print('README / docs 已修正')
