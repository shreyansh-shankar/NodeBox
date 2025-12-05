"""
Centralized logging for NodeBox.

Sets up file and console logging with rotation to keep logs manageable.
Logs go to ~/.nodebox/logs/nodebox.log
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from utils.paths import LOGS_DIR

# Make sure logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_DIR / "nodebox.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(
    name: str = "nodebox",
    level: int = logging.INFO,
    log_to_file: bool = True,
    log_to_console: bool = True,
) -> logging.Logger:
    """
    Set up a logger with file and console output.

    Args:
        name: Logger name (default "nodebox")
        level: Log level (default INFO)
        log_to_file: Write to log file (default True)
        log_to_console: Write to console (default True)

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear any existing handlers
    logger.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # File logging with rotation (10MB max, keeps 5 old files)
    if log_to_file:
        try:
            file_handler = RotatingFileHandler(
                LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not setup file logging: {e}", file=sys.stderr)

    # Console logging
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def get_logger(name: str = "nodebox") -> logging.Logger:
    """
    Get an existing logger or create a new one.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """

    Args:
        name: Name of the logger

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Setup with default configuration if not already configured
        return setup_logger(name)
    return logger


# Default logger
app_logger = setup_logger("nodebox")


def log_exception(logger: logging.Logger, exc: Exception, message: str = ""):
    """
    Log an exception with traceback.
    
    Args:
        logger: Logger to use
        exc: The exception
        message: Extra context (optional)
    """
    if message:
        logger.exception(f"{message}: {exc}")
    else:
        logger.exception(f"Exception occurred: {exc}")
