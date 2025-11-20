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
            close, high = r["close"], r["high"]
            don_u, atr = r.get("donchian_upper", close), r.get("atr", close * 0.02)
            
            # FIX: Use previous donchian_upper for breakout detection
            prev_don_u = df.iloc[i-1].get("donchian_upper", close) if i > 0 else don_u
            
            if pos is None and high > prev_don_u:
                sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.75, sl, tp, {}))
                pos = "LONG"
        logger.info(f"PurePriceActionDonchian: {len(signals)} signals")
        return signals


__all__ = ["PurePriceActionDonchian"]
