"""NY Session Fade"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class NySessionFade(BaseStrategy):
    def __init__(self, config: StrategyConfig = None):
        super().__init__(config)

    def get_required_indicators(self) -> List[str]:
        return ["rsi", "bollinger", "atr"]

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals, pos = [], None
        for i in range(1, len(df)):
            r = df.iloc[i]
            close = r["close"]
            bb_u, bb_l = r.get("bb_upper", close), r.get("bb_lower", close)
            bb_m = (bb_u + bb_l) / 2
            rsi, atr = r.get("rsi", 50), r.get("atr", close * 0.02)

            if pos is None:
                # Fade overbought - expect drop
                if close >= bb_u and rsi > 70:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(
                        Signal(
                            SignalType.SHORT,
                            r["timestamp"],
                            close,
                            0.7,
                            sl,
                            tp,
                            {},
                        )
                    )
                    pos = "SHORT"
                # Fade oversold - expect rise
                elif close <= bb_l and rsi < 30:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(
                        Signal(
                            SignalType.LONG,
                            r["timestamp"],
                            close,
                            0.7,
                            sl,
                            tp,
                            {},
                        )
                    )
                    pos = "LONG"

            # ADD EXIT LOGIC - exit when reaches opposite extreme or BB middle
            elif pos == "SHORT" and (close <= bb_l or rsi < 30):
                signals.append(
                    Signal(
                        SignalType.CLOSE_SHORT,
                        r["timestamp"],
                        close,
                        metadata={"reason": "Reached opposite extreme"},
                    )
                )
                pos = None

            elif pos == "LONG" and (close >= bb_u or rsi > 70):
                signals.append(
                    Signal(
                        SignalType.CLOSE_LONG,
                        r["timestamp"],
                        close,
                        metadata={"reason": "Reached opposite extreme"},
                    )
                )
                pos = None
        logger.info(f"NySessionFade: {len(signals)} signals")
        return signals


__all__ = ["NySessionFade"]
