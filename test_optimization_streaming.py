#!/usr/bin/env python
"""
Test script for optimization with streaming progress
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


async def test_optimization():
    """Test optimization with progress streaming"""
    
    print("\n" + "="*80)
    print("?? TESTING OPTIMIZATION WITH STREAMING PROGRESS")
    print("="*80 + "\n")
    
    # Configuration
    strategy_name = "cci_extreme_snapback"
    symbol = "BTC/USDT"
    timeframe = "1h"
    
    # FAST MODE for testing
    population_size = 10  # Small for quick test
    n_generations = 5     # Few generations
    
    print(f"?? Strategy: {strategy_name}")
    print(f"?? Symbol: {symbol} / {timeframe}")
    print(f"?? Population: {population_size}")
    print(f"?? Generations: {n_generations}")
    print()
    
    # 1. Get strategy
    print("1?? Loading strategy...")
    strategy = registry.get(strategy_name)
    print(f"   ? Loaded: {strategy.__class__.__name__}")
    print()
    
    # 2. Fetch data
    print("2?? Fetching market data...")
    dm = DataManager()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # 3 months for quick test
    
    df = await dm.fetch_historical(
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        max_candles=2000,
    )
    
    await dm.close()
    
    print(f"   ? Fetched {len(df)} candles")
    print(f"   ? Date range: {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
    print()
    
    # 3. Calculate indicators
    print("3?? Calculating indicators...")
    required = strategy.get_required_indicators()
    print(f"   Required: {required}")
    df = calculate_all_indicators(df, required, use_gpu=False)
    print(f"   ? Indicators calculated")
    print()
    
    # 4. Get parameter space from Meta-Learner
    print("4?? Using Meta-Learner for parameter ranges...")
    meta_learner = ParameterMetaLearner()
    
    smart_ranges = meta_learner.get_smart_ranges(
        strategy_name=strategy_name,
        df=df,
        lookback=100
    )
    
    print(f"   ? Got SMART ranges for {len(smart_ranges)} parameters:")
    for param, (min_val, max_val) in list(smart_ranges.items())[:3]:
        print(f"      - {param}: [{min_val}, {max_val}]")
    print(f"      ... (showing 3/{len(smart_ranges)})")
    print()
    
    # 5. Create parameter space
    print("5?? Creating parameter space...")
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
    
    print(f"   ? Parameter space created with {len(param_space)} params")
    print()
    
    # 6. Setup progress callback
    print("6?? Setting up progress tracking...")
    
    progress_log = []
    
    def progress_callback(generation: int, stats: dict):
        """Track progress"""
        progress_log.append({
            "generation": generation,
            "best_sharpe": stats["best_fitness"]["sharpe_ratio"],
            "avg_sharpe": stats["avg_fitness"]["sharpe_ratio"],
            "elapsed": stats["elapsed_time"],
        })
        
        print(f"   ? Gen {generation}/{n_generations}: "
              f"Best Sharpe={stats['best_fitness']['sharpe_ratio']:.2f}, "
              f"Avg Sharpe={stats['avg_fitness']['sharpe_ratio']:.2f}, "
              f"Time={stats['gen_time']:.1f}s")
    
    print(f"   ? Progress callback ready")
    print()
    
    # 7. Create optimizer
    print("7?? Creating Genetic Optimizer...")
    config = OptimizationConfig(
        population_size=population_size,
        n_generations=n_generations,
        use_ray=False,  # Test without Ray first
        use_gpu=False,
    )
    
    optimizer = GeneticOptimizer(
        df=df,
        strategy_class=strategy,
        param_space=param_space,
        config=config,
        use_smart_ranges=False,  # Already using smart ranges
        progress_callback=progress_callback,
    )
    
    print(f"   ? Optimizer ready")
    print()
    
    # 8. Run optimization
    print("8?? Running optimization...")
    print()
    print("   " + "-"*70)
    
    results = optimizer.optimize()
    
    print("   " + "-"*70)
    print()
    
    # 9. Show results
    print("9?? RESULTS:")
    print()
    print(f"   ? Best Sharpe Ratio: {results['best_fitness']['sharpe_ratio']:.2f}")
    print(f"   ? Win Rate: {results['best_fitness']['win_rate']:.1f}%")
    print(f"   ? Max Drawdown: {results['best_fitness']['max_drawdown_pct']:.2f}%")
    print(f"   ? Total Time: {results['total_time']:.1f}s")
    print(f"   ? Evaluations: {results['total_evaluations']}")
    print()
    
    print("   ?? Best Parameters:")
    for param, value in results['best_params'].items():
        print(f"      - {param}: {value}")
    print()
    
    # 10. Verify progress tracking
    print("?? PROGRESS VERIFICATION:")
    print()
    print(f"   ? Tracked {len(progress_log)} generations")
    
    if len(progress_log) == n_generations:
        print(f"   ? All {n_generations} generations logged!")
        
        # Show improvement
        first_gen = progress_log[0]
        last_gen = progress_log[-1]
        
        improvement = last_gen['best_sharpe'] - first_gen['best_sharpe']
        print(f"   ?? Improvement: {first_gen['best_sharpe']:.2f} ? {last_gen['best_sharpe']:.2f} "
              f"({improvement:+.2f})")
    else:
        print(f"   ?? Expected {n_generations} logs, got {len(progress_log)}")
    
    print()
    print("="*80)
    print("? TEST COMPLETED SUCCESSFULLY!")
    print("="*80)
    print()


if __name__ == "__main__":
    asyncio.run(test_optimization())
