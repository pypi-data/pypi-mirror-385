# src/findiff/reporting.py
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Optional, List
import math
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ---------- 小工具 ----------
def _fmt(x: Any, nd: int = 4) -> str:
    """安全数值格式化：None/非数值/非有限数返回 'nan'。"""
    if x is None:
        return "nan"
    try:
        xv = float(x)
    except Exception:
        return str(x)
    if not math.isfinite(xv):
        return "nan"
    return f"{xv:.{nd}f}"


def _ensure_dir(p: str | Path) -> Path:
    p = Path(p)
    p.mkdir(parents=True, exist_ok=True)
    return p


# ---------- 图表：CV 柱状、Test NAV、PSI 热力 ----------
def _plot_cv_bars(out_path: Path, logs: Dict[str, Any]) -> Optional[str]:
    folds = logs.get("cv", {}).get("folds", [])
    if not folds:
        # 生成一个空图防止上游断裂
        fig = plt.figure()
        plt.title("No CV folds")
        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        return str(out_path)

    # 收集每折的 Sharpe（若存在）
    sharpe_vals = []
    fold_ids = []
    for i, d in enumerate(folds, 1):
        # 取第一个 *_sharpe 键
        s = None
        for k, v in d.items():
            if k.endswith("_sharpe"):
                s = v
                break
        if s is not None:
            sharpe_vals.append(float(s))
            fold_ids.append(f"cv{i}")

    if not sharpe_vals:
        fig = plt.figure()
        plt.title("CV folds exist but no *_sharpe found")
        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        return str(out_path)

    fig = plt.figure()
    plt.bar(range(len(sharpe_vals)), sharpe_vals)
    plt.xticks(range(len(sharpe_vals)), fold_ids, rotation=0)
    plt.ylabel("Sharpe")
    plt.title("CV Sharpe per fold")
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return str(out_path)


def _plot_test_nav(out_path: Path, logs: Dict[str, Any]) -> Optional[str]:
    r = logs.get("cv", {}).get("test_returns", None)
    if r is None:
        r = logs.get("series", {}).get("test_returns", None)
    if r is None:
        # 占位空图
        fig = plt.figure()
        plt.title("No test returns")
        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        return str(out_path)

    r = np.asarray(r, dtype=float)
    nav = np.cumprod(1.0 + r) - 1.0
    fig = plt.figure()
    plt.plot(nav)
    plt.xlabel("t")
    plt.ylabel("NAV (cumprod-1)")
    plt.title("Test NAV")
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return str(out_path)


def _psi(p: np.ndarray, q: np.ndarray, eps: float = 1e-12) -> float:
    """简单 PSI 计算。"""
    p = p.astype(float)
    q = q.astype(float)
    p = p / (p.sum() + eps)
    q = q / (q.sum() + eps)
    return float(np.sum((p - q) * np.log((p + eps) / (q + eps))))


def _plot_psi_heat(out_path: Path, train_df: Optional[pd.DataFrame],
                   synth_df: Optional[pd.DataFrame], feature_cols: Optional[List[str]]) -> Optional[str]:
    fig = plt.figure()
    ax = fig.add_subplot(111)

    if train_df is None or synth_df is None or not feature_cols:
        ax.text(0.5, 0.5, "No feature data for PSI", ha="center", va="center")
        ax.set_axis_off()
        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        return str(out_path)

    feats = feature_cols
    psis = []
    for f in feats:
        t = np.asarray(pd.to_numeric(train_df[f], errors="coerce").dropna(), dtype=float)
        s = np.asarray(pd.to_numeric(synth_df[f], errors="coerce").dropna(), dtype=float)
        if t.size == 0 or s.size == 0:
            psis.append(np.nan)
            continue
        bins = np.quantile(t, np.linspace(0, 1, 11))
        bins = np.unique(bins)
        if bins.size < 3:
            # 回退到均匀 bins
            mn = np.nanmin(t); mx = np.nanmax(t)
            if not np.isfinite(mn) or not np.isfinite(mx) or mn == mx:
                psis.append(np.nan)
                continue
            bins = np.linspace(mn, mx, 11)

        p_hist, _ = np.histogram(t, bins=bins)
        q_hist, _ = np.histogram(s, bins=bins)
        psis.append(_psi(p_hist, q_hist))

    data = np.array(psis, dtype=float).reshape(-1, 1)
    im = ax.imshow(data, aspect="auto", interpolation="nearest")
    ax.set_yticks(range(len(feats)))
    ax.set_yticklabels(feats)
    ax.set_xticks([0])
    ax.set_xticklabels(["PSI"])
    fig.colorbar(im, ax=ax)
    ax.set_title("PSI Heatmap (train vs. synth)")
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return str(out_path)


