# -*- coding: utf-8 -*-
"""按引用顺序重排图号（**非破坏式**）：森林图→Fig5，ROC→Fig6，校准→Fig7，DCA→Fig8，SHAP→Fig9，轨迹→Fig10

与旧版的区别：先在暂存区把最终名**全部备齐**（中间名不存在时回退到已存在的最终名），
断言 10 张齐全之后才替换，因此可以安全重复运行，不会吃掉成品图。
"""
import os, shutil, ctypes
from ctypes import wintypes
from PIL import Image

OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/04_图'
TIF = OUT + '/figures_TIFF600'
JCMFIG = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM/Figures'
TMP = OUT + '/_stage'
os.makedirs(TMP, exist_ok=True); os.makedirs(JCMFIG, exist_ok=True); os.makedirs(TIF, exist_ok=True)

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

# 1) 备齐暂存区（优先用中间名；不在了就沿用已存在的最终名）
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
print('staged:', len(made), '/', len(MAP), '| missing:', missing)
assert not missing, '缺少图件，重排已中止（未删除任何文件）：%s' % missing


# 2) 替换成品（先送回收站，再从暂存区放回）
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
if victims:
    print('recycle code', recycle(victims))
for new in sorted(made):
    shutil.copy2(TMP + '/' + new + '.png', OUT + '/' + new + '.png')
for f in os.listdir(TMP):
    os.remove(TMP + '/' + f)
os.rmdir(TMP)

# 3) 600 dpi TIFF + 投 JCM 包
order = ['Fig1_participant_flow', 'Fig2_quadrant_gradient', 'Fig3_edema_cr', 'Fig4_edema_grade',
         'Fig5_forest_OR', 'Fig6_ROC', 'Fig7_calibration', 'Fig8_DCA', 'Fig9_SHAP', 'Fig10_trajectory']
for n in order:
    src = OUT + '/' + n + '.png'
    assert os.path.exists(src), 'missing ' + src
    im = Image.open(src).convert('RGB')
    im.save(TIF + '/' + n + '_600dpi.tif', 'TIFF', compression='tiff_lzw', dpi=(600, 600))
    shutil.copy2(TIF + '/' + n + '_600dpi.tif', JCMFIG + '/' + n + '_600dpi.tif')
    print('  %-30s %s %s' % (n + '.png', im.size, im.mode))

print()
print('=== 04_图 ===', sorted(f for f in os.listdir(OUT) if f.endswith('.png')))
print('=== TIFF600 ===', len(os.listdir(TIF)), 'files')
print('=== JCM/Figures ===', len(os.listdir(JCMFIG)), 'files')
