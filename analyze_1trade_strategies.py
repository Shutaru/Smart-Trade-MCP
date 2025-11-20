# -*- coding: utf-8 -*-
"""
Analisar estrategias com 1 trade para identificar gargalos
"""

import asyncio
from datetime import datetime, timedelta
import pandas as pd
from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators
from src.strategies import registry

# 22 estrategias com 1 trade
STRATEGIES_1_TRADE = [
    "donchian_volatility_breakout", "atr_expansion_breakout", "channel_squeeze_plus",
    "volatility_weighted_breakout", "london_breakout_atr", "mfi_impulse_momentum",
    "triple_momentum_confluence", "rsi_supertrend_flip", "multi_oscillator_confluence",
    "obv_trend_confirmation", "trend_volume_combo", "ema_stack_regime_flip",
    "vwap_institutional_trend", "order_flow_momentum_vwap", "keltner_pullback_continuation",
    "ema200_tap_reversion", "double_donchian_pullback", "pure_price_action_donchian",
    "obv_confirmation_breakout_plus", "ny_session_fade", "regime_adaptive_core",
    "complete_system_5x"
]

async def analyze_1trade_strategies():
    print("=" * 100)
    print("ANALISE DE ESTRATEGIAS COM 1 TRADE - IDENTIFICAR GARGALOS")
    print("=" * 100)
    print()
    
    # Fetch data
    print("Buscando dados...")
    dm = DataManager()
    end = datetime.now()
    start = end - timedelta(days=365)
    df = await dm.fetch_historical('BTC/USDT', '1h', start, end, 'binance')
    await dm.close()
    
    print(f"OK! {len(df)} candles")
    print()
    
    # Calculate all possible indicators
    all_indicators = ['rsi', 'macd', 'ema', 'sma', 'bollinger', 'atr', 'adx', 'cci', 
                     'donchian', 'keltner', 'mfi', 'obv', 'stochastic', 'supertrend', 'vwap']
    df = calculate_all_indicators(df, all_indicators)
    
    print("Analisando cada estrategia...")
    print()
    
    for i, strat_name in enumerate(STRATEGIES_1_TRADE, 1):
        print(f"[{i:2d}/22] {strat_name:40s} ", end="", flush=True)
        
        try:
            strategy = registry.get(strat_name)
            
            # Get required indicators
            req_indicators = strategy.get_required_indicators()
            
            # Generate signals
            signals = strategy.generate_signals(df)
            
            # Check if indicators exist
            missing_indicators = []
            for ind in req_indicators:
                # Map indicator names to columns
                ind_map = {
                    'bollinger': ['bb_upper', 'bb_middle', 'bb_lower'],
                    'donchian': ['donchian_upper', 'donchian_middle', 'donchian_lower'],
                    'keltner': ['keltner_upper', 'keltner_middle', 'keltner_lower'],
                    'ema': ['ema_12', 'ema_26', 'ema_50', 'ema_200'],
                    'sma': ['sma_20', 'sma_50', 'sma_200'],
                    'macd': ['macd', 'macd_signal', 'macd_hist'],
                    'stochastic': ['stoch_k', 'stoch_d'],
                    'supertrend': ['supertrend', 'supertrend_trend']
                }
                
                if ind.lower() in ind_map:
                    cols = ind_map[ind.lower()]
                    if not any(c in df.columns for c in cols):
                        missing_indicators.append(ind)
                elif ind not in df.columns:
                    missing_indicators.append(ind)
            
            # Analyze
            num_signals = len(signals)
            
            if missing_indicators:
                print(f"MISSING INDICATORS: {', '.join(missing_indicators)}")
            elif num_signals == 1:
                print(f"OK - Condicoes muito restritivas (gerar apenas 1 sinal em 1 ano)")
            else:
                print(f"BUG? Gerou {num_signals} signals mas backtest reportou 1 trade")
                
        except Exception as e:
            print(f"ERROR: {str(e)[:50]}")
    
    print()
    print("=" * 100)
    print("CONCLUSAO:")
    print("  - Estrategias com indicadores em falta: precisam dos indicadores adicionados")
    print("  - Estrategias com condicoes restritivas: precisam relaxar filtros")
    print("=" * 100)

if __name__ == "__main__":
    asyncio.run(analyze_1trade_strategies())
