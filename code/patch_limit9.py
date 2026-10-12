# -*- coding: utf-8 -*-
import io
EN='D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM/Manuscript_JCM_EN.md'
CN='D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM/稿件_充血灌注_中文版_JCM.md'
pairs=[
 (EN,"Eighth, patients with missing covariates were excluded from the primary model, although missingness was low.",
     "Eighth, patients with missing covariates were excluded from the primary model, although missingness was low. Ninth, we did not examine model performance or phenotype prevalence by sex, age or any other sociodemographic subgroup, and no fairness analysis was undertaken; because the two databases also differ in healthcare system, documentation practice and case mix, subgroup transportability remains untested."),
 (CN,"第八，主模型排除了协变量缺失者，尽管缺失率很低。",
     "第八，主模型排除了协变量缺失者，尽管缺失率很低。第九，本研究未按性别、年龄或其他社会人口学亚组考察模型表现或表型患病率，也未开展公平性分析；由于两个数据库在医疗体系、记录习惯与病例构成上均有差异，亚组的可迁移性仍属未验证。"),
]
for p,a,b in pairs:
    t=io.open(p,encoding='utf-8').read()
    if a in t:
        io.open(p,'w',encoding='utf-8').write(t.replace(a,b,1)); print('OK', p.split('/')[-1])
    else:
        print('MISS', p.split('/')[-1], a[:50])
