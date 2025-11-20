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
        
        # Strategy-specific parameters
        # TODO: Add configurable parameters from config.params
        
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
        for i in range(1, len(df)):
            r = df.iloc[i]
            close, atr = r["close"], r.get("atr", close*0.02)
            bb_u, bb_l = r.get("bb_upper", close), r.get("bb_lower", close)
            adx = r.get("adx", 0)
            if pos is None and adx >= 20:
                if close > bb_u:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, min(1.0, adx/40), sl, tp, {}))
                    pos = "LONG"
                elif close < bb_l:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(SignalType.SHORT, r["timestamp"], close, min(1.0, adx/40), sl, tp, {}))
                    pos = "SHORT"
        logger.info(f"VolatilityWeightedBreakout: {len(signals)} signals")
        return signals


__all__ = ["VolatilityWeightedBreakout"]
