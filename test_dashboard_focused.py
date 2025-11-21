# -*- coding: utf-8 -*-
"""
FOCUSED TEST - Dashboard & Logging Validation

This test will show us EXACTLY what's happening:
1. Whether logs appear during optimization
2. Whether dashboard updates live
3. Whether encoding works properly
"""

import asyncio
import sys
from pathlib import Path
import time

# Fix Windows encoding FIRST
if sys.platform == 'win32':
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timedelta
from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators
from src.strategies import registry
from src.optimization import (
    GeneticOptimizer,
    ParameterSpace,
    OptimizationPresets,
    CommonParameterSpaces,
)


async def main():
    """Focused test to validate dashboard and logging."""
    
    print("\n" + "="*80)
    print("FOCUSED TEST - Dashboard & Logging Validation")
    print("="*80)
    print()
    print("This test will show:")
    print("  1. ? Whether logs appear DURING optimization (should be NONE)")
    print("  2. ? Whether dashboard updates LIVE (should see progress)")
    print("  3. ? Whether encoding works (no Unicode errors)")
    print()
    print("Watch carefully - dashboard should update smoothly without logs!")
    print()
    input("Press ENTER to start... ")
    print()
    
    # Fetch minimal data (fast test)
    print("?? Fetching data (cached - should be instant)...")
    dm = DataManager()
    
    df = await dm.fetch_historical(
        symbol="BTC/USDT",
        timeframe="1h",
        start_date=datetime.now() - timedelta(days=180),
        end_date=datetime.now(),
        max_candles=2000,  # Smaller dataset for faster test
    )
    
    await dm.close()
    print(f"? Fetched {len(df)} candles\n")
    
    # Setup strategy
    print("?? Loading strategy...")
    strategy = registry.get("rsi")
    
    # Calculate indicators
    print("?? Calculating indicators...")
    required = strategy.get_required_indicators()
    df = calculate_all_indicators(df, required)
    print("? Indicators ready\n")
    
    # Define parameter space
    print("?? Defining parameter space...")
    param_space = CommonParameterSpaces.rsi_strategy()
    print(f"? {len(param_space)} parameters\n")
    
    # Create optimizer with MINIMAL config (faster test)
    print("?? Initializing optimizer...")
    config = OptimizationPresets.quick_test()
    config.population_size = 10  # Even smaller!
    config.n_generations = 3     # Only 3 generations
    
    optimizer = GeneticOptimizer(
        df=df,
        strategy_class=strategy,
        param_space=param_space,
        config=config,
    )
    
    print(f"? Config: {config.population_size} pop, {config.n_generations} gen\n")
    
    print("="*80)
    print("?? STARTING OPTIMIZATION - WATCH FOR LOGS!")
    print("="*80)
    print()
    print("??  If you see LOGS during optimization = PROBLEM")
    print("? If you see ONLY dashboard updates = SUCCESS")
    print()
    time.sleep(2)  # Give you time to read
    
    # Run optimization
    results = optimizer.optimize()
    
    print()
    print("="*80)
    print("? OPTIMIZATION COMPLETE - VALIDATION RESULTS")
    print("="*80)
    print()
    
    # Show results
    print(f"Best Parameters:")
    for key, value in results["best_params"].items():
        print(f"   {key}: {value}")
    
    print()
    print(f"Best Fitness:")
    print(f"   Sharpe: {results['best_fitness']['sharpe_ratio']:.2f}")
    print(f"   Win Rate: {results['best_fitness']['win_rate']:.1f}%")
    print(f"   Max DD: {results['best_fitness']['max_drawdown_pct']:.1f}%")
    
    print()
    print(f"Performance:")
    print(f"   Time: {results['total_time']:.1f}s")
    print(f"   Evaluations: {results['total_evaluations']}")
    print(f"   Speed: {results['total_evaluations']/results['total_time']:.1f} evals/s")
    
    print()
    print("="*80)
    print("VALIDATION CHECKLIST")
    print("="*80)
    print()
    print("Did you see:")
    print("  [ ] Dashboard with colored progress bars?")
    print("  [ ] Live updates during optimization?")
    print("  [ ] ZERO logs during optimization?")
    print("  [ ] Only final summary logs after?")
    print("  [ ] No Unicode/encoding errors?")
    print()
    print("If ALL boxes are ? = PERFECT!")
    print("If ANY box is ? = Tell me which one")
    print()


if __name__ == "__main__":
    asyncio.run(main())
