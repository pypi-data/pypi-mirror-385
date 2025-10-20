# src/findiff/utils/io.py
from __future__ import annotations
from typing import Dict, Any, Optional
import os, json, pickle
from pathlib import Path

import numpy as np
import pandas as pd
try:
    import yaml
except Exception:
    yaml = None

from ..pipeline import FinDiffResult
from .logging import get_run_id, env_summary

def _ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def _to_jsonable(obj):
    if isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    if isinstance(obj, (np.integer, np.int32, np.int64)):
        return int(obj)
    if isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    if isinstance(obj, (pd.Series,)):
        return obj.to_dict()
    if isinstance(obj, (pd.Timestamp,)):
        return obj.isoformat()
    return obj

def _dump_json(path: Path, data: Dict[str, Any]):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=_to_jsonable)

def _save_model_generic(model: Any, out_dir: Path):
    """
    尽力保存用户模型：
      1) 若是我们提供的 TorchTimeSeriesRegressor：保存 state_dict + pickle
      2) 若有 .state_dict()：同时保存 state_dict
      3) 优先 joblib；否则 pickle
    """
    model_dir = out_dir / "model"
    _ensure_dir(model_dir)

    # 1) torch state_dict（如果可用）
    try:
        import torch
        if hasattr(model, "state_dict"):
            sd = model.state_dict()
            torch.save(sd, model_dir / "state_dict.pt")
    except Exception:
        pass

    # 2) joblib 优先
    try:
        import joblib
        joblib.dump(model, model_dir / "model.joblib")
        return str(model_dir / "model.joblib")
    except Exception:
        pass

    # 3) pickle 兜底
    with (model_dir / "model.pkl").open("wb") as f:
        pickle.dump(model, f)
    return str(model_dir / "model.pkl")

def export_run(result: FinDiffResult,
               cfg: Dict[str, Any],
               out_root: str = "artifacts/runs",
               model: Optional[Any] = None,
               tag: Optional[str] = None) -> str:
    """
    将一次 run 的产出落盘：
      artifacts/runs/<run-id>/{metrics.json, logs.json, cfg.yaml/json, synth_kept.csv, blended.csv, model/*}
    返回 run 目录路径。
    """
    run_id = get_run_id("findiff" + (f"-{tag}" if tag else ""))
    out_dir = Path(out_root) / run_id
    _ensure_dir(out_dir)

    # cfg
    if yaml is not None:
        with (out_dir / "cfg.yaml").open("w", encoding="utf-8") as f:
            yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)
    else:
        _dump_json(out_dir / "cfg.json", cfg)

    # metrics & logs（附环境信息）
    metrics = result.metrics.copy()
    logs = result.logs.copy()
    logs.setdefault("env", env_summary())
    _dump_json(out_dir / "metrics.json", metrics)
    _dump_json(out_dir / "logs.json", logs)

    # 数据（仅研究用；可按需关掉）
    try:
        if result.synth_df is not None and len(result.synth_df) > 0:
            result.synth_df.to_csv(out_dir / "synth_kept.csv", index=False)
        if result.blended_df is not None and len(result.blended_df) > 0:
            result.blended_df.to_csv(out_dir / "blended.csv", index=False)
    except Exception:
        pass

    # 模型（如果提供）
    if model is not None:
        _save_model_generic(model, out_dir)

    return str(out_dir)