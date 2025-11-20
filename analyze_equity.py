"""Analyze equity calculation bug."""

import asyncio
from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators
from src.core.backtest_engine import BacktestEngine
from src.strategies import registry


async def analyze():
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
    
    engine = BacktestEngine(initial_capital=10000.0)
    results = engine.run(strategy, df)
    
    # Sum all P&Ls
    total_pnl = sum(t['pnl'] for t in results['trades'])
    expected_final = 10000 + total_pnl
    actual_final = results['final_equity']
    
    print(f"Initial: $10,000")
    print(f"Sum of all P&Ls: ${total_pnl:,.2f}")
    print(f"Expected final equity: ${expected_final:,.2f}")
    print(f"Actual final equity: ${actual_final:,.2f}")
    print(f"Difference: ${actual_final - expected_final:,.2f}")
    print()
    print("Trade P&Ls:")
    for i, t in enumerate(results['trades'], 1):
        print(f"  {i}. {t['side']:5s} P&L: ${t['pnl']:+8.2f}")
    print(f"  {'TOTAL':5s} P&L: ${total_pnl:+8.2f}")


asyncio.run(analyze())
