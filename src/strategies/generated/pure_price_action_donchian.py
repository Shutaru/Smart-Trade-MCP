"""Pure Price Action Donchian"""
from typing import List
import pandas as pd
from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class PurePriceActionDonchian(BaseStrategy):
    def __init__(self, config: StrategyConfig = None):
        super().__init__(config)

    def get_required_indicators(self) -> List[str]:
        return ["donchian", "atr"]

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals, pos = [], None
        for i in range(1, len(df)):
            r = df.iloc[i]
            close, don_u, atr = r["close"], r.get("donchian_upper", close), r.get("atr", close * 0.02)
            if pos is None and close > don_u:
                sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.75, sl, tp, {}))
                pos = "LONG"
        logger.info(f"PurePriceActionDonchian: {len(signals)} signals")
        return signals


__all__ = ["PurePriceActionDonchian"]
