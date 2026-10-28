# -*- coding: utf-8 -*-
"""生成 JCM 投稿所需：STROBE 流程图（Fig 1）、图文摘要（Graphical Abstract）、图号重排"""
import duckdb, os, shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import numpy as np

plt.rcParams['font.family'] = 'Arial'
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['svg.fonttype'] = 'none'

D = 'D:/workbuddygongzuokongjian/2026-10-11-13-20-58/T2_data'
OUT = 'D:/桌面/workbuddyzuopin/CPxiangmu/04_图'
JCM = 'D:/桌面/workbuddyzuopin/CPxiangmu/02_投稿包_JCM'
os.makedirs(JCM, exist_ok=True)

c = duckdb.connect(); c.execute('PRAGMA threads=8')

# ---------------- 精确流程数字 ----------------
print('=== MIMIC-IV flow ===')
n_total = c.execute("SELECT count(*) FROM read_csv_auto('D:/shujuku/mimic-iv-3.1/icu/icustays.csv',header=true,strict_mode=false,ignore_errors=true)").fetchone()[0]
print('ICU stays total          :', n_total)
n_card = c.execute("""SELECT count(*) FROM read_csv_auto('D:/shujuku/mimic-iv-3.1/icu/icustays.csv',header=true,strict_mode=false,ignore_errors=true)
  WHERE lower(first_careunit) LIKE '%cvicu%' OR lower(first_careunit) LIKE '%ccu%'""").fetchone()[0]
print('cardiac-unit ICU stays   :', n_card)
c.execute(f"CREATE OR REPLACE TABLE ic AS SELECT stay_id, subject_id, first_careunit, intime, row_number() OVER (PARTITION BY subject_id ORDER BY intime) rn FROM read_csv_auto('D:/shujuku/mimic-iv-3.1/icu/icustays.csv',header=true,strict_mode=false,ignore_errors=true) WHERE lower(first_careunit) LIKE '%cvicu%' OR lower(first_careunit) LIKE '%ccu%'")
n_first = c.execute("SELECT count(*) FROM ic WHERE rn=1").fetchone()[0]
print('first cardiac stay       :', n_first, ' excluded repeats:', n_card-n_first)
print('  by unit:', c.execute("SELECT first_careunit, count(*) FROM ic WHERE rn=1 GROUP BY 1").fetchall())

mm = c.execute(f"SELECT * FROM read_parquet('{D}/cp_core.parquet')").df() if False else None
c.execute(f"CREATE OR REPLACE TABLE ex AS SELECT stay_id, itemid, off_h FROM read_parquet('{D}/cp_exam_raw.parquet')")
c.execute("CREATE OR REPLACE TABLE coh AS SELECT stay_id FROM ic WHERE rn=1")
n_oed = c.execute("SELECT count(DISTINCT e.stay_id) FROM ex e JOIN coh ON e.stay_id=coh.stay_id WHERE e.itemid=224862 AND e.off_h>=-6 AND e.off_h<=24").fetchone()[0]
n_crt = c.execute("SELECT count(DISTINCT e.stay_id) FROM ex e JOIN coh ON e.stay_id=coh.stay_id WHERE e.itemid IN (223951,224308) AND e.off_h>=-6 AND e.off_h<=24").fetchone()[0]
n_both = c.execute("""SELECT count(*) FROM (
  SELECT e.stay_id FROM ex e JOIN coh ON e.stay_id=coh.stay_id
  WHERE e.off_h>=-6 AND e.off_h<=24 GROUP BY e.stay_id
  HAVING max(CASE WHEN e.itemid=224862 THEN 1 ELSE 0 END)=1
     AND max(CASE WHEN e.itemid IN (223951,224308) THEN 1 ELSE 0 END)=1)""").fetchone()[0]
print('oedema documented window :', n_oed, '(%.1f%%)' % (100*n_oed/n_first))
print('CRT documented window    :', n_crt, '(%.1f%%)' % (100*n_crt/n_first))
print('both documented          :', n_both, '(%.1f%%)' % (100*n_both/n_first))
print('excluded no oedema       :', n_first-n_oed)
print('excluded oedema but no CRT:', n_oed-n_both)

M1, M2, M3, M4 = n_total, n_card, n_first, n_both
M_ex_rep = n_card - n_first
M_ex_oed = n_first - n_oed
M_ex_crt = n_oed - n_both

