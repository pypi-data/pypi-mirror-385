# tests/test_metrics.py
import numpy as np
from findiff.metrics import compute_eval_metrics

def test_metrics_shapes_and_values():
    # 构造有波动、有均值的收益序列
    r = np.array([0.01, -0.005, 0.007, -0.003, 0.004, 0.006, -0.002, 0.005], dtype=float)
    met = compute_eval_metrics(r, ["sharpe","calmar","vol","var","sharpe_p5"], ann=252, prefix="")
    # 基本键存在
    for k in ["sharpe","calmar","vol","var","sharpe_p5"]:
        assert k in met
    # var ~ vol^2 （自由度差异允许一点误差）
    assert np.isfinite(met["var"])
    assert abs(met["var"] - (np.std(r, ddof=1)**2)) < 1e-12 + 1e-6