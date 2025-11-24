#!/usr/bin/env python
"""
Test script for optimization with FAST MODE (avoid timeout)
"""

import asyncio
import sys
import os

# ? FORCE MCP MODE (disable Rich dashboard)
os.environ['SMART_TRADE_MCP_MODE'] = 'true'

# ? FORCE TEST MODE (disable log rotation)
os.environ['SMART_TRADE_TEST_MODE'] = 'true'

sys.path.insert(0, '.')

from datetime import datetime, timedelta
from src.strategies.registry import registry
from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators
from src.optimization.genetic_optimizer import GeneticOptimizer
from src.optimization.config import OptimizationConfig
from src.optimization.meta_learner import ParameterMetaLearner
from src.optimization.parameter_space import ParameterSpace, ParameterDefinition, ParameterType


async def test_fast_optimization():
    """Test FAST optimization mode (should complete in ~1 min)"""
    
    print("\n" + "="*80)
    print("? TESTING FAST OPTIMIZATION MODE (pop=10, gen=5)")
    print("="*80 + "\n")
    
    # Configuration
    strategy_name = "cci_extreme_snapback"
    symbol = "BTC/USDT"
    timeframe = "1h"
    
    # FAST MODE
    population_size = 10
    n_generations = 5
    
    print(f"?? Strategy: {strategy_name}")
    print(f"?? Symbol: {symbol} / {timeframe}")
    print(f"? FAST MODE: Population {population_size}, Generations {n_generations}")
    print(f"??  Expected time: ~60 seconds")
    print()
    
    import time
    start_time = time.time()
    
    # 1. Get strategy
    print("1?? Loading strategy...")
    strategy = registry.get(strategy_name)
    print(f"   ? Loaded: {strategy.__class__.__name__}")
    print()
    
    # 2. Fetch data
    print("2?? Fetching market data...")
    dm = DataManager()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # 3 months
    
    df = await dm.fetch_historical(
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        max_candles=2000,
    )
    
    await dm.close()
    
    print(f"   ? Fetched {len(df)} candles")
    print()
    
    # 3. Calculate indicators
    print("3?? Calculating indicators...")
    required = strategy.get_required_indicators()
    df = calculate_all_indicators(df, required, use_gpu=False)
    print(f"   ? Indicators ready")
    print()
    
    # 4. Meta-Learner
    print("4?? Using Meta-Learner...")
    meta_learner = ParameterMetaLearner()
    
    smart_ranges = meta_learner.get_smart_ranges(
        strategy_name=strategy_name,
        df=df,
        lookback=100
    )
    
    print(f"   ? SMART ranges: {len(smart_ranges)} parameters")
    print()
    
    # 5. Create parameter space
    param_definitions = {}
    for param_name, (min_val, max_val) in smart_ranges.items():
        if isinstance(min_val, int) and isinstance(max_val, int):
            param_type = ParameterType.INT
        else:
            param_type = ParameterType.FLOAT
        
        param_definitions[param_name] = ParameterDefinition(
            name=param_name,
            type=param_type,
            low=min_val,
            high=max_val,
            description=f"Range for {param_name}"
        )
    
    param_space = ParameterSpace(
        parameters=param_definitions,
        strategy_name=strategy_name
    )
    
    # 6. Progress tracking
    print("5?? Starting FAST optimization...")
    print()
    
    progress_log = []
    
    def progress_callback(generation: int, stats: dict):
        progress_log.append(stats)
        print(f"   ? Gen {generation}/{n_generations}: "
              f"Best Sharpe={stats['best_fitness']['sharpe_ratio']:.2f}, "
              f"Avg Sharpe={stats['avg_fitness']['sharpe_ratio']:.2f}")
    
    # 7. Optimize
    config = OptimizationConfig(
        population_size=population_size,
        n_generations=n_generations,
        use_ray=False,
        use_gpu=False,
    )
    
    optimizer = GeneticOptimizer(
        df=df,
        strategy_class=strategy,
        param_space=param_space,
        config=config,
        use_smart_ranges=False,
        progress_callback=progress_callback,
    )
    
    results = optimizer.optimize()
    
    elapsed = time.time() - start_time
    
    print()
    print("="*80)
    print("? FAST OPTIMIZATION COMPLETE!")
    print("="*80)
    print()
    print(f"??  Total Time: {elapsed:.1f}s")
    print(f"?? Best Sharpe: {results['best_fitness']['sharpe_ratio']:.2f}")
    print(f"?? Win Rate: {results['best_fitness']['win_rate']:.1f}%")
    print(f"?? Evaluations: {results['total_evaluations']}")
    print()
    
    # Verify it was under 2 minutes
    if elapsed < 120:
        print(f"? SUCCESS! Completed in {elapsed:.1f}s (< 2 min)")
    else:
        print(f"?? WARNING! Took {elapsed:.1f}s (> 2 min) - may timeout in Claude")
    
    print()


if __name__ == "__main__":
    asyncio.run(test_fast_optimization())
