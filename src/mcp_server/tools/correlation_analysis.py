# -*- coding: utf-8 -*-
"""
Correlation Analysis MCP Tool

Analyzes correlations between trading pairs to enable diversification-aware
agent deployment. Prevents over-allocation to correlated assets.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from ...core.logger import logger  # FIX: Changed from ..core to ...core
from ...core.data_manager import DataManager


async def detect_symbol_correlations(
    symbols: List[str],
    timeframe: str = "1h",
    lookback_days: int = 30
) -> Dict[str, Any]:
    """
    ?? Detect correlations between multiple trading pairs.
    
    **Critical for Portfolio Diversification:**
    - Identifies highly correlated pairs (e.g., BTC/ETH often 0.8+)
    - Prevents over-concentration in similar movements
    - Enables truly diversified agent allocation
    
    **Use Case:**
    Claude analyzes correlations before launching multiple agents.
    If BTC and ETH are 90% correlated, Claude won't launch same
    strategy on both ? ensures real diversification.
    
    Args:
        symbols: List of trading pairs (e.g., ["BTC/USDT", "ETH/USDT"])
        timeframe: Timeframe for correlation analysis
        lookback_days: Days of history to analyze
    
    Returns:
        Correlation matrix and recommendations
    
    Example:
        ```python
        correlations = await detect_symbol_correlations(
            symbols=["BTC/USDT", "ETH/USDT", "SOL/USDT", "MATIC/USDT"],
            timeframe="1h",
            lookback_days=30
        )
        
        # Response:
        {
            "correlation_matrix": {
                "BTC/USDT": {"BTC/USDT": 1.0, "ETH/USDT": 0.87, "SOL/USDT": 0.72, ...},
                "ETH/USDT": {"BTC/USDT": 0.87, "ETH/USDT": 1.0, ...},
                ...
            },
            "high_correlations": [
                {"pair1": "BTC/USDT", "pair2": "ETH/USDT", "correlation": 0.87},
                {"pair1": "BTC/USDT", "pair2": "SOL/USDT", "correlation": 0.72}
            ],
            "diversification_score": 0.65,  # 0-1, higher = more diverse
            "recommendations": {
                "avoid_duplicate_strategies": ["BTC/USDT + ETH/USDT"],
                "good_diversification": ["BTC/USDT + MATIC/USDT"]
            }
        }
        ```
    """
    try:
        logger.info(f"MCP Tool: Analyzing correlations for {len(symbols)} symbols")
        
        data_manager = DataManager()
        
        # Fetch data for all symbols
        price_data = {}
        
        for symbol in symbols:
            df = await data_manager.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=lookback_days * 24 if timeframe == "1h" else lookback_days
            )
            
            if df is None or len(df) < 50:
                logger.warning(f"Insufficient data for {symbol}")
                continue
            
            # Use close prices with timestamp index
            df_indexed = df.set_index('timestamp')
            price_data[symbol] = df_indexed['close']
        
        if len(price_data) < 2:
            return {
                "success": False,
                "error": "Need at least 2 symbols with sufficient data",
                "symbols_analyzed": list(price_data.keys())
            }
        
        # Align all series to same timestamps
        price_df = pd.DataFrame(price_data)
        price_df = price_df.dropna()  # Drop rows with any NaN
        
        if len(price_df) < 50:
            return {
                "success": False,
                "error": "Insufficient overlapping data",
                "overlapping_candles": len(price_df)
            }
        
        # Calculate returns (more meaningful than raw prices)
        returns_df = price_df.pct_change().dropna()
        
        # Calculate correlation matrix
        corr_matrix = returns_df.corr()
        
        # Convert to dict format
        correlation_dict = {}
        for symbol1 in corr_matrix.index:
            correlation_dict[symbol1] = {}
            for symbol2 in corr_matrix.columns:
                correlation_dict[symbol1][symbol2] = round(float(corr_matrix.loc[symbol1, symbol2]), 3)
        
        # Find high correlations (> 0.7)
        high_correlations = []
        for i, symbol1 in enumerate(corr_matrix.index):
            for j, symbol2 in enumerate(corr_matrix.columns):
                if i < j:  # Avoid duplicates
                    corr_value = corr_matrix.loc[symbol1, symbol2]
                    if abs(corr_value) > 0.7:
                        high_correlations.append({
                            "pair1": symbol1,
                            "pair2": symbol2,
                            "correlation": round(float(corr_value), 3),
                            "strength": "very_high" if abs(corr_value) > 0.85 else "high"
                        })
        
        # Sort by correlation
        high_correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        
        # Calculate diversification score
        # Average absolute correlation (lower = more diverse)
        avg_corr = 0
        count = 0
        for i, symbol1 in enumerate(corr_matrix.index):
            for j, symbol2 in enumerate(corr_matrix.columns):
                if i < j:
                    avg_corr += abs(corr_matrix.loc[symbol1, symbol2])
                    count += 1
        
        avg_corr = avg_corr / count if count > 0 else 0
        diversification_score = 1.0 - avg_corr  # Higher = more diverse
        
        # Generate recommendations
        recommendations = {
            "avoid_duplicate_strategies": [],
            "good_diversification_pairs": [],
            "overall_assessment": ""
        }
        
        # Find pairs to avoid duplicating strategies
        for hc in high_correlations:
            if hc["correlation"] > 0.8:
                recommendations["avoid_duplicate_strategies"].append(
                    f"{hc['pair1']} + {hc['pair2']} (corr: {hc['correlation']})"
                )
        
        # Find good diversification pairs (low correlation)
        for i, symbol1 in enumerate(corr_matrix.index):
            for j, symbol2 in enumerate(corr_matrix.columns):
                if i < j:
                    corr_value = abs(corr_matrix.loc[symbol1, symbol2])
                    if corr_value < 0.5:
                        recommendations["good_diversification_pairs"].append(
                            f"{symbol1} + {symbol2} (corr: {round(float(corr_value), 3)})"
                        )
        
        # Overall assessment
        if diversification_score > 0.6:
            recommendations["overall_assessment"] = "Excellent diversification - low correlations across portfolio"
        elif diversification_score > 0.4:
            recommendations["overall_assessment"] = "Good diversification - some correlated pairs but manageable"
        else:
            recommendations["overall_assessment"] = "Poor diversification - highly correlated pairs, risk concentration"
        
        return {
            "success": True,
            "symbols_analyzed": list(price_data.keys()),
            "timeframe": timeframe,
            "lookback_days": lookback_days,
            "candles_analyzed": len(price_df),
            "correlation_matrix": correlation_dict,
            "high_correlations": high_correlations,
            "diversification_score": round(diversification_score, 3),
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in correlation analysis: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


async def get_diversification_recommendations(
    active_agents: List[Dict[str, Any]],
    candidate_symbols: List[str]
) -> Dict[str, Any]:
    """
    ?? Get recommendations for adding new agents based on current portfolio.
    
    **Smart Agent Allocation:**
    - Analyzes current agent allocation
    - Checks correlations with candidate symbols
    - Recommends which new symbols add most diversification
    
    **Use Case:**
    Claude has 5 active agents. User wants to add 3 more.
    This tool recommends which 3 symbols provide best diversification.
    
    Args:
        active_agents: Currently active agents with their symbols
        candidate_symbols: Symbols being considered for new agents
    
    Returns:
        Ranked recommendations
    
    Example:
        ```python
        recommendations = await get_diversification_recommendations(
            active_agents=[
                {"symbol": "BTC/USDT", "strategy": "ema_cloud"},
                {"symbol": "ETH/USDT", "strategy": "bb_mean_rev"}
            ],
            candidate_symbols=["SOL/USDT", "MATIC/USDT", "DOT/USDT"]
        )
        
        # Response:
        {
            "current_symbols": ["BTC/USDT", "ETH/USDT"],
            "ranked_candidates": [
                {
                    "symbol": "MATIC/USDT",
                    "avg_correlation": 0.35,
                    "diversification_benefit": "high",
                    "reason": "Low correlation with current portfolio"
                },
                {
                    "symbol": "DOT/USDT",
                    "avg_correlation": 0.62,
                    "diversification_benefit": "medium"
                },
                {
                    "symbol": "SOL/USDT",
                    "avg_correlation": 0.81,
                    "diversification_benefit": "low",
                    "reason": "High correlation with BTC/ETH"
                }
            ],
            "recommendation": "Add MATIC/USDT first for best diversification"
        }
        ```
    """
    try:
        logger.info("MCP Tool: Generating diversification recommendations")
        
        # Extract current symbols
        current_symbols = [agent["symbol"] for agent in active_agents]
        
        if not current_symbols:
            return {
                "success": True,
                "message": "No active agents - all candidates are equally valid",
                "ranked_candidates": [
                    {"symbol": s, "diversification_benefit": "new_portfolio"}
                    for s in candidate_symbols
                ]
            }
        
        # Get correlations between current and candidates
        all_symbols = list(set(current_symbols + candidate_symbols))
        
        correlations = await detect_symbol_correlations(
            symbols=all_symbols,
            timeframe="1h",
            lookback_days=30
        )
        
        if not correlations.get("success"):
            return {
                "success": False,
                "error": correlations.get("error")
            }
        
        corr_matrix = correlations["correlation_matrix"]
        
        # Rank candidates by average correlation with current portfolio
        ranked = []
        
        for candidate in candidate_symbols:
            if candidate not in corr_matrix:
                continue
            
            # Calculate average correlation with current symbols
            avg_corr = np.mean([
                abs(corr_matrix[candidate].get(current, 0))
                for current in current_symbols
            ])
            
            # Determine benefit
            if avg_corr < 0.5:
                benefit = "high"
                reason = "Low correlation with current portfolio - excellent diversification"
            elif avg_corr < 0.7:
                benefit = "medium"
                reason = "Moderate correlation - adds some diversification"
            else:
                benefit = "low"
                reason = f"High correlation with current portfolio (avg: {avg_corr:.2f})"
            
            ranked.append({
                "symbol": candidate,
                "avg_correlation_with_portfolio": round(avg_corr, 3),
                "diversification_benefit": benefit,
                "reason": reason
            })
        
        # Sort by correlation (lower = better)
        ranked.sort(key=lambda x: x["avg_correlation_with_portfolio"])
        
        # Top recommendation
        top_rec = ranked[0] if ranked else None
        
        return {
            "success": True,
            "current_portfolio": {
                "symbols": current_symbols,
                "agent_count": len(active_agents)
            },
            "ranked_candidates": ranked,
            "top_recommendation": {
                "symbol": top_rec["symbol"],
                "reason": top_rec["reason"]
            } if top_rec else None,
            "diversification_analysis": {
                "high_benefit": [r["symbol"] for r in ranked if r["diversification_benefit"] == "high"],
                "medium_benefit": [r["symbol"] for r in ranked if r["diversification_benefit"] == "medium"],
                "low_benefit": [r["symbol"] for r in ranked if r["diversification_benefit"] == "low"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


__all__ = [
    "detect_symbol_correlations",
    "get_diversification_recommendations",
]
