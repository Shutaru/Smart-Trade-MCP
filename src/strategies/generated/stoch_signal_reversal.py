"""
Stochastic Signal Reversal - Stochastic oversold/overbought crossover
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class StochSignalReversal(BaseStrategy):
    """Stochastic %K crosses %D in extreme zones with EMA + RSI confirmation"""
    
    def __init__(self, config: StrategyConfig = None):
        """Initialize StochSignalReversal strategy."""
        super().__init__(config)
        
        # OPTIMIZABLE PARAMETERS
        self.stoch_k = self.config.get("stoch_k", 14)
        self.stoch_d = self.config.get("stoch_d", 3)
        self.stoch_oversold = self.config.get("stoch_oversold", 20)
        self.stoch_overbought = self.config.get("stoch_overbought", 80)
        self.rsi_confirm = self.config.get("rsi_confirm", 50)
        self.sl_atr_mult = self.config.get("sl_atr_mult", 2.0)
        self.tp_rr_mult = self.config.get("tp_rr_mult", 2.5)

    def get_required_indicators(self) -> List[str]:
        return ["stochastic", "ema", "rsi", "atr"]
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals, pos = [], None
        for i in range(1, len(df)):
            r, p = df.iloc[i], df.iloc[i-1]
            close = r["close"]
            stoch_k, stoch_d = r.get("stoch_k", 50), r.get("stoch_d", 50)
            stoch_k_prev, stoch_d_prev = p.get("stoch_k", 50), p.get("stoch_d", 50)
            rsi = r.get("rsi", 50)
            ema_50 = r.get("ema_50", close)
            atr = r.get("atr", close*0.02)
            
            if pos is None:
                # FIX: More restrictive - need trend confirmation
                k_cross_above = stoch_k_prev <= stoch_d_prev and stoch_k > stoch_d
                deep_oversold = stoch_k < self.stoch_oversold and stoch_d < self.stoch_oversold  # Very oversold
                uptrend = close > ema_50  # Trend confirmation
                rsi_ok = 30 < rsi < 60  # Neutral to slightly bullish
                
                if k_cross_above and deep_oversold and uptrend and rsi_ok:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, 1.0 - (stoch_k/100), sl, tp,
                                        {"stoch_k": stoch_k, "reason": "Stoch oversold crossover + trend"}))
                    pos = "LONG"
                
                # FIX: More restrictive
                k_cross_below = stoch_k_prev >= stoch_d_prev and stoch_k < stoch_d
                deep_overbought = stoch_k > self.stoch_overbought and stoch_d > self.stoch_overbought  # Very overbought
                downtrend = close < ema_50  # Trend confirmation
                rsi_ok_short = 40 < rsi < 70  # Neutral to slightly bearish
                
                if k_cross_below and deep_overbought and downtrend and rsi_ok_short:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(SignalType.SHORT, r["timestamp"], close, (stoch_k-50)/50, sl, tp,
                                        {"stoch_k": stoch_k, "reason": "Stoch overbought crossover + trend"}))
                    pos = "SHORT"
            
            # Exit when stochastic exits extreme zone
            elif pos == "LONG" and stoch_k > self.stoch_overbought:  # Reached overbought
                signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close, 
                                    metadata={"reason": "Stoch overbought"}))
                pos = None
            elif pos == "SHORT" and stoch_k < self.stoch_oversold:  # Reached oversold
                signals.append(Signal(SignalType.CLOSE_SHORT, r["timestamp"], close, 
                                    metadata={"reason": "Stoch oversold"}))
                pos = None
                
        logger.info(f"StochSignalReversal: {len(signals)} signals")
        return signals


__all__ = ["StochSignalReversal"]
