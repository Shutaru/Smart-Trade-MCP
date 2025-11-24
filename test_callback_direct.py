#!/usr/bin/env python
"""Quick test for progress callback"""

import os
os.environ['SMART_TRADE_MCP_MODE'] = 'true'

# Test callback directly
def my_callback(gen, stats):
    print(f"? CALLBACK CALLED! Gen {gen}, Sharpe {stats['best_fitness']['sharpe_ratio']:.2f}")

print("Testing callback...")
my_callback(1, {"best_fitness": {"sharpe_ratio": 1.5}, "avg_fitness": {}})
print("? Callback works!")

# Now test if it's passed correctly
from src.optimization.genetic_optimizer import GeneticOptimizer

print("\nChecking if callback is stored...")
class MockStrategy:
    name = "test"
    def get_required_indicators(self):
        return []

import pandas as pd
from src.optimization.parameter_space import ParameterSpace, ParameterDefinition, ParameterType
from src.optimization.config import OptimizationConfig

# Create minimal param space
param_space = ParameterSpace(
    parameters={
        "test_param": ParameterDefinition(
            name="test_param",
            type=ParameterType.INT,
            low=1,
            high=10
        )
    }
)

# Create minimal df
df = pd.DataFrame({
    "timestamp": pd.date_range("2024-01-01", periods=100, freq="1H"),
    "open": [100.0] * 100,
    "high": [101.0] * 100,
    "low": [99.0] * 100,
    "close": [100.5] * 100,
    "volume": [1000.0] * 100,
})

config = OptimizationConfig(population_size=2, n_generations=2)

optimizer = GeneticOptimizer(
    df=df,
    strategy_class=MockStrategy(),
    param_space=param_space,
    config=config,
    progress_callback=my_callback
)

print(f"Callback stored: {optimizer.progress_callback is not None}")
print(f"Callback is: {optimizer.progress_callback}")

if optimizer.progress_callback:
    print("\n? Testing stored callback...")
    optimizer.progress_callback(99, {
        "generation": 99,
        "total_generations": 100,
        "best_fitness": {"sharpe_ratio": 2.5, "win_rate": 60.0, "max_drawdown_pct": -5.0},
        "avg_fitness": {"sharpe_ratio": 1.0, "win_rate": 50.0, "max_drawdown_pct": -10.0},
        "evaluated": 10,
        "elapsed_time": 30.0,
        "gen_time": 2.0
    })
    print("? Stored callback works!")
else:
    print("? Callback was NOT stored!")
