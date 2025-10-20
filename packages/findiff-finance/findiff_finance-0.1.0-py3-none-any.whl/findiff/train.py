# src/findiff/train.py
from __future__ import annotations
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from .metrics import compute_eval_metrics

def _make_windows(df: pd.DataFrame, feature_cols: List[str], label_col: str, window: int) -> Tuple[np.ndarray, np.ndarray]:
    X = df[feature_cols].values
    y = df[label_col].values
    xs, ys = [], []
    for i in range(window, len(df)):
        xs.append(X[i-window:i, :])
        ys.append(y[i])
    return np.asarray(xs, dtype=np.float32), np.asarray(ys, dtype=np.float32)

def _make_X_windows(df: pd.DataFrame, feature_cols: List[str], window: int) -> np.ndarray:
    X = df[feature_cols].values
    xs = []
    for i in range(window, len(df)):
        xs.append(X[i-window:i, :])
    return np.asarray(xs, dtype=np.float32)

class _GRUReg(nn.Module):
    def __init__(self, in_dim: int, hidden: int = 128, num_layers: int = 1, dropout: float = 0.2):
        super().__init__()
        self.gru = nn.GRU(input_size=in_dim, hidden_size=hidden, num_layers=num_layers,
                          batch_first=True, dropout=0.0 if num_layers==1 else dropout)
        self.head = nn.Sequential(nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, 1))
        self.tanh = nn.Tanh()
    def forward(self, x):
        out, _ = self.gru(x)
        last = out[:, -1, :]
        y = self.head(last)
        return self.tanh(y).squeeze(-1)

