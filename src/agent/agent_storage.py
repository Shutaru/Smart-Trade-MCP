# -*- coding: utf-8 -*-
"""
Agent Storage

Database for storing agent configurations, trades, and performance metrics.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from contextlib import contextmanager

from ..core.logger import logger


class AgentStorage:
    """Storage for agent management and performance tracking."""
    
    def __init__(self, db_path: Path = Path("data/agents.db")):
        """Initialize agent storage."""
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()
        logger.info(f"Agent storage initialized: {db_path}")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _create_tables(self):
        """Create database tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Agents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    params TEXT,
                    risk_per_trade REAL,
                    scan_interval_minutes INTEGER,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    stopped_at TIMESTAMP,
                    stop_reason TEXT
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_status ON agents(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_symbol ON agents(symbol)")
            
            # Trades table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    entry_time TIMESTAMP NOT NULL,
                    stop_loss REAL NOT NULL,
                    take_profit REAL NOT NULL,
                    quantity REAL NOT NULL,
                    exit_price REAL,
                    exit_time TIMESTAMP,
                    pnl REAL,
                    status TEXT DEFAULT 'open',
                    notes TEXT,
                    FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trade_agent ON agent_trades(agent_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trade_status ON agent_trades(status)")
            
            conn.commit()
    
    # ========== AGENT MANAGEMENT ==========
    
    def add_agent(self, config: Dict[str, Any]):
        """Add a new agent to database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO agents 
                (agent_id, symbol, timeframe, strategy, params, 
                 risk_per_trade, scan_interval_minutes, started_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                config["agent_id"],
                config["symbol"],
                config["timeframe"],
                config["strategy"],
                json.dumps(config.get("params", {})),
                config.get("risk_per_trade", 0.02),
                config.get("scan_interval_minutes", 15),
                datetime.now()
            ))
            
            conn.commit()
            logger.info(f"Added agent to database: {config['agent_id']}")
    
    def update_status(self, agent_id: str, status: str, reason: Optional[str] = None):
        """Update agent status."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if status == "stopped":
                cursor.execute("""
                    UPDATE agents 
                    SET status = ?, stopped_at = ?, stop_reason = ?
                    WHERE agent_id = ?
                """, (status, datetime.now(), reason, agent_id))
            else:
                cursor.execute("""
                    UPDATE agents 
                    SET status = ?
                    WHERE agent_id = ?
                """, (status, agent_id))
            
            conn.commit()
    
    def update_params(self, agent_id: str, params: Dict[str, Any]):
        """Update agent parameters."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get current params
            cursor.execute("SELECT params FROM agents WHERE agent_id = ?", (agent_id,))
            row = cursor.fetchone()
            
            if row:
                current_params = json.loads(row["params"]) if row["params"] else {}
                current_params.update(params)
                
                cursor.execute("""
                    UPDATE agents 
                    SET params = ?
                    WHERE agent_id = ?
                """, (json.dumps(current_params), agent_id))
                
                conn.commit()
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent configuration."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM agents WHERE agent_id = ?", (agent_id,))
            row = cursor.fetchone()
            
            if row:
                agent = dict(row)
                if agent["params"]:
                    agent["params"] = json.loads(agent["params"])
                return agent
            
            return None
    
    def get_active_agents(self) -> List[Dict[str, Any]]:
        """Get all active agents."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM agents WHERE status = 'active' ORDER BY created_at DESC")
            
            agents = []
            for row in cursor.fetchall():
                agent = dict(row)
                if agent["params"]:
                    agent["params"] = json.loads(agent["params"])
                agents.append(agent)
            
            return agents
    
    def get_stopped_agents(self) -> List[Dict[str, Any]]:
        """Get all stopped agents."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM agents WHERE status = 'stopped' ORDER BY stopped_at DESC")
            
            agents = []
            for row in cursor.fetchall():
                agent = dict(row)
                if agent["params"]:
                    agent["params"] = json.loads(agent["params"])
                agents.append(agent)
            
            return agents
    
    # ========== TRADE MANAGEMENT ==========
    
    def add_trade(
        self,
        agent_id: str,
        symbol: str,
        direction: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        quantity: float
    ) -> int:
        """Add a new trade."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO agent_trades 
                (agent_id, symbol, direction, entry_price, entry_time,
                 stop_loss, take_profit, quantity, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open')
            """, (
                agent_id,
                symbol,
                direction,
                entry_price,
                datetime.now(),
                stop_loss,
                take_profit,
                quantity
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def close_trade(
        self,
        agent_id: str,
        symbol: str,
        exit_price: float,
        pnl: float,
        notes: Optional[str] = None
    ):
        """Close the most recent open trade for an agent/symbol."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Find latest open trade
            cursor.execute("""
                SELECT id FROM agent_trades 
                WHERE agent_id = ? AND symbol = ? AND status = 'open'
                ORDER BY entry_time DESC
                LIMIT 1
            """, (agent_id, symbol))
            
            row = cursor.fetchone()
            
            if row:
                cursor.execute("""
                    UPDATE agent_trades 
                    SET exit_price = ?, exit_time = ?, pnl = ?, status = 'closed', notes = ?
                    WHERE id = ?
                """, (exit_price, datetime.now(), pnl, notes, row["id"]))
                
                conn.commit()
    
    def get_agent_trades(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all trades for an agent."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM agent_trades 
                WHERE agent_id = ?
                ORDER BY entry_time DESC
            """, (agent_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_open_trades(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all open trades."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if agent_id:
                cursor.execute("""
                    SELECT * FROM agent_trades 
                    WHERE agent_id = ? AND status = 'open'
                    ORDER BY entry_time DESC
                """, (agent_id,))
            else:
                cursor.execute("""
                    SELECT * FROM agent_trades 
                    WHERE status = 'open'
                    ORDER BY entry_time DESC
                """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total agents
            cursor.execute("SELECT COUNT(*) as count FROM agents")
            total_agents = cursor.fetchone()["count"]
            
            # Active agents
            cursor.execute("SELECT COUNT(*) as count FROM agents WHERE status = 'active'")
            active_agents = cursor.fetchone()["count"]
            
            # Total trades
            cursor.execute("SELECT COUNT(*) as count FROM agent_trades")
            total_trades = cursor.fetchone()["count"]
            
            # Total PnL
            cursor.execute("SELECT SUM(pnl) as total FROM agent_trades WHERE status = 'closed'")
            total_pnl = cursor.fetchone()["total"] or 0
            
            return {
                "total_agents": total_agents,
                "active_agents": active_agents,
                "stopped_agents": total_agents - active_agents,
                "total_trades": total_trades,
                "total_pnl": round(total_pnl, 2)
            }


if __name__ == "__main__":
    # Test storage
    storage = AgentStorage(Path("data/agents_test.db"))
    
    # Add test agent
    storage.add_agent({
        "agent_id": "test_001",
        "symbol": "BTC/USDT",
        "timeframe": "1h",
        "strategy": "cci_extreme_snapback",
        "params": {"cci_period": 20}
    })
    
    # Add test trade
    trade_id = storage.add_trade(
        agent_id="test_001",
        symbol="BTC/USDT",
        direction="long",
        entry_price=95000.0,
        stop_loss=93000.0,
        take_profit=99000.0,
        quantity=0.1
    )
    
    print(f"Trade ID: {trade_id}")
    
    # Get stats
    stats = storage.get_statistics()
    print(f"Stats: {stats}")
