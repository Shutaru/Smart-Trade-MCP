"""
ATR Expansion Breakout
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class AtrExpansionBreakout(BaseStrategy):
    """
    AtrExpansionBreakout - ATR expansion signals volatility breakout
    
    Category: breakout
    Indicators: atr, ema, rsi, supertrend, adx
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize AtrExpansionBreakout strategy."""
        super().__init__(config)
        
        # OPTIMIZABLE PARAMETERS
        self.atr_period = self.config.get("atr_period", 14)
        self.atr_multiplier = self.config.get("atr_multiplier", 1.25)
        self.stop_loss_atr_mult = self.config.get("stop_loss_atr_mult", 2.2)
        self.take_profit_rr_ratio = self.config.get("take_profit_rr_ratio", 2.4)

    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        return ["atr", "ema", "supertrend", "adx"]
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        Generate trading signals.
        
        Args:
            df: DataFrame with OHLCV and indicator data
            
        Returns:
            List of trading signals
        """
        signals, pos = [], None
        
        # Calculate dynamic ATR threshold from parameter
        atr_mean = df["atr"].rolling(window=self.atr_period).mean()
        atr_expansion_threshold = atr_mean * self.atr_multiplier
        
        for i in range(self.atr_period, len(df)):
            r = df.iloc[i]
            close = r["close"]
            atr = r.get("atr", close * 0.02)
            
            # USE atr_expansion_threshold from parameter
            is_expanding = atr > atr_expansion_threshold.iloc[i]
            
            # Get SuperTrend and EMA for trend confirmation
            st_trend = r.get("supertrend_trend", 0)
            adx = r.get("adx", 25)
            
            if pos is None:
                # USE adx parameter if available (from metadata, default 20)
                min_adx = 20  # Could add as parameter if needed
                
                # LONG: ATR expansion + bullish SuperTrend + strong trend
                if is_expanding and st_trend == 1 and adx > min_adx:
                    # USE sl/tp parameters
                    sl = close - (atr * self.stop_loss_atr_mult)
                    tp = close + (atr * self.stop_loss_atr_mult * self.take_profit_rr_ratio)
                    
                    signals.append(Signal(
                        SignalType.LONG, 
                        r["timestamp"], 
                        close, 
                        0.8, 
                        sl, 
                        tp,
                        {"atr": atr, "adx": adx, "reason": "ATR expansion breakout"}
                    ))
                    pos = "LONG"
                
                # SHORT: ATR expansion + bearish SuperTrend + strong trend
                elif is_expanding and st_trend == -1 and adx > min_adx:
                    # USE sl/tp parameters
                    sl = close + (atr * self.stop_loss_atr_mult)
                    tp = close - (atr * self.stop_loss_atr_mult * self.take_profit_rr_ratio)
                    
                    signals.append(Signal(
                        SignalType.SHORT, 
                        r["timestamp"], 
                        close, 
                        0.8, 
                        sl, 
                        tp,
                        {"atr": atr, "adx": adx, "reason": "ATR expansion breakdown"}
                    ))
                    pos = "SHORT"
            
            # Exit on SuperTrend flip
            elif pos == "LONG" and st_trend == -1:
                signals.append(Signal(
                    SignalType.CLOSE_LONG, 
                    r["timestamp"], 
                    close,
                    metadata={"reason": "SuperTrend flip"}
                ))
                pos = None
            elif pos == "SHORT" and st_trend == 1:
                signals.append(Signal(
                    SignalType.CLOSE_SHORT, 
                    r["timestamp"], 
                    close,
                    metadata={"reason": "SuperTrend flip"}
                ))
                pos = None
        
        logger.info(f"AtrExpansionBreakout: {len(signals)} signals")
        return signals


__all__ = ["AtrExpansionBreakout"]
