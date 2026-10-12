# -*- coding: utf-8 -*-
"""第五轮：正文（中英）修正 —— 定义域封闭性、校准限定、中心异质性、未迁移变量全列、零成本限定、轨迹降调"""
import io, os, shutil

J = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
EN, ZH = 'Manuscript_JCM_EN.md', '稿件_充血灌注_中文版_JCM.md'
LOG = []
for f in (EN, ZH):
    p = os.path.join(J, f)
    if not os.path.exists(p + '.bak_r5'):
        shutil.copyfile(p, p + '.bak_r5')


def sub(fn, pairs, tag):
    p = os.path.join(J, fn)
    s = io.open(p, encoding='utf-8').read()
    for old, new in pairs:
        n = s.count(old)
        if n == 0 and new in s:
            LOG.append('..  %-18s 已应用' % tag); continue
        assert n == 1, '[%s] 匹配 %d 次 -> %r' % (tag, n, old[:70])
        s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    LOG.append('ok  %-18s %d 处' % (tag, len(pairs)))


# ============================== EN ==============================
sub(EN, [
    # 1) eICU 取值域：非自由文本 + 封闭域 + 无不确定类别
    ("Bedside signs there are held in the *physicalExam* table as free-text paths and values.",
     "Bedside signs there are held in the *physicalExam* table as structured path-value pairs whose value domain is a closed, "
     "pre-specified set: peripheral oedema takes 12 distinct values (bilateral lower-extremity oedema, severity 1+ to 4+, "
     "anasarca, localized swelling, unilateral or upper-extremity swelling and no oedema), jugular venous distension takes 2 "
     "(jvd absent and jvd present), peripheral perfusion takes 4 (adequate, extremities cool, extremities cold/dusky and "
     "extremities flushed) and pulmonary auscultation takes 22. No indeterminate category such as not assessed, unable to "
     "assess, NA or deferred occurs anywhere in the database for these fields, so a field that is recorded is positive or "
     "negative by construction and an unrecorded field is never classified as positive."),
    # 2) 3.6 标题：校准限定
    ("### 3.6. External Replication: The Perfusion Sign Transports and the Transferred Model Is Well Calibrated;",
     "### 3.6. External Replication: The Perfusion Sign Transports and the Transferred Model Is Reasonably Calibrated on Average;"),
    # 3) 中心异质性 + 医院例数范围
    ("Discrimination was stable to the influence of individual centres: excluding each of the six contributing hospitals in turn moved the external AUROC between 0.786 and 0.846 (median 0.835), although one hospital (n = 84, 10 deaths) gave 0.643 (Table S9E).",
     "Discrimination was broadly preserved but clearly heterogeneous across centres: excluding each of the six contributing hospitals in turn moved the external AUROC between 0.786 and 0.846 (median 0.835), and one hospital (n = 84, 10 deaths) gave 0.643 (Table S9E). This spread is wide enough that centre-level performance should be treated as estimated only poorly, and the estimate is for the six centres that contributed, not for eICU-CRD as a whole."),
    ("(median 107 stays per hospital);", "(median 107 stays per hospital, range 1 to 957);"),
    # 4) 局限 (iii)：校准 + 未迁移变量全列 + 探索性
    ("The transferred model was well calibrated overall (observed-to-expected ratio 0.92, calibration slope 0.79), but this is an average across six hospitals and does not establish calibration in any new centre.",
     "The transferred model was reasonably calibrated on average (observed-to-expected ratio 0.92) but not at the extremes (calibration slope 0.79, intercept -0.44), and this is an average across six hospitals that does not establish calibration in any new centre; local recalibration should be undertaken before use."),
    ("Three prespecified comorbidities (coronary heart disease, diabetes and acute kidney injury) were extracted but not carried into the model, so residual confounding by these conditions is possible.",
     "With 152 events over 19 covariates the external events-per-variable ratio is 8.0 and the confidence intervals around the external estimates are correspondingly wide, so the external evaluation should be read as exploratory; the model is not proposed for clinical use without local recalibration. Finally, residual confounding must be considered in full: seven prespecified variables were not carried into the transferred model. Coronary heart disease, diabetes mellitus and acute kidney injury were extracted but not retained even in the development model. Invasive mechanical ventilation, any vasoactive drug infusion, congestive heart failure and chronic kidney disease were retained in the development model but could not be transferred, because eICU-CRD records ventilation and vasoactive therapy in treatment tables and comorbidity in free-text diagnosis strings that are not directly comparable to the MIMIC-IV items. The omitted variables are all markers of greater severity, so their absence would be expected to bias the external estimate of a severity-related phenotype toward the null, which is the direction in which the congestion axis already moved."),
    # 5) 切点乐观性
    ("This also makes the oedema axis intrinsically harder to reproduce:",
     "Because the cut-point was selected in the development set, the apparent increment of +0.0126 may be optimistic even though the sensitivity analyses at grade >=2 and >=4 were consistent (Table S9F). This also makes the oedema axis intrinsically harder to reproduce:"),
    # 6) 讨论中 free-text 措辞
    ("(oedema documented as free-text severity grades, jugular venous distension, auscultatory crackles)",
     "(oedema documented as graded severity, jugular venous distension, auscultatory crackles)"),
    # 7) 局限 (iv)：插补一致性
    ("Multiple imputation was not performed.",
     "Multiple imputation was not performed, but complete-case and median-imputation analyses agreed closely (Table S9G), so the principal conclusions do not depend on the imputation method."),
], 'EN 正文')

