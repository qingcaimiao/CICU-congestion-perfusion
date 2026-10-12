# -*- coding: utf-8 -*-
"""用户决定 1/2/3 的落地：
1) 主图由 10 张降为 9 张：SHAP 图移入补充材料作为 Figure S1，原 Fig10（轨迹）顺延为 Fig9；
2) 标题缩短为 14 词版（中英同步）；
3) 陈露邮箱维持无尾点（无需改动，仅核对）；
另修正《投稿前清单》中我把第四作者误写为"卢润志"（全部稿件实为"卢润之"）。
"""
import io, os, shutil

D = 'D:/桌面/workbuddyzuopin/CPxiangmu'
FIG = D + '/04_图'
SUPFIG = FIG + '/补充图'
TIF = FIG + '/figures_TIFF600'
JCM = D + '/02_投稿包_JCM'
JF = JCM + '/Figures'
LOG = []


def one(s, a, b, tag, cnt=1):
    n = s.count(a)
    assert n == cnt, '%s: 出现 %d 次（期望 %d）' % (tag, n, cnt)
    LOG.append('ok  ' + tag)
    return s.replace(a, b)


# ============ 0) 图件：搬移与改名 ============
os.makedirs(SUPFIG, exist_ok=True)
# 主图：轨迹图顺延为 Fig9；SHAP 移入补充图目录
if os.path.exists(FIG + '/Fig10_trajectory.png'):
    os.replace(FIG + '/Fig10_trajectory.png', FIG + '/Fig9_trajectory.png')
    LOG.append('ok  04_图: Fig10_trajectory.png → Fig9_trajectory.png')
if os.path.exists(FIG + '/Fig9_SHAP.png'):
    shutil.move(FIG + '/Fig9_SHAP.png', SUPFIG + '/FigureS1_SHAP.png')
    LOG.append('ok  04_图: Fig9_SHAP.png → 补充图/FigureS1_SHAP.png')
if os.path.exists(TIF + '/Fig10_trajectory_600dpi.tif'):
    os.replace(TIF + '/Fig10_trajectory_600dpi.tif', TIF + '/Fig9_trajectory_600dpi.tif')
    LOG.append('ok  TIFF600: Fig10_trajectory → Fig9_trajectory')
if os.path.exists(TIF + '/Fig9_SHAP_600dpi.tif'):
    shutil.move(TIF + '/Fig9_SHAP_600dpi.tif', SUPFIG + '/FigureS1_SHAP_600dpi.tif')
    LOG.append('ok  TIFF600: Fig9_SHAP → 补充图/FigureS1_SHAP_600dpi.tif')

# 投稿包 Figures：只留 9 张主图
for f in ['Fig9_SHAP_600dpi.tif', 'Fig10_trajectory_600dpi.tif']:
    if os.path.exists(JF + '/' + f):
        os.remove(JF + '/' + f); LOG.append('ok  投稿包 Figures: 移除 ' + f)
shutil.copy2(TIF + '/Fig9_trajectory_600dpi.tif', JF + '/Fig9_trajectory_600dpi.tif')
LOG.append('ok  投稿包 Figures: 加入 Fig9_trajectory_600dpi.tif')

# ============ 1) 英文稿 ============
p = JCM + '/Manuscript_JCM_EN.md'
s = io.open(p, encoding='utf-8').read()

s = one(s, '# Bedside Congestion–Perfusion Phenotypes in the Cardiac Intensive Care Unit: The Perfusion Sign Replicates Across Databases While Nurse-Charted Congestion Does Not',
        '# Nurse-Charted Congestion–Perfusion Phenotypes in the Cardiac Intensive Care Unit: Perfusion Replicates, Congestion Is Documentation-Dependent',
        'EN 标题')

s = one(s, 'this analysis was not used for variable selection and contributes no performance estimate.',
        'this analysis was not used for variable selection and contributes no performance estimate (Figure S1).',
        'EN 方法-SHAP 图引用')

s = one(s, '![](D:/桌面/workbuddyzuopin/CPxiangmu/04_图/Fig9_SHAP.png "4.6")\n\n**Figure 9.** Variable importance (mean |SHAP|; that is, mean absolute SHAP value), from a random forest including the two bedside signs. Ranking of the routine variables was concordant with the logistic model.\n\n',
        '', 'EN 正文-移除 SHAP 图与图注')

s = one(s, '![](D:/桌面/workbuddyzuopin/CPxiangmu/04_图/Fig10_trajectory.png "6.3")',
        '![](D:/桌面/workbuddyzuopin/CPxiangmu/04_图/Fig9_trajectory.png "6.3")', 'EN 轨迹图路径')
s = one(s, '**Figure 10.** (A) Mean oedema grade', '**Figure 9.** (A) Mean oedema grade', 'EN 轨迹图注号')
s = one(s, '× 10⁻¹⁹; Figure 10)', '× 10⁻¹⁹; Figure 9)', 'EN 轨迹图正文引用')
s = one(s, 'Table S10: complete value domain of the four eICU-CRD bedside-examination fields, with the classification applied to each value.',
        'Table S10: complete value domain of the four eICU-CRD bedside-examination fields, with the classification applied to each value. '
        'Figure S1: variable importance by mean absolute SHAP value, from a random forest fitted to the development cohort as a purely descriptive check.',
        'EN 补充清单-加 Figure S1')
io.open(p, 'w', encoding='utf-8').write(s)

# ============ 2) 中文稿 ============
p = JCM + '/稿件_充血灌注_中文版_JCM.md'
z = io.open(p, encoding='utf-8').read()
z = one(z, '# 心脏重症监护病房的床旁充血—灌注表型：灌注体征可跨数据库复现，而护士记录的充血测量不能',
        '# 心脏重症监护病房中护士记录的充血—灌注表型：灌注可复现，充血依赖记录', 'ZH 标题')
