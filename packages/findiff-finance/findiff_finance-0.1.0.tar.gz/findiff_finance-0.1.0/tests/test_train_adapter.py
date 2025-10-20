# tests/test_train_adapter.py
import numpy as np
from findiff.train import TorchTimeSeriesRegressor, fit_and_eval

def test_torch_regressor_fit_predict(tiny_df):
    df = tiny_df.copy()
    time_col, label_col = "date", "y"
    feature_cols = ["f1","f2"]

    # 简单切分
    split = int(len(df) * 0.8)
    tr = df.iloc[:split].copy()
    te = df.iloc[split:].copy()

    model = TorchTimeSeriesRegressor(in_dim=len(feature_cols), window=16, hidden=32, epochs=1, batch_size=128)
    # 训练 + 返回序列
    _, metrics, series = fit_and_eval(model, tr, tr.iloc[0:0], te, feature_cols, label_col,
                                      params={}, eval_names=["sharpe","var"], ann=252, return_series=True)

    assert "test_sharpe" in metrics and "test_var" in metrics
    assert "test_returns" in series
    r = np.asarray(series["test_returns"], float)
    assert r.ndim == 1 and r.size > 0 and np.isfinite(r).any()