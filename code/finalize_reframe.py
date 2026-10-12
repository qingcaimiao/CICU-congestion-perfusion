# -*- coding: utf-8 -*-
"""重定位收尾：引言研究问题、优势段补充、生成并追加 Table S8。"""
import io, os, shutil, pandas as pd

JCM = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
RES = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
EN = JCM + '/Manuscript_JCM_EN.md'
ZH = JCM + '/稿件_充血灌注_中文版_JCM.md'
LOG = []


def one(s, old, new, tag):
    if s.count(old) != 1:
        raise SystemExit('[%s] 匹配 %d 次' % (tag, s.count(old)))
    LOG.append('ok  ' + tag)
    return s.replace(old, new)


# ---------- 1. 引言研究问题 ----------
en = io.open(EN, encoding='utf-8').read()
en = one(en,
    'Second, do they add discriminatory, calibration and decision-analytic value beyond routinely available clinical variables?',
    'Second, do they add discriminatory, calibration and decision-analytic value beyond routinely available clinical variables, and how much of that value is contributed by each of the two axes?',
    'EN 引言问题二')
en = one(en,
    'several pre-specified analyses of alternative congestion definitions, and the analysis of a data element not previously used for risk stratification.',
    'several pre-specified analyses of alternative congestion definitions, an explicit decomposition of how much each axis contributes and of which axis transports, and the analysis of a data element not previously used for risk stratification.',
    'EN 优势段')
io.open(EN, 'w', encoding='utf-8').write(en)

zh = io.open(ZH, encoding='utf-8').read()
zh = one(zh,
    '第二，它们在常规可得临床变量之外是否带来判别、校准与决策分析层面的增量价值？',
    '第二，它们在常规可得临床变量之外是否带来判别、校准与决策分析层面的增量价值？其中又有多少由两轴各自贡献？',
    'ZH 引言问题二')
zh = one(zh,
    '若干针对替代充血定义的预设分析，以及使用了一个此前未用于风险分层的数据库字段。',
    '若干针对替代充血定义的预设分析，对"两轴各自贡献多少、哪一轴可迁移"的显式分解，以及使用了一个此前未用于风险分层的数据库字段。',
    'ZH 优势段')
io.open(ZH, 'w', encoding='utf-8').write(zh)

# ---------- 2. Table S8 ----------
S8 = """## Table S8. Contribution of each axis of the phenotype to discrimination

Each row is a separate model fitted on top of the routine covariate set; ΔAUROC is relative to that set, except where stated. Confidence intervals are percentile bootstrap intervals from 2,000 resamples. The four-phenotype row reproduces the estimate given in Table 3.

**Panel A. Development cohort (MIMIC-IV; n = 12,052; 758 deaths).** The routine covariate set comprises the 23 variables listed in Section 2.5.

| Model | Predictors | AUROC | ΔAUROC (95% CI) | Adjusted OR for the added term(s) (95% CI) |
|---|---|---|---|---|
| Routine variables only | 23 | 0.858 | — | — |
| + impaired perfusion (capillary refill >3 s) | 24 | 0.869 | +0.0101 (+0.0054 to +0.0149) | 3.24 (2.64–3.98) |
| + congestion, dichotomised (oedema ≥6 mm) | 24 | 0.862 | +0.0038 (+0.0010 to +0.0069) | 1.77 (1.43–2.20) |
| + congestion, ordinal (oedema grade, per level) | 24 | 0.864 | +0.0054 (+0.0019 to +0.0093) | 1.26 (1.17–1.36) |
| + both axes (four phenotypes) | 26 | 0.871 | +0.0126 (+0.0074 to +0.0186) | see Table 2 |
| + congestion added on top of perfusion | 25 | 0.871 | +0.0025† (+0.0006 to +0.0045) | 1.56 (1.25–1.94) |

† Increment relative to the model containing impaired perfusion alone.

**Panel B. Replication cohort (eICU-CRD; n = 1,541; 108 deaths).** Because the development-cohort congestion measurement is absent from this database and the alternative signs are different instruments, these models were fitted *within* eICU-CRD rather than by transferring coefficients, and are therefore exploratory. The routine covariate set comprises the 18 transferable variables plus sex, i.e. 19 predictors.

| Model | Predictors | AUROC | ΔAUROC (95% CI) | Adjusted OR for the added term(s) (95% CI) |
|---|---|---|---|---|
| Routine variables only | 19 | 0.861 | — | — |
| + impaired perfusion (documented inadequate perfusion) | 20 | 0.877 | +0.0155 (+0.0030 to +0.0301) | 3.26 (1.94–5.50) |
| + congestion (composite: oedema, jugular venous distension or crackles) | 20 | 0.862 | +0.0008 (−0.0018 to +0.0035) | 1.21 (0.73–2.00) |
| + both axes (four phenotypes) | 22 | 0.878 | +0.0163 (+0.0031 to +0.0313) | wet-warm 1.19 (0.64–2.24); dry-cold 4.13 (1.69–10.12); wet-cold 3.47 (1.72–7.01) |
| + both axes, as single terms | 21 | 0.877 | +0.0158 (+0.0025 to +0.0304) | perfusion 3.24 (1.92–5.47); congestion 1.07 (0.63–1.80) |

Once perfusion was accounted for, congestion retained a small but statistically significant increment in the development cohort (+0.0025 ΔAUROC; adjusted odds ratio 1.56, 95% CI 1.25 to 1.94) but contributed nothing in the replication cohort (odds ratio 1.07, 95% CI 0.63 to 1.80; AUROC 0.8769 → 0.8771 on adding the congestion term to a model already containing perfusion).
"""
open(RES + '/TableS8.md', 'w', encoding='utf-8').write(S8)

P = JCM + '/Supplementary_Tables_JCM.md'
sup = io.open(P, encoding='utf-8').read()
if not os.path.exists(P + '.bak_reframe'):
    shutil.copyfile(P, P + '.bak_reframe')
if 'Table S8.' not in sup:
    sup = sup.rstrip('\n') + '\n\n' + S8
    io.open(P, 'w', encoding='utf-8').write(sup)
    LOG.append('ok  追加 Table S8')
else:
    LOG.append('..  Table S8 已存在，跳过')

print('\n'.join(LOG))
print('\n完成')
