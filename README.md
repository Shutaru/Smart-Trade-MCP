# ?? Smart Trade MCP

**Autonomous trading system built on Model Context Protocol (MCP) architecture**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-45%20passing-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-65%25-yellow.svg)]()

---

## ?? Overview

Smart Trade MCP is a **production-ready autonomous trading system** that leverages:

- ?? **MCP Architecture** - Clean separation of concerns with Model Context Protocol
- ?? **Strategy System** - Extensible strategy framework (RSI, MACD, and more)
- ? **GPU Optimization** - CUDA-accelerated indicator calculations (optional)
- ?? **Backtest Engine** - Professional backtesting with position tracking
- ?? **Data Management** - Automatic fetching and caching from exchanges
- ?? **Type-Safe** - Full type hints and Pydantic validation

---

## ? Features

### Implemented (Phase 2 Complete)
? **Database Manager** - SQLite with async support (90% test coverage)  
? **Data Manager** - CCXT integration for exchange data  
? **7 Technical Indicators** - EMA, RSI, MACD, Bollinger Bands, ATR, ADX  
? **Strategy System** - Base class + RSI and MACD strategies  
? **Backtest Engine** - Full position tracking, SL/TP, metrics (87% coverage)  
? **45 Tests** - Comprehensive test suite with 65% coverage  
? **Zero Deprecated Code** - Clean, production-ready architecture  

### Coming Soon (Phase 3-5)
?? Genetic Algorithm Optimization  
?? Meta-Learning for parameter prediction  
?? Walk-Forward Validation  
?? Live Trading Mode  
?? Web Dashboard  

---

## ?? Quick Start

### Prerequisites

- Python 3.11+
- Poetry (package manager)
- Optional: CUDA 12.x for GPU acceleration

### Installation

```bash
# Clone repository
git clone https://github.com/Shutaru/Smart-Trade-MCP.git
cd Smart-Trade-MCP

# Install dependencies with Poetry
poetry install

# Copy environment template
cp .env.example .env

# Edit .env with your settings (optional for backtesting)
```

### Running Examples

#### 1. List Available Strategies

```bash
poetry run python examples/list_strategies.py
```

Output:
```
Strategy: rsi
   Class: RSIStrategy
   Description: Classic RSI oversold/overbought strategy
   Required Indicators: rsi, atr
   
   Default Parameters:
      - rsi_period: 14
      - oversold_level: 30
      - overbought_level: 70
      - exit_level: 50
```

#### 2. Run a Simple Backtest

```bash
poetry run python examples/simple_backtest.py
```

This will:
1. Fetch 30 days of BTC/USDT data from Binance
2. Calculate RSI indicator
3. Run backtest with $10,000 initial capital
4. Display results with metrics

---

## ?? Usage Examples

### Example 1: Fetch Market Data

```python
from src.core.data_manager import DataManager
from datetime import datetime, timedelta

async def fetch_data():
    dm = DataManager()
    
    # Fetch recent data
    df = await dm.fetch_ohlcv(
        symbol="BTC/USDT",
        timeframe="1h",
        limit=100
    )
    
    # Or fetch historical range
    df = await dm.fetch_historical(
        symbol="BTC/USDT",
        timeframe="1h",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now()
    )
    
    await dm.close()
    return df
```

### Example 2: Calculate Indicators

```python
from src.core.indicators import calculate_all_indicators

# Add indicators to your DataFrame
df = calculate_all_indicators(df, ['rsi', 'macd', 'ema'])

# Now df has columns: rsi, macd, macd_signal, macd_hist, ema_12, ema_26
```

### Example 3: Run a Backtest

```python
from src.core.backtest_engine import BacktestEngine
from src.strategies import registry

# Get strategy
strategy = registry.get("rsi")

# Run backtest
engine = BacktestEngine(initial_capital=10000.0)
results = engine.run(strategy, df)

print(f"Total Return: {results['total_return']:.2f}%")
print(f"Win Rate: {results['metrics']['win_rate']:.1f}%")
print(f"Sharpe Ratio: {results['metrics']['sharpe_ratio']:.2f}")
```

### Example 4: Create Custom Strategy