def save_standard_plots(run_dir: str,
                        result_metrics: Dict[str, float],
                        logs: Dict[str, Any],
                        train_df: Optional[pd.DataFrame],
                        synth_df: Optional[pd.DataFrame],
                        feature_cols: Optional[List[str]]) -> Dict[str, str]:
    """
    生成标准图表并返回文件路径字典：
      - cv_bars: 每折 Sharpe 柱状
      - test_nav: 测试集 NAV 曲线
      - psi_heat: PSI 热力图
    """
    out = {}
    rd = _ensure_dir(run_dir)

    cv_path = rd / "cv_bars.png"
    nav_path = rd / "test_nav.png"
    psi_path = rd / "psi_heat.png"

    out["cv_bars"] = _plot_cv_bars(cv_path, logs)
    out["test_nav"] = _plot_test_nav(nav_path, logs)
    out["psi_heat"] = _plot_psi_heat(psi_path, train_df, synth_df, feature_cols)

    return out


def save_html_report(run_dir: str,
                     result_metrics: Dict[str, float],
                     logs: Dict[str, Any],
                     stats_block: Optional[Dict[str, Any]] = None,
                     figures: Optional[Dict[str, str]] = None) -> str:
    """
    生成一个 HTML 报告：关键指标 + Baseline vs Augmented 对比 + 图表。
    """
    run = Path(run_dir)
    run.mkdir(parents=True, exist_ok=True)
    html = run / "report.html"

    # --- 安全格式化 ---
    import math
    def _fmt(x, nd=4):
        try:
            v = float(x)
        except Exception:
            return "nan" if x is None else str(x)
        return "nan" if not math.isfinite(v) else f"{v:.{nd}f}"

    sel = logs.get("selected_variant", "augmented")
    cv_s = result_metrics.get("cv_sharpe_mean")
    cv_v = result_metrics.get("cv_var_mean")
    ts   = result_metrics.get("test_sharpe")
    tv   = result_metrics.get("test_var")
    tp5  = result_metrics.get("test_sharpe_p5")
    tcal = result_metrics.get("test_calmar")

    sb  = stats_block or {}
    fig = figures or {}

    # --- 顶部关键指标表 ---
    rows = []
    rows.append(f"<tr><td>Selected Variant</td><td>{sel}</td></tr>")
    rows.append(f"<tr><td>CV Mean Sharpe</td><td>{_fmt(cv_s)}</td></tr>")
    rows.append(f"<tr><td>CV Mean Var</td><td>{_fmt(cv_v)}</td></tr>")
    rows.append(f"<tr><td>Test Sharpe</td><td>{_fmt(ts)}</td></tr>")
    rows.append(f"<tr><td>Test Var</td><td>{_fmt(tv)}</td></tr>")
    rows.append(f"<tr><td>Test Sharpe p5</td><td>{_fmt(tp5)}</td></tr>")
    rows.append(f"<tr><td>Test Calmar</td><td>{_fmt(tcal)}</td></tr>")

    # --- Baseline vs Augmented 对比表（若两者都存在） ---
    cmp_html = ""
    base = logs.get("baseline", {}).get("metrics")
    aug  = logs.get("augmented", {}).get("metrics")
    metric_keys = ["cv_sharpe_mean", "cv_var_mean", "test_sharpe", "test_var", "test_sharpe_p5", "test_calmar"]
    if base and aug:
        cmp_rows = []
        for k in metric_keys:
            b = base.get(k)
            a = aug.get(k)
            d = None
            try:
                if (b is not None) and (a is not None):
                    d = float(a) - float(b)
            except Exception:
                d = None
            mark = "← selected" if ((sel == "baseline" and k in base) or (sel == "augmented" and k in aug)) else ""
            cmp_rows.append(
                f"<tr><td>{k}</td><td>{_fmt(b)}</td><td>{_fmt(a)}</td><td>{_fmt(d)}</td></tr>"
            )
        cmp_html = f"""
        <h3>Baseline vs Augmented</h3>
        <table>
          <thead><tr><th>Metric</th><th>Baseline</th><th>Augmented</th><th>Δ (Aug - Base)</th></tr></thead>
          <tbody>
            {''.join(cmp_rows)}
          </tbody>
        </table>
        """
    elif base or aug:
        # 只有一侧可用也显示出来，避免空白
        single = base or aug
        label  = "Baseline" if base else "Augmented"
        cmp_rows = [f"<tr><td>{k}</td><td>{_fmt(single.get(k))}</td></tr>" for k in metric_keys]
        cmp_html = f"""
        <h3>{label} Metrics</h3>
        <table>
          <thead><tr><th>Metric</th><th>Value</th></tr></thead>
          <tbody>
            {''.join(cmp_rows)}
          </tbody>
        </table>
        """

    # --- 可选统计块 ---
    stat_rows = []
    if sb:
        for k in ["mean","se","t","sharpe","mean_ci","sharpe_ci"]:
            if k in sb:
                stat_rows.append(f"<tr><td>{k}</td><td>{sb[k]}</td></tr>")
    stat_html = ""
    if stat_rows:
        stat_html = f"""
        <h3>Significance (if available)</h3>
        <table><tbody>{''.join(stat_rows)}</tbody></table>
        """

    # --- 图表 ---
    imgs = []
    for name, p in fig.items():
        if p:
            rel = Path(p).name
            imgs.append(f'<div><h4>{name}</h4><img src="{rel}" style="max-width:100%;"/></div>')

    # --- 拼 HTML ---
    html_str = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>FinDiff Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Arial, sans-serif; padding: 20px; }}
    table {{ border-collapse: collapse; margin-bottom: 20px; }}
    td, th {{ border: 1px solid #ccc; padding: 6px 10px; }}
    h1 {{ margin-top: 0; }}
  </style>
</head>
<body>
  <h1>FinDiff Report</h1>

  <h3>Selected Summary</h3>
  <table><tbody>{''.join(rows)}</tbody></table>

  {cmp_html}
  {stat_html}

  {''.join(imgs)}
</body>
</html>
"""
    html.write_text(html_str, encoding="utf-8")
    return str(html)

# ==== append to: src/findiff/reporting.py ====

from typing import Any, Dict, List, Optional

def make_full_report(run_dir: str,
                     result_metrics: Dict[str, float],
                     logs: Dict[str, Any],
                     train_df,
                     synth_df,
                     feature_cols: List[str],
                     nw_lags: int = 5,
                     mbb_block: int = 20,
                     mbb_reps: int = 200) -> str:
    """
    端到端：画图 -> 生成 HTML 报告，返回 report.html 路径。
    统计显著性(stats_block)为可选；若缺依赖/数据则自动降级为 None。
    """
    # 1) 图
    figures = {}
    try:
        figures = save_standard_plots(run_dir, result_metrics, logs, train_df, synth_df, feature_cols)
    except Exception as e:
        # 不阻断主流程；在报告里就没有这些图了
        import warnings
        warnings.warn(f"save_standard_plots failed: {e}")

    # 2) 可选统计块（轻量、安全）
    stats_block = None
    try:
        rets = None
        if isinstance(logs, dict):
            series = logs.get("series", {}) or {}
            rets = series.get("test_returns", None)
        if rets is not None:
            import numpy as np
            r = np.asarray(rets, dtype=float)
            if r.size > 0 and np.isfinite(r).all():
                mean = float(np.mean(r))
                sd = float(np.std(r, ddof=1)) if r.size > 1 else float("nan")
                sharpe = (mean / sd) * (result_metrics.get("ann_factor", 252) ** 0.5) if (sd and sd == sd) else float("nan")
                stats_block = {"mean": mean, "sd": sd, "sharpe": sharpe}
    except Exception:
        stats_block = None  # 静默降级

    # 3) HTML 报告
    return save_html_report(run_dir, result_metrics, logs, stats_block=stats_block, figures=figures)