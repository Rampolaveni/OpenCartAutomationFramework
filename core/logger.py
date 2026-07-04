# core/logger.py

# ============================================================================
# LOGGER MODULE
# ============================================================================
# Provides a single, session-scoped logger for the entire framework.
#
# Features:
# 1. One timestamped log file per test session (never overwritten)
# 2. Rotating file handler — max 10MB per file, keeps last 5
# 3. Log level driven by LOG_LEVEL environment variable (default: DEBUG)
# 4. Console shows INFO+, file captures DEBUG+
# 5. get_session_log_file() exposes log path for Allure attachment
# ============================================================================

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────────────────────
PROJECT_ROOT  = Path(__file__).resolve().parent.parent
LOGS_DIR      = PROJECT_ROOT / "reports" / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION-LEVEL CONSTANTS
# Evaluated once at import time — same values for entire test session
# ─────────────────────────────────────────────────────────────────────────────
_SESSION_LOG_FILE = LOGS_DIR / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
_LOG_LEVEL        = getattr(logging, os.getenv("LOG_LEVEL", "DEBUG").upper(), logging.DEBUG)


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────
def get_logger(name: str) -> logging.Logger:
    """
    Returns a named logger configured with file + console handlers.
    Safe to call multiple times — handlers are only added once per logger.

    Usage:
        from core.logger import get_logger
        log = get_logger(__name__)
        log.info("Something happened")
    """
    logger = logging.getLogger(name)

    # Guard: if handlers already attached, return as-is (avoid duplicates)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False    # prevent messages bubbling to root logger

    # ── Formatters ────────────────────────────────────────────────────────────
    file_fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    )

    # ── File Handler (DEBUG+, rotating) ───────────────────────────────────────
    file_handler = RotatingFileHandler(
        _SESSION_LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_fmt)

    # ── Console Handler (INFO+) ───────────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_session_log_file() -> Path:
    """
    Returns the current session log file path.
    Used by conftest.py to attach logs to Allure report on test failure.
    """
    return _SESSION_LOG_FILE