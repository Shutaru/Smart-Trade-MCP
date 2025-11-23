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
        
        # OPTIMIZABLE PARAMETERS
        self.obv_ema_period = self.config.get("obv_ema_period", 20)
        self.price_ema_period = self.config.get("price_ema_period", 50)
        self.breakout_threshold = self.config.get("breakout_threshold", 1.5)
        self.sl_atr_mult = self.config.get("sl_atr_mult", 2.0)
        self.tp_rr_mult = self.config.get("tp_rr_mult", 2.5)

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
        
        # ? Calculate OBV EMA using parameter
        obv_ema = df["obv"].ewm(span=self.obv_ema_period, adjust=False).mean() if "obv" in df.columns else None
        
        for i in range(max(5, self.obv_ema_period, self.price_ema_period), len(df)):
            r = df.iloc[i]
            close, high, low = r["close"], r["high"], r["low"]
            
            # Get indicators
            bb_u = r.get("bb_upper", close)
            bb_l = r.get("bb_lower", close)
            obv = r.get("obv", 0)
            # ? USE price_ema_period parameter
            price_ema = r.get(f"ema_{self.price_ema_period}", close)
            atr = r.get("atr", close*0.02)
            
            # OBV surge detection
            obv_5ago = df.iloc[i-5].get("obv", 0)
            obv_rising = obv > obv_5ago
            obv_falling = obv < obv_5ago
            
            # ? USE breakout_threshold parameter
            breakout_strength = (close - price_ema) / price_ema if price_ema > 0 else 0
            
            if pos is None:
                # LONG: BB upper breakout + OBV rising + strong breakout
                if (high > bb_u and 
                    obv_rising and 
                    abs(breakout_strength) > self.breakout_threshold / 100):
                    
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(
                        SignalType.LONG, 
                        r["timestamp"], 
                        close, 
                        0.8, 
                        sl, 
                        tp, 
                        {
                            "obv": obv,
                            "breakout_strength": breakout_strength * 100,
                            "breakout_threshold": self.breakout_threshold,
                            "reason": "OBV confirms breakout"
                        }
                    ))
                    pos = "LONG"
                
                # SHORT: BB lower breakdown + OBV falling + strong breakdown
                elif (low < bb_l and 
                      obv_falling and 
                      abs(breakout_strength) > self.breakout_threshold / 100):
                    
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(
                        SignalType.SHORT, 
                        r["timestamp"], 
                        close, 
                        0.8, 
                        sl, 
                        tp, 
                        {
                            "obv": obv,
                            "breakout_strength": breakout_strength * 100,
                            "breakout_threshold": self.breakout_threshold,
                            "reason": "OBV confirms breakdown"
                        }
                    ))
                    pos = "SHORT"
            
            # Exit when OBV reverses or price returns to EMA
            elif pos == "LONG":
                obv_stopped = obv < df.iloc[i-1].get("obv", 0)
                price_returned = close < price_ema
                
                if obv_stopped or price_returned:
                    signals.append(Signal(
                        SignalType.CLOSE_LONG, 
                        r["timestamp"], 
                        close,
                        metadata={"reason": "OBV reversed or price returned to EMA"}
                    ))
                    pos = None
            
            elif pos == "SHORT":
                obv_started = obv > df.iloc[i-1].get("obv", 0)
                price_returned = close > price_ema
                
                if obv_started or price_returned:
                    signals.append(Signal(
                        SignalType.CLOSE_SHORT, 
                        r["timestamp"], 
                        close,
                        metadata={"reason": "OBV reversed or price returned to EMA"}
                    ))
                    pos = None
                
        logger.info(f"ObvConfirmationBreakoutPlus: {len(signals)} signals")
        return signals


__all__ = ["ObvConfirmationBreakoutPlus"]
