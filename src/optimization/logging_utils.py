# -*- coding: utf-8 -*-
"""
Logging utilities for optimization.

Provides context managers to temporarily silence logging during optimization
to prevent interference with Rich CLI dashboards.
"""

import logging
import sys
from contextlib import contextmanager
from typing import Generator, List, Dict


@contextmanager
def silence_all_logging() -> Generator[None, None, None]:
    """
    Context manager to COMPLETELY silence ALL logging and stdout/stderr.
    
    This is NUCLEAR OPTION - silences everything to ensure Rich Live
    dashboard updates without any interference.
    
    Usage:
        with silence_all_logging():
            # All logging AND print statements are suppressed here
            run_noisy_operation()
        # Everything is restored here
    """
    # Save original levels for ALL loggers
    root_logger = logging.getLogger()
    original_root_level = root_logger.level
    original_root_handlers = root_logger.handlers.copy()
    
    # Get all existing loggers
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    original_levels: Dict[str, int] = {}
    original_handlers: Dict[str, List] = {}
    
    for logger in loggers:
        if isinstance(logger, logging.Logger):
            original_levels[logger.name] = logger.level
            original_handlers[logger.name] = logger.handlers.copy()
    
    # Redirect stdout/stderr to devnull (captures print statements too!)
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    devnull = open('/dev/null' if sys.platform != 'win32' else 'nul', 'w')
    
    try:
        # NUCLEAR OPTION: Remove ALL handlers from root logger
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Set root logger to highest level (silence everything)
        root_logger.setLevel(logging.CRITICAL + 100)
        
        # Silence all child loggers AND remove their handlers
        for logger in loggers:
            if isinstance(logger, logging.Logger):
                # Remove all handlers
                for handler in logger.handlers[:]:
                    logger.removeHandler(handler)
                
                # Set to max level
                logger.setLevel(logging.CRITICAL + 100)
                
                # Disable propagation
                logger.propagate = False
        
        # Redirect stdout/stderr (catches print statements)
        sys.stdout = devnull
        sys.stderr = devnull
        
        yield
    
    finally:
        # Restore stdout/stderr FIRST
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        devnull.close()
        
        # Restore root logger
        root_logger.setLevel(original_root_level)
        
        # Restore root handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        for handler in original_root_handlers:
            root_logger.addHandler(handler)
        
        # Restore all child loggers
        for logger in loggers:
            if isinstance(logger, logging.Logger):
                # Restore level
                if logger.name in original_levels:
                    logger.setLevel(original_levels[logger.name])
                
                # Restore handlers
                if logger.name in original_handlers:
                    for handler in logger.handlers[:]:
                        logger.removeHandler(handler)
                    for handler in original_handlers[logger.name]:
                        logger.addHandler(handler)
                
                # Restore propagation
                logger.propagate = True


__all__ = ["silence_all_logging"]
