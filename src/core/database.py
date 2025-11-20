"""
Database module for market data storage and retrieval.

Uses SQLite for efficient storage of OHLCV data with async support via aiosqlite.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple

import aiosqlite
import pandas as pd

from .logger import logger


class DatabaseManager:
    """Manages SQLite database connections and operations."""

    def __init__(self, base_path: Path = Path("data/market")):
        """
        Initialize database manager.

        Args:
            base_path: Base directory for database files
        """
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_db_path(self, exchange: str, symbol: str, timeframe: str) -> Path:
        """
        Generate database path for a specific symbol and timeframe.

        Args:
            exchange: Exchange name (e.g., 'binance')
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Timeframe (e.g., '5m', '1h')

        Returns:
            Path to database file
        """
        symbol_safe = symbol.replace("/", "_").replace(":", "_")
        db_dir = self.base_path / exchange
        db_dir.mkdir(parents=True, exist_ok=True)
        return db_dir / f"{symbol_safe}_{timeframe}.db"

    @staticmethod
    def get_table_name(timeframe: str) -> str:
        """
        Get table name for timeframe.

        Args:
            timeframe: Timeframe string

        Returns:
            Normalized table name
        """
        normalized = (
            timeframe.replace("m", "min")
            .replace("h", "hr")
            .replace("d", "day")
        )
        return f"candles_{normalized}"

    async def init_database(
        self,
        exchange: str,
        symbol: str,
        timeframe: str,
    ) -> None:
        """
        Initialize database with required tables.

        Args:
            exchange: Exchange name
            symbol: Trading pair
            timeframe: Timeframe
        """
        db_path = self.get_db_path(exchange, symbol, timeframe)
        table_name = self.get_table_name(timeframe)

        async with aiosqlite.connect(db_path) as conn:
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    timestamp INTEGER PRIMARY KEY,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL
                )
            """)

            # Create index on timestamp for faster queries
            await conn.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{table_name}_timestamp
                ON {table_name}(timestamp)
            """)

            await conn.commit()

        logger.info(f"Database initialized: {db_path}")

    async def insert_candles(
        self,
        exchange: str,
        symbol: str,
        timeframe: str,
        candles: pd.DataFrame,
    ) -> int:
        """
        Insert OHLCV candles into database.

        Args:
            exchange: Exchange name
            symbol: Trading pair
            timeframe: Timeframe
            candles: DataFrame with columns [timestamp, open, high, low, close, volume]

        Returns:
            Number of rows inserted
        """
        await self.init_database(exchange, symbol, timeframe)

        db_path = self.get_db_path(exchange, symbol, timeframe)
        table_name = self.get_table_name(timeframe)

        # Convert timestamp to Unix milliseconds if needed
        if candles["timestamp"].dtype == "datetime64[ns]":
            candles = candles.copy()
            candles["timestamp"] = (
                candles["timestamp"].astype("int64") // 10**6
            )

        async with aiosqlite.connect(db_path) as conn:
            # Use INSERT OR REPLACE to handle duplicates
            await conn.executemany(
                f"""
                INSERT OR REPLACE INTO {table_name}
                (timestamp, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                candles[["timestamp", "open", "high", "low", "close", "volume"]].values.tolist(),
            )
            await conn.commit()

        logger.info(f"Inserted {len(candles)} candles into {db_path}")
        return len(candles)

    async def load_candles(
        self,
        exchange: str,
        symbol: str,
        timeframe: str,
        start_ts: Optional[int] = None,
        end_ts: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Load candles from database.

        Args:
            exchange: Exchange name
            symbol: Trading pair
            timeframe: Timeframe
            start_ts: Start timestamp (Unix ms), optional
            end_ts: End timestamp (Unix ms), optional
            limit: Maximum number of rows to return

        Returns:
            DataFrame with OHLCV data
        """
        db_path = self.get_db_path(exchange, symbol, timeframe)
        table_name = self.get_table_name(timeframe)

        if not db_path.exists():
            logger.warning(f"Database not found: {db_path}")
            return pd.DataFrame(
                columns=["timestamp", "open", "high", "low", "close", "volume"]
            )

        # Build query
        query = f"SELECT * FROM {table_name}"
        conditions = []
        params = []

        if start_ts is not None:
            conditions.append("timestamp >= ?")
            params.append(start_ts)

        if end_ts is not None:
            conditions.append("timestamp <= ?")
            params.append(end_ts)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY timestamp ASC"

        if limit is not None:
            query += f" LIMIT {limit}"

        async with aiosqlite.connect(db_path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(query, params) as cursor:
                rows = await cursor.fetchall()

        if not rows:
            return pd.DataFrame(
                columns=["timestamp", "open", "high", "low", "close", "volume"]
            )

        df = pd.DataFrame([dict(row) for row in rows])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        logger.info(f"Loaded {len(df)} candles from {db_path}")
        return df

    async def get_data_range(
        self,
        exchange: str,
        symbol: str,
        timeframe: str,
    ) -> Optional[Tuple[datetime, datetime]]:
        """
        Get the date range of available data.

        Args:
            exchange: Exchange name
            symbol: Trading pair
            timeframe: Timeframe

        Returns:
            Tuple of (start_date, end_date) or None if no data
        """
        db_path = self.get_db_path(exchange, symbol, timeframe)
        table_name = self.get_table_name(timeframe)

        if not db_path.exists():
            return None

        async with aiosqlite.connect(db_path) as conn:
            async with conn.execute(
                f"SELECT MIN(timestamp), MAX(timestamp) FROM {table_name}"
            ) as cursor:
                row = await cursor.fetchone()

        if row and row[0] and row[1]:
            start = datetime.fromtimestamp(row[0] / 1000)
            end = datetime.fromtimestamp(row[1] / 1000)
            return (start, end)

        return None


__all__ = ["DatabaseManager"]
