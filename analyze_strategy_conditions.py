# -*- coding: utf-8 -*-
"""
ANALISE DETALHADA - Por que estrategias tem poucos/zero trades?

Verifica cada condicao de cada estrategia para encontrar gargalos.
"""

import asyncio
from datetime import datetime, timedelta
import json
import pandas as pd
from collections import defaultdict

from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators
from src.strategies import registry


# Estrategias com 0 ou 1 trade para investigar
STRATEGIES_TO_ANALYZE = [
    # 0 trades
    "donchian_continuation",
    "donchian_volatility_breakout",
    "pure_price_action_donchian",
    "vwap_mean_reversion",
    # 1 trade (sample)
    "atr_expansion_breakout",
    "channel_squeeze_plus",
    "volatility_weighted_breakout",
    "london_breakout_atr",
    "mfi_impulse_momentum",
    "triple_momentum_confluence",
    "rsi_supertrend_flip",
    "multi_oscillator_confluence",
]


async def analyze_strategy_conditions():
    """Analyze why strategies have few/no trades."""
    
    print("=" * 100)
    print("ANALISE DETALHADA - ESTRATEGIAS COM POUCOS TRADES")
    print("=" * 100)
    print()
    
    # Fetch 1 year of data
    print("Buscando dados de 1 ano...")
    dm = DataManager()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    df = await dm.fetch_historical("BTC/USDT", "1h", start_date, end_date, "binance")
    await dm.close()
    
    print(f"OK! {len(df)} candles de {df['timestamp'].iloc[0]} ate {df['timestamp'].iloc[-1]}")
    print()
    
    # Calculate all indicators
    print("Calculando indicadores...")
    all_indicators = set()
    for strategy_name in STRATEGIES_TO_ANALYZE:
        try:
            strategy = registry.get(strategy_name)
            all_indicators.update(strategy.get_required_indicators())
        except:
            pass
    
    df = calculate_all_indicators(df, list(all_indicators))
    print(f"OK! {len(all_indicators)} indicadores calculados")
    print()
    
    # Analyze each strategy
    results = {}
    
    for strategy_name in STRATEGIES_TO_ANALYZE:
        print("=" * 100)
        print(f"ANALISANDO: {strategy_name}")
        print("=" * 100)
        
        try:
            strategy = registry.get(strategy_name)
            
            # Get strategy code to understand conditions
            analysis = analyze_strategy_logic(strategy_name, df)
            
            results[strategy_name] = analysis
            
            # Display results
            print(f"\nTotal de candles analisados: {len(df)}")
            print(f"\nCondicoes satisfeitas:")
            for condition, count in analysis.items():
                pct = (count / len(df)) * 100
                print(f"  {condition:50s}: {count:6d} candles ({pct:5.1f}%)")
            
            print()
            
        except Exception as e:
            print(f"ERRO ao analisar {strategy_name}: {e}")
            print()
    
    # Save results
    output_file = "strategy_condition_analysis.json"
    with open(output_file, "w") as f:
        json.dump({
            "analysis_date": datetime.now().isoformat(),
            "total_candles": len(df),
            "results": results
        }, f, indent=2)
    
    print("=" * 100)
    print(f"Analise salva em: {output_file}")
    print("=" * 100)


