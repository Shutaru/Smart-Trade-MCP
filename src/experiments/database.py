"""
Experiment Database Module

Manages SQLite database for storing experiment configurations and results.
"""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import aiosqlite

from ..core.logger import logger

class ExperimentDatabase:
    """Manages experiment data persistence."""
    
    def __init__(self, db_path: Path = Path("data/experiments.db")):
        """
        Initialize experiment database.
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    async def init_db(self):
        """Initialize database tables."""
        async with aiosqlite.connect(self.db_path) as db:
            # Experiments table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS experiments (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Runs table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY,
                    experiment_id TEXT NOT NULL,
                    strategy_name TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    parameters TEXT,  -- JSON
                    metrics TEXT,     -- JSON
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (experiment_id) REFERENCES experiments (id)
                )
            """)
            
            await db.commit()
            
    async def create_experiment(self, name: str, description: str = "") -> str:
        """Create a new experiment."""
        exp_id = str(uuid.uuid4())
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO experiments (id, name, description) VALUES (?, ?, ?)",
                (exp_id, name, description)
            )
            await db.commit()
        return exp_id
        
    async def get_experiments(self) -> List[Dict[str, Any]]:
        """List all experiments."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM experiments ORDER BY created_at DESC") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
                
    async def get_experiment(self, exp_id: str) -> Optional[Dict[str, Any]]:
        """Get experiment details."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM experiments WHERE id = ?", (exp_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def create_run(
        self, 
        experiment_id: str,
        strategy_name: str,
        symbol: str,
        timeframe: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Create a new run entry."""
        run_id = str(uuid.uuid4())
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO runs 
                (id, experiment_id, strategy_name, symbol, timeframe, parameters, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id, 
                    experiment_id, 
                    strategy_name, 
                    symbol, 
                    timeframe, 
                    json.dumps(parameters),
                    "pending"
                )
            )
            await db.commit()
        return run_id
        
    async def update_run_status(
        self, 
        run_id: str, 
        status: str, 
        metrics: Optional[Dict[str, Any]] = None
    ):
        """Update run status and metrics."""
        async with aiosqlite.connect(self.db_path) as db:
            if metrics:
                await db.execute(
                    """
                    UPDATE runs 
                    SET status = ?, metrics = ?, completed_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                    """,
                    (status, json.dumps(metrics), run_id)
                )
            else:
                await db.execute(
                    "UPDATE runs SET status = ? WHERE id = ?",
                    (status, run_id)
                )
            await db.commit()
            
    async def get_runs(self, experiment_id: str) -> List[Dict[str, Any]]:
        """Get all runs for an experiment."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM runs WHERE experiment_id = ? ORDER BY created_at DESC", 
                (experiment_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                results = []
                for row in rows:
                    d = dict(row)
                    if d['parameters']:
                        d['parameters'] = json.loads(d['parameters'])
                    if d['metrics']:
                        d['metrics'] = json.loads(d['metrics'])
                    results.append(d)
                return results

# Global instance
_db: Optional[ExperimentDatabase] = None

def get_experiment_db() -> ExperimentDatabase:
    global _db
    if _db is None:
        _db = ExperimentDatabase()
    return _db
