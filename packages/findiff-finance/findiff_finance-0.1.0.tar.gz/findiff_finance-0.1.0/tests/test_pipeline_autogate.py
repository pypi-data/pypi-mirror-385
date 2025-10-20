# tests/test_pipeline_autogate.py
from findiff.pipeline import FinDiff
from findiff.config import deep_update, default_cfg

def test_pipeline_auto_gate(tiny_df):
    df = tiny_df.copy()
    time_col, label_col = "date", "y"
    feature_cols = ["f1","f2"]

    # 配置：强制触发 auto_gate（把阈值设得很高），并关闭CV以加速
    cfg = deep_update(default_cfg(), {
        "data": {"split": {"train": ("min","q80"), "val": ("q80","q80"), "test": ("q80","max")}},
        "generator": {"epochs": 1, "steps": 50, "edit_last_steps": 10, "n_samples": 128, "sample_ratio":{"normal":0.2}},
        "teacher": {"select_rule": {"k_top": 0.5}},
        "mix": {"real_to_synth": "1.0:0.5"},
        "train": {"cv": {"enable": False}, "eval_metrics": ["sharpe","var"], "ann_factor": 252,
                  "params": {"epochs": 1, "batch_size": 128}},
        "security": {"auto_gate_synth": True, "gate_if": {"ic": 0.99, "proxy_sharpe": 9.99},
                     "fallback_mix": "1.0:0.0", "eval_gate": False}
    })

    # 直接传入我们库自带的时序模型（由 pipeline 内部访问）
    from findiff.train import TorchTimeSeriesRegressor
    model = TorchTimeSeriesRegressor(in_dim=len(feature_cols), window=16, hidden=32, epochs=1, batch_size=128)

    res = FinDiff(model, df, time_col, feature_cols, label_col, asset_col=None, config=cfg).run()
    # 自动门控应触发；合成被清空；最终混合中只含真实数据
    assert res.logs.get("security", {}).get("auto_gate_triggered", False) is True
    assert res.logs["counts"]["synth_kept"] == 0
    # metrics 至少包含 test 或 val 指标之一
    assert any(k.startswith("test_") or k.startswith("val_") for k in res.metrics.keys())