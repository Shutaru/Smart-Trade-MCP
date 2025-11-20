"""Unit tests for new indicators."""

import numpy as np
import pandas as pd
import pytest

from src.core.indicators import (
    cci,
    donchian_channels,
    keltner_channels,
    mfi,
    obv,
    stochastic,
    supertrend,
    vwap,
    sma,
)


@pytest.fixture
def sample_ohlcv_data():
    """Sample OHLCV data for testing."""
    np.random.seed(42)
    n = 100
    close = 100 + np.cumsum(np.random.randn(n) * 2)
    high = close + np.abs(np.random.randn(n))
    low = close - np.abs(np.random.randn(n))
    volume = np.random.randint(1000, 10000, n)
    
    return high, low, close, volume


class TestNewIndicators:
    """Test suite for newly added indicators."""

    def test_sma(self):
        """Test Simple Moving Average."""
        data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        result = sma(data, period=3)
        
        assert len(result) == len(data)
        assert not np.isnan(result).any()

    def test_cci(self, sample_ohlcv_data):
        """Test Commodity Channel Index."""
        high, low, close, _ = sample_ohlcv_data
        result = cci(high, low, close, period=20)
        
        assert len(result) == len(close)
        assert not np.isnan(result).any()

    def test_donchian_channels(self, sample_ohlcv_data):
        """Test Donchian Channels."""
        high, low, _, _ = sample_ohlcv_data
        upper, middle, lower = donchian_channels(high, low, period=20)
        
        assert len(upper) == len(high)
        assert len(middle) == len(high)
        assert len(lower) == len(high)
        
        # Upper should be >= Middle >= Lower
        assert (upper >= middle).all()
        assert (middle >= lower).all()

    def test_keltner_channels(self, sample_ohlcv_data):
        """Test Keltner Channels."""
        high, low, close, _ = sample_ohlcv_data
        upper, middle, lower = keltner_channels(high, low, close, period=20)
        
        assert len(upper) == len(close)
        assert len(middle) == len(close)
        assert len(lower) == len(close)
        
        # Upper should be >= Middle >= Lower
        assert (upper >= middle).all()
        assert (middle >= lower).all()

    def test_mfi(self, sample_ohlcv_data):
        """Test Money Flow Index."""
        high, low, close, volume = sample_ohlcv_data
        result = mfi(high, low, close, volume, period=14)
        
        assert len(result) == len(close)
        assert not np.isnan(result).any()
        # MFI should be between 0 and 100
        assert (result >= 0).all()
        assert (result <= 100).all()

    def test_obv(self, sample_ohlcv_data):
        """Test On-Balance Volume."""
        _, _, close, volume = sample_ohlcv_data
        result = obv(close, volume)
        
        assert len(result) == len(close)
        assert not np.isnan(result).any()

    def test_stochastic(self, sample_ohlcv_data):
        """Test Stochastic Oscillator."""
        high, low, close, _ = sample_ohlcv_data
        k_values, d_values = stochastic(high, low, close, k_period=14, d_period=3)
        
        assert len(k_values) == len(close)
        assert len(d_values) == len(close)
        
        # Stochastic should be between 0 and 100
        assert (k_values >= 0).all()
        assert (k_values <= 100).all()
        assert (d_values >= 0).all()
        assert (d_values <= 100).all()

    def test_supertrend(self, sample_ohlcv_data):
        """Test SuperTrend indicator."""
        high, low, close, _ = sample_ohlcv_data
        st_values, trend = supertrend(high, low, close, period=10, multiplier=3.0)
        
        assert len(st_values) == len(close)
        assert len(trend) == len(close)
        
        # Trend should be 1 or -1
        assert set(np.unique(trend)).issubset({-1, 1})

    def test_vwap(self, sample_ohlcv_data):
        """Test VWAP."""
        high, low, close, volume = sample_ohlcv_data
        result = vwap(high, low, close, volume)
        
        assert len(result) == len(close)
        assert not np.isnan(result).any()
        assert (result > 0).all()

    def test_indicators_with_list_input(self):
        """Test that new indicators work with list input."""
        high = [102, 104, 106, 108, 110]
        low = [98, 100, 102, 104, 106]
        close = [100, 102, 104, 106, 108]
        volume = [1000, 1100, 1200, 1300, 1400]
        
        # Should not raise errors
        _ = cci(high, low, close, period=3)
        _ = mfi(high, low, close, volume, period=3)
        _ = obv(close, volume)
        _ = vwap(high, low, close, volume)
