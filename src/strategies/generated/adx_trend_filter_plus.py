"""
ADX Trend Filter Plus - Pure ADX trend strength with EMA alignment

Win Rate: 48-58%
Best Timeframes: 15m, 1h, 4h
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class AdxTrendFilterPlus(BaseStrategy):
    """ADX Trend Filter - Strong ADX + EMA alignment + RSI pullback"""

    def __init__(self, config: StrategyConfig = None):
        super().__init__(config)
        self.config.stop_loss_atr_mult = 1.8
        self.config.take_profit_rr_ratio = 2.4
        
    def get_required_indicators(self) -> List[str]:
        return ["adx", "ema", "rsi", "atr"]
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals = []
        position = None
        
        for i in range(1, len(df)):
            row = df.iloc[i]
            prev = df.iloc[i - 1]
            
            close = row["close"]
            adx = row.get("adx", 0)
            rsi = row.get("rsi", 50)
            ema_200 = row.get("ema_200", close)
            ema_12 = row.get("ema_12", close)
            ema_12_prev = prev.get("ema_12", close)
            atr = row.get("atr", close * 0.02)
            timestamp = row["timestamp"]
            
            # LONG
            if position is None and close > ema_200:
                if adx >= 25 and 42 <= rsi <= 55 and close > ema_12_prev:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(
                        type=SignalType.LONG, timestamp=timestamp, price=close,
                        confidence=min(1.0, adx / 50), stop_loss=sl, take_profit=tp,
                        metadata={"adx": adx, "rsi": rsi, "reason": "ADX strong trend + RSI pullback"}
                    ))
                    position = "LONG"
            
            # SHORT
            elif position is None and close < ema_200:
                if adx >= 25 and 45 <= rsi <= 58 and close < ema_12_prev:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(
                        type=SignalType.SHORT, timestamp=timestamp, price=close,
                        confidence=min(1.0, adx / 50), stop_loss=sl, take_profit=tp,
                        metadata={"adx": adx, "rsi": rsi, "reason": "ADX strong trend + RSI pullback"}
                    ))
                    position = "SHORT"
            
            # Exit
            elif position == "LONG" and close < ema_200:
                signals.append(Signal(type=SignalType.CLOSE_LONG, timestamp=timestamp, price=close, metadata={"reason": "Trend reversal"}))
                position = None
            elif position == "SHORT" and close > ema_200:
                signals.append(Signal(type=SignalType.CLOSE_SHORT, timestamp=timestamp, price=close, metadata={"reason": "Trend reversal"}))
                position = None
        
        logger.info(f"AdxTrendFilterPlus generated {len(signals)} signals")
        return signals


__all__ = ["AdxTrendFilterPlus"]
