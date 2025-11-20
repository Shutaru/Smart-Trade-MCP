"""Debug backtest to see individual trades."""

import asyncio
from datetime import datetime, timedelta

from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators
from src.core.backtest_engine import BacktestEngine
from src.strategies import registry


async def debug_backtest():
    """Run backtest and show trade details."""
    
    # Fetch data
    dm = DataManager()
    df = await dm.fetch_ohlcv(
        symbol="BTC/USDT",
        timeframe="1h",
        exchange="binance",
        limit=500,
        use_cache=False,
    )
    await dm.close()
    
    print(f"Data: {len(df)} candles")
    print(f"Period: {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
    print(f"Price: ${df['close'].iloc[0]:.2f} -> ${df['close'].iloc[-1]:.2f}")
    print()
    
    # Calculate indicators
    strategy = registry.get("rsi")
    df = calculate_all_indicators(df, strategy.get_required_indicators())
    
    # Run backtest
    engine = BacktestEngine(initial_capital=10000.0)
    results = engine.run(strategy, df)
    
    print("=" * 80)
    print(f"STRATEGY: {strategy.name}")
    print("=" * 80)
    print(f"Initial Capital: ${results['initial_capital']:,.2f}")
    print(f"Final Equity: ${results['final_equity']:,.2f}")
    print(f"Total Return: {results['total_return']:+.2f}%")
    print(f"Total Trades: {results['total_trades']}")
    print()
    
    # Show first 5 trades
    print("FIRST 5 TRADES:")
    print("-" * 80)
    for i, trade in enumerate(results['trades'][:5], 1):
        print(f"\nTrade #{i}:")
        print(f"  Side: {trade['side']}")
        print(f"  Entry: ${trade['entry_price']:.2f} @ {trade['entry_time']}")
        print(f"  Exit:  ${trade['exit_price']:.2f} @ {trade['exit_time']}")
        print(f"  Qty: {trade['quantity']:.6f} BTC")
        print(f"  P&L: ${trade['pnl']:+.2f} ({trade['pnl_percent']:+.2f}%)")
        print(f"  Exit Reason: {trade['exit_reason']}")
        print(f"  Fees: ${trade['fees']:.2f}")
    
    print()
    print("=" * 80)
    print("EQUITY CURVE (first 10 points):")
    print("-" * 80)
    for i, point in enumerate(results['equity_curve'][:10], 1):
        print(f"{i}. {point['timestamp']}: ${point['equity']:,.2f}")
    
    # Calculate what SHOULD be realistic
    print()
    print("=" * 80)
    print("REALITY CHECK:")
    print("-" * 80)
    days = (df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).days
    print(f"Trading period: {days} days")
    print(f"Trades: {results['total_trades']}")
    print(f"Trades per day: {results['total_trades'] / days:.2f}")
    print()
    print("Realistic returns for 21 days:")
    print("  Conservative: +5% to +15%")
    print("  Aggressive: +15% to +30%")
    print("  Very risky: +30% to +50%")
    print(f"  ACTUAL: +{results['total_return']:.2f}% <- IMPOSSIBLE!")


if __name__ == "__main__":
    asyncio.run(debug_backtest())
