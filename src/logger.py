import logging
import sys
from pathlib import Path

from src.config import settings

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Define log format
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str) -> logging.Logger:
    """Setup and return a logger instance.

    Args:
        name: Logger name (usually __name__ of the module)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if logger.handlers:
        return logger

    # Set log level based on environment
    if settings.ENVIRONMENT == "development":
        logger.setLevel(logging.DEBUG)
    elif settings.ENVIRONMENT == "staging":
        logger.setLevel(logging.INFO)
    else:  # production
        logger.setLevel(logging.WARNING)

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (all logs)
    file_handler = logging.FileHandler(LOGS_DIR / "app.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Error file handler (errors only)
    error_handler = logging.FileHandler(LOGS_DIR / "error.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger instance.

    Args:
        name: Logger name (usually __name__ of the module)

    Returns:
        Logger instance

    Usage:
        from src.logger import get_logger

        logger = get_logger(__name__)
        logger.info("Hello world")
    """
    return setup_logger(name)


# Create a default logger for quick access
logger = get_logger("app")
