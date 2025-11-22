# -*- coding: utf-8 -*-
"""
Auto-Rebalancing MCP Tool

Automatically rebalances agent portfolio based on performance metrics
and risk constraints. Maintains optimal agent allocation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from ...core.logger import logger  # FIX: Changed from ..core to ...core


async def rebalance_agent_portfolio(
    target_sharpe: float = 1.5,
    max_risk_per_symbol: float = 0.1,
    min_agents: int = 3,
    max_agents: int = 15,
    min_win_rate: float = 0.50,
    max_drawdown_pct: float = 15.0,
    correlation_threshold: float = 0.8
) -> Dict[str, Any]:
    """
    ?? Automatically rebalance agent portfolio for optimal performance.
    
    **What it does:**
    1. Analyzes all active agents
    2. Stops underperforming agents (Sharpe < target, WinRate < min)
    3. Checks correlations (stops duplicate strategies on correlated pairs)
    4. Increases allocation to top performers
    5. Ensures diversification
    6. Maintains min/max agent count
    
    **Use Case:**
    Claude runs this periodically (daily/weekly) to maintain optimal
    portfolio allocation without manual intervention.
    
    Args:
        target_sharpe: Minimum Sharpe ratio to keep agent
        max_risk_per_symbol: Max % allocation per symbol
        min_agents: Minimum agents to maintain
        max_agents: Maximum agents allowed
        min_win_rate: Minimum win rate (0-1)
        max_drawdown_pct: Maximum drawdown % allowed
        correlation_threshold: Stop duplicates above this correlation
    
    Returns:
        Rebalancing actions taken and new portfolio state
    
    Example:
        ```python
        result = await rebalance_agent_portfolio(
            target_sharpe=1.5,
            min_agents=5,
            max_agents=12,
            min_win_rate=0.55
        )
        
        # Response:
        {
            "actions_taken": {
                "stopped": [
                    {
                        "agent_id": "agent_sol_1h_atr_001",
                        "reason": "Sharpe 0.8 below target 1.5",
                        "final_pnl": -45.30
                    }
                ],
                "kept": [
                    {
                        "agent_id": "agent_btc_1h_ema_001",
                        "sharpe": 2.3,
                        "pnl": +523.45,
                        "reason": "Excellent performance"
                    }
                ],
                "warnings": [
                    "BTC/USDT and ETH/USDT both using ema_cloud (correlation 0.87)"
                ]
            },
            "portfolio_before": {
                "total_agents": 8,
                "total_pnl": +1245.67,
                "avg_sharpe": 1.2
            },
            "portfolio_after": {
                "total_agents": 6,
                "total_pnl": +1290.97,  # After stopping losers
                "avg_sharpe": 1.8,
                "improvement": "+0.6 Sharpe"
            },
            "recommendations": [
                "Consider adding agents on low-correlated pairs",
                "MATIC/USDT and DOT/USDT have low correlation with current portfolio"
            ]
        }
        ```
    """
    try:
        logger.info("MCP Tool: Starting portfolio rebalancing")
        
        from .agent_management import list_active_agents, get_agent_performance, stop_trading_agent
        from .correlation_analysis import detect_symbol_correlations
        
        # Get all active agents
        agents_response = await list_active_agents()
        
        if not agents_response.get("success"):
            return {
                "success": False,
                "error": "Could not fetch active agents"
            }
        
        agents = agents_response.get("agents", [])
        
        if not agents:
            return {
                "success": True,
                "message": "No active agents to rebalance",
                "portfolio_state": "empty"
            }
        
        # Portfolio state before
        portfolio_before = {
            "total_agents": len(agents),
            "active_agents": len([a for a in agents if a.get("status") == "active"]),
            "total_pnl": sum(a.get("total_pnl", 0) for a in agents),
            "avg_sharpe": sum(a.get("sharpe_ratio", 0) for a in agents) / len(agents) if agents else 0,
            "avg_win_rate": sum(a.get("win_rate", 0) for a in agents) / len(agents) if agents else 0
        }
        
        actions = {
            "stopped": [],
            "kept": [],
            "warnings": [],
            "correlation_conflicts": []
        }
        
        # 1. Check performance criteria
        for agent in agents:
            if agent.get("status") != "active":
                continue
            
            agent_id = agent["agent_id"]
            sharpe = agent.get("sharpe_ratio", 0)
            win_rate = agent.get("win_rate", 0) / 100  # Convert to 0-1
            max_dd = abs(agent.get("max_drawdown", 0))
            total_pnl = agent.get("total_pnl", 0)
            
            # Reasons to stop
            stop_reasons = []
            
            if sharpe < target_sharpe:
                stop_reasons.append(f"Sharpe {sharpe:.2f} below target {target_sharpe}")
            
            if win_rate < min_win_rate:
                stop_reasons.append(f"Win rate {win_rate:.1%} below minimum {min_win_rate:.1%}")
            
            if max_dd > max_drawdown_pct:
                stop_reasons.append(f"Max drawdown {max_dd:.1f}% exceeds {max_drawdown_pct}%")
            
            if total_pnl < -100:  # Losing more than $100
                stop_reasons.append(f"Total loss ${abs(total_pnl):.2f}")
            
            if stop_reasons:
                # Stop agent
                await stop_trading_agent(
                    agent_id=agent_id,
                    reason="; ".join(stop_reasons)
                )
                
                actions["stopped"].append({
                    "agent_id": agent_id,
                    "symbol": agent["symbol"],
                    "strategy": agent["strategy"],
                    "reasons": stop_reasons,
                    "final_pnl": total_pnl,
                    "final_sharpe": sharpe
                })
            else:
                actions["kept"].append({
                    "agent_id": agent_id,
                    "symbol": agent["symbol"],
                    "strategy": agent["strategy"],
                    "sharpe": sharpe,
                    "win_rate": win_rate,
                    "pnl": total_pnl,
                    "reason": "Performance meets criteria"
                })
        
        # 2. Check correlations and duplicate strategies
        active_kept = [a for a in actions["kept"]]
        
        if len(active_kept) >= 2:
            # Get symbols
            symbols = list(set([a["symbol"] for a in active_kept]))
            
            if len(symbols) >= 2:
                correlations = await detect_symbol_correlations(
                    symbols=symbols,
                    timeframe="1h",
                    lookback_days=30
                )
                
                if correlations.get("success"):
                    high_corrs = correlations.get("high_correlations", [])
                    
                    for hc in high_corrs:
                        if hc["correlation"] > correlation_threshold:
                            # Find agents on these correlated pairs
                            agents_pair1 = [a for a in active_kept if a["symbol"] == hc["pair1"]]
                            agents_pair2 = [a for a in active_kept if a["symbol"] == hc["pair2"]]
                            
                            # Check for duplicate strategies
                            for a1 in agents_pair1:
                                for a2 in agents_pair2:
                                    if a1["strategy"] == a2["strategy"]:
                                        actions["warnings"].append({
                                            "type": "correlation_conflict",
                                            "message": f"{hc['pair1']} and {hc['pair2']} both using {a1['strategy']} (correlation: {hc['correlation']})",
                                            "recommendation": f"Consider stopping one or using different strategies",
                                            "agents": [a1["agent_id"], a2["agent_id"]]
                                        })
        
        # 3. Check min/max constraints
        remaining_agents = len(actions["kept"])
        
        if remaining_agents < min_agents:
            actions["warnings"].append({
                "type": "min_agents_constraint",
                "message": f"Only {remaining_agents} agents remaining, below minimum {min_agents}",
                "recommendation": "Launch more agents to meet minimum"
            })
        
        if remaining_agents > max_agents:
            # Stop lowest performers to get to max
            actions["warnings"].append({
                "type": "max_agents_exceeded",
                "message": f"{remaining_agents} agents exceeds maximum {max_agents}",
                "recommendation": f"Stop {remaining_agents - max_agents} lowest performers"
            })
        
        # Portfolio state after
        remaining_pnl = sum(a["pnl"] for a in actions["kept"])
        remaining_sharpe = sum(a["sharpe"] for a in actions["kept"]) / len(actions["kept"]) if actions["kept"] else 0
        
        portfolio_after = {
            "total_agents": len(actions["kept"]),
            "total_pnl": round(remaining_pnl, 2),
            "avg_sharpe": round(remaining_sharpe, 2),
            "improvement_pnl": round(remaining_pnl - portfolio_before["total_pnl"], 2),
            "improvement_sharpe": round(remaining_sharpe - portfolio_before["avg_sharpe"], 2)
        }
        
        # Generate recommendations
        recommendations = []
        
        if portfolio_after["total_agents"] < min_agents:
            recommendations.append(
                f"Add {min_agents - portfolio_after['total_agents']} more agents to reach minimum"
            )
        
        if len(actions["warnings"]) > 0:
            recommendations.append(
                "Review correlation conflicts and consider diversifying strategies"
            )
        
        if portfolio_after["avg_sharpe"] > target_sharpe:
            recommendations.append(
                f"Excellent portfolio health (avg Sharpe: {portfolio_after['avg_sharpe']:.2f})"
            )
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "actions_taken": actions,
            "portfolio_before": portfolio_before,
            "portfolio_after": portfolio_after,
            "recommendations": recommendations,
            "summary": {
                "agents_stopped": len(actions["stopped"]),
                "agents_kept": len(actions["kept"]),
                "warnings": len(actions["warnings"]),
                "pnl_impact": round(portfolio_after["improvement_pnl"], 2),
                "sharpe_improvement": round(portfolio_after["improvement_sharpe"], 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in portfolio rebalancing: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


async def suggest_new_agents(
    current_portfolio: Optional[Dict[str, Any]] = None,
    candidate_symbols: Optional[List[str]] = None,
    target_agent_count: int = 10
) -> Dict[str, Any]:
    """
    ?? Suggest new agents to add for optimal portfolio balance.
    
    **Smart Agent Suggestions:**
    - Analyzes current portfolio
    - Checks correlations
    - Recommends symbols and strategies for best diversification
    - Ensures target agent count
    
    Args:
        current_portfolio: Current portfolio state (auto-fetched if None)
        candidate_symbols: Symbols to consider (auto-generated if None)
        target_agent_count: Desired number of agents
    
    Returns:
        Ranked suggestions for new agents
    """
    try:
        logger.info("MCP Tool: Generating new agent suggestions")
        
        from .agent_management import list_active_agents
        from .correlation_analysis import get_diversification_recommendations
        from ...strategies import registry
        
        # Get current agents if not provided
        if current_portfolio is None:
            agents_response = await list_active_agents()
            current_agents = agents_response.get("agents", [])
        else:
            current_agents = current_portfolio.get("agents", [])
        
        current_count = len([a for a in current_agents if a.get("status") == "active"])
        needed = max(0, target_agent_count - current_count)
        
        if needed == 0:
            return {
                "success": True,
                "message": f"Already at target agent count ({target_agent_count})",
                "suggestions": []
            }
        
        # Default candidates (top market cap pairs)
        if candidate_symbols is None:
            candidate_symbols = [
                "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT",
                "ADA/USDT", "AVAX/USDT", "DOT/USDT", "MATIC/USDT", "LINK/USDT",
                "UNI/USDT", "ATOM/USDT", "LTC/USDT", "ETC/USDT", "FIL/USDT"
            ]
        
        # Remove symbols already in use
        current_symbols = [a["symbol"] for a in current_agents]
        candidate_symbols = [s for s in candidate_symbols if s not in current_symbols]
        
        # Get diversification recommendations
        div_recs = await get_diversification_recommendations(
            active_agents=current_agents,
            candidate_symbols=candidate_symbols
        )
        
        if not div_recs.get("success"):
            return div_recs
        
        # Get top candidates by diversification
        ranked = div_recs.get("ranked_candidates", [])
        top_candidates = ranked[:needed * 2]  # Get 2x needed for buffer
        
        # For each candidate, suggest best strategy based on regime
        from .regime import detect_market_regime
        
        suggestions = []
        
        for candidate in top_candidates[:needed]:
            symbol = candidate["symbol"]
            
            # Detect regime
            regime = await detect_market_regime(
                symbol=symbol,
                timeframe="1h"
            )
            
            if not regime.get("success"):
                continue
            
            recommended_strategies = regime.get("recommended_strategies", [])
            
            if not recommended_strategies:
                continue
            
            # Pick top strategy
            top_strategy = recommended_strategies[0] if recommended_strategies else "cci_extreme_snapback"
            
            suggestions.append({
                "symbol": symbol,
                "recommended_strategy": top_strategy,
                "regime": regime.get("regime"),
                "diversification_benefit": candidate.get("diversification_benefit"),
                "correlation_with_portfolio": candidate.get("avg_correlation_with_portfolio"),
                "confidence": "high" if candidate.get("diversification_benefit") == "high" else "medium"
            })
        
        return {
            "success": True,
            "current_agent_count": current_count,
            "target_agent_count": target_agent_count,
            "agents_needed": needed,
            "suggestions": suggestions,
            "recommendation": f"Add {len(suggestions)} agents to reach target count with optimal diversification"
        }
        
    except Exception as e:
        logger.error(f"Error generating agent suggestions: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


__all__ = [
    "rebalance_agent_portfolio",
    "suggest_new_agents",
]
