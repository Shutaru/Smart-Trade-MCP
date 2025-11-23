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
        
        # OPTIMIZABLE PARAMETERS
        self.ema_fast = self.config.get("ema_fast", 8)
        self.ema_mid = self.config.get("ema_mid", 21)
        self.ema_slow = self.config.get("ema_slow", 55)
        self.rsi_threshold = self.config.get("rsi_threshold", 50)
        self.sl_atr_mult = self.config.get("sl_atr_mult", 2.0)
        self.tp_rr_mult = self.config.get("tp_rr_mult", 2.5)

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
            
            # ? USE ema_fast, ema_mid, ema_slow parameters
            ema_fast_val = r.get(f"ema_{self.ema_fast}", close)
            ema_mid_val = r.get(f"ema_{self.ema_mid}", close)
            ema_slow_val = r.get(f"ema_{self.ema_slow}", close)
            
            # Previous EMA values
            ema_fast_prev = p.get(f"ema_{self.ema_fast}", close)
            ema_mid_prev = p.get(f"ema_{self.ema_mid}", close)
            
            atr = r.get("atr", close*0.02)
            
            # EMA stack flip detection
            flip_bull = (
                ema_fast_prev <= ema_mid_prev and  # Was bearish/neutral
                ema_fast_val > ema_mid_val and      # Now bullish
                close > ema_slow_val                # Price above slow EMA (trend confirmation)
            )
            
            flip_bear = (
                ema_fast_prev >= ema_mid_prev and  # Was bullish/neutral
                ema_fast_val < ema_mid_val and      # Now bearish
                close < ema_slow_val                # Price below slow EMA (trend confirmation)
            )
            
            if pos is None:
                # LONG: EMA stack flips bullish (regime change to uptrend)
                if flip_bull:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(
                        SignalType.LONG, 
                        r["timestamp"], 
                        close, 
                        0.8, 
                        sl, 
                        tp, 
                        {
                            "ema_fast": self.ema_fast,
                            "ema_mid": self.ema_mid,
                            "ema_slow": self.ema_slow,
                            "reason": "EMA stack flip bullish"
                        }
                    ))
                    pos = "LONG"
                
                # SHORT: EMA stack flips bearish (regime change to downtrend)
                elif flip_bear:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(
                        SignalType.SHORT, 
                        r["timestamp"], 
                        close, 
                        0.8, 
                        sl, 
                        tp, 
                        {
                            "ema_fast": self.ema_fast,
                            "ema_mid": self.ema_mid,
                            "ema_slow": self.ema_slow,
                            "reason": "EMA stack flip bearish"
                        }
                    ))
                    pos = "SHORT"
            
            # Exit when EMA stack reverses
            elif pos == "LONG" and ema_fast_val < ema_mid_val:
                signals.append(Signal(
                    SignalType.CLOSE_LONG, 
                    r["timestamp"], 
                    close,
                    metadata={"reason": "EMA stack reversed"}
                ))
                pos = None
            
            elif pos == "SHORT" and ema_fast_val > ema_mid_val:
                signals.append(Signal(
                    SignalType.CLOSE_SHORT, 
                    r["timestamp"], 
                    close,
                    metadata={"reason": "EMA stack reversed"}
                ))
                pos = None
                
        logger.info(f"EmaStackRegimeFlip: {len(signals)} signals")
        return signals


__all__ = ["EmaStackRegimeFlip"]
