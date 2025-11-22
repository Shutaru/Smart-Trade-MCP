"""Batch comparison tool for multiple strategies."""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import asyncio

from ...core.logger import logger
from ...strategies import registry
from ...core.data_manager import DataManager
from ...core.indicators import calculate_all_indicators
from ...core.backtest_engine import BacktestEngine


async def compare_strategies(
    strategies: List[str],
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    initial_capital: float = 10000.0,
) -> Dict[str, Any]:
    """
    Compare multiple strategies in a single batch operation.
    
    **OPTIMIZED:** Fetches data once, reuses for all strategies.
    
    Args:
        strategies: List of strategy names to compare
        symbol: Trading pair
        timeframe: Candle timeframe
        start_date: Start date (YYYY-MM-DD) - defaults to 1 year ago
        end_date: End date (YYYY-MM-DD) - defaults to now
        initial_capital: Starting capital
        
    Returns:
        Dictionary with comparison results for all strategies
    """
    logger.info(f"Comparing {len(strategies)} strategies on {symbol} {timeframe}")
    
    try:
        # Parse dates
        if end_date is None or end_date == "":
            end_dt = datetime.now()
        else:
            end_dt = datetime.fromisoformat(end_date)
        
        if start_date is None or start_date == "":
            start_dt = end_dt - timedelta(days=365)
        else:
            start_dt = datetime.fromisoformat(start_date)
        
        # Fetch data ONCE for all strategies
        logger.info("?? Fetching data (once for all strategies)...")
        dm = DataManager()
        df = await dm.fetch_historical(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_dt,
            end_date=end_dt,
            max_candles=20000,
        )
        await dm.close()
        
        if df.empty:
            return {"error": "No market data available"}
        
        actual_days = (df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).days
        logger.info(f"? Fetched {len(df)} candles ({actual_days} days)")
        
        # Collect all required indicators
        logger.info("?? Collecting required indicators...")
        all_indicators = set()
        strategy_objects = {}
        
        for strategy_name in strategies:
            try:
                strategy = registry.get(strategy_name)
                strategy_objects[strategy_name] = strategy
                all_indicators.update(strategy.get_required_indicators())
            except Exception as e:
                logger.warning(f"Skipping {strategy_name}: {e}")
        
        # Calculate indicators ONCE for all strategies
        logger.info(f"?? Calculating {len(all_indicators)} unique indicators...")
        df_with_indicators = calculate_all_indicators(
            df.copy(), 
            list(all_indicators), 
            use_gpu=False
        )
        
        # Run backtests for all strategies
        logger.info("?? Running backtests...")
        results = []
        
        for strategy_name, strategy in strategy_objects.items():
            try:
                engine = BacktestEngine(initial_capital=initial_capital, use_gpu=False)
                backtest_result = engine.run(strategy, df_with_indicators)
                
                # Optimized result (minimal data)
                results.append({
                    "strategy": strategy_name,
                    "total_return": float(backtest_result['total_return']),
                    "total_trades": int(backtest_result['total_trades']),
                    "sharpe_ratio": float(backtest_result['metrics']['sharpe_ratio']),
                    "win_rate": float(backtest_result['metrics']['win_rate']),
                    "max_drawdown_pct": float(backtest_result['metrics']['max_drawdown_pct']),
                    "profit_factor": float(backtest_result['metrics']['profit_factor']),
                })
                
            except Exception as e:
                logger.error(f"Backtest failed for {strategy_name}: {e}")
                results.append({
                    "strategy": strategy_name,
                    "error": str(e)
                })
        
        # Sort by Sharpe Ratio (descending)
        valid_results = [r for r in results if 'error' not in r]
        valid_results.sort(key=lambda x: x['sharpe_ratio'], reverse=True)
        
        # Add failed strategies at the end
        failed_results = [r for r in results if 'error' in r]
        
        logger.info(f"? Batch comparison complete: {len(valid_results)} successful, {len(failed_results)} failed")
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "start_date": str(df['timestamp'].iloc[0]),
            "end_date": str(df['timestamp'].iloc[-1]),
            "days_tested": actual_days,
            "candles_tested": len(df),
            "total_strategies": len(strategies),
            "successful": len(valid_results),
            "failed": len(failed_results),
            "results": valid_results + failed_results,  # Successful first, then failed
            "top_3_by_sharpe": valid_results[:3] if len(valid_results) >= 3 else valid_results,
            "top_3_by_return": sorted(valid_results, key=lambda x: x['total_return'], reverse=True)[:3] if valid_results else [],
        }
        
    except Exception as e:
        logger.error(f"Batch comparison error: {e}", exc_info=True)
        return {"error": str(e)}


__all__ = ["compare_strategies"]