```python
from src.strategies import BaseStrategy, Signal, SignalType
import pandas as pd

class MyStrategy(BaseStrategy):
    """Custom strategy example."""
    
    def get_required_indicators(self):
        return ["rsi", "ema"]
    
    def generate_signals(self, df: pd.DataFrame):
        signals = []
        
        for i in range(1, len(df)):
            row = df.iloc[i]
            
            # Your logic here
            if row["rsi"] < 30 and row["close"] > row["ema_12"]:
                signals.append(Signal(
                    type=SignalType.LONG,
                    timestamp=row["timestamp"],
                    price=row["close"],
                ))
        
        return signals
```

---

## ?? Running Tests

```bash
# All tests
poetry run pytest

# With coverage report
poetry run pytest --cov=src --cov-report=html

# Specific test file
poetry run pytest tests/unit/test_strategies.py -v

# Run fast (skip slow tests)
poetry run pytest -m "not slow"
```

### Current Test Status
- **45 tests** passing
- **65% code coverage**
- **Modules with 90%+ coverage**: Database, Strategies, Base Strategy

---

## ??? Architecture

```
Smart-Trade-MCP/
??? src/
?   ??? core/                    # Business Logic
?   ?   ??? config.py           # Pydantic settings
?   ?   ??? database.py         # SQLite manager (90% coverage)
?   ?   ??? data_manager.py     # Exchange data fetching
?   ?   ??? indicators.py       # Technical indicators (77% coverage)
?   ?   ??? backtest_engine.py  # Backtesting (87% coverage)
?   ?   ??? logger.py           # Logging setup (100% coverage)
?   ?
?   ??? strategies/              # Trading Strategies
?   ?   ??? base.py             # Abstract base (90% coverage)
?   ?   ??? rsi_strategy.py     # RSI strategy (94% coverage)
?   ?   ??? macd_strategy.py    # MACD strategy (68% coverage)
?   ?   ??? registry.py         # Strategy registry (96% coverage)
?   ?
?   ??? mcp_server/              # MCP Protocol Layer
?       ??? server.py           # Main MCP server
?       ??? tools/              # MCP tools
?       ??? resources/          # Dynamic resources
?
??? tests/                       # Test Suite
?   ??? unit/                   # Unit tests (32 tests)
?   ??? integration/            # Integration tests (2 tests)
?
??? examples/                    # Usage examples
    ??? list_strategies.py
    ??? simple_backtest.py
```

---

## ??? Available Strategies

| Strategy | Category | Description | Indicators |
|----------|----------|-------------|------------|
| **rsi** | Mean Reversion | Classic RSI oversold/overbought | RSI, ATR |
| **macd** | Trend Following | MACD crossover signals | MACD, ATR |

More strategies coming in Phase 3!

---

## ?? Performance Metrics

The backtest engine calculates:

- **Total Return** - Overall profit/loss percentage
- **Win Rate** - Percentage of winning trades
- **Profit Factor** - Gross profit / Gross loss
- **Sharpe Ratio** - Risk-adjusted returns
- **Max Drawdown** - Largest peak-to-trough decline
- **Average Win/Loss** - Mean profit and loss per trade

---

## ?? Contributing

This is a production-ready project following best practices:

1. **No deprecated code** - Delete immediately, no "TODO: Remove later"
2. **Type everything** - Full type hints, mypy compliant
3. **Test everything** - Target >70% coverage
4. **Document as you go** - Docstrings for all public APIs
5. **Clean commits** - Conventional commits format

---

## ?? License

MIT License - see [LICENSE](LICENSE) file

---

## ?? Acknowledgments

- Built on [Model Context Protocol](https://modelcontextprotocol.io/)
- Uses [CCXT](https://github.com/ccxt/ccxt) for exchange connectivity
- Inspired by quantitative trading research

---

## ?? Support

For questions or issues:
- ?? Check the [examples/](examples/) directory
- ?? Open an issue on GitHub
- ?? Read the [PROGRESS_REPORT.md](PROGRESS_REPORT.md)

---

**Built with ?? for autonomous trading**

**Current Status:** ? Phase 2 Complete - Ready for backtesting!
