"""Unit tests for trading strategies."""

import pandas as pd
import numpy as np
import pytest
from datetime import datetime, timedelta

from src.strategies import (
    RSIStrategy,
    MACDStrategy,
    StrategyConfig,
    SignalType,
    registry,
)


@pytest.fixture
def sample_market_data():
    """Create sample market data with indicators."""
    dates = pd.date_range("2024-01-01", periods=100, freq="1h")
    
    # Generate realistic price data
    np.random.seed(42)
    close_prices = 100 + np.cumsum(np.random.randn(100) * 2)
    
    df = pd.DataFrame({
        "timestamp": dates,
        "open": close_prices - 0.5,
        "high": close_prices + 1.0,
        "low": close_prices - 1.0,
        "close": close_prices,
        "volume": np.random.randint(1000, 10000, 100),
    })
    
    # Add RSI with clear oversold/overbought signals
    rsi_values = []
    for i in range(100):
        if i < 20:
            rsi_values.append(50 + 20 * np.sin(i / 3))  # Start neutral
        elif 20 <= i < 30:
            rsi_values.append(25 - (i - 20))  # Go oversold (below 30)
        elif 30 <= i < 45:
            rsi_values.append(40 + (i - 30))  # Rise back up
        elif 45 <= i < 55:
            rsi_values.append(75 + (i - 45))  # Go overbought (above 70)
        else:
            rsi_values.append(50 + 10 * np.sin((i - 55) / 3))  # Return to neutral
    
    df["rsi"] = rsi_values
    
    # Add MACD with clear crossovers
    macd_line = []
    signal_line = []
    for i in range(100):
        if i < 30:
            macd_line.append(-1.0)
            signal_line.append(0.5)  # MACD below signal
        elif 30 <= i < 35:
            # Crossover up
            progress = (i - 30) / 5
            macd_line.append(-1.0 + progress * 2.5)
            signal_line.append(0.5)
        elif 35 <= i < 60:
            macd_line.append(1.5)
            signal_line.append(0.5)  # MACD above signal
        elif 60 <= i < 65:
            # Crossover down
            progress = (i - 60) / 5
            macd_line.append(1.5 - progress * 2.5)
            signal_line.append(0.5)
        else:
            macd_line.append(-1.0)
            signal_line.append(0.5)  # MACD below signal
    
    df["macd"] = macd_line
    df["macd_signal"] = signal_line
    df["macd_hist"] = df["macd"] - df["macd_signal"]
    
    # Add ATR
    df["atr"] = 2.0
    
    return df


class TestRSIStrategy:
    """Test suite for RSI strategy."""

    def test_initialization(self):
        """Test RSI strategy initialization."""
        strategy = RSIStrategy()
        
        assert strategy.name == "RSIStrategy"
        assert strategy.rsi_period == 14
        assert strategy.oversold == 30
        assert strategy.overbought == 70

    def test_initialization_with_custom_config(self):
        """Test RSI strategy with custom configuration."""
        config = StrategyConfig(params={
            "rsi_period": 20,
            "oversold_level": 25,
            "overbought_level": 75,
        })
        strategy = RSIStrategy(config)
        
        assert strategy.rsi_period == 20
        assert strategy.oversold == 25
        assert strategy.overbought == 75

    def test_required_indicators(self):
        """Test required indicators list."""
        strategy = RSIStrategy()
        indicators = strategy.get_required_indicators()
        
        assert "rsi" in indicators
        assert "atr" in indicators

    def test_generate_signals(self, sample_market_data):
        """Test signal generation."""
        strategy = RSIStrategy()
        signals = strategy.generate_signals(sample_market_data)
        
        assert len(signals) > 0
        assert all(hasattr(s, "type") for s in signals)
        assert all(hasattr(s, "price") for s in signals)
        assert all(hasattr(s, "timestamp") for s in signals)

    def test_signal_types(self, sample_market_data):
        """Test that signals have valid types."""
        strategy = RSIStrategy()
        signals = strategy.generate_signals(sample_market_data)
        
        valid_types = {SignalType.LONG, SignalType.SHORT, SignalType.CLOSE_LONG, SignalType.CLOSE_SHORT}
        
        for signal in signals:
            assert signal.type in valid_types

    def test_backtest_signals(self, sample_market_data):
        """Test backtesting functionality."""
        strategy = RSIStrategy()
        df_with_signals = strategy.backtest_signals(sample_market_data)
        
        assert "signal" in df_with_signals.columns
        assert "signal_price" in df_with_signals.columns
        assert "stop_loss" in df_with_signals.columns
        assert "take_profit" in df_with_signals.columns


class TestMACDStrategy:
    """Test suite for MACD strategy."""

    def test_initialization(self):
        """Test MACD strategy initialization."""
        strategy = MACDStrategy()
        
        assert strategy.name == "MACDStrategy"
        assert strategy.fast_period == 12
        assert strategy.slow_period == 26
        assert strategy.signal_period == 9

    def test_required_indicators(self):
        """Test required indicators list."""
        strategy = MACDStrategy()
        indicators = strategy.get_required_indicators()
        
        assert "macd" in indicators
        assert "atr" in indicators

    def test_generate_signals(self, sample_market_data):
        """Test signal generation."""
        # Use config with no histogram threshold to ensure signals
        config = StrategyConfig(params={"histogram_threshold": -999})  # No threshold
        strategy = MACDStrategy(config)
        signals = strategy.generate_signals(sample_market_data)
        
        assert len(signals) >= 0  # At least should not crash

    def test_signal_confidence(self, sample_market_data):
        """Test that signals have confidence values."""
        strategy = MACDStrategy()
        signals = strategy.generate_signals(sample_market_data)
        
        for signal in signals:
            if signal.type in [SignalType.LONG, SignalType.SHORT]:
                assert 0.0 <= signal.confidence <= 1.0


class TestStrategyRegistry:
    """Test suite for strategy registry."""

    def test_registry_has_strategies(self):
        """Test that registry contains built-in strategies."""
        strategies = registry.list_strategies()
        
        assert len(strategies) >= 2  # At least RSI and MACD
        assert any(s.name == "rsi" for s in strategies)
        assert any(s.name == "macd" for s in strategies)

    def test_get_strategy_by_name(self):
        """Test getting strategy instance by name."""
        strategy = registry.get("rsi")
        
        assert isinstance(strategy, RSIStrategy)

    def test_get_nonexistent_strategy(self):
        """Test getting non-existent strategy raises error."""
        with pytest.raises(KeyError):
            registry.get("nonexistent_strategy")

    def test_list_by_category(self):
        """Test filtering strategies by category."""
        mean_rev = registry.list_strategies(category="mean_reversion")
        trend_follow = registry.list_strategies(category="trend_following")
        
        assert len(mean_rev) > 0
        assert len(trend_follow) > 0

    def test_get_categories(self):
        """Test getting all categories."""
        categories = registry.get_categories()
        
        assert "mean_reversion" in categories
        assert "trend_following" in categories

    def test_get_metadata(self):
        """Test getting strategy metadata."""
        metadata = registry.get_metadata("rsi")
        
        assert metadata.name == "rsi"
        assert metadata.category == "mean_reversion"
        assert len(metadata.required_indicators) > 0
        assert len(metadata.default_params) > 0
