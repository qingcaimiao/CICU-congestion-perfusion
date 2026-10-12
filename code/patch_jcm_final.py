# -*- coding: utf-8 -*-
"""Final pre-submission revision of the JCM manuscripts.

Ten coordinated edits to each of 02_投稿包_JCM/Manuscript_JCM_EN.md and
02_投稿包_JCM/稿件_充血灌注_中文版_JCM.md:
 1. cite the TRIPOD+AI checklist (Supplementary File S2); add protocol/registration
    and patient-and-public-involvement statements
 2. renumber the data-quality issues (two -> three)
 3. document the implausible respiratory-rate values and the winsorisation sensitivity
 4. correct the standardisation description; point to Table S6 for the full model
 5. correct the transferred-model sample (1,555 -> 1,541, 108 deaths)
 6. add the case-mix comparison (Table S5) and the number of contributing hospitals
 7. correct the Figure 7 caption
 8. correct the external events-per-variable ratio (6.1 -> 6.0)
 9. list the new supplementary items
10. remove the Zenodo promise from the Data Availability statement
"""
import io

EN = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM/Manuscript_JCM_EN.md'
CN = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM/稿件_充血灌注_中文版_JCM.md'

en_edits = [
    # 1 reporting / protocol / PPI
    ("Reporting follows the STROBE statement for cohort studies (checklist provided as Supplementary File S1) and the TRIPOD+AI statement for the prediction-model components [17].",
     "Reporting follows the STROBE statement for cohort studies (checklist provided as Supplementary File S1) and the TRIPOD+AI statement for the prediction-model components [17] (checklist provided as Supplementary File S2). The study was not registered and no publicly available protocol was prepared; the statistical analysis plan was specified before any modelling was undertaken. No patients or members of the public were involved in the design, conduct, reporting or dissemination of this study."),
    # 2 two -> three
    ("Two unit and extraction issues were resolved on audit and are reported for reproducibility. First, temperature",
     "Three data-quality issues were identified on audit and are reported here for reproducibility. First, temperature"),
    # 3 third data-quality issue (respiratory rate) + winsorisation sensitivity
    ("systolic and mean arterial pressure were therefore taken as the minimum across non-invasive (`Non-Invasive BP Systolic`/`Mean`) and invasive (`Invasive BP Systolic`/`Mean`) sources.",
     "systolic and mean arterial pressure were therefore taken as the minimum across non-invasive (`Non-Invasive BP Systolic`/`Mean`) and invasive (`Invasive BP Systolic`/`Mean`) sources. Third, respiratory rate in MIMIC-IV contains a small number of implausible charted values: of 8,636,655 values of the respiratory-rate item, 476 exceeded 80/min and 54 exceeded 300/min, several of them stored in scientific notation (up to 7.0 x 10^6/min). Because a handful of such values inflate the standard deviation of the maximum respiratory rate by four orders of magnitude (from 6.6 to 67,322/min), the corresponding standardised covariate is effectively inert (odds ratio 0.86, 95% CI 0.007-112; Table S6). In a post hoc sensitivity analysis, winsorising respiratory rate at 80/min changed the full-model AUROC from 0.870 to 0.871 and the incremental AUROC from +0.0124 to +0.0123, and altered no phenotype odds ratio by more than 2%; the primary analysis therefore retains the values as charted."),
    # 4 standardisation wording + Table S6 pointer
    ("Continuous covariates were standardised; phenotype dummies and individual grade indicators were entered untransformed so that odds ratios are directly interpretable.",
     "Continuous covariates were standardised; binary indicators and the phenotype dummies were entered untransformed so that their odds ratios are directly interpretable. The full specification of both the development model and the transferred model - standardisation constants, all coefficients and the intercept - is given in Table S6 so that predictions can be reproduced in new individuals."),
    # 5 transferred-model sample size
    ("Applying the MIMIC-IV coefficients unchanged to the 1,555 eICU-CRD stays in which both axes were ascertainable gave an external AUROC of",
     "Of the 1,555 stays in which both axes were documented (Table 4, Figure 2), 1,541 (108 deaths) also met the pre-specified covariate-availability requirement (at least 60% of the transferable covariates recorded) and were used to evaluate the transferred model. Applying the MIMIC-IV coefficients unchanged to those 1,541 stays gave an external AUROC of"),
    # 6 case mix + hospitals
    ("Excluding temperature from the transferable set (the primary specification) rather than including it changed the external AUROC from 0.850 to 0.856.",
     "Excluding temperature from the transferable set (the primary specification) rather than including it changed the external AUROC from 0.850 to 0.856. The two analysis sets differed in case mix in ways relevant to the transferred model: the median minimum oxygen saturation was lower in the replication set (87% versus 93%), the maximum heart rate was higher (105 versus 95/min) and the phenotype was far more often classified as wet (wet-warm 42.4% versus 10.3%), reflecting the more sensitive composite congestion definition available in eICU-CRD (Table S5); these differences are consistent with the systematic over-prediction observed. The 1,555 analysable stays came from 6 of the 208 hospitals contributing to eICU-CRD (median 107 stays per hospital), so hospital-level variation in performance could not be estimated reliably."),
    # 7 Figure 7 caption
    ("(B) the eICU-CRD replication cohort (n = 1,555; coefficients transferred unchanged",
     "(B) the eICU-CRD replication cohort (n = 1,541; coefficients transferred unchanged"),
    # 8 EPV in limitations
    ("the analysable subset with both axes documented was 1,555 stays with 110 deaths and 18 transferable covariates, giving an external events-per-variable ratio of only 6.1",
     "the analysable subset with both axes documented was 1,555 stays (110 deaths), of which 1,541 (108 deaths) were used to evaluate the transferred 18-covariate model, giving an external events-per-variable ratio of only 6.0, and those stays came from only 6 of the 208 hospitals in eICU-CRD, so hospital-level performance could not be examined"),
    # 9 supplementary list (two edits)
    ("Supplementary File S1: STROBE checklist for this study. Table S1:",
     "Supplementary File S1: STROBE checklist for this study. Supplementary File S2: TRIPOD+AI checklist for this study. Table S1:"),
    ("Table S4: frequency of every charted value of the MIMIC-IV *Edema Amount* item (itemid 224862).",
     "Table S4: frequency of every charted value of the MIMIC-IV *Edema Amount* item (itemid 224862). Table S5: distribution of the transferable predictors in the development and replication analysis sets. Table S6: full specification of the development and transferred models (standardisation constants, coefficients, odds ratios and intercepts)."),
    # 10 data availability
    ("openly available at https://github.com/qingcaimiao/CICU-congestion-perfusion. A versioned archive with a permanent DOI will be deposited in Zenodo upon acceptance.",
     "openly available at https://github.com/qingcaimiao/CICU-congestion-perfusion (code snapshot commit 8630f92)."),
]

