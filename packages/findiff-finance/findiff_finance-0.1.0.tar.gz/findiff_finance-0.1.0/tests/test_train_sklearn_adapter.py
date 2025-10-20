# tests/test_train_sklearn_adapter.py
import numpy as np
from sklearn.linear_model import LinearRegression
from findiff.train import fit_and_eval

def test_fit_and_eval_with_sklearn_adapter(tiny_df):
    df = tiny_df.copy()
    time_col, label_col = "date", "y"
    feature_cols = ["f1","f2"]

    split = int(len(df) * 0.8)
    tr = df.iloc[:split].copy()
    te = df.iloc[split:].copy()

    model = LinearRegression()
    _, met, series = fit_and_eval(model, tr, tr.iloc[0:0], te, feature_cols, label_col,
                                  params={}, eval_names=["sharpe","var"], ann=252, return_series=True)
    assert "test_sharpe" in met and "test_returns" in series
    assert np.isfinite(series["test_returns"]).any()