# -*- coding: utf-8 -*-
"""
Complete Parameter Spaces

Parameter spaces for ALL 40+ strategies (built-in + generated).
Ready for genetic algorithm optimization.
"""

from .parameter_space import ParameterSpace, ParameterType


class AllParameterSpaces:
    """Complete collection of parameter spaces for all strategies"""
    
    # =========================================================================
    # BUILT-IN STRATEGIES
    # =========================================================================
    
    @staticmethod
    def rsi_strategy() -> ParameterSpace:
        """RSI Strategy - Built-in"""
        return ParameterSpace.from_dict({
            "rsi_period": {
                "type": ParameterType.INT,
                "low": 7,
                "high": 21,
                "description": "RSI calculation period"
            },
            "oversold_level": {
                "type": ParameterType.INT,
                "low": 20,
                "high": 35,
                "description": "Oversold threshold"
            },
            "overbought_level": {
                "type": ParameterType.INT,
                "low": 65,
                "high": 80,
                "description": "Overbought threshold"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.5,
                "high": 3.0,
                "description": "Stop-loss ATR multiplier"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.5,
                "high": 3.0,
                "description": "Take-profit risk-reward multiplier"
            }
        }, strategy_name="rsi")
    
    @staticmethod
    def macd_strategy() -> ParameterSpace:
        """MACD Strategy - Built-in"""
        return ParameterSpace.from_dict({
            "fast_period": {
                "type": ParameterType.INT,
                "low": 8,
                "high": 15,
                "description": "Fast EMA period"
            },
            "slow_period": {
                "type": ParameterType.INT,
                "low": 20,
                "high": 30,
                "description": "Slow EMA period"
            },
            "signal_period": {
                "type": ParameterType.INT,
                "low": 7,
                "high": 12,
                "description": "Signal line period"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.5,
                "high": 3.0,
                "description": "Stop-loss ATR multiplier"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.5,
                "high": 3.0,
                "description": "Take-profit risk-reward multiplier"
            }
        }, strategy_name="macd")
    
    @staticmethod
    def volume_shooter_strategy() -> ParameterSpace:
        """Volume Shooter Strategy - Built-in"""
        return ParameterSpace.from_dict({
            "volume_factor": {
                "type": ParameterType.FLOAT,
                "low": 1.5,
                "high": 3.0,
                "description": "Volume spike multiplier"
            },
            "volume_period": {
                "type": ParameterType.INT,
                "low": 30,
                "high": 100,
                "description": "Volume SMA period"
            },
            "take_profit_pct": {
                "type": ParameterType.FLOAT,
                "low": 50.0,
                "high": 150.0,
                "description": "Take profit percentage"
            },
            "stop_loss_pct": {
                "type": ParameterType.FLOAT,
                "low": 5.0,
                "high": 20.0,
                "description": "Stop loss percentage"
            },
        }, strategy_name="volume_shooter")
    
    # =========================================================================
    # MEAN REVERSION (5 strategies)
    # =========================================================================
    
    @staticmethod
    def rsi_band_reversion_strategy() -> ParameterSpace:
        """RSI Band Reversion"""
        return ParameterSpace.from_dict({
            "rsi_period": {"type": ParameterType.INT, "low": 10, "high": 21},
            "rsi_oversold": {"type": ParameterType.INT, "low": 25, "high": 35},
            "rsi_overbought": {"type": ParameterType.INT, "low": 65, "high": 75},
            "bb_period": {"type": ParameterType.INT, "low": 15, "high": 30},
            "bb_std": {"type": ParameterType.FLOAT, "low": 1.5, "high": 2.5},
            "ema_period": {"type": ParameterType.INT, "low": 40, "high": 60},
        }, strategy_name="rsi_band_reversion")
    
    @staticmethod
    def bollinger_mean_reversion_strategy() -> ParameterSpace:
        """Bollinger Mean Reversion"""
        return ParameterSpace.from_dict({
            "bb_period": {"type": ParameterType.INT, "low": 15, "high": 30},
            "bb_std": {"type": ParameterType.FLOAT, "low": 1.5, "high": 2.5},
            "rsi_filter": {"type": ParameterType.INT, "low": 40, "high": 60},
        }, strategy_name="bollinger_mean_reversion")
    
    @staticmethod
    def ema200_tap_reversion_strategy() -> ParameterSpace:
        """EMA200 Tap Reversion"""
        return ParameterSpace.from_dict({
            "ema_period": {"type": ParameterType.INT, "low": 150, "high": 250},
            "tap_threshold": {"type": ParameterType.FLOAT, "low": 0.3, "high": 1.0},
        }, strategy_name="ema200_tap_reversion")
    
    @staticmethod
    def vwap_mean_reversion_strategy() -> ParameterSpace:
        """VWAP Mean Reversion"""
        return ParameterSpace.from_dict({
            "vwap_deviation": {"type": ParameterType.FLOAT, "low": 1.5, "high": 3.0},
            "rsi_filter": {"type": ParameterType.INT, "low": 40, "high": 60},
        }, strategy_name="vwap_mean_reversion")
    
    @staticmethod
    def mfi_divergence_reversion_strategy() -> ParameterSpace:
        """MFI Divergence Reversion"""
        return ParameterSpace.from_dict({
            "mfi_period": {"type": ParameterType.INT, "low": 10, "high": 20},
            "mfi_oversold": {"type": ParameterType.INT, "low": 15, "high": 25},
            "mfi_overbought": {"type": ParameterType.INT, "low": 75, "high": 85},
        }, strategy_name="mfi_divergence_reversion")
    
    # =========================================================================
    # TREND FOLLOWING (5 strategies)
    # =========================================================================
    
    @staticmethod
    def trendflow_supertrend_strategy() -> ParameterSpace:
        """TrendFlow SuperTrend"""
        return ParameterSpace.from_dict({
            "st_multiplier": {"type": ParameterType.FLOAT, "low": 2.0, "high": 4.0},
            "adx_threshold": {"type": ParameterType.INT, "low": 20, "high": 30},
            "rsi_pullback_min": {"type": ParameterType.INT, "low": 35, "high": 45},
            "rsi_pullback_max": {"type": ParameterType.INT, "low": 55, "high": 65},
        }, strategy_name="trendflow_supertrend")
    
    @staticmethod
    def ema_cloud_trend_strategy() -> ParameterSpace:
        """EMA Cloud Trend"""
        return ParameterSpace.from_dict({
            "ema_fast": {"type": ParameterType.INT, "low": 15, "high": 25},
            "ema_slow": {"type": ParameterType.INT, "low": 40, "high": 60},
            "rsi_threshold": {"type": ParameterType.INT, "low": 45, "high": 55},
        }, strategy_name="ema_cloud_trend")
    
    @staticmethod
    def macd_zero_trend_strategy() -> ParameterSpace:
        """MACD Zero Trend"""
        return ParameterSpace.from_dict({
            "fast_period": {"type": ParameterType.INT, "low": 10, "high": 15},
            "slow_period": {"type": ParameterType.INT, "low": 22, "high": 30},
            "signal_period": {"type": ParameterType.INT, "low": 7, "high": 12},
        }, strategy_name="macd_zero_trend")
    
    @staticmethod
    def adx_trend_filter_plus_strategy() -> ParameterSpace:
        """ADX Trend Filter Plus"""
        return ParameterSpace.from_dict({
            "adx_threshold": {"type": ParameterType.INT, "low": 20, "high": 35},
            "ema_fast": {"type": ParameterType.INT, "low": 15, "high": 25},
            "ema_slow": {"type": ParameterType.INT, "low": 45, "high": 55},
        }, strategy_name="adx_trend_filter_plus")
    
    @staticmethod
    def donchian_continuation_strategy() -> ParameterSpace:
        """Donchian Continuation"""
        return ParameterSpace.from_dict({
            "donchian_period": {"type": ParameterType.INT, "low": 15, "high": 30},
            "adx_threshold": {"type": ParameterType.INT, "low": 20, "high": 30},
        }, strategy_name="donchian_continuation")
    
    # =========================================================================
    # BREAKOUT (8 strategies)
    # =========================================================================
    
    @staticmethod
    def bollinger_squeeze_breakout_strategy() -> ParameterSpace:
        """Bollinger Squeeze Breakout"""
        return ParameterSpace.from_dict({
            "bb_period": {"type": ParameterType.INT, "low": 15, "high": 25},
            "squeeze_threshold": {"type": ParameterType.FLOAT, "low": 0.3, "high": 0.8},
            "breakout_threshold": {"type": ParameterType.FLOAT, "low": 1.0, "high": 2.5},
        }, strategy_name="bollinger_squeeze_breakout")
    
    @staticmethod
    def atr_expansion_breakout_strategy() -> ParameterSpace:
        """ATR Expansion Breakout"""
        return ParameterSpace.from_dict({
            "atr_period": {"type": ParameterType.INT, "low": 10, "high": 20},
            "atr_multiplier": {"type": ParameterType.FLOAT, "low": 1.2, "high": 2.0},
        }, strategy_name="atr_expansion_breakout")
    
    @staticmethod
    def keltner_expansion_strategy() -> ParameterSpace:
        """Keltner Expansion"""
        return ParameterSpace.from_dict({
            "keltner_period": {"type": ParameterType.INT, "low": 15, "high": 25},
            "keltner_mult": {"type": ParameterType.FLOAT, "low": 1.5, "high": 2.5},
        }, strategy_name="keltner_expansion")
    
    @staticmethod
    def donchian_volatility_breakout_strategy() -> ParameterSpace:
        """Donchian Volatility Breakout"""
        return ParameterSpace.from_dict({
            "donchian_period": {"type": ParameterType.INT, "low": 15, "high": 30},
            "atr_threshold": {"type": ParameterType.FLOAT, "low": 1.0, "high": 2.0},
        }, strategy_name="donchian_volatility_breakout")
    
    # =========================================================================
    # MOMENTUM (8 strategies)
    # =========================================================================
    
    @staticmethod
    def ema_stack_momentum_strategy() -> ParameterSpace:
        """EMA Stack Momentum"""
        return ParameterSpace.from_dict({
            "ema_fast": {"type": ParameterType.INT, "low": 5, "high": 12},
            "ema_mid": {"type": ParameterType.INT, "low": 18, "high": 25},
            "ema_slow": {"type": ParameterType.INT, "low": 50, "high": 60},
        }, strategy_name="ema_stack_momentum")
    
    @staticmethod
    def triple_momentum_confluence_strategy() -> ParameterSpace:
        """Triple Momentum Confluence"""
        return ParameterSpace.from_dict({
            "rsi_period": {"type": ParameterType.INT, "low": 10, "high": 18},
            "macd_fast": {"type": ParameterType.INT, "low": 10, "high": 15},
            "stoch_k": {"type": ParameterType.INT, "low": 10, "high": 18},
        }, strategy_name="triple_momentum_confluence")
    
    @staticmethod
    def multi_oscillator_confluence_strategy() -> ParameterSpace:
        """Multi Oscillator Confluence"""
        return ParameterSpace.from_dict({
            "rsi_period": {"type": ParameterType.INT, "low": 10, "high": 21},
            "cci_period": {"type": ParameterType.INT, "low": 15, "high": 25},
            "stoch_k": {"type": ParameterType.INT, "low": 10, "high": 18},
        }, strategy_name="multi_oscillator_confluence")
    
    # =========================================================================
    # HYBRID (6 strategies)
    # =========================================================================
    
    @staticmethod
    def vwap_institutional_trend_strategy() -> ParameterSpace:
        """VWAP Institutional Trend"""
        return ParameterSpace.from_dict({
            "vwap_deviation": {"type": ParameterType.FLOAT, "low": 0.5, "high": 1.5},
            "obv_threshold": {"type": ParameterType.INT, "low": 10, "high": 30},
        }, strategy_name="vwap_institutional_trend")
    
    # =========================================================================
    # ADVANCED (6 strategies)
    # =========================================================================
    
    @staticmethod
    def regime_adaptive_core_strategy() -> ParameterSpace:
        """Regime Adaptive Core"""
        return ParameterSpace.from_dict({
            "adx_threshold": {"type": ParameterType.INT, "low": 20, "high": 30},
            "atr_period": {"type": ParameterType.INT, "low": 10, "high": 20},
            "regime_lookback": {"type": ParameterType.INT, "low": 50, "high": 100},
        }, strategy_name="regime_adaptive_core")
    
    @staticmethod
    def complete_system_5x_strategy() -> ParameterSpace:
        """Complete System 5X"""
        return ParameterSpace.from_dict({
            "ema_fast": {"type": ParameterType.INT, "low": 15, "high": 25},
            "rsi_period": {"type": ParameterType.INT, "low": 10, "high": 18},
            "macd_fast": {"type": ParameterType.INT, "low": 10, "high": 15},
            "adx_threshold": {"type": ParameterType.INT, "low": 20, "high": 30},
        }, strategy_name="complete_system_5x")


# Backward compatibility - keep CommonParameterSpaces
class CommonParameterSpaces(AllParameterSpaces):
    """Alias for AllParameterSpaces (backward compatibility)"""
    pass
