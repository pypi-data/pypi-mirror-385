# src/findiff/config.py
from __future__ import annotations
from typing import Any, Dict, Tuple, Union
import pandas as pd
import numpy as np

SplitTuple = Tuple[Union[int, float, str, pd.Timestamp], Union[int, float, str, pd.Timestamp]]

def default_cfg() -> Dict[str, Any]:
    """
    项目全局默认配置（可以被 deep_update 覆盖）。
    """
    return {
        "data": {
            # 例：
            # "split": {"train": (min, q80), "val": (q80+1, q80), "test": (q80+1, max)}
            # 这里的 min/max/qXX 会在 get_splits 里解析
            "split": {"train": ("min", "q80"), "val": ("q80", "q80"), "test": ("q80", "max")},
            "freq": "D",
        },
        "conditions": {
            "enable": True,
            "fields": ["trend", "vol_level"],
            "builders": {
                # 按需在调用处替换 label_name
                "trend": {"window": 63, "label_name": "label"},
                "vol_level": {"window": 21, "label_name": "label", "quantiles": [0.33, 0.67]},
            },
        },
        "generator": {
            "epochs": 8, "steps": 600, "edit_last_steps": 80, "guidance_scale": 1.3,
            "n_samples": None, "sample_ratio": {"normal": 0.30},
            "cond_drop_p": 0.2, "batch_size": 512, "lr": 1e-3,
        },
        "teacher": {
            "scores": ["ic", "proxy_sharpe", "max_dd"],
            "select_rule": {"k_top": 0.15, "thresholds": {"ic": 0.0}},
            "portfolio": {"top_frac": 0.2, "cost_bps": 10, "ann_factor": 252},
        },
        "mix": {"real_to_synth": "1.0:0.2"},
        "train": {
            "params": {"epochs": 20, "batch_size": 512, "lr": 8e-4},
            "ann_factor": 252,
            "eval_metrics": ["sharpe", "calmar", "sharpe_p5", "vol", "var"],
            "cv": {
                "enable": True,
                "region": "train",               # "train" | "val"
                "scheme": "sliding",             # "expanding" | "sliding"
                "train_window": 756,             # sliding 必填
                "n_folds": 5,
                "embargo": 96,
                "min_train_rows": 96,
                # "model_builder": callable
            },
        },
        "safety": {"leakage_check": True},
        "security": {
            "auto_gate_synth": True,
            "gate_if": {"ic": 0.0, "proxy_sharpe": 0.0},
            "fallback_mix": "1.0:0.0",
            "eval_gate": True,
            "accept_if": {
                "cv_sharpe_mean_min": 0.0,
                "test_sharpe_delta_min": 0.0,
                "test_p5_delta_min": 0.0,
            },
        },
    }

def deep_update(base: Dict[str, Any], extra: Dict[str, Any]) -> Dict[str, Any]:
    """
    递归覆盖更新：字典合并；列表/标量用 extra 覆盖 base。
    """
    if extra is None:
        return base
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            base[k] = deep_update(base[k], v)
        else:
            base[k] = v
    return base

def _parse_bound(val, series: pd.Series):
    """
    支持:
    - 'min' / 'max'
    - 'q80' / 'q20'（分位数）
    - 时间戳字符串（若列为 datetime）
    - 直接数值/时间戳
    """
    if isinstance(val, str):
        v = val.strip().lower()
        if v == "min":
            return series.min()
        if v == "max":
            return series.max()
        if v.startswith("q"):
            q = float(v[1:]) / 100.0
            return series.quantile(q)
        # 尝试解析日期字符串
        try:
            ts = pd.to_datetime(v)
            # 若原列不是 datetime，返回对应的整数位置近似
            if np.issubdtype(series.dtype, np.datetime64):
                return ts
            # 否则返回最接近的值
            return series.iloc[(series - series.median()).abs().argsort()].iloc[0]
        except Exception:
            return val
    return val

def get_splits(df: pd.DataFrame, time_col: str, split_cfg: Dict[str, SplitTuple]):
    """
    train = [tr_lo, tr_hi]
    val   = (max(tr_hi, va_lo), va_hi]   # 尊重 val_lo，同时不与 train 重叠
    test  = (max(tr_hi, va_hi, te_lo), te_hi]
    """
    ser = df[time_col]

    def bounds(pair):
        if pair is None: return (None, None)
        lo, hi = pair
        return _parse_bound(lo, ser), _parse_bound(hi, ser)

    tr_lo, tr_hi = bounds(split_cfg.get("train"))
    va_lo, va_hi = bounds(split_cfg.get("val"))
    te_lo, te_hi = bounds(split_cfg.get("test"))

    # train
    m_tr = (ser >= tr_lo) & (ser <= tr_hi) if (tr_lo is not None and tr_hi is not None) else ser < -1
    tr = df.loc[m_tr].copy()

    # val：起点 = max(tr_hi, va_lo)
    if va_lo is not None and va_hi is not None:
        va_start = max(tr_hi, va_lo)
        m_va = (ser > va_start) & (ser <= va_hi)
        va = df.loc[m_va].copy()
    else:
        va = df.iloc[0:0].copy()

    # test：起点 = max(tr_hi, va_hi(若有), te_lo(若有))
    prev_end = tr_hi
    if va_lo is not None and va_hi is not None:
        prev_end = max(prev_end, va_hi)
    if te_lo is not None:
        prev_end = max(prev_end, te_lo)
    if te_lo is not None and te_hi is not None:
        m_te = (ser > prev_end) & (ser <= te_hi)
        test = df.loc[m_te].copy()
    else:
        test = df.iloc[0:0].copy()

    return tr, va, test