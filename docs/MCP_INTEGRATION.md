# ?? Smart Trade MCP - Claude Desktop Integration

Complete MCP (Model Context Protocol) integration for autonomous trading AI.

---

## ?? **SETUP - Claude Desktop:**

### **1. Install Claude Desktop**
Download from: https://claude.ai/download

### **2. Configure MCP Server**

Edit Claude Desktop config file:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "smart-trade": {
      "command": "python",
      "args": [
        "-m",
        "src.mcp_server.server"
      ],
      "cwd": "C:\\Users\\shuta\\source\\repos\\Smart-Trade-MCP",
      "env": {
        "PYTHONPATH": "C:\\Users\\shuta\\source\\repos\\Smart-Trade-MCP",
        "SMART_TRADE_ENV": "production"
      }
    }
  }
}
```

**?? IMPORTANTE:** Atualiza o `cwd` path para o teu diretório!

### **3. Restart Claude Desktop**

Fecha e abre novamente Claude Desktop para carregar o servidor MCP.

### **4. Verify Connection**

No Claude Desktop, verifica se vês o servidor "smart-trade" disponível.

---

## ?? **AVAILABLE TOOLS (15+):**

### **?? Market Data**
- `get_market_data` - Fetch OHLCV candles
- `calculate_indicators` - Calculate technical indicators

### **?? Backtesting**
- `backtest_strategy` - Run strategy backtest
- `run_walk_forward_analysis` - WFA validation
- `run_k_fold_validation` - K-Fold cross-validation
- `run_monte_carlo_simulation` - Monte Carlo risk analysis

### **?? Optimization**
- `optimize_strategy_parameters` - Genetic Algorithm optimization
- `optimize_portfolio` - Multi-strategy portfolio optimization
- `run_nfold_walk_forward` - N-Fold WFA (advanced)

### **?? Strategy Management**
- `list_strategies` - List all 42+ strategies
- `diagnose_strategy_failure` - Diagnose why strategy failed
- `suggest_parameter_fixes` - Get parameter fix suggestions

### **?? Market Regime**
- `detect_market_regime` - Detect current regime
- `detect_historical_regimes` - Historical regime analysis

### **?? Portfolio**
- `get_portfolio_status` - Current portfolio status

---

## ?? **USAGE EXAMPLES:**

### **Example 1: Optimize Strategy**
```
Claude, optimize the RSI strategy on BTC/USDT using genetic algorithm.
Use 50 population size and 20 generations.
```

### **Example 2: Portfolio Optimization**
```
Claude, create an optimized portfolio with these strategies:
- trendflow_supertrend
- rsi_band_reversion
- volume_shooter

Use max Sharpe ratio optimization.
```

### **Example 3: N-Fold WFA Validation**
```
Claude, validate the multi_oscillator_confluence strategy using 3-fold walk-forward analysis.
Use BTC/USDT 1h data.
```

### **Example 4: Market Regime Detection**
```
Claude, detect the current market regime for BTC/USDT and recommend suitable strategies.
```

---

## ?? **RESOURCES:**

Claude can access these resources directly:

- `portfolio://current` - Real-time portfolio data
- `market://status` - Current market status
- `performance://latest` - Latest performance metrics

---

## ?? **WORKFLOW EXAMPLE:**

```markdown
1. "Claude, list all available mean reversion strategies"
   ? Lists 5+ mean reversion strategies

2. "Backtest rsi_band_reversion on BTC/USDT for 6 months"
   ? Runs backtest, shows results

3. "Now validate it with walk-forward analysis"
   ? Runs WFA, checks for overfitting

4. "If it passed, optimize the parameters"
   ? Runs genetic algorithm optimization

5. "Create a portfolio with the top 3 strategies"
   ? Runs portfolio optimization
```

---

## ?? **ADVANCED FEATURES:**

### **Ray Parallel Processing**
```
Claude, optimize the portfolio using Ray parallel processing for faster execution.
```

### **Custom Parameter Spaces**
```
Claude, optimize RSI strategy but limit RSI period to 10-18 instead of default 7-21.
```

### **Regime-Aware Backtesting**
```
Claude, backtest this strategy only during trending regimes.
```

---

## ?? **TROUBLESHOOTING:**

### **Server Not Connecting:**
1. Check Python path in config
2. Verify `cwd` points to project root
3. Check Claude Desktop logs

### **Tools Not Appearing:**
1. Restart Claude Desktop
2. Check MCP server is running
3. Verify JSON config syntax

### **Import Errors:**
1. Ensure all dependencies installed: `pip install -r requirements.txt`
2. Check PYTHONPATH environment variable
3. Verify project structure

---

## ?? **PERFORMANCE:**

- **42+ Strategies** ready to use
- **Parameter spaces** defined for optimization
- **Ray parallelization** for 10-20x speedup
- **N-Fold WFA** for robust validation
- **Portfolio optimization** with 4 methods

---

## ?? **LEARN MORE:**

- MCP Protocol: https://modelcontextprotocol.io/
- Claude Desktop: https://claude.ai/desktop
- Smart Trade Docs: See `docs/` folder

---

**?? Enjoy autonomous trading with AI! ??**
