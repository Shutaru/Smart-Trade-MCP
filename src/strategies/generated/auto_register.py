# -*- coding: utf-8 -*-
"""Auto-register all 37 generated strategies (1 was removed: ema_cloud_trend)"""

from ...core.logger import logger
from ..base import StrategyConfig  # ? Import StrategyConfig
import importlib


def register_all_generated_strategies(registry_instance):
    """Register all 37 generated strategies automatically (1 was removed: ema_cloud_trend)."""
    
    # Define all 37 strategies with their metadata (was 38, removed ema_cloud_trend)
    strategies_to_register = [
        # Mean Reversion (5)
        ("bollinger_mean_reversion", "BollingerMeanReversion", "mean_reversion", "BB mean reversion 60-70% win rate"),
        ("rsi_band_reversion", "RsiBandReversion", "mean_reversion", "RSI + BB reversion 58-68% win rate"),
        ("cci_extreme_snapback", "CciExtremeSnapback", "mean_reversion", "CCI extreme reversal"),
        ("mfi_divergence_reversion", "MfiDivergenceReversion", "mean_reversion", "MFI divergence 52-62% win rate"),
        ("stoch_signal_reversal", "StochSignalReversal", "mean_reversion", "Stochastic crossover reversal"),
        
        # Trend Following (4) - ema_cloud_trend removed
        ("donchian_continuation", "DonchianContinuation", "trend_following", "Donchian breakout continuation"),
        ("macd_zero_trend", "MacdZeroTrend", "trend_following", "MACD zero line trend"),
        ("adx_trend_filter_plus", "AdxTrendFilterPlus", "trend_following", "ADX trend filter 48-58% win rate"),
        ("trendflow_supertrend", "TrendflowSupertrend", "trend_following", "SuperTrend + ADX momentum"),
        
        # Breakout (8)
        ("bollinger_squeeze_breakout", "BollingerSqueezeBreakout", "breakout", "BB squeeze expansion"),
        ("keltner_expansion", "KeltnerExpansion", "breakout", "Keltner channel expansion"),
        ("donchian_volatility_breakout", "DonchianVolatilityBreakout", "breakout", "Donchian with volatility"),
        ("atr_expansion_breakout", "AtrExpansionBreakout", "breakout", "ATR expansion breakout"),
        ("channel_squeeze_plus", "ChannelSqueezePlus", "breakout", "Multi-channel squeeze"),
        ("volatility_weighted_breakout", "VolatilityWeightedBreakout", "breakout", "Volatility weighted breakout"),
        ("london_breakout_atr", "LondonBreakoutAtr", "breakout", "London session breakout"),
        ("vwap_breakout", "VwapBreakout", "breakout", "VWAP breakout"),
        
        # Momentum (8)
        ("ema_stack_momentum", "EmaStackMomentum", "momentum", "EMA stack alignment"),
        ("mfi_impulse_momentum", "MfiImpulseMomentum", "momentum", "MFI impulse momentum"),
        ("triple_momentum_confluence", "TripleMomentumConfluence", "momentum", "Triple oscillator confluence"),
        ("rsi_supertrend_flip", "RsiSupertrendFlip", "momentum", "RSI + SuperTrend flip"),
        ("multi_oscillator_confluence", "MultiOscillatorConfluence", "momentum", "Multi oscillator alignment"),
        ("obv_trend_confirmation", "ObvTrendConfirmation", "momentum", "OBV trend confirmation"),
        ("trend_volume_combo", "TrendVolumeCombo", "momentum", "Trend + volume combination"),
        ("ema_stack_regime_flip", "EmaStackRegimeFlip", "momentum", "EMA stack regime change"),
        
        # Hybrid (6)
        ("vwap_institutional_trend", "VwapInstitutionalTrend", "hybrid", "VWAP institutional 58-68% win rate"),
        ("vwap_mean_reversion", "VwapMeanReversion", "hybrid", "VWAP mean reversion"),
        ("vwap_band_fade_pro", "VwapBandFadePro", "hybrid", "VWAP band fade"),
        ("order_flow_momentum_vwap", "OrderFlowMomentumVwap", "hybrid", "Order flow + VWAP"),
        ("keltner_pullback_continuation", "KeltnerPullbackContinuation", "hybrid", "Keltner pullback"),
        ("ema200_tap_reversion", "Ema200TapReversion", "hybrid", "EMA200 tap reversion 56-64%"),
        
        # Advanced (6)
        ("double_donchian_pullback", "DoubleDonchianPullback", "advanced", "Double Donchian pullback"),
        ("pure_price_action_donchian", "PurePriceActionDonchian", "advanced", "Pure price action"),
        ("obv_confirmation_breakout_plus", "ObvConfirmationBreakoutPlus", "advanced", "OBV breakout confirmation"),
        ("ny_session_fade", "NySessionFade", "advanced", "NY session fade"),
        ("regime_adaptive_core", "RegimeAdaptiveCore", "advanced", "Regime adaptive 52-66%"),
        ("complete_system_5x", "CompleteSystem5x", "advanced", "Complete system 56-68%"),
    ]
    
    registered = 0
    for strategy_name, class_name, category, description in strategies_to_register:
        try:
            # ? FIX: Use importlib for proper imports
            module = importlib.import_module(f'.{strategy_name}', package='src.strategies.generated')
            strategy_class = getattr(module, class_name)
            
            # ? FIX: Extract default params from strategy instance
            # Create temp instance to read default values from __init__
            temp_config = StrategyConfig()
            temp_instance = strategy_class(temp_config)
            
            # Extract all params that were set (NOT sl_atr_mult/tp_rr_mult, those are universal)
            default_params = {}
            for attr_name in dir(temp_instance):
                if not attr_name.startswith('_') and attr_name not in ['config', 'calculate_exit_levels', 'backtest_signals', 'get_required_indicators', 'generate_signals']:
                    attr_value = getattr(temp_instance, attr_name, None)
                    # Only include simple types (int, float, str, bool)
                    if isinstance(attr_value, (int, float, str, bool)):
                        # Skip sl/tp as they're universal
                        if attr_name not in ['sl_atr_mult', 'tp_rr_mult']:
                            default_params[attr_name] = attr_value
            
            # Register with extracted defaults
            registry_instance.register(
                name=strategy_name,
                strategy_class=strategy_class,
                category=category,
                description=description,
                default_params=default_params,  # ? Now has real defaults!
            )
            registered += 1
            
        except (ImportError, AttributeError) as e:
            logger.debug(f"Skipping {strategy_name}: {e}")
    
    logger.info(f"? Auto-registered {registered}/37 generated strategies")
