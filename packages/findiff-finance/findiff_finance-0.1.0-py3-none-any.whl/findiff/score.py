# src/findiff/score.py
from __future__ import annotations
from typing import Dict, Any, Optional, List
import numpy as np
import pandas as pd
from .metrics import compute_eval_metrics

def _ridge_fit(X: np.ndarray, y: np.ndarray, alpha: float = 1e-2) -> np.ndarray:
    # (X^T X + alpha I)^{-1} X^T y
    X = np.asarray(X, float); y = np.asarray(y, float).reshape(-1, 1)
    xtx = X.T @ X
    p = xtx.shape[0]
    w = np.linalg.solve(xtx + alpha * np.eye(p), X.T @ y)
    return w.reshape(-1)

def _predict_linear(X: np.ndarray, w: np.ndarray) -> np.ndarray:
    return X @ w

class TeacherScorer:
    """
    线性教师（ridge）：
      - 在训练段 fit：w = argmin ||Xw - y||
      - teacher_summary: 
          ic = corr(yhat, y), proxy_sharpe = sharpe(yhat*y), max_dd = MDD(yhat*y)
      - 对合成样本：utility_i = yhat_i * y_i
    portfolio/top_frac/cost_bps 配置用于 proxy 组合的收益（简化：直接 yhat*label 即可；可扩展为分层持仓）
    """
    def __init__(self, cfg: Dict[str, Any], time_col: str,
                 asset_col: Optional[str], feature_cols: List[str], label_col: str):
        self.cfg = cfg
        self.time_col = time_col
        self.asset_col = asset_col
        self.feature_cols = feature_cols
        self.label_col = label_col
        self.w: Optional[np.ndarray] = None
        self.mu: Optional[np.ndarray] = None
        self.sd: Optional[np.ndarray] = None
        self.ann = int(cfg.get("portfolio", {}).get("ann_factor", 252))

    def _fit_scaler(self, X: np.ndarray):
        mu = X.mean(axis=0); sd = X.std(axis=0)
        sd[sd == 0] = 1.0
        self.mu, self.sd = mu, sd

    def _norm(self, X: np.ndarray) -> np.ndarray:
        return (X - self.mu) / self.sd

    def fit_teacher(self, train_df: pd.DataFrame):
        X = train_df[self.feature_cols].values
        y = train_df[self.label_col].values
        self._fit_scaler(X)
        Xn = self._norm(X)
        self.w = _ridge_fit(Xn, y, alpha=float(self.cfg.get("alpha", 1e-2)))

    def _proxy_eval(self, yhat: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        # 简化的组合收益：r = yhat * y
        r = yhat * y
        out = compute_eval_metrics(r, ["sharpe", "calmar"], ann=self.ann, prefix="")
        # 最大回撤单独拿出来
        # calmar 里已考虑 MDD，但为保持和旧日志一致，记录一个 max_dd
        # 复制 max_drawdown 逻辑（避免循环导入）
        nav = np.cumprod(1.0 + r)
        peak = np.maximum.accumulate(nav)
        dd = (nav - peak) / peak
        out["max_dd"] = float(-np.nanmin(dd)) if len(dd) else np.nan
        return out

    def score(self, synth_df: pd.DataFrame) -> (pd.DataFrame, Dict[str, float]):
        assert self.w is not None, "fit_teacher() first."
        # teacher summary on train（可选：你也可以把 train_df 传进来重算）
        # 这里简化：用 ridge 的 Xn 与 y 的相关性作为 ic
        # 注意：fit_teacher 时未缓存 train_df，这里只做参数摘要，ic 用 w 与样本协方估算近似：
        # 为稳妥起见，要求由上层 pipeline 传 train_df 进来做 summary 更好，这里返回 proxy 指标为主。
        summary = {}
        # 对合成样本打分
        Xs = synth_df[self.feature_cols].values
        ys = synth_df[self.label_col].values
        Xsn = self._norm(Xs)
        yhat = _predict_linear(Xsn, self.w)
        util = yhat * ys
        out = synth_df.copy()
        out["__utility__"] = util

        # summary（用合成样本做一个近似的 teacher 快照）
        # ic：yhat 与 y 的 Pearson 相关
        if np.std(yhat) > 0 and np.std(ys) > 0:
            summary["ic"] = float(np.corrcoef(yhat, ys)[0, 1])
        else:
            summary["ic"] = 0.0
        pxy = self._proxy_eval(yhat, ys)
        summary.update({"proxy_sharpe": pxy.get("sharpe", np.nan), "max_dd": pxy.get("max_dd", np.nan)})
        return out, summary