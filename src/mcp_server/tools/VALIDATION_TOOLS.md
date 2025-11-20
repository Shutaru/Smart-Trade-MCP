# ?? VALIDATION TOOLS - MCP INTERFACE

**Component:** `src/mcp_server/tools/validation.py`  
**Purpose:** MCP-exposed validation tools for AI agents  
**Status:** ? Production Ready (WFA) | ?? In Progress (K-Fold, Monte Carlo)

---

## ?? OVERVIEW

This module provides MCP tools for strategy validation, exposing advanced
backtesting methods to AI agents via the Model Context Protocol.

**Available Tools:**
1. ? `run_walk_forward_analysis` - Out-of-sample validation
2. ?? `run_k_fold_validation` - Cross-validation
3. ?? `run_monte_carlo_simulation` - Risk analysis

---

## ?? TOOL 1: Walk-Forward Analysis

### MCP Tool Definition

```python
async def run_walk_forward_analysis(
    strategy_name: str,
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    train_days: int = 180,
    test_days: int = 60,
    step_days: int = 30,
    initial_capital: float = 10000.0,
    parallel: bool = True,
    n_jobs: int = -1,
) -> Dict[str, Any]:
```

### Tool Schema (MCP)

```json
{
  "name": "run_walk_forward_analysis",
  "description": "Validate strategy with Walk-Forward Analysis - Critical for detecting overfitting",
  "inputSchema": {
    "type": "object",
    "properties": {
      "strategy_name": {
        "type": "string",
        "description": "Name of strategy to validate"
      },
      "symbol": {
        "type": "string",
        "default": "BTC/USDT",
        "description": "Trading pair"
      },
      "timeframe": {
        "type": "string",
        "default": "1h",
        "description": "Candle timeframe"
      },
      "train_days": {
        "type": "integer",
        "default": 180,
        "description": "Training window size (days)"
      },
      "test_days": {
        "type": "integer",
        "default": 60,
        "description": "Testing window size (days)"
      }
    },
    "required": ["strategy_name"]
  }
}
```

### AI Agent Usage Example

```python
# AI Agent calls via MCP
response = await mcp_client.call_tool(
    "run_walk_forward_analysis",
    {
        "strategy_name": "cci_extreme_snapback",
        "symbol": "BTC/USDT",
        "train_days": 180,
        "test_days": 60
    }
)

# Response structure
{
    "strategy": "cci_extreme_snapback",
    "symbol": "BTC/USDT",
    "timeframe": "1h",
    "n_windows": 5,
    "stability_ratio": 0.85,
    "consistency": 80.0,
    "avg_in_sample_return": 9.2,
    "avg_out_sample_return": 7.8,
    "recommendation": "PASS - Strategy validated",
    "windows": [...],
    "best_window": {...},
    "worst_window": {...}
}
```

### Internal Implementation

```python
async def run_walk_forward_analysis(...):
    """
    1. Get strategy from registry
    2. Fetch historical data (auto-calculate required candles)
    3. Calculate required indicators
    4. Run BacktestEngine.walk_forward_analysis()
    5. Add metadata and return results
    """
    
    # Strategy lookup
    strategy = registry.get(strategy_name)
    
    # Data fetching (automatic sizing)
    days_needed = train_days + (test_days * 3) + (step_days * 3)
    candles_per_day = {"1h": 24, "4h": 6, "1d": 1}
    limit = days_needed * candles_per_day[timeframe]
    
    # Fetch and prepare
    df = await dm.fetch_ohlcv(symbol, timeframe, limit)
    df = calculate_all_indicators(df, strategy.get_required_indicators())
    
    # Execute WFA
    engine = BacktestEngine(initial_capital)
    results = engine.walk_forward_analysis(
        strategy=strategy,
        df=df,
        train_days=train_days,
        test_days=test_days,
        step_days=step_days,
        parallel=parallel,
        n_jobs=n_jobs,
    )
    
    # Add metadata
    results['strategy'] = strategy_name
    results['symbol'] = symbol
    results['timeframe'] = timeframe
    
    return results
```

