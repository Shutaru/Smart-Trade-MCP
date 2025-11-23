"""
Regime Detection MCP Tool

Exposes market regime detection via MCP for LLM access.
"""

from typing import Dict, Any
import asyncio

from ...core.logger import logger
from ...core.regime_detector import get_regime_detector, MarketRegime
from ...core.data_manager import DataManager
from ...core.indicators import calculate_all_indicators


async def detect_market_regime(
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    lookback: int = 100,
) -> Dict[str, Any]:
    """Detect current market regime - OPTIMIZED for MCP speed"""
    logger.info(f"Detecting market regime: {symbol} {timeframe}")
    
    try:
        async def _detect_with_timeout():
            dm = DataManager()
            # ? REDUCED limit for speed (100 + 30 = 130 instead of 150)
            df = await dm.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=min(lookback + 30, 130),  # ? Max 130 candles
                use_cache=True,
            )
            await dm.close()
            
            if df.empty:
                return {"error": "No market data available"}
            
            # ? Calculate ONLY essential indicators (skip bollinger for speed)
            indicators = ['adx', 'atr', 'ema']  # ? Removed 'bollinger'
            df = calculate_all_indicators(df, indicators, use_gpu=False)
            
            # Detect regime
            detector = get_regime_detector()
            # ? Use smaller lookback if needed
            actual_lookback = min(lookback, len(df) - 20)
            analysis = detector.detect(df, lookback=actual_lookback)
            
            result = analysis.to_dict()
            
            logger.info(
                f"? Regime detected: {result['regime']} "
                f"(confidence: {result['confidence']:.2f})"
            )
            
            return result
        
        # ? REDUCED timeout to 30 seconds (from 50)
        result = await asyncio.wait_for(_detect_with_timeout(), timeout=30.0)
        return result
        
    except asyncio.TimeoutError:
        logger.error("? Regime detection timed out after 30 seconds")
        return {
            "error": "Timeout: Analysis took >30 sec",
            "suggestion": "Try with smaller lookback (e.g., 50 instead of 100)",
            "regime": "UNKNOWN",  # ? Return default so Claude can continue
            "confidence": 0.0,
        }
    except Exception as e:
        logger.error(f"? Regime detection failed: {e}", exc_info=True)
        return {
            "error": str(e),
            "regime": "UNKNOWN",
            "confidence": 0.0,
        }


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
        # FIX: Add timeout for long-running operation
        async def _detect_historical_with_timeout():
            # Fetch historical data
            dm = DataManager()
            df = await dm.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit,
                use_cache=True,  # FIX: Use cache!
            )
            await dm.close()
            
            if df.empty:
                return {"error": "No market data available"}
            
            # Calculate indicators (SKIP GPU)
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
        
        # Run with 55 second timeout
        result = await asyncio.wait_for(_detect_historical_with_timeout(), timeout=55.0)
        return result
        
    except asyncio.TimeoutError:
        logger.error("Historical regime detection timed out")
        return {
            "error": "Timeout: Analysis took too long (>55 sec)",
            "suggestion": "Try with smaller limit or window_size"
        }
    except Exception as e:
        logger.error(f"Historical regime detection failed: {e}", exc_info=True)
        return {"error": str(e)}


__all__ = [
    'detect_market_regime',
    'detect_historical_regimes',
]
