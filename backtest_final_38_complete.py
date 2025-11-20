# -*- coding: utf-8 -*-
"""
BACKTEST COMPARATIVO FINAL - TODAS AS 38 ESTRATEGIAS

Testa todas as 38 estrategias com exit logic completo e gera relatorio detalhado.
Compara com resultados originais onde aplicavel.
"""

import asyncio
from datetime import datetime, timedelta
import json
import pandas as pd
from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators
from src.core.backtest_engine import BacktestEngine
from src.strategies import registry

# TODAS AS 38 ESTRATEGIAS
ALL_STRATEGIES = [
    "adx_trend_filter_plus",
    "atr_expansion_breakout",
    "bollinger_mean_reversion",
    "bollinger_squeeze_breakout",
    "cci_extreme_snapback",
    "channel_squeeze_plus",
    "complete_system_5x",
    "donchian_continuation",
    "donchian_volatility_breakout",
    "double_donchian_pullback",
    "ema200_tap_reversion",
    "ema_cloud_trend",
    "ema_stack_momentum",
    "ema_stack_regime_flip",
    "keltner_expansion",
    "keltner_pullback_continuation",
    "london_breakout_atr",
    "macd_zero_trend",
    "mfi_divergence_reversion",
    "mfi_impulse_momentum",
    "multi_oscillator_confluence",
    "ny_session_fade",
    "obv_confirmation_breakout_plus",
    "obv_trend_confirmation",
    "order_flow_momentum_vwap",
    "pure_price_action_donchian",
    "regime_adaptive_core",
    "rsi_band_reversion",
    "rsi_supertrend_flip",
    "stoch_signal_reversal",
    "trend_volume_combo",
    "trendflow_supertrend",
    "triple_momentum_confluence",
    "volatility_weighted_breakout",
    "vwap_band_fade_pro",
    "vwap_breakout",
    "vwap_institutional_trend",
    "vwap_mean_reversion",
]

