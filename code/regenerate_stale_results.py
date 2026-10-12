# -*- coding: utf-8 -*-
"""投稿前收尾（二）：把仓库中两个仍是"eICU 结局修正前"的结果文件重算。

1) results/TableS8.md —— Panel B 仍是 108 例死亡 / 0.861 / +0.0155 / +0.0008 的旧值
   （由 finalize_reframe.py 在重定位时硬编码写入，其后未随结局修正重跑）。
   本脚本从 axis_contribution_eicu.csv（结局修正后的重跑产物）动态生成 Panel B，
   Panel A 从 axis_contribution_mimic.csv 复核后原样保留。
2) results/T_eicu_congestion_definitions_full.csv —— 四象限计数用的是 ICU 级死亡（合计 1,727），
   改为院内死亡（合计 2,666）。
"""
import io, csv, shutil
import duckdb

RES = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
G = 'D:/桌面/workbuddyzuopin/CPxiangmu/06_GitHub_CP/results'
EICU = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data/eicu_cp.parquet'


def f3(x):
    return '%.3f' % x


def f4(x):
    return '%+.4f' % x


def ci(lo, hi):
    return '(%+.4f to %+.4f)' % (lo, hi)


def rng(lo, hi):
    return '%.2f-%.2f' % (lo, hi)


def load(p):
    with io.open(p, encoding='utf-8') as fh:
        return {r['model']: r for r in csv.DictReader(fh)}


def num(d, k):
    v = d.get(k, '')
    return float(v) if v not in ('', None) else None


# ---------- 1) TableS8.md ----------
mm = load(RES + '/axis_contribution_mimic.csv')
ee = load(RES + '/axis_contribution_eicu.csv')

# 复核 Panel A 与既有文件一致（若不一致则中止，避免误改）
for key, auc, dauc in [('M0 常规变量（23）', '0.858', None),
                       ('M1 常规 + 灌注（CRT）', '0.869', '+0.0101'),
                       ('M2 常规 + 充血（水肿≥6mm）', '0.862', '+0.0038'),
                       ('M2b 常规 + 充血（水肿每级）', '0.864', '+0.0054'),
                       ('M3 常规 + 四象限表型', '0.871', '+0.0126'),
                       ('M4 常规 + 灌注 + 充血（同尺度）', '0.871', '+0.0025')]:
    assert f3(num(mm[key], 'auc')) == auc, (key, num(mm[key], 'auc'))
    if dauc:
        assert f4(num(mm[key], 'dauc')) == dauc, (key, num(mm[key], 'dauc'))
print('Panel A 复核通过（未改动）')

R0, R1, R2, R3, R4 = (ee['R0 eICU 常规变量（18）'], ee['R1 eICU + 灌注'],
                      ee['R2 eICU + 充血（复合）'], ee['R3 eICU + 四象限'],
                      ee['R4 eICU + 灌注 + 充血'])

rowsB = [
    ('Routine variables only', 19, f3(num(R0, 'auc')), '—', '—'),
    ('+ impaired perfusion (documented inadequate perfusion)', 20, f3(num(R1, 'auc')),
     '%s %s' % (f4(num(R1, 'dauc')), ci(num(R1, 'dauc_lo'), num(R1, 'dauc_hi'))),
     '%s (%s)' % ('%.2f' % num(R1, 'OR_Perfusion'), rng(num(R1, 'OR_Perfusion_lo'), num(R1, 'OR_Perfusion_hi')))),
    ('+ congestion (composite: oedema, jugular venous distension or crackles)', 20, f3(num(R2, 'auc')),
     '%s %s' % (f4(num(R2, 'dauc')), ci(num(R2, 'dauc_lo'), num(R2, 'dauc_hi'))),
     '%s (%s)' % ('%.2f' % num(R2, 'OR_Congestion'), rng(num(R2, 'OR_Congestion_lo'), num(R2, 'OR_Congestion_hi')))),
    ('+ both axes (four phenotypes)', 22, f3(num(R3, 'auc')),
     '%s %s' % (f4(num(R3, 'dauc')), ci(num(R3, 'dauc_lo'), num(R3, 'dauc_hi'))),
     'wet-warm %s (%s); dry-cold %s (%s); wet-cold %s (%s)' % (
         '%.2f' % num(R3, 'OR_WetWarm'), rng(num(R3, 'OR_WetWarm_lo'), num(R3, 'OR_WetWarm_hi')),
         '%.2f' % num(R3, 'OR_DryCold'), rng(num(R3, 'OR_DryCold_lo'), num(R3, 'OR_DryCold_hi')),
         '%.2f' % num(R3, 'OR_WetCold'), rng(num(R3, 'OR_WetCold_lo'), num(R3, 'OR_WetCold_hi')))),
    ('+ both axes, as single terms', 21, f3(num(R4, 'auc')),
     '%s %s' % (f4(num(R4, 'dauc')), ci(num(R4, 'dauc_lo'), num(R4, 'dauc_hi'))),
     'perfusion %s (%s); congestion %s (%s)' % (
         '%.2f' % num(R4, 'OR_Perfusion'), rng(num(R4, 'OR_Perfusion_lo'), num(R4, 'OR_Perfusion_hi')),
         '%.2f' % num(R4, 'OR_Congestion'), rng(num(R4, 'OR_Congestion_lo'), num(R4, 'OR_Congestion_hi')))),
]

