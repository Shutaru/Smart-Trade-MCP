"""
Base Strategy Class

Abstract base class for all trading strategies with common interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime

import pandas as pd
import numpy as np

from ..core.logger import logger


class SignalType(Enum):
    """Trading signal types."""
    
    LONG = "LONG"
    SHORT = "SHORT"
    CLOSE_LONG = "CLOSE_LONG"
    CLOSE_SHORT = "CLOSE_SHORT"
    HOLD = "HOLD"


@dataclass
class Signal:
    """Trading signal with metadata."""
    
    type: SignalType
    timestamp: datetime
    price: float
    confidence: float = 1.0  # 0.0 to 1.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary."""
        return {
            "type": self.type.value,
            "timestamp": str(self.timestamp),
            "price": self.price,
            "confidence": self.confidence,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "metadata": self.metadata,
        }


@dataclass
class StrategyConfig:
    """Strategy configuration parameters."""
    
    # Risk Management
    stop_loss_atr_mult: float = 2.0
    take_profit_rr_ratio: float = 2.0  # Risk:Reward ratio
    trailing_stop_atr_mult: float = 2.0
    
    # Position Sizing
    max_position_size: float = 0.1  # % of portfolio
    
    # Strategy-specific params
    params: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get parameter value."""
        return self.params.get(key, default)


class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies.
    
    All strategies must implement:
    - generate_signals(): Main signal generation logic
    - get_indicators(): Required indicators for the strategy
    """

    def __init__(self, config: Optional[StrategyConfig] = None):
        """
        Initialize strategy.

        Args:
            config: Strategy configuration
        """
        self.config = config or StrategyConfig()
        self.name = self.__class__.__name__
        logger.info(f"Strategy initialized: {self.name}")

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        Generate trading signals from market data.

        Args:
            df: DataFrame with OHLCV and indicator data

        Returns:
            List of Signal objects
        """
        pass

    @abstractmethod
    def get_required_indicators(self) -> List[str]:
        """
        Get list of required indicators for this strategy.

        Returns:
            List of indicator names (e.g., ['rsi', 'macd', 'ema'])
        """
        pass

    def calculate_exit_levels(
        self,
        signal_type: SignalType,
        entry_price: float,
        atr: float,
    ) -> tuple[float, float]:
        """
        Calculate stop loss and take profit levels.

        Args:
            signal_type: LONG or SHORT
            entry_price: Entry price
            atr: Average True Range value

        Returns:
            Tuple of (stop_loss, take_profit)
        """
        sl_mult = self.config.stop_loss_atr_mult
        tp_rr = self.config.take_profit_rr_ratio

        if signal_type == SignalType.LONG:
            stop_loss = entry_price - (sl_mult * atr)
            risk = entry_price - stop_loss
            take_profit = entry_price + (tp_rr * risk)
        elif signal_type == SignalType.SHORT:
            stop_loss = entry_price + (sl_mult * atr)
            risk = stop_loss - entry_price
            take_profit = entry_price - (tp_rr * risk)
        else:
            # For exit signals, no SL/TP needed
            return None, None

        return stop_loss, take_profit

    def validate_dataframe(self, df: pd.DataFrame) -> bool:
        """
        Validate that DataFrame has required columns.

        Args:
            df: DataFrame to validate

        Returns:
            True if valid, False otherwise
        """
        required_cols = ["timestamp", "open", "high", "low", "close", "volume"]
        
        for col in required_cols:
            if col not in df.columns:
                logger.error(f"Missing required column: {col}")
                return False

        # Check for required indicators
        # Map indicator names to actual column names
        indicator_columns_map = {
            "bollinger": ["bb_upper", "bb_middle", "bb_lower"],
            "keltner": ["keltner_upper", "keltner_middle", "keltner_lower"],
            "donchian": ["donchian_upper", "donchian_middle", "donchian_lower"],
            "macd": ["macd", "macd_signal", "macd_hist"],
            "stochastic": ["stoch_k", "stoch_d"],
            "ema": ["ema_12", "ema_26", "ema_50", "ema_200"],
            "sma": ["sma_20", "sma_50", "sma_200"],
            "rsi": ["rsi"],
            "atr": ["atr"],
            "adx": ["adx"],
            "cci": ["cci"],
            "mfi": ["mfi"],
            "obv": ["obv"],
            "supertrend": ["supertrend_trend", "supertrend_line"],
            "vwap": ["vwap"],
        }
        
        required_indicators = self.get_required_indicators()
        for indicator in required_indicators:
            indicator_lower = indicator.lower()
            
            # Check if this indicator maps to specific columns
            if indicator_lower in indicator_columns_map:
                columns_to_check = indicator_columns_map[indicator_lower]
                # Check if ANY of the columns exist (at least one)
                if not any(col in df.columns for col in columns_to_check):
                    logger.warning(f"Missing indicator '{indicator}' (looked for columns: {columns_to_check})")
            elif indicator not in df.columns:
                logger.warning(f"Missing indicator: {indicator}")

        return True

    def backtest_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Backtest strategy on historical data.

        Args:
            df: DataFrame with OHLCV and indicators

        Returns:
            DataFrame with signals added
        """
        if not self.validate_dataframe(df):
            raise ValueError("Invalid DataFrame")

        signals = self.generate_signals(df)
        
        # Add signals to dataframe
        df_copy = df.copy()
        df_copy["signal"] = SignalType.HOLD.value
        df_copy["signal_price"] = np.nan
        df_copy["stop_loss"] = np.nan
        df_copy["take_profit"] = np.nan

        for signal in signals:
            # Find matching timestamp
            mask = df_copy["timestamp"] == signal.timestamp
            if mask.any():
                idx = df_copy[mask].index[0]
                df_copy.loc[idx, "signal"] = signal.type.value
                df_copy.loc[idx, "signal_price"] = signal.price
                df_copy.loc[idx, "stop_loss"] = signal.stop_loss
                df_copy.loc[idx, "take_profit"] = signal.take_profit

        logger.info(f"Generated {len(signals)} signals for {self.name}")
        return df_copy

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.name}(config={self.config})"


__all__ = [
    "BaseStrategy",
    "Signal",
    "SignalType",
    "StrategyConfig",
]
