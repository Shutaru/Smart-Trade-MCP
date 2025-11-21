# -*- coding: utf-8 -*-
"""
Rich Dashboard Context Manager

Silences loguru logs while Rich dashboards are active.
"""

import sys
from contextlib import contextmanager
from loguru import logger
from rich.console import Console


@contextmanager
def silent_logs():
    """
    Context manager to temporarily silence loguru logs.
    
    Usage:
        with silent_logs():
            # Code that uses Rich dashboards
            # Logs won't interfere
            pass
    """
    # Remove all handlers
    logger_ids = []
    for handler_id in logger._core.handlers.copy():
        logger_ids.append(handler_id)
        logger.remove(handler_id)
    
    try:
        yield
    finally:
        # Re-add default handler
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO",
        )


@contextmanager
def rich_dashboard_mode():
    """
    Context manager for Rich dashboard operations.
    
    Silences logs and provides clean console.
    
    Usage:
        with rich_dashboard_mode() as console:
            # Use console for Rich outputs
            console.print("[bold]Dashboard[/bold]")
    """
    # Silence logs
    logger_ids = []
    for handler_id in logger._core.handlers.copy():
        logger_ids.append(handler_id)
        logger.remove(handler_id)
    
    # Create console
    console = Console()
    
    try:
        yield console
    finally:
        # Re-enable logs
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO",
        )


__all__ = ["silent_logs", "rich_dashboard_mode"]
