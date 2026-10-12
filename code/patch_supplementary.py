# -*- coding: utf-8 -*-
"""更新补充材料（Table S5/S6 重建 + 追加 Table S7）、TRIPOD/STROBE 清单与 Cover letter 的数值。"""
import io, os, shutil, pandas as pd

JCM = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
RES = 'D:/桌面/workbuddyzuopin/CPxiangmu/03_结果'
LOG = []


def rep(s, old, new, tag):
    if old not in s:
        raise SystemExit('未找到 [%s]: %s' % (tag, old[:160]))
    if s.count(old) != 1:
        raise SystemExit('[%s] 出现 %d 次' % (tag, s.count(old)))
    LOG.append('ok  ' + tag)
    return s.replace(old, new)


def md_table(csv_path, header):
    df = pd.read_csv(csv_path)
    cols = list(df.columns)
    rows = ['| ' + ' | '.join(cols) + ' |', '|' + '|'.join(['---'] * len(cols)) + '|']
    for _, r in df.iterrows():
        rows.append('| ' + ' | '.join(str(r[c]) for c in cols) + ' |')
    return rows


def swap_table(text, header_line, new_rows, tag):
    lines = text.split('\n')
    idx = [i for i, l in enumerate(lines) if l.strip() == header_line.strip()]
    if len(idx) != 1:
        raise SystemExit('[%s] 表头匹配 %d 次' % (tag, len(idx)))
    i = idx[0]
    # 表头行 + 分隔行，其后为数据行
    j = i + 2
    while j < len(lines) and lines[j].startswith('|'):
        j += 1
    LOG.append('ok  %s（替换 %d 行）' % (tag, j - (i + 2)))
    return '\n'.join(lines[:i + 2] + new_rows + lines[j:])


# ---------------- 补充材料 ----------------
P = JCM + '/Supplementary_Tables_JCM.md'
sup = io.open(P, encoding='utf-8').read()
if not os.path.exists(P + '.bak_2601'):
    shutil.copyfile(P, P + '.bak_2601')
sup = swap_table(sup, '| Variable | Type | Development | Replication | SMD |',
                 md_table(RES + '/TableS5_predictor_distributions.csv',
                          'Variable|Type|Development|Replication|SMD'), 'Table S5')
sup = swap_table(sup, '| Panel | Term | Coding | Median | SD | beta | SE | OR | OR_low | OR_high | p |',
                 md_table(RES + '/TableS6_full_model_coefficients.csv',
                          'Panel|Term|Coding|Median|SD|beta|SE|OR|OR_low|OR_high|p'), 'Table S6')
sup = rep(sup,
    ' The maximum respiratory rate carries an inflated SD because of a small number of implausible values in MIMIC-IV (Section 2.5) and is therefore inert.',
    ' Every covariate is summarised after the pre-specified plausibility screen (Section 2.5, Table S7).',
    'S6 注释')
sup = sup.rstrip('\n') + '\n\n' + io.open(RES + '/TableS7.md', encoding='utf-8').read().strip() + '\n'
io.open(P, 'w', encoding='utf-8').write(sup)
LOG.append('ok  追加 Table S7')

# ---------------- Cover letter ----------------
P = JCM + '/Cover_Letter_JCM.md'
cl = io.open(P, encoding='utf-8').read()
shutil.copyfile(P, P + '.bak_2601')
cl = rep(cl, 'raised the AUROC from 0.858 to 0.870 (Δ +0.0124, 95% CI +0.0069 to +0.0177), with preserved temporal discrimination (0.853)',
             'raised the AUROC from 0.858 to 0.871 (Δ +0.0126, 95% CI +0.0074 to +0.0186), with preserved temporal discrimination (0.851)',
             'CL EN 数值')
cl = rep(cl, 'AUROC 由 0.858 升至 0.870（Δ +0.0124，95%CI +0.0069~+0.0177），时间验证判别力 0.853',
             'AUROC 由 0.858 升至 0.871（Δ +0.0126，95%CI +0.0074~+0.0186），时间验证判别力 0.851',
             'CL ZH 数值')
io.open(P, 'w', encoding='utf-8').write(cl)

# ---------------- TRIPOD+AI ----------------
P = JCM + '/TRIPOD_AI_Checklist.md'
tp = io.open(P, encoding='utf-8').read()
shutil.copyfile(P, P + '.bak_2601')
tp = rep(tp, '(intercept −0.97, slope 0.76, observed-to-expected ratio 0.65)',
             '(intercept −0.87, slope 0.83, observed-to-expected ratio 0.66)', 'TRIPOD 12f')
tp = rep(tp, 'AUROC (0.858 → 0.870 with the phenotype; external 0.856), ΔAUROC with a 95% bootstrap confidence interval, IDI, continuous and categorical NRI, calibration deciles with the highest decile predicted 35.5% versus observed 34.8%,',
             'AUROC (0.858 → 0.871 with the phenotype; external 0.855), ΔAUROC with a 95% bootstrap confidence interval, IDI, continuous and categorical NRI, calibration deciles with the highest decile predicted 35.8% versus observed 35.1%,',
             'TRIPOD 23a')
tp = rep(tp, '(intercept −0.97, slope 0.76, O:E 0.65; mean predicted risk 10.7% versus observed 7.0%)',
             '(intercept −0.87, slope 0.83, O:E 0.66; mean predicted risk 10.7% versus observed 7.0%)', 'TRIPOD 24')
io.open(P, 'w', encoding='utf-8').write(tp)

# ---------------- STROBE ----------------
P = JCM + '/STROBE_Checklist.md'
st = io.open(P, encoding='utf-8').read()
shutil.copyfile(P, P + '.bak_2601')
st = rep(st, 'adjusted odds ratios with 95% CIs (wet-warm 1.63, dry-cold 3.13, wet-cold 4.44)',
             'adjusted odds ratios with 95% CIs (wet-warm 1.63, dry-cold 3.20, wet-cold 4.49)', 'STROBE 16')
io.open(P, 'w', encoding='utf-8').write(st)

print('\n'.join(LOG))
print('\n完成')