### Error Handling

```python
try:
    results = await run_walk_forward_analysis(...)
except KeyError:
    return {
        "error": "Strategy not found",
        "available_strategies": [s.name for s in registry.list_strategies()]
    }
except ValueError as e:
    return {
        "error": str(e),  # e.g., "Insufficient data"
        "strategy": strategy_name
    }
except Exception as e:
    logger.error(f"WFA error: {e}", exc_info=True)
    raise
```

---

## ?? TOOL 2: K-Fold Validation (Coming Soon)

### Purpose

Complementary validation method that divides data into K equal folds.

### MCP Tool Definition

```python
async def run_k_fold_validation(
    strategy_name: str,
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    k: int = 5,
    shuffle: bool = False,
    initial_capital: float = 10000.0,
    parallel: bool = True,
    n_jobs: int = -1,
) -> Dict[str, Any]:
```

### Expected Return

```python
{
    "strategy": "cci_extreme_snapback",
    "symbol": "BTC/USDT",
    "k": 5,
    "folds": [
        {
            "fold_id": 1,
            "train_size": 800,
            "test_size": 200,
            "return": 4.5,
            "sharpe": 0.78
        },
        ...
    ],
    "mean_return": 4.2,
    "std_return": 1.3,
    "consistency": 80.0,
    "recommendation": "PASS"
}
```

### Status

?? **To be implemented in Phase 1 completion**

---

## ?? TOOL 3: Monte Carlo Simulation (Coming Soon)

### Purpose

Risk analysis by resampling trade sequences.

### MCP Tool Definition

```python
async def run_monte_carlo_simulation(
    strategy_name: str,
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    n_simulations: int = 1000,
    initial_capital: float = 10000.0,
    parallel: bool = True,
    n_jobs: int = -1,
) -> Dict[str, Any]:
```

### Expected Return

```python
{
    "strategy": "cci_extreme_snapback",
    "n_simulations": 1000,
    "median_return": 8.2,
    "confidence_intervals": {
        "95": [3.1, 15.8],
        "90": [4.2, 13.5],
        "75": [5.5, 11.2]
    },
    "risk_of_ruin": 2.3,  # % chance of >20% DD
    "worst_case": -5.2,   # 1st percentile
    "best_case": 22.1,    # 99th percentile
    "equity_curves_sample": [...]  # For visualization
}
```

### Status

?? **To be implemented in Phase 1 completion**

---

## ?? WORKFLOW INTEGRATION

### AI Agent Validation Workflow

```
???????????????????????????????????????????
?  AI Agent                                ?
???????????????????????????????????????????
             ?
             ? 1. Call: run_walk_forward_analysis
             ?
???????????????????????????????????????????
?  MCP Server                              ?
?  ?? Validation Tool                     ?
?  ?? Fetch Data                           ?
?  ?? Calculate Indicators                 ?
?  ?? Run BacktestEngine.WFA()            ?
???????????????????????????????????????????
             ?
             ? 2. Results
             ?
???????????????????????????????????????????
?  AI Agent Decision                       ?
?                                          ?
?  IF recommendation == "PASS":            ?
?      ? Proceed to optimization           ?
?  ELIF recommendation == "MARGINAL":      ?
?      ? Tune parameters and re-test       ?
?  ELSE:                                   ?
?      ? Discard strategy                  ?
????????????????????????????????????????????
```

---

## ?? DATA MANAGEMENT

### Automatic Data Sizing

The tool automatically calculates required data:

```python
# Calculate minimum candles needed
min_windows = 3  # At least 3 windows for meaningful WFA
days_needed = train_days + (test_days * min_windows) + (step_days * min_windows)

# Convert to candles
candles_per_day = {
    "1h": 24,
    "4h": 6,
    "1d": 1,
    "15m": 96,
    "5m": 288,
}

limit = days_needed * candles_per_day.get(timeframe, 24)
```

### Data Quality Checks

