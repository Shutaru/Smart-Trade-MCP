"""Deep debug of backtest cash flow."""

import asyncio
from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators
from src.core.backtest_engine import BacktestEngine
from src.strategies import registry


class DebugBacktestEngine(BacktestEngine):
    """Backtest engine with cash flow logging."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cash_log = [(0, self.cash, "Initial")]
    
    def _open_position(self, *args, **kwargs):
        super()._open_position(*args, **kwargs)
        self.cash_log.append((len(self.cash_log), self.cash, f"After OPEN {self.position.side.value if self.position else '?'}"))
    
    def _close_position(self, *args, **kwargs):
        side = self.position.side.value if self.position else "?"
        super()._close_position(*args, **kwargs)
        self.cash_log.append((len(self.cash_log), self.cash, f"After CLOSE {side}"))


async def debug():
    dm = DataManager()
    df = await dm.fetch_ohlcv(
        symbol="BTC/USDT",
        timeframe="1h",
        exchange="binance",
        limit=500,
        use_cache=False
    )
    await dm.close()
    
    strategy = registry.get("rsi")
    df = calculate_all_indicators(df, strategy.get_required_indicators())
    
    engine = DebugBacktestEngine(initial_capital=10000.0)
    results = engine.run(strategy, df)
    
    print("CASH FLOW LOG:")
    print("-" * 60)
    for step, cash, desc in engine.cash_log:
        print(f"{step:2d}. ${cash:10,.2f} - {desc}")
    
    print()
    print(f"Final cash: ${engine.cash:,.2f}")
    print(f"Final equity: ${results['final_equity']:,.2f}")
    print(f"Open position: {engine.position is not None}")
    
    if engine.position:
        print(f"Position value: ${engine.position.entry_price * engine.position.quantity:,.2f}")


asyncio.run(debug())
