# -*- coding: utf-8 -*-
"""Quick test of fixed strategies"""
import asyncio
from datetime import datetime, timedelta
from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators
from src.core.backtest_engine import BacktestEngine
from src.strategies import registry

FIXED_STRATEGIES = [
    "multi_oscillator_confluence",
    "triple_momentum_confluence",
    "atr_expansion_breakout",
    "channel_squeeze_plus",
    "volatility_weighted_breakout",
    "london_breakout_atr",
    "mfi_impulse_momentum",
    "trend_volume_combo"
]

async def test_fixes():
    dm = DataManager()
    df = await dm.fetch_historical('BTC/USDT', '1h', datetime.now()-timedelta(days=365), datetime.now(), 'binance')
    await dm.close()
    
    df = calculate_all_indicators(df, ['rsi', 'cci', 'stochastic', 'mfi', 'macd', 'atr', 'ema', 
                                       'bollinger', 'keltner', 'adx', 'obv', 'supertrend'])
    
    print(f"{'Strategy':<40} {'Trades (Before?After)':>25} {'Win Rate':>10}")
    print("-" * 80)
    
    before_trades = {
        "multi_oscillator_confluence": 1,
        "triple_momentum_confluence": 1,
        "atr_expansion_breakout": 1,
        "channel_squeeze_plus": 1,
        "volatility_weighted_breakout": 1,
        "london_breakout_atr": 1,
        "mfi_impulse_momentum": 1,
        "trend_volume_combo": 1
    }
    
    for name in FIXED_STRATEGIES:
        s = registry.get(name)
        e = BacktestEngine(10000)
        r = e.run(s, df)
        m = r['metrics']
        
        before = before_trades[name]
        after = m['total_trades']
        change = f"{before} ? {after}"
        
        print(f"{name:40s} {change:>25s} {m['win_rate']:>9.1f}%")
    
    print()

if __name__ == "__main__":
    asyncio.run(test_fixes())
