"""
Trend Volume Combo
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class TrendVolumeCombo(BaseStrategy):
    """
    TrendVolumeCombo - Trend + Volume confirmation combo
    
    Category: momentum
    Indicators: ema, obv, atr
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize TrendVolumeCombo strategy."""
        super().__init__(config)
        
        # OPTIMIZABLE PARAMETERS
        self.ema_fast = self.config.get("ema_fast", 20)
        self.ema_slow = self.config.get("ema_slow", 50)
        self.obv_ema_period = self.config.get("obv_ema_period", 20)
        self.sl_atr_mult = self.config.get("sl_atr_mult", 2.0)
        self.tp_rr_mult = self.config.get("tp_rr_mult", 2.5)

    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        return ["ema", "obv", "atr"]
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        Generate trading signals.
        
        Args:
            df: DataFrame with OHLCV and indicator data
            
        Returns:
            List of trading signals
        """
        signals, pos = [], None
        
        # ? Calculate OBV EMA using parameter
        obv_ema = df["obv"].ewm(span=self.obv_ema_period, adjust=False).mean() if "obv" in df.columns else None
        
        for i in range(max(5, self.obv_ema_period), len(df)):
            r = df.iloc[i]
            prev = df.iloc[i - 1]
            
            close = r["close"]
            volume = r["volume"]
            obv = r.get("obv", 0)
            obv_prev = prev.get("obv", 0)
            atr = r.get("atr", close*0.02)
            
            # ? USE ema_fast and ema_slow parameters
            ema_fast_val = r.get(f"ema_{self.ema_fast}", close)
            ema_slow_val = r.get(f"ema_{self.ema_slow}", close)
            
            # Volume confirmation
            vol_avg = df["volume"].iloc[i-5:i].mean()
            high_vol = volume > vol_avg * 1.2
            
            # Trend confirmation
            bullish_trend = ema_fast_val > ema_slow_val
            bearish_trend = ema_fast_val < ema_slow_val
            
            # OBV trend confirmation
            obv_rising = obv > obv_prev
            obv_falling = obv < obv_prev
            
            # ? USE EMA parameters for trend + OBV for volume confirmation
            if pos is None and high_vol:
                # LONG: Bullish EMA + OBV rising + volume
                if bullish_trend and obv_rising:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(
                        SignalType.LONG, 
                        r["timestamp"], 
                        close, 
                        0.75, 
                        sl, 
                        tp, 
                        {
                            "vol_ratio": volume/vol_avg,
                            "ema_fast": self.ema_fast,
                            "ema_slow": self.ema_slow,
                            "obv_rising": obv_rising
                        }
                    ))
                    pos = "LONG"
                    
                # SHORT: Bearish EMA + OBV falling + volume
                elif bearish_trend and obv_falling:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(
                        SignalType.SHORT, 
                        r["timestamp"], 
                        close, 
                        0.75, 
                        sl, 
                        tp, 
                        {
                            "vol_ratio": volume/vol_avg,
                            "ema_fast": self.ema_fast,
                            "ema_slow": self.ema_slow,
                            "obv_falling": obv_falling
                        }
                    ))
                    pos = "SHORT"
            
            # Exit when trend or OBV reverses
            elif pos == "LONG" and (not bullish_trend or obv_falling):
                signals.append(Signal(
                    SignalType.CLOSE_LONG, 
                    r["timestamp"], 
                    close,
                    metadata={"reason": "Trend or OBV reversed"}
                ))
                pos = None
            
            elif pos == "SHORT" and (not bearish_trend or obv_rising):
                signals.append(Signal(
                    SignalType.CLOSE_SHORT, 
                    r["timestamp"], 
                    close,
                    metadata={"reason": "Trend or OBV reversed"}
                ))
                pos = None
                
        logger.info(f"TrendVolumeCombo: {len(signals)} signals")
        return signals


__all__ = ["TrendVolumeCombo"]
