# ?? Autonomous Trading Agent - Quick Start

**Version:** 1.0.0  
**Status:** ? Ready to Use

---

## ?? **What is This?**

**Autonomous trading agent** that:
- ?? Scans multiple trading pairs automatically
- ?? Runs every X minutes (configurable)
- ?? Generates trading signals using 42+ strategies
- ?? Saves signals to database
- ?? (Optional) Sends alerts via Telegram/Email

**Completely standalone!** No manual intervention needed.

---

## ?? **Quick Start (3 Steps)**

### **1. Configure Your Agent**

Edit `config/agent_config.yaml`:

```yaml
# Which pairs to monitor
pairs:
  - symbol: "BTC/USDT"
    timeframe: "1h"
    enabled: true
  
  - symbol: "ETH/USDT"
    timeframe: "1h"
    enabled: true

# Which strategies to use
strategies:
  - name: "cci_extreme_snapback"  # Best performer!
    enabled: true
    min_confidence: 0.75

# How often to scan (minutes)
scanner:
  scan_interval_minutes: 15  # Every 15 minutes
```

### **2. Start the Agent**

```bash
# Start autonomous agent (runs forever)
python start_agent.py

# OR: Run single scan and exit
python start_agent.py --once

# OR: Check status
python start_agent.py --status
```

### **3. View Signals**

Signals are saved to `data/signals.db` (SQLite)

```python
from src.agent import SignalStorage

storage = SignalStorage("data/signals.db")
signals = storage.get_active_signals()

for signal in signals:
    print(f"{signal['symbol']} {signal['direction']} @ {signal['entry_price']}")
```

---

## ?? **Configuration Options**

### **Trading Pairs**

```yaml
pairs:
  - symbol: "BTC/USDT"    # Trading pair
    timeframe: "1h"        # Candle timeframe
    enabled: true          # Enable/disable
```

**Supported timeframes:** `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`

### **Strategies**

```yaml
strategies:
  - name: "cci_extreme_snapback"  # Strategy name
    enabled: true                  # Enable/disable
    min_confidence: 0.75           # Minimum signal confidence (0-1)
```

**Best strategies** (from backtests):
1. `cci_extreme_snapback` - +7.91% return, 72% win rate ?
2. `bollinger_mean_reversion` - +3.20% return, 62% win rate
3. `atr_expansion_breakout` - +2.39% return, 57% win rate

### **Scan Settings**

```yaml
scanner:
  scan_interval_minutes: 15  # How often to scan
  lookback_candles: 500       # How many candles to analyze
  parallel_scanning: true     # Scan pairs in parallel
  max_workers: 4              # Number of parallel workers
```

**Recommended intervals:**
- **Day Trading:** 5-15 minutes
- **Swing Trading:** 30-60 minutes
- **Position Trading:** 240 minutes (4 hours)

---

## ??? **Usage Modes**

### **Mode 1: Autonomous (Scheduled)**

Run forever, scan every X minutes:

```bash
python start_agent.py
```

**Output:**
```
================================================================================
STARTING AUTONOMOUS TRADING AGENT
================================================================================
Scan interval: 15 minutes
Monitoring: 3 pairs
Strategies: 3 active
================================================================================
? Agent started successfully!
Next scan: 2025-11-21 20:15:00
Press Ctrl+C to stop
================================================================================
```

### **Mode 2: Single Scan**

Run once and exit:

```bash
python start_agent.py --once
```

**Good for:**
- Testing configuration
- Manual signal generation
- Cron jobs

### **Mode 3: Status Check**

Check agent status:

```bash
python start_agent.py --status
```

---

## ?? **Signal Database**

All signals are saved to SQLite: `data/signals.db`

**Tables:**
- `signals` - All generated signals
- `signal_history` - Signal lifecycle events

**Query examples:**

```python
from src.agent import SignalStorage

storage = SignalStorage("data/signals.db")

# Get active signals
active = storage.get_active_signals()

# Get signals for BTC/USDT
btc_signals = storage.get_active_signals(symbol="BTC/USDT")

# Get statistics
stats = storage.get_statistics()
print(f"Total signals: {stats['total_signals']}")
print(f"Active: {stats['active_signals']}")
```

