"""Logging utilities for jupyter2hugo."""

import logging
from typing import Optional


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with consistent formatting.

    Args:
        name: Logger name
        level: Logging level

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (defaults to 'jupyter2hugo')

    Returns:
        Logger instance
    """
    if name is None:
        name = 'jupyter2hugo'
    return logging.getLogger(name)
