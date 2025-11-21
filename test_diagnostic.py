# -*- coding: utf-8 -*-
"""
DIAGNOSTIC TEST - Find the exact problem

This will test each component separately to identify the issue.
"""

import sys
import os
import logging

# Fix encoding FIRST
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

print("\n" + "="*80)
print("DIAGNOSTIC TEST - Component by Component")
print("="*80)
print()

# TEST 1: Rich library
print("TEST 1: Rich Library")
print("-"*80)
try:
    from rich.console import Console
    from rich.progress import Progress, BarColumn, TextColumn
    from rich.panel import Panel
    from rich.text import Text
    
    console = Console(force_terminal=True, legacy_windows=False)
    
    # Try to render something simple
    console.print(Panel(Text("? Rich library works!", style="bold green")))
    print("? Rich library: OK")
except Exception as e:
    print(f"? Rich library FAILED: {e}")
print()

# TEST 2: Rich Live Dashboard
print("TEST 2: Rich Live Updates")
print("-"*80)
try:
    from rich.live import Live
    import time
    
    panel = Panel(Text("Testing Live Updates...", style="cyan"), title="?? Test")
    
    with Live(panel, console=console, refresh_per_second=2) as live:
        for i in range(5):
            panel = Panel(Text(f"Update {i+1}/5", style="cyan"), title="?? Test")
            live.update(panel)
            time.sleep(0.5)
    
    print("? Rich Live: OK")
except Exception as e:
    print(f"? Rich Live FAILED: {e}")
    import traceback
    traceback.print_exc()
print()

# TEST 3: Logging Suppression
print("TEST 3: Logging Suppression")
print("-"*80)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
test_logger = logging.getLogger("test")

print("Before suppression (you should see this log):")
test_logger.info("This log SHOULD appear")

print("\nDuring suppression (you should NOT see logs):")
sys.path.insert(0, os.path.dirname(__file__))

try:
    from src.optimization.logging_utils import silence_all_logging
    
    with silence_all_logging():
        test_logger.info("This log should NOT appear")
        logging.getLogger("src.core.backtest_engine").info("Backtest log should NOT appear")
        print("  [If you see logs above this line = PROBLEM]")
    
    print("\nAfter suppression (logs should appear again):")
    test_logger.info("This log SHOULD appear again")
    print("? Logging suppression: OK")
    
except Exception as e:
    print(f"? Logging suppression FAILED: {e}")
    import traceback
    traceback.print_exc()
print()

# TEST 4: Dashboard CLI
print("TEST 4: Dashboard CLI Component")
print("-"*80)
try:
    from src.core.cli_dashboard import OptimizationDashboard
    
    dashboard = OptimizationDashboard(
        population_size=10,
        n_generations=3,
        n_gpus=0,
        strategy_name="TestStrategy"
    )
    
    dashboard.start()
    
    # Simulate a generation
    dashboard.update_generation(1, 10)
    
    best = {"sharpe_ratio": 0.5, "win_rate": 45.0, "max_drawdown": -10.0}
    avg = {"sharpe_ratio": 0.3, "win_rate": 40.0, "max_drawdown": -15.0}
    
    dashboard.complete_generation(best, avg)
    
    # Render
    renderable = dashboard.render()
    console.print(renderable)
    
    print("? Dashboard CLI: OK")
    
except Exception as e:
    print(f"? Dashboard CLI FAILED: {e}")
    import traceback
    traceback.print_exc()
print()

# TEST 5: Full Integration (Short)
print("TEST 5: Full Integration (Minimal)")
print("-"*80)
try:
    from src.core.cli_dashboard import OptimizationDashboard
    from src.optimization.logging_utils import silence_all_logging
    from rich.live import Live
    import time
    
    dashboard = OptimizationDashboard(
        population_size=5,
        n_generations=2,
        n_gpus=0,
        strategy_name="IntegrationTest"
    )
    
    dashboard.start()
    
    print("Starting Live dashboard with logging suppression...")
    print("(Watch for logs - there should be NONE)")
    print()
    
    with silence_all_logging():
        with Live(dashboard.render(), console=console, refresh_per_second=2) as live:
            for gen in range(1, 3):
                # Simulate work
                for i in range(5):
                    # These logs should NOT appear
                    test_logger.info(f"Gen {gen} - Eval {i} - THIS SHOULD BE HIDDEN")
                    time.sleep(0.1)
                
                dashboard.update_generation(gen, 5)
                
                best = {"sharpe_ratio": 0.5 + gen*0.1, "win_rate": 45.0, "max_drawdown": -10.0}
                avg = {"sharpe_ratio": 0.3, "win_rate": 40.0, "max_drawdown": -15.0}
                
                dashboard.complete_generation(best, avg)
                live.update(dashboard.render())
    
    print("\n? Full Integration: OK")
    
except Exception as e:
    print(f"\n? Full Integration FAILED: {e}")
    import traceback
    traceback.print_exc()
print()

print("="*80)
print("DIAGNOSTIC SUMMARY")
print("="*80)
print()
print("If ALL tests passed (?), the problem is elsewhere.")
print("If ANY test failed (?), that's what we need to fix!")
print()
