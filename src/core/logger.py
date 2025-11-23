"""Logging configuration using Loguru."""

import sys
import os
from pathlib import Path
from typing import Optional

from loguru import logger

from .config import settings


# Global flag to disable logging (set by test scripts)
_LOGGING_DISABLED = os.environ.get('SMART_TRADE_DISABLE_LOGGING', '').lower() == 'true'

# Flag to disable colors (for MCP Server - JSON output must be clean!)
_IS_MCP_SERVER = os.environ.get('SMART_TRADE_MCP_MODE', '').lower() == 'true'

# Flag for test mode (disable rotation to avoid conflicts)
_IS_TEST_MODE = os.environ.get('SMART_TRADE_TEST_MODE', '').lower() == 'true'


def setup_logging(log_file: Optional[Path] = None) -> None:
    """
    Configure logging with Loguru.

    Args:
        log_file: Optional path to log file. Defaults to logs/smart_trade.log
    """
    # If logging is globally disabled, do nothing!
    if _LOGGING_DISABLED:
        logger.remove()  # Remove all handlers
        return
    
    # Remove default handler
    logger.remove()

    # Console handler - NO COLORS for MCP Server!
    if _IS_MCP_SERVER:
        # Plain format for MCP (no ANSI codes)
        logger.add(
            sys.stderr,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=settings.log_level,
            colorize=False,  # CRITICAL: No colors for MCP!
        )
    else:
        # Colored format for CLI
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=settings.log_level,
            colorize=True,
        )

    # File handler (never colored)
    if log_file is None:
        log_file = Path("logs/smart_trade.log")

    log_file.parent.mkdir(parents=True, exist_ok=True)

    # ? FIX: Disable rotation in test mode to avoid file conflicts
    if _IS_TEST_MODE:
        # Test mode: Simple file logging, no rotation
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation=None,  # ? DISABLED
            enqueue=True,  # ? Thread-safe
        )
    else:
        # Production mode: Full rotation
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            enqueue=True,  # ? Thread-safe
        )

    logger.info(f"Logging initialized - Level: {settings.log_level}, MCP Mode: {_IS_MCP_SERVER}, Test Mode: {_IS_TEST_MODE}")


# Initialize on import (unless disabled)
if not _LOGGING_DISABLED:
    setup_logging()

__all__ = ["logger", "setup_logging"]
