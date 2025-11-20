# -*- coding: utf-8 -*-
"""Debug Donchian values"""
import asyncio
from datetime import datetime, timedelta
from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators

async def debug_donchian():
    dm = DataManager()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    df = await dm.fetch_historical("BTC/USDT", "1h", start_date, end_date, "binance")
    await dm.close()
    
    df = calculate_all_indicators(df, ["donchian"])
    
    print(f"Total candles: {len(df)}")
    print(f"\nLast 10 rows:")
    print(df[['timestamp', 'high', 'low', 'close', 'donchian_upper', 'donchian_lower']].tail(10))
    
    # Check if high ever exceeds donchian_upper
    breakouts = (df['high'] > df['donchian_upper']).sum()
    print(f"\nHigh > Donchian Upper: {breakouts} times ({breakouts/len(df)*100:.1f}%)")
    
    # Check if close exceeds don_upper
    close_breakouts = (df['close'] > df['donchian_upper']).sum()
    print(f"Close > Donchian Upper: {close_breakouts} times ({close_breakouts/len(df)*100:.1f}%)")
    
    # Show where high == donchian_upper (touches)
    touches = (df['high'] >= df['donchian_upper'] * 0.9999).sum()
    print(f"High touches Donchian Upper (99.99%): {touches} times")

if __name__ == "__main__":
    asyncio.run(debug_donchian())
