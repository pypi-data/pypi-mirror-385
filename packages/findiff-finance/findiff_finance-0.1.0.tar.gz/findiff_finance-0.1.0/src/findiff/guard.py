# src/findiff/guard.py
from __future__ import annotations
import pandas as pd
from typing import Optional

def _min(df: pd.DataFrame, col: str) -> Optional[float]:
    return df[col].min() if len(df) > 0 else None

def _max(df: pd.DataFrame, col: str) -> Optional[float]:
    return df[col].max() if len(df) > 0 else None

def assert_no_leak(tr: pd.DataFrame, va: pd.DataFrame, te: pd.DataFrame, time_col: str):
    """
    防穿越校验（允许 val/test 为空）：
      - 若 val 非空：要求 max(train) < min(val)
      - 若 test 非空：要求 (val 非空时) max(val) < min(test)，否则要求 max(train) < min(test)
    """
    if len(tr) == 0 and len(va) == 0 and len(te) == 0:
        return

    t_max = _max(tr, time_col)
    v_min = _min(va, time_col)
    v_max = _max(va, time_col)
    te_min = _min(te, time_col)

    if len(tr) > 0 and len(va) > 0:
        assert t_max is not None and v_min is not None and t_max < v_min, "Train/Val overlap!"

    if len(va) > 0 and len(te) > 0:
        assert v_max is not None and te_min is not None and v_max < te_min, "Val/Test overlap!"

    if len(va) == 0 and len(tr) > 0 and len(te) > 0:
        assert t_max is not None and te_min is not None and t_max < te_min, "Train/Test overlap!"