NL = '\n'
txt = [
    '## Table S8. Contribution of each axis of the phenotype to discrimination',
    '',
    'Each row is a separate model fitted on top of the routine covariate set; \u0394AUROC is relative to that set, '
    'except where stated. Confidence intervals are percentile bootstrap intervals from 2,000 resamples. The '
    'four-phenotype row reproduces the estimate given in Table 3.',
    '',
    '**Panel A. Development cohort (MIMIC-IV; n = 12,052; 758 deaths).** The routine covariate set comprises the 23 '
    'variables listed in Section 2.5.',
    '',
    '| Model | Predictors | AUROC | \u0394AUROC (95% CI) | Adjusted OR for the added term(s) (95% CI) |',
    '|---|---|---|---|---|',
    '| Routine variables only | 23 | 0.858 | \u2014 | \u2014 |',
    '| + impaired perfusion (capillary refill >3 s) | 24 | 0.869 | +0.0101 (+0.0054 to +0.0149) | 3.24 (2.64\u20133.98) |',
    '| + congestion, dichotomised (oedema \u22656 mm) | 24 | 0.862 | +0.0038 (+0.0010 to +0.0069) | 1.77 (1.43\u20132.20) |',
    '| + congestion, ordinal (oedema grade, per level) | 24 | 0.864 | +0.0054 (+0.0019 to +0.0093) | 1.26 (1.17\u20131.36) |',
    '| + both axes (four phenotypes) | 26 | 0.871 | +0.0126 (+0.0074 to +0.0186) | see Table 2 |',
    '| + congestion added on top of perfusion | 25 | 0.871 | +0.0025\u2020 (+0.0006 to +0.0045) | 1.56 (1.25\u20131.94) |',
    '',
    '\u2020 Increment relative to the model containing impaired perfusion alone.',
    '',
    '**Panel B. Replication cohort (eICU-CRD; n = 1,541; 152 in-hospital deaths).** Because the development-cohort '
    'congestion measurement is absent from this database and the alternative signs are different instruments, these '
    'models were fitted *within* eICU-CRD rather than by transferring coefficients, and are therefore exploratory. The '
    'routine covariate set comprises the 18 transferable variables plus sex, i.e. 19 predictors.',
    '',
    '| Model | Predictors | AUROC | \u0394AUROC (95% CI) | Adjusted OR for the added term(s) (95% CI) |',
    '|---|---|---|---|---|',
]
for a, b, c, d, e in rowsB:
    txt.append('| %s | %d | %s | %s | %s |' % (a, b, c, d, e))
txt += [
    '',
    'Once perfusion was accounted for, congestion retained a small but statistically significant increment in the '
    'development cohort (+0.0025 \u0394AUROC; adjusted odds ratio 1.56, 95%% CI 1.25 to 1.94) but contributed no '
    'increment in the replication cohort (odds ratio %s, 95%% CI %s; AUROC %s \u2192 %s on adding the congestion term '
    'to a model already containing perfusion), a null increment whose confidence interval crosses zero.'
    % ('%.2f' % num(R4, 'OR_Congestion'), rng(num(R4, 'OR_Congestion_lo'), num(R4, 'OR_Congestion_hi')),
       f3(num(R4, 'auc') - num(R4, 'dauc')), f3(num(R4, 'auc'))),
    '',
]
io.open(RES + '/TableS8.md', 'w', encoding='utf-8').write(NL.join(txt))
shutil.copy2(RES + '/TableS8.md', G + '/TableS8.md')
print('TableS8.md 已重生成（Panel B 死亡数 %d）' % 152)
for x in rowsB:
    print('   ', ' | '.join(str(i) for i in x))

# ---------- 2) T_eicu_congestion_definitions_full.csv ----------
c = duckdb.connect(); c.execute('PRAGMA threads=8')
c.execute("CREATE OR REPLACE TABLE t AS SELECT * FROM read_parquet('%s')" % EICU)
DEFS = [('oedema only', 'coalesce(edema_pos,0)'),
        ('JVD only', 'coalesce(jvd_pos,0)'),
        ('crackles only', 'coalesce(crackles,0)'),
        ('composite (any)', 'CASE WHEN coalesce(edema_pos,0)=1 OR coalesce(jvd_pos,0)=1 OR coalesce(crackles,0)=1 THEN 1 ELSE 0 END')]
out = [('definition', 'cell', 'n', 'deaths', 'mortality')]
for name, expr in DEFS:
    q = """
    SELECT CASE WHEN {e}=1 AND coalesce(hypoperf,0)=1 THEN 'wet-cold'
                WHEN {e}=1 AND coalesce(hypoperf,0)=0 THEN 'wet-warm'
                WHEN {e}=0 AND coalesce(hypoperf,0)=1 THEN 'dry-cold'
                ELSE 'dry-warm' END AS cell,
           count(*) AS n, sum(died) AS deaths
    FROM t GROUP BY 1 ORDER BY 2""".format(e=expr)
    for cell, n, d in c.execute(q).fetchall():
        out.append((name, cell, int(n), int(d), '%.2f' % (100.0 * d / n)))
order = {'wet-cold': 0, 'wet-warm': 1, 'dry-cold': 2, 'dry-warm': 3}
out = [out[0]] + sorted(out[1:], key=lambda r: (r[0], order[r[1]]))
with io.open(RES + '/T_eicu_congestion_definitions_full.csv', 'w', encoding='utf-8', newline='') as fh:
    csv.writer(fh).writerows(out)
shutil.copy2(RES + '/T_eicu_congestion_definitions_full.csv', G + '/T_eicu_congestion_definitions_full.csv')
tot = {r[0]: sum(x[3] for x in out[1:] if x[0] == r[0]) for r in out[1:]}
print('T_eicu_congestion_definitions_full.csv 已重生成，各定义死亡合计:', tot)
