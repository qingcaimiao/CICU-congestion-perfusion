# -*- coding: utf-8 -*-
"""按引用顺序重排图号（**非破坏式**）。

当前方案（2026-10-12 第 11 轮起）：**主图 9 张**
  森林图→Fig5，ROC→Fig6，校准→Fig7，DCA→Fig8，轨迹→Fig9；
  SHAP 图**不进主图**，输出为补充图 `04_图/补充图/FigureS1_SHAP.png`。

机制：先把最终名在暂存区**全部备齐**（中间名不存在时回退到已存在的最终名），断言齐全后才替换，
因此可安全重复运行，不会吃掉成品图。
"""
import os, shutil, ctypes
from ctypes import wintypes
from PIL import Image

OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/04_图'
SUP = OUT + '/补充图'
TIF = OUT + '/figures_TIFF600'
JCMFIG = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM/Figures'
TMP = OUT + '/_stage'
for d in (TMP, SUP, TIF, JCMFIG):
    os.makedirs(d, exist_ok=True)

# 主图 9 张：中间名 → 最终名
MAP = {
    'Fig1_participant_flow': 'Fig1_participant_flow',
    'Fig2_quadrant_gradient': 'Fig2_quadrant_gradient',
    'Fig4_edema_grade': 'Fig4_edema_grade',
    'Fig9_forest_OR': 'Fig3_forest_OR',
    'Fig3_edema_cr': 'Fig5_edema_cr',
    'Fig5_ROC': 'Fig6_ROC',
    'Fig6_calibration': 'Fig7_calibration',
    'Fig7_DCA': 'Fig8_DCA',
    'Fig8_trajectory': 'Fig9_trajectory',
}
# 补充图：SHAP 从主图序列移出
SUPMAP = ['Fig10_SHAP', 'Fig9_SHAP']

# 1) 备齐暂存区
made, missing = [], []
for old, new in MAP.items():
    src = None
    for cand in (old, new):
        p = OUT + '/' + cand + '.png'
        if os.path.exists(p):
            src = p; break
    if src is None:
        missing.append(new); continue
    shutil.copy2(src, TMP + '/' + new + '.png'); made.append(new)
print('主图 staged:', len(made), '/', len(MAP), '| missing:', missing)
assert not missing, '缺少图件，重排已中止（未删除任何文件）：%s' % missing

sup_src = None
for cand in SUPMAP:
    p = OUT + '/' + cand + '.png'
    if os.path.exists(p):
        sup_src = p; break
if sup_src is None:
    sup_src = SUP + '/FigureS1_SHAP.png'
    assert os.path.exists(sup_src), '补充图缺失且主图序列中也没有：' + sup_src
print('补充图 source:', sup_src)


# 2) 替换成品
class SHFILEOPSTRUCTW(ctypes.Structure):
    _fields_ = [('hwnd', wintypes.HWND), ('wFunc', wintypes.UINT), ('pFrom', wintypes.LPCWSTR),
                ('pTo', wintypes.LPCWSTR), ('fFlags', ctypes.c_uint16),
                ('fAnyOperationsAborted', wintypes.BOOL), ('hNameMappings', ctypes.c_void_p),
                ('lpszProgressTitle', wintypes.LPCWSTR)]


def recycle(paths):
    op = SHFILEOPSTRUCTW(); op.wFunc = 3; op.pFrom = '\0'.join(paths) + '\0\0'
    op.fFlags = 0x40 | 0x10 | 0x4
    return ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op))


victims = [OUT + '/' + f for f in os.listdir(OUT) if f.startswith('Fig') and f.endswith('.png')]
victims += [TIF + '/' + f for f in os.listdir(TIF)]
victims += [JCMFIG + '/' + f for f in os.listdir(JCMFIG)]
if victims:
    print('recycle code', recycle(victims))
for new in sorted(made):
    shutil.copy2(TMP + '/' + new + '.png', OUT + '/' + new + '.png')
shutil.copy2(sup_src, SUP + '/FigureS1_SHAP.png')
for f in os.listdir(TMP):
    os.remove(TMP + '/' + f)
os.rmdir(TMP)

# 3) 600 dpi TIFF + 投稿包
order = ['Fig1_participant_flow', 'Fig2_quadrant_gradient', 'Fig3_forest_OR', 'Fig4_edema_grade',
         'Fig5_edema_cr', 'Fig6_ROC', 'Fig7_calibration', 'Fig8_DCA', 'Fig9_trajectory']
for n in order:
    src = OUT + '/' + n + '.png'
    assert os.path.exists(src), 'missing ' + src
    im = Image.open(src).convert('RGB')
    im.save(TIF + '/' + n + '_600dpi.tif', 'TIFF', compression='tiff_lzw', dpi=(600, 600))
    shutil.copy2(TIF + '/' + n + '_600dpi.tif', JCMFIG + '/' + n + '_600dpi.tif')
    print('  %-30s %s %s' % (n + '.png', im.size, im.mode))
im = Image.open(SUP + '/FigureS1_SHAP.png').convert('RGB')
im.save(SUP + '/FigureS1_SHAP_600dpi.tif', 'TIFF', compression='tiff_lzw', dpi=(600, 600))
print('  %-30s %s %s (补充图)' % ('FigureS1_SHAP.png', im.size, im.mode))

print()
print('=== 04_图 ===', sorted(f for f in os.listdir(OUT) if f.endswith('.png')))
print('=== 补充图 ===', sorted(os.listdir(SUP)))
print('=== TIFF600 ===', len(os.listdir(TIF)), 'files')
print('=== JCM/Figures ===', len(os.listdir(JCMFIG)), 'files')
