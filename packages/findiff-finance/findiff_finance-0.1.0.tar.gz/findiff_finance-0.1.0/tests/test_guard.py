# tests/test_guard.py
import pandas as pd
from findiff.config import get_splits
from findiff.guard import assert_no_leak

def test_no_leakage_basic(tiny_df):
    df = tiny_df.copy()
    split = {"train": ("min", "q80"), "val": ("q80", "q80"), "test": ("q80", "max")}
    tr, va, te = get_splits(df, "date", split)
    # 不应抛异常
    assert_no_leak(tr, va, te, "date")
    # 边界检查：最大train < 最小val < 最小test
    assert len(tr) > 0 and len(te) > 0
    assert tr["date"].max() < te["date"].min()
    if len(va) > 0:
        assert tr["date"].max() < va["date"].min() <= te["date"].min()