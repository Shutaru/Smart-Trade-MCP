# -*- coding: utf-8 -*-
"""
Volume Shooter Strategy

High-volume breakout strategy with momentum confirmation.
Originally from TradingView: [SB2018] VOLUME-SHOOTER

Logic:
- LONG: Volume spike (> FACTOR * SMA) + 2-period price rise
- SHORT: Volume spike (> FACTOR * SMA) + 2-period price fall
- Optional SAR direction filter for trend confirmation
- Fixed % take profit and stop loss

Parameters:
- volume_factor: Multiplier for volume SMA (default: 2)
- volume_period: SMA period for volume (default: 50)
- take_profit_pct: Take profit percentage (default: 95%)
- stop_loss_pct: Stop loss percentage (default: 10%)
- use_sar_filter: Use SAR for trend direction (default: False)
- sar_acceleration: SAR acceleration factor (default: 0.02)
- sar_maximum: SAR maximum value (default: 0.2)
"""

from typing import List
import pandas as pd
import numpy as np

from .base import BaseStrategy, Signal, SignalType, StrategyConfig
from ..core.logger import logger


class VolumeShooterStrategy(BaseStrategy):
    """
    Volume Shooter Strategy - High-volume momentum breakout.
    
    Category: momentum
    Indicators: volume, sma, sar (optional), atr
    
    Entry:
    - LONG: Volume > FACTOR * SMA(volume) AND close rising for 2 periods
    - SHORT: Volume > FACTOR * SMA(volume) AND close falling for 2 periods
    
    Exit:
    - Take Profit: +95% (default)
    - Stop Loss: -10% (default)
    """
    
    def __init__(self, config: StrategyConfig = None):
        """Initialize Volume Shooter strategy."""
        super().__init__(config)
        
        # Volume parameters
        self.volume_factor = self.config.get("volume_factor", 2.0)
        self.volume_period = self.config.get("volume_period", 50)
        
        # Exit parameters
        self.take_profit_pct = self.config.get("take_profit_pct", 95.0)
        self.stop_loss_pct = self.config.get("stop_loss_pct", 10.0)
        
        # Optional SAR filter
        self.use_sar_filter = self.config.get("use_sar_filter", False)
        self.sar_acceleration = self.config.get("sar_acceleration", 0.02)
        self.sar_maximum = self.config.get("sar_maximum", 0.2)
        
        # Direction enablers
        self.enable_longs = self.config.get("enable_longs", True)
        self.enable_shorts = self.config.get("enable_shorts", False)
    
    def get_required_indicators(self) -> List[str]:
        """Required indicators for this strategy."""
        indicators = ["atr"]
        
        if self.use_sar_filter:
            indicators.append("sar")
        
        return indicators
    
    def _calculate_volume_sma(self, df: pd.DataFrame) -> pd.Series:
        """Calculate SMA of volume"""
        return df['volume'].rolling(window=self.volume_period).mean()
    
    def _is_rising(self, series: pd.Series, periods: int = 2) -> pd.Series:
        """Check if series is rising for N periods"""
        return (series > series.shift(1)) & (series.shift(1) > series.shift(2))
    
    def _is_falling(self, series: pd.Series, periods: int = 2) -> pd.Series:
        """Check if series is falling for N periods"""
        return (series < series.shift(1)) & (series.shift(1) < series.shift(2))
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        Generate Volume Shooter signals.
        
        Args:
            df: DataFrame with OHLCV and indicators
            
        Returns:
            List of trading signals
        """
        signals = []
        
        # Calculate volume SMA
        volume_sma = self._calculate_volume_sma(df)
        volume_threshold = self.volume_factor * volume_sma
        
        # Volume spike condition
        volume_spike = df['volume'] > volume_threshold
        
        # Price momentum conditions
        rising = self._is_rising(df['close'], periods=2)
        falling = self._is_falling(df['close'], periods=2)
        
        # Track position
        position = None  # None, "LONG", or "SHORT"
        entry_price = None
        
        for i in range(2, len(df)):  # Start at 2 for 2-period lookback
            current_row = df.iloc[i]
            prev_row = df.iloc[i - 1]
            
            timestamp = current_row["timestamp"]
            price = current_row["close"]
            atr = current_row.get("atr", price * 0.02)
            
            # Entry conditions
            if self.use_sar_filter:
                # Use SAR for direction
                sar_value = current_row.get("sar", price)
                long_condition = price > sar_value
                short_condition = price < sar_value
            else:
                # Use volume + momentum
                long_condition = volume_spike.iloc[i] and rising.iloc[i]
                short_condition = volume_spike.iloc[i] and falling.iloc[i]
            
            # LONG ENTRY
            if position is None and long_condition and self.enable_longs:
                entry_price = price
                
                # Calculate exit levels
                stop_loss = entry_price * (1 - self.stop_loss_pct / 100)
                take_profit = entry_price * (1 + self.take_profit_pct / 100)
                
                signals.append(Signal(
                    type=SignalType.LONG,
                    timestamp=timestamp,
                    price=price,
                    confidence=min(1.0, (volume_spike.iloc[i] / volume_threshold.iloc[i] - 1) * 2),
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    metadata={
                        "volume": current_row["volume"],
                        "volume_sma": volume_sma.iloc[i],
                        "volume_factor": self.volume_factor,
                        "reason": "volume_spike_long",
                    },
                ))
                position = "LONG"
            
            # SHORT ENTRY
            elif position is None and short_condition and self.enable_shorts:
                entry_price = price
                
                # Calculate exit levels
                stop_loss = entry_price * (1 + self.stop_loss_pct / 100)
                take_profit = entry_price * (1 - self.take_profit_pct / 100)
                
                signals.append(Signal(
                    type=SignalType.SHORT,
                    timestamp=timestamp,
                    price=price,
                    confidence=min(1.0, (volume_spike.iloc[i] / volume_threshold.iloc[i] - 1) * 2),
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    metadata={
                        "volume": current_row["volume"],
                        "volume_sma": volume_sma.iloc[i],
                        "volume_factor": self.volume_factor,
                        "reason": "volume_spike_short",
                    },
                ))
                position = "SHORT"
            
            # EXIT LOGIC (handled by stop loss / take profit in backtest engine)
            # But we can add manual exit signals if needed
            
            # Note: In the original Pine Script, exits are handled by
            # strategy.close() when SL/TP is hit. Our backtest engine
            # handles this automatically via the SL/TP in the Signal.
        
        logger.info(f"VolumeShooterStrategy generated {len(signals)} signals")
        return signals


__all__ = ["VolumeShooterStrategy"]
