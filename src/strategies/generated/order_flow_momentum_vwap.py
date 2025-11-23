"""Order Flow Momentum VWAP"""
from typing import List
import pandas as pd
from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class OrderFlowMomentumVwap(BaseStrategy):
    def __init__(self, config: StrategyConfig = None):
        """Initialize OrderFlowMomentumVwap strategy."""
        super().__init__(config)
        
        # OPTIMIZABLE PARAMETERS
        self.vwap_deviation_std = self.config.get("vwap_deviation_std", 1.0)
        self.obv_ema_period = self.config.get("obv_ema_period", 20)
        self.momentum_threshold = self.config.get("momentum_threshold", 1.5)
        self.sl_atr_mult = self.config.get("sl_atr_mult", 2.0)
        self.tp_rr_mult = self.config.get("tp_rr_mult", 2.5)

    def get_required_indicators(self) -> List[str]:
        return ["vwap", "obv", "atr"]

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals, pos = [], None
        
        # Calculate OBV EMA using parameter
        obv_ema = df["obv"].ewm(span=self.obv_ema_period, adjust=False).mean() if "obv" in df.columns else None
        
        # Calculate VWAP deviation bands
        vwap_std = df["close"].rolling(window=20).std()
        
        for i in range(max(5, self.obv_ema_period, 20), len(df)):
            r = df.iloc[i]
            close = r["close"]
            vwap = r.get("vwap", close)
            obv = r.get("obv", 0)
            atr = r.get("atr", close * 0.02)
            
            # USE vwap_deviation_std parameter
            vwap_upper = vwap + (vwap_std.iloc[i] * self.vwap_deviation_std)
            vwap_lower = vwap - (vwap_std.iloc[i] * self.vwap_deviation_std)
            
            # OBV momentum detection
            obv_5ago = df.iloc[i - 5].get("obv", 0)
            obv_change = (obv - obv_5ago) / obv_5ago if obv_5ago != 0 else 0
            
            # USE momentum_threshold parameter
            strong_obv_momentum = abs(obv_change) > (self.momentum_threshold / 100)
            
            # Direction
            obv_rising = obv > obv_5ago
            obv_falling = obv < obv_5ago
            
            if pos is None:
                # LONG: Price above VWAP + strong OBV momentum upward
                if close > vwap and obv_rising and strong_obv_momentum:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(
                        SignalType.LONG, 
                        r["timestamp"], 
                        close, 
                        min(1.0, abs(obv_change) * 10),  # Confidence based on momentum
                        sl, 
                        tp, 
                        {
                            "obv": obv,
                            "obv_change_pct": obv_change * 100,
                            "momentum_threshold": self.momentum_threshold,
                            "vwap_deviation_std": self.vwap_deviation_std,
                            "reason": "Strong order flow momentum (buy-side)"
                        }
                    ))
                    pos = "LONG"
                
                # SHORT: Price below VWAP + strong OBV momentum downward
                elif close < vwap and obv_falling and strong_obv_momentum:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(
                        SignalType.SHORT, 
                        r["timestamp"], 
                        close, 
                        min(1.0, abs(obv_change) * 10),
                        sl, 
                        tp, 
                        {
                            "obv": obv,
                            "obv_change_pct": obv_change * 100,
                            "momentum_threshold": self.momentum_threshold,
                            "vwap_deviation_std": self.vwap_deviation_std,
                            "reason": "Strong order flow momentum (sell-side)"
                        }
                    ))
                    pos = "SHORT"
            
            # Exit when OBV reverses OR VWAP cross
            elif pos == "LONG":
                obv_reversed = obv < df.iloc[i-1].get("obv", 0)
                vwap_cross = close < vwap
                
                if obv_reversed or vwap_cross:
                    signals.append(Signal(
                        SignalType.CLOSE_LONG, 
                        r["timestamp"], 
                        close,
                        metadata={"reason": "OBV reversed or VWAP cross"}
                    ))
                    pos = None
            
            elif pos == "SHORT":
                obv_reversed = obv > df.iloc[i-1].get("obv", 0)
                vwap_cross = close > vwap
                
                if obv_reversed or vwap_cross:
                    signals.append(Signal(
                        SignalType.CLOSE_SHORT, 
                        r["timestamp"], 
                        close,
                        metadata={"reason": "OBV reversed or VWAP cross"}
                    ))
                    pos = None
                    
        logger.info(f"OrderFlowMomentumVwap: {len(signals)} signals")
        return signals


__all__ = ["OrderFlowMomentumVwap"]
