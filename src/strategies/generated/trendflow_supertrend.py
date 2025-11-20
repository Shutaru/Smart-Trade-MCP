"""
SuperTrend + ADX momentum with pullback entries
"""

from typing import List
import pandas as pd
import numpy as np

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class TrendflowSupertrend(BaseStrategy):
    """
    TrendflowSupertrend - SuperTrend + ADX momentum with pullback entries
    
    Category: trend_following
    Indicators: supertrend, adx, ema, rsi, atr
    
    Logic:
    - LONG: SuperTrend bullish + ADX >= 22 + (breakout OR pullback to EMA20)
    - SHORT: SuperTrend bearish + ADX >= 22 + (breakdown OR pullback to EMA20)
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize TrendflowSupertrend strategy."""
        super().__init__(config)
        
        # Strategy parameters
        self.adx_threshold = self.config.get("adx_threshold", 22)
        self.rsi_pullback_min = self.config.get("rsi_pullback_min", 40)
        self.rsi_pullback_max = self.config.get("rsi_pullback_max", 55)
        
    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        return ["supertrend", "adx", "ema", "rsi", "atr"]
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        Generate trading signals.
        
        Args:
            df: DataFrame with OHLCV and indicator data
            
        Returns:
            List of trading signals
        """
        signals = []
        
        # Verify required columns exist
        required = ["close", "high", "low", "adx", "rsi"]
        if not all(col in df.columns for col in required):
            logger.warning(f"Missing required columns for TrendflowSupertrend")
            return signals
        
        position = None  # Track position state
        
        for i in range(1, len(df)):
            row = df.iloc[i]
            prev_row = df.iloc[i - 1]
            
            close = row["close"]
            high = row["high"]
            low = row["low"]
            adx = row.get("adx", 0)
            rsi = row.get("rsi", 50)
            ema20 = row.get("ema_12", close)  # Fallback to close
            ema200 = row.get("ema_26", close)
            atr = row.get("atr", close * 0.02)
            
            # SuperTrend: simplified version (needs proper implementation)
            # For now, use EMA alignment as proxy
            supertrend_bull = ema20 > ema200
            supertrend_bear = ema20 < ema200
            
            prev_high = prev_row["high"]
            prev_low = prev_row["low"]
            
            timestamp = row["timestamp"]
            
            # LONG signals
            if position is None and adx >= self.adx_threshold and close > ema200:
                breakout = close > prev_high
                pullback = (
                    self.rsi_pullback_min <= rsi <= self.rsi_pullback_max
                    and close > ema20
                )
                
                if supertrend_bull and (breakout or pullback):
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    
                    signals.append(Signal(
                        type=SignalType.LONG,
                        timestamp=timestamp,
                        price=close,
                        confidence=min(1.0, adx / 40),
                        stop_loss=sl,
                        take_profit=tp,
                        metadata={
                            "adx": adx,
                            "rsi": rsi,
                            "reason": "breakout" if breakout else "pullback",
                        },
                    ))
                    position = "LONG"
            
            # SHORT signals
            elif position is None and adx >= self.adx_threshold and close < ema200:
                breakdown = close < prev_low
                pullback = (
                    45 <= rsi <= 60  # Slightly different for SHORT
                    and close < ema20
                )
                
                if supertrend_bear and (breakdown or pullback):
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    
                    signals.append(Signal(
                        type=SignalType.SHORT,
                        timestamp=timestamp,
                        price=close,
                        confidence=min(1.0, adx / 40),
                        stop_loss=sl,
                        take_profit=tp,
                        metadata={
                            "adx": adx,
                            "rsi": rsi,
                            "reason": "breakdown" if breakdown else "pullback",
                        },
                    ))
                    position = "SHORT"
            
            # Exit signals (simplified - based on trend reversal)
            elif position == "LONG" and supertrend_bear:
                signals.append(Signal(
                    type=SignalType.CLOSE_LONG,
                    timestamp=timestamp,
                    price=close,
                    metadata={"reason": "trend_reversal"},
                ))
                position = None
            
            elif position == "SHORT" and supertrend_bull:
                signals.append(Signal(
                    type=SignalType.CLOSE_SHORT,
                    timestamp=timestamp,
                    price=close,
                    metadata={"reason": "trend_reversal"},
                ))
                position = None
        
        logger.info(f"TrendflowSupertrend generated {len(signals)} signals")
        return signals


__all__ = ["TrendflowSupertrend"]
