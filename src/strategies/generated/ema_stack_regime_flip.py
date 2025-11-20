"""
EMA Stack Regime Flip
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class EmaStackRegimeFlip(BaseStrategy):
    """
    EmaStackRegimeFlip - EMA stack flips indicate regime change
    
    Category: momentum
    Indicators: ema, rsi, atr
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize EmaStackRegimeFlip strategy."""
        super().__init__(config)
        
        # Strategy-specific parameters
        # TODO: Add configurable parameters from config.params
        
    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        return ['ema', 'atr']
    
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
            r, p = df.iloc[i], df.iloc[i-1]
            close = r["close"]
            ema12, ema26, ema200 = r.get("ema_12", close), r.get("ema_26", close), r.get("ema_200", close)
            e12p, e26p = p.get("ema_12", close), p.get("ema_26", close)
            atr = r.get("atr", close*0.02)
            flip_bull = e12p <= e26p and ema12 > ema26 and close > ema200
            flip_bear = e12p >= e26p and ema12 < ema26 and close < ema200
            
            if pos is None:
                if flip_bull:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.8, sl, tp, {}))
                    pos = "LONG"
                elif flip_bear:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(SignalType.SHORT, r["timestamp"], close, 0.8, sl, tp, {}))
                    pos = "SHORT"
            
            # FIX: ADD EXIT LOGIC - exit when EMA stack reverses
            elif pos == "LONG" and ema12 < ema26:
                signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close,
                                    metadata={"reason": "EMA stack reversed"}))
                pos = None
            
            elif pos == "SHORT" and ema12 > ema26:
                signals.append(Signal(SignalType.CLOSE_SHORT, r["timestamp"], close,
                                    metadata={"reason": "EMA stack reversed"}))
                pos = None
        logger.info(f"EmaStackRegimeFlip: {len(signals)} signals")
        return signals


__all__ = ["EmaStackRegimeFlip"]
