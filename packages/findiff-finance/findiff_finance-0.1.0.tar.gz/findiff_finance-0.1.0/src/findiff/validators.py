# src/findiff/validators.py
from __future__ import annotations
from typing import Any, Dict, Tuple, List

def _clamp(x, lo, hi):
    try:
        v = float(x)
    except Exception:
        return lo
    return max(lo, min(v, hi))

def validate_cfg(cfg: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Return (normalized_cfg, warnings). 不改原 dict。"""
    c = {**cfg}
    warns: List[str] = []

    data = c.setdefault("data", {})
    data.setdefault("freq", "B")
    data.setdefault("split", {"train": ("min","q80"), "val": ("q80","q80"), "test": ("q80","max")})

    gen = c.setdefault("generator", {})
    gen.setdefault("epochs", 0)
    gen.setdefault("steps", 0)
    gen.setdefault("edit_last_steps", 0)
    gen.setdefault("guidance_scale", 1.3)
    gen.setdefault("batch_size", 256)
    gen.setdefault("sample_ratio", {"normal": 0.0})

    if gen["epochs"] > 0 and gen["steps"] <= 0:
        gen["steps"] = 200
        warns.append("generator.steps<=0, set to 200")
    if gen["edit_last_steps"] > gen["steps"] and gen["steps"] > 0:
        gen["edit_last_steps"] = max(1, int(0.2 * gen["steps"]))
        warns.append("generator.edit_last_steps>steps, shrink to 20% steps")

    sr = gen.get("sample_ratio", {})
    for k, v in list(sr.items()):
        nv = _clamp(v, 0.0, 1.0)
        if nv != v:
            warns.append(f"generator.sample_ratio[{k}] clamped to [0,1]")
            sr[k] = nv

    teacher = c.setdefault("teacher", {})
    rule = teacher.setdefault("select_rule", {"k_top": 0.35})
    rule["k_top"] = _clamp(rule.get("k_top", 0.35), 0.0, 1.0)

    mix = c.setdefault("mix", {})
    mix.setdefault("real_to_synth", "1.0:0.0")
    # 解析比例
    try:
        r, s = mix["real_to_synth"].split(":")
        r, s = float(r), float(s)
        if r < 0 or s < 0:
            raise ValueError
        mix["_ratio_tuple"] = (r, s)
    except Exception:
        mix["real_to_synth"] = "1.0:0.0"
        mix["_ratio_tuple"] = (1.0, 0.0)
        warns.append("mix.real_to_synth invalid, fallback to 1.0:0.0")

    train = c.setdefault("train", {})
    train.setdefault("params", {})
    train.setdefault("eval_metrics", ["sharpe","calmar","sharpe_p5","vol","var"])
    train.setdefault("ann_factor", 252)

    cv = train.setdefault("cv", {})
    cv.setdefault("enable", True)
    cv.setdefault("region", "train")
    cv.setdefault("scheme", "sliding")
    cv.setdefault("train_window", 756)
    cv.setdefault("n_folds", 5)
    cv.setdefault("embargo", 63)
    cv.setdefault("min_train_rows", 96)
    if cv["n_folds"] < 1:
        warns.append("train.cv.n_folds<1, set to 1")
        cv["n_folds"] = 1
    if cv["min_train_rows"] < 8:
        warns.append("train.cv.min_train_rows too small, set to 8")
        cv["min_train_rows"] = 8

    sec = c.setdefault("security", {})
    sec.setdefault("auto_gate_synth", False)
    sec.setdefault("gate_if", {"ic": 0.0, "proxy_sharpe": 0.0})
    sec.setdefault("fallback_mix", "1.0:0.0")
    sec.setdefault("eval_gate", False)
    sec.setdefault("accept_if", {})

    return c, warns