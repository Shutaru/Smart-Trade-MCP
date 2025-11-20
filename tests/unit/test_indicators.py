"""Unit tests for technical indicators."""

import numpy as np
import pytest

from src.core.indicators import (
    ema,
    rsi,
    macd,
    bollinger_bands,
    atr,
    adx,
)


class TestIndicators:
    """Test suite for technical indicators."""

    @pytest.fixture
    def sample_close_data(self):
        """Sample close price data."""
        return np.array([
            100, 102, 101, 103, 105, 104, 106, 108, 107, 109,
            111, 110, 112, 114, 113, 115, 117, 116, 118, 120,
        ])

    @pytest.fixture
    def sample_ohlc_data(self):
        """Sample OHLC data."""
        close = np.array([100, 102, 101, 103, 105, 104, 106, 108, 107, 109])
        high = close + 2
        low = close - 2
        return high, low, close

    def test_ema_calculation(self, sample_close_data):
        """Test EMA calculation."""
        result = ema(sample_close_data, period=10)

        assert len(result) == len(sample_close_data)
        assert not np.isnan(result).any()
        assert result[0] == sample_close_data[0]  # First value should match

    def test_rsi_calculation(self, sample_close_data):
        """Test RSI calculation."""
        result = rsi(sample_close_data, period=14)

        assert len(result) == len(sample_close_data)
        assert not np.isnan(result).any()
        assert (result >= 0).all()
        assert (result <= 100).all()

    def test_macd_calculation(self, sample_close_data):
        """Test MACD calculation."""
        macd_line, signal_line, histogram = macd(sample_close_data)

        assert len(macd_line) == len(sample_close_data)
        assert len(signal_line) == len(sample_close_data)
        assert len(histogram) == len(sample_close_data)
        
        # Histogram should be MACD - Signal
        np.testing.assert_array_almost_equal(
            histogram,
            macd_line - signal_line,
        )

    def test_bollinger_bands_calculation(self, sample_close_data):
        """Test Bollinger Bands calculation."""
        upper, middle, lower = bollinger_bands(sample_close_data, period=10, std_dev=2.0)

        assert len(upper) == len(sample_close_data)
        assert len(middle) == len(sample_close_data)
        assert len(lower) == len(sample_close_data)

        # Upper should be > Middle > Lower
        assert (upper >= middle).all()
        assert (middle >= lower).all()

    def test_atr_calculation(self, sample_ohlc_data):
        """Test ATR calculation."""
        high, low, close = sample_ohlc_data
        result = atr(high, low, close, period=14)

        assert len(result) == len(close)
        assert not np.isnan(result).any()
        assert (result >= 0).all()  # ATR should always be positive

    def test_adx_calculation(self, sample_ohlc_data):
        """Test ADX calculation."""
        high, low, close = sample_ohlc_data
        result = adx(high, low, close, period=14)

        assert len(result) == len(close)
        assert not np.isnan(result).any()
        assert (result >= 0).all()
        assert (result <= 100).all()

    def test_ema_with_period_1(self, sample_close_data):
        """Test EMA with period=1 returns original data."""
        result = ema(sample_close_data, period=1)
        np.testing.assert_array_almost_equal(result, sample_close_data)

    def test_indicators_with_list_input(self):
        """Test that indicators work with list input."""
        data = [100, 102, 104, 106, 108, 110]
        
        result = rsi(data, period=3)
        assert isinstance(result, np.ndarray)
        assert len(result) == len(data)
