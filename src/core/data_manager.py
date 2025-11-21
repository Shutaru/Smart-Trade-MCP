"""
Data Manager for fetching and caching market data from exchanges.

Handles automatic data fetching with intelligent caching and retry logic.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import ccxt.async_support as ccxt
import pandas as pd

from .config import settings
from .database import DatabaseManager
from .logger import logger


class DataManager:
    """Manages market data fetching and caching."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize data manager.

        Args:
            db_manager: Optional database manager instance
        """
        self.db = db_manager or DatabaseManager()
        self._exchange_instances: Dict[str, ccxt.Exchange] = {}

    async def _get_exchange(self, exchange_name: str) -> ccxt.Exchange:
        """
        Get or create exchange instance.

        Args:
            exchange_name: Exchange name (e.g., 'binance')

        Returns:
            CCXT exchange instance
        """
        if exchange_name not in self._exchange_instances:
            exchange_class = getattr(ccxt, exchange_name)
            
            config = {
                "enableRateLimit": True,
                "options": {
                    "defaultType": "future" if "binance" in exchange_name else "swap"
                },
            }

            # Add API keys only if they are valid (not placeholders)
            if exchange_name == "binance" and settings.is_valid_api_key():
                config["apiKey"] = settings.binance_api_key
                config["secret"] = settings.binance_secret_key
                logger.info("Using authenticated Binance API")
            else:
                logger.info("Using public Binance API (no authentication)")

            exchange = exchange_class(config)
            await exchange.load_markets()
            
            self._exchange_instances[exchange_name] = exchange
            logger.info(f"Exchange initialized: {exchange_name}")

        return self._exchange_instances[exchange_name]

    async def close(self) -> None:
        """Close all exchange connections."""
        for exchange in self._exchange_instances.values():
            await exchange.close()
        self._exchange_instances.clear()
        logger.info("All exchange connections closed")

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        exchange: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 500,
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data from exchange with intelligent caching.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Timeframe (e.g., '5m', '1h', '1d')
            exchange: Exchange name (defaults to settings.exchange)
            since: Start date (optional)
            limit: Number of candles to fetch
            use_cache: Whether to use cached data

        Returns:
            DataFrame with OHLCV data
        """
        exchange = exchange or settings.exchange
        
        # Check cache first
        if use_cache:
            cached_data = await self._get_cached_data(
                exchange, symbol, timeframe, since, limit
            )
            if cached_data is not None and not cached_data.empty:
                logger.info(f"Using cached data for {symbol} {timeframe}")
                return cached_data

        # Fetch from exchange
        logger.info(f"Fetching {symbol} {timeframe} from {exchange}")
        
        exchange_instance = await self._get_exchange(exchange)
        
        since_ms = None
        if since:
            since_ms = int(since.timestamp() * 1000)

        try:
            ohlcv = await exchange_instance.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                since=since_ms,
                limit=limit,
            )
        except Exception as e:
            logger.error(f"Error fetching data from {exchange}: {e}")
            # Try to return cached data as fallback
            cached = await self.db.load_candles(exchange, symbol, timeframe, limit=limit)
            if not cached.empty:
                logger.warning("Returning cached data due to fetch error")
                return cached
            raise

        # Convert to DataFrame
        df = pd.DataFrame(
            ohlcv,
            columns=["timestamp", "open", "high", "low", "close", "volume"],
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        # Cache the data
        if use_cache and not df.empty:
            await self.db.insert_candles(exchange, symbol, timeframe, df)

        logger.info(f"Fetched {len(df)} candles for {symbol} {timeframe}")
        return df

    async def _get_cached_data(
        self,
        exchange: str,
        symbol: str,
        timeframe: str,
        since: Optional[datetime],
        limit: int,
    ) -> Optional[pd.DataFrame]:
        """
        Get cached data if available and fresh enough.

        Args:
            exchange: Exchange name
            symbol: Trading pair
            timeframe: Timeframe
            since: Start date
            limit: Number of candles

        Returns:
            Cached DataFrame or None
        """
        # Get available data range
        data_range = await self.db.get_data_range(exchange, symbol, timeframe)
        
        if not data_range:
            return None

        start_date, end_date = data_range

        # Check if cache is fresh (within last hour)
        if datetime.now() - end_date > timedelta(hours=1):
            logger.debug("Cache is stale, will fetch fresh data")
            return None

        # Load from cache
        start_ts = None
        if since:
            start_ts = int(since.timestamp() * 1000)

        return await self.db.load_candles(
            exchange, symbol, timeframe,
            start_ts=start_ts,
            limit=limit,
        )

    async def fetch_historical(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        exchange: Optional[str] = None,
        max_candles: Optional[int] = None,
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """
        Fetch historical data in chunks with rate limiting and pagination.
        
        Automatically handles CCXT limitations and fetches multiple years of data.
        Uses database cache to avoid redundant API calls.

        Args:
            symbol: Trading pair
            timeframe: Timeframe
            start_date: Start date
            end_date: End date (defaults to now)
            exchange: Exchange name
            max_candles: Maximum number of candles to fetch (None = unlimited)
            use_cache: Use cached data if available (default: True)

        Returns:
            DataFrame with historical OHLCV data
        """
        exchange = exchange or settings.exchange
        end_date = end_date or datetime.now()

        logger.info(
            f"Fetching historical data: {symbol} {timeframe} "
            f"from {start_date} to {end_date}"
        )

        # Check if we have complete cached data for this range
        if use_cache:
            cached_data = await self._check_complete_cached_range(
                exchange, symbol, timeframe, start_date, end_date
            )
            if cached_data is not None and len(cached_data) > 0:
                logger.info(f"? Using complete cached data: {len(cached_data)} candles")
                
                # Apply max_candles limit if specified
                if max_candles and len(cached_data) > max_candles:
                    cached_data = cached_data.tail(max_candles)
                
                return cached_data

        all_data = []
        current_since = start_date

        # Calculate timeframe duration
        tf_minutes = self._parse_timeframe_to_minutes(timeframe)
        chunk_size = 1000  # CCXT limit per request

        total_fetched = 0
        chunks_fetched = 0

        while current_since < end_date:
            # Check if we've hit max_candles limit
            if max_candles and total_fetched >= max_candles:
                logger.info(f"Reached max_candles limit: {max_candles}")
                break
            
            # Adjust chunk size if near limit
            if max_candles:
                remaining = max_candles - total_fetched
                chunk_size = min(chunk_size, remaining)
            
            # Fetch chunk (now uses cache!)
            try:
                df = await self.fetch_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    exchange=exchange,
                    since=current_since,
                    limit=chunk_size,
                    use_cache=use_cache,
                )
            except Exception as e:
                logger.error(f"Error fetching chunk: {e}")
                # Continue with what we have
                break

            if df.empty:
                logger.warning("Received empty data, stopping fetch")
                break

            all_data.append(df)
            total_fetched += len(df)
            chunks_fetched += 1

            # Progress logging (only every 10 chunks to avoid spam)
            if chunks_fetched % 10 == 0:
                logger.debug(f"Progress: {total_fetched} candles fetched ({chunks_fetched} chunks)")

            # Move to next chunk
            last_timestamp = df["timestamp"].iloc[-1]
            next_since = last_timestamp + timedelta(minutes=tf_minutes)
            
            # Prevent infinite loop if timestamp doesn't advance
            if next_since <= current_since:
                logger.warning("Timestamp not advancing, stopping")
                break
            
            current_since = next_since

            # Check if we've reached the end
            if current_since >= end_date:
                break

            # Rate limiting (respect exchange limits)
            await asyncio.sleep(0.1)  # Reduced from 0.5s for faster fetching

        if not all_data:
            return pd.DataFrame(
                columns=["timestamp", "open", "high", "low", "close", "volume"]
            )

        # Combine all chunks
        result = pd.concat(all_data, ignore_index=True)
        result = result.drop_duplicates(subset=["timestamp"]).sort_values("timestamp")

        # Filter to exact date range
        result = result[
            (result["timestamp"] >= start_date) &
            (result["timestamp"] <= end_date)
        ]

        # Cache the complete result
        if use_cache:
            await self.db.insert_candles(exchange, symbol, timeframe, result)

        logger.info(f"? Fetched {len(result)} total candles in {chunks_fetched} chunks")
        return result

    async def _check_complete_cached_range(
        self,
        exchange: str,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Optional[pd.DataFrame]:
        """
        Check if we have complete cached data for the requested range.
        
        Args:
            exchange: Exchange name
            symbol: Trading pair
            timeframe: Timeframe
            start_date: Requested start date
            end_date: Requested end date
            
        Returns:
            Cached DataFrame if complete range is available, None otherwise
        """
        # Get available data range from DB
        data_range = await self.db.get_data_range(exchange, symbol, timeframe)
        
        if not data_range:
            logger.debug("No cached data available")
            return None
        
        cached_start, cached_end = data_range
        
        # Check if cached range covers requested range
        if cached_start <= start_date and cached_end >= end_date:
            logger.debug(
                f"Cache covers full range: cached {cached_start} to {cached_end}, "
                f"requested {start_date} to {end_date}"
            )
            
            # Load data from cache
            start_ts = int(start_date.timestamp() * 1000)
            end_ts = int(end_date.timestamp() * 1000)
            
            df = await self.db.load_candles(
                exchange, symbol, timeframe,
                start_ts=start_ts,
                end_ts=end_ts,
            )
            
            return df
        else:
            logger.debug(
                f"Cache incomplete: cached {cached_start} to {cached_end}, "
                f"requested {start_date} to {end_date}"
            )
            return None

    @staticmethod
    def _parse_timeframe_to_minutes(timeframe: str) -> int:
        """
        Parse timeframe string to minutes.

        Args:
            timeframe: Timeframe string (e.g., '5m', '1h', '1d')

        Returns:
            Number of minutes
        """
        if timeframe.endswith("m"):
            return int(timeframe[:-1])
        elif timeframe.endswith("h"):
            return int(timeframe[:-1]) * 60
        elif timeframe.endswith("d"):
            return int(timeframe[:-1]) * 60 * 24
        else:
            raise ValueError(f"Unsupported timeframe: {timeframe}")


__all__ = ["DataManager"]
