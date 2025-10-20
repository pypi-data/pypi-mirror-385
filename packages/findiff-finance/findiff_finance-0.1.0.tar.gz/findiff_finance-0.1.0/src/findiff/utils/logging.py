# src/findiff/utils/logging.py
from __future__ import annotations
from typing import Dict, Any
import os, sys, time, random, platform
import numpy as np

def seed_everything(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        try:
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
        except Exception:
            pass
    except Exception:
        pass
    return seed

def get_run_id(prefix: str = "findiff") -> str:
    ts = time.strftime("%Y%m%d-%H%M%S", time.localtime())
    rnd = ("%04x" % random.getrandbits(16))
    return f"{prefix}-{ts}-{rnd}"

def env_summary() -> Dict[str, Any]:
    info = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }
    try:
        import numpy
        info["numpy"] = numpy.__version__
    except Exception:
        pass
    try:
        import pandas
        info["pandas"] = pandas.__version__
    except Exception:
        pass
    try:
        import torch
        info["torch"] = torch.__version__
        info["cuda_available"] = bool(torch.cuda.is_available())
    except Exception:
        pass
    try:
        import sklearn
        info["sklearn"] = sklearn.__version__
    except Exception:
        pass
    return info