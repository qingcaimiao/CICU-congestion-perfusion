# -*- coding: utf-8 -*-
"""投稿前收尾（三）：
1) cp_eicu_final.json 的 epv/n_vars 仍按"18 个连续变量"计（EPV 8.4），而稿件口径是
   "22 个待估参数（18 连续 + 性别 + 3 个表型哑变量）、EPV 6.9"。改为显式分列
   n_continuous_variables / n_parameters_excl_intercept / epv，避免与稿件冲突。
2) 把 3 个内部评审核查产物（critique checks）移出公开仓库 results/。
"""
import io, json, os, shutil

RES = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
G = 'D:/桌面/workbuddyzuopin/CPxiangmu/06_GitHub_CP'
GRES = G + '/results'

p = RES + '/cp_eicu_final.json'
d = json.load(io.open(p, encoding='utf-8'))
PLAN = {'with temperature': 23, 'temperature excluded': 22}   # 18 连续(+体温) + 性别 + 3 表型哑变量
for block, npar in PLAN.items():
    if block not in d:
        continue
    b = d[block]
    deaths = b['deaths']
    b['n_continuous_variables'] = b.pop('n_vars')
    b['n_parameters_excl_intercept'] = npar
    b['epv'] = round(float(deaths) / npar, 2)
    # 键顺序整理
    ordered = {}
    for k in ['apparent_auc', 'external_auc', 'oe', 'slope', 'intercept', 'n', 'deaths',
              'n_continuous_variables', 'n_parameters_excl_intercept', 'epv', 'mean_pred', 'obs']:
        if k in b:
            ordered[k] = b[k]
    for k in b:
        ordered.setdefault(k, b[k])
    d[block] = ordered
io.open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1) + '\n')
shutil.copy2(p, GRES + '/cp_eicu_final.json')
print(json.dumps(d, ensure_ascii=False, indent=1))

for f in ['cp_critique_checks.json', 'cp_critique2_checks.json', 'cp_critique2_fixes.json']:
    t = GRES + '/' + f
    if os.path.exists(t):
        os.remove(t); print('移出公开仓库:', f)