class TorchTimeSeriesRegressor:
    def __init__(self, in_dim: int, window: int = 96, hidden: int = 128,
                 num_layers: int = 1, dropout: float = 0.2,
                 epochs: int = 10, batch_size: int = 512, lr: float = 1e-3,
                 device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.in_dim = in_dim; self.window = window
        self.hidden = hidden; self.num_layers = num_layers; self.dropout = dropout
        self.epochs = epochs; self.batch_size = batch_size; self.lr = lr
        self.device = torch.device(device)
        self.net = _GRUReg(in_dim, hidden, num_layers, dropout).to(self.device)
        self.x_mean = None; self.x_std = None

    def clone(self):
        return TorchTimeSeriesRegressor(in_dim=self.in_dim, window=self.window,
                                        hidden=self.hidden, num_layers=self.num_layers, dropout=self.dropout,
                                        epochs=self.epochs, batch_size=self.batch_size, lr=self.lr,
                                        device=str(self.device))

    def _fit_scaler(self, X: np.ndarray):
        mu = X.mean(axis=0); sd = X.std(axis=0)
        sd[sd==0] = 1.0
        self.x_mean, self.x_std = mu, sd

    def fit_with_df(self, train_df: pd.DataFrame, feature_cols: List[str], label_col: str, **params):
        if params:
            self.epochs     = int(params.get("epochs", self.epochs))
            self.batch_size = int(params.get("batch_size", self.batch_size))
            self.lr         = float(params.get("lr", self.lr))

        X_full = train_df[feature_cols].values
        self._fit_scaler(X_full)
        train_df_norm = train_df.copy()
        train_df_norm.loc[:, feature_cols] = (X_full - self.x_mean) / self.x_std

        X_seq, y_seq = _make_windows(train_df_norm, feature_cols, label_col, self.window)
        if len(X_seq) == 0:
            raise ValueError(f"Not enough rows for window={self.window}")

        ds = TensorDataset(torch.tensor(X_seq, dtype=torch.float32, device=self.device),
                           torch.tensor(y_seq.reshape(-1), dtype=torch.float32, device=self.device))
        dl = DataLoader(ds, batch_size=self.batch_size, shuffle=True, drop_last=False)
        opt = torch.optim.Adam(self.net.parameters(), lr=self.lr)
        loss_fn = nn.MSELoss()

        self.net.train()
        for _ in range(self.epochs):
            for xb, yb in dl:
                pred = self.net(xb)
                loss = loss_fn(pred, yb)
                opt.zero_grad(); loss.backward(); opt.step()
        return self

    @torch.no_grad()
    def predict_with_df(self, df: pd.DataFrame, feature_cols: List[str]) -> np.ndarray:
        df = df.copy()
        X = df[feature_cols].values
        Xn = (X - self.x_mean) / self.x_std
        df.loc[:, feature_cols] = Xn
        X_seq = _make_X_windows(df, feature_cols, self.window)
        if len(X_seq) == 0:
            return np.array([])
        dl = DataLoader(torch.tensor(X_seq, dtype=torch.float32, device=self.device),
                        batch_size=1024, shuffle=False)
        self.net.eval()
        preds = []
        for xb in dl:
            preds.append(self.net(xb).detach().cpu().numpy())
        preds = np.concatenate(preds, axis=0)
        pad = np.full((self.window,), np.nan)
        return np.concatenate([pad, preds], axis=0)

    # sklearn 兼容
    def fit(self, X: np.ndarray, y: np.ndarray, **params):
        if params:
            self.epochs     = int(params.get("epochs", self.epochs))
            self.batch_size = int(params.get("batch_size", self.batch_size))
            self.lr         = float(params.get("lr", self.lr))
        self._fit_scaler(X)
        Xn = (X - self.x_mean) / self.x_std
        Xn = Xn[:, None, :]
        ds = TensorDataset(torch.tensor(Xn, dtype=torch.float32, device=self.device),
                           torch.tensor(y.reshape(-1), dtype=torch.float32, device=self.device))
        dl = DataLoader(ds, batch_size=self.batch_size, shuffle=True, drop_last=False)
        opt = torch.optim.Adam(self.net.parameters(), lr=self.lr)
        loss_fn = nn.MSELoss()
        self.net.train()
        for _ in range(self.epochs):
            for xb, yb in dl:
                pred = self.net(xb)
                loss = loss_fn(pred, yb)
                opt.zero_grad(); loss.backward(); opt.step()
        return self

    @torch.no_grad()
    def predict(self, X: np.ndarray) -> np.ndarray:
        Xn = (X - self.x_mean) / self.x_std
        Xn = Xn[:, None, :]
        self.net.eval()
        dl = DataLoader(torch.tensor(Xn, dtype=torch.float32, device=self.device),
                        batch_size=1024, shuffle=False)
        preds = []
        for xb in dl:
            preds.append(self.net(xb).detach().cpu().numpy())
        return np.concatenate(preds, axis=0)

def fit_and_eval(model: Any,
                 train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame,
                 feature_cols: List[str], label_col: str,
                 params: Dict[str, Any], eval_names: List[str], ann: int = 252,
                 return_series: bool = False):
    """
    训练并评估（返回 model, metrics[, series]）。
    - 若模型实现 fit_with_df / predict_with_df，优先用时序接口；
    - 度量对 val/test 段计算 r = yhat * y（包含 var）。
    - return_series=True 时返回 { 'val_returns': ndarray?, 'test_returns': ndarray? }
    """
    # 训练
    if hasattr(model, "fit_with_df"):
        model.fit_with_df(train_df, feature_cols, label_col, **(params or {}))
    else:
        Xtr, ytr = train_df[feature_cols].values, train_df[label_col].values
        model.fit(Xtr, ytr, **(params or {}))

    out = {}
    series_out: Dict[str, np.ndarray] = {}

    def _eval_one(tag: str, df: pd.DataFrame):
        if len(df) == 0:
            return
        if hasattr(model, "predict_with_df"):
            yhat = model.predict_with_df(df, feature_cols)
        else:
            yhat = model.predict(df[feature_cols].values)
        y = df[label_col].values
        m = ~np.isnan(yhat)
        if m.sum() == 0:
            return
        r = yhat[m] * y[m]
        met = compute_eval_metrics(r, eval_names, ann=ann, prefix=f"{tag}_")
        out.update(met)
        if return_series:
            series_out[f"{tag}_returns"] = r

    _eval_one("val", val_df)
    _eval_one("test", test_df)

    if return_series:
        return model, out, series_out
    return model, out