print()
print('=== eICU-CRD flow ===')
E = 'D:/shujuku/EICU 2.0'
def Rr(p): return "read_csv_auto('%s',header=true,strict_mode=false,ignore_errors=true)" % p
e_tot = c.execute("SELECT count(*) FROM %s" % Rr(E+'/patient.csv')).fetchone()[0]
print('unit stays total         :', e_tot)
c.execute("CREATE OR REPLACE TABLE ec AS SELECT patientunitstayid, unittype, unitdischargeoffset FROM %s WHERE unittype IN ('Cardiac ICU','CCU-CTICU')" % Rr(E+'/patient.csv'))
e_card = c.execute("SELECT count(*) FROM ec").fetchone()[0]
print('cardiac ICU stays        :', e_card)
print('  by unittype:', c.execute("SELECT unittype, count(*) FROM ec GROUP BY 1").fetchall())
ecp = c.execute(f"SELECT * FROM read_parquet('{D}/eicu_cp.parquet')").df()
print('eicu_cp rows             :', len(ecp))
sub = ecp[(ecp[['edema_doc','jvd_doc','lungs_doc']].fillna(0).sum(axis=1) > 0) & (ecp.perf_doc.fillna(0) == 1)]
print('congestion & perfusion   :', len(sub), ' deaths:', int(sub.died.sum()) if 'died' in sub else 'n/a')
print('deaths among cardiac ICU :', int(ecp.died.sum()) if 'died' in ecp else 'n/a')
E1, E2, E3 = e_tot, e_card, len(sub)
E4 = int(sub.died.sum())

# ---------------- Fig 1: STROBE 流程图 ----------------
INK = '#2C2C2A'; MUT = '#5F5E5A'; LINE = '#888780'
DEV_F = '#E6F1FB'; DEV_S = '#185FA5'
REP_F = '#E1F5EE'; REP_S = '#0F6E56'
EXC_F = '#FCEBEB'; EXC_S = '#A32D2D'

fig, ax = plt.subplots(figsize=(11.5, 8.2), dpi=300)
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')

def box(x, y, w, h, txt, fc, ec, fs=8.0, bold_first=True, lw=1.1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.35,rounding_size=0.8',
                                linewidth=lw, edgecolor=ec, facecolor=fc, mutation_aspect=1))
    lines = txt.split('\n')
    n = len(lines)
    for i, ln in enumerate(lines):
        yy = y + h/2 + (n-1)*1.35 - i*2.7
        ax.text(x + w/2, yy, ln, ha='center', va='center', fontsize=fs,
                color=INK, fontweight=('bold' if (i == 0 and bold_first) else 'normal'))

def arrow(x1, y1, x2, y2, style='-|>', lw=1.1, color=LINE, ls='-'):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=11,
                                 linewidth=lw, color=color, linestyle=ls,
                                 shrinkA=0, shrinkB=0))

# 横向布局（互不重叠）：左列 8..33 | 排除框 34..50 | 分隔虚线 50.8 | 右列 59..95
LC = 19          # 左列中心
RC = 77            # 右列中心

ax.text(LC, 97.5, 'Development cohort (MIMIC-IV v3.1)', ha='center', fontsize=10.5, color=DEV_S, fontweight='bold')
ax.text(RC, 97.5, 'Replication cohort (eICU-CRD v2.0)', ha='center', fontsize=10.5, color=REP_S, fontweight='bold')

# --- left column ---
box(8, 87, 22, 8, 'All ICU stays\nn = %s' % format(M1, ','), 'white', LINE, fs=7.6)
arrow(LC, 87, LC, 83.5)
box(8, 75, 22, 8, 'ICU stays in a cardiac unit\nCVICU %s; CCU %s\nn = %s' % (format(14771, ','), format(10775, ','), format(M2, ',')), DEV_F, DEV_S, fs=7.4)
arrow(LC, 75, LC, 71.5)
box(33.5, 70.5, 16, 8.5, 'Excluded: repeat cardiac ICU\nadmission in the same patient\nn = %s' % format(M_ex_rep, ','), EXC_F, EXC_S, fs=6.8, bold_first=False)
arrow(30.3, 74.75, 33.3, 74.75, color=EXC_S)
box(8, 60, 22, 10, 'First cardiac ICU stay\nper patient\nn = %s\nin-hospital deaths 1,575 (7.6%%)' % format(M3, ','), DEV_F, DEV_S, fs=7.4)
arrow(LC, 60, LC, 56.5)
box(33.5, 55, 16, 8.5, 'Excluded: oedema grade\nnot charted in window\n−6 h to +24 h  |  n = %s' % format(M_ex_oed, ','), EXC_F, EXC_S, fs=6.8, bold_first=False)
arrow(30.3, 59.25, 33.3, 59.25, color=EXC_S)
box(8, 44.5, 22, 10, 'Oedema grade documented\nn = %s (69.1%%)' % format(n_oed, ','), DEV_F, DEV_S, fs=7.4)
arrow(LC, 44.5, LC, 41)
box(33.5, 39.5, 16, 8.5, 'Excluded: capillary refill\nnot charted in window\nn = %s' % format(M_ex_crt, ','), EXC_F, EXC_S, fs=6.8, bold_first=False)
arrow(30.3, 43.75, 33.3, 43.75, color=EXC_S)
box(8, 28, 22, 11, 'Primary analysis set\nn = %s (57.9%%)\ndeaths 758 (6.29%%)' % format(M4, ','), '#E6F1FB', DEV_S, fs=8.0)

