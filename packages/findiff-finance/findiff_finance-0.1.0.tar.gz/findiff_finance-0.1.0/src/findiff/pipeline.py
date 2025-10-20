# src/findiff/pipeline.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional

import numpy as np
import pandas as pd

from .config import get_splits
from .data import prepare_df, build_conditions
from .gen import DDPMGenerator
from .mix import blend_real_synth
from .train import fit_and_eval
from .guard import assert_no_leak
from .validators import validate_cfg
from .logging_util import get_logger


# ---------- 工具：按 freq 生成 Offset ----------
def _offset_from_freq(n_days: int, freq: str) -> pd.offsets.BaseOffset | pd.Timedelta:
    """
    将天数 n_days 转为 Offset：
      - freq 以 'B' 开头（如 'B'/'BD'）→ 返回 pandas.offsets.BDay(n)
      - 其他 → 返回 pandas.Timedelta(days=n)
    """
    n = int(n_days)
    if n <= 0:
        return pd.Timedelta(0)
    f = (freq or "D").upper()
    if f.startswith("B"):
        return pd.offsets.BDay(n)
    return pd.Timedelta(days=n)


# ---------- CV 折生成 ----------
def make_time_folds(
    df: pd.DataFrame,
    time_col: str,
    n_folds: int = 5,
    scheme: str = "sliding",
    embargo: int = 0,
    train_window: int = 756,
) -> List[Tuple[np.ndarray, np.ndarray]]:
    """
    生成时间序列 CV 折（只产生 region 内部的 mask；外部数据由上层切分）
    - sliding: 固定 train_window，验证窗口均分
    - expanding: 训练集从起点累积增长，验证窗口均分
    """
    assert n_folds >= 1
    ser = pd.to_datetime(df[time_col].values)
    n = len(ser)
    if n_folds == 1:
        split = int(n * 0.8)
        va_mask = np.zeros(n, dtype=bool)
        va_mask[split:] = True
        tr_mask = ~va_mask
        return [(tr_mask, va_mask)]

    idx = np.linspace(0, n, num=n_folds + 1, dtype=int)
    folds = []
    for i in range(n_folds):
        va_lo, va_hi = idx[i], idx[i + 1]
        if va_hi <= va_lo:
            continue
        va_mask = np.zeros(n, dtype=bool)
        va_mask[va_lo:va_hi] = True

        vstart = ser[va_lo]
        emb_off = _offset_from_freq(embargo, "D")  # 这里只做“天数”偏移
        train_hi_time = vstart - emb_off

        if scheme == "expanding":
            train_lo_time = ser[0]
        else:  # sliding
            train_off = _offset_from_freq(train_window, "D")
            train_lo_time = vstart - train_off

        tr_mask = (ser >= train_lo_time) & (ser < train_hi_time)
        tr_mask = np.asarray(tr_mask, dtype=bool)
        folds.append((tr_mask, va_mask))

    return folds


# ---------- 结果数据结构 ----------
@dataclass
class FinDiffResult:
    metrics: Dict[str, float]
    logs: Dict[str, Any]
    synth_df: Optional[pd.DataFrame] = None
    blended_df: Optional[pd.DataFrame] = None


