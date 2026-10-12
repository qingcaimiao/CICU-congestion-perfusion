# -*- coding: utf-8 -*-
p = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包/Manuscript_CongestionPerfusion_EN.md'
t = open(p, encoding='utf-8').read()

# ---- 1. 引言第三个缺口：纠正错误归因 + 整合 Hao ----
OLD = ('Third, dynamic "trajectory" phenotypes are themselves an active line of work in critical care: '
       'group-based trajectory modelling of cumulative fluid balance over the first 72 h in three ICU databases '
       'identified reproducible subphenotypes with markedly different 28-day mortality [27], and heart failure '
       'oedema-index trajectories measured by bioelectrical impedance in nurse-led clinics over six months predict '
       'outcome after discharge [14]. Neither addresses the *bedside-charted depth of pitting oedema* recorded every '
       'shift during an acute ICU admission: the fluid-balance approach is a derived cumulative quantity that requires '
       'complete intake\u2013output records, and the oedema-index work begins after discharge. Notably, the '
       'fluid-balance trajectory study also reports that in the replication cohort the relevant documentation was too '
       'sparse to classify trajectories at all, which is itself an argument for testing whether a simpler, universally '
       'charted sign can be used. Whether the shift-by-shift ordinal depth of pitting oedema defines informative '
       'short-window trajectories during the acute cardiac ICU admission \u2014 and whether such trajectories can be '
       'classified reproducibly \u2014 has not been examined.')

NEW = ('Third, dynamic "trajectory" phenotypes are themselves an active line of work in critical care. Group-based '
       'trajectory modelling of cumulative fluid balance over the first 72 h in three ICU databases identified '
       'reproducible subphenotypes with markedly different 28-day mortality [27], and a recent analysis, deposited with '
       'its analysis code, reports that the trajectory of *any peripheral oedema* over the first ICU week is '
       'independently associated with 28- and 90-day mortality in general critically ill adults, that the association is '
       'only partly mediated by fluid balance and appears confined to patients without sepsis, and \u2014 directly '
       'relevant here \u2014 that peripheral-site charting in eICU-CRD was too sparse to classify trajectories at all '
       '[28]. Oedema-index trajectories measured by bioelectrical impedance in nurse-led clinics over six months after '
       'heart failure discharge also predict outcome [14]. None of these addresses the *nurse-charted ordinal depth of '
       'pitting oedema* recorded every shift during an acute cardiac ICU admission: the fluid-balance approach is a '
       'cumulative quantity derived from complete intake\u2013output records; the peripheral-oedema trajectory analysis '
       'examined oedema in isolation, in a general ICU population and over the first week; and the oedema-index work '
       'begins after discharge. Whether the shift-by-shift depth of pitting oedema defines informative short-window '
       'trajectories when combined with peripheral perfusion in a cardiac ICU population \u2014 and whether such '
       'trajectories can be classified reproducibly in a second database \u2014 has not been examined.')

assert OLD in t, 'intro paragraph not found'
t = t.replace(OLD, NEW)

# ---- 2. 讨论：在 Liu 段之后补 Hao 对照 ----
OLD2 = ('Third, oedema trajectories and outcomes have been studied after heart failure hospitalisation using a '
        'bioimpedance-derived oedema index in nurse-led clinics over six months [14]. That work measured oedema '
        'repeatedly, quantitatively, and after discharge; ours uses the shift-by-shift ordinal bedside-charted pitting '
        'depth during the acute ICU admission, which is the form in which the information actually exists at the point '
        'of care, and covers an earlier part of the care pathway.')
NEW2 = OLD2 + (' A parallel analysis of MIMIC-IV and MIMIC-III CareVue, deposited as a data archive accompanying a '
        'manuscript submitted to Scientific Reports (not peer reviewed), similarly reports that the early trajectory of '
        'any peripheral oedema over the first ICU week was independently associated with 28- and 90-day mortality in '
        'general critically ill adults, that the association was only partly mediated by fluid balance and appeared '
        'confined to patients without sepsis, and that peripheral-site documentation in eICU-CRD was too sparse for '
        'trajectory classification [28]. Our analysis differs in the trajectory window (shifts within 0\u201324 h '
        'versus 24\u201372 h from ICU admission, rather than the first ICU week), in the population (an unselected '
        'cardiac ICU cohort rather than a general ICU cohort), and in the exposure definition (ordinal nurse-charted '
        'pitting depth combined with capillary refill time, rather than peripheral oedema analysed in isolation). The '
        'two analyses nonetheless converge on the same conclusion about the second database \u2014 that peripheral '
        'bedside documentation there is too sparse to support trajectory classification \u2014 which corroborates, '
        'rather than weakens, the documentation-dependence argument developed below.')
assert OLD2 in t, 'discussion paragraph not found'
t = t.replace(OLD2, NEW2)

# ---- 3. 局限：轨迹未复现处加 [28] 佐证 ----
OLD3 = 'so a trajectory phenotype could not be constructed there at all.'
NEW3 = 'so a trajectory phenotype could not be constructed there at all \u2014 a limitation independently reported for the same database by others [28].'
assert OLD3 in t, 'limitation sentence not found'
t = t.replace(OLD3, NEW3)

# ---- 4. 新增参考文献 28 ----
OLD4 = '27. Wang K, Xiong H, Zhu Y, Zhou Y, Kang Y. Distinct 72-hour fluid balance trajectories are associated with 28-day mortality in a multicenter cohort of sepsis patients. Sci Rep. 2026;16:15126. doi:10.1038/s41598-026-46063-2. PMID: 41888401'
NEW4 = OLD4 + ('\n28. Hao Y, Qin L, Zhang Q, Chen S, Li P, Wan J, Ye H. Peripheral edema trajectories as a dynamic bedside '
        'prognostic marker in critically ill adults: analysis code and aggregate results (v1.2.1) [Data set]. Zenodo. 2026. '
        'doi:10.5281/zenodo.22674523. Accompanying manuscript submitted to Scientific Reports (not peer reviewed)')
assert OLD4 in t, 'ref 27 not found'
t = t.replace(OLD4, NEW4)

open(p, 'w', encoding='utf-8').write(t)
print('EN edits applied. ref28:', '22674523' in t, '| c28 citations:', t.count('[28]'))
