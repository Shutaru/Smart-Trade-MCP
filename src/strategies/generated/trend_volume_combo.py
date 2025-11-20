"""
Trend Volume Combo
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class TrendVolumeCombo(BaseStrategy):
    """
    TrendVolumeCombo - Trend + Volume confirmation combo
    
    Category: momentum
    Indicators: ema, obv, atr
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize TrendVolumeCombo strategy."""
        super().__init__(config)
        
        # Strategy-specific parameters
        # TODO: Add configurable parameters from config.params
        
    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        return ["ema", "obv", "atr"]
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        Generate trading signals.
        
        Args:
            df: DataFrame with OHLCV and indicator data
            
        Returns:
            List of trading signals
        """
        signals, pos = [], None
        for i in range(5, len(df)):
            r = df.iloc[i]
            close, volume = r["close"], r["volume"]
            ema200, obv = r.get("ema_200", close), r.get("obv", 0)
            atr = r.get("atr", close*0.02)
            vol_avg = df["volume"].iloc[i-5:i].mean()
            high_vol = volume > vol_avg * 1.5
            if pos is None and high_vol:
                if close > ema200 and obv > df.iloc[i-1].get("obv", 0):
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.75, sl, tp, {}))
                    pos = "LONG"
                elif close < ema200 and obv < df.iloc[i-1].get("obv", 0):
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(SignalType.SHORT, r["timestamp"], close, 0.75, sl, tp, {}))
                    pos = "SHORT"
        logger.info(f"TrendVolumeCombo: {len(signals)} signals")
        return signals


__all__ = ["TrendVolumeCombo"]
