# src/findiff/mix.py
from __future__ import annotations
from typing import Dict, Any
import pandas as pd
import numpy as np

def _parse_ratio(r: str):
    # "1.0:0.2" -> (1.0, 0.2)
    a, b = r.split(":")
    return float(a), float(b)

def blend_real_synth(train_df: pd.DataFrame, synth_kept: pd.DataFrame, cfg: Dict[str, Any]) -> pd.DataFrame:
    """
    按比例将合成样本与真实样本混合。
    cfg["real_to_synth"] = "1.0:0.2" 表示 synth = 0.2 * real_count
    """
    ratio = cfg.get("real_to_synth", "1.0:0.0")
    a, b = _parse_ratio(ratio)
    real_n = len(train_df)
    need_synth = int(real_n * (b / max(a, 1e-12)))
    if len(synth_kept) <= 0 or need_synth <= 0:
        return train_df.copy()
    # 若不足则有放回采样，若过多则截断
    if len(synth_kept) >= need_synth:
        syn = synth_kept.sample(n=need_synth, replace=False, random_state=42)
    else:
        syn = synth_kept.sample(n=need_synth, replace=True, random_state=42)
    blended = pd.concat([train_df, syn], axis=0, ignore_index=True)
    return blended