"""
London Breakout ATR
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class LondonBreakoutAtr(BaseStrategy):
    """
    LondonBreakoutAtr - London session breakout with ATR filter
    
    Category: breakout
    Indicators: atr, ema
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize LondonBreakoutAtr strategy."""
        super().__init__(config)
        
        # OPTIMIZABLE PARAMETERS
        self.atr_period = self.config.get("atr_period", 14)
        self.atr_mult = self.config.get("atr_mult", 1.5)
        self.ema_period = self.config.get("ema_period", 20)
        self.london_start_hour = self.config.get("london_start_hour", 8)
        self.london_end_hour = self.config.get("london_end_hour", 12)
        self.sl_atr_mult = self.config.get("sl_atr_mult", 2.0)
        self.tp_rr_mult = self.config.get("tp_rr_mult", 3.0)

    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        return ["atr", "ema"]
    
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
            close, high, low = r["close"], r["high"], r["low"]
            atr = r.get("atr", close*0.02)
            
            # FIX: Relaxed ATR threshold from 1.5% to 1.0%
            # Note: Removed time-based filter since crypto trades 24/7
            if pos is None and atr > close * 0.010:  # Relaxed from 0.015
                prev_high, prev_low = df.iloc[i-1]["high"], df.iloc[i-1]["low"]
                
                # FIX: Use high/low for breakout detection
                if high > prev_high:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.7, sl, tp, 
                                        {"atr_pct": atr/close}))
                    pos = "LONG"
                elif low < prev_low:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(SignalType.SHORT, r["timestamp"], close, 0.7, sl, tp, 
                                        {"atr_pct": atr/close}))
                    pos = "SHORT"
            
            # FIX: ADD EXIT LOGIC - exit on opposite breakout
            elif pos == "LONG":
                curr_low = df.iloc[i]["low"]
                prev_low = df.iloc[i-1]["low"]
                if curr_low < prev_low:
                    signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close,
                                        metadata={"reason": "Opposite breakout"}))
                    pos = None
            
            elif pos == "SHORT":
                curr_high = df.iloc[i]["high"]
                prev_high = df.iloc[i-1]["high"]
                if curr_high > prev_high:
                    signals.append(Signal(SignalType.CLOSE_SHORT, r["timestamp"], close,
                                        metadata={"reason": "Opposite breakout"}))
                    pos = None
        logger.info(f"LondonBreakoutAtr: {len(signals)} signals")
        return signals


__all__ = ["LondonBreakoutAtr"]
