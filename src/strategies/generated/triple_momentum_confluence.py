"""
Triple Momentum Confluence
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class TripleMomentumConfluence(BaseStrategy):
    """
    TripleMomentumConfluence - RSI + MACD + Stochastic alignment
    
    Category: momentum
    Indicators: rsi, macd, stochastic, atr
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize TripleMomentumConfluence strategy."""
        super().__init__(config)
        
        # OPTIMIZABLE PARAMETERS
        self.rsi_period = self.config.get("rsi_period", 14)
        self.rsi_threshold = self.config.get("rsi_threshold", 50)
        self.macd_fast = self.config.get("macd_fast", 12)
        self.macd_slow = self.config.get("macd_slow", 26)
        self.macd_signal = self.config.get("macd_signal", 9)
        self.stoch_k = self.config.get("stoch_k", 14)
        self.stoch_d = self.config.get("stoch_d", 3)
        self.sl_atr_mult = self.config.get("sl_atr_mult", 2.0)
        self.tp_rr_mult = self.config.get("tp_rr_mult", 2.5)

    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        return ['rsi', 'macd', 'stochastic', 'atr']
    
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
            
            # Get indicators
            rsi = r.get("rsi", 50)
            macd_hist = r.get("macd_hist", 0)
            stoch_k_val = r.get("stoch_k", 50)
            stoch_d_val = r.get("stoch_d", 50)
            atr = r.get("atr", close*0.02)
            
            # ? USE rsi_threshold parameter for RSI levels
            rsi_bullish = rsi > self.rsi_threshold
            rsi_bearish = rsi < self.rsi_threshold
            
            # MACD momentum
            macd_bullish = macd_hist > 0
            macd_bearish = macd_hist < 0
            
            # Stochastic momentum (use 50 as neutral threshold)
            stoch_bullish = stoch_k_val > 50 and stoch_k_val > stoch_d_val
            stoch_bearish = stoch_k_val < 50 and stoch_k_val < stoch_d_val
            
            if pos is None:
                # Count bullish/bearish signals (need 2 out of 3)
                bullish_count = sum([rsi_bullish, macd_bullish, stoch_bullish])
                bearish_count = sum([rsi_bearish, macd_bearish, stoch_bearish])
                
                # LONG: At least 2 out of 3 momentum indicators bullish
                if bullish_count >= 2:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(
                        SignalType.LONG, 
                        r["timestamp"], 
                        close, 
                        bullish_count / 3.0,  # Confidence based on alignment
                        sl, 
                        tp, 
                        {
                            "rsi": rsi,
                            "macd_hist": macd_hist,
                            "stoch_k": stoch_k_val,
                            "bullish_signals": bullish_count,
                            "rsi_threshold": self.rsi_threshold
                        }
                    ))
                    pos = "LONG"
                
                # SHORT: At least 2 out of 3 momentum indicators bearish
                elif bearish_count >= 2:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(
                        SignalType.SHORT, 
                        r["timestamp"], 
                        close, 
                        bearish_count / 3.0,
                        sl, 
                        tp, 
                        {
                            "rsi": rsi,
                            "macd_hist": macd_hist,
                            "stoch_k": stoch_k_val,
                            "bearish_signals": bearish_count,
                            "rsi_threshold": self.rsi_threshold
                        }
                    ))
                    pos = "SHORT"
            
            # Exit when momentum reverses (2 out of 3 flip)
            elif pos == "LONG":
                bearish_count = sum([rsi_bearish, macd_bearish, stoch_bearish])
                if bearish_count >= 2:
                    signals.append(Signal(
                        SignalType.CLOSE_LONG, 
                        r["timestamp"], 
                        close,
                        metadata={"reason": "Momentum reversed", "bearish_signals": bearish_count}
                    ))
                    pos = None
            
            elif pos == "SHORT":
                bullish_count = sum([rsi_bullish, macd_bullish, stoch_bullish])
                if bullish_count >= 2:
                    signals.append(Signal(
                        SignalType.CLOSE_SHORT, 
                        r["timestamp"], 
                        close,
                        metadata={"reason": "Momentum reversed", "bullish_signals": bullish_count}
                    ))
                    pos = None
                    
        logger.info(f"TripleMomentumConfluence: {len(signals)} signals")
        return signals


__all__ = ["TripleMomentumConfluence"]
