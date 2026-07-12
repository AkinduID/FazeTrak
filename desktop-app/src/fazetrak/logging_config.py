"""
Centralized logging setup for FazeTrak.

Every module gets its logger via ``logging.getLogger(__name__)`` as usual;
this module is only responsible for configuring *how* those log records are
formatted and where they go (console + rotating log file). Call
``configure_logging()`` exactly once, as early as possible in the
application's entry point.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fazetrak import config

# Keep at most this many log files (fazetrak.log, fazetrak.log.1, ...).
_MAX_LOG_FILE_BACKUPS = 3
# Rotate the log file once it passes this size.
_MAX_LOG_FILE_BYTES = 2 * 1024 * 1024  # 2 MB


def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure the root logger with a console handler and a rotating file
    handler.

    Args:
        level: The minimum severity that should be logged (e.g. logging.DEBUG
            during development, logging.INFO in normal use).
    """
    log_directory = Path(config.LOG_DIRECTORY)
    log_directory.mkdir(parents=True, exist_ok=True)
    log_file_path = log_directory / config.LOG_FILE_NAME

    formatter = logging.Formatter(config.LOG_FORMAT)

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        filename=log_file_path,
        maxBytes=_MAX_LOG_FILE_BYTES,
        backupCount=_MAX_LOG_FILE_BACKUPS,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    # Avoid duplicate handlers if configure_logging() is ever called twice.
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    logging.getLogger(__name__).info(
        "Logging configured (level=%s, file=%s)",
        logging.getLevelName(level),
        log_file_path,
    )