```python
# After fetching
if df.empty:
    return {"error": "No market data available"}

# Log actual coverage
actual_days = (df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).days
logger.info(f"Fetched {len(df)} candles covering {actual_days} days")

# Warn if insufficient
if actual_days < (train_days + test_days):
    logger.warning("Insufficient data for requested windows")
```

---

## ?? BEST PRACTICES

### 1. Strategy Naming

? **Correct:**
```python
await run_walk_forward_analysis(
    strategy_name="cci_extreme_snapback"  # Lowercase, snake_case
)
```

? **Wrong:**
```python
await run_walk_forward_analysis(
    strategy_name="CCIExtremeSnapback"  # Wrong case
)
```

### 2. Timeframe Selection

**For crypto (24/7 markets):**
- ? 1h, 4h, 1d - Good balance
- ?? 15m, 5m - High data requirements
- ? 1m - Too noisy, requires huge datasets

**For stocks (limited hours):**
- ? 1d, 1h - Standard
- ?? Intraday - Gaps and limited hours

### 3. Window Sizing

**Conservative (recommended):**
```python
train_days=180,  # 6 months
test_days=60,    # 2 months
step_days=30,    # 1 month step (50% overlap)
```

**Aggressive (faster but less reliable):**
```python
train_days=120,  # 4 months
test_days=40,    # 1.3 months
step_days=40,    # No overlap
```

---

## ?? DEBUGGING

### Enable Verbose Logging

```python
import logging
logging.getLogger("src.mcp_server.tools.validation").setLevel(logging.DEBUG)

# Now see detailed logs
results = await run_walk_forward_analysis(...)
```

### Test with Known Strategy

```python
# Use a simple, known-good strategy for testing
results = await run_walk_forward_analysis(
    strategy_name="rsi",  # Built-in simple strategy
    symbol="BTC/USDT",
    train_days=120,
    test_days=40,
)
```

### Dry Run (No Execution)

```python
# Fetch data and check sizing without running WFA
dm = DataManager()
df = await dm.fetch_ohlcv("BTC/USDT", "1h", limit=500)
print(f"Fetched {len(df)} candles")
print(f"Period: {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
await dm.close()
```

---

## ?? PERFORMANCE TIPS

### 1. Use Parallelism

```python
# Default (fastest)
results = await run_walk_forward_analysis(
    ...,
    parallel=True,
    n_jobs=-1,  # All cores
)
```

### 2. Cache Data

```python
# If testing multiple strategies on same data
dm = DataManager()
df = await dm.fetch_ohlcv("BTC/USDT", "1h", limit=1000)

# Test multiple strategies
for strategy_name in ["cci_extreme_snapback", "bollinger_mean_reversion"]:
    # Use pre-fetched data (not implemented yet, but good pattern)
    ...
```

### 3. Batch Validation

```python
# Validate multiple strategies in one go
strategies = ["cci_extreme_snapback", "multi_oscillator_confluence", "bollinger_mean_reversion"]

for strategy in strategies:
    results = await run_walk_forward_analysis(strategy_name=strategy)
    print(f"{strategy}: {results['recommendation']}")
```

---

## ?? SUPPORT

### Common Issues

**Issue:** Tool returns error "Strategy not found"

**Solution:**
```python
# Check available strategies
from src.strategies import registry
available = [s.name for s in registry.list_strategies()]
print(available)
```

**Issue:** Not enough data for WFA

**Solution:**
```python
# Reduce window sizes or fetch more data
results = await run_walk_forward_analysis(
    train_days=120,  # Smaller
    test_days=40,    # Smaller
)
```

**Issue:** WFA takes too long

**Solution:**
```python
# Enable parallelism
results = await run_walk_forward_analysis(
    parallel=True,
    n_jobs=-1,
)
```

---

## ?? RELATED DOCUMENTATION

- `src/core/BACKTEST_ENGINE.md` - BacktestEngine implementation details
- `docs/VALIDATION.md` - Conceptual overview of validation methods
- `examples/walk_forward_example.py` - Full usage example

---

**Last Updated:** 2025-11-20  
**Version:** 1.0.0  
**Status:** ? WFA Ready | ?? K-Fold & Monte Carlo In Progress