def analyze_strategy_logic(strategy_name, df):
    """Analyze specific strategy conditions."""
    
    analysis = {}
    
    # donchian_continuation
    if strategy_name == "donchian_continuation":
        analysis["close > ema_200"] = (df['close'] > df.get('ema_200', df['close'])).sum()
        analysis["supertrend_trend > 0"] = (df.get('supertrend_trend', 0) > 0).sum()
        analysis["adx >= 18"] = (df.get('adx', 0) >= 18).sum()
        
        # Combined
        cond1 = df['close'] > df.get('ema_200', df['close'])
        cond2 = df.get('supertrend_trend', 0) > 0
        cond3 = df.get('adx', 0) >= 18
        analysis["ALL 3 conditions above"] = (cond1 & cond2 & cond3).sum()
        
        # Breakout
        analysis["close > donchian_upper"] = (df['close'] > df.get('donchian_upper', df['close'])).sum()
        
        # Full LONG signal (without ADX rising check)
        full_cond = cond1 & cond2 & cond3 & (df['close'] > df.get('donchian_upper', df['close']))
        analysis["FULL LONG condition (no ADX rising)"] = full_cond.sum()
    
    # donchian_volatility_breakout
    elif strategy_name == "donchian_volatility_breakout":
        analysis["close > donchian_upper"] = (df['close'] > df.get('donchian_upper', df['close'])).sum()
        analysis["adx > 0"] = (df.get('adx', 0) > 0).sum()
        analysis["adx >= 20"] = (df.get('adx', 0) >= 20).sum()
        
        # Combined
        cond1 = df['close'] > df.get('donchian_upper', df['close'])
        cond2 = df.get('adx', 0) >= 20
        analysis["BOTH conditions"] = (cond1 & cond2).sum()
    
    # pure_price_action_donchian
    elif strategy_name == "pure_price_action_donchian":
        analysis["close > donchian_upper"] = (df['close'] > df.get('donchian_upper', df['close'])).sum()
        # This strategy might have no other conditions!
    
    # vwap_mean_reversion
    elif strategy_name == "vwap_mean_reversion":
        if 'vwap' in df.columns:
            dist = abs(df['close'] - df['vwap']) / df['vwap']
            analysis["vwap exists"] = len(df)
            analysis["dist > 0.015 (1.5%)"] = (dist > 0.015).sum()
            analysis["close < vwap"] = (df['close'] < df['vwap']).sum()
            analysis["close > vwap"] = (df['close'] > df['vwap']).sum()
            analysis["rsi < 40"] = (df.get('rsi', 50) < 40).sum()
            analysis["rsi > 60"] = (df.get('rsi', 50) > 60).sum()
            
            # LONG condition
            cond_long = (dist > 0.015) & (df['close'] < df['vwap']) & (df.get('rsi', 50) < 40)
            analysis["FULL LONG condition"] = cond_long.sum()
            
            # SHORT condition
            cond_short = (dist > 0.015) & (df['close'] > df['vwap']) & (df.get('rsi', 50) > 60)
            analysis["FULL SHORT condition"] = cond_short.sum()
        else:
            analysis["ERROR"] = "VWAP not calculated!"
    
    # Generic analysis for 1-trade strategies
    elif strategy_name in ["atr_expansion_breakout", "channel_squeeze_plus", "volatility_weighted_breakout"]:
        # Check ADX if needed
        if 'adx' in df.columns:
            analysis["adx >= 20"] = (df.get('adx', 0) >= 20).sum()
            analysis["adx >= 25"] = (df.get('adx', 0) >= 25).sum()
        
        # Check bollinger bands
        if 'bb_upper' in df.columns:
            analysis["close > bb_upper"] = (df['close'] > df.get('bb_upper', df['close'])).sum()
            analysis["close < bb_lower"] = (df['close'] < df.get('bb_lower', df['close'])).sum()
        
        # EMA trends
        if 'ema_200' in df.columns:
            analysis["close > ema_200 (uptrend)"] = (df['close'] > df['ema_200']).sum()
            analysis["close < ema_200 (downtrend)"] = (df['close'] < df['ema_200']).sum()
    
    # RSI/momentum strategies
    elif strategy_name in ["rsi_supertrend_flip", "multi_oscillator_confluence"]:
        if 'rsi' in df.columns:
            analysis["rsi < 30"] = (df['rsi'] < 30).sum()
            analysis["rsi > 70"] = (df['rsi'] > 70).sum()
            analysis["40 < rsi < 60"] = ((df['rsi'] > 40) & (df['rsi'] < 60)).sum()
        
        if 'supertrend_trend' in df.columns:
            # SuperTrend flips
            st_changes = (df['supertrend_trend'].diff() != 0).sum()
            analysis["supertrend_trend changes"] = st_changes
            analysis["supertrend bullish"] = (df['supertrend_trend'] > 0).sum()
            analysis["supertrend bearish"] = (df['supertrend_trend'] < 0).sum()
    
    else:
        # Generic analysis
        analysis["total_candles"] = len(df)
        if 'ema_200' in df.columns:
            analysis["close > ema_200"] = (df['close'] > df['ema_200']).sum()
        if 'rsi' in df.columns:
            analysis["30 < rsi < 70"] = ((df['rsi'] > 30) & (df['rsi'] < 70)).sum()
    
    return analysis


if __name__ == "__main__":
    asyncio.run(analyze_strategy_conditions())
