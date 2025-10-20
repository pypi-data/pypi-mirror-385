# tests/test_metrics_edges.py
import numpy as np
from findiff.metrics import compute_eval_metrics

def test_metrics_edge_zero_vol():
    r = np.zeros(20, dtype=float)
    met = compute_eval_metrics(r, ["sharpe","calmar","vol","var","sharpe_p5"], ann=252, prefix="")
    for key in ["sharpe","calmar","vol","var","sharpe_p5"]:
        assert key in met  # 不报错即可