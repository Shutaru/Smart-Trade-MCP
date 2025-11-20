# -*- coding: utf-8 -*-
"""Test if SuperTrend is calculated in backtest data"""
import asyncio
from datetime import datetime, timedelta
import pandas as pd
from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators

async def test_supertrend():
    dm = DataManager()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    df = await dm.fetch_historical("BTC/USDT", "1h", start_date, end_date, "binance")
    await dm.close()
    
    print(f"Fetched {len(df)} candles")
    print(f"Columns before indicators: {df.columns.tolist()}")
    
    df = calculate_all_indicators(df, ["supertrend", "donchian", "ema", "adx"])
    
    print(f"\nColumns after indicators: {df.columns.tolist()}")
    print(f"\nSuperTrend columns: {[c for c in df.columns if 'supertrend' in c.lower()]}")
    print(f"Donchian columns: {[c for c in df.columns if 'donchian' in c.lower()]}")
    
    if 'supertrend_trend' in df.columns:
        print(f"\nSuperTrend trend values (last 10):")
        print(df['supertrend_trend'].tail(10).values)
        print(f"Unique values: {df['supertrend_trend'].unique()}")
    else:
        print("\nERROR: supertrend_trend NOT CALCULATED!")
    
    # Test DonchianContinuation conditions
    if 'supertrend_trend' in df.columns and 'donchian_upper' in df.columns:
        test_row = df.iloc[-1]
        close = test_row['close']
        ema_200 = test_row.get('ema_200', close)
        st_trend = test_row.get('supertrend_trend', 0)
        adx = test_row.get('adx', 0)
        don_upper = test_row.get('donchian_upper', close)
        
        print(f"\nTest conditions (last candle):")
        print(f"  close > ema_200: {close} > {ema_200} = {close > ema_200}")
        print(f"  supertrend_trend > 0: {st_trend} > 0 = {st_trend > 0}")
        print(f"  adx >= 18: {adx} >= 18 = {adx >= 18}")
        print(f"  close > donchian_upper: {close} > {don_upper} = {close > don_upper}")

if __name__ == "__main__":
    asyncio.run(test_supertrend())
