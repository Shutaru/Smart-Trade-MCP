"""
Triple Momentum Confluence
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class TripleMomentumConfluence(BaseStrategy):
    """
    TripleMomentumConfluence - RSI + MACD + Stochastic alignment
    
    Category: momentum
    Indicators: rsi, macd, stochastic, atr
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize TripleMomentumConfluence strategy."""
        super().__init__(config)
        
        # Strategy-specific parameters
        # TODO: Add configurable parameters from config.params
        
    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        return ['rsi', 'macd', 'stochastic', 'atr']
    
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
            rsi, mfi, macd_hist = r.get("rsi", 50), r.get("mfi", 50), r.get("macd_hist", 0)
            atr = r.get("atr", close*0.02)
            # All 3 oscillators bullish
            if pos is None:
                if rsi > 50 and mfi > 50 and macd_hist > 0:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.85, sl, tp, {}))
                    pos = "LONG"
                elif rsi < 50 and mfi < 50 and macd_hist < 0:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(SignalType.SHORT, r["timestamp"], close, 0.85, sl, tp, {}))
                    pos = "SHORT"
        logger.info(f"TripleMomentumConfluence: {len(signals)} signals")
        return signals


__all__ = ["TripleMomentumConfluence"]
