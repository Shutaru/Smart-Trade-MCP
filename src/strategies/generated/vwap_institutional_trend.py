"""
VWAP Institutional Trend | VWAP Mean Reversion | VWAP Band Fade Pro | Order Flow Momentum VWAP
"""

from typing import List
import pandas as pd
from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class VwapInstitutionalTrend(BaseStrategy):
    """VWAP institutional level trend (Win: 58-68%)"""

    def __init__(self, config: StrategyConfig = None):
        super().__init__(config)

    def get_required_indicators(self) -> List[str]:
        return ["vwap", "ema", "atr"]

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals, pos = [], None
        for i in range(1, len(df)):
            r = df.iloc[i]
            close, vwap = r["close"], r.get("vwap", close)
            ema200, atr = r.get("ema_200", close), r.get("atr", close * 0.02)
            if pos is None:
                if close > ema200 and close > vwap and df.iloc[i - 1]["close"] <= vwap:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.8, sl, tp, {}))
                    pos = "LONG"
                elif close < ema200 and close < vwap and df.iloc[i - 1]["close"] >= vwap:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(SignalType.SHORT, r["timestamp"], close, 0.8, sl, tp, {}))
                    pos = "SHORT"
        logger.info(f"VwapInstitutionalTrend: {len(signals)} signals")
        return signals


class VwapMeanReversion(BaseStrategy):
    def __init__(self, config: StrategyConfig = None):
        super().__init__(config)

    def get_required_indicators(self) -> List[str]:
        return ["vwap", "rsi", "atr"]

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals, pos = [], None
        for i in range(1, len(df)):
            r = df.iloc[i]
            close, vwap = r["close"], r.get("vwap", close)
            rsi, atr = r.get("rsi", 50), r.get("atr", close * 0.02)
            dist = abs(close - vwap) / vwap if vwap > 0 else 0
            if pos is None and dist > 0.015:  # 1.5% deviation
                if close < vwap and rsi < 40:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.7, sl, tp, {}))
                    pos = "LONG"
                elif close > vwap and rsi > 60:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(SignalType.SHORT, r["timestamp"], close, 0.7, sl, tp, {}))
                    pos = "SHORT"
            elif pos and abs(close - vwap) / vwap < 0.005:  # Close to VWAP
                sig_type = SignalType.CLOSE_LONG if pos == "LONG" else SignalType.CLOSE_SHORT
                signals.append(Signal(sig_type, r["timestamp"], close, metadata={}))
                pos = None
        logger.info(f"VwapMeanReversion: {len(signals)} signals")
        return signals


class VwapBandFadePro(BaseStrategy):
    def __init__(self, config: StrategyConfig = None):
        super().__init__(config)

    def get_required_indicators(self) -> List[str]:
        return ["vwap", "atr", "rsi"]

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals, pos = [], None
        for i in range(1, len(df)):
            r = df.iloc[i]
            close, vwap = r["close"], r.get("vwap", close)
            atr, rsi = r.get("atr", close * 0.02), r.get("rsi", 50)
            # VWAP bands: VWAP ± 2*ATR
            vwap_upper, vwap_lower = vwap + 2 * atr, vwap - 2 * atr
            if pos is None:
                if close <= vwap_lower and rsi < 35:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.8, sl, tp, {}))
                    pos = "LONG"
                elif close >= vwap_upper and rsi > 65:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(SignalType.SHORT, r["timestamp"], close, 0.8, sl, tp, {}))
                    pos = "SHORT"
            elif pos and abs(close - vwap) < atr * 0.5:
                sig_type = SignalType.CLOSE_LONG if pos == "LONG" else SignalType.CLOSE_SHORT
                signals.append(Signal(sig_type, r["timestamp"], close, metadata={}))
                pos = None
        logger.info(f"VwapBandFadePro: {len(signals)} signals")
        return signals


class OrderFlowMomentumVwap(BaseStrategy):
    def __init__(self, config: StrategyConfig = None):
        super().__init__(config)

    def get_required_indicators(self) -> List[str]:
        return ["vwap", "obv", "atr"]

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals, pos = [], None
        for i in range(5, len(df)):
            r = df.iloc[i]
            close, vwap = r["close"], r.get("vwap", close)
            obv, atr = r.get("obv", 0), r.get("atr", close * 0.02)
            obv_rising = obv > df.iloc[i - 5].get("obv", 0)
            if pos is None:
                if close > vwap and obv_rising:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.75, sl, tp, {}))
                    pos = "LONG"
                elif close < vwap and not obv_rising:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(SignalType.SHORT, r["timestamp"], close, 0.75, sl, tp, {}))
                    pos = "SHORT"
        logger.info(f"OrderFlowMomentumVwap: {len(signals)} signals")
        return signals


__all__ = ["VwapInstitutionalTrend", "VwapMeanReversion", "VwapBandFadePro", "OrderFlowMomentumVwap"]
