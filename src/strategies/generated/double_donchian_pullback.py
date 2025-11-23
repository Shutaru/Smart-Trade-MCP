"""
Double Donchian Pullback | Pure Price Action Donchian | OBV Confirmation Breakout Plus | EMA200 Tap Reversion | NY Session Fade | Regime Adaptive Core | Complete System 5x
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class DoubleDonchianPullback(BaseStrategy):
    def __init__(self, config: StrategyConfig = None):
        """Initialize DoubleDonchianPullback strategy."""
        super().__init__(config)
        
        # OPTIMIZABLE PARAMETERS
        self.donchian_fast = self.config.get("donchian_fast", 10)
        self.donchian_slow = self.config.get("donchian_slow", 20)
        self.ema_period = self.config.get("ema_period", 50)
        self.sl_atr_mult = self.config.get("sl_atr_mult", 2.0)
        self.tp_rr_mult = self.config.get("tp_rr_mult", 2.5)

    def get_required_indicators(self) -> List[str]:
        return ["donchian", "atr"]
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals, pos = [], None
        
        for i in range(max(self.donchian_slow, self.ema_period), len(df)):
            r = df.iloc[i]
            close = r["close"]
            
            # Get Donchian middle (average of upper and lower)
            don_m = r.get("donchian_middle", close)
            don_u = r.get("donchian_upper", close)
            don_l = r.get("donchian_lower", close)
            
            # ? USE ema_period parameter for trend confirmation
            ema_trend = r.get(f"ema_{self.ema_period}", close)
            atr = r.get("atr", close*0.02)
            
            # Pullback to Donchian middle (mean reversion within trend)
            near_middle = abs(close - don_m) < atr * 0.5
            
            if pos is None and near_middle:
                # LONG: Price at Donchian middle + uptrend
                if close > don_m and close > ema_trend:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(
                        SignalType.LONG, 
                        r["timestamp"], 
                        close, 
                        0.7, 
                        sl, 
                        tp, 
                        {
                            "donchian_fast": self.donchian_fast,
                            "donchian_slow": self.donchian_slow,
                            "ema_period": self.ema_period,
                            "reason": "Pullback to Donchian middle in uptrend"
                        }
                    ))
                    pos = "LONG"
                
                # SHORT: Price at Donchian middle + downtrend
                elif close < don_m and close < ema_trend:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(
                        SignalType.SHORT, 
                        r["timestamp"], 
                        close, 
                        0.7, 
                        sl, 
                        tp, 
                        {
                            "donchian_fast": self.donchian_fast,
                            "donchian_slow": self.donchian_slow,
                            "ema_period": self.ema_period,
                            "reason": "Pullback to Donchian middle in downtrend"
                        }
                    ))
                    pos = "SHORT"
            
            # Exit when breaks opposite Donchian extreme (trend reversed)
            elif pos == "LONG" and close < don_l:
                signals.append(Signal(
                    SignalType.CLOSE_LONG, 
                    r["timestamp"], 
                    close,
                    metadata={"reason": "Broke Donchian lower (trend reversed)"}
                ))
                pos = None
            
            elif pos == "SHORT" and close > don_u:
                signals.append(Signal(
                    SignalType.CLOSE_SHORT, 
                    r["timestamp"], 
                    close,
                    metadata={"reason": "Broke Donchian upper (trend reversed)"}
                ))
                pos = None
                
        logger.info(f"DoubleDonchianPullback: {len(signals)} signals")
        return signals


class PurePriceActionDonchian(BaseStrategy):
    def __init__(self, config: StrategyConfig = None):
        super().__init__(config)
        
    def get_required_indicators(self) -> List[str]:
        return ["donchian", "atr"]
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals, pos = [], None
        for i in range(1, len(df)):
            r = df.iloc[i]
            close = r["close"]
            don_u, atr = r.get("donchian_upper", close), r.get("atr", close*0.02)
            if pos is None and close > don_u:
                sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.75, sl, tp, {}))
                pos = "LONG"
        logger.info(f"PurePriceActionDonchian: {len(signals)} signals")
        return signals


class ObvConfirmationBreakoutPlus(BaseStrategy):
    def __init__(self, config: StrategyConfig = None):
        super().__init__(config)
        
    def get_required_indicators(self) -> List[str]:
        return ["obv", "bollinger", "atr"]
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals, pos = [], None
        for i in range(5, len(df)):
            r = df.iloc[i]
            close = r["close"]
            bb_u, obv, atr = r.get("bb_upper", close), r.get("obv", 0), r.get("atr", close*0.02)
            obv_rising = obv > df.iloc[i-5].get("obv", 0)
            if pos is None and close > bb_u and obv_rising:
                sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.8, sl, tp, {}))
                pos = "LONG"
        logger.info(f"ObvConfirmationBreakoutPlus: {len(signals)} signals")
        return signals


class Ema200TapReversion(BaseStrategy):
    def __init__(self, config: StrategyConfig = None):
        super().__init__(config)
        
    def get_required_indicators(self) -> List[str]:
        return ["ema", "rsi", "atr"]
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals, pos = [], None
        for i in range(1, len(df)):
            r = df.iloc[i]
            close = r["close"]
            low, ema200, rsi, atr = r["low"], r.get("ema_200", close), r.get("rsi", 50), r.get("atr", close*0.02)
            tap_ema = abs(low - ema200) < atr * 0.5
            if pos is None and close > ema200 and tap_ema and 40 < rsi < 55:
                sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.8, sl, tp, {}))
                pos = "LONG"
        logger.info(f"Ema200TapReversion: {len(signals)} signals")
        return signals


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
            bb_u, bb_l, rsi, atr = r.get("bb_upper", close), r.get("bb_lower", close), r.get("rsi", 50), r.get("atr", close*0.02)
            if pos is None:
                if close >= bb_u and rsi > 70:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(SignalType.SHORT, r["timestamp"], close, 0.7, sl, tp, {}))
                    pos = "SHORT"
        logger.info(f"NySessionFade: {len(signals)} signals")
        return signals


class RegimeAdaptiveCore(BaseStrategy):
    def __init__(self, config: StrategyConfig = None):
        super().__init__(config)
        
    def get_required_indicators(self) -> List[str]:
        return ["adx", "ema", "rsi", "atr"]
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals, pos = [], None
        for i in range(1, len(df)):
            r = df.iloc[i]
            close = r["close"]
            adx, ema200, rsi, atr = r.get("adx", 0), r.get("ema_200", close), r.get("rsi", 50), r.get("atr", close*0.02)
            trending = adx > 25
            if pos is None:
                if trending and close > ema200 and rsi > 50:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.8, sl, tp, {}))
                    pos = "LONG"
                elif not trending and rsi < 30:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.7, sl, tp, {}))
                    pos = "LONG"
        logger.info(f"RegimeAdaptiveCore: {len(signals)} signals")
        return signals


class CompleteSystem5x(BaseStrategy):
    def __init__(self, config: StrategyConfig = None):
        super().__init__(config)
        
    def get_required_indicators(self) -> List[str]:
        return ["ema", "rsi", "macd", "bollinger", "adx", "supertrend", "atr"]
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals, pos = [], None
        for i in range(1, len(df)):
            r = df.iloc[i]
            close = r["close"]
            ema200, rsi, macd_hist, adx = r.get("ema_200", close), r.get("rsi", 50), r.get("macd_hist", 0), r.get("adx", 0)
            st_trend, atr = r.get("supertrend_trend", 0), r.get("atr", close*0.02)
            # All conditions aligned
            if pos is None and close > ema200 and rsi > 50 and macd_hist > 0 and adx > 20 and st_trend > 0:
                sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                signals.append(Signal(SignalType.LONG, r["timestamp"], close, 0.95, sl, tp, {}))
                pos = "LONG"
        logger.info(f"CompleteSystem5x: {len(signals)} signals")
        return signals


__all__ = ["DoubleDonchianPullback", "PurePriceActionDonchian", "ObvConfirmationBreakoutPlus", "Ema200TapReversion", "NySessionFade", "RegimeAdaptiveCore", "CompleteSystem5x"]
