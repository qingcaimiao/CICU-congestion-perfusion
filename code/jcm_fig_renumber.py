# -*- coding: utf-8 -*-
"""按引用顺序重排图号：森林图→Fig5，ROC→Fig6，校准→Fig7，DCA→Fig8，SHAP→Fig9，轨迹→Fig10"""
import os, shutil, ctypes
from ctypes import wintypes
from PIL import Image

OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/04_图'
TIF = OUT + '/figures_TIFF600'
JCMFIG = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM/Figures'
TMP = OUT + '/_stage'
os.makedirs(TMP, exist_ok=True); os.makedirs(JCMFIG, exist_ok=True)

MAP = {
    'Fig1_participant_flow': 'Fig1_participant_flow',
    'Fig2_quadrant_gradient': 'Fig2_quadrant_gradient',
    'Fig3_edema_cr': 'Fig3_edema_cr',
    'Fig4_edema_grade': 'Fig4_edema_grade',
    'Fig9_forest_OR': 'Fig5_forest_OR',
    'Fig5_ROC': 'Fig6_ROC',
    'Fig6_calibration': 'Fig7_calibration',
    'Fig7_DCA': 'Fig8_DCA',
    'Fig10_SHAP': 'Fig9_SHAP',
    'Fig8_trajectory': 'Fig10_trajectory',
}

# 1) 复制到暂存区（最终名）
made = []
for old, new in MAP.items():
    p = OUT + '/' + old + '.png'
    if os.path.exists(p):
        shutil.copy2(p, TMP + '/' + new + '.png'); made.append(new + '.png')
print('staged PNGs:', len(made))

# 2) 删除现有全部 Fig*.png 与 Fig*.tif（送回收站）
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
victims += [TIF + '/' + f for f in os.listdir(TIF)] if os.path.isdir(TIF) else []
if victims:
    print('recycle code', recycle(victims), '| all gone:', all(not os.path.exists(v) for v in victims))

# 3) 从暂存区放回，并生成 600dpi TIFF + 投 JCM 包
for new in sorted(made):
    shutil.copy2(TMP + '/' + new, OUT + '/' + new)
for f in os.listdir(TMP):
    os.remove(TMP + '/' + f)
os.rmdir(TMP)

order = ['Fig1_participant_flow', 'Fig2_quadrant_gradient', 'Fig3_edema_cr', 'Fig4_edema_grade',
         'Fig5_forest_OR', 'Fig6_ROC', 'Fig7_calibration', 'Fig8_DCA', 'Fig9_SHAP', 'Fig10_trajectory']
for n in order:
    src = OUT + '/' + n + '.png'
    im = Image.open(src).convert('RGB')
    im.save(TIF + '/' + n + '_600dpi.tif', 'TIFF', compression='tiff_lzw', dpi=(600, 600))
    shutil.copy2(TIF + '/' + n + '_600dpi.tif', JCMFIG + '/' + n + '_600dpi.tif')
    print('  %-30s %s %s' % (n + '.png', im.size, im.mode))

print()
print('=== 04_图 ===', sorted(f for f in os.listdir(OUT) if f.endswith('.png')))
print('=== TIFF600 ===', sorted(os.listdir(TIF)))
print('=== JCM/Figures ===', sorted(os.listdir(JCMFIG)))
