"""VWAP Band Fade Pro"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class VwapBandFadePro(BaseStrategy):
    """
    VwapBandFadePro - Professional VWAP band fading system
    
    Category: advanced
    Indicators: vwap, rsi, atr
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize VwapBandFadePro strategy."""
        super().__init__(config)
        
        # OPTIMIZABLE PARAMETERS
        self.vwap_deviation_std = self.config.get("vwap_deviation_std", 2.0)
        self.rsi_oversold = self.config.get("rsi_oversold", 30)
        self.rsi_overbought = self.config.get("rsi_overbought", 70)
        self.fade_threshold = self.config.get("fade_threshold", 1.5)
        self.sl_atr_mult = self.config.get("sl_atr_mult", 2.0)
        self.tp_rr_mult = self.config.get("tp_rr_mult", 2.5)

    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        return ["vwap", "atr", "rsi"]
    
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
            vwap = r.get("vwap", close)
            atr, rsi = r.get("atr", close*0.02), r.get("rsi", 50)
            vwap_upper, vwap_lower = vwap + 2*atr, vwap - 2*atr
            if pos is None:
                if close <= vwap_lower and rsi < self.rsi_oversold:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.8, sl, tp, {}))
                    pos = "LONG"
                elif close >= vwap_upper and rsi > self.rsi_overbought:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(SignalType.SHORT, r["timestamp"], close, 0.8, sl, tp, {}))
                    pos = "SHORT"
            elif pos and abs(close - vwap) < atr * 0.5:
                sig_type = SignalType.CLOSE_LONG if pos == "LONG" else SignalType.CLOSE_SHORT
                signals.append(Signal(sig_type, r["timestamp"], close, metadata={}))
                pos = None
        logger.info(f"VwapBandFadePro: {len(signals)} signals")
        return signals


__all__ = ["VwapBandFadePro"]
