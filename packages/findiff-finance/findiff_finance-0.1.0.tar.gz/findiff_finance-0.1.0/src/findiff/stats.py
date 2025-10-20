# src/findiff/stats.py
from __future__ import annotations
from typing import Dict, Tuple
import numpy as np

def newey_west_for_mean(ret: np.ndarray, lags: int = 5) -> Tuple[float, float]:
    """
    返回 (mean, NW标准误). 以 Bartlett 权重估计 HAC 方差。
    """
    r = np.asarray(ret, float)
    r = r[~np.isnan(r)]
    n = len(r)
    if n == 0:
        return np.nan, np.nan
    mu = np.mean(r)
    x = r - mu
    # 自协方差（非偏）
    gamma0 = np.dot(x, x) / n
    var_hat = gamma0
    L = min(lags, n - 1)
    for j in range(1, L + 1):
        cov = np.dot(x[j:], x[:-j]) / n
        w = 1.0 - j / (L + 1.0)
        var_hat += 2.0 * w * cov
    se = np.sqrt(var_hat / n) if var_hat > 0 else np.nan
    return mu, se

def nw_tstat_mean(ret: np.ndarray, lags: int = 5, ann: int = 252) -> Dict[str, float]:
    """
    对“均值收益”为零的假设做 NW t 检验；同时返回年化 Sharpe 估计（便于对照）。
    """
    r = np.asarray(ret, float)
    r = r[~np.isnan(r)]
    if len(r) == 0:
        return {"mean": np.nan, "se": np.nan, "t": np.nan, "sharpe": np.nan}
    mu, se = newey_west_for_mean(r, lags=lags)
    t = (mu / se) if (se is not None and se > 0) else np.nan
    sd = np.std(r, ddof=1)
    sharpe = (mu / sd * np.sqrt(ann)) if sd > 0 else np.nan
    return {"mean": float(mu), "se": float(se) if se is not None else np.nan,
            "t": float(t), "sharpe": float(sharpe)}

def moving_block_bootstrap_ci(ret: np.ndarray, block: int = 20, reps: int = 1000, ann: int = 252) -> Dict[str, Tuple[float, float]]:
    """
    移动区块自助法（MBB）对均值与年化 Sharpe 给出 95% CI。
    """
    r = np.asarray(ret, float)
    r = r[~np.isnan(r)]
    n = len(r)
    if n == 0:
        return {"mean_ci": (np.nan, np.nan), "sharpe_ci": (np.nan, np.nan)}
    if block <= 0: block = 1
    K = int(np.ceil(n / block))
    means, sharpes = [], []
    for _ in range(reps):
        idx = []
        for _k in range(K):
            s = np.random.randint(0, max(1, n - block + 1))
            idx.extend(range(s, min(s + block, n)))
        idx = idx[:n]
        sample = r[idx]
        m = np.mean(sample)
        sd = np.std(sample, ddof=1)
        sh = (m / sd * np.sqrt(ann)) if sd > 0 else np.nan
        means.append(m); sharpes.append(sh)
    lo_m, hi_m = np.nanpercentile(means, [2.5, 97.5])
    lo_s, hi_s = np.nanpercentile(sharpes, [2.5, 97.5])
    return {"mean_ci": (float(lo_m), float(hi_m)), "sharpe_ci": (float(lo_s), float(hi_s))}