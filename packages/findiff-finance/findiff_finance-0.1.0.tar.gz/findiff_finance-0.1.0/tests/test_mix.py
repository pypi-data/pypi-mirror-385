# tests/test_mix.py
import pandas as pd
from findiff.mix import blend_real_synth

def test_blend_real_synth_counts():
    tr = pd.DataFrame({"a":[1,2,3,4,5], "x":[0,0,0,0,0]})
    synth = pd.DataFrame({"a":[10,20], "x":[1,1], "__utility__":[0.9,0.8]})
    cfg = {"real_to_synth": "1.0:0.4"}  # 5真实 -> 需要 2 合成（四舍五入向下）
    out = blend_real_synth(tr, synth, cfg)
    assert len(out) == 5 + 2