cn_edits = [
    ("报告遵循观察性队列研究的 STROBE 声明（清单见补充文件 S1）与预测模型部分的 TRIPOD+AI 声明[17]。",
     "报告遵循观察性队列研究的 STROBE 声明（清单见补充文件 S1）与预测模型部分的 TRIPOD+AI 声明[17]（清单见补充文件 S2）。本研究未注册、亦未制定公开的研究方案；统计分析计划在建模前已确定。本研究在设计、实施、报告与传播全过程中均无患者或公众参与。"),
    ("有两处单位与提取问题在核查中解决，一并报告以保证可复现。第一，体温",
     "有三处数据质量问题在核查中被识别，一并报告以保证可复现。第一，体温"),
    ("因此收缩压与平均动脉压取无创（`Non-Invasive BP Systolic`/`Mean`）与有创（`Invasive BP Systolic`/`Mean`）来源的最小值。",
     "因此收缩压与平均动脉压取无创（`Non-Invasive BP Systolic`/`Mean`）与有创（`Invasive BP Systolic`/`Mean`）来源的最小值。第三，MIMIC-IV 的呼吸频率存在少量不合理记录：该条目 8,636,655 条记录中，476 条 >80 次/分、54 条 >300 次/分，其中若干以科学计数法存储（最高达 7.0×10^6 次/分）。由于极少数此类数值使“最高呼吸频率”的标准差放大了四个数量级（由 6.6 升至 67,322 次/分），对应的标准化协变量在模型中实际无效（OR 0.86，95%CI 0.007–112；补充表 S6）。在事后敏感性分析中，将呼吸频率在 80 次/分处截尾，使全模型 AUROC 由 0.870 变为 0.871、增量 AUROC 由 +0.0124 变为 +0.0123，且未使任何表型 OR 变化超过 2%；因此主分析保留原始记录值。"),
    ("连续协变量标准化；表型哑变量与各等级指示变量不转换，使 OR 可直接解读。",
     "连续协变量标准化；二分类指示变量与表型哑变量不转换，使 OR 可直接解读。开发模型与迁移模型的完整设定——标准化常数、全部系数与截距——见补充表 S6，以便第三方在新个体中重现预测。"),
    ("将 MIMIC-IV 系数原样套用至两轴均可判定的 1,555 例 eICU-CRD 住院，**外部 AUROC 为 0.856**",
     "两轴均被记录的 1,555 例中，有 1,541 例（死亡 108 例）同时满足预设的协变量可得性要求（可迁移协变量记录率 ≥60%）并用于评估迁移模型（表 4、图 2）。将 MIMIC-IV 系数原样套用至这 1,541 例，**外部 AUROC 为 0.856**"),
    ("敏感性分析中，把体温纳入可迁移变量集（主设定为剔除）使外部 AUROC 由 0.850 变为 0.856。",
     "敏感性分析中，把体温纳入可迁移变量集（主设定为剔除）使外部 AUROC 由 0.850 变为 0.856。两个分析集的病例构成存在与迁移模型相关的差异：复现集最低血氧饱和度中位数更低（87% vs 93%）、最高心率更高（105 vs 95 次/分），且表型被判定为“湿”的比例高得多（湿暖型 42.4% vs 10.3%），后者反映了 eICU-CRD 可得的复合充血定义更为敏感（补充表 S5）；这些差异与观察到的系统性高估一致。可分析的 1,555 例来自 eICU-CRD 208 家医院中的 6 家（每家医院中位 107 例），因此无法可靠估计医院层面的表现差异。"),
    ("（B）eICU-CRD 复现队列（n = 1,555；系数原样迁移",
     "（B）eICU-CRD 复现队列（n = 1,541；系数原样迁移"),
    ("但两轴均有记录的可分析子集仅 1,555 例、死亡 110 例、可迁移协变量 18 个，**外部 EPV 仅 6.1**",
     "但两轴均有记录的可分析子集为 1,555 例（死亡 110 例），其中 1,541 例（死亡 108 例）用于评估迁移后的 18 协变量模型，**外部 EPV 仅 6.0**，且这些病例仅来自 eICU-CRD 208 家医院中的 6 家，无法考察医院层面的表现"),
    ("补充文件 S1：本研究的 STROBE 清单。补充表 S1：",
     "补充文件 S1：本研究的 STROBE 清单。补充文件 S2：本研究的 TRIPOD+AI 清单。补充表 S1："),
    ("补充表 S4：MIMIC-IV *Edema Amount* 项（itemid 224862）全部取值频数。",
     "补充表 S4：MIMIC-IV *Edema Amount* 项（itemid 224862）全部取值频数。补充表 S5：可迁移预测变量在开发集与复现集中的分布。补充表 S6：开发模型与迁移模型的完整设定（标准化常数、系数、OR 与截距）。"),
    ("已公开于 https://github.com/qingcaimiao/CICU-congestion-perfusion。带永久 DOI 的版本化存档将在论文被接收后存缴至 Zenodo。",
     "已公开于 https://github.com/qingcaimiao/CICU-congestion-perfusion（代码快照 commit 8630f92）。"),
]

for path, edits in [(EN, en_edits), (CN, cn_edits)]:
    t = io.open(path, encoding='utf-8').read()
    ok = 0
    for i, (a, b) in enumerate(edits, 1):
        if a in t:
            t = t.replace(a, b, 1)
            ok += 1
        else:
            print('MISS %s #%d: %s' % (path.split('/')[-1], i, a[:70]))
    io.open(path, 'w', encoding='utf-8').write(t)
    print('%s -> %d/%d edits applied' % (path.split('/')[-1], ok, len(edits)))
