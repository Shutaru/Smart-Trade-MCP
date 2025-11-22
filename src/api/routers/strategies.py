# -*- coding: utf-8 -*-
"""
Strategies Router

REST API endpoints for strategy management and listing.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional

from ..models.responses import ListStrategiesResponse, StrategyInfo, ErrorResponse
from ...core.logger import logger

router = APIRouter()


@router.get(
    "/",
    response_model=ListStrategiesResponse,
    summary="List all available strategies",
    description="Get list of all 42+ trading strategies with metadata",
)
async def list_strategies(
    category: Optional[str] = Query(
        None,
        description="Filter by category",
        enum=["breakout", "trend", "mean_reversion", "momentum", "hybrid", "advanced"],
    )
) -> Dict[str, Any]:
    """
    List all available trading strategies.
    
    **Categories:**
    - **breakout:** 12 strategies (high volatility, trending markets)
    - **trend:** 8 strategies (momentum-based, directional moves)
    - **mean_reversion:** 6 strategies (counter-trend, ranging markets)
    - **momentum:** 8 strategies (oscillator-based)
    - **hybrid:** 6 strategies (combined approaches)
    - **advanced:** 2 strategies (multi-component adaptive)
    
    **Performance:** <100ms
    """
    try:
        logger.info(f"API: List strategies request (category={category})")
        
        # Import MCP tool
        from ...mcp_server.tools.strategies import list_strategies as mcp_list_strategies
        
        # Get strategies
        result = await mcp_list_strategies(category=category)
        
        logger.info(f"API: Returning {result['total']} strategies")
        
        return result
        
    except Exception as e:
        logger.error(f"API: List strategies error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{strategy_name}",
    response_model=StrategyInfo,
    responses={404: {"model": ErrorResponse}},
    summary="Get strategy details",
    description="Get detailed information about a specific strategy",
)
async def get_strategy_info(strategy_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific strategy.
    
    **Returns:**
    - Strategy metadata
    - Required indicators
    - Category
    - Description
    
    **Performance:** <50ms
    """
    try:
        logger.info(f"API: Get strategy info for {strategy_name}")
        
        # Import registry
        from ...strategies import registry
        
        try:
            strategy = registry.get(strategy_name)
        except KeyError:
            raise HTTPException(
                status_code=404,
                detail=f"Strategy '{strategy_name}' not found",
            )
        
        # Build response
        info = {
            "name": strategy_name,
            "category": getattr(strategy, "category", "unknown"),
            "description": strategy.__class__.__doc__ or f"{strategy_name} trading strategy",
            "required_indicators": strategy.get_required_indicators(),
        }
        
        return info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Get strategy info error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/categories/list",
    summary="List all strategy categories",
    description="Get list of all available strategy categories",
)
async def list_categories() -> Dict[str, Any]:
    """
    List all strategy categories.
    
    **Returns:**
    - Category name
    - Number of strategies
    - Description
    - Best markets
    
    **Performance:** <50ms
    """
    return {
        "categories": [
            {
                "name": "breakout",
                "count": 12,
                "description": "High-volatility breakout strategies",
                "best_markets": "Trending, high volatility",
                "avoid": "Ranging, low volatility",
            },
            {
                "name": "trend",
                "count": 8,
                "description": "Momentum-based trend following",
                "best_markets": "Strong trends",
                "avoid": "Choppy, ranging markets",
            },
            {
                "name": "mean_reversion",
                "count": 6,
                "description": "Counter-trend price extremes",
                "best_markets": "Ranging, low volatility",
                "avoid": "Strong trends",
            },
            {
                "name": "momentum",
                "count": 8,
                "description": "Oscillator-based momentum",
                "best_markets": "Medium volatility, trending",
                "avoid": "Extreme volatility",
            },
            {
                "name": "hybrid",
                "count": 6,
                "description": "Combined approach strategies",
                "best_markets": "All market conditions",
                "performance": "Moderate, consistent",
            },
            {
                "name": "advanced",
                "count": 2,
                "description": "Multi-component adaptive systems",
                "best_markets": "Adaptive to all conditions",
                "complexity": "High",
            },
        ],
        "total_strategies": 42,
    }


@router.get(
    "/search/{query}",
    summary="Search strategies",
    description="Search strategies by name or keywords",
)
async def search_strategies(query: str) -> Dict[str, Any]:
    """
    Search strategies by name or keywords.
    
    **Example queries:**
    - "RSI" ? Returns all RSI-based strategies
    - "momentum" ? Returns momentum strategies
    - "VWAP" ? Returns VWAP-related strategies
    
    **Performance:** <100ms
    """
    try:
        logger.info(f"API: Search strategies query='{query}'")
        
        # Import registry
        from ...strategies import registry
        
        # Get all strategies
        all_strategies = registry.list_all()
        
        # Filter by query (case-insensitive)
        query_lower = query.lower()
        matches = [
            name for name in all_strategies
            if query_lower in name.lower()
        ]
        
        logger.info(f"API: Found {len(matches)} matches for '{query}'")
        
        return {
            "query": query,
            "total_matches": len(matches),
            "strategies": matches,
        }
        
    except Exception as e:
        logger.error(f"API: Search strategies error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
