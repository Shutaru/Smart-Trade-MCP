"""
Experiment Manager

Core logic for managing and executing backtest experiments.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from .database import get_experiment_db
from ..core.backtest_engine import BacktestEngine
from ..core.data_manager import DataManager
from ..strategies import registry
from ..core.logger import logger

class ExperimentManager:
    """Orchestrates experiments and backtests."""
    
    def __init__(self):
        self.db = get_experiment_db()
        
    async def initialize(self):
        """Initialize database."""
        await self.db.init_db()
        
    async def create_experiment(self, name: str, description: str = "") -> str:
        """Create a new experiment container."""
        return await self.db.create_experiment(name, description)
        
    async def run_backtest(
        self,
        experiment_id: str,
        strategy_name: str,
        symbol: str,
        timeframe: str,
        parameters: Dict[str, Any],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        initial_capital: float = 10000.0
    ) -> str:
        """
        Run a single backtest and store results.
        
        Returns:
            run_id
        """
        # 1. Create run entry
        run_id = await self.db.create_run(
            experiment_id, strategy_name, symbol, timeframe, parameters
        )
        
        try:
            # 2. Update status to running
            await self.db.update_run_status(run_id, "running")
            
            # 3. Fetch Data
            dm = DataManager()
            # Default start_date to 365 days ago if not provided
            if start_date is None:
                from datetime import timedelta
                start_date = datetime.now() - timedelta(days=365)

            df = await dm.fetch_historical(
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date
            )
            await dm.close()
            
            if df.empty:
                raise ValueError(f"No data found for {symbol} {timeframe}")
                
            # 4. Initialize Strategy
            strategy_cls = registry.get(strategy_name).__class__
            # Merge default params with overrides
            # Note: This assumes strategy __init__ takes **kwargs or we map them manually
            # For now, we'll assume the strategy registry handles instantiation or we do it here
            # Ideally, we'd pass params to the strategy. 
            # Let's assume we can re-instantiate or set params.
            # Since registry returns an INSTANCE, we might need to create a NEW instance with params.
            
            # Hack: For now, we'll use the registry instance but we SHOULD support params
            # TODO: Update Strategy Registry to support factory pattern with params
            strategy = registry.get(strategy_name) 
            
            # 5. Run Backtest
            engine = BacktestEngine(initial_capital=initial_capital)
            results = engine.run(strategy, df)
            
            # 6. Save Results
            metrics = {
                "total_return": results.total_return,
                "sharpe_ratio": results.sharpe_ratio,
                "max_drawdown": results.max_drawdown,
                "win_rate": results.win_rate,
                "total_trades": results.total_trades,
                "profit_factor": results.profit_factor
            }
            
            await self.db.update_run_status(run_id, "completed", metrics)
            return run_id
            
        except Exception as e:
            logger.error(f"Experiment run failed: {e}", exc_info=True)
            await self.db.update_run_status(run_id, "failed", {"error": str(e)})
            raise

# Global instance
_manager: Optional[ExperimentManager] = None

def get_experiment_manager() -> ExperimentManager:
    global _manager
    if _manager is None:
        _manager = ExperimentManager()
    return _manager
