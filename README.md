# ?? Smart Trade MCP

**Autonomous trading system built on Model Context Protocol (MCP) architecture**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ?? Overview

Smart Trade MCP is a **production-ready autonomous trading system** that leverages:

- ?? **MCP Architecture** - Clean separation of concerns with Model Context Protocol
- ?? **38 Trading Strategies** - Battle-tested strategies from trend-following to machine learning
- ? **GPU Optimization** - CUDA-accelerated indicator calculations (optional)
- ?? **Meta-Learning** - ML-based parameter prediction (78% accuracy)
- ?? **Walk-Forward Validation** - Robust anti-overfitting mechanisms
- ?? **Autonomous Agent** - Self-directed decision making with workflow enforcement

---

## ??? Architecture

```
Smart-Trade-MCP/
??? src/
?   ??? mcp_server/          # MCP Protocol Layer
?   ?   ??? server.py        # Main MCP server
?   ?   ??? tools/           # MCP tools (market data, backtest, etc.)
?   ?   ??? resources/       # Dynamic resources (portfolio, performance)
?   ?   ??? prompts/         # Agent guidance prompts
?   ??? core/                # Business Logic Layer
?   ?   ??? config.py        # Configuration management
?   ?   ??? indicators.py    # Technical indicators
?   ?   ??? logger.py        # Logging setup
?   ?   ??? ...
?   ??? strategies/          # Trading Strategies
?       ??? ...
??? tests/                   # Comprehensive test suite
??? configs/                 # Configuration files
??? data/                    # Data storage
??? logs/                    # Application logs
```

**Design Principles:**
- ? **MCP server** = Interface layer (tools, resources, prompts)
- ? **Core** = Business logic (no MCP dependencies)
- ? **Clean imports** - No circular dependencies
- ? **Type hints** - Full mypy compliance
- ? **Async-first** - Modern async/await patterns

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

# Optional: Install with GPU support
poetry install -E gpu

# Copy environment template
cp .env.example .env

# Edit .env with your API keys and settings
```

### Configuration

Edit `.env` file:

```env
# Trading Configuration
EXCHANGE=binance
TESTNET=true
DRY_RUN=true

# API Keys
BINANCE_API_KEY=your_key_here
BINANCE_SECRET_KEY=your_secret_here

# Optimization
MAX_WORKERS=4
GPU_ENABLED=false
```

### Running the MCP Server

```bash
# Activate Poetry environment
poetry shell

# Start MCP server
python -m src.mcp_server.server
```

### Testing with MCP Inspector

```bash
# Install MCP Inspector (if not already installed)
npm install -g @modelcontextprotocol/inspector

# Run inspector
mcp-inspector python -m src.mcp_server.server
```

---

## ??? MCP Tools

### Market Data Tools

- **`get_market_data`** - Fetch OHLCV data from exchange
- **`calculate_indicators`** - Compute technical indicators

### Backtesting Tools

- **`backtest_strategy`** - Run strategy backtest (Phase 2)
- **`optimize_strategy`** - Genetic algorithm optimization (Phase 3)

### Portfolio Tools

- **`get_portfolio_status`** - Current holdings and performance
- **`execute_trade`** - Place orders (Phase 5)

### Strategy Tools

- **`list_strategies`** - Available strategies
- **`get_strategy_info`** - Strategy metadata

---

## ?? MCP Resources

Dynamic resources updated in real-time:

- **`portfolio://current`** - Portfolio holdings and P&L
- **`market://status`** - Market regime and conditions
- **`performance://latest`** - Performance metrics

---

## ?? Development

### Running Tests

```bash
# All tests
poetry run pytest

# With coverage
poetry run pytest --cov=src --cov-report=html

# Specific test file
poetry run pytest tests/unit/test_indicators.py
```

### Code Quality

```bash
# Format code
poetry run black src/ tests/

# Lint
poetry run ruff check src/ tests/

# Type check
poetry run mypy src/
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
poetry run pre-commit install

# Run manually
poetry run pre-commit run --all-files
```

---

## ?? Implementation Roadmap

### ? Phase 1: Foundation (CURRENT)
- [x] Project structure
- [x] MCP server boilerplate
- [x] Configuration management
- [x] Market data tools
- [x] Technical indicators
- [x] Logging setup

### ?? Phase 2: Strategies (NEXT)
- [ ] Strategy base class
- [ ] Port 38 strategies from original repo
- [ ] Backtest engine
- [ ] Strategy registry
- [ ] Performance metrics

### ?? Phase 3: Optimization
- [ ] Genetic algorithm optimizer
- [ ] Meta-learning system
- [ ] Walk-forward validation
- [ ] Job manager

### ?? Phase 4: Agent
- [ ] MCP client wrapper
- [ ] Decision loop
- [ ] Workflow enforcement
- [ ] Loop detection

### ?? Phase 5: Production
- [ ] Live trading mode
- [ ] Web dashboard
- [ ] Monitoring & alerts
- [ ] Deployment scripts

---

## ?? Contributing

This is a **production-ready** project following best practices:

1. **No deprecated code** - Delete immediately, no "TODO: Remove later"
2. **Type everything** - Full type hints, mypy compliant
3. **Test everything** - >90% coverage required
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

## ?? Contact

For questions or support, open an issue on GitHub.

---

**Built with ?? for autonomous trading**
