# -*- coding: utf-8 -*-
"""
Test logging suppression during optimization.

This test will help identify any remaining log leaks.
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.optimization.logging_utils import silence_all_logging
from rich.live import Live
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import time

console = Console()

def noisy_function():
    """Function that generates lots of logs."""
    logger = logging.getLogger("test")
    logger.info("This should NOT appear during silence!")
    
    # Try different loggers
    logging.getLogger("src.core.backtest_engine").info("Backtest log - should be silent!")
    logging.getLogger("src.strategies.base").info("Strategy log - should be silent!")
    logging.getLogger("src.optimization").info("Optimization log - should be silent!")


def test_logging_suppression():
    """Test that ALL logging is suppressed."""
    
    print("\n" + "="*80)
    print("LOGGING SUPPRESSION TEST")
    print("="*80)
    print()
    
    # Configure logging first
    logging.basicConfig(level=logging.INFO)
    
    print("1. Testing BEFORE suppression (logs should appear):")
    print("-" * 80)
    noisy_function()
    print()
    
    print("2. Testing DURING suppression (NO logs should appear):")
    print("-" * 80)
    
    with silence_all_logging():
        # Create a simple live display
        panel = Panel(
            Text("Dashboard is updating...\nNo logs should interfere!", style="bold green"),
            title="?? Live Dashboard",
            border_style="cyan"
        )
        
        with Live(panel, console=console, refresh_per_second=4) as live:
            for i in range(10):
                # Generate LOTS of logs
                noisy_function()
                
                # Update display
                panel = Panel(
                    Text(f"Update {i+1}/10\nNo logs should interfere!", style="bold green"),
                    title="?? Live Dashboard",
                    border_style="cyan"
                )
                live.update(panel)
                time.sleep(0.2)
    
    print()
    print("3. Testing AFTER suppression (logs should appear again):")
    print("-" * 80)
    noisy_function()
    print()
    
    print("="*80)
    print("? TEST COMPLETE")
    print("If you saw logs during step 2, there's a leak!")
    print("="*80)
    print()


if __name__ == "__main__":
    test_logging_suppression()
