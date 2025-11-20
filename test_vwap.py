# -*- coding: utf-8 -*-
"""Test VWAP calculation"""
import pandas as pd
import numpy as np
from src.core.indicators import calculate_all_indicators

df = pd.DataFrame({
    'open': np.random.rand(100)+100,
    'high': np.random.rand(100)+101,
    'low': np.random.rand(100)+99,
    'close': np.random.rand(100)+100,
    'volume': np.random.rand(100)*1000,
    'timestamp': pd.date_range('2024-01-01', periods=100)
})

df2 = calculate_all_indicators(df, ['vwap'])

print("VWAP existe?", 'vwap' in df2.columns)
print("Colunas com 'vwap':", [c for c in df2.columns if 'vwap' in c.lower()])
if 'vwap' in df2.columns:
    print("\nPrimeiros 10 valores VWAP:")
    print(df2['vwap'].head(10))
else:
    print("\nERROR: VWAP NAO FOI CALCULADO!")
    print("Todas as colunas:", df2.columns.tolist())
