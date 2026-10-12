# -*- coding: utf-8 -*-
"""第四轮：补充材料 + TRIPOD + STROBE 同步（eICU 院内死亡口径、19 协变量、表 S3/S7/S8 重算）"""
import io, shutil, os, json, pandas as pd

J = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
RES = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
LOG = []
S = 'Supplementary_Tables_JCM.md'
s = io.open(os.path.join(J, S), encoding='utf-8').read()
if not os.path.exists(os.path.join(J, S + '.bak_r4')):
    shutil.copyfile(os.path.join(J, S), os.path.join(J, S + '.bak_r4'))

NL = chr(10)


def row(*cells):
    return '| ' + ' | '.join(str(c) for c in cells) + ' |' + NL


def dci(x, lo, hi):
    return '%+.4f (%+.4f to %+.4f)' % (x, lo, hi)


def orb(o, lo, hi):
    return '%.2f (%.2f-%.2f)' % (o, lo, hi)


# ---- 1. 计数与敏感性口径 ----
pairs = [
    ("The transferred model contains 18 covariates.",
     "The transferred model contains 19 covariates (the 18 continuously measured variables plus sex)."),
    ("| B. Transferred model (18 covariates, applied to eICU-CRD) |",
     "| B. Transferred model (19 covariates: 18 continuous variables plus sex) |"),
    ("The transferred 18-covariate model, applied unchanged",
     "The transferred 19-covariate model, applied unchanged"),
    ("(n = 1,541; 108 deaths).", "(n = 1,541; 152 deaths)."),
    ("| External AUROC (18 covariates) | 0.855 | 0.852 | 0.002 |",
     "| External AUROC (19 covariates) | 0.835 | 0.832 | 0.002 |"),
    ("| External calibration slope | 0.826 | 0.810 | 0.016 |",
     "| External calibration slope | 0.791 | 0.775 | 0.016 |"),
    ("| External calibration intercept | -0.870 | -0.903 | +0.033 |",
     "| External calibration intercept | -0.442 | -0.478 | +0.036 |"),
    ("| External observed-to-expected ratio | 0.66 | 0.65 | 0.01 |",
     "| External observed-to-expected ratio | 0.92 | 0.92 | 0.01 |"),
]
for old, new in pairs:
    n = s.count(old)
    if n == 0 and new in s:
        continue
    assert n >= 1, '补料未匹配 -> %r' % old[:70]
    s = s.replace(old, new)
LOG.append('ok  补料 计数/敏感性')

# ---- 2. 表 S3 ----
s3 = pd.read_csv(RES + '/TableS3_final.csv')
body = NL.join(row(r.definition, format(r.n, ','), r.deaths, '%.2f' % r.dry_warm, '%.2f' % r.wet_warm,
                   '%.2f' % r.dry_cold, '%.2f' % r.wet_cold, '%+.2f' % r.wet_minus_dry_warm,
                   '%+.2f' % r.dry_cold_minus_dry_warm) for r in s3.itertuples())
new_s3 = (row('Definition of congestion', 'n', 'Deaths', 'Dry-warm (%)', 'Wet-warm (%)', 'Dry-cold (%)',
              'Wet-cold (%)', 'Wet-warm - dry-warm (pp)', 'Dry-cold - dry-warm (pp)')
          + '|' + '|'.join(['---'] * 9) + '|' + NL + body)
i = s.index('| Definition of congestion |')
j = s.index(NL + NL + '---', i)
s = s[:i] + new_s3 + s[j:]

doc = json.load(open(RES + '/eicu_documentation_rates.json'))
old_para = 'Only stays in which congestion and perfusion were both *documented* (5–9% of stays) are included.'
new_para = ('Only stays in which congestion and perfusion were both *documented* are included. The three congestion fields were '
            'recorded in %.1f%% (peripheral oedema), %.1f%% (jugular venous distension) and %.1f%% (pulmonary crackles) of the '
            '%s cardiac ICU stays; at least one congestion field was recorded in %s stays (%.1f%%), and in %s stays (%.1f%%) '
            'none of the three was recorded at all. Perfusion was documented in %.1f%% of stays.'
            % (doc['edema'], doc['jvd'], doc['crackles'], format(doc['n'], ','),
               format(doc['any_congestion_field_n'], ','), doc['any_congestion_field'],
               format(doc['no_congestion_field'], ','), round(100 * doc['no_congestion_field'] / doc['n'], 1),
               doc['perfusion']))
assert s.count(old_para) == 1
s = s.replace(old_para, new_para)
s = s.replace('(−0.19 to +2.88 percentage points, i.e. no monotone or definition-robust congestion gradient)',
              '(%+.2f to %+.2f percentage points, i.e. no monotone or definition-robust congestion gradient)'
              % (s3.wet_minus_dry_warm.min(), s3.wet_minus_dry_warm.max()))
s = s.replace('(+21 to +27 percentage points)', '(+%.0f to +%.0f percentage points)'
              % (s3.dry_cold_minus_dry_warm.min(), s3.dry_cold_minus_dry_warm.max()))
LOG.append('ok  表 S3 重算')

# ---- 3. 表 S8 面板 B ----
ax = pd.read_csv(RES + '/axis_contribution_eicu.csv')
by = {r.model.split()[0]: r for r in ax.itertuples()}
R0, R1, R2, R3, R4 = by['R0'], by['R1'], by['R2'], by['R3'], by['R4']

