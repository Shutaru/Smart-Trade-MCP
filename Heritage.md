# Heritage.md - Complete System Documentation for Future AI Instances

**Document Version:** 1.0.0  
**Last Updated:** 2025-11-21  
**System Status:** Production Ready with Known Issues

---

## ?? Executive Summary

**Smart-Trade MCP** is a professional algorithmic trading platform with 42+ built-in strategies, integrated with **Claude Desktop** via the **Model Context Protocol (MCP)**. The system provides comprehensive backtesting, optimization, and portfolio management capabilities for cryptocurrency trading.

### Current State:
- ? **Production Ready:** Core functionality operational
- ?? **Known Issue:** MCP backtest tool fetches only 6 days instead of 1 year
- ? **Configuration:** Claude Desktop MCP integration active
- ? **Performance:** GPU-accelerated backtesting operational

---

## ??? System Architecture

### High-Level Overview

```
????????????????????????????????????????????????????????????????
?                     CLAUDE DESKTOP                           ?
?                   (User Interface)                           ?
????????????????????????????????????????????????????????????????
                     ?
                     ? MCP Protocol (stdio)
                     ?
????????????????????????????????????????????????????????????????
?                   MCP SERVER                                 ?
?              (src/mcp_server/server.py)                      ?
?                                                              ?
?  Tools Available:                                            ?
?  • list_strategies                                           ?
?  • backtest_strategy                                         ?
?  • optimize_strategy_parameters                              ?
?  • run_walk_forward_analysis                                 ?
?  • run_k_fold_validation                                     ?
?  • detect_market_regime                                      ?
?  • optimize_portfolio                                        ?
?  • diagnose_strategy_failure                                 ?
?  • suggest_parameter_fixes                                   ?
????????????????????????????????????????????????????????????????
                     ?
         ???????????????????????????????????????????????????????
         ?                       ?              ?              ?
???????????????????  ??????????????????  ????????????  ??????????????
?  STRATEGY       ?  ?   BACKTEST     ?  ?   DATA   ?  ?OPTIMIZATION?
?  REGISTRY       ?  ?   ENGINE       ?  ? MANAGER  ?  ?  ENGINE    ?
?                 ?  ?                ?  ?          ?  ?            ?
?  42+ Strategies ?  ?  GPU/CPU       ?  ?  CCXT    ?  ?  Genetic   ?
?  - Breakout     ?  ?  Execution     ?  ?  SQLite  ?  ?  Algorithm ?
?  - Trend        ?  ?  Commission    ?  ?  Cache   ?  ?  WFA       ?
?  - Mean Rev.    ?  ?  Slippage      ?  ?          ?  ?  K-Fold    ?
?  - Momentum     ?  ?  Risk Mgmt     ?  ?          ?  ?            ?
?  - Hybrid       ?  ?                ?  ?          ?  ?            ?
?  - Advanced     ?  ?                ?  ?          ?  ?            ?
???????????????????  ??????????????????  ????????????  ??????????????
                                ?
                     ???????????????????????
                     ?  PORTFOLIO          ?
                     ?  OPTIMIZER          ?
                     ?                     ?
                     ?  - Equal Weight     ?
                     ?  - Risk Parity      ?
                     ?  - Max Sharpe       ?
                     ?  - Min Variance     ?
                     ???????????????????????
```

---

## ?? Project Structure

