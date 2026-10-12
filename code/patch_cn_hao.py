# -*- coding: utf-8 -*-
p = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包/稿件_充血灌注_中文版.md'
t = open(p, encoding='utf-8').read()

OLD1 = ("第三，**动态轨迹表型本身是重症领域的一条活跃路线**：以组基轨迹模型（GBTM）分析三个 ICU 数据库中前 72 小时"
        "**累积液体平衡**，可识别出 28 天死亡率差异显著的稳定亚型，且在校正基线严重度后轨迹本身仍具预后意义[27]；"
        "心衰出院后以生物阻抗测得的水肿指数轨迹亦与结局相关[14]。但两者均不涉及**急性 ICU 住院期间每班记录的凹陷深度**："
        "液体平衡是由完整出入量推导的累积量，水肿指数研究始于出院之后。值得注意的是，上述液体平衡轨迹研究本身也报告，"
        "在复现队列中相关记录**过于稀疏、根本无法分类轨迹**——这恰恰构成检验更简单、记录更普遍的体征是否可用的理由。"
        "ICU 内每班记录的水肿凹陷深度能否在急性心脏 ICU 住院期界定出有信息的短窗轨迹、且该轨迹能否被可复现地分类，尚未被研究。")
NEW1 = ("第三，**动态轨迹表型本身是重症领域的一条活跃路线**。以组基轨迹模型（GBTM）分析三个 ICU 数据库中前 72 小时"
        "**累积液体平衡**，可识别出 28 天死亡率差异显著的稳定亚型[27]；而一项连同分析代码一并存档的新近分析报告："
        "**任何外周水肿**在 ICU 第一周的轨迹与 28 天及 90 天死亡独立相关，该关联**仅部分由液体平衡介导**、"
        "并似**仅限于非脓毒症患者**，且——对本研究尤为关键——**eICU-CRD 中外周部位记录过于稀疏，根本无法分类轨迹**[28]；"
        "心衰出院后以生物阻抗测得的水肿指数轨迹亦与结局相关[14]。但以上工作均不涉及**急性心脏 ICU 住院期间每班记录的"
        "有序凹陷深度**：液体平衡是由完整出入量推导的累积量；外周水肿轨迹分析系孤立考察水肿、面向综合 ICU 人群、覆盖第一周；"
        "水肿指数研究则始于出院之后。ICU 内每班记录的水肿凹陷深度在与周围灌注联合、且以心脏 ICU 人群为对象时能否界定出"
        "有信息的短窗轨迹、且该轨迹能否在第二个数据库中被可复现地分类，尚未被研究。")
assert OLD1 in t, 'CN intro not found'
t = t.replace(OLD1, NEW1)

OLD2 = ("第三，水肿**轨迹**与结局的关系已在心衰住院后、以生物阻抗法测得的 oedema index 在护理门诊随访 6 个月的研究中被报道[14]。"
        "该工作测量的是**出院后、定量、重复**的水肿；本研究使用的是**急性 ICU 住院期间、每班记录、有序分级**的床旁凹陷深度"
        "——这正是该信息在诊疗现场实际存在的形式——覆盖的是病程更早的阶段。")
NEW2 = OLD2 + ("另一项对 MIMIC-IV 与 MIMIC-III CareVue 的平行分析（以数据存档形式发布，随附一份已投 *Scientific Reports*、"
        "**尚未经同行评议**的稿件）同样报告：任何外周水肿在 ICU 第一周的早期轨迹与 28 天及 90 天死亡独立相关，"
        "该关联仅部分由液体平衡介导、且似仅见于非脓毒症患者，并指出 eICU-CRD 中外周部位记录过于稀疏、无法分类轨迹[28]。"
        "本研究的差异有三：轨迹窗口（入 ICU 后 0–24 小时与 24–72 小时按班次划分，而非第一周）；人群（未选择的心脏 ICU 队列，"
        "而非综合 ICU 队列）；暴露定义（有序的护士勾选凹陷深度并联合毛细血管再充盈，而非孤立的外周水肿）。"
        "值得注意的是，两项分析在**第二个数据库上得出同一结论**——该库的外周床旁记录过于稀疏，无法支持轨迹分类——"
        "这恰好**印证**而非削弱了本文随后提出的\u201c依赖记录方式\u201d这一论点。")
assert OLD2 in t, 'CN discussion not found'
t = t.replace(OLD2, NEW2)

OLD3 = "而 eICU-CRD 中相应床旁字段的记录率不足十分之一，**根本无法构建轨迹表型**。因此轨迹结果应视为产生假设。"
NEW3 = ("而 eICU-CRD 中相应床旁字段的记录率不足十分之一，**根本无法构建轨迹表型**——这一局限已被他人针对同一数据库独立报告[28]。"
        "因此轨迹结果应视为产生假设。")
assert OLD3 in t, 'CN limitation not found'
t = t.replace(OLD3, NEW3)

OLD4 = ("- **27.** Wang K, Xiong H, Zhu Y, Zhou Y, Kang Y. Distinct 72-hour fluid balance trajectories are associated with "
        "28-day mortality in a multicenter cohort of sepsis patients. Sci Rep. 2026;16:15126. "
        "doi:10.1038/s41598-026-46063-2（PMID 41888401）。本轮新增，用于与本文轨迹分析作差异化对照；"
        "Europe PMC 与 PubMed 均命中，Crossref 反查通过。")
NEW4 = OLD4 + ("\n- **28.** Hao Y, Qin L, Zhang Q, Chen S, Li P, Wan J, Ye H. Peripheral edema trajectories as a dynamic bedside "
        "prognostic marker in critically ill adults: analysis code and aggregate results (v1.2.1) [Data set]. Zenodo. 2026. "
        "doi:10.5281/zenodo.22674523。随附稿件已投 *Scientific Reports*（**尚未经同行评议**）。"
        "经 **DataCite**（Zenodo DOI 的权威注册机构）核实：题名、作者、版本 1.2.1、发布日期 2026-09-09、MIT 许可、"
        "资源类型 Software 均一致；DOI 元数据仅登记首位创作者 Hao Y，完整作者名单见存档描述。")
assert OLD4 in t, 'CN ref27 not found'
t = t.replace(OLD4, NEW4)

open(p, 'w', encoding='utf-8').write(t)
print('CN edits applied. ref28:', '22674523' in t, '| [28] citations:', t.count('[28]'))
