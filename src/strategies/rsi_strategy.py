"""
RSI-based Trading Strategy

Classic RSI strategy with overbought/oversold levels.
"""

from typing import List

import pandas as pd

from .base import BaseStrategy, Signal, SignalType, StrategyConfig
from ..core.logger import logger


class RSIStrategy(BaseStrategy):
    """
    RSI Strategy - Classic mean reversion.
    
    **Logic:**
    - LONG: RSI < 30 (oversold)
    - SHORT: RSI > 70 (overbought)
    - Exit: RSI crosses back to 50
    
    **Parameters:**
    - rsi_period: RSI calculation period (default: 14)
    - oversold_level: Oversold threshold (default: 30)
    - overbought_level: Overbought threshold (default: 70)
    - exit_level: Exit signal level (default: 50)
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize RSI strategy."""
        super().__init__(config)
        
        # Strategy-specific defaults
        self.rsi_period = self.config.get("rsi_period", 14)
        self.oversold = self.config.get("oversold_level", 30)
        self.overbought = self.config.get("overbought_level", 70)
        self.exit_level = self.config.get("exit_level", 50)

    def get_required_indicators(self) -> List[str]:
        """RSI strategy requires RSI and ATR indicators."""
        return ["rsi", "atr"]

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        Generate RSI-based trading signals.

        Args:
            df: DataFrame with OHLCV and RSI data

        Returns:
            List of trading signals
        """
        signals = []
        
        if "rsi" not in df.columns:
            logger.warning("RSI column not found in DataFrame")
            return signals

        # Track current position (for exit signals)
        position = None  # None, "LONG", or "SHORT"

        for i in range(1, len(df)):
            current_row = df.iloc[i]
            prev_row = df.iloc[i - 1]

            rsi_current = current_row["rsi"]
            rsi_prev = prev_row["rsi"]
            
            if pd.isna(rsi_current) or pd.isna(rsi_prev):
                continue

            timestamp = current_row["timestamp"]
            price = current_row["close"]
            atr = current_row.get("atr", price * 0.02)  # Fallback to 2% if no ATR

            # Entry Signals
            if position is None:
                # LONG entry: RSI crosses below oversold
                if rsi_prev >= self.oversold and rsi_current < self.oversold:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, price, atr)
                    
                    signals.append(Signal(
                        type=SignalType.LONG,
                        timestamp=timestamp,
                        price=price,
                        confidence=min(1.0, (self.oversold - rsi_current) / 10),
                        stop_loss=sl,
                        take_profit=tp,
                        metadata={"rsi": rsi_current, "reason": "RSI oversold"},
                    ))
                    position = "LONG"

                # SHORT entry: RSI crosses above overbought
                elif rsi_prev <= self.overbought and rsi_current > self.overbought:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, price, atr)
                    
                    signals.append(Signal(
                        type=SignalType.SHORT,
                        timestamp=timestamp,
                        price=price,
                        confidence=min(1.0, (rsi_current - self.overbought) / 10),
                        stop_loss=sl,
                        take_profit=tp,
                        metadata={"rsi": rsi_current, "reason": "RSI overbought"},
                    ))
                    position = "SHORT"

            # Exit Signals
            else:
                # Exit LONG: RSI crosses above exit level
                if position == "LONG" and rsi_prev < self.exit_level and rsi_current >= self.exit_level:
                    signals.append(Signal(
                        type=SignalType.CLOSE_LONG,
                        timestamp=timestamp,
                        price=price,
                        metadata={"rsi": rsi_current, "reason": "RSI mean reversion"},
                    ))
                    position = None

                # Exit SHORT: RSI crosses below exit level
                elif position == "SHORT" and rsi_prev > self.exit_level and rsi_current <= self.exit_level:
                    signals.append(Signal(
                        type=SignalType.CLOSE_SHORT,
                        timestamp=timestamp,
                        price=price,
                        metadata={"rsi": rsi_current, "reason": "RSI mean reversion"},
                    ))
                    position = None

        logger.info(f"RSIStrategy generated {len(signals)} signals")
        return signals


__all__ = ["RSIStrategy"]
