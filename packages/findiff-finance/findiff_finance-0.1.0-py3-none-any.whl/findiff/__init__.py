# src/findiff/__init__.py
from .version import __version__
from .config import default_cfg, deep_update, get_splits
from .pipeline import FinDiff, FinDiffResult
from .train import TorchTimeSeriesRegressor, fit_and_eval
from .plotting import (
    plot_cv_sharpe_bars,
    plot_test_nav_from_returns,
    compare_feature_hist,
    plot_psi_heatmap,
)

__all__ = [
    "__version__",
    "default_cfg", "deep_update", "get_splits",
    "FinDiff", "FinDiffResult",
    "TorchTimeSeriesRegressor", "fit_and_eval",
    "plot_cv_sharpe_bars", "plot_test_nav_from_returns",
    "compare_feature_hist", "plot_psi_heatmap",
]