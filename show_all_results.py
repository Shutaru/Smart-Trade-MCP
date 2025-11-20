# -*- coding: utf-8 -*-
"""Mostrar resultados completos das 38 estrategias"""

import json
import pandas as pd

# Load results
with open("backtest_1year_results.json", "r") as f:
    data = json.load(f)

results = data["results"]
df = pd.DataFrame(results)

print("=" * 120)
print("RESULTADOS COMPLETOS - 38 ESTRATEGIAS - 1 ANO BTC/USDT 1h")
print("=" * 120)
print()

# Add rank
df['rank'] = range(1, len(df) + 1)

# Format and display
print(f"{'Rank':<6} {'Estrategia':<42} {'Return':>10} {'Trades':>8} {'Win Rate':>10} {'Sharpe':>10}")
print("-" * 120)

for i, row in df.iterrows():
    rank_str = f"#{row['rank']:02d}"
    
    # Add emoji for top 3
    if row['rank'] == 1:
        rank_str = "??#01"
    elif row['rank'] == 2:
        rank_str = "??#02"
    elif row['rank'] == 3:
        rank_str = "??#03"
    
    # Color code by performance
    if row['return'] > 5:
        prefix = "??"  # Excellent
    elif row['return'] > 0:
        prefix = "?  "  # Good
    elif row['return'] > -1:
        prefix = "?  "  # Neutral
    elif row['return'] > -10:
        prefix = "??  "  # Warning
    else:
        prefix = "?  "  # Critical
    
    print(f"{prefix} {rank_str:<6} {row['strategy']:<40} {row['return']:+9.2f}% {row['trades']:>7.0f} {row['win_rate']:>9.1f}% {row['sharpe']:>9.2f}")

print("-" * 120)
print()

# Summary stats
print("ESTATISTICAS RESUMIDAS:")
print(f"  Total: 38 estrategias")
print(f"  Lucrativas (>0%): {(df['return'] > 0).sum()} ({(df['return'] > 0).sum()/len(df)*100:.1f}%)")
print(f"  Prejuizo (<0%): {(df['return'] < 0).sum()} ({(df['return'] < 0).sum()/len(df)*100:.1f}%)")
print(f"  Break-even (0%): {(df['return'] == 0).sum()}")
print()
print(f"  Retorno medio: {df['return'].mean():+.2f}%")
print(f"  Retorno mediano: {df['return'].median():+.2f}%")
print(f"  Total de trades: {df['trades'].sum():.0f}")
print(f"  Media de trades: {df['trades'].mean():.1f}")
print()

# Categorize by trades
print("DISTRIBUICAO POR NUMERO DE TRADES:")
one_trade = (df['trades'] == 1).sum()
few_trades = ((df['trades'] > 1) & (df['trades'] <= 10)).sum()
some_trades = ((df['trades'] > 10) & (df['trades'] <= 50)).sum()
many_trades = ((df['trades'] > 50) & (df['trades'] <= 200)).sum()
very_many = (df['trades'] > 200).sum()

print(f"  1 trade: {one_trade} estrategias")
print(f"  2-10 trades: {few_trades} estrategias")
print(f"  11-50 trades: {some_trades} estrategias")
print(f"  51-200 trades: {many_trades} estrategias")
print(f"  >200 trades: {very_many} estrategias")
print()

# Win rate distribution
print("DISTRIBUICAO POR WIN RATE:")
wr_0 = (df['win_rate'] == 0).sum()
wr_low = ((df['win_rate'] > 0) & (df['win_rate'] < 30)).sum()
wr_mid = ((df['win_rate'] >= 30) & (df['win_rate'] < 50)).sum()
wr_good = ((df['win_rate'] >= 50) & (df['win_rate'] < 70)).sum()
wr_excellent = (df['win_rate'] >= 70).sum()

print(f"  0% WR: {wr_0} estrategias (PROBLEMA!)")
print(f"  1-29% WR: {wr_low} estrategias (Muito Baixo)")
print(f"  30-49% WR: {wr_mid} estrategias (Baixo/Medio)")
print(f"  50-69% WR: {wr_good} estrategias (Bom)")
print(f"  70%+ WR: {wr_excellent} estrategias (Excelente)")
print()
