# -*- coding: utf-8 -*-
"""
Auto-generated Parameter Spaces

Add these methods to AllParameterSpaces class.
"""

from .parameter_space import ParameterSpace, ParameterType


class GeneratedParameterSpaces:
    @staticmethod
    def bollinger_mean_reversion_strategy() -> ParameterSpace:
        """Price touches outer Bollinger Band and reverts to middle"""
        return ParameterSpace.from_dict({
            "bb_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Bb Period"
            },
            "bb_std": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Bb Std"
            },
            "rsi_period": {
                "type": ParameterType.INT,
                "low": 9,
                "high": 18,
                "description": "Rsi Period"
            },
            "rsi_filter": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Rsi Filter"
            },
            "rsi_oversold": {
                "type": ParameterType.INT,
                "low": 24,
                "high": 45,
                "description": "Rsi Oversold"
            },
            "rsi_overbought": {
                "type": ParameterType.INT,
                "low": 45,
                "high": 84,
                "description": "Rsi Overbought"
            },
            "bb_width_min": {
                "type": ParameterType.FLOAT,
                "low": 1.05,
                "high": 1.95,
                "description": "Bb Width Min"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="bollinger_mean_reversion")
    
    @staticmethod
    def rsi_band_reversion_strategy() -> ParameterSpace:
        """Classic RSI oversold/overbought with Bollinger Band confirmation"""
        return ParameterSpace.from_dict({
            "rsi_period": {
                "type": ParameterType.INT,
                "low": 9,
                "high": 18,
                "description": "Rsi Period"
            },
            "rsi_oversold": {
                "type": ParameterType.INT,
                "low": 21,
                "high": 39,
                "description": "Rsi Oversold"
            },
            "rsi_overbought": {
                "type": ParameterType.INT,
                "low": 49,
                "high": 91,
                "description": "Rsi Overbought"
            },
            "bb_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Bb Period"
            },
            "bb_std": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Bb Std"
            },
            "ema_period": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Ema Period"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="rsi_band_reversion")
    
    @staticmethod
    def ema200_tap_reversion_strategy() -> ParameterSpace:
        """Price taps EMA200 in trending market then bounces"""
        return ParameterSpace.from_dict({
            "ema_period": {
                "type": ParameterType.INT,
                "low": 140,
                "high": 260,
                "description": "Ema Period"
            },
            "tap_threshold_pct": {
                "type": ParameterType.FLOAT,
                "low": 0.35,
                "high": 0.65,
                "description": "Tap Threshold Pct"
            },
            "rsi_filter": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Rsi Filter"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="ema200_tap_reversion")
    
    @staticmethod
    def vwap_mean_reversion_strategy() -> ParameterSpace:
        """Price deviation from VWAP with mean reversion"""
        return ParameterSpace.from_dict({
            "vwap_deviation_std": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Vwap Deviation Std"
            },
            "rsi_filter": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Rsi Filter"
            },
            "rsi_oversold": {
                "type": ParameterType.INT,
                "low": 24,
                "high": 45,
                "description": "Rsi Oversold"
            },
            "rsi_overbought": {
                "type": ParameterType.INT,
                "low": 45,
                "high": 84,
                "description": "Rsi Overbought"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="vwap_mean_reversion")
    
    @staticmethod
    def mfi_divergence_reversion_strategy() -> ParameterSpace:
        """MFI divergence signals volume-based reversals"""
        return ParameterSpace.from_dict({
            "mfi_period": {
                "type": ParameterType.INT,
                "low": 9,
                "high": 18,
                "description": "Mfi Period"
            },
            "mfi_oversold": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Mfi Oversold"
            },
            "mfi_overbought": {
                "type": ParameterType.INT,
                "low": 56,
                "high": 104,
                "description": "Mfi Overbought"
            },
            "ema_period": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Ema Period"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="mfi_divergence_reversion")
    
    @staticmethod
    def trendflow_supertrend_strategy() -> ParameterSpace:
        """SuperTrend + ADX momentum with pullback entries"""
        return ParameterSpace.from_dict({
            "st_period": {
                "type": ParameterType.INT,
                "low": 7,
                "high": 13,
                "description": "St Period"
            },
            "st_multiplier": {
                "type": ParameterType.FLOAT,
                "low": 2.1,
                "high": 3.9,
                "description": "St Multiplier"
            },
            "adx_threshold": {
                "type": ParameterType.INT,
                "low": 17,
                "high": 32,
                "description": "Adx Threshold"
            },
            "rsi_pullback_min": {
                "type": ParameterType.INT,
                "low": 28,
                "high": 52,
                "description": "Rsi Pullback Min"
            },
            "rsi_pullback_max": {
                "type": ParameterType.INT,
                "low": 42,
                "high": 78,
                "description": "Rsi Pullback Max"
            },
            "ema_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Ema Period"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="trendflow_supertrend")
    
    @staticmethod
    def ema_cloud_trend_strategy() -> ParameterSpace:
        """Pullback to EMA20/50 cloud in trending markets"""
        return ParameterSpace.from_dict({
            "ema_fast": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Ema Fast"
            },
            "ema_slow": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Ema Slow"
            },
            "rsi_threshold": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Rsi Threshold"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="ema_cloud_trend")
    
    @staticmethod
    def macd_zero_trend_strategy() -> ParameterSpace:
        """MACD histogram crosses zero with trend confirmation"""
        return ParameterSpace.from_dict({
            "fast_period": {
                "type": ParameterType.INT,
                "low": 8,
                "high": 15,
                "description": "Fast Period"
            },
            "slow_period": {
                "type": ParameterType.INT,
                "low": 18,
                "high": 33,
                "description": "Slow Period"
            },
            "signal_period": {
                "type": ParameterType.INT,
                "low": 6,
                "high": 11,
                "description": "Signal Period"
            },
            "ema_trend": {
                "type": ParameterType.INT,
                "low": 140,
                "high": 260,
                "description": "Ema Trend"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="macd_zero_trend")
    
    @staticmethod
    def adx_trend_filter_plus_strategy() -> ParameterSpace:
        """Pure ADX trend strength filter with EMA alignment"""
        return ParameterSpace.from_dict({
            "adx_period": {
                "type": ParameterType.INT,
                "low": 9,
                "high": 18,
                "description": "Adx Period"
            },
            "adx_threshold": {
                "type": ParameterType.INT,
                "low": 17,
                "high": 32,
                "description": "Adx Threshold"
            },
            "ema_fast": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Ema Fast"
            },
            "ema_slow": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Ema Slow"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="adx_trend_filter_plus")
    
    @staticmethod
    def donchian_continuation_strategy() -> ParameterSpace:
        """Donchian breakout with ADX momentum confirmation"""
        return ParameterSpace.from_dict({
            "donchian_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Donchian Period"
            },
            "adx_threshold": {
                "type": ParameterType.INT,
                "low": 17,
                "high": 32,
                "description": "Adx Threshold"
            },
            "ema_period": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Ema Period"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="donchian_continuation")
    
    @staticmethod
    def bollinger_squeeze_breakout_strategy() -> ParameterSpace:
        """Bollinger Band squeeze followed by explosive breakout"""
        return ParameterSpace.from_dict({
            "bb_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Bb Period"
            },
            "bb_std": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Bb Std"
            },
            "keltner_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Keltner Period"
            },
            "keltner_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.05,
                "high": 1.95,
                "description": "Keltner Mult"
            },
            "squeeze_threshold_pct": {
                "type": ParameterType.FLOAT,
                "low": 3.5,
                "high": 6.5,
                "description": "Squeeze Threshold Pct"
            },
            "adx_threshold": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Adx Threshold"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 2.1,
                "high": 3.9,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="bollinger_squeeze_breakout")
    
    @staticmethod
    def atr_expansion_breakout_strategy() -> ParameterSpace:
        """ATR expansion signals volatility breakout"""
        return ParameterSpace.from_dict({
            "atr_period": {
                "type": ParameterType.INT,
                "low": 9,
                "high": 18,
                "description": "Atr Period"
            },
            "atr_multiplier": {
                "type": ParameterType.FLOAT,
                "low": 0.88,
                "high": 1.62,
                "description": "Atr Multiplier"
            },
            "stop_loss_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.54,
                "high": 2.86,
                "description": "Stop Loss Atr Mult"
            },
            "take_profit_rr_ratio": {
                "type": ParameterType.FLOAT,
                "low": 1.68,
                "high": 3.12,
                "description": "Take Profit Rr Ratio"
            },
        }, strategy_name="atr_expansion_breakout")
    
    @staticmethod
    def keltner_expansion_strategy() -> ParameterSpace:
        """Keltner Channel expansion breakout with volume"""
        return ParameterSpace.from_dict({
            "keltner_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Keltner Period"
            },
            "keltner_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Keltner Mult"
            },
            "expansion_threshold_pct": {
                "type": ParameterType.FLOAT,
                "low": 7.0,
                "high": 13.0,
                "description": "Expansion Threshold Pct"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 2.1,
                "high": 3.9,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="keltner_expansion")
    
    @staticmethod
    def donchian_volatility_breakout_strategy() -> ParameterSpace:
        """Donchian breakout during volatility expansion"""
        return ParameterSpace.from_dict({
            "donchian_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Donchian Period"
            },
            "atr_expansion_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.05,
                "high": 1.95,
                "description": "Atr Expansion Mult"
            },
            "adx_threshold": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Adx Threshold"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 2.1,
                "high": 3.9,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="donchian_volatility_breakout")
    
    @staticmethod
    def channel_squeeze_plus_strategy() -> ParameterSpace:
        """Multi-channel squeeze breakout system"""
        return ParameterSpace.from_dict({
            "bb_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Bb Period"
            },
            "keltner_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Keltner Period"
            },
            "donchian_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Donchian Period"
            },
            "squeeze_threshold_pct": {
                "type": ParameterType.FLOAT,
                "low": 3.5,
                "high": 6.5,
                "description": "Squeeze Threshold Pct"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 2.1,
                "high": 3.9,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="channel_squeeze_plus")
    
    @staticmethod
    def volatility_weighted_breakout_strategy() -> ParameterSpace:
        """Breakout weighted by volatility regime"""
        return ParameterSpace.from_dict({
            "atr_period": {
                "type": ParameterType.INT,
                "low": 9,
                "high": 18,
                "description": "Atr Period"
            },
            "atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.05,
                "high": 1.95,
                "description": "Atr Mult"
            },
            "bb_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Bb Period"
            },
            "adx_threshold": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Adx Threshold"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 2.1,
                "high": 3.9,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="volatility_weighted_breakout")
    
    @staticmethod
    def london_breakout_atr_strategy() -> ParameterSpace:
        """London session breakout with ATR filter"""
        return ParameterSpace.from_dict({
            "atr_period": {
                "type": ParameterType.INT,
                "low": 9,
                "high": 18,
                "description": "Atr Period"
            },
            "atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.05,
                "high": 1.95,
                "description": "Atr Mult"
            },
            "ema_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Ema Period"
            },
            "london_start_hour": {
                "type": ParameterType.INT,
                "low": 5,
                "high": 10,
                "description": "London Start Hour"
            },
            "london_end_hour": {
                "type": ParameterType.INT,
                "low": 8,
                "high": 15,
                "description": "London End Hour"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 2.1,
                "high": 3.9,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="london_breakout_atr")
    
    @staticmethod
    def vwap_breakout_strategy() -> ParameterSpace:
        """VWAP level breakout with volume confirmation"""
        return ParameterSpace.from_dict({
            "vwap_deviation_std": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Vwap Deviation Std"
            },
            "volume_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.05,
                "high": 1.95,
                "description": "Volume Mult"
            },
            "rsi_threshold": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Rsi Threshold"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 2.1,
                "high": 3.9,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="vwap_breakout")
    
    @staticmethod
    def ema_stack_momentum_strategy() -> ParameterSpace:
        """EMA stack alignment with strong momentum"""
        return ParameterSpace.from_dict({
            "ema_fast": {
                "type": ParameterType.INT,
                "low": 5,
                "high": 10,
                "description": "Ema Fast"
            },
            "ema_mid": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 27,
                "description": "Ema Mid"
            },
            "ema_slow": {
                "type": ParameterType.INT,
                "low": 38,
                "high": 71,
                "description": "Ema Slow"
            },
            "rsi_threshold": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Rsi Threshold"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="ema_stack_momentum")
    
    @staticmethod
    def mfi_impulse_momentum_strategy() -> ParameterSpace:
        """MFI surge indicates strong buying/selling pressure"""
        return ParameterSpace.from_dict({
            "mfi_period": {
                "type": ParameterType.INT,
                "low": 9,
                "high": 18,
                "description": "Mfi Period"
            },
            "mfi_threshold_high": {
                "type": ParameterType.INT,
                "low": 56,
                "high": 104,
                "description": "Mfi Threshold High"
            },
            "mfi_threshold_low": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Mfi Threshold Low"
            },
            "ema_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Ema Period"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="mfi_impulse_momentum")
    
    @staticmethod
    def triple_momentum_confluence_strategy() -> ParameterSpace:
        """RSI + MACD + Stochastic alignment"""
        return ParameterSpace.from_dict({
            "rsi_period": {
                "type": ParameterType.INT,
                "low": 9,
                "high": 18,
                "description": "Rsi Period"
            },
            "rsi_threshold": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Rsi Threshold"
            },
            "macd_fast": {
                "type": ParameterType.INT,
                "low": 8,
                "high": 15,
                "description": "Macd Fast"
            },
            "macd_slow": {
                "type": ParameterType.INT,
                "low": 18,
                "high": 33,
                "description": "Macd Slow"
            },
            "macd_signal": {
                "type": ParameterType.INT,
                "low": 6,
                "high": 11,
                "description": "Macd Signal"
            },
            "stoch_k": {
                "type": ParameterType.INT,
                "low": 9,
                "high": 18,
                "description": "Stoch K"
            },
            "stoch_d": {
                "type": ParameterType.INT,
                "low": 2,
                "high": 3,
                "description": "Stoch D"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="triple_momentum_confluence")
    
    @staticmethod
    def obv_trend_confirmation_strategy() -> ParameterSpace:
        """OBV trend confirms price trend"""
        return ParameterSpace.from_dict({
            "obv_ema_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Obv Ema Period"
            },
            "price_ema_period": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Price Ema Period"
            },
            "adx_threshold": {
                "type": ParameterType.INT,
                "low": 17,
                "high": 32,
                "description": "Adx Threshold"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="obv_trend_confirmation")
    
    @staticmethod
    def trend_volume_combo_strategy() -> ParameterSpace:
        """Trend + Volume confirmation combo"""
        return ParameterSpace.from_dict({
            "ema_fast": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Ema Fast"
            },
            "ema_slow": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Ema Slow"
            },
            "obv_ema_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Obv Ema Period"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="trend_volume_combo")
    
    @staticmethod
    def ema_stack_regime_flip_strategy() -> ParameterSpace:
        """EMA stack flips indicate regime change"""
        return ParameterSpace.from_dict({
            "ema_fast": {
                "type": ParameterType.INT,
                "low": 5,
                "high": 10,
                "description": "Ema Fast"
            },
            "ema_mid": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 27,
                "description": "Ema Mid"
            },
            "ema_slow": {
                "type": ParameterType.INT,
                "low": 38,
                "high": 71,
                "description": "Ema Slow"
            },
            "rsi_threshold": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Rsi Threshold"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="ema_stack_regime_flip")
    
    @staticmethod
    def rsi_supertrend_flip_strategy() -> ParameterSpace:
        """RSI + SuperTrend alignment for entries"""
        return ParameterSpace.from_dict({
            "rsi_period": {
                "type": ParameterType.INT,
                "low": 9,
                "high": 18,
                "description": "Rsi Period"
            },
            "rsi_threshold": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Rsi Threshold"
            },
            "st_period": {
                "type": ParameterType.INT,
                "low": 7,
                "high": 13,
                "description": "St Period"
            },
            "st_multiplier": {
                "type": ParameterType.FLOAT,
                "low": 2.1,
                "high": 3.9,
                "description": "St Multiplier"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="rsi_supertrend_flip")
    
    @staticmethod
    def multi_oscillator_confluence_strategy() -> ParameterSpace:
        """Multiple oscillators align for high-probability setup"""
        return ParameterSpace.from_dict({
            "rsi_period": {
                "type": ParameterType.INT,
                "low": 9,
                "high": 18,
                "description": "Rsi Period"
            },
            "rsi_oversold": {
                "type": ParameterType.INT,
                "low": 21,
                "high": 39,
                "description": "Rsi Oversold"
            },
            "rsi_overbought": {
                "type": ParameterType.INT,
                "low": 49,
                "high": 91,
                "description": "Rsi Overbought"
            },
            "cci_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Cci Period"
            },
            "cci_oversold": {
                "type": ParameterType.INT,
                "low": -70,
                "high": -130,
                "description": "Cci Oversold"
            },
            "cci_overbought": {
                "type": ParameterType.INT,
                "low": 70,
                "high": 130,
                "description": "Cci Overbought"
            },
            "stoch_k": {
                "type": ParameterType.INT,
                "low": 9,
                "high": 18,
                "description": "Stoch K"
            },
            "stoch_d": {
                "type": ParameterType.INT,
                "low": 2,
                "high": 3,
                "description": "Stoch D"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="multi_oscillator_confluence")
    
    @staticmethod
    def vwap_institutional_trend_strategy() -> ParameterSpace:
        """VWAP + institutional volume trend"""
        return ParameterSpace.from_dict({
            "vwap_deviation_std": {
                "type": ParameterType.FLOAT,
                "low": 0.7,
                "high": 1.3,
                "description": "Vwap Deviation Std"
            },
            "obv_ema_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Obv Ema Period"
            },
            "price_ema_period": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Price Ema Period"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="vwap_institutional_trend")
    
    @staticmethod
    def keltner_pullback_continuation_strategy() -> ParameterSpace:
        """Pullback to Keltner Channel then continuation"""
        return ParameterSpace.from_dict({
            "keltner_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Keltner Period"
            },
            "keltner_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Keltner Mult"
            },
            "ema_period": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Ema Period"
            },
            "rsi_threshold": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Rsi Threshold"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="keltner_pullback_continuation")
    
    @staticmethod
    def double_donchian_pullback_strategy() -> ParameterSpace:
        """Dual Donchian timeframe pullback system"""
        return ParameterSpace.from_dict({
            "donchian_fast": {
                "type": ParameterType.INT,
                "low": 7,
                "high": 13,
                "description": "Donchian Fast"
            },
            "donchian_slow": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Donchian Slow"
            },
            "ema_period": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Ema Period"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="double_donchian_pullback")
    
    @staticmethod
    def order_flow_momentum_vwap_strategy() -> ParameterSpace:
        """Order flow momentum around VWAP levels"""
        return ParameterSpace.from_dict({
            "vwap_deviation_std": {
                "type": ParameterType.FLOAT,
                "low": 0.7,
                "high": 1.3,
                "description": "Vwap Deviation Std"
            },
            "obv_ema_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Obv Ema Period"
            },
            "momentum_threshold": {
                "type": ParameterType.FLOAT,
                "low": 1.05,
                "high": 1.95,
                "description": "Momentum Threshold"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="order_flow_momentum_vwap")
    
    @staticmethod
    def obv_confirmation_breakout_plus_strategy() -> ParameterSpace:
        """OBV confirms price breakout with volume"""
        return ParameterSpace.from_dict({
            "obv_ema_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Obv Ema Period"
            },
            "price_ema_period": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Price Ema Period"
            },
            "breakout_threshold": {
                "type": ParameterType.FLOAT,
                "low": 1.05,
                "high": 1.95,
                "description": "Breakout Threshold"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="obv_confirmation_breakout_plus")
    
    @staticmethod
    def regime_adaptive_core_strategy() -> ParameterSpace:
        """Adapts strategy based on market regime detection"""
        return ParameterSpace.from_dict({
            "adx_period": {
                "type": ParameterType.INT,
                "low": 9,
                "high": 18,
                "description": "Adx Period"
            },
            "adx_threshold_trending": {
                "type": ParameterType.INT,
                "low": 17,
                "high": 32,
                "description": "Adx Threshold Trending"
            },
            "adx_threshold_ranging": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Adx Threshold Ranging"
            },
            "atr_period": {
                "type": ParameterType.INT,
                "low": 9,
                "high": 18,
                "description": "Atr Period"
            },
            "regime_lookback": {
                "type": ParameterType.INT,
                "low": 70,
                "high": 130,
                "description": "Regime Lookback"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="regime_adaptive_core")
    
    @staticmethod
    def complete_system_5x_strategy() -> ParameterSpace:
        """Complete multi-factor system with 5 confirmations"""
        return ParameterSpace.from_dict({
            "ema_fast": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Ema Fast"
            },
            "ema_slow": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Ema Slow"
            },
            "rsi_period": {
                "type": ParameterType.INT,
                "low": 9,
                "high": 18,
                "description": "Rsi Period"
            },
            "rsi_threshold": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Rsi Threshold"
            },
            "macd_fast": {
                "type": ParameterType.INT,
                "low": 8,
                "high": 15,
                "description": "Macd Fast"
            },
            "macd_slow": {
                "type": ParameterType.INT,
                "low": 18,
                "high": 33,
                "description": "Macd Slow"
            },
            "adx_threshold": {
                "type": ParameterType.INT,
                "low": 17,
                "high": 32,
                "description": "Adx Threshold"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="complete_system_5x")
    
    @staticmethod
    def pure_price_action_donchian_strategy() -> ParameterSpace:
        """Pure price action with Donchian levels"""
        return ParameterSpace.from_dict({
            "donchian_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Donchian Period"
            },
            "breakout_confirm_bars": {
                "type": ParameterType.INT,
                "low": 1,
                "high": 2,
                "description": "Breakout Confirm Bars"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="pure_price_action_donchian")
    
    @staticmethod
    def vwap_band_fade_pro_strategy() -> ParameterSpace:
        """Professional VWAP band fading system"""
        return ParameterSpace.from_dict({
            "vwap_deviation_std": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Vwap Deviation Std"
            },
            "rsi_oversold": {
                "type": ParameterType.INT,
                "low": 21,
                "high": 39,
                "description": "Rsi Oversold"
            },
            "rsi_overbought": {
                "type": ParameterType.INT,
                "low": 49,
                "high": 91,
                "description": "Rsi Overbought"
            },
            "fade_threshold": {
                "type": ParameterType.FLOAT,
                "low": 1.05,
                "high": 1.95,
                "description": "Fade Threshold"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="vwap_band_fade_pro")
    
    @staticmethod
    def cci_extreme_snapback_strategy() -> ParameterSpace:
        """CCI extreme levels with snapback entries"""
        return ParameterSpace.from_dict({
            "cci_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Cci Period"
            },
            "cci_oversold": {
                "type": ParameterType.INT,
                "low": -140,
                "high": -260,
                "description": "Cci Oversold"
            },
            "cci_overbought": {
                "type": ParameterType.INT,
                "low": 140,
                "high": 260,
                "description": "Cci Overbought"
            },
            "ema_period": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Ema Period"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="cci_extreme_snapback")
    
    @staticmethod
    def stoch_signal_reversal_strategy() -> ParameterSpace:
        """Stochastic overbought/oversold reversal"""
        return ParameterSpace.from_dict({
            "stoch_k": {
                "type": ParameterType.INT,
                "low": 9,
                "high": 18,
                "description": "Stoch K"
            },
            "stoch_d": {
                "type": ParameterType.INT,
                "low": 2,
                "high": 3,
                "description": "Stoch D"
            },
            "stoch_oversold": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Stoch Oversold"
            },
            "stoch_overbought": {
                "type": ParameterType.INT,
                "low": 56,
                "high": 104,
                "description": "Stoch Overbought"
            },
            "rsi_confirm": {
                "type": ParameterType.INT,
                "low": 35,
                "high": 65,
                "description": "Rsi Confirm"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="stoch_signal_reversal")
    
    @staticmethod
    def ny_session_fade_strategy() -> ParameterSpace:
        """New York session fade strategy"""
        return ParameterSpace.from_dict({
            "vwap_deviation_std": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Vwap Deviation Std"
            },
            "atr_period": {
                "type": ParameterType.INT,
                "low": 9,
                "high": 18,
                "description": "Atr Period"
            },
            "ema_period": {
                "type": ParameterType.INT,
                "low": 14,
                "high": 26,
                "description": "Ema Period"
            },
            "ny_start_hour": {
                "type": ParameterType.INT,
                "low": 9,
                "high": 18,
                "description": "Ny Start Hour"
            },
            "ny_end_hour": {
                "type": ParameterType.INT,
                "low": 12,
                "high": 23,
                "description": "Ny End Hour"
            },
            "sl_atr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.4,
                "high": 2.6,
                "description": "Sl Atr Mult"
            },
            "tp_rr_mult": {
                "type": ParameterType.FLOAT,
                "low": 1.75,
                "high": 3.25,
                "description": "Tp Rr Mult"
            },
        }, strategy_name="ny_session_fade")
    
