"""Order Flow Momentum VWAP"""
from typing import List
import pandas as pd
from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class OrderFlowMomentumVwap(BaseStrategy):
    def __init__(self, config: StrategyConfig = None):
        super().__init__(config)

    def get_required_indicators(self) -> List[str]:
        return ["vwap", "obv", "atr"]

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals, pos = [], None
        for i in range(5, len(df)):
            r = df.iloc[i]
            close = r["close"]
            vwap = r.get("vwap", close)
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


__all__ = ["OrderFlowMomentumVwap"]
