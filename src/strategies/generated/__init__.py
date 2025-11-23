"""Generated strategies - All 37 trading strategies"""

# Mean Reversion (5)
from .bollinger_mean_reversion import BollingerMeanReversion
from .rsi_band_reversion import RsiBandReversion
from .cci_extreme_snapback import CciExtremeSnapback
from .mfi_divergence_reversion import MfiDivergenceReversion
from .stoch_signal_reversal import StochSignalReversal

# Trend Following (4) - ? ema_cloud_trend removed (doesn't exist)
from .donchian_continuation import DonchianContinuation
from .macd_zero_trend import MacdZeroTrend
from .adx_trend_filter_plus import AdxTrendFilterPlus
from .trendflow_supertrend import TrendflowSupertrend

# Breakout (8)
from .bollinger_squeeze_breakout import BollingerSqueezeBreakout
from .keltner_expansion import KeltnerExpansion
from .donchian_volatility_breakout import DonchianVolatilityBreakout
from .atr_expansion_breakout import AtrExpansionBreakout
from .channel_squeeze_plus import ChannelSqueezePlus
from .volatility_weighted_breakout import VolatilityWeightedBreakout
from .london_breakout_atr import LondonBreakoutAtr
from .vwap_breakout import VwapBreakout

# Momentum (8)
from .ema_stack_momentum import EmaStackMomentum
from .mfi_impulse_momentum import MfiImpulseMomentum
from .triple_momentum_confluence import TripleMomentumConfluence
from .rsi_supertrend_flip import RsiSupertrendFlip
from .multi_oscillator_confluence import MultiOscillatorConfluence
from .obv_trend_confirmation import ObvTrendConfirmation
from .trend_volume_combo import TrendVolumeCombo
from .ema_stack_regime_flip import EmaStackRegimeFlip

# Hybrid (6)
from .vwap_institutional_trend import VwapInstitutionalTrend
from .vwap_mean_reversion import VwapMeanReversion
from .vwap_band_fade_pro import VwapBandFadePro
from .order_flow_momentum_vwap import OrderFlowMomentumVwap
from .keltner_pullback_continuation import KeltnerPullbackContinuation
from .ema200_tap_reversion import Ema200TapReversion

# Advanced (6)
from .double_donchian_pullback import DoubleDonchianPullback
from .pure_price_action_donchian import PurePriceActionDonchian
from .obv_confirmation_breakout_plus import ObvConfirmationBreakoutPlus
from .ny_session_fade import NySessionFade
from .regime_adaptive_core import RegimeAdaptiveCore
from .complete_system_5x import CompleteSystem5x

__all__ = [
    # Mean Reversion
    "BollingerMeanReversion",
    "RsiBandReversion",
    "CciExtremeSnapback",
    "MfiDivergenceReversion",
    "StochSignalReversal",
    # Trend Following (? removed EmaCloudTrend)
    "DonchianContinuation",
    "MacdZeroTrend",
    "AdxTrendFilterPlus",
    "TrendflowSupertrend",
    # Breakout
    "BollingerSqueezeBreakout",
    "KeltnerExpansion",
    "DonchianVolatilityBreakout",
    "AtrExpansionBreakout",
    "ChannelSqueezePlus",
    "VolatilityWeightedBreakout",
    "LondonBreakoutAtr",
    "VwapBreakout",
    # Momentum
    "EmaStackMomentum",
    "MfiImpulseMomentum",
    "TripleMomentumConfluence",
    "RsiSupertrendFlip",
    "MultiOscillatorConfluence",
    "ObvTrendConfirmation",
    "TrendVolumeCombo",
    "EmaStackRegimeFlip",
    # Hybrid
    "VwapInstitutionalTrend",
    "VwapMeanReversion",
    "VwapBandFadePro",
    "OrderFlowMomentumVwap",
    "KeltnerPullbackContinuation",
    "Ema200TapReversion",
    # Advanced
    "DoubleDonchianPullback",
    "PurePriceActionDonchian",
    "ObvConfirmationBreakoutPlus",
    "NySessionFade",
    "RegimeAdaptiveCore",
    "CompleteSystem5x",
]

