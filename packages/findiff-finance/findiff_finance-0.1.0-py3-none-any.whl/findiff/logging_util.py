# src/findiff/logging_util.py
import logging
import os
from typing import Optional

def get_logger(name: str = "findiff", level: Optional[str] = None) -> logging.Logger:
    """
    统一日志入口：默认 INFO；可通过环境变量 FINDIFF_LOGLEVEL 覆盖（DEBUG/INFO/WARN/ERROR）。
    """
    lvl = (level or os.getenv("FINDIFF_LOGLEVEL") or "INFO").upper()
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s",
                                datefmt="%H:%M:%S")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, lvl, logging.INFO))
    logger.propagate = False
    return logger