import os
import logging
from unittest import mock
import pytest
from grammar_checker.logger import get_logger
from logging.handlers import RotatingFileHandler


@pytest.fixture(autouse=True)
def clean_logger_handlers():
    # Runs before and after each test to clear handlers and filters to avoid cross-test contamination
    yield
    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.filters.clear()
        logger.setLevel(logging.NOTSET)
        logger.propagate = True
        

def test_get_logger_returns_logger_instance():
    logger = get_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"


# Tests three different scenarios for the DEBUG environment variable
@pytest.mark.parametrize("debug_value,expected_level", [
    ("true", logging.DEBUG),
    ("false", logging.INFO),
    ("", logging.INFO),
])
def test_logger_level_set_by_debug_env(monkeypatch, debug_value, expected_level):
    monkeypatch.setenv("DEBUG", debug_value)
    logger_name = f"test_logger_{debug_value or 'empty'}"
    logger = get_logger(logger_name)
    assert logger.getEffectiveLevel() == expected_level


def test_logger_has_rotating_file_and_stream_handlers():
    logger = get_logger("handler_logger")
    handler_types = {type(h) for h in logger.handlers}
    assert RotatingFileHandler in handler_types
    assert logging.StreamHandler in handler_types


def test_logger_formatter_is_set():
    logger = get_logger("formatter_logger")
    for handler in logger.handlers:
        assert handler.formatter is not None
        fmt = handler.formatter._fmt
        assert "%(asctime)s" in fmt
        assert "%(levelname)s" in fmt
        assert "%(name)s" in fmt
        assert "%(message)s" in fmt


def test_logger_no_duplicate_handlers():
    logger = get_logger("dup_logger")
    initial_handlers = list(logger.handlers)
    logger2 = get_logger("dup_logger")
    # Should not add more handlers
    assert logger.handlers == initial_handlers


def test_logger_file_handler_uses_config(monkeypatch):
    # Patch config values to test
    monkeypatch.setattr("grammar_checker.logger.LOG_FILE", "test.log")
    monkeypatch.setattr("grammar_checker.logger.MAX_LOG_SIZE", 12345)
    monkeypatch.setattr("grammar_checker.logger.BACKUP_COUNT", 7)

    logger = get_logger("config_logger")
    file_handlers = [h for h in logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
    assert file_handlers

    handler = file_handlers[0]
    assert handler.baseFilename.endswith("test.log")
    assert handler.maxBytes == 12345
    assert handler.backupCount == 7
