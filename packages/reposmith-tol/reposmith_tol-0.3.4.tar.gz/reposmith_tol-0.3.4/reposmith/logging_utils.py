from __future__ import annotations

import logging
import os
from typing import Optional

from .console import enable_utf8_console, sanitize_text, maybe_strip_emoji

class SafeStreamHandler(logging.StreamHandler):
    """
    Logging handler that ensures encoding-safe output.

    The message is passed through `maybe_strip_emoji` and `sanitize_text`
    before being written to the output stream.
    """
    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            msg = maybe_strip_emoji(msg)
            msg = sanitize_text(msg)
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)

def _level_from_str(level: str) -> int:
    """
    Convert string log level to logging module constant.

    Args:
        level (str): Log level as string (e.g., "INFO").

    Returns:
        int: Corresponding logging level constant.
    """
    level = (level or "INFO").upper()
    return getattr(logging, level, logging.INFO)

def setup_logging(level: str = "INFO", no_emoji: bool = False, logger_name: Optional[str] = None) -> logging.Logger:
    """
    Configure and return a logger for CLI use.

    Args:
        level (str): Logging level (e.g., "DEBUG", "INFO").
        no_emoji (bool): Disable emojis if True.
        logger_name (Optional[str]): Optional custom logger name.

    Returns:
        logging.Logger: Configured logger instance.
    """
    enable_utf8_console()
    if no_emoji:
        os.environ["REPOSMITH_NO_EMOJI"] = "1"

    logger = logging.getLogger(logger_name or "reposmith")
    logger.setLevel(_level_from_str(level))
    logger.propagate = False

    # Remove existing handlers to prevent duplication (e.g., during tests)
    for h in list(logger.handlers):
        logger.removeHandler(h)

    handler = SafeStreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(handler)

    # Reduce verbosity of other libraries
    logging.getLogger().setLevel(logging.WARNING)

    return logger