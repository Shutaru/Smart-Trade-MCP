# Smart-Trade MCP - Production Setup Guide

## ?? Overview

Smart-Trade MCP is a professional trading strategy backtesting and optimization platform with 42+ built-in strategies, integrated with Claude Desktop via Model Context Protocol (MCP).

---

## ? Current Status

### **What's Working:**
- ? MCP Server running and accessible to Claude Desktop
- ? 42+ trading strategies loaded and registered
- ? Backtest engine with GPU support
- ? Walk-Forward Analysis (WFA) validation
- ? Genetic Algorithm optimization
- ? Market regime detection
- ? Portfolio optimization

### **Configuration:**
- MCP config file: `%APPDATA%/Claude/claude_desktop_config.json`
- Python environment: Active
- Database: SQLite (local storage in `data/market/`)

---

## ?? MCP Tools Available

### **Core Tools:**

1. **`list_strategies`** - List all 42+ available strategies
   - Filter by category (breakout, trend, mean_reversion, momentum, hybrid, advanced)

2. **`backtest_strategy`** - Run strategy backtest
   - Auto-fetches 1 year of historical data
   - Supports all major exchanges via CCXT
   - Returns: Sharpe Ratio, Win Rate, Max Drawdown, Profit Factor

3. **`detect_market_regime`** - Analyze current market conditions
   - Detects: trending, ranging, volatile, quiet regimes
   - Recommends suitable strategies
   - Warns against unsuitable strategies

4. **`optimize_strategy_parameters`** - Genetic Algorithm optimization
   - Population-based parameter search
   - Multi-objective optimization (return, Sharpe, drawdown)
   - Walk-forward validation support

5. **`run_walk_forward_analysis`** - Robust strategy validation
   - Train/test splits with rolling windows
   - Out-of-sample performance testing
   - Prevents overfitting

6. **`run_k_fold_validation`** - Cross-validation for strategies
   - K-fold splits for comprehensive testing
   - Aggregated performance metrics

7. **`optimize_portfolio`** - Multi-strategy portfolio optimization
   - Equal weight, Risk Parity, Max Sharpe, Min Variance methods
   - Correlation analysis
   - Portfolio-level metrics

---

## ?? Known Issues & Solutions

### **Issue 1: Backtest Only Fetches 6 Days of Data**

**Symptoms:**
- `days_tested: 6` instead of ~364
- `candles_tested: 150` instead of ~8760
- `total_trades: 1` instead of 20+

**Status:** ?? UNRESOLVED
- Tool version correctly shows `2.0.0-auto-fetch`
- MCP server reloaded successfully
- `fetch_historical()` works when called directly (fetches 8760 candles)
- **Root cause:** Unknown - data fetch limitation only occurs via MCP call

**Next Steps:**
1. Debug MCP tool invocation flow
2. Check if date parameters are being passed correctly
3. Verify CCXT exchange rate limits
4. Test with explicit start_date/end_date parameters

---

## ?? Strategy Categories

### **Breakout (12 strategies)**
- ATR Expansion Breakout
- Donchian Volatility Breakout
- Channel Squeeze Plus
- And more...

### **Trend Following (8 strategies)**
- EMA Stack Momentum
- SuperTrend Flip
- Trend Volume Combo
- And more...

### **Mean Reversion (6 strategies)**
- Bollinger Band Reversal
- VWAP Mean Reversion
- EMA200 Tap Reversion
- And more...

### **Momentum (8 strategies)**
- MFI Impulse Momentum
- Triple Momentum Confluence
- Multi Oscillator Confluence
- And more...

### **Hybrid (6 strategies)**
- VWAP Institutional Trend
- Keltner Pullback Continuation
- Order Flow Momentum VWAP
- And more...

### **Advanced (2 strategies)**
- Regime Adaptive Core (52-66% win rate)
- Complete System 5x (56-68% win rate)

---

## ?? Usage Examples

### **Example 1: List Strategies**
```
Claude, list all breakout strategies available
```

### **Example 2: Run Backtest**
```
Claude, backtest the atr_expansion_breakout strategy on BTC/USDT 1h.
Show me Sharpe Ratio, Win Rate, and Max Drawdown.
```

