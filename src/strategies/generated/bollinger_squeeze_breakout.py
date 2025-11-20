"""
Bollinger Squeeze Breakout - BB squeeze + explosive breakout
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class BollingerSqueezeBreakout(BaseStrategy):
    """Bollinger Band squeeze -> expansion breakout (Win: 45-52%)"""
    
    def __init__(self, config: StrategyConfig = None):
        super().__init__(config)
        self.config.stop_loss_atr_mult = 2.0
        self.config.take_profit_rr_ratio = 2.2
        
    def get_required_indicators(self) -> List[str]:
        return ["bollinger", "atr", "rsi"]
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals, pos = [], None
        for i in range(20, len(df)):  # Need history for bandwidth
            r, p = df.iloc[i], df.iloc[i-1]
            close, high, low = r["close"], r["high"], r["low"]
            bb_u, bb_l, bb_m = r.get("bb_upper", close), r.get("bb_lower", close), r.get("bb_middle", close)
            rsi, atr = r.get("rsi", 50), r.get("atr", close*0.02)
            
            # Squeeze detection: BB bandwidth narrow
            bw = (bb_u - bb_l) / bb_m if bb_m > 0 else 0
            bw_prev = (p.get("bb_upper", close) - p.get("bb_lower", close)) / p.get("bb_middle", close) if p.get("bb_middle", close) > 0 else 0
            
            # FIX: Better squeeze detection - need sustained narrow bandwidth
            avg_bw_20 = sum((df.iloc[j].get("bb_upper", close) - df.iloc[j].get("bb_lower", close)) / df.iloc[j].get("bb_middle", close) 
                           for j in range(i-20, i)) / 20 if i >= 20 else bw
            is_squeezed = bw < 0.015 and bw < avg_bw_20 * 0.7  # Narrow AND contracting
            is_expanding = bw > bw_prev * 1.1  # Expanding now
            
            if pos is None and is_squeezed and is_expanding:
                # FIX: Use HIGH for breakout (not close)
                # LONG: breakout above BB upper with momentum
                if high > bb_u and rsi > 50 and rsi < 80:  # Need upward momentum
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.8, sl, tp, 
                                        {"bw": bw, "reason": "BB squeeze breakout"}))
                    pos = "LONG"
                # FIX: Use LOW for breakdown (not close)  
                # SHORT: breakdown below BB lower with momentum
                elif low < bb_l and rsi < 50 and rsi > 20:  # Need downward momentum
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(SignalType.SHORT, r["timestamp"], close, 0.8, sl, tp, 
                                        {"bw": bw, "reason": "BB squeeze breakdown"}))
                    pos = "SHORT"
            
            # FIX: Exit on trend reversal (not mean reversion!)
            # For breakouts, we want to ride the trend, not exit at middle
            elif pos == "LONG" and close < bb_l:  # Trend reversed (was above, now below)
                signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close, 
                                    metadata={"reason": "Trend reversal"}))
                pos = None
            elif pos == "SHORT" and close > bb_u:  # Trend reversed (was below, now above)
                signals.append(Signal(SignalType.CLOSE_SHORT, r["timestamp"], close, 
                                    metadata={"reason": "Trend reversal"}))
                pos = None
                
        logger.info(f"BollingerSqueezeBreakout: {len(signals)} signals")
        return signals


__all__ = ["BollingerSqueezeBreakout"]
