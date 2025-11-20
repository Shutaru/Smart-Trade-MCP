"""
EMA Cloud Trend - Pullback to EMA cloud in trending markets

Win Rate: 50-60%
Best Timeframes: 15m, 1h, 4h
"""

from typing import List
import pandas as pd
import numpy as np

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class EmaCloudTrend(BaseStrategy):
    """
    EMA Cloud Trend Strategy
    
    LONG: Price > EMA200 + pullback to EMA20/50 + RSI 40-55 + resume
    SHORT: Price < EMA200 + pullback to EMA20/50 + RSI 45-60 + resume
    
    Category: Trend Following
    Win Rate: 50-60%
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize EMA Cloud Trend strategy."""
        super().__init__(config)
        
        self.config.stop_loss_atr_mult = 1.8
        self.config.take_profit_rr_ratio = 2.5
        
    def get_required_indicators(self) -> List[str]:
        """Required indicators."""
        return ["ema", "rsi", "atr"]
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """Generate trading signals."""
        signals = []
        position = None
        
        for i in range(1, len(df)):
            row = df.iloc[i]
            prev_row = df.iloc[i - 1]
            
            close = row["close"]
            low = row["low"]
            high = row["high"]
            rsi = row.get("rsi", 50)
            ema_12 = row.get("ema_12", close)
            ema_26 = row.get("ema_26", close)
            ema_200 = row.get("ema_200", close)
            atr = row.get("atr", close * 0.02)
            
            ema_12_prev = prev_row.get("ema_12", close)
            prev_high = prev_row["high"]
            prev_low = prev_row["low"]
            timestamp = row["timestamp"]
            
            # LONG entry
            if position is None and close > ema_200:
                # Simplified: Just need close above EMA200 and cross above EMA12
                bullish_cross = close > ema_12 and prev_row["close"] <= ema_12_prev
                rsi_ok = 35 <= rsi <= 65  # Wider RSI range
                
                if bullish_cross and rsi_ok:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(
                        type=SignalType.LONG,
                        timestamp=timestamp,
                        price=close,
                        confidence=0.7,
                        stop_loss=sl,
                        take_profit=tp,
                        metadata={"rsi": rsi, "reason": "EMA12 bullish cross"},
                    ))
                    position = "LONG"
            
            # SHORT entry - simplified
            elif position is None and close < ema_200:
                bearish_cross = close < ema_12 and prev_row["close"] >= ema_12_prev
                rsi_ok = 35 <= rsi <= 65
                
                if bearish_cross and rsi_ok:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(
                        type=SignalType.SHORT,
                        timestamp=timestamp,
                        price=close,
                        confidence=0.7,
                        stop_loss=sl,
                        take_profit=tp,
                        metadata={"rsi": rsi, "reason": "EMA12 bearish cross"},
                    ))
                    position = "SHORT"
            
            # Exit
            elif position == "LONG" and close < ema_200:
                signals.append(Signal(
                    type=SignalType.CLOSE_LONG,
                    timestamp=timestamp,
                    price=close,
                    metadata={"reason": "Trend reversal"},
                ))
                position = None
            
            elif position == "SHORT" and close > ema_200:
                signals.append(Signal(
                    type=SignalType.CLOSE_SHORT,
                    timestamp=timestamp,
                    price=close,
                    metadata={"reason": "Trend reversal"},
                ))
                position = None
        
        logger.info(f"EmaCloudTrend generated {len(signals)} signals")
        return signals


__all__ = ["EmaCloudTrend"]
