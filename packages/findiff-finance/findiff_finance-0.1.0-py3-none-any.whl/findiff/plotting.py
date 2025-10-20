# src/findiff/plotting.py
from __future__ import annotations
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def plot_cv_sharpe_bars(cv_folds: List[Dict[str, float]]):
    """
    传入 pipeline.logs['cv']['folds']
    """
    xs, ys = [], []
    for i, fm in enumerate(cv_folds, 1):
        # 找该折唯一的 sharpe key
        k = [k for k in fm.keys() if k.endswith("_sharpe")]
        if not k: continue
        xs.append(f"cv{i}")
        ys.append(fm[k[0]])
    if not ys:
        return
    plt.figure()
    plt.bar(xs, ys)
    plt.title("CV Sharpe per fold")
    plt.xlabel("Fold")
    plt.ylabel("Sharpe")
    plt.tight_layout()

def plot_test_nav_from_returns(ret: np.ndarray):
    """
    给定 test 段日度策略收益，画 NAV 曲线。
    """
    r = np.asarray(ret, float)
    r = r[~np.isnan(r)]
    if r.size == 0: return
    nav = np.cumprod(1.0 + r)
    plt.figure()
    plt.plot(nav)
    plt.title("Test NAV")
    plt.xlabel("Time")
    plt.ylabel("NAV")
    plt.tight_layout()

def compare_feature_hist(real_df: pd.DataFrame, synth_df: pd.DataFrame, feature_cols: List[str], max_cols: int = 6):
    """
    选前 max_cols 个特征，画真实 vs 合成的直方图对比（每行 3 个）。
    """
    feats = feature_cols[:max_cols]
    n = len(feats)
    if n == 0: return
    rows = int(np.ceil(n / 3))
    plt.figure(figsize=(9, 3*rows))
    for i, f in enumerate(feats, 1):
        plt.subplot(rows, 3, i)
        real = real_df[f].dropna().values
        syn  = synth_df[f].dropna().values
        if len(real) == 0 or len(syn) == 0: continue
        plt.hist(real, bins=30, alpha=0.5, label="real", density=True)
        plt.hist(syn,  bins=30, alpha=0.5, label="synth", density=True)
        plt.title(f)
        plt.legend()
    plt.tight_layout()

def psi(a: np.ndarray, b: np.ndarray, bins: int = 20) -> float:
    hist_a, edges = np.histogram(a[~np.isnan(a)], bins=bins)
    hist_b, _ = np.histogram(b[~np.isnan(b)], bins=edges)
    pa = hist_a / max(hist_a.sum(), 1)
    pb = hist_b / max(hist_b.sum(), 1)
    pa = np.clip(pa, 1e-6, None); pb = np.clip(pb, 1e-6, None)
    return float(np.sum((pa - pb) * np.log(pa / pb)))

def plot_psi_heatmap(real_df: pd.DataFrame, synth_df: pd.DataFrame, feature_cols: List[str], bins: int = 20):
    """
    计算每个特征的 PSI 并绘制热图（条形图）。
    """
    vals = []
    cols = []
    for f in feature_cols:
        a = real_df[f].values; b = synth_df[f].values
        if np.all(np.isnan(a)) or np.all(np.isnan(b)): continue
        cols.append(f); vals.append(psi(a, b, bins=bins))
    if not vals: return
    order = np.argsort(vals)[::-1]
    cols = [cols[i] for i in order]; vals = [vals[i] for i in order]
    plt.figure(figsize=(8, max(2, len(cols)*0.3)))
    plt.barh(cols, vals)
    plt.title("PSI (synth vs real)")
    plt.xlabel("PSI")
    plt.tight_layout()