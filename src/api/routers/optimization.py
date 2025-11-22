# -*- coding: utf-8 -*-
"""
Optimization Router

REST API endpoints for strategy optimization operations.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ..models.requests import OptimizeParametersRequest, OptimizePortfolioRequest
from ...core.logger import logger

router = APIRouter()


@router.post("/parameters", summary="Optimize strategy parameters")
async def optimize_parameters(request: OptimizeParametersRequest) -> Dict[str, Any]:
    """
    Optimize strategy parameters using Genetic Algorithm.
    
    **Performance:** 2-5 minutes (depends on population_size × n_generations)
    """
    try:
        logger.info(f"API: Parameter optimization for {request.strategy_name}")
        
        from ...mcp_server.tools.optimization import optimize_strategy_parameters
        
        result = await optimize_strategy_parameters(
            strategy_name=request.strategy_name,
            symbol=request.symbol,
            timeframe=request.timeframe,
            population_size=request.population_size,
            n_generations=request.n_generations,
            use_ray=request.use_ray,
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Parameter optimization error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/portfolio", summary="Optimize portfolio allocation")
async def optimize_portfolio_endpoint(request: OptimizePortfolioRequest) -> Dict[str, Any]:
    """
    Optimize multi-strategy portfolio allocation.
    
    **Performance:** 2-3 minutes for 5-10 strategies
    """
    try:
        logger.info(f"API: Portfolio optimization for {len(request.strategies)} strategies")
        
        from ...mcp_server.tools.optimization import optimize_portfolio
        
        result = await optimize_portfolio(
            strategies=request.strategies,
            symbol=request.symbol,
            timeframe=request.timeframe,
            method=request.method,
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Portfolio optimization error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
