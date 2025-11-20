"""
Strategy Migration Tool

Converts strategies from old format to new MCP architecture.
Reads metadata and generates clean Strategy classes.
"""

from typing import Dict, Any, List
import re


# Strategy metadata from old repo
STRATEGY_METADATA = {
    # MEAN REVERSION (5 strategies)
    "rsi_band_reversion": {
        "category": "mean_reversion",
        "description": "Classic RSI oversold/overbought with Bollinger Band confirmation",
        "indicators": ["rsi", "bollinger", "ema", "atr"],
    },
    "bollinger_mean_reversion": {
        "category": "mean_reversion", 
        "description": "Price touches outer Bollinger Band and reverts to middle",
        "indicators": ["bollinger", "rsi", "atr"],
    },
    "ema200_tap_reversion": {
        "category": "mean_reversion",
        "description": "Price taps EMA200 in trending market then bounces",
        "indicators": ["ema", "rsi", "atr"],
    },
    "mfi_divergence_reversion": {
        "category": "mean_reversion",
        "description": "Volume-based reversal using MFI divergence detection",
        "indicators": ["mfi", "ema", "atr"],
    },
    "vwap_mean_reversion": {
        "category": "mean_reversion",
        "description": "Price deviation from VWAP with mean reversion",
        "indicators": ["vwap", "rsi", "atr"],
    },
    
    # TREND FOLLOWING (5 strategies)
    "trendflow_supertrend": {
        "category": "trend_following",
        "description": "SuperTrend + ADX momentum with pullback entries",
        "indicators": ["supertrend", "adx", "ema", "rsi", "atr"],
    },
    "ema_cloud_trend": {
        "category": "trend_following",
        "description": "Pullback to EMA20/50 cloud in trending markets",
        "indicators": ["ema", "rsi", "atr"],
    },
    "donchian_continuation": {
        "category": "trend_following",
        "description": "Donchian breakout with ADX momentum confirmation",
        "indicators": ["donchian", "adx", "ema", "atr"],
    },
    "macd_zero_trend": {
        "category": "trend_following",
        "description": "MACD histogram crosses zero with trend confirmation",
        "indicators": ["macd", "ema", "atr"],
    },
    "adx_trend_filter_plus": {
        "category": "trend_following",
        "description": "Pure ADX trend strength filter with EMA alignment",
        "indicators": ["adx", "ema", "atr"],
    },
    
    # BREAKOUT (8 strategies)
    "bollinger_squeeze_breakout": {
        "category": "breakout",
        "description": "Bollinger Band squeeze followed by explosive breakout",
        "indicators": ["bollinger", "atr", "rsi"],
    },
    "keltner_expansion": {
        "category": "breakout",
        "description": "Keltner Channel expansion breakout with volume",
        "indicators": ["keltner", "atr", "ema"],
    },
    "donchian_volatility_breakout": {
        "category": "breakout",
        "description": "Donchian breakout during volatility expansion",
        "indicators": ["donchian", "atr", "adx"],
    },
    "atr_expansion_breakout": {
        "category": "breakout",
        "description": "ATR expansion signals volatility breakout",
        "indicators": ["atr", "ema", "rsi"],
    },
    "channel_squeeze_plus": {
        "category": "breakout",
        "description": "Multi-channel squeeze breakout system",
        "indicators": ["bollinger", "keltner", "atr"],
    },
    "volatility_weighted_breakout": {
        "category": "breakout",
        "description": "Breakout weighted by volatility regime",
        "indicators": ["atr", "bollinger", "adx"],
    },
    "london_breakout_atr": {
        "category": "breakout",
        "description": "London session breakout with ATR filter",
        "indicators": ["atr", "ema"],
    },
    "vwap_breakout": {
        "category": "breakout",
        "description": "VWAP level breakout with volume confirmation",
        "indicators": ["vwap", "atr", "rsi"],
    },
    
    # MOMENTUM (8 strategies)
    "ema_stack_momentum": {
        "category": "momentum",
        "description": "EMA stack alignment with strong momentum",
        "indicators": ["ema", "rsi", "macd", "atr"],
    },
    "mfi_impulse_momentum": {
        "category": "momentum",
        "description": "MFI surge indicates strong buying/selling pressure",
        "indicators": ["mfi", "ema", "atr"],
    },
    "triple_momentum_confluence": {
        "category": "momentum",
        "description": "RSI + MACD + Stochastic alignment",
        "indicators": ["rsi", "macd", "stochastic", "atr"],
    },
    "obv_confirmation_breakout_plus": {
        "category": "momentum",
        "description": "OBV confirms price breakout with volume",
        "indicators": ["obv", "ema", "atr"],
    },
    "obv_trend_confirmation": {
        "category": "momentum",
        "description": "OBV trend confirms price trend",
        "indicators": ["obv", "ema", "adx", "atr"],
    },
    "order_flow_momentum_vwap": {
        "category": "momentum",
        "description": "Order flow momentum around VWAP levels",
        "indicators": ["vwap", "obv", "atr"],
    },
    "trend_volume_combo": {
        "category": "momentum",
        "description": "Trend + Volume confirmation combo",
        "indicators": ["ema", "obv", "atr"],
    },
    "ema_stack_regime_flip": {
        "category": "momentum",
        "description": "EMA stack flips indicate regime change",
        "indicators": ["ema", "rsi", "atr"],
    },
    
    # HYBRID (6 strategies)
    "keltner_pullback_continuation": {
        "category": "hybrid",
        "description": "Pullback to Keltner Channel then continuation",
        "indicators": ["keltner", "ema", "rsi", "atr"],
    },
    "double_donchian_pullback": {
        "category": "hybrid",
        "description": "Dual Donchian timeframe pullback system",
        "indicators": ["donchian", "ema", "atr"],
    },
    "rsi_supertrend_flip": {
        "category": "hybrid",
        "description": "RSI + SuperTrend alignment for entries",
        "indicators": ["rsi", "supertrend", "atr"],
    },
    "multi_oscillator_confluence": {
        "category": "hybrid",
        "description": "Multiple oscillators align for high-probability setup",
        "indicators": ["rsi", "cci", "stochastic", "atr"],
    },
    "vwap_institutional_trend": {
        "category": "hybrid",
        "description": "VWAP + institutional volume trend",
        "indicators": ["vwap", "obv", "ema", "atr"],
    },
    "regime_adaptive_core": {
        "category": "hybrid",
        "description": "Adapts strategy based on market regime detection",
        "indicators": ["adx", "atr", "ema", "rsi"],
    },
    
    # ADVANCED (6 strategies)
    "complete_system_5x": {
        "category": "advanced",
        "description": "Complete multi-factor system with 5 confirmations",
        "indicators": ["ema", "rsi", "macd", "adx", "atr"],
    },
    "pure_price_action_donchian": {
        "category": "advanced",
        "description": "Pure price action with Donchian levels",
        "indicators": ["donchian", "atr"],
    },
    "vwap_band_fade_pro": {
        "category": "advanced",
        "description": "Professional VWAP band fading system",
        "indicators": ["vwap", "rsi", "atr"],
    },
    "cci_extreme_snapback": {
        "category": "advanced",
        "description": "CCI extreme levels with snapback entries",
        "indicators": ["cci", "ema", "atr"],
    },
    "stoch_signal_reversal": {
        "category": "advanced",
        "description": "Stochastic overbought/oversold reversal",
        "indicators": ["stochastic", "rsi", "atr"],
    },
    "ny_session_fade": {
        "category": "advanced",
        "description": "New York session fade strategy",
        "indicators": ["vwap", "atr", "ema"],
    },
}


