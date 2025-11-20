"""
Batch Strategy Implementation

This script reads strategies from the old repo and converts them
to the new format. Focuses on TOP performing strategies first.
"""

TOP_10_STRATEGIES = [
    # Win Rate 60-70%
    "bollinger_mean_reversion",
    
    # Win Rate 58-68%
    "rsi_band_reversion",
    "vwap_institutional_trend",
    
    # Win Rate 56-64%
    "ema200_tap_reversion",
    
    # Win Rate 55-65%
    "rsi_band_reversion", 
    
    # Win Rate 50-60%
    "ema_cloud_trend",
    "keltner_pullback_continuation",
    
    # Proven performers
    "trendflow_supertrend",  # Already implemented
    "donchian_continuation",
    "bollinger_squeeze_breakout",
]

print("TOP 10 Strategies to implement:")
for i, strategy in enumerate(TOP_10_STRATEGIES, 1):
    print(f"{i}. {strategy}")
