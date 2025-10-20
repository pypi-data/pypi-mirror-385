# src/findiff/data.py
from __future__ import annotations
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

def prepare_df(df: pd.DataFrame, time_col: str, feature_cols, label_col: str, asset_col: Optional[str]=None) -> pd.DataFrame:
    """
    - 时间排序
    - 精确去重：同 (time_col, asset_col?) 完全重复行只保留首个
    - 特征缺失 ffill→bfill
    - 丢弃 label 缺失
    """
    out = df.copy()
    out = out.replace([np.inf, -np.inf], np.nan)
    out = out.sort_values(time_col)

    # 去重键：有资产列就 (time, asset)，否则只用 time
    key_cols = [time_col] + ([asset_col] if asset_col else [])
    out = out.drop_duplicates(subset=key_cols, keep="first")

    if feature_cols:
        out.loc[:, feature_cols] = out[feature_cols].ffill().bfill()

    out = out.dropna(subset=[label_col]).reset_index(drop=True)
    return out

def build_conditions(df: pd.DataFrame, cfg: Dict[str, Any],
                     time_col: str, asset_col: Optional[str], label_col: str) -> pd.DataFrame:
    """
    根据 cfg['fields'] 计算条件列。
    - trend: rolling mean(label, window).shift(1)  防止泄漏
    - vol_level: rolling std(label, window).shift(1) 再按 quantiles 分箱 {0,1,2}
    """
    if not cfg or not cfg.get("enable", True):
        return pd.DataFrame(index=df.index)

    fields = cfg.get("fields", [])
    builders = cfg.get("builders", {})
    out = pd.DataFrame(index=df.index)

    if "trend" in fields:
        w = int(builders.get("trend", {}).get("window", 63))
        ln = builders.get("trend", {}).get("label_name", label_col)
        lbl = ln if ln in df.columns else label_col
        if asset_col:
            tr = (
                df.groupby(asset_col)[lbl]
                .rolling(w).mean().shift(1)
                .reset_index(level=0, drop=True)
            )
        else:
            tr = df[lbl].rolling(w).mean().shift(1)
        out["trend"] = tr

    if "vol_level" in fields:
        b = builders.get("vol_level", {})
        w = int(b.get("window", 21))
        ln = b.get("label_name", label_col)
        lbl = ln if ln in df.columns else label_col
        qs = b.get("quantiles", [0.33, 0.67])

        if asset_col:
            vol = (
                df.groupby(asset_col)[lbl]
                .rolling(w).std().shift(1)
                .reset_index(level=0, drop=True)
            )
        else:
            vol = df[lbl].rolling(w).std().shift(1)

        # 分箱：基于训练段的历史分位数（本函数通常对 train 调用）
        q1, q2 = np.nanquantile(vol.dropna().values, qs[0]), np.nanquantile(vol.dropna().values, qs[1])
        lvl = pd.Series(np.nan, index=vol.index, dtype=float)
        lvl[vol <= q1] = 0.0
        lvl[(vol > q1) & (vol <= q2)] = 1.0
        lvl[vol > q2] = 2.0
        out["vol_level"] = lvl

    # 统一缺失处理（后续生成器可决定是否再填充）
    return out