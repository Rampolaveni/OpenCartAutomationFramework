# core/logger.py

# ============================================================================
# LOGGER MODULE
# ============================================================================
# Provides a single, session-scoped logger for the entire framework.
#
# Features:
# 1. One timestamped log file per test session
# 2. Rotating file handler — max 10MB per file, keeps last 5
# 3. Log level driven by LOG_LEVEL environment variable
# 4. Console shows INFO+, file captures configured LOG_LEVEL+
# 5. get_session_log_file() exposes log path for Allure attachment
# ============================================================================

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from core.paths import LOGS_DIR, create_report_directories


# ─────────────────────────────────────────────────────────────────────────────
# DIRECTORY SETUP
# ─────────────────────────────────────────────────────────────────────────────

create_report_directories()


# ─────────────────────────────────────────────────────────────────────────────
# SESSION-LEVEL CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

_SESSION_LOG_FILE = LOGS_DIR / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

_LOG_LEVEL = getattr(
    logging,
    os.getenv("LOG_LEVEL", "DEBUG").upper(),
    logging.DEBUG
)


# ─────────────────────────────────────────────────────────────────────────────
# SHARED HANDLERS
# ─────────────────────────────────────────────────────────────────────────────

_FILE_HANDLER = None
_CONSOLE_HANDLER = None


def _get_file_handler():
    global _FILE_HANDLER

    if _FILE_HANDLER:
        return _FILE_HANDLER

    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    _FILE_HANDLER = RotatingFileHandler(
        _SESSION_LOG_FILE,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )

    _FILE_HANDLER.setLevel(_LOG_LEVEL)
    _FILE_HANDLER.setFormatter(file_formatter)

    return _FILE_HANDLER


def _get_console_handler():
    global _CONSOLE_HANDLER

    if _CONSOLE_HANDLER:
        return _CONSOLE_HANDLER

    console_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    )

    _CONSOLE_HANDLER = logging.StreamHandler()
    _CONSOLE_HANDLER.setLevel(logging.INFO)
    _CONSOLE_HANDLER.setFormatter(console_formatter)

    return _CONSOLE_HANDLER


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

def get_logger(name: str) -> logging.Logger:
    """
    Returns a named logger configured with file + console handlers.
    Safe to call multiple times.
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(_LOG_LEVEL)
    logger.propagate = False

    logger.addHandler(_get_file_handler())
    logger.addHandler(_get_console_handler())

    return logger


def get_session_log_file() -> Path:
    """
    Returns current session log file path.
    Used by conftest.py to attach logs to Allure on failure.
    """

    return _SESSION_LOG_FILE