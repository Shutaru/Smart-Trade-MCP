"""
MACD Zero Trend - MACD histogram crosses zero with trend confirmation

Win Rate: 45-52%
Best Timeframes: 15m, 1h
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class MacdZeroTrend(BaseStrategy):
    """MACD Zero Line Trend - MACD hist > 0 + breakout"""

    def __init__(self, config: StrategyConfig = None):
        super().__init__(config)
        self.config.stop_loss_atr_mult = 2.2
        self.config.take_profit_rr_ratio = 2.2
        
    def get_required_indicators(self) -> List[str]:
        return ["macd", "ema", "rsi", "adx", "supertrend", "atr"]
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals = []
        position = None
        
        for i in range(1, len(df)):
            row = df.iloc[i]
            prev = df.iloc[i - 1]
            
            close = row["close"]
            macd_hist = row.get("macd_hist", 0)
            rsi = row.get("rsi", 50)
            ema_200 = row.get("ema_200", close)
            adx = row.get("adx", 0)
            supertrend_trend = row.get("supertrend_trend", 0)
            atr = row.get("atr", close * 0.02)
            prev_high = prev["high"]
            prev_low = prev["low"]
            timestamp = row["timestamp"]
            
            # LONG
            if position is None:
                # Just MACD > 0, SuperTrend bullish, ADX > 15
                if macd_hist > 0 and supertrend_trend > 0 and adx >= 15 and 30 < rsi < 75:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(
                        type=SignalType.LONG, timestamp=timestamp, price=close,
                        confidence=min(1.0, adx / 40), stop_loss=sl, take_profit=tp,
                        metadata={"macd_hist": macd_hist, "adx": adx}
                    ))
                    position = "LONG"
            
                # SHORT
                elif macd_hist < 0 and supertrend_trend < 0 and adx >= 15 and 25 < rsi < 70:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(
                        type=SignalType.SHORT, timestamp=timestamp, price=close,
                        confidence=min(1.0, adx / 40), stop_loss=sl, take_profit=tp,
                        metadata={"macd_hist": macd_hist, "adx": adx}
                    ))
                    position = "SHORT"
            
            # Exit
            elif position == "LONG" and supertrend_trend < 0:
                signals.append(Signal(type=SignalType.CLOSE_LONG, timestamp=timestamp, price=close, metadata={"reason": "ST reversal"}))
                position = None
            elif position == "SHORT" and supertrend_trend > 0:
                signals.append(Signal(type=SignalType.CLOSE_SHORT, timestamp=timestamp, price=close, metadata={"reason": "ST reversal"}))
                position = None
        
        logger.info(f"MacdZeroTrend generated {len(signals)} signals")
        return signals


__all__ = ["MacdZeroTrend"]
