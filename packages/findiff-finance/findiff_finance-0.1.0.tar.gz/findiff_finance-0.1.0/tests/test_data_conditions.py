# tests/test_data_conditions.py
import numpy as np
import pandas as pd
from findiff.data import build_conditions, prepare_df

def test_build_conditions_with_placeholder_label(tiny_df):
    df = tiny_df.copy()
    df = prepare_df(df, "date", ["f1","f2"], "y", asset_col=None)
    cfg = {
        "fields": ["trend", "vol_level"],
        "builders": {
            "trend": {"window": 5, "label_name": "${label_col}"},
            "vol_level": {"window": 10, "label_name": "not_exists", "quantiles":[0.3,0.7]},
        }
    }
    cond = build_conditions(df, cfg, time_col="date", asset_col=None, label_col="y")
    assert "trend" in cond.columns and "vol_level" in cond.columns
    assert np.isfinite(cond["trend"].iloc[10:]).all()