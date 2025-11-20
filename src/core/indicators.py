"""
Technical Indicators Library

Efficient implementations of common technical indicators using NumPy.
All functions accept pandas Series or numpy arrays and return numpy arrays.
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple

ArrayLike = Union[np.ndarray, pd.Series, list]


def ema(arr: ArrayLike, period: int) -> np.ndarray:
    """
    Exponential Moving Average.

    Args:
        arr: Price array
        period: EMA period

    Returns:
        EMA values as numpy array
    """
    arr = np.asarray(arr, dtype=float)
    if period <= 1:
        return arr.copy()

    alpha = 2.0 / (period + 1.0)
    out = np.zeros_like(arr)
    out[0] = arr[0]

    for i in range(1, len(arr)):
        out[i] = alpha * arr[i] + (1 - alpha) * out[i - 1]

    return out


def rma(arr: ArrayLike, period: int) -> np.ndarray:
    """
    Running Moving Average (Wilder's smoothing).

    Args:
        arr: Price array
        period: RMA period

    Returns:
        RMA values as numpy array
    """
    arr = np.asarray(arr, dtype=float)
    out = np.zeros_like(arr)

    # Initialize first value
    start_idx = min(period - 1, len(arr) - 1)
    out[start_idx] = arr[:period].mean() if len(arr) >= period else arr.mean()

    alpha = 1.0 / max(period, 1)
    for i in range(period, len(arr)):
        out[i] = alpha * arr[i] + (1 - alpha) * out[i - 1]

    return out


def atr(high: ArrayLike, low: ArrayLike, close: ArrayLike, period: int = 14) -> np.ndarray:
    """
    Average True Range.

    Args:
        high: High prices
        low: Low prices
        close: Close prices
        period: ATR period

    Returns:
        ATR values as numpy array
    """
    high = np.asarray(high, dtype=float)
    low = np.asarray(low, dtype=float)
    close = np.asarray(close, dtype=float)

    # Calculate True Range
    tr = np.maximum(high[1:], close[:-1]) - np.minimum(low[1:], close[:-1])
    tr = np.insert(tr, 0, high[0] - low[0])

    return rma(tr, period)


def rsi(close: ArrayLike, period: int = 14) -> np.ndarray:
    """
    Relative Strength Index.

    Args:
        close: Close prices
        period: RSI period

    Returns:
        RSI values as numpy array (0-100)
    """
    close = np.asarray(close, dtype=float)
    diff = np.diff(close, prepend=close[0])

    gains = np.clip(diff, 0, None)
    losses = -np.clip(diff, None, 0)

    avg_gains = rma(gains, period)
    avg_losses = rma(losses, period)

    rs = avg_gains / (avg_losses + 1e-12)
    return 100.0 - (100.0 / (1.0 + rs))


def macd(
    close: ArrayLike,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    MACD (Moving Average Convergence Divergence).

    Args:
        close: Close prices
        fast: Fast EMA period
        slow: Slow EMA period
        signal: Signal line period

    Returns:
        Tuple of (macd_line, signal_line, histogram)
    """
    close = np.asarray(close, dtype=float)

    ema_fast = ema(close, fast)
    ema_slow = ema(close, slow)

    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def bollinger_bands(
    close: ArrayLike,
    period: int = 20,
    std_dev: float = 2.0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Bollinger Bands.

    Args:
        close: Close prices
        period: Period for moving average
        std_dev: Standard deviation multiplier

    Returns:
        Tuple of (upper_band, middle_band, lower_band)
    """
    close = np.asarray(close, dtype=float)

    # Calculate SMA
    middle = np.convolve(close, np.ones(period) / period, mode="same")

    # Calculate rolling standard deviation
    std = np.zeros_like(close)
    for i in range(len(close)):
        start = max(0, i - period + 1)
        std[i] = np.std(close[start : i + 1])

    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)

    return upper, middle, lower


def adx(high: ArrayLike, low: ArrayLike, close: ArrayLike, period: int = 14) -> np.ndarray:
    """
    Average Directional Index.

    Args:
        high: High prices
        low: Low prices
        close: Close prices
        period: ADX period

    Returns:
        ADX values as numpy array
    """
    high = np.asarray(high, dtype=float)
    low = np.asarray(low, dtype=float)
    close = np.asarray(close, dtype=float)

    # Calculate +DM and -DM
    up = high[1:] - high[:-1]
    down = low[:-1] - low[1:]

    plus_dm = np.where((up > down) & (up > 0), up, 0.0)
    minus_dm = np.where((down > up) & (down > 0), down, 0.0)

    # Calculate True Range
    tr = np.maximum(high[1:], close[:-1]) - np.minimum(low[1:], close[:-1])
    tr = np.insert(tr, 0, high[0] - low[0])

    # Calculate +DI and -DI
    atr_values = rma(tr, period)
    plus_di = 100 * rma(plus_dm, period) / (atr_values[1:] + 1e-12)
    minus_di = 100 * rma(minus_dm, period) / (atr_values[1:] + 1e-12)

    # Calculate DX
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-12)
    dx = np.insert(dx, 0, dx[0])

    # Calculate ADX
    adx_values = rma(dx, period)
    return np.concatenate([[adx_values[0]], adx_values])[: len(close)]


def calculate_all_indicators(df: pd.DataFrame, indicators: list[str]) -> pd.DataFrame:
    """
    Calculate multiple indicators on a DataFrame.

    Args:
        df: DataFrame with OHLCV data
        indicators: List of indicator names to calculate

    Returns:
        DataFrame with added indicator columns
    """
    df = df.copy()

    for indicator in indicators:
        indicator = indicator.lower()

        if indicator == "rsi":
            df["rsi"] = rsi(df["close"].values)

        elif indicator == "macd":
            macd_line, signal_line, histogram = macd(df["close"].values)
            df["macd"] = macd_line
            df["macd_signal"] = signal_line
            df["macd_hist"] = histogram

        elif indicator == "ema":
            df["ema_12"] = ema(df["close"].values, 12)
            df["ema_26"] = ema(df["close"].values, 26)

        elif indicator == "bollinger":
            upper, middle, lower = bollinger_bands(df["close"].values)
            df["bb_upper"] = upper
            df["bb_middle"] = middle
            df["bb_lower"] = lower

        elif indicator == "atr":
            df["atr"] = atr(df["high"].values, df["low"].values, df["close"].values)

        elif indicator == "adx":
            df["adx"] = adx(df["high"].values, df["low"].values, df["close"].values)

    return df


__all__ = [
    "ema",
    "rma",
    "atr",
    "rsi",
    "macd",
    "bollinger_bands",
    "adx",
    "calculate_all_indicators",
]