# ============================== ZH ==============================
ZH_PAIRS = [
    ("该库的床旁体征存于 *physicalExam* 表，以自由文本路径与取值记录。",
     "该库的床旁体征存于 *physicalExam* 表，以**结构化的路径—取值对**记录，取值域为封闭的预设集合："
     "外周水肿 12 种（双下肢水肿、1+~4+、全身性水肿、局限性肿胀、单侧或上肢肿胀，以及 no edema）、"
     "颈静脉充盈 2 种（jvd absent 与 jvd present）、周围灌注 4 种（adequate、extremities cool、extremities cold/dusky、extremities flushed）、"
     "肺部听诊 22 种。这些字段在整库中**不存在任何不确定类别**（not assessed、unable to assess、NA、deferred 等一概没有），"
     "因此**已记录即必为阳性或阴性，未记录绝不会被判为阳性**。"),
    ("### 3.6 外部复现：灌注体征可迁移、迁移模型校准良好；",
     "### 3.6 外部复现：灌注体征可迁移、迁移模型平均校准尚可；"),
    ("判别力对单一中心的影响稳健：依次剔除 6 家贡献医院中的任意一家，外部 AUROC 在 0.786~0.846 之间（中位 0.835），其中一家（n = 84，死亡 10 例）给出 0.643（补充表 S9E）。",
     "判别力总体保留，但**中心间差异明显**：依次剔除 6 家贡献医院中的任意一家，外部 AUROC 在 0.786~0.846 之间（中位 0.835），"
     "其中一家（n = 84，死亡 10 例）给出 0.643（补充表 S9E）。这一跨度足以说明院级表现只能视为粗估，"
     "且该估计仅代表这 6 家中心，而非 eICU-CRD 整体。"),
    ("（eICU-CRD 共 208 家医院，每家医院中位 107 例）", "（eICU-CRD 共 208 家医院，每家医院中位 107 例、范围 1~957 例）"),
    ("迁移模型总体校准良好（O:E 比 0.92、校准斜率 0.79），但这是 6 家医院的平均值，不足以证明在任何新中心均校准良好。",
     "迁移模型**平均**校准尚可（O:E 比 0.92），但**在风险分布两端并不理想**（校准斜率 0.79、截距 −0.44）；"
     "且这是 6 家医院的平均值，不足以证明在任何新中心均校准良好，投入临床前应行本地重校准。"),
    ("此外，冠心病、糖尿病与急性肾损伤三项预设合并症虽已提取但未进入模型，因此这些疾病带来的残余混杂不能排除。",
     "在 152 例事件 / 19 个协变量的条件下，**外部 EPV 仅 8.0**，外部估计的置信区间相应较宽，故外部验证应视为**探索性**，"
     "未经本地重校准不推荐直接用于临床。此外，残余混杂须完整交代：**共有 7 项预设变量未进入迁移模型**——"
     "冠心病、糖尿病、急性肾损伤三项虽已提取，但在开发模型中即未保留；有创机械通气、血管活性药输注、心力衰竭、慢性肾病四项"
     "保留于开发模型、却因 eICU-CRD 把通气与血管活性治疗记在治疗表、把合并症记在自由文本诊断中而无法迁移"
     "（与 MIMIC-IV 条目不可直接对应）。这些被省略的变量都是病情更重的标记，其缺失预期会把"
     "与严重程度相关的表型外部估计**推向无效**，而这正是充血轴已经呈现的方向。"),
    ("这也使水肿轴在本质上更难复现：",
     "由于切点是在开发集中选定的，表观的 +0.0126 增量**可能偏乐观**，尽管 ≥2 级与 ≥4 级的敏感性分析结果一致（补充表 S9F）。"
     "这也使水肿轴在本质上更难复现："),
    ("以自由文本严重度分级记录的水肿、颈静脉怒张、听诊啰音）",
     "以分级严重度记录的水肿、颈静脉怒张、听诊啰音）"),
    ("本研究未做多重插补。",
     "本研究未做多重插补，但完整案例分析与中位数插补分析结果高度一致（补充表 S9G），故主要结论不依赖于插补方法。"),
]
sub(ZH, ZH_PAIRS, 'ZH 正文')

print('\n'.join(LOG))