```
Smart-Trade-MCP/
??? src/
?   ??? mcp_server/              # MCP Server Implementation
?   ?   ??? server.py            # Main MCP server (stdio protocol)
?   ?   ??? tools/               # MCP Tools
?   ?       ??? backtest.py      # Backtesting tool
?   ?       ??? strategies.py    # Strategy listing
?   ?       ??? regime.py        # Market regime detection
?   ?       ??? optimization.py  # Strategy optimization
?   ?       ??? walk_forward.py  # WFA validation
?   ?       ??? k_fold.py        # K-Fold validation
?   ?       ??? portfolio.py     # Portfolio optimization
?   ?       ??? monte_carlo.py   # Monte Carlo simulation
?   ?       ??? diagnostics.py   # Strategy diagnostics
?   ?
?   ??? strategies/              # Trading Strategies
?   ?   ??? base.py              # BaseStrategy class
?   ?   ??? registry.py          # Strategy registry
?   ?   ??? __init__.py          # Main exports
?   ?   ??? generated/           # 42+ Strategy Implementations
?   ?       ??? auto_register.py # Auto-registration
?   ?       ??? breakout/        # 12 Breakout strategies
?   ?       ??? trend/           # 8 Trend strategies
?   ?       ??? mean_reversion/  # 6 Mean reversion strategies
?   ?       ??? momentum/        # 8 Momentum strategies
?   ?       ??? hybrid/          # 6 Hybrid strategies
?   ?       ??? advanced/        # 2 Advanced strategies
?   ?
?   ??? core/                    # Core Engine
?   ?   ??? backtest_engine.py   # Backtesting execution
?   ?   ??? data_manager.py      # CCXT + SQLite data management
?   ?   ??? indicators.py        # Technical indicators (TA-Lib)
?   ?   ??? database.py          # SQLite database operations
?   ?   ??? logger.py            # Logging configuration
?   ?   ??? risk_manager.py      # Position sizing & risk
?   ?
?   ??? optimization/            # Optimization Engines
?   ?   ??? genetic_optimizer.py # Genetic Algorithm
?   ?   ??? walk_forward.py      # Walk-Forward Analysis
?   ?   ??? k_fold.py            # K-Fold Cross-Validation
?   ?   ??? monte_carlo.py       # Monte Carlo simulation
?   ?   ??? n_fold_wfa.py        # N-Fold WFA
?   ?
?   ??? portfolio/               # Portfolio Management
?       ??? portfolio_optimizer.py # Multi-strategy optimization
?       ??? portfolio_config.py    # Portfolio configuration
?
??? data/                        # Data Storage
?   ??? market/                  # Market data cache
?       ??? binance/             # Exchange-specific DBs
?           ??? BTC_USDT_1h.db   # SQLite database
?
??? logs/                        # Log files (auto-generated)
?
??? .mcp.json                    # MCP config for Claude Code (CLI)
??? claude_desktop_config.json   # Example Claude Desktop config
??? .env.example                 # Environment variables template
??? .gitignore                   # Git ignore rules
??? pyproject.toml               # Python dependencies (Poetry)
??? poetry.lock                  # Locked dependencies
??? README.md                    # User documentation
??? Heritage.md                  # THIS FILE
```

---

## ?? MCP Tools Reference

### 1. **list_strategies**
Lists all available trading strategies (42+).

**Parameters:**
- `category` (optional): Filter by category
  - `breakout`, `trend`, `mean_reversion`, `momentum`, `hybrid`, `advanced`

**Returns:**
```json
{
  "total": 42,
  "strategies": [
    {
      "name": "atr_expansion_breakout",
      "category": "breakout",
      "description": "ATR expansion breakout strategy",
      "required_indicators": ["atr", "ema"],
      "default_params": {}
    },
    ...
  ]
}
```

---

### 2. **backtest_strategy**
Runs backtest for a trading strategy with auto-fetch of historical data.

**Parameters:**
- `strategy_name` (required): Strategy identifier
- `symbol` (optional): Trading pair (default: "BTC/USDT")
- `timeframe` (optional): Candle timeframe (default: "1h")
- `start_date` (optional): Start date YYYY-MM-DD (default: 1 year ago)
- `end_date` (optional): End date YYYY-MM-DD (default: now)
- `initial_capital` (optional): Starting capital (default: 10000.0)

**Returns:**
```json
{
  "strategy": "AtrExpansionBreakout",
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "start_date": "2024-11-21 18:00:00",
  "end_date": "2025-11-21 17:00:00",
  "days_tested": 364,
  "candles_tested": 8760,
  "total_return": 2.25,
  "total_trades": 22,
  "metrics": {
    "sharpe_ratio": 0.077,
    "win_rate": 54.5,
    "max_drawdown_pct": -10.73,
    "profit_factor": 1.15
  },
  "tool_version": "2.0.0-auto-fetch"
}
```

