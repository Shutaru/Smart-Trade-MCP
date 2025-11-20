"""
MACD Trend Following Strategy

Classic MACD crossover strategy with trend confirmation.
"""

from typing import List

import pandas as pd

from .base import BaseStrategy, Signal, SignalType, StrategyConfig
from ..core.logger import logger


class MACDStrategy(BaseStrategy):
    """
    MACD Strategy - Trend following with MACD crossovers.
    
    **Logic:**
    - LONG: MACD crosses above signal line + MACD histogram > 0
    - SHORT: MACD crosses below signal line + MACD histogram < 0
    - Exit: Opposite crossover
    
    **Parameters:**
    - fast_period: Fast EMA period (default: 12)
    - slow_period: Slow EMA period (default: 26)
    - signal_period: Signal line period (default: 9)
    - histogram_threshold: Minimum histogram value (default: 0)
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize MACD strategy."""
        super().__init__(config)
        
        # Strategy-specific defaults
        self.fast_period = self.config.get("fast_period", 12)
        self.slow_period = self.config.get("slow_period", 26)
        self.signal_period = self.config.get("signal_period", 9)
        self.hist_threshold = self.config.get("histogram_threshold", 0.0)

    def get_required_indicators(self) -> List[str]:
        """MACD strategy requires MACD and ATR indicators."""
        return ["macd", "atr"]

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        Generate MACD-based trading signals.

        Args:
            df: DataFrame with OHLCV and MACD data

        Returns:
            List of trading signals
        """
        signals = []
        
        required_cols = ["macd", "macd_signal", "macd_hist"]
        if not all(col in df.columns for col in required_cols):
            logger.warning("MACD columns not found in DataFrame")
            return signals

        # Track current position
        position = None  # None, "LONG", or "SHORT"

        for i in range(1, len(df)):
            current_row = df.iloc[i]
            prev_row = df.iloc[i - 1]

            macd = current_row["macd"]
            macd_signal = current_row["macd_signal"]
            macd_hist = current_row["macd_hist"]
            
            macd_prev = prev_row["macd"]
            macd_signal_prev = prev_row["macd_signal"]
            
            if pd.isna(macd) or pd.isna(macd_signal):
                continue

            timestamp = current_row["timestamp"]
            price = current_row["close"]
            atr = current_row.get("atr", price * 0.02)

            # Entry Signals
            if position is None:
                # LONG entry: MACD crosses above signal line
                if macd_prev < macd_signal_prev and macd > macd_signal and macd_hist > self.hist_threshold:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, price, atr)
                    
                    # Confidence based on histogram strength
                    confidence = min(1.0, abs(macd_hist) / (atr * 10))
                    
                    signals.append(Signal(
                        type=SignalType.LONG,
                        timestamp=timestamp,
                        price=price,
                        confidence=confidence,
                        stop_loss=sl,
                        take_profit=tp,
                        metadata={
                            "macd": macd,
                            "macd_signal": macd_signal,
                            "histogram": macd_hist,
                            "reason": "MACD bullish crossover",
                        },
                    ))
                    position = "LONG"

                # SHORT entry: MACD crosses below signal line
                elif macd_prev > macd_signal_prev and macd < macd_signal and macd_hist < -self.hist_threshold:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, price, atr)
                    
                    confidence = min(1.0, abs(macd_hist) / (atr * 10))
                    
                    signals.append(Signal(
                        type=SignalType.SHORT,
                        timestamp=timestamp,
                        price=price,
                        confidence=confidence,
                        stop_loss=sl,
                        take_profit=tp,
                        metadata={
                            "macd": macd,
                            "macd_signal": macd_signal,
                            "histogram": macd_hist,
                            "reason": "MACD bearish crossover",
                        },
                    ))
                    position = "SHORT"

            # Exit Signals
            else:
                # Exit LONG: MACD crosses below signal line
                if position == "LONG" and macd_prev > macd_signal_prev and macd < macd_signal:
                    signals.append(Signal(
                        type=SignalType.CLOSE_LONG,
                        timestamp=timestamp,
                        price=price,
                        metadata={
                            "macd": macd,
                            "macd_signal": macd_signal,
                            "reason": "MACD bearish crossover",
                        },
                    ))
                    position = None

                # Exit SHORT: MACD crosses above signal line
                elif position == "SHORT" and macd_prev < macd_signal_prev and macd > macd_signal:
                    signals.append(Signal(
                        type=SignalType.CLOSE_SHORT,
                        timestamp=timestamp,
                        price=price,
                        metadata={
                            "macd": macd,
                            "macd_signal": macd_signal,
                            "reason": "MACD bullish crossover",
                        },
                    ))
                    position = None

        logger.info(f"MACDStrategy generated {len(signals)} signals")
        return signals


__all__ = ["MACDStrategy"]
