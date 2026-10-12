# -*- coding: utf-8 -*-
"""第 12 轮：图像按"正文首次引用顺序"编号（MDPI 要求），并清掉两处旧措辞。

现状问题：
  §3.2 的图首次引用顺序为 Fig1 → Fig5(森林) → Fig4(水肿等级) → Fig3(水肿/CR) → Fig6…，
  且 Fig2 直到 §3.6 才被正文引用（只有图注在前）。
修法：
  ① §3.2 首句补 "(Figure 2)"（描述四格死亡率处，是最自然的位置）；
  ② 三个图按首次引用顺序重编号：森林图 Fig5→Fig3，水肿等级 Fig4 不变，水肿/CR Fig3→Fig5；
  ③ 图注块顺序随之重排（森林 → 水肿等级 → 水肿CR）；
  ④ 文件同步改名（04_图 / TIFF600 / 投稿包 Figures），并更新 jcm_fig_renumber.py。
另：补充表 S2 表题与 TRIPOD 第 3b 项仍用已废弃的 "zero-cost"，统一为现行措辞。
"""
import io, os, shutil

D = 'D:/桌面/workbuddyzuopin/CPxiangmu'
FIG, TIF, JF = D + '/04_图', D + '/04_图/figures_TIFF600', D + '/02_投稿包_JCM/Figures'
JCM = D + '/02_投稿包_JCM'
LOG = []


def one(s, a, b, tag, cnt=1):
    n = s.count(a)
    assert n == cnt, '%s: 出现 %d 次（期望 %d）' % (tag, n, cnt)
    LOG.append('ok  ' + tag)
    return s.replace(a, b)


# ----------[1] 文件改名：森林 ↔ 水肿CR 互换编号 ----------
RENAME = [('Fig3_edema_cr', 'Fig5_edema_cr'), ('Fig5_forest_OR', 'Fig3_forest_OR')]
TMP = FIG + '/_swap'
os.makedirs(TMP, exist_ok=True)
for old, new in RENAME:                      # 先全部搬到暂存，避免命名撞车
    for base, ext in ((FIG, '.png'), (TIF, '_600dpi.tif'), (JF, '_600dpi.tif')):
        src = os.path.join(base, old + ext)
        if os.path.exists(src):
            shutil.move(src, os.path.join(TMP, old + ext))
            LOG.append('ok  %s: %s%s → 暂存' % (os.path.basename(base), old, ext))
for old, new in RENAME:
    for base, ext in ((FIG, '.png'), (TIF, '_600dpi.tif'), (JF, '_600dpi.tif')):
        src = os.path.join(TMP, old + ext)
        if os.path.exists(src):
            shutil.move(src, os.path.join(base, new + ext))
            LOG.append('ok  %s: %s%s' % (os.path.basename(base), new, ext))
os.rmdir(TMP)

# ----------[2] 英文稿 ----------
p = JCM + '/Manuscript_JCM_EN.md'
s = io.open(p, encoding='utf-8').read()
s = one(s, 'Mortality differed steeply across the four phenotypes (Table 2).',
        'Mortality differed steeply across the four phenotypes (Table 2, Figure 2).', 'EN §3.2 补 Figure 2 引用')
s = one(s, '(Table 2, Figure 5)', '(Table 2, Figure 3)', 'EN 森林图引用改 Fig3')
s = one(s, '(*p* = 5.7 × 10⁻¹²⁹; Figure 3)', '(*p* = 5.7 × 10⁻¹²⁹; Figure 5)', 'EN 水肿/CR 引用改 Fig5')

OLD_BLK = ('![](D:/桌面/workbuddyzuopin/CPxiangmu/04_图/Fig3_edema_cr.png "6.3")\n\n'
           '**Figure 3.** In-hospital mortality by (A) worst oedema grade in the first 24 h and (B) capillary refill time, MIMIC-IV development cohort.\n\n'
           '![](D:/桌面/workbuddyzuopin/CPxiangmu/04_图/Fig4_edema_grade.png "6.3")\n\n'
           '**Figure 4.** Oedema grade and in-hospital mortality: (A) unadjusted mortality by grade; (B) multivariable-adjusted odds ratios with 95% confidence intervals, reference grade 0. Only the highest grade (anasarca) remained independently significant after adjustment.\n\n'
           '![](D:/桌面/workbuddyzuopin/CPxiangmu/04_图/Fig5_forest_OR.png "4.2")\n\n'
           '**Figure 5.** Adjusted odds ratios for in-hospital death by congestion–perfusion phenotype, with dry-warm as the reference category.')
NEW_BLK = ('![](D:/桌面/workbuddyzuopin/CPxiangmu/04_图/Fig3_forest_OR.png "4.2")\n\n'
           '**Figure 3.** Adjusted odds ratios for in-hospital death by congestion–perfusion phenotype, with dry-warm as the reference category.\n\n'
           '![](D:/桌面/workbuddyzuopin/CPxiangmu/04_图/Fig4_edema_grade.png "6.3")\n\n'
           '**Figure 4.** Oedema grade and in-hospital mortality: (A) unadjusted mortality by grade; (B) multivariable-adjusted odds ratios with 95% confidence intervals, reference grade 0. Only the highest grade (anasarca) remained independently significant after adjustment.\n\n'
           '![](D:/桌面/workbuddyzuopin/CPxiangmu/04_图/Fig5_edema_cr.png "6.3")\n\n'
           '**Figure 5.** In-hospital mortality by (A) worst oedema grade in the first 24 h and (B) capillary refill time, MIMIC-IV development cohort.')