---

### 3. **optimize_strategy_parameters**
Optimizes strategy parameters using Genetic Algorithm.

**Parameters:**
- `strategy_name` (required)
- `symbol` (optional)
- `timeframe` (optional)
- `population_size` (optional): GA population (default: 30)
- `n_generations` (optional): Number of generations (default: 10)

**Returns:**
```json
{
  "best_params": {...},
  "best_fitness": 1.25,
  "optimization_history": [...],
  "final_backtest": {...}
}
```

---

### 4. **run_walk_forward_analysis**
Performs Walk-Forward Analysis for robust validation.

**Parameters:**
- `strategy_name` (required)
- `symbol` (optional)
- `timeframe` (optional)
- `n_splits` (optional): Number of train/test splits (default: 5)
- `train_ratio` (optional): Training data ratio (default: 0.7)

**Returns:**
```json
{
  "aggregated_metrics": {
    "mean_return": 2.5,
    "mean_sharpe": 0.8,
    "consistency_score": 0.75
  },
  "fold_results": [...]
}
```

---

### 5. **detect_market_regime**
Analyzes current market conditions and recommends strategies.

**Parameters:**
- `symbol` (optional): Trading pair (default: "BTC/USDT")
- `timeframe` (optional): Candle timeframe (default: "1h")
- `lookback` (optional): Candles to analyze (default: 100)

**Returns:**
```json
{
  "regime": "trending",
  "confidence": 0.85,
  "volatility": "medium",
  "recommended_strategies": ["atr_expansion_breakout", ...],
  "avoid_strategies": ["bollinger_mean_reversion", ...]
}
```

---

### 6. **optimize_portfolio**
Multi-strategy portfolio optimization.

**Parameters:**
- `strategies` (required): List of strategy names
- `symbol` (optional)
- `timeframe` (optional)
- `optimization_method` (optional): 
  - `equal_weight`, `risk_parity`, `max_sharpe`, `min_variance`

**Returns:**
```json
{
  "weights": {
    "atr_expansion_breakout": 0.35,
    "ema_stack_momentum": 0.25,
    ...
  },
  "portfolio_sharpe": 1.2,
  "portfolio_max_drawdown": -8.5,
  "correlation_matrix": [[...]]
}
```

---

## ?? Known Issues & Debugging

### Issue #1: Backtest Fetches Only 6 Days Instead of 1 Year

**Symptoms:**
- `days_tested: 6` instead of ~364
- `candles_tested: 150` instead of ~8760
- `total_trades: 1` instead of 20+
- `tool_version: "2.0.0-auto-fetch"` (correct)

**What Works:**
- ? Direct Python call to `fetch_historical()` fetches 8760 candles
- ? MCP server loads correctly
- ? Tool version shows "2.0.0-auto-fetch"

**What Doesn't Work:**
- ? MCP tool call only fetches recent data

**Root Cause:**
Unknown. Suspected issues:
1. Date parameters not being passed through MCP protocol
2. CCXT exchange rate limiting
3. SQLite cache returning stale data
4. MCP server state issue

**Debugging Steps for Next AI Instance:**

1. **Check MCP Tool Invocation:**
   ```python
   # In src/mcp_server/tools/backtest.py
   # Add logging to verify parameters:
   logger.info(f"start_date: {start_date}, end_date: {end_date}")
   logger.info(f"start_dt: {start_dt}, end_dt: {end_dt}")
   ```

2. **Test Direct Tool Call:**
   ```python
   import asyncio
   from src.mcp_server.tools.backtest import backtest_strategy
   
   result = asyncio.run(backtest_strategy(
       strategy_name="atr_expansion_breakout",
       symbol="BTC/USDT",
       timeframe="1h"
   ))
   print(result['days_tested'])  # Should be ~364
   ```

3. **Check CCXT Rate Limits:**
   ```python
   # In src/core/data_manager.py
   # Verify pagination is working:
   logger.info(f"Fetching chunk {i+1}, since={since}")
   ```

