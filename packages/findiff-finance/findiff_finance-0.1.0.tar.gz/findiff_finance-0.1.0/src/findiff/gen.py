# src/findiff/gen.py
from __future__ import annotations
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

def _to_tensor(x: np.ndarray, device):
    return torch.tensor(x, dtype=torch.float32, device=device)

class _MLP(nn.Module):
    def __init__(self, in_dim: int, out_dim: int, hidden: int = 256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, out_dim)
        )
    def forward(self, x):
        return self.net(x)

class DDPMGenerator:
    """
    轻量“表格扩散”生成器：去噪噪声预测（noise-prediction）+ 条件拼接。
    - 训练：随机挑选噪声强度 sigma，对 x + sigma*eps 用 MLP 预测 eps(仅特征维度)，MSE 损失。
    - 条件：将 cond 直接拼接到输入（可配 cond_drop_p）。
    - 采样：从“真实样本 + 初始噪声”开始，只做后半段的反向去噪（轻编辑）。
    """
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.scaler_mean: Optional[np.ndarray] = None
        self.scaler_std: Optional[np.ndarray] = None
        self.model: Optional[_MLP] = None
        self.cond_dim: int = 0
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.noise_levels = None

    def _fit_scaler(self, X: pd.DataFrame):
        mu = X.values.mean(axis=0)
        sd = X.values.std(axis=0)
        sd[sd == 0] = 1.0
        self.scaler_mean, self.scaler_std = mu, sd

    def _norm(self, X: np.ndarray) -> np.ndarray:
        return (X - self.scaler_mean) / self.scaler_std

    def _denorm(self, Xn: np.ndarray) -> np.ndarray:
        return Xn * self.scaler_std + self.scaler_mean

    def fit(self, X: pd.DataFrame, cond_df: Optional[pd.DataFrame] = None):
        X = X.copy()
        self._fit_scaler(X)
        Xn = self._norm(X.values).astype(np.float32)
        feat_dim = Xn.shape[1]

        cond = None
        if cond_df is not None and len(cond_df) == len(X):
            cond = np.nan_to_num(cond_df.values.astype(np.float32))
            self.cond_dim = cond.shape[1]
        else:
            self.cond_dim = 0

        in_dim = feat_dim + (self.cond_dim if self.cond_dim > 0 else 0)
        hidden = int(self.cfg.get("hidden", 256))
        # ★ 输出维度 = feat_dim（只预测特征噪声）
        self.model = _MLP(in_dim=in_dim, out_dim=feat_dim, hidden=hidden).to(self.device)

        epochs = int(self.cfg.get("epochs", 8))
        batch_size = int(self.cfg.get("batch_size", 512))
        lr = float(self.cfg.get("lr", 1e-3))
        steps = int(self.cfg.get("steps", 600))

        # 几何序列噪声（大→小）
        self.noise_levels = np.geomspace(1.0, 0.01, num=steps).astype(np.float32)

        n = Xn.shape[0]
        sigma_idx = np.random.randint(0, len(self.noise_levels), size=n)
        sigma = self.noise_levels[sigma_idx][:, None]
        eps = np.random.randn(*Xn.shape).astype(np.float32)   # ★ 目标仅 feat_dim

        X_noisy = Xn + sigma * eps

        # 条件拼接 + classifier-free（随机脱离）
        if cond is not None:
            p = float(self.cfg.get("cond_drop_p", 0.2))
            mask = (np.random.rand(n, 1) > p).astype(np.float32)
            c_in = cond * mask
            X_in = np.concatenate([X_noisy, c_in], axis=1).astype(np.float32)
        else:
            X_in = X_noisy.astype(np.float32)

        ds = TensorDataset(_to_tensor(X_in, self.device), _to_tensor(eps, self.device))
        dl = DataLoader(ds, batch_size=batch_size, shuffle=True, drop_last=False)

        opt = torch.optim.Adam(self.model.parameters(), lr=lr)
        loss_fn = nn.MSELoss()

        self.model.train()
        for _ in range(epochs):
            for xb, yb in dl:
                pred = self.model(xb)          # [B, feat_dim]
                loss = loss_fn(pred, yb)       # yb: [B, feat_dim]
                opt.zero_grad(); loss.backward(); opt.step()

    @torch.no_grad()
    def sample_edit(self, base_X: pd.DataFrame, cond_df: Optional[pd.DataFrame],
                    n_samples: int, guidance_scale: float = 1.3, edit_last_steps: int = 80) -> pd.DataFrame:
        """
        从 base_X 中随机抽样 n_samples 行，添加噪声后只在最后 edit_last_steps 反向去噪。
        """
        assert self.model is not None and self.scaler_mean is not None, "Call fit() first."
        base = base_X.sample(n=n_samples, replace=True, random_state=42).reset_index(drop=True)
        Xn = self._norm(base.values).astype(np.float32)
        steps = len(self.noise_levels)
        # 起点：带噪的真实样本
        x = Xn + self.noise_levels[0] * np.random.randn(*Xn.shape).astype(np.float32)

        # 条件
        if cond_df is not None and len(cond_df) == len(base_X):
            cond_full = np.nan_to_num(cond_df.values.astype(np.float32))
            cond_sel = cond_full[np.random.randint(0, len(cond_full), size=n_samples)]
            cond_sel = cond_sel * guidance_scale
        else:
            cond_sel = None

        self.model.eval()
        start = max(0, steps - int(edit_last_steps))
        for t in range(start, steps):
            sigma = self.noise_levels[t]
            # 拼条件
            if cond_sel is not None:
                x_in = np.concatenate([x, cond_sel], axis=1)
            else:
                x_in = x
            eps_pred = self.model(_to_tensor(x_in, self.device)).cpu().numpy()  # [B, feat_dim]
            x = x - sigma * eps_pred

        X_out = self._denorm(x)
        return pd.DataFrame(X_out, columns=base_X.columns)