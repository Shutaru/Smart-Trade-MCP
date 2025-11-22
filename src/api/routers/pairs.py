# -*- coding: utf-8 -*-
"""
Pair Management Router

REST API endpoints for dynamic trading pair management.
Allows frontend to control which pairs are actively scanned.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from ...agent.pair_management import PairManagementStorage
from ...core.logger import logger
from pathlib import Path

router = APIRouter()

# Initialize storage
pair_storage = PairManagementStorage(Path("data/pair_management.db"))


# ========== REQUEST MODELS ==========

class PairEnableRequest(BaseModel):
    """Request to enable trading pairs."""
    symbols: List[str]
    timeframe: str = "1h"


class PairDisableRequest(BaseModel):
    """Request to disable trading pairs."""
    symbols: List[str]


class TopPairsRequest(BaseModel):
    """Request for top pairs by criteria."""
    criteria: str  # 'volatility_5m', 'volatility_1h', 'marketcap_4h'
    limit: int = 10


# ========== ENDPOINTS ==========

@router.get("/available", summary="Get all available Binance Futures pairs")
async def get_available_pairs() -> Dict[str, Any]:
    """
    Get all available trading pairs from Binance Futures.
    
    Returns list of all tradable USDT perpetual futures.
    """
    try:
        logger.info("API: Fetching available Binance Futures pairs")
        
        import ccxt
        
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        
        # Fetch markets
        markets = exchange.load_markets()
        
        # Filter USDT perpetuals
        usdt_perps = [
            {
                'symbol': market['symbol'],
                'base': market['base'],
                'quote': market['quote'],
                'active': market['active'],
                'type': market['type']
            }
            for market in markets.values()
            if market['quote'] == 'USDT' and market['type'] == 'swap'
        ]
        
        # Close exchange
        await exchange.close()
        
        logger.info(f"Found {len(usdt_perps)} USDT perpetual contracts")
        
        return {
            'total': len(usdt_perps),
            'pairs': usdt_perps
        }
        
    except Exception as e:
        logger.error(f"API: Error fetching available pairs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active", summary="Get actively scanned pairs")
async def get_active_pairs() -> Dict[str, Any]:
    """
    Get pairs currently enabled for scanning.
    
    Returns pairs that the autonomous agent is actively monitoring.
    """
    try:
        enabled_pairs = pair_storage.get_enabled_pairs()
        
        return {
            'total': len(enabled_pairs),
            'pairs': enabled_pairs
        }
        
    except Exception as e:
        logger.error(f"API: Error fetching active pairs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", summary="Get all configured pairs")
async def get_all_pairs() -> Dict[str, Any]:
    """
    Get all pairs (enabled and disabled).
    
    Includes configuration and status for each pair.
    """
    try:
        all_pairs = pair_storage.get_all_pairs()
        stats = pair_storage.get_statistics()
        
        return {
            'total': len(all_pairs),
            'enabled': stats['enabled_pairs'],
            'disabled': stats['disabled_pairs'],
            'pairs': all_pairs
        }
        
    except Exception as e:
        logger.error(f"API: Error fetching all pairs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enable", summary="Enable trading pairs (hotswap ON)")
async def enable_pairs(request: PairEnableRequest) -> Dict[str, Any]:
    """
    Enable one or more trading pairs for scanning.
    
    **Hotswap:** Agent will start scanning these pairs immediately.
    """
    try:
        logger.info(f"API: Enabling {len(request.symbols)} pairs")
        
        # Add/update pairs
        for symbol in request.symbols:
            pair_storage.add_pair(symbol, request.timeframe, enabled=True)
        
        return {
            'success': True,
            'enabled': request.symbols,
            'message': f'Enabled {len(request.symbols)} pairs'
        }
        
    except Exception as e:
        logger.error(f"API: Error enabling pairs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disable", summary="Disable trading pairs (hotswap OFF)")
async def disable_pairs(request: PairDisableRequest) -> Dict[str, Any]:
    """
    Disable one or more trading pairs.
    
    **Behavior:**
    - Agent stops scanning these pairs immediately
    - Active trades continue following SL/TP logic
    - No new trades opened until re-enabled
    """
    try:
        logger.info(f"API: Disabling {len(request.symbols)} pairs")
        
        # Check for active trades
        active_trades = {}
        for symbol in request.symbols:
            trades = pair_storage.get_active_trades(symbol)
            if trades:
                active_trades[symbol] = len(trades)
        
        # Disable pairs
        pair_storage.bulk_disable_pairs(request.symbols)
        
        return {
            'success': True,
            'disabled': request.symbols,
            'active_trades': active_trades,
            'message': f'Disabled {len(request.symbols)} pairs. {len(active_trades)} pairs have active trades.'
        }
        
    except Exception as e:
        logger.error(f"API: Error disabling pairs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-volatility", summary="Get top pairs by volatility")
async def get_top_volatility(
    timeframe: str = "5m",
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get top N pairs by volatility (ATR-based).
    
    **Criteria:**
    - 5m: High-frequency trading pairs
    - 1h: Day trading pairs
    
    **Implementation:** Calculates ATR% for last 100 candles.
    """
    try:
        logger.info(f"API: Fetching top {limit} volatile pairs ({timeframe})")
        
        import ccxt
        import pandas as pd
        import numpy as np
        
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        
        # Get all USDT perpetuals
        markets = exchange.load_markets()
        symbols = [m['symbol'] for m in markets.values() 
                  if m['quote'] == 'USDT' and m['type'] == 'swap' and m['active']]
        
        # Calculate volatility for each
        volatility_data = []
        
        for symbol in symbols[:50]:  # Limit to top 50 by volume to save time
            try:
                # Fetch OHLCV
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                
                # Calculate ATR
                high_low = df['high'] - df['low']
                high_close = np.abs(df['high'] - df['close'].shift())
                low_close = np.abs(df['low'] - df['close'].shift())
                tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                atr = tr.rolling(14).mean().iloc[-1]
                
                # ATR as % of price
                atr_pct = (atr / df['close'].iloc[-1]) * 100
                
                volatility_data.append({
                    'symbol': symbol,
                    'atr_pct': atr_pct,
                    'price': df['close'].iloc[-1],
                    'volume_24h': df['volume'].sum()
                })
                
            except Exception as e:
                logger.debug(f"Skipping {symbol}: {e}")
                continue
        
        await exchange.close()
        
        # Sort by volatility
        volatility_data.sort(key=lambda x: x['atr_pct'], reverse=True)
        top_pairs = volatility_data[:limit]
        
        return {
            'criteria': f'volatility_{timeframe}',
            'timeframe': timeframe,
            'total_analyzed': len(volatility_data),
            'top_pairs': top_pairs
        }
        
    except Exception as e:
        logger.error(f"API: Error fetching top volatility: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-marketcap", summary="Get top pairs by market cap")
