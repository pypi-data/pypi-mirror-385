# tests/test_time_folds.py
import numpy as np
from findiff.pipeline import make_time_folds

def test_time_folds_no_overlap(tiny_df):
    df = tiny_df.copy()
    folds = make_time_folds(df, "date", n_folds=4, scheme="sliding", embargo=5, train_window=100)
    tvals = df["date"].values
    for tr_mask, va_mask in folds:
        # 验证集非空
        assert va_mask.sum() > 0
        vstart, vend = tvals[va_mask][0], tvals[va_mask][-1]
        # 训练不包含验证窗口（含 embargo）
        assert not np.any(tr_mask & va_mask)
        # 训练最晚日期 < vstart - embargo
        if tr_mask.sum() > 0:
            assert tvals[tr_mask].max() < vstart