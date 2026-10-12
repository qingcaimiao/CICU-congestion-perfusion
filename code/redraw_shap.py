# -*- coding: utf-8 -*-
"""按 tables_cp.py 的同一份重要性数据与同一绘图样式重绘 Fig9_SHAP.png（数据未变，仅恢复被误删的图件）"""
import pandas as pd, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
FIG = 'D:/桌面/workbuddyzuopin/CPxiangmu/04_图'
imp = pd.read_csv(OUT + '/T_shap_importance.csv').sort_values('v')      # 与 tables_cp.py 同步的排序
assert len(imp) == 25, len(imp)

fig, ax = plt.subplots(figsize=(4.6, 4.2))
cols = ['#B23A3A' if f in ('ew2', 'cr2') else '#8A8A8A' for f in imp.f]
ax.barh(list(imp.name), imp.v.values, color=cols)
ax.set_xlabel('Mean |SHAP value|')
ax.set_title('Variable importance, random forest', fontsize=8.6, loc='left')
plt.tight_layout(); plt.savefig(FIG + '/Fig9_SHAP.png', dpi=400); plt.close()
print('Fig9_SHAP.png redrawn from T_shap_importance.csv; top5:')
print(imp.tail(5).iloc[::-1][['name', 'v']].to_string(index=False))
