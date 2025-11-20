# -*- coding: utf-8 -*-
"""
Lista das 22 estrategias com 1 trade que precisam de exit logic
"""

STRATEGIES_NEED_EXIT = [
    # Ja corrigida:
    # "multi_oscillator_confluence",
    
    # Precisam correcao:
    "donchian_volatility_breakout",
    "atr_expansion_breakout",
    "channel_squeeze_plus",
    "volatility_weighted_breakout",
    "london_breakout_atr",
    "mfi_impulse_momentum",
    "triple_momentum_confluence",
    "rsi_supertrend_flip",
    "obv_trend_confirmation",
    "trend_volume_combo",
    "ema_stack_regime_flip",
    "vwap_institutional_trend",
    "order_flow_momentum_vwap",
    "keltner_pullback_continuation",
    "ema200_tap_reversion",
    "double_donchian_pullback",
    "pure_price_action_donchian",
    "obv_confirmation_breakout_plus",
    "ny_session_fade",
    "regime_adaptive_core",
    "complete_system_5x"
]

# Exit logic patterns por tipo de estrategia:
EXIT_PATTERNS = {
    "oscillator": "Exit when oscillators reach opposite extreme",
    "momentum": "Exit when momentum reverses",
    "breakout": "Exit on trend reversal or stop loss",
    "mean_reversion": "Exit when price returns to mean",
    "trend_following": "Exit when trend changes"
}

print(f"Total strategies needing exit logic: {len(STRATEGIES_NEED_EXIT)}")
print()
print("Manual fixes needed for each...")
