# tests/test_stats_plot_report.py
import numpy as np
import pandas as pd
from pathlib import Path

from findiff.stats import nw_tstat_mean, moving_block_bootstrap_ci
from findiff.reporting import save_standard_plots, save_html_report, make_full_report

def test_stats_functions_basic():
    r = np.array([0.001, -0.0005, 0.0008, 0.0002, -0.0003] * 20, dtype=float)
    out = nw_tstat_mean(r, lags=3)
    assert set(out.keys()) == {"mean","se","t","sharpe"}
    ci = moving_block_bootstrap_ci(r, block=10, reps=100)
    assert "mean_ci" in ci and "sharpe_ci" in ci

def test_reporting_end2end(tmp_path: Path):
    # 伪 logs/metrics + 简易数据
    logs = {
        "cv": {"folds": [{"cv1_sharpe": 0.2}, {"cv2_sharpe": -0.1}]},
        "series": {"test_returns": [0.001, -0.0005, 0.0007, 0.0, 0.0003]},
        "selected_variant": "augmented",
    }
    metrics = {"cv_sharpe_mean": 0.05, "cv_var_mean": 1e-6, "test_sharpe": 0.2, "test_var": 1e-6,
               "test_sharpe_p5": 0.1, "test_calmar": 0.3}
    train_df = pd.DataFrame({"f": [1,2,3,4,5], "y":[0,0,0,0,0]})
    synth_df = pd.DataFrame({"f": [1,1,2,3,5], "y":[0,0,0,0,0]})
    figs = save_standard_plots(str(tmp_path), metrics, logs, train_df, synth_df, ["f"])
    assert "cv_bars" in figs and "test_nav" in figs and "psi_heat" in figs
    rep = save_html_report(str(tmp_path), metrics, logs, stats_block=None, figures=figs)
    assert Path(rep).exists()

def test_make_full_report(tmp_path: Path):
    logs = {"series": {"test_returns": [0.001, 0.0, -0.0002, 0.0003]}}
    metrics = {}
    # 不提供 train/synth 也应能生成报告
    path = make_full_report(str(tmp_path), metrics, logs, train_df=None, synth_df=None, feature_cols=None, mbb_reps=100)
    assert Path(path).exists()