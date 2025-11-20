"""
Regime Detection MCP Tool

Exposes market regime detection via MCP for LLM access.
"""

from typing import Dict, Any

from ...core.logger import logger
from ...core.regime_detector import get_regime_detector, MarketRegime
from ...core.data_manager import DataManager
from ...core.indicators import calculate_all_indicators


async def detect_market_regime(
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    lookback: int = 100,
) -> Dict[str, Any]:
    """
    Detect current market regime.
    
    Analyzes recent market data to classify regime and recommend strategies.
    
    Args:
        symbol: Trading pair
        timeframe: Candle timeframe
        lookback: Number of candles to analyze
        
    Returns:
        Dictionary with regime analysis:
        {
            "regime": str,  # TRENDING_UP, TRENDING_DOWN, RANGING, VOLATILE, CONSOLIDATING
            "confidence": float,  # 0-1
            "timestamp": str,
            "metrics": Dict[str, float],
            "recommended_strategies": List[str],
            "avoid_strategies": List[str],
        }
        
    Example (via MCP):
        >>> result = await detect_market_regime(symbol="BTC/USDT")
        >>> print(f"Regime: {result['regime']}")
        >>> print(f"Use strategies: {result['recommended_strategies']}")
    """
    logger.info(f"Detecting market regime: {symbol} {timeframe}")
    
    try:
        # Fetch data
        dm = DataManager()
        df = await dm.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=lookback + 50,  # Extra for indicator calculation
        )
        await dm.close()
        
        if df.empty:
            return {"error": "No market data available"}
        
        # Calculate required indicators
        indicators = ['adx', 'atr', 'bollinger', 'ema']
        df = calculate_all_indicators(df, indicators, use_gpu=False)
        
        # Detect regime
        detector = get_regime_detector()
        analysis = detector.detect(df, lookback=lookback)
        
        result = analysis.to_dict()
        
        logger.info(
            f"Regime detected: {result['regime']} "
            f"(confidence: {result['confidence']:.2f})"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Regime detection failed: {e}", exc_info=True)
        return {"error": str(e)}


async def detect_historical_regimes(
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    limit: int = 5000,
    window_size: int = 100,
) -> Dict[str, Any]:
    """
    Detect regime changes across historical data.
    
    Useful for regime-aware backtesting - shows which regimes existed when.
    
    Args:
        symbol: Trading pair
        timeframe: Candle timeframe
        limit: Number of historical candles
        window_size: Rolling window for detection
        
    Returns:
        Dictionary with regime periods:
        {
            "symbol": str,
            "timeframe": str,
            "total_periods": int,
            "periods": List[{
                "start": str,
                "end": str,
                "regime": str,
                "duration_hours": int,
            }],
            "regime_distribution": Dict[str, float],  # % of time in each regime
        }
    """
    logger.info(f"Detecting historical regimes: {symbol} {timeframe}")
    
    try:
        # Fetch historical data
        dm = DataManager()
        df = await dm.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )
        await dm.close()
        
        if df.empty:
            return {"error": "No market data available"}
        
        # Calculate indicators
        indicators = ['adx', 'atr', 'bollinger', 'ema']
        df = calculate_all_indicators(df, indicators, use_gpu=False)
        
        # Detect regimes
        detector = get_regime_detector()
        regime_periods = detector.detect_historical_regimes(df, window_size=window_size)
        
        # Format results
        periods = []
        regime_hours = {}
        
        for start, end, regime in regime_periods:
            duration = (end - start).total_seconds() / 3600  # hours
            
            periods.append({
                'start': start.isoformat(),
                'end': end.isoformat(),
                'regime': regime.value,
                'duration_hours': int(duration),
            })
            
            # Track time in each regime
            regime_name = regime.value
            regime_hours[regime_name] = regime_hours.get(regime_name, 0) + duration
        
        # Calculate distribution
        total_hours = sum(regime_hours.values())
        regime_distribution = {
            regime: round((hours / total_hours) * 100, 1)
            for regime, hours in regime_hours.items()
        } if total_hours > 0 else {}
        
        logger.info(f"Detected {len(periods)} regime periods")
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'total_periods': len(periods),
            'periods': periods,
            'regime_distribution': regime_distribution,
        }
        
    except Exception as e:
        logger.error(f"Historical regime detection failed: {e}", exc_info=True)
        return {"error": str(e)}


__all__ = [
    'detect_market_regime',
    'detect_historical_regimes',
]
