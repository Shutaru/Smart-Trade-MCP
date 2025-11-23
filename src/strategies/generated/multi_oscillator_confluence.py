"""
Multiple oscillators align for high-probability setup
"""

from typing import List
import pandas as pd

from ..base import BaseStrategy, Signal, SignalType, StrategyConfig
from ...core.logger import logger


class MultiOscillatorConfluence(BaseStrategy):
    """
    MultiOscillatorConfluence - Multiple oscillators align for high-probability setup
    
    Category: hybrid
    Indicators: rsi, cci, stochastic, atr
    """

    def __init__(self, config: StrategyConfig = None):
        """Initialize MultiOscillatorConfluence strategy."""
        super().__init__(config)
        
        # OPTIMIZABLE PARAMETERS
        self.rsi_period = self.config.get("rsi_period", 14)
        self.rsi_oversold = self.config.get("rsi_oversold", 30)
        self.rsi_overbought = self.config.get("rsi_overbought", 70)
        self.cci_period = self.config.get("cci_period", 20)
        self.cci_oversold = self.config.get("cci_oversold", -100)
        self.cci_overbought = self.config.get("cci_overbought", 100)
        self.stoch_k = self.config.get("stoch_k", 14)
        self.stoch_d = self.config.get("stoch_d", 3)
        self.sl_atr_mult = self.config.get("sl_atr_mult", 2.0)
        self.tp_rr_mult = self.config.get("tp_rr_mult", 2.5)

    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        return ['rsi', 'cci', 'stochastic', 'atr']
    
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
            
            # Get oscillator values
            rsi = r.get("rsi", 50)
            cci = r.get("cci", 0)
            stoch_k_val = r.get("stoch_k", 50)
            atr = r.get("atr", close * 0.02)
            
            if pos is None:
                # ? USE parameters for oversold/overbought levels
                # Count oversold signals (using parameters!)
                oversold_count = sum([
                    rsi < self.rsi_oversold,
                    cci < self.cci_oversold,
                    stoch_k_val < 20  # Stochastic oversold threshold
                ])
                
                # Count overbought signals
                overbought_count = sum([
                    rsi > self.rsi_overbought,
                    cci > self.cci_overbought,
                    stoch_k_val > 80  # Stochastic overbought threshold
                ])
                
                # LONG: At least 2 out of 3 oscillators oversold (reversal signal)
                if oversold_count >= 2:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(
                        SignalType.LONG, 
                        r["timestamp"], 
                        close, 
                        oversold_count / 3.0,  # Confidence based on alignment
                        sl, 
                        tp, 
                        {
                            "rsi": rsi,
                            "cci": cci,
                            "stoch_k": stoch_k_val,
                            "oversold_signals": oversold_count,
                            "rsi_oversold": self.rsi_oversold,
                            "cci_oversold": self.cci_oversold
                        }
                    ))
                    pos = "LONG"
                
                # SHORT: At least 2 out of 3 oscillators overbought (reversal signal)
                elif overbought_count >= 2:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    signals.append(Signal(
                        SignalType.SHORT, 
                        r["timestamp"], 
                        close, 
                        overbought_count / 3.0,
                        sl, 
                        tp, 
                        {
                            "rsi": rsi,
                            "cci": cci,
                            "stoch_k": stoch_k_val,
                            "overbought_signals": overbought_count,
                            "rsi_overbought": self.rsi_overbought,
                            "cci_overbought": self.cci_overbought
                        }
                    ))
                    pos = "SHORT"
            
            # Exit when oscillators reach opposite extreme
            elif pos == "LONG":
                # ? USE overbought parameters for exit
                overbought_count = sum([
                    rsi > self.rsi_overbought,
                    cci > self.cci_overbought,
                    stoch_k_val > 80
                ])
                
                if overbought_count >= 2:
                    signals.append(Signal(
                        SignalType.CLOSE_LONG, 
                        r["timestamp"], 
                        close, 
                        metadata={
                            "reason": "Oscillators overbought", 
                            "overbought_signals": overbought_count
                        }
                    ))
                    pos = None
            
            elif pos == "SHORT":
                # ? USE oversold parameters for exit
                oversold_count = sum([
                    rsi < self.rsi_oversold,
                    cci < self.cci_oversold,
                    stoch_k_val < 20
                ])
                
                if oversold_count >= 2:
                    signals.append(Signal(
                        SignalType.CLOSE_SHORT, 
                        r["timestamp"], 
                        close, 
                        metadata={
                            "reason": "Oscillators oversold", 
                            "oversold_signals": oversold_count
                        }
                    ))
                    pos = None
                    
        logger.info(f"MultiOscillatorConfluence: {len(signals)} signals")
        return signals


__all__ = ["MultiOscillatorConfluence"]
