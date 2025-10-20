# src/findiff/metrics.py
from __future__ import annotations
from typing import Dict, List
import numpy as np

def _nan_guard(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float).reshape(-1)
    return x[~np.isnan(x)]

def _ann_mean(ret: np.ndarray, ann: int) -> float:
    return float(np.nanmean(ret) * ann)

def _ann_vol(ret: np.ndarray, ann: int) -> float:
    dstd = float(np.nanstd(ret, ddof=1))
    return dstd * np.sqrt(ann) if dstd > 0 else np.nan

def _max_drawdown(ret: np.ndarray) -> float:
    if ret.size == 0:
        return np.nan
    nav = np.cumprod(1.0 + ret)
    peak = np.maximum.accumulate(nav)
    dd = (nav - peak) / peak
    return float(-np.nanmin(dd))  # 正数

def _calmar(ret: np.ndarray, ann: int) -> float:
    ann_ret = _ann_mean(ret, ann)
    mdd = _max_drawdown(ret)
    if mdd is None or np.isnan(mdd) or mdd == 0:
        return np.nan
    return float(ann_ret / mdd)

def compute_eval_metrics(ret: np.ndarray,
                         eval_names: List[str],
                         ann: int = 252,
                         prefix: str = "") -> Dict[str, float]:
    """
    支持的指标：sharpe, calmar, vol, var, sharpe_p5
    ret: 日度策略收益序列（方向类预测时= yhat * y）
    """
    out: Dict[str, float] = {}
    r = _nan_guard(ret)
    if r.size == 0:
        return {f"{prefix}{name}": np.nan for name in eval_names}

    mu = float(np.nanmean(r))
    dstd = float(np.nanstd(r, ddof=1))
    var = float(np.nanvar(r, ddof=1))

    for name in eval_names:
        key = f"{prefix}{name}"
        if name == "sharpe":
            out[key] = (mu / dstd * np.sqrt(ann)) if dstd > 0 else np.nan
        elif name == "calmar":
            out[key] = _calmar(r, ann)
        elif name == "vol":
            out[key] = dstd
        elif name == "var":
            out[key] = var
        elif name == "sharpe_p5":
            p5 = float(np.nanpercentile(r, 5))
            denom = abs(p5)
            out[key] = (mu / denom * np.sqrt(ann)) if denom > 1e-12 else np.nan
        else:
            continue
    return out