# --- right column ---
box(59, 87, 36, 8, 'All unit stays\nn = %s  |  208 hospitals' % format(E1, ','), 'white', LINE, fs=7.8)
arrow(RC, 87, RC, 83.5)
box(59, 73, 36, 9, 'Cardiac ICU stays\nCardiac ICU %s; CCU-CTICU %s\nn = %s  |  in-hospital deaths 2,666 (9.6%%)' % (format(12467, ','), format(15290, ','), format(E2, ',')), REP_F, REP_S, fs=7.6)
arrow(RC, 73, RC, 69.5)
box(59, 59, 36, 9, 'Congestion (any of three signs)\nand perfusion documented\nn = %s  |  deaths %d' % (format(E3, ','), E4), REP_F, REP_S, fs=7.6)
arrow(RC, 59, RC, 55.5)
box(59, 44.5, 36, 10, 'Replication analysis set\nn = %s  |  deaths %d (%.1f%%)' % (format(E3, ','), E4, 100*E4/E3), '#E1F5EE', REP_S, fs=8.2)
box(59, 31, 36, 11, 'Perfusion axis replicated\n6.25% vs 33.96%\nExternal AUROC 0.835', REP_F, REP_S, fs=7.6, bold_first=False)

ax.plot([50.8, 50.8], [24, 94], color='#D3D1C7', lw=0.9, ls=(0, (4, 3)))
ax.text(4, 4, 'Window for exposure ascertainment: 6 h before to 24 h after ICU admission. Outcome: in-hospital death over the entire hospitalisation.\n'
              'Reporting follows the STROBE statement for cohort studies and TRIPOD+AI for the prediction-model components.',
        ha='left', fontsize=7.2, color=MUT)
