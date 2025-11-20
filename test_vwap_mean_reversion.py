# -*- coding: utf-8 -*-
"""Test VWAP Mean Reversion strategy with real data"""
import asyncio
from datetime import datetime, timedelta
import pandas as pd
from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators
from src.strategies import registry

async def test_vwap_mean_reversion():
    # Fetch data
    dm = DataManager()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    df = await dm.fetch_historical("BTC/USDT", "1h", start_date, end_date, "binance")
    await dm.close()
    
    print(f"Fetched {len(df)} candles")
    
    # Calculate indicators
    df = calculate_all_indicators(df, ["vwap", "rsi", "atr"])
    
    print(f"\nVWAP calculated: {'vwap' in df.columns}")
    print(f"VWAP sample (last 5): {df['vwap'].tail(5).values}")
    
    # Test conditions
    close = df['close']
    vwap = df['vwap']
    rsi = df['rsi']
    
    dist = abs(close - vwap) / vwap
    
    print(f"\nCondition analysis:")
    print(f"  dist > 0.015: {(dist > 0.015).sum()} / {len(df)} ({(dist > 0.015).sum()/len(df)*100:.1f}%)")
    print(f"  close < vwap: {(close < vwap).sum()} / {len(df)} ({(close < vwap).sum()/len(df)*100:.1f}%)")
    print(f"  rsi < 40: {(rsi < 40).sum()} / {len(df)} ({(rsi < 40).sum()/len(df)*100:.1f}%)")
    
    # LONG conditions
    long_cond = (dist > 0.015) & (close < vwap) & (rsi < 40)
    print(f"\n  FULL LONG condition: {long_cond.sum()} / {len(df)} ({long_cond.sum()/len(df)*100:.1f}%)")
    
    # Get strategy and generate signals
    print(f"\nTesting VwapMeanReversion strategy...")
    strategy = registry.get("vwap_mean_reversion")
    signals = strategy.generate_signals(df)
    
    print(f"Signals generated: {len(signals)}")
    if signals:
        for i, sig in enumerate(signals[:5], 1):
            print(f"  Signal {i}: {sig.type} at {sig.timestamp} price {sig.price}")
    else:
        print("  NO SIGNALS GENERATED!")
        
        # Debug: Check if VWAP exists at each iteration
        print("\nDEBUG: Checking VWAP availability...")
        vwap_exists = df['vwap'].notna().sum()
        print(f"  VWAP non-null values: {vwap_exists} / {len(df)}")
        
        # Check first few rows where conditions are met
        matching_rows = df[long_cond].head(10)
        if len(matching_rows) > 0:
            print(f"\n  First 5 rows where LONG condition is TRUE:")
            print(matching_rows[['timestamp', 'close', 'vwap', 'rsi']].head(5))

if __name__ == "__main__":
    asyncio.run(test_vwap_mean_reversion())