4. **Clear Database Cache:**
   ```bash
   rm data/market/binance/BTC_USDT_1h.db
   # Then retry backtest
   ```

5. **Test with Explicit Dates:**
   ```
   Claude, backtest atr_expansion_breakout on BTC/USDT 1h 
   from 2024-01-01 to 2025-01-01
   ```

---

## ?? Configuration Files

### Claude Desktop Config
**Location:** `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "smart-trade": {
      "command": "python",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "C:\\Users\\shuta\\source\\repos\\Smart-Trade-MCP",
      "env": {
        "PYTHONPATH": "C:\\Users\\shuta\\source\\repos\\Smart-Trade-MCP"
      }
    }
  }
}
```

### Claude Code (CLI) Config
**Location:** `.mcp.json` (project root)

```json
{
  "mcpServers": {
    "smart-trade": {
      "command": "python",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "C:\\Users\\shuta\\source\\repos\\Smart-Trade-MCP",
      "env": {
        "PYTHONPATH": "C:\\Users\\shuta\\source\\repos\\Smart-Trade-MCP",
        "SMART_TRADE_ENV": "production"
      }
    }
  }
}
```

---

## ?? Strategy Categories

### Breakout Strategies (12)
High-volatility breakout strategies optimized for trending markets.

**Examples:**
- `atr_expansion_breakout` - ATR-based volatility expansion
- `donchian_volatility_breakout` - Donchian channel breakout
- `channel_squeeze_plus` - Price compression breakout
- `volatility_weighted_breakout` - Volatility-adjusted entries
- `london_breakout_atr` - Session-based breakout

**Best Markets:** Trending, high volatility  
**Avoid:** Ranging, low volatility

---

### Trend Following Strategies (8)
Momentum-based strategies for sustained directional moves.

**Examples:**
- `ema_stack_momentum` - EMA alignment trading
- `supertrend_flip` - SuperTrend indicator reversals
- `trend_volume_combo` - Trend + volume confluence
- `ema_stack_regime_flip` - Regime-based EMA stack

**Best Markets:** Strong trends  
**Avoid:** Choppy, ranging markets

---

### Mean Reversion Strategies (6)
Counter-trend strategies exploiting price extremes.

**Examples:**
- `bollinger_mean_reversion` - Bollinger Band reversals
- `vwap_mean_reversion` - VWAP deviation trades
- `ema200_tap_reversion` - EMA200 bounce trades
- `rsi_extreme_reversal` - RSI overbought/oversold

**Best Markets:** Ranging, low volatility  
**Avoid:** Strong trends

---

### Momentum Strategies (8)
Oscillator-based momentum capture.

**Examples:**
- `mfi_impulse_momentum` - Money Flow Index signals
- `triple_momentum_confluence` - Multi-oscillator alignment
- `rsi_supertrend_flip` - RSI + SuperTrend combo
- `multi_oscillator_confluence` - RSI + CCI + Stoch

**Best Markets:** Medium volatility, trending  
**Avoid:** Extreme volatility

---

### Hybrid Strategies (6)
Combined approach strategies.

**Examples:**
- `vwap_institutional_trend` - 58-68% win rate
- `keltner_pullback_continuation` - Pullback entries
- `order_flow_momentum_vwap` - Order flow + VWAP
- `vwap_band_fade_pro` - VWAP band reversals

**Best Markets:** All market conditions  
**Performance:** Moderate, consistent

---

### Advanced Strategies (2)
Multi-component adaptive systems.

**Examples:**
- `regime_adaptive_core` - 52-66% win rate
- `complete_system_5x` - 56-68% win rate

**Complexity:** High  
**Best Markets:** Adaptive to all conditions

---

## ?? Technical Stack

### Core Technologies:
- **Python:** 3.10+
- **MCP Protocol:** Model Context Protocol (Anthropic)
- **Data:** CCXT (exchange API) + SQLite (cache)
- **Indicators:** TA-Lib
- **Optimization:** DEAP (Genetic Algorithms), scipy
- **GPU Acceleration:** CuPy (optional)

