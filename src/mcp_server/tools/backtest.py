"""Backtesting tool for strategy validation."""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json

from ...core.logger import logger
from ...strategies import registry
from ...core.data_manager import DataManager
from ...core.indicators import calculate_all_indicators
from ...core.backtest_engine import BacktestEngine

# VERSION TRACKING - to verify server reloaded
BACKTEST_TOOL_VERSION = "2.0.2-optimized"  # Optimized response size


async def backtest_strategy(
    strategy_name: str,
    symbol: str,
    timeframe: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    initial_capital: float = 10000.0,
) -> Dict[str, Any]:
    """
    Run backtest for a trading strategy.
    
    **AUTO-FETCHES 1 YEAR OF DATA** if start_date not specified!
    
    Version: 2.0.2-optimized (optimized response size for MCP)

    Args:
        strategy_name: Name of strategy to backtest
        symbol: Trading pair
        timeframe: Timeframe (e.g., '1h', '4h', '1d')
        start_date: Start date (YYYY-MM-DD) - defaults to 1 year ago
        end_date: End date (YYYY-MM-DD) - defaults to now
        initial_capital: Starting capital

    Returns:
        Backtest results with performance metrics (optimized for MCP)
    """
    # ==================== DEBUG LOGGING START ====================
    logger.info("=" * 80)
    logger.info("BACKTEST TOOL - DETAILED DEBUG LOG")
    logger.info("=" * 80)
    logger.info(f"Tool Version: {BACKTEST_TOOL_VERSION}")
    logger.info(f"Strategy: {strategy_name}")
    logger.info(f"Symbol: {symbol}")
    logger.info(f"Timeframe: {timeframe}")
    logger.info(f"Initial Capital: {initial_capital}")
    logger.info("-" * 80)
    logger.info("RAW PARAMETERS RECEIVED:")
    logger.info(f"  start_date: {repr(start_date)} (type: {type(start_date).__name__})")
    logger.info(f"  end_date: {repr(end_date)} (type: {type(end_date).__name__})")
    logger.info("=" * 80)
    # ==================== DEBUG LOGGING END ====================

    try:
        # Get strategy
        strategy = registry.get(strategy_name)
        logger.info(f"? Strategy loaded: {strategy.__class__.__name__}")

        # Parse dates - DEFAULT TO 1 YEAR if not specified!
        # Handle empty strings as None (MCP may send "" instead of null)
        if end_date is None or end_date == "":
            end_dt = datetime.now()
            logger.info(f"?? end_date was None/empty ? using NOW: {end_dt}")
        else:
            end_dt = datetime.fromisoformat(end_date)
            logger.info(f"?? end_date parsed: {end_dt}")
        
        if start_date is None or start_date == "":
            # DEFAULT: 1 year of data
            start_dt = end_dt - timedelta(days=365)
            logger.info(f"?? start_date was None/empty ? AUTO-FETCH MODE")
            logger.info(f"   Calculated start_dt: {start_dt} (1 year before end)")
        else:
            start_dt = datetime.fromisoformat(start_date)
            logger.info(f"?? start_date parsed: {start_dt}")
        
        # Calculate requested period
        requested_days = (end_dt - start_dt).days
        logger.info("-" * 80)
        logger.info("DATE RANGE SUMMARY:")
        logger.info(f"  Start: {start_dt.date()} {start_dt.time()}")
        logger.info(f"  End:   {end_dt.date()} {end_dt.time()}")
        logger.info(f"  Days:  {requested_days}")
        logger.info("=" * 80)

        # Fetch historical data with pagination (HANDLES MULTI-YEAR DATA!)
        logger.info("?? Initiating data fetch from DataManager...")
        dm = DataManager()
        df = await dm.fetch_historical(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_dt,
            end_date=end_dt,
            max_candles=20000,  # Up to ~2.3 years of hourly data
        )
        await dm.close()

        if df.empty:
            logger.error("? DataManager returned EMPTY dataframe!")
            return {
                "error": "No market data available for the specified period",
                "symbol": symbol,
                "timeframe": timeframe,
                "start_date": str(start_dt),
                "end_date": str(end_dt),
                "requested_days": requested_days,
                "tool_version": BACKTEST_TOOL_VERSION,
            }
        
        actual_days = (df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).days
        logger.info("=" * 80)
        logger.info("DATA FETCH RESULTS:")
        logger.info(f"  ? Fetched {len(df)} candles")
        logger.info(f"  ?? Actual period: {actual_days} days")
        logger.info(f"  ?? First candle: {df['timestamp'].iloc[0]}")
        logger.info(f"  ?? Last candle: {df['timestamp'].iloc[-1]}")
        logger.info(f"  ?? Price start: ${df['close'].iloc[0]:.2f}")
        logger.info(f"  ?? Price end: ${df['close'].iloc[-1]:.2f}")
        
        # CRITICAL: Check if we got the expected amount
        if actual_days < requested_days * 0.5:  # Less than 50% of requested
            logger.warning("?? WARNING: Fetched significantly less data than requested!")
            logger.warning(f"   Requested: {requested_days} days")
            logger.warning(f"   Received:  {actual_days} days ({actual_days/requested_days*100:.1f}%)")
        else:
            logger.info(f"  ? Data coverage: {actual_days/requested_days*100:.1f}% of requested period")
        
        logger.info("=" * 80)

        # Calculate indicators
        required_indicators = strategy.get_required_indicators()
        logger.info(f"?? Calculating indicators: {required_indicators}")
        df = calculate_all_indicators(df, required_indicators, use_gpu=False)
        logger.info(f"? Indicators calculated, DataFrame has {len(df.columns)} columns")

        # Run backtest
        logger.info("?? Starting backtest execution...")
        engine = BacktestEngine(initial_capital=initial_capital, use_gpu=False)
        results = engine.run(strategy, df)

        logger.info("=" * 80)
        logger.info("BACKTEST COMPLETE:")
        logger.info(f"  Total Trades: {results['total_trades']}")
        logger.info(f"  Total Return: {results['total_return']:.2f}%")
        logger.info(f"  Win Rate: {results['metrics']['win_rate']:.1f}%")
        logger.info(f"  Sharpe Ratio: {results['metrics']['sharpe_ratio']:.2f}")
        logger.info("=" * 80)

        # ==================== OPTIMIZE RESPONSE FOR MCP ====================
        # Remove large arrays and numpy types that cause serialization issues
        optimized_result = {
            "strategy": strategy_name,
            "symbol": symbol,
            "timeframe": timeframe,
            "start_date": str(df['timestamp'].iloc[0]),
            "end_date": str(df['timestamp'].iloc[-1]),
            "days_tested": actual_days,
            "candles_tested": len(df),
            "requested_days": requested_days,
            "data_coverage_pct": round(actual_days / requested_days * 100, 1),
            "tool_version": BACKTEST_TOOL_VERSION,
            
            # Core results
            "initial_capital": float(results['initial_capital']),
            "final_equity": float(results['final_equity']),
            "total_return": float(results['total_return']),
            "total_trades": int(results['total_trades']),
            
            # Key metrics (convert numpy types to Python types)
            "metrics": {
                "total_trades": int(results['metrics']['total_trades']),
                "winning_trades": int(results['metrics']['winning_trades']),
                "losing_trades": int(results['metrics']['losing_trades']),
                "win_rate": float(results['metrics']['win_rate']),
                "avg_win": float(results['metrics']['avg_win']),
                "avg_loss": float(results['metrics']['avg_loss']),
                "profit_factor": float(results['metrics']['profit_factor']),
                "sharpe_ratio": float(results['metrics']['sharpe_ratio']),
                "max_drawdown": float(results['metrics']['max_drawdown']),
                "max_drawdown_pct": float(results['metrics']['max_drawdown_pct']),
            },
            
            # Simplified equity summary (first, last, min, max only)
            "equity_summary": {
                "start": float(results['equity_curve'][0]['equity']),
                "end": float(results['equity_curve'][-1]['equity']),
                "peak": float(max(e['equity'] for e in results['equity_curve'])),
                "trough": float(min(e['equity'] for e in results['equity_curve'])),
            },
            
            # First and last few trades only (not all)
            "sample_trades": {
                "first_3": results['trades'][:3] if len(results['trades']) >= 3 else results['trades'],
                "last_3": results['trades'][-3:] if len(results['trades']) >= 3 else [],
                "total_count": len(results['trades']),
            }
        }
        
        logger.info(f"? Response optimized for MCP (removed large arrays)")
        return optimized_result

    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"? BACKTEST FAILED: {e}", exc_info=True)
        logger.error("=" * 80)
        return {
            "error": str(e),
            "strategy": strategy_name,
            "tool_version": BACKTEST_TOOL_VERSION,
        }


__all__ = ["backtest_strategy"]