# ---------- 主流水线 ----------
class FinDiff:
    def __init__(
        self,
        model: Any,
        df: pd.DataFrame,
        time_col: str,
        feature_cols: List[str],
        label_col: str,
        asset_col: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.model = model
        self.df = df.copy()
        self.time_col = time_col
        self.feature_cols = feature_cols
        self.label_col = label_col
        self.asset_col = asset_col
        self.cfg = config or {}
        self.logger = get_logger("findiff.pipeline")

    # ------ 内部：CV + 最终 Test 评估 ------
    def _eval_with_train_df(
        self,
        blended: pd.DataFrame,
        region_df: pd.DataFrame,
        va_ref: pd.DataFrame,
        te: pd.DataFrame,
        merged_params: Dict[str, Any],
        eval_names: List[str],
        ann: int,
        cv_cfg: Dict[str, Any],
        synth_kept: Optional[pd.DataFrame] = None,   # ★ 新增：每折内部再做混合，避免掩码长度不一致
    ):
        """
        在 region(通常是train的80%) 上做 Rolling/Sliding CV，并在 test 段做最终检验。
        修复：
          - 时间偏移统一使用 Offset（不做 Timestamp - int）
          - 训练集按时间筛选仅作用于 region_df（真实样本）；合成样本按配置在每折内混合
        """
        freq = str(self.cfg.get("data", {}).get("freq", "D"))
        embargo = int(cv_cfg.get("embargo", 0))
        train_win = int(cv_cfg.get("train_window", 756))
        min_rows = int(cv_cfg.get("min_train_rows", 96))
        n_folds = int(cv_cfg.get("n_folds", 5))
        scheme = str(cv_cfg.get("scheme", "sliding"))

        folds = make_time_folds(
            region_df, self.time_col, n_folds=n_folds, scheme=scheme, embargo=embargo, train_window=train_win
        )

        fold_metrics = []
        cv_logs: Dict[str, Any] = {"folds": []}
        tser = pd.to_datetime(region_df[self.time_col].values)

        emb_off = _offset_from_freq(embargo, freq)
        train_off = _offset_from_freq(train_win, freq)

        # 逐折评估
        for i, (tr_mask0, va_mask) in enumerate(folds, start=1):
            if va_mask.sum() == 0:
                cv_logs.setdefault("skipped_folds", []).append({"fold": i, "reason": "empty_val"})
                continue

            # 验证起止
            v_times = tser[va_mask]
            vstart, vend = v_times[0], v_times[-1]

            # 训练时间窗：[vstart - train_window, vstart - embargo)
            tr_low_time = pd.Timestamp(vstart) - train_off
            tr_high_time = pd.Timestamp(vstart) - emb_off
            tr_mask = (tser >= tr_low_time) & (tser < tr_high_time)

            train_rows = int(tr_mask.sum())
            if train_rows < min_rows:
                cv_logs.setdefault("skipped_folds", []).append(
                    {"fold": i, "reason": "train_rows<min_train_rows", "train_rows": train_rows}
                )
                continue

            # ★ 本折真实训练集（按时间）
            train_real_fold = region_df.loc[tr_mask]

            # ★ 在“本折内部”做混合（使用全局 synth_kept，按配置比例）
            if synth_kept is not None and len(synth_kept) > 0:
                train_fold = blend_real_synth(train_real_fold, synth_kept, self.cfg.get("mix", {}))
            else:
                train_fold = train_real_fold

            va_fold = region_df.loc[va_mask]

            # 每折构造新模型
            mb = self.cfg.get("train", {}).get("cv", {}).get("model_builder", None)
            model_i = mb() if callable(mb) else (self.model.clone() if hasattr(self.model, "clone") else self.model)

            _, eval_out_i = fit_and_eval(
                model_i,
                train_fold,
                va_fold,
                pd.DataFrame(columns=va_fold.columns),
                self.feature_cols,
                self.label_col,
                merged_params,
                eval_names,
                ann=ann,
            )
            fold_rec = {f"cv{i}_" + k.replace("val_", ""): v for k, v in eval_out_i.items() if k.startswith("val_")}
            fold_metrics.append(fold_rec)
            cv_logs["folds"].append(fold_rec)

        # 汇总 CV
        metrics: Dict[str, float] = {}
        if fold_metrics:
            keys = sorted(set().union(*[d.keys() for d in fold_metrics]))
            for k in keys:
                vals = [d.get(k) for d in fold_metrics if k in d and pd.notna(d.get(k))]
                if vals:
                    metrics[k] = float(np.mean(vals))
            cv_sharpes = [d[k] for d in fold_metrics for k in d if k.endswith("_sharpe")]
            cv_vars = [d[k] for d in fold_metrics for k in d if k.endswith("_var")]
            if cv_sharpes:
                metrics["cv_sharpe_mean"] = float(np.mean(cv_sharpes))
            if cv_vars:
                metrics["cv_var_mean"] = float(np.mean(cv_vars))

        # Test：用 test 起点前（减 embargo）的全部“真实样本”做基底，再混合合成样本
        if len(te) > 0:
            test_start = pd.Timestamp(te[self.time_col].min())
            cut_time = test_start - emb_off
            # ★ 注意：只在真实样本里按时间筛选
            train_full_real = region_df.loc[pd.to_datetime(region_df[self.time_col]) < cut_time]
            if len(train_full_real) >= min_rows:
                if synth_kept is not None and len(synth_kept) > 0:
                    train_full = blend_real_synth(train_full_real, synth_kept, self.cfg.get("mix", {}))
                else:
                    train_full = train_full_real

                mb = self.cfg.get("train", {}).get("cv", {}).get("model_builder", None)
                model_final = mb() if callable(mb) else (self.model.clone() if hasattr(self.model, "clone") else self.model)
                _, test_out, test_series = fit_and_eval(
                    model_final,
                    train_full,
                    pd.DataFrame(columns=te.columns),
                    te,
                    self.feature_cols,
                    self.label_col,
                    merged_params,
                    eval_names,
                    ann=ann,
                    return_series=True,
                )
                metrics.update(test_out)
                if "test_returns" in test_series:
                    cv_logs["test_returns"] = test_series["test_returns"]
            else:
                cv_logs["test_skipped"] = {
                    "reason": f"train_rows<{min_rows} before test",
                    "train_rows": int(len(train_full_real)),
                }
        else:
            cv_logs["note"] = "No test set; only CV metrics reported."

        return metrics, cv_logs

    # ------ 主流程 ------
    def run(self) -> FinDiffResult:
        cfg = self.cfg
        # 配置校验 + 归一化
        self.cfg, cfg_warns = validate_cfg(self.cfg)
        for w in cfg_warns:
            self.logger.warning(f"cfg: {w}")
        cfg = self.cfg  # 后续都用规范化后的 cfg
        freq = str(cfg.get("data", {}).get("freq", "D"))
        eval_names = cfg.get("train", {}).get("eval_metrics", ["sharpe", "calmar", "sharpe_p5", "vol", "var"])
        ann = int(cfg.get("train", {}).get("ann_factor", 252))
        use_cv = bool(cfg.get("train", {}).get("cv", {}).get("enable", True))
        cv_cfg = cfg.get("train", {}).get("cv", {})
        merged_params = cfg.get("train", {}).get("params", {}) or {}

        # 0) 清洗
        df = prepare_df(self.df, self.time_col, self.feature_cols, self.label_col, asset_col=self.asset_col)

        # 1) 切分
        tr, va, te = get_splits(df, self.time_col, cfg.get("data", {}).get("split", {}))
        if cfg.get("safety", {}).get("leakage_check", True):
            assert_no_leak(tr, va, te, self.time_col)

        # region（80%）
        region_df = tr.copy()
        logs: Dict[str, Any] = {}

        # 2) 条件（可选）
        cond_tr = build_conditions(
            region_df,
            cfg.get("conditions", {}),
            self.time_col,
            self.asset_col,
            self.label_col,
        )

        # 3) 生成器训练 & 采样
        gen_cfg = cfg.get("generator", {}) or {}
        gen = DDPMGenerator(gen_cfg)
        if int(gen_cfg.get("epochs", 0)) > 0 and int(gen_cfg.get("steps", 0)) > 0:
            gen.fit(region_df[self.feature_cols], cond_tr)

            # 采样数量：优先 n_samples；否则按 sample_ratio 计算
            n_samples = gen_cfg.get("n_samples", None)
            if n_samples is None:
                r = float(gen_cfg.get("sample_ratio", {}).get("normal", 0.0))
                n_samples = int(max(0, round(len(region_df) * r)))
            n_samples = int(n_samples or 0)

            synth = pd.DataFrame(columns=region_df.columns)
            if n_samples > 0:
                g_scale = float(gen_cfg.get("guidance_scale", 1.3))
                edit_last = int(gen_cfg.get("edit_last_steps", 80))
                synth_X = gen.sample_edit(
                    region_df[self.feature_cols], cond_tr, n_samples, guidance_scale=g_scale, edit_last_steps=edit_last
                )
                # 合成标签：从真实标签自助采样（简单安全）
                y_sample = region_df[self.label_col].sample(n=len(synth_X), replace=True, random_state=42).reset_index(
                    drop=True
                )
                synth = pd.concat(
                    [synth_X.reset_index(drop=True), y_sample.rename(self.label_col)],
                    axis=1,
                )
        else:
            synth = pd.DataFrame(columns=region_df.columns)

        # 4) Teacher 打分与选择（简化版）
        teacher_cfg = cfg.get("teacher", {}) or {}
        k_top = float(teacher_cfg.get("select_rule", {}).get("k_top", 0.35))
        synth_kept = pd.DataFrame(columns=region_df.columns)

        def _teacher_summary(train_df: pd.DataFrame) -> Dict[str, float]:
            if len(train_df) < 32:
                return {"ic": 0.0, "proxy_sharpe": 0.0, "max_dd": 0.0}
            y = train_df[self.label_col].values
            ic = float(np.corrcoef(y[:-1], y[1:])[0, 1]) if len(y) > 1 else 0.0
            mu = float(np.mean(y))
            sd = float(np.std(y) + 1e-12)
            proxy_sharpe = mu / sd * np.sqrt(ann)
            max_dd = float(min(0.0, np.min(np.cumsum(y))))
            return {"ic": ic if np.isfinite(ic) else 0.0, "proxy_sharpe": proxy_sharpe, "max_dd": max_dd}

        t_summary = _teacher_summary(region_df)

        if len(synth) > 0:
            util = synth[self.feature_cols[0]].values
            synth = synth.copy()
            synth["__utility__"] = (util - util.mean()) / (util.std() + 1e-12)

            if k_top > 0.0:
                k = int(max(0, min(len(synth), round(len(synth) * k_top))))
                synth = synth.sort_values("__utility__", ascending=False).reset_index(drop=True)
                synth_kept = synth.iloc[:k].drop(columns=["__utility__"], errors="ignore")
            else:
                synth_kept = synth.drop(columns=["__utility__"], errors="ignore")

        # 5) Auto Gate（根据 teacher_summary 与 gate_if 阈值）
        sec = cfg.get("security", {}) or {}
        auto_gate = bool(sec.get("auto_gate_synth", False))
        gate_if = sec.get("gate_if", {"ic": 0.0, "proxy_sharpe": 0.0})
        auto_gate_triggered = False
        if auto_gate:
            cond_ok = True
            if "ic" in gate_if:
                cond_ok = cond_ok and (t_summary.get("ic", 0.0) >= float(gate_if["ic"]))
            if "proxy_sharpe" in gate_if:
                cond_ok = cond_ok and (t_summary.get("proxy_sharpe", 0.0) >= float(gate_if["proxy_sharpe"]))
            if not cond_ok:
                auto_gate_triggered = True
                synth_kept = synth_kept.iloc[0:0]  # 清空
                fb = sec.get("fallback_mix", None)
                if fb:
                    cfg.setdefault("mix", {})["real_to_synth"] = fb

        # 6) 混合（全量 blended，仅用于日志/参考；CV 内部另行基于窗口重混）
        blended = blend_real_synth(region_df, synth_kept, cfg.get("mix", {}))

        # 7) 训练与评估（增强方案）
        metrics_aug: Dict[str, float] = {}
        cv_logs_aug: Dict[str, Any] = {}
        if bool(cfg.get("train", {}).get("cv", {}).get("enable", True)):
            metrics_aug, cv_logs_aug = self._eval_with_train_df(
                blended, region_df, va, te, merged_params, eval_names, ann, cfg.get("train", {}).get("cv", {}), synth_kept=synth_kept
            )
        else:
            # 直接用 hold-out val/test
            # 按 holdout，不做时间窗口重采；直接用 blended
            _, eval_out, series_out = fit_and_eval(
                self.model,
                blended,
                va,
                te,
                self.feature_cols,
                self.label_col,
                merged_params,
                eval_names,
                ann=ann,
                return_series=True,
            )
            metrics_aug.update(eval_out)
            cv_logs_aug = {}
            cv_logs_aug.setdefault("test_returns", series_out.get("test_returns", None))
            # >>> 新增：先把增强方案记入 logs，供报告对比使用
        logs.setdefault("augmented", {})
        logs["augmented"] = {"cv": cv_logs_aug, "metrics": dict(metrics_aug)}
            # <<< 新增结束
        # 8) Baseline（纯真实数据）+ 选择逻辑
        selected_variant = "augmented"
        security_log = {"auto_gate_triggered": auto_gate_triggered, "fallback_baseline": False}

        if bool(sec.get("eval_gate", False)):
            base_metrics, base_cv_logs = self._eval_with_train_df(
                region_df, region_df, va, te, merged_params, eval_names, ann, cfg.get("train", {}).get("cv", {}), synth_kept=None
            )
            logs_baseline = {"cv": base_cv_logs, "metrics": base_metrics}
            logs = {"baseline": logs_baseline}
            # 选择规则
            acc = sec.get("accept_if", {}) or {}
            accept = True
            th_cv = acc.get("cv_sharpe_mean_min", None)
            if th_cv is not None:
                accept = accept and (metrics_aug.get("cv_sharpe_mean", -1e9) >= float(th_cv))
            th_ts = acc.get("test_sharpe_delta_min", None)
            if th_ts is not None:
                delta = (metrics_aug.get("test_sharpe", -np.inf) - base_metrics.get("test_sharpe", -np.inf))
                accept = accept and (delta >= float(th_ts))
            th_p5 = acc.get("test_p5_delta_min", None)
            if th_p5 is not None and ("test_sharpe_p5" in metrics_aug) and ("test_sharpe_p5" in base_metrics):
                delta_p5 = metrics_aug["test_sharpe_p5"] - base_metrics["test_sharpe_p5"]
                accept = accept and (delta_p5 >= float(th_p5))
            if not accept:
                selected_variant = "baseline"
                security_log["fallback_baseline"] = True
        else:
            logs = {}

        # 9) 汇总日志与指标
        counts = {
            "train": len(tr),
            "val": len(va),
            "test": len(te),
            "synth_total": int(len(synth)),
            "synth_kept": int(len(synth_kept)),
        }
        teacher_summary = dict(t_summary)

        logs.update(
            {
                "counts": counts,
                "teacher_summary": teacher_summary,
                "cv": cv_logs_aug,
                "selected_variant": selected_variant,
                "security": security_log,
            }
        )

        # 输出指标 = 选择方案的指标
        final_metrics = dict(metrics_aug)
        if selected_variant == "baseline" and "baseline" in logs:
            final_metrics = dict(logs["baseline"]["metrics"])
            logs["selected_variant"] = "baseline"

        return FinDiffResult(metrics=final_metrics, logs=logs, synth_df=synth_kept, blended_df=blended)