async def run_complete_backtest():
    print("=" * 140)
    print("BACKTEST COMPARATIVO FINAL - TODAS AS 38 ESTRATEGIAS COM EXIT LOGIC COMPLETO")
    print("=" * 140)
    print()
    
    # Fetch data
    print("Carregando dados BTC/USDT 1h (365 dias)...")
    dm = DataManager()
    end = datetime.now()
    start = end - timedelta(days=365)
    df = await dm.fetch_historical('BTC/USDT', '1h', start, end, 'binance')
    await dm.close()
    
    print(f"OK! {len(df)} candles carregados ({start.date()} a {end.date()})")
    print()
    
    # Calculate all indicators
    print("Calculando todos os indicadores...")
    all_indicators = ['rsi', 'cci', 'stochastic', 'macd', 'ema', 'sma', 'atr', 'adx', 
                     'bollinger', 'keltner', 'donchian', 'mfi', 'obv', 'supertrend', 'vwap']
    df = calculate_all_indicators(df, all_indicators)
    print(f"OK! {len(all_indicators)} indicadores calculados")
    print()
    
    # Run backtest
    results = []
    profitable = []
    zero_wr = []
    high_wr = []
    
    print("=" * 140)
    print(f"{'#':<4} {'Estrategia':<50} {'Return':>10} {'Trades':>8} {'WR':>8} {'Sharpe':>8} {'Status':<20}")
    print("=" * 140)
    
    for i, strategy_name in enumerate(ALL_STRATEGIES, 1):
        try:
            strategy = registry.get(strategy_name)
            engine = BacktestEngine(initial_capital=10000)
            result = engine.run(strategy, df)
            
            ret = result["total_return"]
            trades = result["metrics"]["total_trades"]
            wr = result["metrics"]["win_rate"]
            sharpe = result["metrics"]["sharpe_ratio"]
            max_dd = result["metrics"]["max_drawdown"]
            
            # Determine status
            if trades == 0:
                status = "NO TRADES"
            elif wr == 0:
                status = "0% WR - PROBLEMA"
                zero_wr.append(strategy_name)
            elif ret > 5:
                status = "EXCELENTE"
                profitable.append(strategy_name)
                if wr >= 55:
                    high_wr.append(strategy_name)
            elif ret > 0:
                status = "LUCRATIVA"
                profitable.append(strategy_name)
                if wr >= 55:
                    high_wr.append(strategy_name)
            elif ret > -1:
                status = "NEUTRO"
            elif ret > -5:
                status = "PREJUIZO LEVE"
            elif ret > -20:
                status = "PREJUIZO MEDIO"
            else:
                status = "PREJUIZO SEVERO"
            
            # Add emoji for profitable ones
            if ret > 0:
                status_display = f"OK {status}"
            elif ret > -5:
                status_display = f"~  {status}"
            else:
                status_display = f"X  {status}"
            
            print(f"{i:<4} {strategy_name:<50} {ret:+9.2f}% {trades:>7} {wr:>7.1f}% {sharpe:>7.2f}  {status_display:<20}")
            
            results.append({
                "rank": i,
                "strategy": strategy_name,
                "return": ret,
                "trades": trades,
                "win_rate": wr,
                "sharpe": sharpe,
                "max_drawdown": max_dd,
                "avg_win": result["metrics"]["avg_win"],
                "avg_loss": result["metrics"]["avg_loss"],
                "status": status
            })
            
        except Exception as e:
            print(f"{i:<4} {strategy_name:<50} ERROR: {str(e)[:50]}")
            results.append({
                "rank": i,
                "strategy": strategy_name,
                "error": str(e)
            })
    
    print("=" * 140)
    print()
    
    # Calculate statistics
    valid_results = [r for r in results if "error" not in r]
    total_strategies = len(valid_results)
    
    if total_strategies > 0:
        avg_return = sum(r["return"] for r in valid_results) / total_strategies
        avg_trades = sum(r["trades"] for r in valid_results) / total_strategies
        avg_wr = sum(r["win_rate"] for r in valid_results) / total_strategies
        avg_sharpe = sum(r["sharpe"] for r in valid_results) / total_strategies
        
        # Summary stats
        print("=" * 140)
        print("RESUMO ESTATISTICO GERAL:")
        print("=" * 140)
        print(f"  Total de estrategias testadas:     {total_strategies}")
        print(f"  Estrategias lucrativas (>0%):      {len(profitable)} ({len(profitable)/total_strategies*100:.1f}%)")
        print(f"  Estrategias com WR >= 55%:         {len(high_wr)} ({len(high_wr)/total_strategies*100:.1f}%)")
        print(f"  Estrategias com 0% WR:             {len(zero_wr)} ({len(zero_wr)/total_strategies*100:.1f}%)")
        print()
        print(f"  Retorno medio:                     {avg_return:+.2f}%")
        print(f"  Trades medio:                      {avg_trades:.1f}")
        print(f"  Win Rate medio:                    {avg_wr:.1f}%")
        print(f"  Sharpe Ratio medio:                {avg_sharpe:.2f}")
        print()
        
        # TOP 10
        sorted_by_return = sorted(valid_results, key=lambda x: x["return"], reverse=True)
        
        print("=" * 140)
        print("TOP 10 MELHORES ESTRATEGIAS:")
        print("=" * 140)
        print(f"{'Rank':<6} {'Estrategia':<50} {'Return':>10} {'Trades':>8} {'WR':>8} {'Sharpe':>8}")
        print("-" * 140)
        for i, r in enumerate(sorted_by_return[:10], 1):
            emoji = "1." if i == 1 else "2." if i == 2 else "3." if i == 3 else f"{i}."
            print(f"{emoji:<6} {r['strategy']:<50} {r['return']:+9.2f}% {r['trades']:>7} {r['win_rate']:>7.1f}% {r['sharpe']:>7.2f}")
        print()
        
        # BOTTOM 10
        print("=" * 140)
        print("10 PIORES ESTRATEGIAS:")
        print("=" * 140)
        print(f"{'Rank':<6} {'Estrategia':<50} {'Return':>10} {'Trades':>8} {'WR':>8} {'Problema':<30}")
        print("-" * 140)
        for i, r in enumerate(sorted_by_return[-10:], 1):
            problema = "Overtrading" if r['trades'] > 500 else "WR baixo" if r['win_rate'] < 30 else "Prejuizo"
            print(f"{i}.<6 {r['strategy']:<50} {r['return']:+9.2f}% {r['trades']:>7} {r['win_rate']:>7.1f}% {problema:<30}")
        print()
        
        # Profitable strategies detail
        if profitable:
            print("=" * 140)
            print(f"ESTRATEGIAS LUCRATIVAS - DETALHES ({len(profitable)}):")
            print("=" * 140)
            print(f"{'#':<4} {'Estrategia':<50} {'Return':>10} {'Trades':>8} {'WR':>8} {'Sharpe':>8} {'Avg Win':>10} {'Avg Loss':>10}")
            print("-" * 140)
            profitable_sorted = sorted([r for r in valid_results if r["return"] > 0], key=lambda x: x["return"], reverse=True)
            for i, r in enumerate(profitable_sorted, 1):
                print(f"{i:<4} {r['strategy']:<50} {r['return']:+9.2f}% {r['trades']:>7} {r['win_rate']:>7.1f}% {r['sharpe']:>7.2f} {r['avg_win']:>9.2f}% {r['avg_loss']:>9.2f}%")
            print()
        
        # Trade frequency distribution
        print("=" * 140)
        print("DISTRIBUICAO POR FREQUENCIA DE TRADES:")
        print("=" * 140)
        freq_0 = len([r for r in valid_results if r["trades"] == 0])
        freq_1 = len([r for r in valid_results if r["trades"] == 1])
        freq_2_10 = len([r for r in valid_results if 2 <= r["trades"] <= 10])
        freq_11_50 = len([r for r in valid_results if 11 <= r["trades"] <= 50])
        freq_51_200 = len([r for r in valid_results if 51 <= r["trades"] <= 200])
        freq_201_500 = len([r for r in valid_results if 201 <= r["trades"] <= 500])
        freq_500plus = len([r for r in valid_results if r["trades"] > 500])
        
        print(f"  0 trades:       {freq_0} estrategias")
        print(f"  1 trade:        {freq_1} estrategias")
        print(f"  2-10 trades:    {freq_2_10} estrategias")
        print(f"  11-50 trades:   {freq_11_50} estrategias")
        print(f"  51-200 trades:  {freq_51_200} estrategias")
        print(f"  201-500 trades: {freq_201_500} estrategias")
        print(f"  >500 trades:    {freq_500plus} estrategias (OVERTRADING)")
        print()
        
        # Win Rate distribution
        print("=" * 140)
        print("DISTRIBUICAO POR WIN RATE:")
        print("=" * 140)
        wr_0 = len([r for r in valid_results if r["win_rate"] == 0 and r["trades"] > 0])
        wr_1_29 = len([r for r in valid_results if 0 < r["win_rate"] < 30])
        wr_30_49 = len([r for r in valid_results if 30 <= r["win_rate"] < 50])
        wr_50_69 = len([r for r in valid_results if 50 <= r["win_rate"] < 70])
        wr_70plus = len([r for r in valid_results if r["win_rate"] >= 70])
        
        print(f"  0% WR:       {wr_0} estrategias {'PROBLEMA!' if wr_0 > 0 else 'OK'}")
        print(f"  1-29% WR:    {wr_1_29} estrategias (Muito baixo)")
        print(f"  30-49% WR:   {wr_30_49} estrategias (Medio)")
        print(f"  50-69% WR:   {wr_50_69} estrategias (Bom)")
        print(f"  70%+ WR:     {wr_70plus} estrategias (Excelente)")
        print()
        
        # Strategies needing improvement
        needs_improvement = [r for r in valid_results if r["return"] < -5 or (r["win_rate"] < 30 and r["trades"] > 10)]
        if needs_improvement:
            print("=" * 140)
            print(f"ESTRATEGIAS QUE PRECISAM MELHORIA ({len(needs_improvement)}):")
            print("=" * 140)
            for r in sorted(needs_improvement, key=lambda x: x["return"]):
                reason = []
                if r["return"] < -10:
                    reason.append("Prejuizo severo")
                if r["win_rate"] < 20:
                    reason.append("WR muito baixo")
                if r["trades"] > 500:
                    reason.append("Overtrading")
                print(f"  - {r['strategy']:<50} {r['return']:+9.2f}% | Razoes: {', '.join(reason)}")
            print()
    
    # Save results
    output = {
        "date": datetime.now().isoformat(),
        "period": f"{start.date()} to {end.date()}",
        "total_strategies": total_strategies,
        "profitable_count": len(profitable),
        "zero_wr_count": len(zero_wr),
        "avg_return": avg_return if total_strategies > 0 else 0,
        "avg_trades": avg_trades if total_strategies > 0 else 0,
        "avg_win_rate": avg_wr if total_strategies > 0 else 0,
        "avg_sharpe": avg_sharpe if total_strategies > 0 else 0,
        "profitable_strategies": profitable,
        "high_wr_strategies": high_wr,
        "zero_wr_strategies": zero_wr,
        "results": results
    }
    
    with open("backtest_final_38_strategies.json", "w") as f:
        json.dump(output, f, indent=2, default=str)
    
    print("=" * 140)
    print("Resultados salvos em: backtest_final_38_strategies.json")
    print("=" * 140)
    print()
    
    # Final conclusion
    print("=" * 140)
    print("CONCLUSAO FINAL:")
    print("=" * 140)
    print(f"  {len(profitable)} estrategias lucrativas de {total_strategies} testadas ({len(profitable)/total_strategies*100:.1f}%)")
    print(f"  {len(zero_wr)} estrategias com 0% WR (exit logic {'FUNCIONOU!' if len(zero_wr) == 0 else 'precisa ajustes'})")
    print(f"  Retorno medio: {avg_return:+.2f}%")
    print(f"  Win rate medio: {avg_wr:.1f}%")
    print()
    
    if len(profitable) >= 5:
        print("  SISTEMA PRONTO! Temos estrategias lucrativas suficientes para portfolio diversificado!")
    elif len(profitable) >= 3:
        print("  BOM PROGRESSO! Temos estrategias lucrativas para comecar trading.")
    else:
        print("  Precisamos otimizar mais estrategias antes de producao.")
    
    print()
    print("  Proximos passos recomendados:")
    if len(profitable) > 0:
        print(f"    1. Paper trading com TOP {min(3, len(profitable))} estrategias")
        print("    2. Walk-forward analysis")
        print("    3. Otimizar parametros das lucrativas")
    if len(needs_improvement) > 0:
        print(f"    4. Corrigir {len(needs_improvement)} estrategias com problemas")
    if freq_500plus > 0:
        print(f"    5. Resolver overtrading em {freq_500plus} estrategias")
    
    print("=" * 140)

if __name__ == "__main__":
    asyncio.run(run_complete_backtest())
