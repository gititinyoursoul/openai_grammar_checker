# grammar_checker/logger.py

import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from grammar_checker.config import LOG_FILE, MAX_LOG_SIZE, BACKUP_COUNT
from grammar_checker.config import PROJECT_ROOT


def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger with rotating file and console handlers."""
    logger = logging.getLogger(name)

    # Set the logging level based on the DEBUG environment variable
    if logger.level == logging.NOTSET:
        debug_mode = os.getenv("DEBUG", "False").lower() == "true"
        level = logging.DEBUG if debug_mode else logging.INFO
        logger.setLevel(level)

    # Prevent duplicate handlers if get_logger is called multiple times
    if not logger.handlers:

        # Formatter
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

        # Rotating file handler
        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)
        file_handler.setFormatter(formatter)

        # Stream (console) handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        # Attach handlers
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger


def get_display_path(path: Path, root: Path = PROJECT_ROOT) -> str:
    """
    Returns the path relative to the project root for clean display.
    Falls back to absolute path if not under the root.
    """
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)  # fallback to absolute path