---

## ?? **Alerts (Optional)**

Enable notifications when signals are found:

### **Telegram**

```yaml
alerts:
  telegram_enabled: true
  telegram_bot_token: "YOUR_BOT_TOKEN"
  telegram_chat_id: "YOUR_CHAT_ID"
```

### **Email**

```yaml
alerts:
  email_enabled: true
  email_to: "you@example.com"
```

### **Webhook**

```yaml
alerts:
  webhook_enabled: true
  webhook_url: "https://your-webhook.com/signals"
```

---

## ?? **Example Output**

```
?? Starting scan...
Scanning 3 pairs with 3 strategies

?? SIGNAL FOUND: BTC/USDT | cci_extreme_snapback | LONG @ 95000.00 | R/R: 2.50 | Confidence: 85.00%
?? SIGNAL FOUND: ETH/USDT | bollinger_mean_reversion | LONG @ 3500.00 | R/R: 2.00 | Confidence: 78.00%

================================================================================
? Scan complete!
Found 2 signals in 5.23 seconds
Average: 0.58s per pair/strategy
================================================================================

================================================================================
SCAN RESULTS
================================================================================
Total signals: 2
By symbol: {'BTC/USDT': 1, 'ETH/USDT': 1}
By strategy: {'cci_extreme_snapback': 1, 'bollinger_mean_reversion': 1}
Long/Short: 2/0
Avg confidence: 81.50%
Avg R/R: 2.25
================================================================================

?? Saved 2 signals to database
```

---

## ??? **Customization**

### **Add More Pairs**

```yaml
pairs:
  - symbol: "ADA/USDT"
    timeframe: "1h"
    enabled: true
  
  - symbol: "MATIC/USDT"
    timeframe: "1h"
    enabled: true
```

### **Add More Strategies**

List all available strategies:

```python
from src.strategies import registry

all_strategies = registry.list_all()
print(f"Total strategies: {len(all_strategies)}")
for name in all_strategies:
    print(f"  - {name}")
```

### **Change Scan Interval**

```yaml
scanner:
  scan_interval_minutes: 5  # Scan every 5 minutes
```

---

## ?? **Monitoring**

### **Check Logs**

Logs are saved to `logs/` folder:

```bash
tail -f logs/smart_trade.log
```

### **Database Stats**

```bash
python -c "
from src.agent import SignalStorage
storage = SignalStorage('data/signals.db')
stats = storage.get_statistics()
print(f'Total signals: {stats[\"total_signals\"]}')
print(f'Active: {stats[\"active_signals\"]}')
"
```

---

## ?? **Production Deployment**

### **Run as System Service (Linux)**

Create `/etc/systemd/system/smart-trade.service`:

```ini
[Unit]
Description=Smart-Trade Autonomous Trading Agent
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/Smart-Trade-MCP
ExecStart=/path/to/python /path/to/start_agent.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable smart-trade
sudo systemctl start smart-trade
sudo systemctl status smart-trade
```

### **Run in Docker**

```dockerfile
FROM python:3.10

WORKDIR /app
COPY . .

RUN pip install poetry && poetry install

CMD ["python", "start_agent.py"]
```

---

## ?? **FAQ**

**Q: How do I stop the agent?**  
A: Press `Ctrl+C` or send SIGTERM signal.

**Q: Can I change config while agent is running?**  
A: No, restart the agent after config changes.

**Q: How many pairs can I monitor?**  
A: No limit, but more pairs = longer scan time.

**Q: What happens if a scan takes longer than the interval?**  
A: Next scan will wait until current scan finishes.

**Q: Can I run multiple agents?**  
A: Yes, use different config files and database paths.

---

## ?? **Next Steps**

1. ? Configure your pairs/strategies
2. ? Test with `--once`
3. ? Start autonomous agent
4. ?? Implement paper trading (coming soon!)
5. ?? Connect to live trading (coming soon!)

---

**Happy Trading!** ??

**Version:** 1.0.0  
**Status:** Production Ready  
**Support:** See main README.md
