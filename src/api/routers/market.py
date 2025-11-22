# -*- coding: utf-8 -*-
"""
Market Router

REST API endpoints for market analysis and regime detection.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ..models.requests import MarketRegimeRequest
from ...core.logger import logger

router = APIRouter()


@router.post("/regime", summary="Detect market regime")
async def detect_regime(request: MarketRegimeRequest) -> Dict[str, Any]:
    """
    Detect current market regime.
    
    **Performance:** <1 second
    """
    try:
        logger.info(f"API: Market regime detection for {request.symbol}")
        
        from ...mcp_server.tools.regime import detect_market_regime
        
        result = await detect_market_regime(
            symbol=request.symbol,
            timeframe=request.timeframe,
            lookback=request.lookback,
        )
        
        return result
        
    except Exception as e:
        logger.error(f"API: Market regime detection error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
