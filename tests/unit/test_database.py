"""Unit tests for database manager."""

import asyncio
from datetime import datetime
from pathlib import Path
import tempfile

import pandas as pd
import pytest

from src.core.database import DatabaseManager


@pytest.fixture
def temp_db_path():
    """Create temporary directory for test databases."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def db_manager(temp_db_path):
    """Create database manager with temp path."""
    return DatabaseManager(base_path=temp_db_path)


@pytest.fixture
def sample_candles():
    """Sample OHLCV data."""
    data = {
        "timestamp": pd.date_range("2024-01-01", periods=10, freq="5min"),
        "open": [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0],
        "high": [102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 111.0],
        "low": [99.0, 100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0],
        "close": [101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0],
        "volume": [1000.0] * 10,
    }
    return pd.DataFrame(data)


class TestDatabaseManager:
    """Test suite for DatabaseManager."""

    def test_get_db_path(self, db_manager):
        """Test database path generation."""
        path = db_manager.get_db_path("binance", "BTC/USDT", "5m")
        
        assert path.parent.name == "binance"
        assert "BTC_USDT_5m.db" in str(path)

    def test_get_table_name(self):
        """Test table name normalization."""
        assert DatabaseManager.get_table_name("5m") == "candles_5min"
        assert DatabaseManager.get_table_name("1h") == "candles_1hr"
        assert DatabaseManager.get_table_name("1d") == "candles_1day"

    @pytest.mark.asyncio
    async def test_init_database(self, db_manager):
        """Test database initialization."""
        await db_manager.init_database("binance", "BTC/USDT", "5m")
        
        db_path = db_manager.get_db_path("binance", "BTC/USDT", "5m")
        assert db_path.exists()

    @pytest.mark.asyncio
    async def test_insert_and_load_candles(self, db_manager, sample_candles):
        """Test inserting and loading candles."""
        # Insert
        count = await db_manager.insert_candles(
            "binance", "BTC/USDT", "5m", sample_candles
        )
        assert count == len(sample_candles)

        # Load
        loaded = await db_manager.load_candles("binance", "BTC/USDT", "5m")
        
        assert len(loaded) == len(sample_candles)
        assert list(loaded.columns) == ["timestamp", "open", "high", "low", "close", "volume"]
        assert loaded["close"].iloc[0] == 101.0

    @pytest.mark.asyncio
    async def test_load_with_limit(self, db_manager, sample_candles):
        """Test loading with limit."""
        await db_manager.insert_candles("binance", "BTC/USDT", "5m", sample_candles)
        
        loaded = await db_manager.load_candles("binance", "BTC/USDT", "5m", limit=5)
        assert len(loaded) == 5

    @pytest.mark.asyncio
    async def test_load_nonexistent_db(self, db_manager):
        """Test loading from non-existent database."""
        loaded = await db_manager.load_candles("binance", "ETH/USDT", "1h")
        
        assert loaded.empty
        assert list(loaded.columns) == ["timestamp", "open", "high", "low", "close", "volume"]

    @pytest.mark.asyncio
    async def test_get_data_range(self, db_manager, sample_candles):
        """Test getting data range."""
        await db_manager.insert_candles("binance", "BTC/USDT", "5m", sample_candles)
        
        data_range = await db_manager.get_data_range("binance", "BTC/USDT", "5m")
        
        assert data_range is not None
        start, end = data_range
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert start < end

    @pytest.mark.asyncio
    async def test_duplicate_insert(self, db_manager, sample_candles):
        """Test that duplicate inserts are handled (REPLACE)."""
        # Insert first time
        await db_manager.insert_candles("binance", "BTC/USDT", "5m", sample_candles)
        
        # Insert again (should replace)
        await db_manager.insert_candles("binance", "BTC/USDT", "5m", sample_candles)
        
        # Should still have same number of rows
        loaded = await db_manager.load_candles("binance", "BTC/USDT", "5m")
        assert len(loaded) == len(sample_candles)