s = one(s, OLD_BLK, NEW_BLK, 'EN 图注块重排')
io.open(p, 'w', encoding='utf-8').write(s)

# ----------[3] 中文稿 ----------
p = JCM + '/稿件_充血灌注_中文版_JCM.md'
z = io.open(p, encoding='utf-8').read()
z = one(z, '四型间死亡率差异陡峭（表 2）。', '四型间死亡率差异陡峭（表 2、图 2）。', 'ZH §3.2 补图 2 引用')
z = one(z, '（表 2、图 5）', '（表 2、图 3）', 'ZH 森林图引用改图 3')
z = one(z, '（*p* = 5.7 × 10⁻¹²⁹；图 3）', '（*p* = 5.7 × 10⁻¹²⁹；图 5）', 'ZH 水肿/CR 引用改图 5')
OLD_Z = ('![](D:/桌面/workbuddyzuopin/CPxiangmu/04_图/Fig3_edema_cr.png "6.3")\n\n'
         '**图 3**　院内死亡率按（A）前 24 小时内最差水肿等级与（B）毛细血管再充盈时间分层（MIMIC-IV 开发队列）。\n\n'
         '![](D:/桌面/workbuddyzuopin/CPxiangmu/04_图/Fig4_edema_grade.png "6.3")\n\n'
         '**图 4**　水肿等级与院内死亡：（A）各等级未校正死亡率；（B）多因素校正 OR 及 95%CI（参照 0 级）。校正后仅最高等级（全身性水肿）保持独立显著。\n\n'
         '![](D:/桌面/workbuddyzuopin/CPxiangmu/04_图/Fig5_forest_OR.png "4.2")\n\n'
         '**图 5**　按充血—灌注表型的院内死亡校正 OR（参照干暖型）。')
NEW_Z = ('![](D:/桌面/workbuddyzuopin/CPxiangmu/04_图/Fig3_forest_OR.png "4.2")\n\n'
         '**图 3**　按充血—灌注表型的院内死亡校正 OR（参照干暖型）。\n\n'
         '![](D:/桌面/workbuddyzuopin/CPxiangmu/04_图/Fig4_edema_grade.png "6.3")\n\n'
         '**图 4**　水肿等级与院内死亡：（A）各等级未校正死亡率；（B）多因素校正 OR 及 95%CI（参照 0 级）。校正后仅最高等级（全身性水肿）保持独立显著。\n\n'
         '![](D:/桌面/workbuddyzuopin/CPxiangmu/04_图/Fig5_edema_cr.png "6.3")\n\n'
         '**图 5**　院内死亡率按（A）前 24 小时内最差水肿等级与（B）毛细血管再充盈时间分层（MIMIC-IV 开发队列）。')
z = one(z, OLD_Z, NEW_Z, 'ZH 图注块重排')
io.open(p, 'w', encoding='utf-8').write(z)

# ----------[4] 旧措辞：补充表 S2 与 TRIPOD ----------
p = JCM + '/Supplementary_Tables_JCM.md'
t = io.open(p, encoding='utf-8').read()
t = one(t, 'Performance of the phenotype used as a zero-cost screening rule',
        'Performance of the phenotype used as a screening rule', 'S2 表题去 zero-cost')
io.open(p, 'w', encoding='utf-8').write(t)

p = JCM + '/TRIPOD_AI_Checklist.md'
t = io.open(p, encoding='utf-8').read()
t = one(t, 'Intended purpose: zero-cost bedside risk stratification and allocation of monitoring intensity',
        'Intended purpose: bedside risk stratification and allocation of monitoring intensity, requiring no additional data collection where the two signs are already charted',
        'TRIPOD 目的措辞')
io.open(p, 'w', encoding='utf-8').write(t)

# ----------[5] 重排脚本同步 ----------
p = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/jcm_fig_renumber.py'
t = io.open(p, encoding='utf-8').read()
t = t.replace("    'Fig3_edema_cr': 'Fig3_edema_cr',\n    'Fig4_edema_grade': 'Fig4_edema_grade',\n    'Fig9_forest_OR': 'Fig5_forest_OR',",
              "    'Fig4_edema_grade': 'Fig4_edema_grade',\n    'Fig9_forest_OR': 'Fig3_forest_OR',\n    'Fig3_edema_cr': 'Fig5_edema_cr',")
t = t.replace("order = ['Fig1_participant_flow', 'Fig2_quadrant_gradient', 'Fig3_edema_cr', 'Fig4_edema_grade',\n         'Fig5_forest_OR', 'Fig6_ROC', 'Fig7_calibration', 'Fig8_DCA', 'Fig9_trajectory']",
              "order = ['Fig1_participant_flow', 'Fig2_quadrant_gradient', 'Fig3_forest_OR', 'Fig4_edema_grade',\n         'Fig5_edema_cr', 'Fig6_ROC', 'Fig7_calibration', 'Fig8_DCA', 'Fig9_trajectory']")
io.open(p, 'w', encoding='utf-8').write(t)
LOG.append('ok  jcm_fig_renumber.py 已同步新编号')

print('\n'.join(LOG))
print('\n共 %d 项' % len(LOG))
