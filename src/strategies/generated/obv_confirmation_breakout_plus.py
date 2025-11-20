"""
OBV Confirmation Breakout Plus
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class ObvConfirmationBreakoutPlus(BaseStrategy):
    """
    ObvConfirmationBreakoutPlus - OBV confirms price breakout with volume
    
    Category: momentum
    Indicators: obv, ema, atr
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize ObvConfirmationBreakoutPlus strategy."""
        super().__init__(config)
        
        # Strategy-specific parameters
        # TODO: Add configurable parameters from config.params
        
    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        return ['obv', 'bollinger', 'atr']
    
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
            close = r["close"]
            bb_u, obv, atr = r.get("bb_upper", close), r.get("obv", 0), r.get("atr", close*0.02)
            obv_rising = obv > df.iloc[i-5].get("obv", 0)
            if pos is None and close > bb_u and obv_rising:
                sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.8, sl, tp, {}))
                pos = "LONG"
                
        logger.info(f"ObvConfirmationBreakoutPlus: {len(signals)} signals")
        return signals


__all__ = ["ObvConfirmationBreakoutPlus"]
