# -*- coding: utf-8 -*-
"""
BACKTEST COMPARATIVO - AS 38 ESTRATEGIAS - 1 ANO
BTC/USDT, 1h, 365 dias com batching automatico
"""

import asyncio
from datetime import datetime, timedelta
import json
import pandas as pd

from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators
from src.core.backtest_engine import BacktestEngine
from src.strategies import registry
from src.core.logger import logger


ALL_STRATEGIES = [
    "bollinger_mean_reversion", "rsi_band_reversion", "cci_extreme_snapback",
    "mfi_divergence_reversion", "stoch_signal_reversal",
    "ema_cloud_trend", "donchian_continuation", "macd_zero_trend",
    "adx_trend_filter_plus", "trendflow_supertrend",
    "bollinger_squeeze_breakout", "keltner_expansion", "donchian_volatility_breakout",
    "atr_expansion_breakout", "channel_squeeze_plus", "volatility_weighted_breakout",
    "london_breakout_atr", "vwap_breakout",
    "ema_stack_momentum", "mfi_impulse_momentum", "triple_momentum_confluence",
    "rsi_supertrend_flip", "multi_oscillator_confluence", "obv_trend_confirmation",
    "trend_volume_combo", "ema_stack_regime_flip",
    "vwap_institutional_trend", "vwap_mean_reversion", "vwap_band_fade_pro",
    "order_flow_momentum_vwap", "keltner_pullback_continuation", "ema200_tap_reversion",
    "double_donchian_pullback", "pure_price_action_donchian", "obv_confirmation_breakout_plus",
    "ny_session_fade", "regime_adaptive_core", "complete_system_5x",
]


async def main():
    print("=" * 100)
    print("BACKTEST 1 ANO - 38 ESTRATEGIAS")
    print("=" * 100)
    print()
    
    symbol, timeframe, capital, days = "BTC/USDT", "1h", 10000, 365
    
    print(f"Config: {symbol} {timeframe}, {days} dias, ${capital:,}")
    print()
    print("PASSO 1: Fetching data (batching automatico)...")
    
    dm = DataManager()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    df = await dm.fetch_historical(symbol, timeframe, start_date, end_date, "binance")
    await dm.close()
    
    print(f"OK! {len(df):,} candles ({(df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).days} dias)")
    print()
    print("PASSO 2: Calculating indicators...")
    
    all_ind = set()
    for s in ALL_STRATEGIES:
        try:
            all_ind.update(registry.get(s).get_required_indicators())
        except:
            pass
    
    df = calculate_all_indicators(df, list(all_ind))
    print(f"OK! {len(all_ind)} indicators")
    print()
    print("PASSO 3: Running backtests...")
    print()
    
    results = []
    for i, sname in enumerate(ALL_STRATEGIES, 1):
        print(f"[{i:2d}/38] {sname:40s} ", end="", flush=True)
        try:
            s = registry.get(sname)
            e = BacktestEngine(capital)
            r = e.run(s, df)
            m = r['metrics']
            results.append({"strategy": sname, "return": r['total_return'], "trades": m['total_trades'], "win_rate": m['win_rate'], "sharpe": m['sharpe_ratio']})
            print(f"OK {r['total_return']:+7.2f}% | {m['total_trades']:3d} trades | WR {m['win_rate']:5.1f}%")
        except Exception as ex:
            print(f"ERROR: {str(ex)[:40]}")
            results.append({"strategy": sname, "return": 0, "trades": 0, "win_rate": 0, "sharpe": 0})
    
    print()
    print("=" * 100)
    print("TOP 10:")
    rs = sorted(results, key=lambda x: x["return"], reverse=True)
    for i, r in enumerate(rs[:10], 1):
        print(f"#{i:2d} {r['strategy']:40s} {r['return']:+8.2f}% | {r['trades']:3d} trades | WR {r['win_rate']:5.1f}%")
    
    print()
    print("STATS:")
    pos = [r for r in results if r["return"] > 0]
    print(f"Lucrativas: {len(pos)}/38 ({len(pos)/38*100:.0f}%)")
    print(f"Melhor: {rs[0]['strategy']} ({rs[0]['return']:+.2f}%)")
    
    with open("backtest_1year_results.json", "w") as f:
        json.dump({"results": rs, "stats": {"profitable": len(pos)}}, f, indent=2)
    
    print()
    print("DONE! Results saved to: backtest_1year_results.json")

if __name__ == "__main__":
    asyncio.run(main())
