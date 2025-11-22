# -*- coding: utf-8 -*-
"""
Backtest Router

REST API endpoints for backtesting operations.
Reuses MCP tools for actual execution.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any

from ..models.requests import BacktestRequest, CompareStrategiesRequest
from ..models.responses import BacktestResponse, CompareStrategiesResponse, ErrorResponse
from ...core.logger import logger

router = APIRouter()


@router.post(
    "/single",
    response_model=BacktestResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Run single strategy backtest",
    description="Execute backtest for a single trading strategy with optimized response",
)
async def backtest_single_strategy(request: BacktestRequest) -> Dict[str, Any]:
    """
    Run backtest for a single strategy.
    
    **Key Features:**
    - Auto-fetches 1 year of data if dates not specified
    - Returns optimized response (~3KB)
    - Includes equity summary and sample trades
    
    **Performance:** ~1-2 seconds
    """
    try:
        logger.info(f"API: Backtest request for {request.strategy_name}")
        
        # Import MCP tool
        from ...mcp_server.tools.backtest import backtest_strategy
        
        # Execute backtest (reuse MCP tool)
        result = await backtest_strategy(
            strategy_name=request.strategy_name,
            symbol=request.symbol,
            timeframe=request.timeframe,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
        )
        
        # Check for errors
        if "error" in result:
            raise HTTPException(
                status_code=404 if "not found" in result["error"].lower() else 400,
                detail=result["error"],
            )
        
        logger.info(
            f"API: Backtest complete - {result['days_tested']} days, "
            f"{result['total_trades']} trades, "
            f"{result['total_return']:.2f}% return"
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Backtest error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/compare",
    response_model=CompareStrategiesResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Compare multiple strategies (BATCH)",
    description="Compare 2-100 strategies in ONE efficient operation. 20-30x faster than individual calls!",
)
async def compare_strategies_endpoint(request: CompareStrategiesRequest) -> Dict[str, Any]:
    """
    Compare multiple strategies using batch processing.
    
    **Key Features:**
    - Fetches data ONCE for all strategies
    - Calculates unique indicators ONCE
    - Returns top performers + all results
    
    **Performance:**
    - 10 strategies: ~3-5 seconds
    - 41 strategies: ~15 seconds
    - 100 strategies: ~30 seconds
    
    **Optimization:** 20-30x faster than individual backtests!
    """
    try:
        logger.info(f"API: Batch comparison request for {len(request.strategies)} strategies")
        
        # Import MCP tool
        from ...mcp_server.tools.batch_compare import compare_strategies
        
        # Execute batch comparison (reuse MCP tool)
        result = await compare_strategies(
            strategies=request.strategies,
            symbol=request.symbol,
            timeframe=request.timeframe,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
        )
        
        # Check for errors
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        logger.info(
            f"API: Batch comparison complete - {result['successful']}/{result['total_strategies']} successful, "
            f"{result['days_tested']} days tested"
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Batch comparison error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/status/{task_id}",
    summary="Get backtest task status",
    description="Get status of a running backtest task (for async operations)",
)
async def get_backtest_status(task_id: str):
    """
    Get status of a background backtest task.
    
    **Note:** Currently all backtests are synchronous.
    This endpoint is for future async implementation.
    """
    return {
        "task_id": task_id,
        "status": "not_implemented",
        "message": "Async backtests not yet implemented",
    }
