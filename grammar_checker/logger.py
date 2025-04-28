# grammar_checker/logger.py

import os
import logging
from logging.handlers import RotatingFileHandler
from grammar_checker.config import LOG_FILE, MAX_LOG_SIZE, BACKUP_COUNT


def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger with rotating file and console handlers."""
    logger = logging.getLogger(name)
    
    # Set the logging level based on the DEBUG environment variable
    debug_mode = os.getenv("DEBUG", "False").lower() == "true"
    level = logging.DEBUG if debug_mode else logging.INFO
    logger.setLevel(level)

    # Prevent duplicate handlers if get_logger is called multiple times
    if not logger.handlers:

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )

        # Rotating file handler
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT
        )
        file_handler.setFormatter(formatter)

        # Stream (console) handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        # Attach handlers
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
