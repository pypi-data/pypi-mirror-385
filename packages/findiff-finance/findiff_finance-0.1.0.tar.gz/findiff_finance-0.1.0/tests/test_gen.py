# tests/test_gen.py
import numpy as np
import pandas as pd
from findiff.gen import DDPMGenerator

def _toy_df(n=128, f=4):
    rng = np.random.default_rng(0)
    X = rng.normal(size=(n, f)).astype(np.float32)
    y = rng.normal(scale=0.01, size=(n,)).astype(np.float32)
    df = pd.DataFrame(X, columns=[f"f{i}" for i in range(f)])
    df["y"] = y
    df["t"] = np.arange(n)
    return df

def test_ddpm_fit_sample_with_cond():
    df = _toy_df()
    X = df[["f0","f1","f2","f3"]]
    cond = pd.DataFrame({"trend": np.tanh(df["y"]).values, "vol": np.abs(df["y"]).values})
    gen = DDPMGenerator({"epochs":1, "steps":12, "edit_last_steps":5, "batch_size":64, "cond_drop_p":0.0})
    gen.fit(X, cond)
    out = gen.sample_edit(X, cond, n_samples=32, guidance_scale=1.2, edit_last_steps=5)
    assert out.shape == (32, X.shape[1])
    assert np.isfinite(out.values).all()

def test_ddpm_fit_sample_no_cond():
    df = _toy_df()
    X = df[["f0","f1","f2","f3"]]
    gen = DDPMGenerator({"epochs":1, "steps":10, "edit_last_steps":4, "batch_size":64})
    gen.fit(X, None)
    out = gen.sample_edit(X, None, n_samples=16)
    assert out.shape == (16, X.shape[1])