plt.tight_layout()
plt.savefig(OUT + '/Fig1_participant_flow.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print('\nsaved Fig1_participant_flow.png')

# ---------------- Graphical Abstract ----------------
fig = plt.figure(figsize=(8.67, 5.0), dpi=300)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
ax.add_patch(Rectangle((0, 0), 100, 100, facecolor='white', edgecolor='none'))

ax.text(50, 95.5, 'Routinely charted bedside signs in the cardiac ICU: the perfusion axis transports, the congestion axis does not',
        ha='center', fontsize=11.5, color=INK, fontweight='bold')
ax.plot([4, 96], [91.5, 91.5], color='#D3D1D7', lw=1.2)

# Zone A
ax.text(15.5, 86, '1. Two signs already charted every shift', ha='center', fontsize=8.6, color=DEV_S, fontweight='bold')
ax.add_patch(FancyBboxPatch((2.5, 63), 26, 19, boxstyle='round,pad=0.5,rounding_size=1.2', linewidth=1.1, edgecolor=DEV_S, facecolor=DEV_F))
ax.text(15.5, 78.5, 'Oedema depth (nursing item)', ha='center', fontsize=7.6, color=INK)
ax.text(15.5, 74.8, 'none → 2 → 4 → 6 → 8 mm → anasarca', ha='center', fontsize=7.0, color=MUT)
ax.text(15.5, 70.3, 'Capillary refill time', ha='center', fontsize=7.6, color=INK)
ax.text(15.5, 66.6, 'normal (<3 s) vs prolonged (>3 s)', ha='center', fontsize=7.0, color=MUT)

# Zone B : 2x2
ax.text(50, 86, '2. Four phenotypes, 7-fold mortality gradient', ha='center', fontsize=8.6, color=INK, fontweight='bold')
cells = [('Dry-warm', '4.10%', 31.5, 71.5, '#FCEBEB', INK),
         ('Wet-warm', '8.19%', 50.0, 71.5, '#F7C1C1', INK),
         ('Dry-cold', '20.94%', 31.5, 63.0, '#F09595', INK),
         ('Wet-cold', '29.92%', 50.0, 63.0, '#E24B4A', 'white')]
for nm, val, x, y, fc, tc in cells:
    ax.add_patch(FancyBboxPatch((x, y), 17.6, 7.8, boxstyle='round,pad=0.3,rounding_size=1.0', linewidth=1.0, edgecolor='#A32D2D', facecolor=fc))
    ax.text(x + 8.8, y + 5.2, nm, ha='center', fontsize=7.8, color=tc, fontweight='bold')
    ax.text(x + 8.8, y + 2.1, val, ha='center', fontsize=9.2, color=tc)
ax.text(40.2, 81.0, 'congested →', ha='center', fontsize=7.0, color=MUT)
ax.text(27.5, 67.3, 'perfused', ha='center', fontsize=7.0, color=MUT, rotation=90)
ax.text(70.4, 67.3, 'hypoperfused', ha='center', fontsize=7.0, color=MUT, rotation=90)
ax.text(50, 58.5, 'MIMIC-IV, n = 12,052  |  deaths 758', ha='center', fontsize=7.4, color=MUT)

# Zone C
ax.text(84, 86, '3. What travels?', ha='center', fontsize=8.6, color=REP_S, fontweight='bold')
ax.add_patch(FancyBboxPatch((72.5, 63), 25, 19, boxstyle='round,pad=0.5,rounding_size=1.2', linewidth=1.1, edgecolor=REP_S, facecolor=REP_F))
ax.text(85, 78.6, 'eICU-CRD, 6 contributing centres', ha='center', fontsize=7.2, color=INK)
ax.text(85, 74.3, 'external AUROC 0.835', ha='center', fontsize=7.6, color=INK)
ax.text(85, 69.6, 'Perfusion axis: 6.25% → 33.96%', ha='center', fontsize=7.2, color='#0F6E56', fontweight='bold')
ax.text(85, 65.8, 'Congestion axis: did not replicate', ha='center', fontsize=7.2, color='#A32D2D', fontweight='bold')

# bottom band
ax.add_patch(FancyBboxPatch((2.5, 24), 95, 29, boxstyle='round,pad=0.6,rounding_size=1.2', linewidth=1.1, edgecolor=LINE, facecolor='#F1EFE8'))
ax.text(50, 47.5, 'Beyond 23 conventional variables', ha='center', fontsize=8.4, color=INK, fontweight='bold')
ax.text(50, 42.0, 'Perfusion alone  ΔAUROC +0.0101     Congestion alone  +0.0038     Both axes  +0.0126', ha='center', fontsize=8.2, color=INK)
ax.text(50, 36.4, 'AUROC 0.858 → 0.871      IDI +0.0209      categorical NRI +0.0539      temporal validation 0.867', ha='center', fontsize=7.8, color=MUT)
ax.text(50, 30.0, 'Highest (wet-cold) vs lowest (dry-warm) phenotype: 29.92% vs 4.10% in-hospital mortality', ha='center', fontsize=7.8, color=INK)

ax.text(50, 17.5, 'The perfusion sign transports across databases; the nurse-charted congestion measurement does not exist in the second database,',
        ha='center', fontsize=8.0, color=INK)
ax.text(50, 13.0, 'and alternative congestion signs did not reproduce the gradient — bedside congestion phenotypes are documentation-dependent.',
        ha='center', fontsize=8.0, color=INK)
ax.text(50, 5.5, 'MIMIC-IV v3.1 (development)  ·  eICU-CRD v2.0 (external replication)  ·  retrospectively documented, no additional cost',
        ha='center', fontsize=7.0, color=MUT)

plt.savefig(OUT + '/GraphicalAbstract.png', dpi=300, facecolor='white')
from PIL import Image
im = Image.open(OUT + '/GraphicalAbstract.png').convert('RGB')
im.save(JCM + '/Graphical_Abstract.tif', 'TIFF', compression='tiff_lzw', dpi=(300, 300))
print('saved GraphicalAbstract.png', im.size, '-> tif')

# 图号重排由 jcm_fig_renumber.py 单独执行（最终编号见该脚本 MAP），此处不再内嵌旧方案

