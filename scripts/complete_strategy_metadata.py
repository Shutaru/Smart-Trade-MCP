# -*- coding: utf-8 -*-
"""
COMPLETE STRATEGY METADATA - All 41 Strategies

Comprehensive metadata for ALL strategies in the system.
Used by auto-fix scripts to connect parameters correctly.
"""

# ============================================================================
# COMPLETE METADATA FOR 41 STRATEGIES
# ============================================================================

COMPLETE_STRATEGY_METADATA = {
    # ========================================================================
    # MEAN REVERSION (5 strategies)
    # ========================================================================
    "bollinger_mean_reversion": {
        "category": "mean_reversion",
        "description": "Price touches outer Bollinger Band and reverts to middle",
        "indicators": ["bollinger", "rsi", "atr"],
        "default_params": {
            "bb_period": 20,
            "bb_std": 2.0,
            "rsi_period": 14,
            "rsi_filter": 50,
            "rsi_oversold": 35,
            "rsi_overbought": 65,
            "bb_width_min": 1.5,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.0,
        },
    },
    "rsi_band_reversion": {
        "category": "mean_reversion",
        "description": "Classic RSI oversold/overbought with Bollinger Band confirmation",
        "indicators": ["rsi", "bollinger", "ema", "atr"],
        "default_params": {
            "rsi_period": 14,
            "rsi_oversold": 30,
            "rsi_overbought": 70,
            "bb_period": 20,
            "bb_std": 2.0,
            "ema_period": 50,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.0,
        },
    },
    "ema200_tap_reversion": {
        "category": "mean_reversion",
        "description": "Price taps EMA200 in trending market then bounces",
        "indicators": ["ema", "rsi", "atr"],
        "default_params": {
            "ema_period": 200,
            "tap_threshold_pct": 0.5,
            "rsi_filter": 50,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.0,
        },
    },
    "vwap_mean_reversion": {
        "category": "mean_reversion",
        "description": "Price deviation from VWAP with mean reversion",
        "indicators": ["vwap", "rsi", "atr"],
        "default_params": {
            "vwap_deviation_std": 2.0,
            "rsi_filter": 50,
            "rsi_oversold": 35,
            "rsi_overbought": 65,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.0,
        },
    },
    "mfi_divergence_reversion": {
        "category": "mean_reversion",
        "description": "MFI divergence signals volume-based reversals",
        "indicators": ["mfi", "ema", "atr"],
        "default_params": {
            "mfi_period": 14,
            "mfi_oversold": 20,
            "mfi_overbought": 80,
            "ema_period": 50,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.0,
        },
    },
    
    # ========================================================================
    # TREND FOLLOWING (5 strategies)
    # ========================================================================
    "trendflow_supertrend": {
        "category": "trend_following",
        "description": "SuperTrend + ADX momentum with pullback entries",
        "indicators": ["supertrend", "adx", "ema", "rsi", "atr"],
        "default_params": {
            "st_period": 10,
            "st_multiplier": 3.0,
            "adx_threshold": 25,
            "rsi_pullback_min": 40,
            "rsi_pullback_max": 60,
            "ema_period": 20,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "ema_cloud_trend": {
        "category": "trend_following",
        "description": "Pullback to EMA20/50 cloud in trending markets",
        "indicators": ["ema", "rsi", "atr"],
        "default_params": {
            "ema_fast": 20,
            "ema_slow": 50,
            "rsi_threshold": 50,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "macd_zero_trend": {
        "category": "trend_following",
        "description": "MACD histogram crosses zero with trend confirmation",
        "indicators": ["macd", "ema", "atr"],
        "default_params": {
            "fast_period": 12,
            "slow_period": 26,
            "signal_period": 9,
            "ema_trend": 200,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "adx_trend_filter_plus": {
        "category": "trend_following",
        "description": "Pure ADX trend strength filter with EMA alignment",
        "indicators": ["adx", "ema", "atr"],
        "default_params": {
            "adx_period": 14,
            "adx_threshold": 25,
            "ema_fast": 20,
            "ema_slow": 50,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "donchian_continuation": {
        "category": "trend_following",
        "description": "Donchian breakout with ADX momentum confirmation",
        "indicators": ["donchian", "adx", "ema", "atr"],
        "default_params": {
            "donchian_period": 20,
            "adx_threshold": 25,
            "ema_period": 50,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    
    # ========================================================================
    # BREAKOUT (8 strategies)
    # ========================================================================
    "bollinger_squeeze_breakout": {
        "category": "breakout",
        "description": "Bollinger Band squeeze followed by explosive breakout",
        "indicators": ["bollinger", "keltner", "atr", "adx"],
        "default_params": {
            "bb_period": 20,
            "bb_std": 2.0,
            "keltner_period": 20,
            "keltner_mult": 1.5,
            "squeeze_threshold_pct": 5.0,
            "adx_threshold": 20,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 3.0,
        },
    },
    "atr_expansion_breakout": {
        "category": "breakout",
        "description": "ATR expansion signals volatility breakout",
        "indicators": ["atr", "ema", "supertrend", "adx"],
        "default_params": {
            "atr_period": 14,
            "atr_multiplier": 1.25,
            "stop_loss_atr_mult": 2.2,
            "take_profit_rr_ratio": 2.4,
        },
    },
    "keltner_expansion": {
        "category": "breakout",
        "description": "Keltner Channel expansion breakout with volume",
        "indicators": ["keltner", "atr", "ema"],
        "default_params": {
            "keltner_period": 20,
            "keltner_mult": 2.0,
            "expansion_threshold_pct": 10.0,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 3.0,
        },
    },
    "donchian_volatility_breakout": {
        "category": "breakout",
        "description": "Donchian breakout during volatility expansion",
        "indicators": ["donchian", "atr", "adx"],
        "default_params": {
            "donchian_period": 20,
            "atr_expansion_mult": 1.5,
            "adx_threshold": 20,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 3.0,
        },
    },
    "channel_squeeze_plus": {
        "category": "breakout",
        "description": "Multi-channel squeeze breakout system",
        "indicators": ["bollinger", "keltner", "donchian", "atr"],
        "default_params": {
            "bb_period": 20,
            "keltner_period": 20,
            "donchian_period": 20,
            "squeeze_threshold_pct": 5.0,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 3.0,
        },
    },
    "volatility_weighted_breakout": {
        "category": "breakout",
        "description": "Breakout weighted by volatility regime",
        "indicators": ["atr", "bollinger", "adx"],
        "default_params": {
            "atr_period": 14,
            "atr_mult": 1.5,
            "bb_period": 20,
            "adx_threshold": 20,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 3.0,
        },
    },
    "london_breakout_atr": {
        "category": "breakout",
        "description": "London session breakout with ATR filter",
        "indicators": ["atr", "ema"],
        "default_params": {
            "atr_period": 14,
            "atr_mult": 1.5,
            "ema_period": 20,
            "london_start_hour": 8,
            "london_end_hour": 12,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 3.0,
        },
    },
    "vwap_breakout": {
        "category": "breakout",
        "description": "VWAP level breakout with volume confirmation",
        "indicators": ["vwap", "atr", "rsi"],
        "default_params": {
            "vwap_deviation_std": 2.0,
            "volume_mult": 1.5,
            "rsi_threshold": 50,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 3.0,
        },
    },
    
    # ========================================================================
    # MOMENTUM (8 strategies)
    # ========================================================================
    "ema_stack_momentum": {
        "category": "momentum",
        "description": "EMA stack alignment with strong momentum",
        "indicators": ["ema", "rsi", "macd", "atr"],
        "default_params": {
            "ema_fast": 8,
            "ema_mid": 21,
            "ema_slow": 55,
            "rsi_threshold": 50,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "mfi_impulse_momentum": {
        "category": "momentum",
        "description": "MFI surge indicates strong buying/selling pressure",
        "indicators": ["mfi", "ema", "atr"],
        "default_params": {
            "mfi_period": 14,
            "mfi_threshold_high": 80,
            "mfi_threshold_low": 20,
            "ema_period": 20,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "triple_momentum_confluence": {
        "category": "momentum",
        "description": "RSI + MACD + Stochastic alignment",
        "indicators": ["rsi", "macd", "stochastic", "atr"],
        "default_params": {
            "rsi_period": 14,
            "rsi_threshold": 50,
            "macd_fast": 12,
            "macd_slow": 26,
            "macd_signal": 9,
            "stoch_k": 14,
            "stoch_d": 3,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "obv_trend_confirmation": {
        "category": "momentum",
        "description": "OBV trend confirms price trend",
        "indicators": ["obv", "ema", "adx", "atr"],
        "default_params": {
            "obv_ema_period": 20,
            "price_ema_period": 50,
            "adx_threshold": 25,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "trend_volume_combo": {
        "category": "momentum",
        "description": "Trend + Volume confirmation combo",
        "indicators": ["ema", "obv", "atr"],
        "default_params": {
            "ema_fast": 20,
            "ema_slow": 50,
            "obv_ema_period": 20,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "ema_stack_regime_flip": {
        "category": "momentum",
        "description": "EMA stack flips indicate regime change",
        "indicators": ["ema", "rsi", "atr"],
        "default_params": {
            "ema_fast": 8,
            "ema_mid": 21,
            "ema_slow": 55,
            "rsi_threshold": 50,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "rsi_supertrend_flip": {
        "category": "momentum",
        "description": "RSI + SuperTrend alignment for entries",
        "indicators": ["rsi", "supertrend", "atr"],
        "default_params": {
            "rsi_period": 14,
            "rsi_threshold": 50,
            "st_period": 10,
            "st_multiplier": 3.0,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "multi_oscillator_confluence": {
        "category": "momentum",
        "description": "Multiple oscillators align for high-probability setup",
        "indicators": ["rsi", "cci", "stochastic", "atr"],
        "default_params": {
            "rsi_period": 14,
            "rsi_oversold": 30,
            "rsi_overbought": 70,
            "cci_period": 20,
            "cci_oversold": -100,
            "cci_overbought": 100,
            "stoch_k": 14,
            "stoch_d": 3,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    
    # ========================================================================
    # HYBRID (6 strategies)
    # ========================================================================
    "vwap_institutional_trend": {
        "category": "hybrid",
        "description": "VWAP + institutional volume trend",
        "indicators": ["vwap", "obv", "ema", "atr"],
        "default_params": {
            "vwap_deviation_std": 1.0,
            "obv_ema_period": 20,
            "price_ema_period": 50,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "keltner_pullback_continuation": {
        "category": "hybrid",
        "description": "Pullback to Keltner Channel then continuation",
        "indicators": ["keltner", "ema", "rsi", "atr"],
        "default_params": {
            "keltner_period": 20,
            "keltner_mult": 2.0,
            "ema_period": 50,
            "rsi_threshold": 50,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "double_donchian_pullback": {
        "category": "hybrid",
        "description": "Dual Donchian timeframe pullback system",
        "indicators": ["donchian", "ema", "atr"],
        "default_params": {
            "donchian_fast": 10,
            "donchian_slow": 20,
            "ema_period": 50,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "order_flow_momentum_vwap": {
        "category": "hybrid",
        "description": "Order flow momentum around VWAP levels",
        "indicators": ["vwap", "obv", "atr"],
        "default_params": {
            "vwap_deviation_std": 1.0,
            "obv_ema_period": 20,
            "momentum_threshold": 1.5,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "obv_confirmation_breakout_plus": {
        "category": "hybrid",
        "description": "OBV confirms price breakout with volume",
        "indicators": ["obv", "ema", "atr"],
        "default_params": {
            "obv_ema_period": 20,
            "price_ema_period": 50,
            "breakout_threshold": 1.5,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "regime_adaptive_core": {
        "category": "hybrid",
        "description": "Adapts strategy based on market regime detection",
        "indicators": ["adx", "atr", "ema", "rsi"],
        "default_params": {
            "adx_period": 14,
            "adx_threshold_trending": 25,
            "adx_threshold_ranging": 20,
            "atr_period": 14,
            "regime_lookback": 100,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    
    # ========================================================================
    # ADVANCED (6 strategies)
    # ========================================================================
    "complete_system_5x": {
        "category": "advanced",
        "description": "Complete multi-factor system with 5 confirmations",
        "indicators": ["ema", "rsi", "macd", "adx", "atr"],
        "default_params": {
            "ema_fast": 20,
            "ema_slow": 50,
            "rsi_period": 14,
            "rsi_threshold": 50,
            "macd_fast": 12,
            "macd_slow": 26,
            "adx_threshold": 25,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "pure_price_action_donchian": {
        "category": "advanced",
        "description": "Pure price action with Donchian levels",
        "indicators": ["donchian", "atr"],
        "default_params": {
            "donchian_period": 20,
            "breakout_confirm_bars": 2,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "vwap_band_fade_pro": {
        "category": "advanced",
        "description": "Professional VWAP band fading system",
        "indicators": ["vwap", "rsi", "atr"],
        "default_params": {
            "vwap_deviation_std": 2.0,
            "rsi_oversold": 30,
            "rsi_overbought": 70,
            "fade_threshold": 1.5,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "cci_extreme_snapback": {
        "category": "advanced",
        "description": "CCI extreme levels with snapback entries",
        "indicators": ["cci", "ema", "atr"],
        "default_params": {
            "cci_period": 20,
            "cci_oversold": -200,
            "cci_overbought": 200,
            "ema_period": 50,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "stoch_signal_reversal": {
        "category": "advanced",
        "description": "Stochastic overbought/oversold reversal",
        "indicators": ["stochastic", "rsi", "atr"],
        "default_params": {
            "stoch_k": 14,
            "stoch_d": 3,
            "stoch_oversold": 20,
            "stoch_overbought": 80,
            "rsi_confirm": 50,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
    "ny_session_fade": {
        "category": "advanced",
        "description": "New York session fade strategy",
        "indicators": ["vwap", "atr", "ema"],
        "default_params": {
            "vwap_deviation_std": 2.0,
            "atr_period": 14,
            "ema_period": 20,
            "ny_start_hour": 14,
            "ny_end_hour": 18,
            "sl_atr_mult": 2.0,
            "tp_rr_mult": 2.5,
        },
    },
}


# Total count
print(f"Total strategies in metadata: {len(COMPLETE_STRATEGY_METADATA)}")