async def get_top_marketcap(limit: int = 10) -> Dict[str, Any]:
    """
    Get top N pairs by market capitalization.
    
    **Criteria:** Most liquid/established coins
    **Recommended timeframe:** 4h
    """
    try:
        logger.info(f"API: Fetching top {limit} pairs by market cap")
        
        # Top market cap coins (hardcoded for now - could fetch from CoinGecko)
        top_marketcap = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
            'ADA/USDT', 'AVAX/USDT', 'DOGE/USDT', 'DOT/USDT', 'MATIC/USDT',
            'LTC/USDT', 'LINK/USDT', 'UNI/USDT', 'ATOM/USDT', 'ETC/USDT'
        ]
        
        # Verify pairs exist on Binance
        import ccxt
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        
        markets = exchange.load_markets()
        available = [p for p in top_marketcap[:limit] if p in markets]
        
        await exchange.close()
        
        return {
            'criteria': 'marketcap_4h',
            'total': len(available),
            'pairs': [{'symbol': s, 'rank': i+1} for i, s in enumerate(available)]
        }
        
    except Exception as e:
        logger.error(f"API: Error fetching top market cap: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-select", summary="Auto-select pairs by criteria")
async def auto_select_pairs(request: TopPairsRequest) -> Dict[str, Any]:
    """
    Automatically select and enable pairs by criteria.
    
    **Criteria:**
    - `volatility_5m`: Top volatile pairs for 5m timeframe
    - `volatility_1h`: Top volatile pairs for 1h timeframe
    - `marketcap_4h`: Top market cap pairs for 4h timeframe
    
    **Replaces** currently enabled auto-selected pairs.
    """
    try:
        logger.info(f"API: Auto-selecting pairs by {request.criteria}")
        
        # Get top pairs by criteria
        if request.criteria == 'volatility_5m':
            result = await get_top_volatility(timeframe='5m', limit=request.limit)
            symbols = [p['symbol'] for p in result['top_pairs']]
            timeframe = '5m'
        elif request.criteria == 'volatility_1h':
            result = await get_top_volatility(timeframe='1h', limit=request.limit)
            symbols = [p['symbol'] for p in result['top_pairs']]
            timeframe = '1h'
        elif request.criteria == 'marketcap_4h':
            result = await get_top_marketcap(limit=request.limit)
            symbols = [p['symbol'] for p in result['pairs']]
            timeframe = '4h'
        else:
            raise HTTPException(status_code=400, detail=f"Unknown criteria: {request.criteria}")
        
        # Disable old auto-selected pairs
        all_pairs = pair_storage.get_all_pairs()
        auto_selected = [p['symbol'] for p in all_pairs if p.get('auto_selected')]
        if auto_selected:
            pair_storage.bulk_disable_pairs(auto_selected)
        
        # Enable new pairs
        for symbol in symbols:
            pair_storage.add_pair(
                symbol, 
                timeframe=timeframe,
                enabled=True,
                auto_selected=True,
                selection_criteria=request.criteria
            )
        
        return {
            'success': True,
            'criteria': request.criteria,
            'replaced': len(auto_selected),
            'enabled': symbols,
            'message': f'Auto-selected {len(symbols)} pairs by {request.criteria}'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Error auto-selecting pairs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades/active", summary="Get active trades")
async def get_active_trades(symbol: Optional[str] = None) -> Dict[str, Any]:
    """
    Get currently active trades.
    
    **Filters:**
    - `symbol`: Get trades for specific pair (optional)
    
    **Returns:** All open positions with entry, SL, TP info.
    """
    try:
        trades = pair_storage.get_active_trades(symbol)
        
        return {
            'total': len(trades),
            'symbol_filter': symbol,
            'trades': trades
        }
        
    except Exception as e:
        logger.error(f"API: Error fetching active trades: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", summary="Get pair management statistics")
async def get_stats() -> Dict[str, Any]:
    """Get overall statistics."""
    try:
        stats = pair_storage.get_statistics()
        enabled_pairs = pair_storage.get_enabled_pairs()
        
        return {
            **stats,
            'enabled_symbols': [p['symbol'] for p in enabled_pairs]
        }
        
    except Exception as e:
        logger.error(f"API: Error fetching stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ['router']