def generate_strategy_template(name: str, metadata: Dict[str, Any]) -> str:
    """Generate Python code for a strategy class."""
    
    class_name = "".join(word.capitalize() for word in name.split("_"))
    
    template = f'''"""
{metadata["description"]}
"""

from typing import List
import pandas as pd
import numpy as np

from .base import BaseStrategy, Signal, SignalType, StrategyConfig
from ..core.logger import logger


class {class_name}(BaseStrategy):
    """
    {class_name} - {metadata["description"]}
    
    Category: {metadata["category"]}
    Indicators: {", ".join(metadata["indicators"])}
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize {class_name} strategy."""
        super().__init__(config)
        
        # Strategy-specific parameters
        # TODO: Add configurable parameters from config.params
        
    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        return {metadata["indicators"]}
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        Generate trading signals.
        
        Args:
            df: DataFrame with OHLCV and indicator data
            
        Returns:
            List of trading signals
        """
        signals = []
        
        # TODO: Implement strategy logic
        # This is a placeholder - needs migration from old format
        
        logger.info(f"{class_name} generated {{len(signals)}} signals")
        return signals


__all__ = ["{class_name}"]
'''
    
    return template


def main():
    """Generate all strategy files."""
    print("=" * 70)
    print("Strategy Migration Tool")
    print("=" * 70)
    print()
    
    print(f"Total strategies to migrate: {len(STRATEGY_METADATA)}")
    print()
    
    # Group by category
    by_category = {}
    for name, meta in STRATEGY_METADATA.items():
        category = meta["category"]
        if category not in by_category:
            by_category[category] = []
        by_category[category].append((name, meta))
    
    for category, strategies in sorted(by_category.items()):
        print(f"\n[{category.upper()}] - {len(strategies)} strategies")
        for name, meta in strategies:
            print(f"  - {name}")
    
    print()
    print("=" * 70)
    print("Ready to generate strategy files!")
    print("Run this script to create placeholder strategies.")
    print("=" * 70)


if __name__ == "__main__":
    main()
