"""
VWAP Breakout
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class VwapBreakout(BaseStrategy):
    """
    VwapBreakout - VWAP level breakout with volume confirmation
    
    Category: breakout
    Indicators: vwap, atr, rsi
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize VwapBreakout strategy."""
        super().__init__(config)
        
        # Strategy-specific parameters
        # TODO: Add configurable parameters from config.params
        
    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        return ['vwap', 'atr', 'rsi']
    
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
            close = r["close"]
            vwap = r.get("vwap", close)
            rsi, atr = r.get("rsi", 50), r.get("atr", close*0.02)
            if pos is None:
                # FIX: Relaxed VWAP breakout threshold from 1.002 to 1.001 (0.2% to 0.1%)
                # Use high for breakout detection
                if r["high"] > vwap * 1.001 and 45 < rsi < 75:  # Wider RSI range
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.7, sl, tp, {"vwap_dist": (close-vwap)/vwap}))
                    pos = "LONG"
                # Use low for breakdown
                elif r["low"] < vwap * 0.999 and 25 < rsi < 55:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(SignalType.SHORT, r["timestamp"], close, 0.7, sl, tp, {"vwap_dist": (close-vwap)/vwap}))
                    pos = "SHORT"
            elif pos == "LONG" and close < vwap:
                signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close, metadata={}))
                pos = None
            elif pos == "SHORT" and close > vwap:
                signals.append(Signal(SignalType.CLOSE_SHORT, r["timestamp"], close, metadata={}))
                pos = None
        logger.info(f"VwapBreakout: {len(signals)} signals")
        return signals


__all__ = ["VwapBreakout"]
