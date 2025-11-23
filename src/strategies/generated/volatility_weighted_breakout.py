"""
Breakout weighted by volatility regime
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class VolatilityWeightedBreakout(BaseStrategy):
    """
    VolatilityWeightedBreakout - Breakout weighted by volatility regime
    
    Category: breakout
    Indicators: atr, bollinger, adx
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize VolatilityWeightedBreakout strategy."""
        super().__init__(config)
        
        # OPTIMIZABLE PARAMETERS
        self.atr_period = self.config.get("atr_period", 14)
        self.atr_mult = self.config.get("atr_mult", 1.5)
        self.bb_period = self.config.get("bb_period", 20)
        self.adx_threshold = self.config.get("adx_threshold", 20)
        self.sl_atr_mult = self.config.get("sl_atr_mult", 2.0)
        self.tp_rr_mult = self.config.get("tp_rr_mult", 3.0)

    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        return ['atr', 'bollinger', 'adx']
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        Generate trading signals.
        
        Args:
            df: DataFrame with OHLCV and indicator data
            
        Returns:
            List of trading signals
        """
        signals, pos = [], None
        
        # ? Calculate ATR-based volatility threshold
        atr_mean = df["atr"].rolling(window=self.atr_period).mean()
        
        for i in range(max(self.atr_period, self.bb_period), len(df)):
            r = df.iloc[i]
            close, high, low = r["close"], r["high"], r["low"]
            adx = r.get("adx", 25)
            bb_u, bb_l = r.get("bb_upper", close), r.get("bb_lower", close)
            atr = r.get("atr", close*0.02)
            
            # ? USE atr_mult parameter for volatility regime detection
            is_high_volatility = atr > (atr_mean.iloc[i] * self.atr_mult)
            
            # ? Volatility-weighted confidence (higher confidence in high volatility)
            volatility_weight = min(1.0, atr / (atr_mean.iloc[i] + 1e-10))
            
            # ? USE adx_threshold parameter
            if pos is None and adx >= self.adx_threshold and is_high_volatility:
                # Use high/low for breakout detection
                if high > bb_u:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    # ? Weight confidence by volatility and ADX
                    confidence = min(1.0, (adx / 40) * volatility_weight)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, confidence, sl, tp, 
                                        {"adx": adx, "volatility_weight": volatility_weight}))
                    pos = "LONG"
                elif low < bb_l:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    confidence = min(1.0, (adx / 40) * volatility_weight)
                    signals.append(Signal(SignalType.SHORT, r["timestamp"], close, confidence, sl, tp, 
                                        {"adx": adx, "volatility_weight": volatility_weight}))
                    pos = "SHORT"
            
            # Exit on opposite breakout
            elif pos == "LONG" and low < bb_l:
                signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close,
                                    metadata={"reason": "Opposite breakout"}))
                pos = None
            
            elif pos == "SHORT" and high > bb_u:
                signals.append(Signal(SignalType.CLOSE_SHORT, r["timestamp"], close,
                                    metadata={"reason": "Opposite breakout"}))
                pos = None
                
        logger.info(f"VolatilityWeightedBreakout: {len(signals)} signals")
        return signals


__all__ = ["VolatilityWeightedBreakout"]
