"""EMA200 Tap Reversion"""
from typing import List
import pandas as pd
from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class Ema200TapReversion(BaseStrategy):
    """
    Ema200TapReversion - Price taps EMA200 in trending market then bounces
    
    Category: mean_reversion
    Indicators: ema, rsi, atr
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize Ema200TapReversion strategy."""
        super().__init__(config)
        
        # OPTIMIZABLE PARAMETERS
        self.ema_period = self.config.get("ema_period", 200)
        self.tap_threshold_pct = self.config.get("tap_threshold_pct", 0.5)
        self.rsi_filter = self.config.get("rsi_filter", 50)
        self.sl_atr_mult = self.config.get("sl_atr_mult", 2.0)
        self.tp_rr_mult = self.config.get("tp_rr_mult", 2.0)

    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        return ["ema", "rsi", "atr"]
    
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
            prev = df.iloc[i-1]
            close = r["close"]
            low = r["low"]
            high = r["high"]
            
            # ? USE ema_period parameter
            ema_trend = r.get(f"ema_{self.ema_period}", close)
            rsi = r.get("rsi", 50)
            atr = r.get("atr", close*0.02)
            
            # ? USE tap_threshold_pct parameter for tap detection
            tap_distance = (self.tap_threshold_pct / 100) * ema_trend
            
            # LONG: Price taps EMA from above (pullback in uptrend)
            taps_ema_from_above = (
                close > ema_trend and  # Currently above EMA (uptrend)
                low <= ema_trend + tap_distance  # Low touched/near EMA
            )
            
            # SHORT: Price taps EMA from below (pullback in downtrend)
            taps_ema_from_below = (
                close < ema_trend and  # Currently below EMA (downtrend)
                high >= ema_trend - tap_distance  # High touched/near EMA
            )
            
            # ? USE rsi_filter parameter for RSI range
            rsi_neutral_low = self.rsi_filter - 10
            rsi_neutral_high = self.rsi_filter + 15
            
            if pos is None:
                # LONG: Uptrend + EMA tap + RSI not overbought
                if taps_ema_from_above and rsi_neutral_low < rsi < rsi_neutral_high:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(
                        SignalType.LONG, 
                        r["timestamp"], 
                        close, 
                        0.8, 
                        sl, 
                        tp, 
                        {
                            "ema_period": self.ema_period,
                            "tap_threshold_pct": self.tap_threshold_pct,
                            "distance_from_ema": abs(low - ema_trend),
                            "reason": f"EMA{self.ema_period} tap in uptrend"
                        }
                    ))
                    pos = "LONG"
                
                # SHORT: Downtrend + EMA tap + RSI not oversold
                elif taps_ema_from_below and rsi_neutral_low < rsi < rsi_neutral_high:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(
                        SignalType.SHORT, 
                        r["timestamp"], 
                        close, 
                        0.8, 
                        sl, 
                        tp, 
                        {
                            "ema_period": self.ema_period,
                            "tap_threshold_pct": self.tap_threshold_pct,
                            "distance_from_ema": abs(high - ema_trend),
                            "reason": f"EMA{self.ema_period} tap in downtrend"
                        }
                    ))
                    pos = "SHORT"
            
            # Exit when price crosses back through EMA (trend change)
            elif pos == "LONG" and close < ema_trend:
                signals.append(Signal(
                    SignalType.CLOSE_LONG, 
                    r["timestamp"], 
                    close,
                    metadata={"reason": f"Price crossed below EMA{self.ema_period}"}
                ))
                pos = None
            
            elif pos == "SHORT" and close > ema_trend:
                signals.append(Signal(
                    SignalType.CLOSE_SHORT, 
                    r["timestamp"], 
                    close,
                    metadata={"reason": f"Price crossed above EMA{self.ema_period}"}
                ))
                pos = None
                
        logger.info(f"Ema200TapReversion: {len(signals)} signals")
        return signals


__all__ = ["Ema200TapReversion"]
