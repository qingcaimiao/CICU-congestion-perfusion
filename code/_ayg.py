# -*- coding: utf-8 -*-
"""anchor_year_group 的唯一权威来源（era / temporal-validation helper）

为什么要这个模块
----------------
早期版本的 analyze_cp2.py 用 stay_id -> anchor_year_group 的映射取自
``T2_data/mimic_T2.parquet``。那是**另一个课题的队列文件**（15,699 例），
与本研究的 12,052 例只有 9,715 例 stay_id 重叠。于是 2,337 例本队列患者
被误判为"数据库中无年代标注"，一度写进稿件（"temporal validation in 9,715
dated stays, excluding 2,337 undated stays with 14.7% mortality"）。

事实上 ``hosp/patients.csv`` 的 ``anchor_year_group`` 对全部 364,627 名患者
**零缺失**。正确做法是按 subject_id 关联 patients.csv，而不是拿另一个队列的
stay_id 清单去 map。

核对口径（2026-10-28 重算）
---------------------------
- 旧实现（mimic_T2.parquet）：覆盖 9,715 / 12,052，缺失 2,337，AUROC 0.851
- 本实现（patients.csv）：覆盖 12,052 / 12,052，缺失 0，AUROC 0.867
  训练（<= 2011 - 2013）4,778 例 / 死亡 277；测试 7,274 例 / 死亡 481

若表中没有 subject_id，先用 icustays.csv 补：
    stay_id -> subject_id  （mimiciv_icu.icustays）
"""
import duckdb
import pandas as pd

PATIENTS_CSV = 'D:/shujuku/mimic-iv-3.1/hosp/patients.csv'
ICUSTAYS_CSV = 'D:/shujuku/mimic-iv-3.1/icu/icustays.csv'
ERA_CUT = '2011 - 2013'


def _read_patients(con=None, patients_csv=PATIENTS_CSV):
    c = con or duckdb.connect()
    pat = c.execute(
        f"SELECT subject_id, anchor_year_group FROM read_csv_auto('{patients_csv}')"
    ).df()
    assert len(pat) == pat.subject_id.nunique(), 'patients.csv: subject_id 不唯一'
    assert pat.anchor_year_group.notna().all(), 'patients.csv: anchor_year_group 出现缺失'
    return pat


def add_subject_id(df, con=None, icustays_csv=ICUSTAYS_CSV):
    """给只有 stay_id 的表补 subject_id（一对一，带唯一性断言）。"""
    if 'subject_id' in df.columns:
        return df
    assert 'stay_id' in df.columns, '既无 subject_id 也无 stay_id，无法建立映射'
    c = con or duckdb.connect()
    mp = c.execute(
        f"SELECT stay_id, subject_id FROM read_csv_auto('{icustays_csv}')"
    ).df()
    assert len(mp) == mp.stay_id.nunique(), 'icustays.csv: stay_id 不唯一'
    out = df.merge(mp, on='stay_id', how='left')
    assert len(out) == len(df), 'merge 改变了行数'
    assert out.subject_id.notna().all(), '部分 stay_id 在 icustays.csv 中查不到'
    return out


def attach_ayg(df, con=None, patients_csv=PATIENTS_CSV, require_full=True):
    """按 subject_id 挂 anchor_year_group，列名统一为 ayg。

    require_full=True 时断言零缺失——主语料库不该有缺失；
    敏感性分析若确实允许缺失，可置 False 并自行报告。
    """
    df = add_subject_id(df, con=con)
    pat = _read_patients(con=con, patients_csv=patients_csv)
    out = df.drop(columns=['ayg'], errors='ignore').merge(
        pat.rename(columns={'anchor_year_group': 'ayg'}), on='subject_id', how='left')
    assert len(out) == len(df), 'merge 改变了行数（subject_id 疑似重复）'
    if require_full:
        assert out.ayg.notna().all(), (
            '仍存在无年代的记录：%d 条。请确认传入的是本队列，且 patients.csv 完整。'
            % int(out.ayg.isna().sum()))
    return out


def split_era(df, cut=ERA_CUT):
    """早段训练 / 晚段测试（按 anchor_year_group 字符串可比序）。"""
    assert 'ayg' in df.columns, '请先调用 attach_ayg()'
    tr = df[df.ayg <= cut].copy()
    te = df[df.ayg > cut].copy()
    assert len(tr) + len(te) + df.ayg.isna().sum() == len(df), '时代切分未覆盖全部行'
    return tr, te


if __name__ == '__main__':
    # 自检：以已落盘的分析集复现时间验证的样本量
    d = pd.read_parquet('D:/桌面/workbuddyzuopin/CPxiangmu/03_结果/cp_analysis_set.parquet')
    d = attach_ayg(d)
    tr, te = split_era(d)
    print('分析集 %d，零缺失；训练 %d（死亡 %d）/ 测试 %d（死亡 %d）' % (
        len(d), len(tr), tr.died.sum(), len(te), te.died.sum()))
    print(d.groupby('ayg').agg(n=('died', 'size'), 死亡=('died', 'sum'),
                             死亡率=('died', lambda s: round(100 * s.mean(), 2))).to_string())