### Key Dependencies:
```toml
[tool.poetry.dependencies]
python = "^3.10"
mcp = "^1.0.0"
ccxt = "^4.0.0"
pandas = "^2.0.0"
numpy = "^1.24.0"
ta-lib = "^0.4.0"
deap = "^1.4.0"
scipy = "^1.11.0"
cupy-cuda12x = {version = "^12.0.0", optional = true}
```

---

## ?? Performance Benchmarks

### Backtest Speed:
- **CPU Mode:** ~1,000 candles/second
- **GPU Mode:** ~5,000 candles/second (CUDA)

### Optimization Speed:
- **Genetic Algorithm:** 30 pop × 10 gen = ~5 minutes
- **Walk-Forward Analysis:** 5 folds = ~2 minutes
- **Portfolio Optimization:** 10 strategies = ~3 minutes

### Data Fetching:
- **First Fetch:** ~10 seconds (1 year, hourly)
- **Cached Access:** <1 second

---

## ?? Usage Examples

### Example 1: Simple Backtest
```
Claude, backtest the atr_expansion_breakout strategy on BTC/USDT 1h.
Show me Sharpe Ratio, Win Rate, and Max Drawdown.
```

### Example 2: Strategy Comparison
```
Claude, compare these strategies on BTC/USDT 1h:
- atr_expansion_breakout
- ema_stack_momentum
- bollinger_mean_reversion

Show which has the best Sharpe Ratio.
```

### Example 3: Market Regime Analysis
```
Claude, detect the current market regime for BTC/USDT 
and recommend the top 3 strategies to use right now.
```

### Example 4: Portfolio Optimization
```
Claude, optimize a portfolio with these strategies using risk parity:
- atr_expansion_breakout
- vwap_institutional_trend
- regime_adaptive_core

Show me the optimal weights.
```

### Example 5: Parameter Optimization
```
Claude, optimize the RSI strategy parameters for BTC/USDT 1h.
Use 20 population size and 5 generations.
Show me the improvement over default parameters.
```

---

## ?? Development Workflow

### Adding a New Strategy:

1. **Create Strategy File:**
   ```python
   # src/strategies/generated/my_new_strategy.py
   from ..base import BaseStrategy
   
   class MyNewStrategy(BaseStrategy):
       def __init__(self):
           super().__init__(name="my_new_strategy")
       
       def get_required_indicators(self):
           return ["rsi", "ema", "atr"]
       
       def generate_signals(self, df):
           # Implementation
           pass
   ```

2. **Register Strategy:**
   Auto-registration happens via `auto_register.py`

3. **Test Strategy:**
   ```python
   from src.strategies import registry
   strategy = registry.get("my_new_strategy")
   ```

4. **Backtest:**
   ```
   Claude, backtest my_new_strategy on BTC/USDT 1h
   ```

---

### Running Tests:

```bash
# Unit tests
python -m pytest tests/

# Integration test
python -c "
from src.mcp_server.tools.backtest import backtest_strategy
import asyncio
result = asyncio.run(backtest_strategy('atr_expansion_breakout', 'BTC/USDT', '1h'))
print(result['days_tested'])
"
```

---

### Debugging MCP Server:

```bash
# Run server with verbose logging
PYTHONUNBUFFERED=1 python -m src.mcp_server.server

# Check Claude Desktop logs
# Windows: %APPDATA%/Claude/logs/
# Mac: ~/Library/Logs/Claude/
```

---

## ?? Roadmap & Future Work

### High Priority:
- [ ] **Fix 6-day data fetch issue** (CRITICAL)
- [ ] Add real-time paper trading support
- [ ] Implement strategy performance dashboard
- [ ] Add multi-exchange support (Binance, Coinbase, Kraken)

### Medium Priority:
- [ ] TradingView webhook integration
- [ ] Telegram notifications for signals
- [ ] Web-based portfolio monitoring
- [ ] Advanced risk management (Kelly Criterion)

