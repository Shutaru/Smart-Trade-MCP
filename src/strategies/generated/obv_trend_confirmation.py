"""
OBV Trend Confirmation
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class ObvTrendConfirmation(BaseStrategy):
    """
    ObvTrendConfirmation - OBV trend confirms price trend
    
    Category: momentum
    Indicators: obv, ema, adx, atr
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize ObvTrendConfirmation strategy."""
        super().__init__(config)
        
        # OPTIMIZABLE PARAMETERS
        self.obv_ema_period = self.config.get("obv_ema_period", 20)
        self.price_ema_period = self.config.get("price_ema_period", 50)
        self.adx_threshold = self.config.get("adx_threshold", 25)
        self.sl_atr_mult = self.config.get("sl_atr_mult", 2.0)
        self.tp_rr_mult = self.config.get("tp_rr_mult", 2.5)

    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        return ["obv", "ema", "atr"]
    
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
        
        for i in range(max(10, self.obv_ema_period, self.price_ema_period), len(df)):
            r = df.iloc[i]
            close = r["close"]
            
            # Get OBV and its trend
            obv = r.get("obv", 0)
            obv_prev = df.iloc[i-1].get("obv", 0)
            obv_10ago = df.iloc[i-10].get("obv", 0)
            
            # ? USE price_ema_period parameter
            price_ema = r.get(f"ema_{self.price_ema_period}", close)
            atr = r.get("atr", close*0.02)
            
            # OBV trend detection
            obv_rising = obv > obv_prev and obv > obv_10ago
            obv_falling = obv < obv_prev and obv < obv_10ago
            
            # Price trend detection
            price_uptrend = close > price_ema
            price_downtrend = close < price_ema
            
            if pos is None:
                # LONG: Price uptrend + OBV rising (volume confirms trend)
                if price_uptrend and obv_rising:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(
                        SignalType.LONG, 
                        r["timestamp"], 
                        close, 
                        0.7, 
                        sl, 
                        tp, 
                        {
                            "obv": obv,
                            "obv_ema_period": self.obv_ema_period,
                            "price_ema_period": self.price_ema_period,
                            "reason": "OBV confirms uptrend"
                        }
                    ))
                    pos = "LONG"
                
                # SHORT: Price downtrend + OBV falling (volume confirms trend)
                elif price_downtrend and obv_falling:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(
                        SignalType.SHORT, 
                        r["timestamp"], 
                        close, 
                        0.7, 
                        sl, 
                        tp, 
                        {
                            "obv": obv,
                            "obv_ema_period": self.obv_ema_period,
                            "price_ema_period": self.price_ema_period,
                            "reason": "OBV confirms downtrend"
                        }
                    ))
                    pos = "SHORT"
            
            # Exit when OBV diverges from price or trend reverses
            elif pos == "LONG":
                obv_stopped = obv < obv_prev
                trend_reversed = close < price_ema
                
                if obv_stopped or trend_reversed:
                    signals.append(Signal(
                        SignalType.CLOSE_LONG, 
                        r["timestamp"], 
                        close,
                        metadata={"reason": "OBV divergence or trend reversed"}
                    ))
                    pos = None
            
            elif pos == "SHORT":
                obv_started_rising = obv > obv_prev and obv > df.iloc[i-5].get("obv", 0)
                trend_reversed = close > price_ema
                
                if obv_started_rising or trend_reversed:
                    signals.append(Signal(
                        SignalType.CLOSE_SHORT, 
                        r["timestamp"], 
                        close,
                        metadata={"reason": "OBV divergence or trend reversed"}
                    ))
                    pos = None
                    
        logger.info(f"ObvTrendConfirmation: {len(signals)} signals")
        return signals


__all__ = ["ObvTrendConfirmation"]
