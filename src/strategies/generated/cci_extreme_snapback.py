"""
CCI Extreme Snapback - CCI crosses back from extreme with EMA confirmation
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class CciExtremeSnapback(BaseStrategy):
    """CCI extreme reversal with EMA touch"""
    
    def __init__(self, config: StrategyConfig = None):
        super().__init__(config)
        self.config.stop_loss_atr_mult = 1.6
        self.config.take_profit_rr_ratio = 1.8
        
    def get_required_indicators(self) -> List[str]:
        return ["cci", "ema", "atr"]
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals, pos = [], None
        for i in range(1, len(df)):
            r, p = df.iloc[i], df.iloc[i-1]
            close, low, high = r["close"], r["low"], r["high"]
            cci, cci_prev = r.get("cci", 0), p.get("cci", 0)
            ema_12, ema_26 = r.get("ema_12", close), r.get("ema_26", close)
            atr = r.get("atr", close*0.02)
            
            if pos is None:
                # LONG: CCI crosses back above -150 from extreme + touched EMA
                # FIX: Changed from -100 to -150 for more extreme reversions
                cci_extreme = cci_prev < -150  # More extreme threshold
                cci_cross_back = cci >= -150
                touched_ema = low <= ema_12 or low <= ema_26
                
                if cci_extreme and cci_cross_back and touched_ema:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, min(1.0, abs(cci_prev)/200), sl, tp,
                                        {"cci": cci, "cci_prev": cci_prev, "reason": "CCI extreme snapback"}))
                    pos = "LONG"
                
                # SHORT: CCI crosses back below +150 from extreme
                # FIX: Changed from +100 to +150 for more extreme reversions
                cci_extreme_high = cci_prev > 150  # More extreme threshold
                cci_cross_down = cci <= 150
                touched_ema_high = high >= ema_12 or high >= ema_26
                
                if cci_extreme_high and cci_cross_down and touched_ema_high:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(SignalType.SHORT, r["timestamp"], close, min(1.0, abs(cci_prev)/200), sl, tp,
                                        {"cci": cci, "cci_prev": cci_prev, "reason": "CCI extreme snapback"}))
                    pos = "SHORT"
            
            # Exit when CCI crosses zero
            elif pos == "LONG" and cci > 0:
                signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close, metadata={"reason": "CCI crossed zero"}))
                pos = None
            elif pos == "SHORT" and cci < 0:
                signals.append(Signal(SignalType.CLOSE_SHORT, r["timestamp"], close, metadata={"reason": "CCI crossed zero"}))
                pos = None
                
        logger.info(f"CciExtremeSnapback: {len(signals)} signals")
        return signals


__all__ = ["CciExtremeSnapback"]
