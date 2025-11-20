# -*- coding: utf-8 -*-
"""
INVESTIGACAO PROFUNDA - Por que 22 estrategias tem apenas 1 trade?

Vamos testar uma estrategia especifica linha por linha para encontrar o problema.
"""

import asyncio
from datetime import datetime, timedelta
import pandas as pd
from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators
from src.strategies import registry

# Estrategia para debug profundo
STRATEGY_TO_DEBUG = "multi_oscillator_confluence"

async def deep_debug():
    print("=" * 100)
    print(f"INVESTIGACAO PROFUNDA: {STRATEGY_TO_DEBUG}")
    print("=" * 100)
    print()
    
    # Fetch data
    dm = DataManager()
    end = datetime.now()
    start = end - timedelta(days=365)
    df = await dm.fetch_historical('BTC/USDT', '1h', start, end, 'binance')
    await dm.close()
    
    print(f"Dados: {len(df)} candles")
    print()
    
    # Calculate indicators
    all_indicators = ['rsi', 'cci', 'stochastic', 'macd', 'ema', 'atr', 'mfi']
    df = calculate_all_indicators(df, all_indicators)
    
    # Get strategy
    strategy = registry.get(STRATEGY_TO_DEBUG)
    
    print(f"Estrategia: {strategy.__class__.__name__}")
    print(f"Indicadores requeridos: {strategy.get_required_indicators()}")
    print()
    
    # Check if all required indicators exist
    print("Verificando indicadores...")
    for ind in strategy.get_required_indicators():
        ind_map = {
            'rsi': ['rsi'],
            'cci': ['cci'],
            'stochastic': ['stoch_k', 'stoch_d'],
            'mfi': ['mfi'],
            'macd': ['macd', 'macd_signal', 'macd_hist']
        }
        cols = ind_map.get(ind.lower(), [ind])
        exists = any(c in df.columns for c in cols)
        print(f"  {ind}: {'OK' if exists else 'MISSING'}")
    print()
    
    # Manually simulate the strategy logic
    print("Simulando logica da estrategia manualmente...")
    print()
    
    signals_count = 0
    condition_met_count = 0
    
    for i in range(1, len(df)):
        r = df.iloc[i]
        rsi = r.get("rsi", 50)
        cci = r.get("cci", 0)
        stoch_k = r.get("stoch_k", 50)
        
        # Check conditions from the strategy
        # LONG: At least 2 of 3 oversold
        oversold_count = sum([rsi < 35, cci < -80, stoch_k < 25])
        
        # LONG: At least 2 of 3 overbought
        overbought_count = sum([rsi > 65, cci > 80, stoch_k > 75])
        
        if oversold_count >= 2:
            condition_met_count += 1
            if condition_met_count <= 10:  # Show first 10
                print(f"  Candle {i:5d} @ {r['timestamp']}: LONG condition met!")
                print(f"    RSI: {rsi:.1f}, CCI: {cci:.1f}, Stoch K: {stoch_k:.1f}")
                print(f"    Oversold count: {oversold_count}/3")
        
        if overbought_count >= 2:
            condition_met_count += 1
            if condition_met_count <= 10:
                print(f"  Candle {i:5d} @ {r['timestamp']}: SHORT condition met!")
                print(f"    RSI: {rsi:.1f}, CCI: {cci:.1f}, Stoch K: {stoch_k:.1f}")
                print(f"    Overbought count: {overbought_count}/3")
    
    print()
    print(f"Total de vezes que condicoes foram satisfeitas: {condition_met_count}")
    print()
    
    # Now run the actual strategy
    print("Rodando estrategia real...")
    signals = strategy.generate_signals(df)
    print(f"Sinais gerados: {len(signals)}")
    print()
    
    # Show all signals
    if len(signals) > 0:
        print("Sinais gerados pela estrategia:")
        for i, sig in enumerate(signals, 1):
            print(f"  Signal {i}: {sig.type} @ {sig.timestamp} price {sig.price}")
    else:
        print("NENHUM SINAL GERADO!")
    print()
    
    # DIAGNOSTIC: Check position tracking bug
    print("=" * 100)
    print("DIAGNOSTICO: Possivel bug de position tracking?")
    print("=" * 100)
    
    # Simulate with position tracking
    pos = None
    entries = 0
    
    for i in range(1, len(df)):
        r = df.iloc[i]
        rsi = r.get("rsi", 50)
        cci = r.get("cci", 0)
        stoch_k = r.get("stoch_k", 50)
        
        oversold_count = sum([rsi < 35, cci < -80, stoch_k < 25])
        overbought_count = sum([rsi > 65, cci > 80, stoch_k > 75])
        
        if pos is None:
            if oversold_count >= 2:
                pos = "LONG"
                entries += 1
                if entries <= 5:
                    print(f"Entry {entries}: LONG @ candle {i}, timestamp {r['timestamp']}")
            elif overbought_count >= 2:
                pos = "SHORT"
                entries += 1
                if entries <= 5:
                    print(f"Entry {entries}: SHORT @ candle {i}, timestamp {r['timestamp']}")
        # else:
        #     # Position is open, strategy doesn't have exit logic?
        #     pass
    
    print()
    print(f"Total de entradas (sem exit): {entries}")
    print()
    
    # CONCLUSION
    print("=" * 100)
    print("CONCLUSAO:")
    print("=" * 100)
    
    if condition_met_count > 100 and len(signals) <= 1:
        print("BUG ENCONTRADO: Condicoes satisfeitas >100 vezes mas apenas 1 sinal gerado!")
        print("Possiveis causas:")
        print("  1. Position tracking nao esta sendo resetado (pos fica travado)")
        print("  2. Falta logica de exit (pos nunca volta a None)")
        print("  3. Backtest engine nao esta processando os sinais corretamente")
    elif condition_met_count < 10:
        print("Condicoes muito restritivas - estrategia OK, apenas conservadora")
    else:
        print("Necessario investigacao mais profunda")

if __name__ == "__main__":
    asyncio.run(deep_debug())