z = one(z, '该分析未用于变量筛选，也不提供任何性能估计。',
        '该分析未用于变量筛选，也不提供任何性能估计（补充图 S1）。', 'ZH 方法-补充图引用')
z = one(z, '![](D:/桌面/workbuddyzuopin/CPxiangmu/04_图/Fig9_SHAP.png "4.6")\n\n**图 9**　变量重要性（平均 |SHAP|，即平均绝对 SHAP 值；随机森林含两项床旁体征）。常规变量的排序与 logistic 模型一致。\n\n',
        '', 'ZH 正文-移除 SHAP 图与图注')
z = one(z, '![](D:/桌面/workbuddyzuopin/CPxiangmu/04_图/Fig10_trajectory.png "6.3")',
        '![](D:/桌面/workbuddyzuopin/CPxiangmu/04_图/Fig9_trajectory.png "6.3")', 'ZH 轨迹图路径')
z = one(z, '**图 10**　（A）0–24 小时与 24–72 小时两窗口的平均水肿等级', '**图 9**　（A）0–24 小时与 24–72 小时两窗口的平均水肿等级', 'ZH 轨迹图注号')
z = one(z, '× 10⁻¹⁹；图 10）', '× 10⁻¹⁹；图 9）', 'ZH 轨迹图正文引用')
z = one(z, '补充表 S10：eICU-CRD 四个床旁查体字段的完整取值域，以及每个取值所采用的分类。',
        '补充表 S10：eICU-CRD 四个床旁查体字段的完整取值域，以及每个取值所采用的分类。'
        '补充图 S1：开发队列随机森林的平均绝对 SHAP 值变量重要性（纯描述性检查）。', 'ZH 补充清单-加补充图 S1')
io.open(p, 'w', encoding='utf-8').write(z)

# ============ 3) 补充材料：新增 Figure S1 ============
p = JCM + '/Supplementary_Tables_JCM.md'
t = io.open(p, encoding='utf-8').read().rstrip('\n')
t += ('\n\n---\n\n## Figure S1. Variable importance by mean absolute SHAP value\n\n'
      '![](D:/桌面/workbuddyzuopin/CPxiangmu/04_图/补充图/FigureS1_SHAP.png "6.3")\n\n'
      '**Figure S1.** Variable importance (mean |SHAP|; that is, mean absolute SHAP value), from a random forest fitted to the '
      'development cohort with the same covariates as the primary model. The ranking of the routine variables was concordant with '
      'the logistic model, and the two bedside signs appear among the highest-ranked features. This analysis is purely descriptive: '
      'it was not used for variable selection and contributes no performance estimate.\n')
io.open(p, 'w', encoding='utf-8').write(t)
LOG.append('ok  补充材料: 新增 Figure S1')

# ============ 4) 标题同步：cover letter / 审稿人 / README / 清单 ============
NEW = 'Nurse-Charted Congestion–Perfusion Phenotypes in the Cardiac Intensive Care Unit: Perfusion Replicates, Congestion Is Documentation-Dependent'
OLD_LONG = ('Bedside Congestion–Perfusion Phenotypes from Routinely Documented Nursing Assessments and In-Hospital Mortality in the '
            'Cardiac Intensive Care Unit: Development in MIMIC-IV and External Replication in eICU')

p = JCM + '/Cover_Letter_JCM.md'
s = io.open(p, encoding='utf-8').read()
s = one(s, '**Manuscript title:** ' + OLD_LONG, '**Manuscript title:** ' + NEW, 'Cover-标题')
io.open(p, 'w', encoding='utf-8').write(s)

p = JCM + '/Reviewer_Suggestions_JCM.md'
s = io.open(p, encoding='utf-8').read()
s = one(s, '**Manuscript:** ' + OLD_LONG, '**Manuscript:** ' + NEW, '审稿人建议-标题')
io.open(p, 'w', encoding='utf-8').write(s)

p = D + '/06_GitHub_CP/README.md'
s = io.open(p, encoding='utf-8').read()
s = one(s, '> **' + OLD_LONG + '**', '> **' + NEW + '**', 'README-标题')
io.open(p, 'w', encoding='utf-8').write(s)

# ============ 5) 投稿前清单：修正作者名 + 更新标题与图数 ============
p = D + '/投稿前清单_JCM.md'
s = io.open(p, encoding='utf-8').read()
s = one(s, '| 4 | Runzhi Lu 卢润志 | 第四作者 | —（待补） | —（待补） |',
        '| 4 | Runzhi Lu 卢润之 | 第四作者 | 298837507@qq.com | —（待补） |', '清单-第四作者姓名与邮箱')
s = one(s, '稿件：*Bedside Congestion–Perfusion Phenotypes in the Cardiac Intensive Care Unit: The Perfusion Sign Replicates Across Databases While Nurse-Charted Congestion Does Not*',
        '稿件：*' + NEW + '*', '清单-标题')
s = one(s, '| 主图（投稿用） | `Figures/Fig1–Fig10_*_600dpi.tif` | 10 张、**RGB + 内嵌 600 dpi**（已逐张核验） |',
        '| 主图（投稿用） | `Figures/Fig1–Fig9_*_600dpi.tif` | **9 张**、RGB + 内嵌 600 dpi（SHAP 图已移入补充材料作 Figure S1） |',
        '清单-图数')
io.open(p, 'w', encoding='utf-8').write(s)

print('\n'.join(LOG))
print('\n共 %d 项' % len(LOG))
