# -*- coding: utf-8 -*-
"""Test 3 critical fixes"""
import asyncio
from datetime import datetime, timedelta
from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators
from src.core.backtest_engine import BacktestEngine
from src.strategies import registry

async def test_critical_fixes():
    print("Testing 3 CRITICAL FIXES...")
    print()
    
    dm = DataManager()
    end = datetime.now()
    start = end - timedelta(days=365)
    df = await dm.fetch_historical('BTC/USDT', '1h', start, end, 'binance')
    await dm.close()
    
    df = calculate_all_indicators(df, ['bollinger', 'rsi', 'atr', 'stochastic', 'ema'])
    
    print(f"{'Strategy':<40} {'Return':>10} {'Trades':>8} {'Win Rate':>10}")
    print("-" * 70)
    
    for name in ['bollinger_mean_reversion', 'bollinger_squeeze_breakout', 'stoch_signal_reversal']:
        s = registry.get(name)
        e = BacktestEngine(10000)
        r = e.run(s, df)
        m = r['metrics']
        
        # Compare with original
        original_trades = {
            'bollinger_mean_reversion': 3861,
            'bollinger_squeeze_breakout': 160,
            'stoch_signal_reversal': 160
        }
        
        improvement = ""
        if m['total_trades'] < original_trades[name]:
            reduction = ((original_trades[name] - m['total_trades']) / original_trades[name]) * 100
            improvement = f" (reduced {reduction:.0f}% from {original_trades[name]})"
        
        print(f"{name:40s} {r['total_return']:+9.2f}% {m['total_trades']:>7.0f} {m['win_rate']:>9.1f}%{improvement}")
    
    print()

if __name__ == "__main__":
    asyncio.run(test_critical_fixes())
