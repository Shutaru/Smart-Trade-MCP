"""Market data tools for fetching and processing OHLCV data."""

from datetime import datetime
from typing import Optional, Dict, Any

import pandas as pd

from ...core.config import settings
from ...core.logger import logger
from ...core.data_manager import DataManager
from ...core.indicators import calculate_all_indicators


# Global data manager instance
_data_manager: Optional[DataManager] = None


async def get_data_manager() -> DataManager:
    """Get or create global data manager instance."""
    global _data_manager
    if _data_manager is None:
        _data_manager = DataManager()
    return _data_manager


async def get_market_data(
    symbol: str,
    timeframe: str,
    limit: int = 500,
    since: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Fetch OHLCV market data from exchange.

    Args:
        symbol: Trading pair (e.g., 'BTC/USDT')
        timeframe: Timeframe (e.g., '1m', '5m', '1h', '1d')
        limit: Number of candles to fetch
        since: Optional start date (YYYY-MM-DD)

    Returns:
        Dictionary containing OHLCV data and metadata
    """
    logger.info(f"Fetching market data: {symbol} {timeframe} (limit={limit})")

    try:
        # Get data manager
        dm = await get_data_manager()

        # Parse since date if provided
        since_dt = None
        if since:
            since_dt = datetime.fromisoformat(since)

        # Fetch data
        df = await dm.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            since=since_dt,
            limit=limit,
        )

        if df.empty:
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "candles": 0,
                "data": [],
                "error": "No data available",
            }

        logger.info(f"Fetched {len(df)} candles for {symbol}")

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "candles": len(df),
            "start_date": str(df["timestamp"].iloc[0]),
            "end_date": str(df["timestamp"].iloc[-1]),
            "latest_close": float(df["close"].iloc[-1]),
            "data": df.tail(min(100, len(df))).to_dict(orient="records"),  # Last 100 rows
        }

    except Exception as e:
        logger.error(f"Error fetching market data: {e}", exc_info=True)
        raise


async def calculate_indicators(
    symbol: str,
    indicators: list[str],
    timeframe: str,
    limit: int = 500,
) -> Dict[str, Any]:
    """
    Calculate technical indicators on market data.

    Args:
        symbol: Trading pair
        indicators: List of indicator names (e.g., ['rsi', 'macd', 'ema'])
        timeframe: Timeframe for calculation
        limit: Number of candles to use

    Returns:
        Dictionary containing indicator values
    """
    logger.info(f"Calculating indicators for {symbol}: {indicators}")

    try:
        # Fetch market data
        market_data = await get_market_data(symbol, timeframe, limit)
        
        if market_data.get("candles", 0) == 0:
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "indicators": indicators,
                "error": "No market data available",
                "data": [],
            }

        # Get full dataframe
        dm = await get_data_manager()
        df = await dm.fetch_ohlcv(symbol, timeframe, limit=limit)

        # Calculate indicators
        df_with_indicators = calculate_all_indicators(df, indicators)

        logger.info(f"Calculated {len(indicators)} indicators")

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "indicators": indicators,
            "candles": len(df_with_indicators),
            "data": df_with_indicators.tail(100).to_dict(orient="records"),  # Last 100 rows
        }

    except Exception as e:
        logger.error(f"Error calculating indicators: {e}", exc_info=True)
        raise


__all__ = ["get_market_data", "calculate_indicators"]
