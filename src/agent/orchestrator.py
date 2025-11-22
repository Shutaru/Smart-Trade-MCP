# -*- coding: utf-8 -*-
"""
Agent Orchestrator

Manages multiple autonomous trading agents.
Each agent is a dedicated process for one symbol + timeframe + strategy.
"""

import asyncio
import multiprocessing
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from uuid import uuid4
import signal
import sys

from ..core.logger import logger
from .trading_agent import TradingAgent
from .agent_storage import AgentStorage


class AgentOrchestrator:
    """
    Central orchestrator for managing multiple trading agents.
    
    Responsibilities:
    - Launch new agents
    - Stop existing agents
    - Monitor agent performance
    - Persist agent state to database
    """
    
    def __init__(self, db_path: Path = Path("data/agents.db")):
        """Initialize orchestrator."""
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.storage = AgentStorage(db_path)
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        logger.info("=" * 80)
        logger.info("AGENT ORCHESTRATOR - INITIALIZED")
        logger.info("=" * 80)
    
    async def launch_agent(
        self,
        symbol: str,
        timeframe: str,
        strategy: str,
        params: Dict[str, Any],
        risk_per_trade: float = 0.02,
        scan_interval_minutes: int = 15
    ) -> str:
        """
        Launch a new dedicated trading agent.
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe
            strategy: Strategy name
            params: Strategy parameters (optimized)
            risk_per_trade: Risk per trade
            scan_interval_minutes: Scan frequency
        
        Returns:
            agent_id
        """
        # Generate unique agent ID
        agent_id = self._generate_agent_id(symbol, timeframe, strategy)
        
        logger.info(f"?? Launching agent: {agent_id}")
        logger.info(f"   Symbol: {symbol}")
        logger.info(f"   Timeframe: {timeframe}")
        logger.info(f"   Strategy: {strategy}")
        logger.info(f"   Scan interval: {scan_interval_minutes} min")
        
        # Create agent configuration
        agent_config = {
            "agent_id": agent_id,
            "symbol": symbol,
            "timeframe": timeframe,
            "strategy": strategy,
            "params": params,
            "risk_per_trade": risk_per_trade,
            "scan_interval_minutes": scan_interval_minutes
        }
        
        # Save to database
        self.storage.add_agent(agent_config)
        
        # Create agent instance
        agent = TradingAgent(**agent_config)
        
        # Start agent process
        process = multiprocessing.Process(
            target=agent.run,
            name=f"Agent-{agent_id}"
        )
        process.start()
        
        # Store agent info
        self.agents[agent_id] = {
            "agent": agent,
            "process": process,
            "config": agent_config,
            "started_at": datetime.now(),
            "status": "active"
        }
        
        logger.info(f"? Agent {agent_id} launched (PID: {process.pid})")
        
        return agent_id
    
    def stop_agent(self, agent_id: str, reason: Optional[str] = None):
        """
        Stop a running agent.
        
        Args:
            agent_id: Agent to stop
            reason: Reason for stopping
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        logger.info(f"?? Stopping agent: {agent_id}")
        if reason:
            logger.info(f"   Reason: {reason}")
        
        agent_info = self.agents[agent_id]
        
        # Terminate process
        if agent_info["process"].is_alive():
            agent_info["process"].terminate()
            agent_info["process"].join(timeout=5)
            
            # Force kill if still alive
            if agent_info["process"].is_alive():
                agent_info["process"].kill()
        
        # Update status
        agent_info["status"] = "stopped"
        agent_info["stopped_at"] = datetime.now()
        agent_info["stop_reason"] = reason
        
        # Update database
        self.storage.update_status(agent_id, "stopped", reason)
        
        logger.info(f"? Agent {agent_id} stopped")
    
    def get_agent_info(self, agent_id: str) -> Dict[str, Any]:
        """Get basic agent info."""
        if agent_id not in self.agents:
            return self.storage.get_agent(agent_id)
        
        agent_info = self.agents[agent_id]
        
        return {
            "agent_id": agent_id,
            "symbol": agent_info["config"]["symbol"],
            "timeframe": agent_info["config"]["timeframe"],
            "strategy": agent_info["config"]["strategy"],
            "status": agent_info["status"],
            "pid": agent_info["process"].pid if agent_info["process"].is_alive() else None,
            "started_at": agent_info["started_at"].isoformat(),
            "is_alive": agent_info["process"].is_alive()
        }
    
    def get_agent_performance(self, agent_id: str) -> Dict[str, Any]:
        """Get detailed performance metrics for an agent."""
        # Get from database
        trades = self.storage.get_agent_trades(agent_id)
        
        if not trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "sharpe_ratio": 0,
                "max_drawdown": 0
            }
        
        # Calculate metrics
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t["pnl"] > 0)
        losing_trades = sum(1 for t in trades if t["pnl"] < 0)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = sum(t["pnl"] for t in trades)
        
        wins = [t["pnl"] for t in trades if t["pnl"] > 0]
        losses = [t["pnl"] for t in trades if t["pnl"] < 0]
        
        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        # Calculate Sharpe ratio (simplified)
        import numpy as np
        returns = [t["pnl"] for t in trades]
        sharpe = (np.mean(returns) / np.std(returns)) if len(returns) > 1 else 0
        
        # Max drawdown
        cumulative_pnl = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative_pnl)
        drawdown = cumulative_pnl - running_max
        max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0
        
        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": round(win_rate, 2),
            "total_pnl": round(total_pnl, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "sharpe_ratio": round(sharpe, 2),
            "max_drawdown": round(max_drawdown, 2),
            "profit_factor": round(abs(sum(wins) / sum(losses)), 2) if losses else 0
        }
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get status of all agents."""
        agents = []
        
        # Get from memory
        for agent_id, info in self.agents.items():
            agent_data = {
                "agent_id": agent_id,
                **info["config"],
                "status": info["status"],
                "pid": info["process"].pid if info["process"].is_alive() else None,
                "started_at": info["started_at"].isoformat(),
                "is_alive": info["process"].is_alive()
            }
            
            # Add performance
            perf = self.get_agent_performance(agent_id)
            agent_data.update(perf)
            
            agents.append(agent_data)
        
        # Also get stopped agents from database
        stopped = self.storage.get_stopped_agents()
        for agent in stopped:
            if agent["agent_id"] not in self.agents:
                perf = self.get_agent_performance(agent["agent_id"])
                agent.update(perf)
                agents.append(agent)
        
        return agents
    
    def update_agent_params(self, agent_id: str, params: Dict[str, Any]):
        """
        Update agent parameters on-the-fly.
        
        Note: This requires agent to support hot-reload.
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Update config
        self.agents[agent_id]["config"]["params"].update(params)
        
        # Update database
        self.storage.update_params(agent_id, params)
        
        # Signal agent to reload (if supported)
        # TODO: Implement IPC for parameter updates
        
        logger.info(f"? Updated params for agent {agent_id}")
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get high-level portfolio summary."""
        agents = self.get_all_agents()
        
        if not agents:
            return {
                "total_agents": 0,
                "active_agents": 0,
                "total_pnl": 0,
                "total_trades": 0,
                "overall_win_rate": 0
            }
        
        active = [a for a in agents if a["status"] == "active"]
        
        total_pnl = sum(a.get("total_pnl", 0) for a in agents)
        total_trades = sum(a.get("total_trades", 0) for a in agents)
        total_wins = sum(a.get("winning_trades", 0) for a in agents)
        
        overall_win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
        
        # Best and worst agents
        agents_with_pnl = [a for a in agents if a.get("total_pnl", 0) != 0]
        best_agent = max(agents_with_pnl, key=lambda x: x.get("total_pnl", 0)) if agents_with_pnl else None
        worst_agent = min(agents_with_pnl, key=lambda x: x.get("total_pnl", 0)) if agents_with_pnl else None
        
        return {
            "total_agents": len(agents),
            "active_agents": len(active),
            "stopped_agents": len(agents) - len(active),
            "total_pnl": round(total_pnl, 2),
            "total_trades": total_trades,
            "overall_win_rate": round(overall_win_rate, 2),
            "best_agent": {
                "agent_id": best_agent["agent_id"],
                "symbol": best_agent["symbol"],
                "strategy": best_agent["strategy"],
                "pnl": best_agent["total_pnl"]
            } if best_agent else None,
            "worst_agent": {
                "agent_id": worst_agent["agent_id"],
                "symbol": worst_agent["symbol"],
                "strategy": worst_agent["strategy"],
                "pnl": worst_agent["total_pnl"]
            } if worst_agent else None
        }
    
    def _generate_agent_id(self, symbol: str, timeframe: str, strategy: str) -> str:
        """Generate unique agent ID."""
        symbol_clean = symbol.replace("/", "_").replace(":", "_")
        unique_suffix = uuid4().hex[:6]
        return f"agent_{symbol_clean}_{timeframe}_{strategy}_{unique_suffix}"
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals - stop all agents gracefully."""
        logger.info("Orchestrator received shutdown signal")
        self.shutdown()
        sys.exit(0)
    
    def shutdown(self):
        """Gracefully shutdown all agents."""
        logger.info("=" * 80)
        logger.info("SHUTTING DOWN ORCHESTRATOR")
        logger.info("=" * 80)
        
        for agent_id in list(self.agents.keys()):
            try:
                self.stop_agent(agent_id, reason="Orchestrator shutdown")
            except Exception as e:
                logger.error(f"Error stopping agent {agent_id}: {e}")
        
        logger.info("? All agents stopped")


if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def test():
        orchestrator = AgentOrchestrator()
        
        # Launch test agent
        agent_id = await orchestrator.launch_agent(
            symbol="BTC/USDT",
            timeframe="1h",
            strategy="cci_extreme_snapback",
            params={"cci_period": 20},
            scan_interval_minutes=1
        )
        
        print(f"Launched: {agent_id}")
        
        # Wait a bit
        await asyncio.sleep(5)
        
        # Get performance
        perf = orchestrator.get_agent_performance(agent_id)
        print(f"Performance: {perf}")
        
        # Stop agent
        orchestrator.stop_agent(agent_id, "Test complete")
    
    asyncio.run(test())
