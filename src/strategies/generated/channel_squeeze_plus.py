"""
Multi-channel squeeze breakout system
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class ChannelSqueezePlus(BaseStrategy):
    """
    ChannelSqueezePlus - Multi-channel squeeze breakout system
    
    Category: breakout
    Indicators: bollinger, keltner, atr
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize ChannelSqueezePlus strategy."""
        super().__init__(config)
        self.config.stop_loss_atr_mult = 2.0
        
    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        return ['bollinger', 'keltner', 'atr']
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        Generate trading signals.
        
        Args:
            df: DataFrame with OHLCV and indicator data
            
        Returns:
            List of trading signals
        """
        signals, pos = [], None
        for i in range(10, len(df)):
            r = df.iloc[i]
            close = r["close"]
            atr = r.get("atr", close*0.02)
            bb_u, bb_l = r.get("bb_upper", close), r.get("bb_lower", close)
            kc_u, kc_l = r.get("keltner_upper", close), r.get("keltner_lower", close)
            # Squeeze: BB inside Keltner
            squeeze = bb_u < kc_u and bb_l > kc_l
            squeeze_prev = df.iloc[i-1].get("bb_upper", close) < df.iloc[i-1].get("keltner_upper", close)
            just_released = squeeze_prev and not squeeze
            
            if pos is None and just_released:
                if close > bb_u:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.85, sl, tp, {}))
                    pos = "LONG"
                elif close < bb_l:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(SignalType.SHORT, r["timestamp"], close, 0.85, sl, tp, {}))
                    pos = "SHORT"
        logger.info(f"ChannelSqueezePlus: {len(signals)} signals")
        return signals


__all__ = ["ChannelSqueezePlus"]
