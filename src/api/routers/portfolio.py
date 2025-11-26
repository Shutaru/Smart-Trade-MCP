# -*- coding: utf-8 -*-
"""
Portfolio Router

REST API endpoints for portfolio management.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from ...portfolio.portfolio_config import PortfolioConfig
from ...portfolio.portfolio_optimizer import PortfolioOptimizer
from ...core.data_manager import DataManager
from ...core.indicators import calculate_all_indicators
from ...strategies import registry
from ...core.logger import logger

router = APIRouter()


async def _fetch_and_prepare_data(strategies: List[str], symbol: str = "BTC/USDT", timeframe: str = "1h", days: int = 365):
    """Helper to fetch data and calculate indicators for strategies"""
    dm = DataManager()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    try:
        df = await dm.fetch_historical(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            max_candles=10000,
        )
    finally:
        await dm.close()
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No data available")
    
    # Calculate required indicators
    all_indicators = set()
    for strategy_name in strategies:
        try:
            strategy = registry.get(strategy_name)
            all_indicators.update(strategy.get_required_indicators())
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    df = calculate_all_indicators(df, list(all_indicators), use_gpu=False)
    return df


@router.post("/optimize", summary="Optimize portfolio weights")
async def optimize_portfolio(config: PortfolioConfig):
    """
    Optimize portfolio weights using specified method.
    
    - **strategies**: List of strategies to include
    - **method**: equal_weight, risk_parity, max_sharpe, min_variance
    - **constraints**: min/max weights, max correlation
    """
    try:
        # Validate config
        config.validate_config()
        
        # Fetch data
        df = await _fetch_and_prepare_data(config.strategies)
        
        # Run optimization
        optimizer = PortfolioOptimizer(df=df, config=config)
        weights = optimizer.optimize()
        metrics = optimizer.get_portfolio_metrics()
        
        return {
            "status": "success",
            "weights": weights,
            "metrics": metrics,
            "config": config.dict()
        }
        
    except Exception as e:
        logger.error(f"Portfolio optimization error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", summary="Analyze portfolio correlation")
async def analyze_portfolio(config: PortfolioConfig):
    """
    Analyze portfolio correlation and risk without optimizing.
    Returns correlation matrix and current performance metrics (assuming equal weight if not specified).
    """
    try:
        # Fetch data
        df = await _fetch_and_prepare_data(config.strategies)
        
        # Initialize optimizer (but don't run full optimization if not needed)
        # We use equal weight temporarily to get metrics if no weights provided
        # But here we just want correlation and individual stats
        
        optimizer = PortfolioOptimizer(df=df, config=config)
        
        # We need to run backtests to get returns for correlation
        for strategy_name in config.strategies:
            optimizer._backtest_strategy(strategy_name)
            # Store manually as _backtest_strategy returns but doesn't store in self.strategy_performances automatically in all paths?
            # Actually optimize() does it. Let's manually do what optimize() does partially.
            optimizer.strategy_performances[strategy_name] = optimizer._backtest_strategy(strategy_name)

        corr_matrix = optimizer._calculate_correlation_matrix()
        
        # Get individual performances
        performances = {
            name: {
                'sharpe': perf.sharpe,
                'volatility': perf.volatility,
                'max_drawdown': perf.max_drawdown,
                'total_return': perf.total_return,
            }
            for name, perf in optimizer.strategy_performances.items()
        }

        return {
            "status": "success",
            "correlation_matrix": corr_matrix.tolist(),
            "strategies": config.strategies,
            "individual_performances": performances
        }
        
    except Exception as e:
        logger.error(f"Portfolio analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rebalance", summary="Get rebalancing trades")
async def get_rebalancing_trades(
    config: PortfolioConfig, 
    current_weights: Optional[Dict[str, float]] = None,
    total_capital: float = 10000.0
):
    """
    Calculate trades needed to rebalance portfolio to optimal weights.
    
    - **current_weights**: Current allocation (optional, defaults to 0)
    - **total_capital**: Total portfolio value
    """
    try:
        # 1. Optimize to get target weights
        df = await _fetch_and_prepare_data(config.strategies)
        optimizer = PortfolioOptimizer(df=df, config=config)
        target_weights = optimizer.optimize()
        
        # 2. Calculate differences
        current_weights = current_weights or {s: 0.0 for s in config.strategies}
        trades = []
        
        for strategy in config.strategies:
            current_w = current_weights.get(strategy, 0.0)
            target_w = target_weights.get(strategy, 0.0)
            
            diff = target_w - current_w
            
            # Only trade if difference is significant (e.g. > 1%)
            if abs(diff) > 0.01:
                action = "BUY" if diff > 0 else "SELL"
                amount = abs(diff) * total_capital
                
                trades.append({
                    "strategy": strategy,
                    "action": action,
                    "weight_diff": round(diff, 4),
                    "amount_usd": round(amount, 2),
                    "current_weight": current_w,
                    "target_weight": round(target_w, 4)
                })
        
        return {
            "status": "success",
            "rebalancing_needed": len(trades) > 0,
            "trades": trades,
            "target_weights": target_weights
        }
        
    except Exception as e:
        logger.error(f"Rebalancing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
