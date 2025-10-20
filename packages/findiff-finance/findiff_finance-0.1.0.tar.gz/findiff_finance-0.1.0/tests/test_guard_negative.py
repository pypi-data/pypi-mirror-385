# tests/test_guard_negative.py
import pytest
from findiff.guard import assert_no_leak

def test_assert_no_leak_raises_on_overlap(tiny_df):
    df = tiny_df.copy()
    # 人为制造重叠的 tr/va，绕开 get_splits 的修正逻辑
    tr = df.iloc[:200].copy()
    va = df.iloc[150:250].copy()  # 与 train 重叠
    te = df.iloc[250:].copy()
    with pytest.raises(AssertionError):
        assert_no_leak(tr, va, te, "date")