### Low Priority:
- [ ] Machine learning strategy generator
- [ ] Sentiment analysis integration
- [ ] Multi-asset correlation analysis
- [ ] Automated strategy discovery

---

## ?? Troubleshooting Guide

### Problem: MCP Server Not Connecting

**Solution:**
1. Restart Claude Desktop
2. Check `%APPDATA%/Claude/logs/mcp-server-smart-trade.log`
3. Verify Python path in config
4. Test server manually: `python -m src.mcp_server.server`

---

### Problem: Strategies Not Loading

**Solution:**
1. Check `src/strategies/generated/auto_register.py`
2. Verify strategy files have correct class structure
3. Look for import errors in logs

---

### Problem: Backtest Running Slow

**Solution:**
1. Enable GPU mode: `use_gpu=True`
2. Reduce data range
3. Use cached data (don't clear database)
4. Optimize indicator calculations

---

### Problem: Optimization Taking Too Long

**Solution:**
1. Reduce population size (e.g., 20 instead of 30)
2. Reduce generations (e.g., 5 instead of 10)
3. Use smaller date range for fitness evaluation
4. Enable parallel processing (multi-core)

---

## ?? Notes for Next AI Instance

### Context You Should Know:

1. **User has Claude Max subscription** - no token limits
2. **User prefers production-ready solutions** - avoid experimental
3. **System is Windows-based** - PowerShell commands
4. **GPU available:** RTX 3070 Ti (CUDA 12.x)
5. **Primary use case:** BTC/USDT algorithmic trading

### What NOT to Suggest:

- ? Open WebUI integration (tried, not stable)
- ? Ollama/local LLMs (lack tool calling)
- ? GPT-4 API (user chose Claude Max)
- ? React/Vue frontends (not needed, MCP is the interface)

### What to Focus On:

- ? Fixing the 6-day data fetch issue
- ? Improving strategy performance
- ? Adding more validation tools
- ? Portfolio optimization enhancements
- ? MCP tool improvements

---

## ?? Quick Reference Commands

### Start MCP Server (Claude Desktop auto-starts it):
```bash
python -m src.mcp_server.server
```

### Test Data Fetch:
```python
import asyncio
from src.core.data_manager import DataManager
from datetime import datetime, timedelta

async def test():
    dm = DataManager()
    df = await dm.fetch_historical(
        symbol='BTC/USDT',
        timeframe='1h',
        start_date=datetime.now() - timedelta(days=365),
        end_date=datetime.now(),
        max_candles=10000
    )
    await dm.close()
    print(f"Fetched {len(df)} candles")

asyncio.run(test())
```

### List All Strategies:
```python
from src.strategies import registry
print(f"Total strategies: {len(registry.list_all())}")
for name in registry.list_all():
    print(f"  - {name}")
```

### Direct Backtest:
```python
import asyncio
from src.mcp_server.tools.backtest import backtest_strategy

result = asyncio.run(backtest_strategy(
    strategy_name="atr_expansion_breakout",
    symbol="BTC/USDT",
    timeframe="1h"
))
print(f"Days tested: {result['days_tested']}")
print(f"Total trades: {result['total_trades']}")
```

---

## ?? Final Status Summary

### What's Production-Ready:
- ? MCP Server with 9 tools
- ? 42+ trading strategies
- ? Backtest engine (GPU-accelerated)
- ? Genetic Algorithm optimization
- ? Walk-Forward Analysis
- ? Portfolio optimization
- ? Market regime detection

### What Needs Attention:
- ?? 6-day data fetch limitation in MCP backtest
- ?? No live trading implementation (by design)
- ?? Limited exchange support (Binance only tested)

### Repository Cleanliness:
- ? All experimental files removed
- ? Historical docs archived
- ? Test files cleaned up
- ? Only production code remains

---

**End of Heritage Document**

**For Future AI Instances:**  
Read this document first before making changes. It contains critical context, known issues, and architectural decisions. The 6-day data fetch issue is the #1 priority to solve.

**Version:** 1.0.0  
**Date:** 2025-11-21  
**Author:** Smart-Trade MCP Development Team
