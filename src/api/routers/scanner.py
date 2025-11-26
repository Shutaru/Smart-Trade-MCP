# -*- coding: utf-8 -*-
"""
Scanner Router

REST API endpoints for the real-time signal scanner.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...agent.signal_scanner import SignalScanner, TradingSignal
from ...agent.config import AgentConfig, TradingPairConfig, StrategyConfig
from ...core.logger import logger

router = APIRouter()

# Global scanner instance (lazy loaded)
_scanner: Optional[SignalScanner] = None

def get_scanner() -> SignalScanner:
    """Get or create global scanner instance."""
    global _scanner
    if _scanner is None:
        # Load default config
        config = AgentConfig()
        _scanner = SignalScanner(config)
    return _scanner

@router.post("/scan", summary="Trigger manual scan")
async def trigger_scan(
    background_tasks: BackgroundTasks,
    pairs: Optional[List[str]] = None,
    strategies: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Trigger a manual scan for trading signals.
    
    - **pairs**: Optional list of pairs to scan (e.g. ["BTC/USDT"]). If None, scans all configured.
    - **strategies**: Optional list of strategies to use. If None, uses all configured.
    """
    try:
        scanner = get_scanner()
        
        # Override config if parameters provided
        if pairs:
            # Create temporary config with specific pairs
            # We assume default timeframe '1h' for ad-hoc requests for now
            scanner.config.pairs = [
                TradingPairConfig(symbol=p, timeframe="1h", enabled=True) 
                for p in pairs
            ]
            
        if strategies:
            # Create temporary config with specific strategies
            scanner.config.strategies = [
                StrategyConfig(name=s, enabled=True) 
                for s in strategies
            ]
            
        # Run scan
        logger.info(f"API: Triggering scan for {len(scanner.config.pairs)} pairs")
        signals = await scanner.scan_all()
        
        # Generate summary
        summary = scanner.get_summary(signals)
        
        return {
            "status": "success",
            "signals_found": len(signals),
            "summary": summary,
            "signals": [s.to_dict() for s in signals]
        }
        
    except Exception as e:
        logger.error(f"API: Scan failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config", summary="Get scanner configuration")
async def get_scanner_config() -> Dict[str, Any]:
    """Get current scanner configuration."""
    scanner = get_scanner()
    return scanner.config.dict()

@router.post("/config", summary="Update scanner configuration")
async def update_scanner_config(config: AgentConfig) -> Dict[str, Any]:
    """Update scanner configuration."""
    global _scanner
    try:
        _scanner = SignalScanner(config)
        return {
            "status": "success",
            "message": "Scanner configuration updated",
            "config": config.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
