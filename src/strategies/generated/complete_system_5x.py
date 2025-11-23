"""
Complete System 5x - Ultimate multi-factor confluence system
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class CompleteSystem5x(BaseStrategy):
    """Complete System 5x - Ultimate multi-factor confluence system"""

    def __init__(self, config: StrategyConfig = None):
        """Initialize CompleteSystem5x strategy."""
        super().__init__(config)
        
        # OPTIMIZABLE PARAMETERS
        self.ema_fast = self.config.get("ema_fast", 20)
        self.ema_slow = self.config.get("ema_slow", 50)
        self.rsi_period = self.config.get("rsi_period", 14)
        self.rsi_threshold = self.config.get("rsi_threshold", 50)
        self.macd_fast = self.config.get("macd_fast", 12)
        self.macd_slow = self.config.get("macd_slow", 26)
        self.adx_threshold = self.config.get("adx_threshold", 25)
        self.sl_atr_mult = self.config.get("sl_atr_mult", 2.0)
        self.tp_rr_mult = self.config.get("tp_rr_mult", 2.5)

    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        return ["ema", "rsi", "macd", "bollinger", "adx", "supertrend", "atr"]

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
            close = r["close"]
            ema200, rsi, macd_hist, adx = r.get("ema_200", close), r.get("rsi", 50), r.get("macd_hist", 0), r.get("adx", 0)
            st_trend, atr = r.get("supertrend_trend", 0), r.get("atr", close * 0.02)
            bb_u, bb_l = r.get("bb_upper", close), r.get("bb_lower", close)
            
            # All 5 confirmations for LONG
            long_confirmations = sum([
                close > ema200,
                rsi > 50,
                macd_hist > 0,
                adx > 20,
                st_trend > 0
            ])
            
            # All 5 confirmations for SHORT
            short_confirmations = sum([
                close < ema200,
                rsi < 50,
                macd_hist < 0,
                adx > 20,
                st_trend < 0
            ])
            
            if pos is None:
                if long_confirmations >= 4:  # At least 4 of 5 confirmations
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.95, sl, tp,
                                        {"confirmations": long_confirmations}))
                    pos = "LONG"
                elif short_confirmations >= 4:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(SignalType.SHORT, r["timestamp"], close, 0.95, sl, tp,
                                        {"confirmations": short_confirmations}))
                    pos = "SHORT"
            
            # ADD EXIT LOGIC - exit when any confirmation fails
            elif pos == "LONG":
                confirmations_lost = long_confirmations < 3  # Needs at least 3 to stay
                if confirmations_lost or st_trend < 0:
                    signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close,
                                        metadata={"reason": "Confirmations failed"}))
                    pos = None
            
            elif pos == "SHORT":
                confirmations_lost = short_confirmations < 3
                if confirmations_lost or st_trend > 0:
                    signals.append(Signal(SignalType.CLOSE_SHORT, r["timestamp"], close,
                                        metadata={"reason": "Confirmations failed"}))
                    pos = None
        logger.info(f"CompleteSystem5x: {len(signals)} signals")
        return signals


__all__ = ["CompleteSystem5x"]
