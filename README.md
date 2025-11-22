# 🚀 Smart-Trade MCP - Professional Algorithmic Trading Platform

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![MCP](https://img.shields.io/badge/MCP-2.0-purple.svg)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Smart-Trade MCP** is a production-ready algorithmic trading platform featuring:
- 🎯 **42+ Built-in Strategies** (Breakout, Trend, Mean Reversion, Momentum, Hybrid, Advanced)
- ⚡ **Batch Processing** - Compare 41 strategies in 15 seconds (20-30x faster!)
- 🔧 **Claude Desktop Integration** - MCP protocol for AI-powered analysis
- 🌐 **REST API** - FastAPI backend for universal access
- 📊 **GPU-Accelerated** - High-performance backtesting engine
- 🎓 **Professional Tools** - WFA, K-Fold, Genetic Algorithm, Portfolio Optimization

---

## 📊 **Current Status: v3.0.0 Production Ready**

| Component | Status | Version | Performance |
|-----------|--------|---------|-------------|
| **MCP Server** | ✅ Operational | 2.0.2-optimized | 16 tools available |
| **FastAPI Backend** | ✅ Operational | 3.0.0 | 11 endpoints |
| **Batch Processing** | ✅ Operational | 2.0.0 | 20-30x faster |
| **Strategies** | ✅ Ready | 42+ | All categories |
| **Data Engine** | ✅ Optimized | 2.0.0 | 364 days, 8760 candles |
| **Frontend** | 🟡 Partial | 1.0.0 | Ready to connect |

### **Recent Updates (v3.0.0):**
- ✅ **FastAPI REST API** - Production-grade backend
- ✅ **Batch Comparison** - 20-30x faster than individual calls
- ✅ **Response Optimization** - 3KB vs 500KB (166x smaller)
- ✅ **System Prompts** - Optimized Claude Desktop interaction
- ✅ **Full Documentation** - Heritage, guides, and examples

---

## 🎯 **Quick Start**

### **1. Claude Desktop (MCP Protocol)**

Already configured! Just ask Claude:

```
Claude, compare ALL strategies on BTC/USDT 1h using batch processing.
Show me top 10 by Sharpe Ratio.
```

**Available Commands:**
- `list strategies` - Get all 42+ strategies
- `backtest [strategy]` - Run single backtest
- `compare strategies` - Batch comparison (FAST!)
- `detect market regime` - Identify current market
- `optimize portfolio` - Multi-strategy allocation

### **2. FastAPI Backend**

```bash
# Install dependencies
poetry install

# Start API server
poetry run uvicorn src.api.main:app --reload

# Open interactive docs
http://localhost:8000/api/docs
```

**Key Endpoints:**
- `POST /api/v1/backtest/compare` - Batch comparison ⭐
- `POST /api/v1/backtest/single` - Single backtest
- `GET /api/v1/strategies/` - List strategies
- `POST /api/v1/market/regime` - Detect regime
- `POST /api/v1/optimization/portfolio` - Optimize portfolio

---

## 🏗️ **Architecture**

```
┌────────────────────────────────────────────────────────┐
│                   USERS / CLIENTS                      │
│                                                        │
│  Claude Desktop  │  REST API  │  Frontend  │  Mobile   │
└────────┬─────────┴─────┬──────┴─────┬──────┴──────┬────┘
         │               │            │             │
    MCP Protocol     HTTP/REST    HTTP/REST    HTTP/REST
         │               │            │             │
┌────────▼───────────────▼────────────▼─────────────▼────┐
│              SMART-TRADE PLATFORM                      │
├────────────────────────────────────────────────────────┤
│  MCP Server (stdio)     │    FastAPI Backend (HTTP)    │
│  • 16 MCP Tools         │    • 11 REST Endpoints       │
│  • Batch Processing     │    • OpenAPI Docs            │
│  • Claude Integration   │    • CORS / Compression      │
├────────────────────────────────────────────────────────┤
│                    CORE ENGINES                        │
│  • Strategy Registry (42+ strategies)                  │
│  • Backtest Engine (GPU/CPU accelerated)               │
│  • Data Manager (CCXT + SQLite cache)                  │
│  • Optimization Engine (GA, WFA, K-Fold)               │
│  • Portfolio Optimizer (Multi-strategy)                │
└────────────────────────────────────────────────────────┘
```

---

## 📁 **Project Structure**

```
Smart-Trade-MCP/
├── src/
│   ├── api/                     # FastAPI Backend (v3.0.0) ✨ NEW
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Settings
│   │   ├── models/              # Pydantic schemas
│   │   └── routers/             # API endpoints
│   │       ├── strategies.py    # 4 endpoints
│   │       ├── backtest.py      # 3 endpoints (batch!)
│   │       ├── optimization.py  # 2 endpoints
│   │       ├── market.py        # 1 endpoint
│   │       └── portfolio.py     # 1 endpoint
│   │
│   ├── mcp_server/              # MCP Server (v2.0.2)
│   │   ├── server.py            # MCP protocol handler
│   │   └── tools/               # 16 MCP tools
│   │       ├── backtest.py      # Optimized (3KB response)
│   │       ├── batch_compare.py # ✨ Batch processing
│   │       ├── strategies.py
│   │       ├── regime.py
│   │       ├── optimization.py
│   │       └── ...
│   │
│   ├── strategies/              # Trading Strategies
│   │   ├── base.py              # BaseStrategy class
│   │   ├── registry.py          # Auto-registration
│   │   └── generated/           # 42+ implementations
│   │       ├── breakout/        # 12 strategies
│   │       ├── trend/           # 8 strategies
│   │       ├── mean_reversion/  # 6 strategies
│   │       ├── momentum/        # 8 strategies
│   │       ├── hybrid/          # 6 strategies
│   │       └── advanced/        # 2 strategies
│   │
│   ├── core/                    # Core Engine
│   │   ├── backtest_engine.py   # GPU/CPU execution
│   │   ├── data_manager.py      # CCXT + SQLite
│   │   ├── indicators.py        # TA-Lib wrapper
│   │   └── risk_manager.py      # Position sizing
│   │
│   ├── optimization/            # Optimization
│   │   ├── genetic_optimizer.py # GA
│   │   ├── walk_forward.py      # WFA
│   │   ├── k_fold.py            # K-Fold
│   │   └── monte_carlo.py       # Monte Carlo
│   │
│   └── portfolio/               # Portfolio Management
│       ├── portfolio_optimizer.py
│       └── portfolio_config.py
│
├── data/market/                 # SQLite cache
├── logs/                        # Auto-generated logs
├── docs/                        # Documentation
│   ├── Heritage.md              # Complete system docs
│   ├── ROADMAP.md               # Development roadmap ✨ NEW
│   ├── FASTAPI_BACKEND_V3.md    # API guide
│   └── ...
│
├── frontend/                    # React frontend (partial)
├── tests/                       # Test scripts
├── pyproject.toml               # Poetry dependencies
└── README.md                    # This file
```

---

## 🛠️ **MCP Tools (Claude Desktop)**

### **Category 1: Strategy Comparison**
- `list_strategies` - List all 42+ strategies
- `backtest_strategy` - Single backtest (1-2 sec)
- **`compare_strategies`** ⭐ - Batch comparison (15 sec for 41!)

### **Category 2: Optimization**
- `optimize_strategy_parameters` - Genetic Algorithm
- `optimize_portfolio` - Multi-strategy allocation

### **Category 3: Validation**
- `run_walk_forward_analysis` - Time-series validation
- `run_k_fold_validation` - Cross-validation
- `run_monte_carlo_simulation` - Risk analysis

### **Category 4: Market Analysis**
- `detect_market_regime` - Current regime detection
- `detect_historical_regimes` - Historical analysis

### **Category 5: Diagnostics**
- `diagnose_strategy_failure` - Why strategy failed
- `suggest_parameter_fixes` - Parameter recommendations

---

## 📊 **Strategy Categories**

| Category | Count | Description | Best For |
|----------|-------|-------------|----------|
| **Breakout** | 12 | High-volatility expansion | Trending, high vol |
| **Trend** | 8 | Momentum-based following | Strong trends |
| **Mean Reversion** | 6 | Counter-trend extremes | Ranging, low vol |
| **Momentum** | 8 | Oscillator-based | Medium vol, trending |
| **Hybrid** | 6 | Combined approaches | All conditions |
| **Advanced** | 2 | Multi-component adaptive | Adaptive |

**Top Performers (Last Year):**
1. `cci_extreme_snapback` - +7.91% return, 72.15% win rate ⭐
2. `bollinger_mean_reversion` - +3.20% return, 61.61% win rate
3. `atr_expansion_breakout` - +2.39% return, 57.14% win rate

---

## ⚡ **Performance Benchmarks**

### **Batch Processing** (Game Changer!)

| Strategies | Individual Calls | Batch Processing | Speedup |
|------------|------------------|------------------|---------|
| 5 | 5 seconds | 3 seconds | **1.7x** |
| 10 | 10 seconds | 5 seconds | **2x** |
| 41 | 5 minutes | 15 seconds | **20x** ⚡ |

### **Backtest Speed**
- CPU Mode: ~1,000 candles/second
- GPU Mode: ~5,000 candles/second (CUDA)

### **Optimization**
- Genetic Algorithm: 30 pop × 10 gen = 2-5 min
- Walk-Forward Analysis: 5 folds = 2-3 min
- Portfolio Optimization: 10 strategies = 2-3 min

### **Data Fetching**
- First fetch: ~10 sec (1 year, 8760 candles)
- Cached: <1 second

---

## 📚 **Usage Examples**

### **Claude Desktop (MCP)**

```
# List strategies
Claude, list all mean reversion strategies

# Single backtest
Claude, backtest cci_extreme_snapback on BTC/USDT 1h

# Batch comparison (FAST!)
Claude, compare ALL strategies on BTC/USDT 1h using batch processing.
Show me top 10 by Sharpe Ratio.

# Market regime
Claude, detect current market regime for BTC/USDT 
and recommend top 3 strategies

# Portfolio optimization
Claude, optimize portfolio with top 5 strategies by Sharpe.
Use max_sharpe method.
```

### **FastAPI (REST)**

```bash
# List strategies
curl http://localhost:8000/api/v1/strategies/

# Batch comparison
curl -X POST http://localhost:8000/api/v1/backtest/compare \
  -H "Content-Type: application/json" \
  -d '{
    "strategies": ["cci_extreme_snapback", "bollinger_mean_reversion"],
    "symbol": "BTC/USDT",
    "timeframe": "1h"
  }'

# Detect market regime
curl -X POST http://localhost:8000/api/v1/market/regime \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC/USDT", "lookback": 100}'
```

### **Frontend (React/Vue)**

```typescript
import axios from 'axios';

// Batch comparison
const { data } = await axios.post('/api/v1/backtest/compare', {
  strategies: ['cci_extreme_snapback', 'bollinger_mean_reversion'],
  symbol: 'BTC/USDT',
  timeframe: '1h'
});

console.log(data.top_3_by_sharpe);
```

---

## 🔧 **Installation & Setup**

### **Prerequisites**
- Python 3.10+
- Poetry (package manager)
- TA-Lib (technical analysis library)
- Optional: CUDA 12.x for GPU acceleration

### **Quick Install**

```bash
# Clone repository
git clone https://github.com/Shutaru/Smart-Trade-MCP.git
cd Smart-Trade-MCP

# Install dependencies
poetry install

# Optional: GPU support
poetry install -E gpu

# Configure Claude Desktop
# Copy config to: %APPDATA%/Claude/claude_desktop_config.json
```

### **MCP Configuration**

**Claude Desktop:** `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "smart-trade": {
      "command": "python",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "C:\\path\\to\\Smart-Trade-MCP",
      "env": {
        "PYTHONPATH": "C:\\path\\to\\Smart-Trade-MCP"
      }
    }
  }
}
```

### **Start Services**

```bash
# MCP Server (auto-started by Claude Desktop)
# Manual: python -m src.mcp_server.server

# FastAPI Backend
poetry run uvicorn src.api.main:app --reload

# Frontend (if developing)
cd frontend && npm run dev
```

---

## 🎯 **Development Roadmap**

See [`ROADMAP.md`](ROADMAP.md) for detailed development plan.

### **Completed ✅**
- MCP Server with 16 tools
- FastAPI Backend v3.0.0
- Batch processing (20-30x faster)
- 42+ trading strategies
- Response optimization (166x smaller)

### **In Progress 🚧**
- Signal Scanner (real-time signals)
- Experiment Manager (track tests)
- Frontend integration

### **Planned 📋**
- Paper Trading Engine
- TradingView webhooks
- Telegram notifications
- Multi-exchange support

---

## 📖 **Documentation**

- **[Heritage.md](Heritage.md)** - Complete system documentation
- **[ROADMAP.md](ROADMAP.md)** - Development roadmap
- **[FASTAPI_BACKEND_V3.md](FASTAPI_BACKEND_V3.md)** - API guide
- **[SYSTEM_MESSAGE.md](SYSTEM_MESSAGE.md)** - Claude Desktop prompts
- **[MCP_TOOLS_CATEGORIZED.md](MCP_TOOLS_CATEGORIZED.md)** - Tool reference

---

## 🔐 **Security & Privacy**

- ✅ All data stored locally (SQLite)
- ✅ No external analytics or tracking
- ✅ API keys stay local (not in code)
- ✅ MCP communication is local-only
- ✅ Optional API authentication (production)

---

## 🤝 **Contributing**

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Follow existing code style
4. Add tests for new features
5. Update documentation
6. Submit pull request

---

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [CCXT](https://github.com/ccxt/ccxt) - Cryptocurrency exchange API
- [TA-Lib](https://ta-lib.org/) - Technical analysis library
- [MCP](https://modelcontextprotocol.io) - Model Context Protocol

---

## 📞 **Support**

- 📚 Documentation: See `docs/` folder
- 🐛 Issues: [GitHub Issues](https://github.com/Shutaru/Smart-Trade-MCP/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/Shutaru/Smart-Trade-MCP/discussions)

---

**Built with ❤️ by Smart-Trade MCP Team**

**Version:** 3.0.0  
**Status:** ✅ Production Ready  
**Last Updated:** 2025-11-21

---

## 🚀 **Getting Started (3 Steps)**

```bash
# 1. Install
poetry install

# 2. Start API
poetry run uvicorn src.api.main:app --reload

# 3. Ask Claude
"Claude, compare ALL strategies on BTC/USDT 1h!"
```

**That's it!** 🎉
