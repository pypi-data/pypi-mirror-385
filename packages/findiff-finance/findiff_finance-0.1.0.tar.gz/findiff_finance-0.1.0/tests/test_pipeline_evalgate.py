# tests/test_pipeline_evalgate.py
import pandas as pd
from findiff.pipeline import FinDiff
from findiff.config import deep_update, default_cfg
from findiff.train import TorchTimeSeriesRegressor

def test_pipeline_eval_gate_fallback(tiny_df):
    df = tiny_df.copy()
    time_col, label_col = "date", "y"
    feature_cols = ["f1","f2"]

    cfg = deep_update(default_cfg(), {
        "data": {"split": {"train": ("min","q80"), "val": ("q80","q80"), "test": ("q80","max")}},
        "generator": {"epochs": 1, "steps": 10, "edit_last_steps": 4, "n_samples": 64, "sample_ratio":{"normal":0.2}},
        "teacher": {"select_rule": {"k_top": 0.5}},
        "mix": {"real_to_synth": "1.0:0.3"},
        "train": {"cv": {"enable": True, "region":"train", "scheme":"sliding", "train_window":100,
                         "n_folds": 3, "embargo": 10, "min_train_rows": 32},
                  "eval_metrics": ["sharpe","var"], "ann_factor": 252,
                  "params": {"epochs": 1, "batch_size": 64}},
        "security": {"auto_gate_synth": False, "eval_gate": True,
                     "accept_if": {"cv_sharpe_mean_min": 9.99, "test_sharpe_delta_min": 9.99, "test_p5_delta_min": 9.99}}
    })

    model = TorchTimeSeriesRegressor(in_dim=len(feature_cols), window=16, hidden=32, epochs=1, batch_size=64)
    res = FinDiff(model, df, time_col, feature_cols, label_col, asset_col=None, config=cfg).run()

    assert res.logs.get("selected_variant") == "baseline"
    assert res.logs.get("security", {}).get("fallback_baseline", False) is True