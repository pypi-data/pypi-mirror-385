# src/findiff/dataio.py
from __future__ import annotations
from typing import List, Optional
import pandas as pd

def load_timeseries_csv(path: str,
                        time_col: str,
                        feature_cols: Optional[List[str]] = None,
                        label_col: Optional[str] = None,
                        parse_dates: bool = True,
                        fillna: bool = True) -> pd.DataFrame:
    df = pd.read_csv(path)
    if parse_dates:
        df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
    df = df.sort_values(time_col).reset_index(drop=True)
    if fillna:
        df = df.fillna(method="ffill").fillna(method="bfill")
    if feature_cols is not None and label_col is not None:
        cols = [time_col] + feature_cols + [label_col]
        miss = [c for c in cols if c not in df.columns]
        if miss:
            raise ValueError(f"Missing columns: {miss}")
        df = df[cols]
    return df