s8 = ('**Panel B. Replication cohort (eICU-CRD; n = 1,541; 152 deaths).** Because the development-cohort congestion '
      'measurement is absent from this database and the alternative signs are different instruments, these models were '
      'fitted *within* eICU-CRD rather than by transferring coefficients, and are therefore exploratory. The routine '
      'covariate set comprises the 18 continuously measured transferable variables plus sex, i.e. 19 predictors.' + NL + NL
      + row('Model', 'Predictors', 'AUROC', 'ΔAUROC (95% CI)', 'Adjusted OR for the added term(s) (95% CI)')
      + '|' + '|'.join(['---'] * 5) + '|' + NL
      + row('Routine variables only', 19, '%.3f' % R0.auc, '—', '—')
      + row('+ impaired perfusion (documented inadequate perfusion)', 20, '%.3f' % R1.auc,
            dci(R1.dauc, R1.dauc_lo, R1.dauc_hi), orb(R1.OR_Perfusion, R1.OR_Perfusion_lo, R1.OR_Perfusion_hi))
      + row('+ congestion (composite: oedema, jugular venous distension or crackles)', 20, '%.3f' % R2.auc,
            dci(R2.dauc, R2.dauc_lo, R2.dauc_hi), orb(R2.OR_Congestion, R2.OR_Congestion_lo, R2.OR_Congestion_hi))
      + row('+ both axes (four phenotypes)', 22, '%.3f' % R3.auc, dci(R3.dauc, R3.dauc_lo, R3.dauc_hi),
            'wet-warm ' + orb(R3.OR_WetWarm, R3.OR_WetWarm_lo, R3.OR_WetWarm_hi)
            + '; dry-cold ' + orb(R3.OR_DryCold, R3.OR_DryCold_lo, R3.OR_DryCold_hi)
            + '; wet-cold ' + orb(R3.OR_WetCold, R3.OR_WetCold_lo, R3.OR_WetCold_hi))
      + row('+ both axes, as single terms', 21, '%.3f' % R4.auc, dci(R4.dauc, R4.dauc_lo, R4.dauc_hi),
            'perfusion ' + orb(R4.OR_Perfusion, R4.OR_Perfusion_lo, R4.OR_Perfusion_hi)
            + '; congestion ' + orb(R4.OR_Congestion, R4.OR_Congestion_lo, R4.OR_Congestion_hi))
      + NL)
i = s.index('**Panel B. Replication cohort (eICU-CRD; n = 1,541')
j = s.index('Once perfusion was accounted for', i)
s = s[:i] + s8 + s[j:]
old_close = ('but contributed nothing in the replication cohort (odds ratio 1.07, 95% CI 0.63 to 1.80; '
             'AUROC 0.8769 → 0.8771 on adding the congestion term to a model already containing perfusion).')
assert old_close in s
s = s.replace(old_close,
              'but contributed nothing in the replication cohort (odds ratio '
              + orb(R4.OR_Congestion, R4.OR_Congestion_lo, R4.OR_Congestion_hi)
              + '; AUROC %.4f → %.4f on adding the congestion term to a model already containing perfusion).'
              % (R1.auc, R4.auc))
LOG.append('ok  表 S8 面板 B 重算')

# ---- 4. 表 S9(F) 中文表头 ----
s = s.replace('| 切点 | ΔAUROC | 湿暖型 OR | 湿暖型 n |', '| Cut-point | ΔAUROC | Wet-warm OR | Wet-warm n |')
s = s.replace('| 水肿 ≥2 级 |', '| Oedema ≥2 |').replace('| 水肿 ≥3 级 |', '| Oedema ≥3 |').replace('| 水肿 ≥4 级 |', '| Oedema ≥4 |')
s = s.replace('| 时段 | n | ≥6mm 死亡% | ≥6mm n | <6mm 死亡% | 差(pp) |',
              '| Era | n | Mortality with oedema ≥6 mm (%) | n with ≥6 mm | Mortality with oedema <6 mm (%) | Difference (pp) |')
for a, b in [('| 2008 - 2010 |', '| 2008–2010 |'), ('| 2011 - 2013 |', '| 2011–2013 |'),
             ('| 2014 - 2016 |', '| 2014–2016 |'), ('| 2017 - 2019 |', '| 2017–2019 |'),
             ('| 2020 - 2022 |', '| 2020–2022 |')]:
    s = s.replace(a, b)
LOG.append('ok  表 S9(F) 表头')
io.open(os.path.join(J, S), 'w', encoding='utf-8').write(s)


def rep(fn, pairs, tag):
    p = os.path.join(J, fn)
    t = io.open(p, encoding='utf-8').read()
    if not os.path.exists(p + '.bak_r4'):
        shutil.copyfile(p, p + '.bak_r4')
    for old, new in pairs:
        n = t.count(old)
        if n == 0 and new in t:
            continue
        assert n >= 1, '[%s] 未匹配 -> %r' % (tag, old[:70])
        t = t.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(t)
    LOG.append('ok  %-8s %d 组' % (tag, len(pairs)))


rep('TRIPOD_AI_Checklist.md', [
    ("with 108 deaths", "with 152 deaths"),
    ("(intercept −0.87, slope 0.83, observed-to-expected ratio 0.66), demonstrating that the transferred model requires local recalibration before use",
     "(intercept −0.44, slope 0.79, observed-to-expected ratio 0.92), showing that average risk was estimated well, although a slope below 1 and the small number of contributing hospitals still make local recalibration advisable before use"),
    ("external 0.855", "external 0.835"),
    ("(intercept −0.87, slope 0.83, O:E 0.66; mean predicted risk 10.7% versus observed 7.0%)",
     "(intercept −0.44, slope 0.79, O:E 0.92; mean predicted risk 10.7% versus observed 9.9%)"),
], 'TRIPOD')

rep('STROBE_Checklist.md', [
    ("1,727 deaths in eICU-CRD (6.2%), 110 in the replication subset",
     "2,666 in-hospital deaths in eICU-CRD (9.6%), 156 in the replication subset"),
], 'STROBE')

print(NL.join(LOG))