### **Example 3: Optimize Strategy**
```
Claude, optimize the RSI strategy parameters using genetic algorithm.
Use 30 population size and 10 generations.
```

### **Example 4: Market Analysis**
```
Claude, detect the current market regime for BTC/USDT 
and recommend which strategies to use.
```

---

## ?? Architecture

```
???????????????????
? Claude Desktop  ?
???????????????????
         ? MCP Protocol
         ?
???????????????????
?  MCP Server     ?
?  (stdio)        ?
???????????????????
         ?
         ???? Strategy Registry (42+ strategies)
         ???? Backtest Engine (GPU/CPU)
         ???? Data Manager (CCXT + SQLite cache)
         ???? Optimization Engine (Genetic Algorithm)
         ???? Portfolio Optimizer (Multi-strategy)
```

---

## ?? Project Structure

```
Smart-Trade-MCP/
??? src/
?   ??? mcp_server/        # MCP server implementation
?   ?   ??? server.py      # Main MCP server
?   ?   ??? tools/         # MCP tools (backtest, optimize, etc.)
?   ??? strategies/        # Trading strategies
?   ?   ??? base.py        # Base strategy class
?   ?   ??? registry.py    # Strategy registry
?   ?   ??? generated/     # 42+ strategy implementations
?   ??? core/              # Core engine
?   ?   ??? backtest_engine.py
?   ?   ??? data_manager.py
?   ?   ??? indicators.py
?   ??? optimization/      # Optimization engines
?   ?   ??? genetic_optimizer.py
?   ?   ??? walk_forward.py
?   ??? portfolio/         # Portfolio management
?       ??? portfolio_optimizer.py
?       ??? portfolio_config.py
??? data/                  # Local data storage
?   ??? market/            # Market data cache (SQLite)
??? .mcp.json              # MCP config for Claude Code (CLI)
??? README.md
```

---

## ??? Development

### **Running Tests:**
```bash
python -m pytest tests/
```

### **Running MCP Server Standalone:**
```bash
python -m src.mcp_server.server
```

### **Debugging:**
- MCP server logs appear in Claude Desktop developer console
- Set `PYTHONUNBUFFERED=1` for real-time logging
- Use `logger.info()` for debugging (see `src/core/logger.py`)

---

## ?? Performance Benchmarks

### **Backtest Speed:**
- **CPU:** ~1000 candles/sec
- **GPU:** ~5000 candles/sec (CUDA acceleration)

### **Optimization:**
- **Genetic Algorithm:** 30 population × 10 generations = ~5 minutes
- **Walk-Forward Analysis:** 5 folds × backtest = ~2 minutes

### **Data Fetching:**
- **First fetch:** ~10 seconds (1 year hourly data)
- **Cached:** <1 second

---

## ?? Security & Privacy

- ? All data stored locally (SQLite)
- ? No data sent to external services (except exchange API for market data)
- ? API keys stored locally (not in code)
- ? MCP communication is local-only (stdio protocol)

---

## ?? Resources

- **MCP Specification:** https://modelcontextprotocol.io
- **CCXT Documentation:** https://docs.ccxt.com
- **TA-Lib Documentation:** https://ta-lib.github.io/ta-lib-python/

---

## ?? Roadmap

### **High Priority:**
- [ ] Fix 6-day data fetch issue in MCP backtest
- [ ] Add more detailed error messages
- [ ] Implement caching for optimization results

### **Medium Priority:**
- [ ] Add paper trading support
- [ ] Integrate with TradingView webhooks
- [ ] Web dashboard for portfolio monitoring

### **Low Priority:**
- [ ] Add more strategies (target: 100+)
- [ ] Machine learning strategy generator
- [ ] Multi-exchange arbitrage strategies

---

## ?? Support

For issues or questions:
1. Check this documentation
2. Review MCP server logs in Claude Desktop
3. Test tools directly (see Development section)
4. Create GitHub issue with reproduction steps

---

**Built with ?? by Smart-Trade-MCP Team**

**Version:** 2.0.0-auto-fetch  
**Last Updated:** 2025-11-21
