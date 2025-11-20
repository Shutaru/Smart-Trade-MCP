# -*- coding: utf-8 -*-
"""
BACKTEST COMPARATIVO - 10 Estrategias com Exit Logic Corrigida

Compara resultados das estrategias que tinham 1 trade ANTES vs DEPOIS da correcao.
"""

import asyncio
from datetime import datetime, timedelta
import json
import pandas as pd
from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators
from src.core.backtest_engine import BacktestEngine
from src.strategies import registry

# Estrategias corrigidas (tinham 1 trade antes)
FIXED_STRATEGIES = [
    "multi_oscillator_confluence",
    "triple_momentum_confluence",
    "donchian_volatility_breakout",
    "atr_expansion_breakout",
    "channel_squeeze_plus",
    "volatility_weighted_breakout",
]

# Resultados ANTES (1 trade cada)
BEFORE_RESULTS = {
    "multi_oscillator_confluence": {"return": 0.21, "trades": 1, "win_rate": 100.0},
    "triple_momentum_confluence": {"return": -0.03, "trades": 1, "win_rate": 0.0},
    "donchian_volatility_breakout": {"return": -0.19, "trades": 1, "win_rate": 0.0},
    "atr_expansion_breakout": {"return": -0.24, "trades": 1, "win_rate": 0.0},
    "channel_squeeze_plus": {"return": -0.12, "trades": 1, "win_rate": 0.0},
    "volatility_weighted_breakout": {"return": -0.18, "trades": 1, "win_rate": 0.0},
}

async def run_comparative_backtest():
    print("=" * 100)
    print("BACKTEST COMPARATIVO - ANTES vs DEPOIS EXIT LOGIC")
    print("=" * 100)
    print()
    
    # Fetch data
    print("Carregando dados de 1 ano...")
    dm = DataManager()
    end = datetime.now()
    start = end - timedelta(days=365)
    df = await dm.fetch_historical('BTC/USDT', '1h', start, end, 'binance')
    await dm.close()
    
    print(f"OK! {len(df)} candles")
    print()
    
    # Calculate all indicators
    print("Calculando indicadores...")
    all_indicators = ['rsi', 'cci', 'stochastic', 'macd', 'ema', 'atr', 'mfi', 'adx',
                     'bollinger', 'keltner', 'donchian', 'supertrend', 'vwap', 'obv']
    df = calculate_all_indicators(df, all_indicators)
    print(f"OK! Indicadores calculados")
    print()
    
    # Run backtest for each strategy
    results = []
    
    print("=" * 100)
    print(f"{'#':<3} {'Estrategia':<40} {'ANTES':>20} {'DEPOIS':>20} {'Melhoria':>15}")
    print("=" * 100)
    
    for i, strategy_name in enumerate(FIXED_STRATEGIES, 1):
        try:
            strategy = registry.get(strategy_name)
            engine = BacktestEngine(initial_capital=10000)
            result = engine.run(strategy, df)
            
            before = BEFORE_RESULTS[strategy_name]
            after = {
                "return": result["total_return"],
                "trades": result["metrics"]["total_trades"],
                "win_rate": result["metrics"]["win_rate"]
            }
            
            # Calculate improvement
            trades_change = after["trades"] - before["trades"]
            trades_pct = ((after["trades"] - before["trades"]) / before["trades"] * 100) if before["trades"] > 0 else 0
            return_change = after["return"] - before["return"]
            wr_change = after["win_rate"] - before["win_rate"]
            
            # Format output
            before_str = f"{before['trades']}t, {before['return']:+.2f}%"
            after_str = f"{after['trades']}t, {after['return']:+.2f}%"
            
            if trades_change > 100:
                improvement = f"?? +{trades_change}t!"
            elif trades_change > 10:
                improvement = f"? +{trades_change}t"
            elif trades_change > 0:
                improvement = f"?? +{trades_change}t"
            else:
                improvement = f"??  {trades_change}t"
            
            print(f"{i:<3} {strategy_name:<40} {before_str:>20} {after_str:>20} {improvement:>15}")
            
            results.append({
                "strategy": strategy_name,
                "before": before,
                "after": after,
                "improvement": {
                    "trades": trades_change,
                    "trades_pct": trades_pct,
                    "return": return_change,
                    "win_rate": wr_change
                }
            })
            
        except Exception as e:
            print(f"{i:<3} {strategy_name:<40} ERROR: {str(e)[:30]}")
    
    print("=" * 100)
    print()
    
    # Summary statistics
    total_before_trades = sum(r["before"]["trades"] for r in results)
    total_after_trades = sum(r["after"]["trades"] for r in results)
    avg_before_return = sum(r["before"]["return"] for r in results) / len(results)
    avg_after_return = sum(r["after"]["return"] for r in results) / len(results)
    
    print("RESUMO GERAL:")
    print("=" * 100)
    print(f"  Total de estrategias testadas: {len(results)}")
    print()
    print(f"  TRADES:")
    print(f"    ANTES:  {total_before_trades} trades (todas com 1 trade cada)")
    print(f"    DEPOIS: {total_after_trades} trades")
    print(f"    AUMENTO: +{total_after_trades - total_before_trades} trades ({((total_after_trades/total_before_trades - 1)*100):.0f}%)")
    print()
    print(f"  RETORNO MEDIO:")
    print(f"    ANTES:  {avg_before_return:+.2f}%")
    print(f"    DEPOIS: {avg_after_return:+.2f}%")
    print(f"    MUDANCA: {avg_after_return - avg_before_return:+.2f}%")
    print()
    
    # Show best improvements
    sorted_by_trades = sorted(results, key=lambda x: x["improvement"]["trades"], reverse=True)
    
    print("TOP 3 MAIORES MELHORIAS (por numero de trades):")
    for i, r in enumerate(sorted_by_trades[:3], 1):
        print(f"  {i}. {r['strategy']}")
        print(f"     {r['before']['trades']} ? {r['after']['trades']} trades (+{r['improvement']['trades']})")
        print(f"     Return: {r['before']['return']:+.2f}% ? {r['after']['return']:+.2f}% ({r['improvement']['return']:+.2f}%)")
        print(f"     Win Rate: {r['before']['win_rate']:.1f}% ? {r['after']['win_rate']:.1f}% ({r['improvement']['win_rate']:+.1f}%)")
        print()
    
    # Save results
    output = {
        "date": datetime.now().isoformat(),
        "strategies_tested": len(results),
        "total_before_trades": total_before_trades,
        "total_after_trades": total_after_trades,
        "avg_before_return": avg_before_return,
        "avg_after_return": avg_after_return,
        "results": results
    }
    
    with open("backtest_exit_logic_comparison.json", "w") as f:
        json.dump(output, f, indent=2, default=str)
    
    print("=" * 100)
    print("Resultados salvos em: backtest_exit_logic_comparison.json")
    print("=" * 100)

if __name__ == "__main__":
    asyncio.run(run_comparative_backtest())
