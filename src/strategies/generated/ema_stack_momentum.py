"""
EMA stack alignment with strong momentum
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class EmaStackMomentum(BaseStrategy):
    """
    EmaStackMomentum - EMA stack alignment with strong momentum
    
    Category: momentum
    Indicators: ema, rsi, macd, atr
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize EmaStackMomentum strategy."""
        super().__init__(config)
        
        # Strategy-specific parameters
        # TODO: Add configurable parameters from config.params
        
    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        return ['ema', 'rsi', 'macd', 'atr']
    
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
            ema12, ema26, ema200 = r.get("ema_12", close), r.get("ema_26", close), r.get("ema_200", close)
            rsi, macd_hist = r.get("rsi", 50), r.get("macd_hist", 0)
            atr = r.get("atr", close*0.02)
            # EMA stack aligned
            stack_bull = ema12 > ema26 > ema200
            stack_bear = ema12 < ema26 < ema200
            if pos is None:
                if stack_bull and macd_hist > 0 and 40 < rsi < 70:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.8, sl, tp, {}))
                    pos = "LONG"
                elif stack_bear and macd_hist < 0 and 30 < rsi < 60:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(SignalType.SHORT, r["timestamp"], close, 0.8, sl, tp, {}))
                    pos = "SHORT"
            elif pos == "LONG" and (not stack_bull or macd_hist < 0):
                signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close, metadata={}))
                pos = None
            elif pos == "SHORT" and (not stack_bear or macd_hist > 0):
                signals.append(Signal(SignalType.CLOSE_SHORT, r["timestamp"], close, metadata={}))
                pos = None
        logger.info(f"EmaStackMomentum: {len(signals)} signals")
        return signals


__all__ = ["EmaStackMomentum"]
