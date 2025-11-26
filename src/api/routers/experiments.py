# -*- coding: utf-8 -*-
"""
Experiment API Router

REST API endpoints for managing backtest experiments.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from ...experiments.manager import get_experiment_manager
from ...core.logger import logger

router = APIRouter()

# --- Models ---

class CreateExperimentRequest(BaseModel):
    name: str
    description: Optional[str] = ""

class RunBacktestRequest(BaseModel):
    strategy_name: str
    symbol: str
    timeframe: str
    parameters: Dict[str, Any] = {}
    initial_capital: float = 10000.0

# --- Endpoints ---

@router.post("/", summary="Create new experiment")
async def create_experiment(request: CreateExperimentRequest):
    """Create a new experiment container."""
    try:
        manager = get_experiment_manager()
        await manager.initialize() # Ensure DB is ready
        exp_id = await manager.create_experiment(request.name, request.description)
        return {"status": "success", "experiment_id": exp_id}
    except Exception as e:
        logger.error(f"Failed to create experiment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", summary="List all experiments")
async def list_experiments():
    """List all experiments."""
    try:
        manager = get_experiment_manager()
        await manager.initialize()
        experiments = await manager.db.get_experiments()
        return {"status": "success", "experiments": experiments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{experiment_id}", summary="Get experiment details")
async def get_experiment(experiment_id: str):
    """Get experiment details and runs."""
    try:
        manager = get_experiment_manager()
        await manager.initialize()
        
        experiment = await manager.db.get_experiment(experiment_id)
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
            
        runs = await manager.db.get_runs(experiment_id)
        
        return {
            "status": "success", 
            "experiment": experiment,
            "runs": runs
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{experiment_id}/run", summary="Run backtest in experiment")
async def run_experiment_backtest(
    experiment_id: str,
    request: RunBacktestRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger a backtest run within an experiment.
    
    The backtest runs in the background.
    """
    try:
        manager = get_experiment_manager()
        await manager.initialize()
        
        # Validate experiment exists
        experiment = await manager.db.get_experiment(experiment_id)
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
            
        # We run it in background to avoid blocking API
        # But for now, let's await it to return the result immediately for simplicity
        # or we can return the run_id and let client poll.
        # Let's await it for this MVP version to ensure it works.
        
        run_id = await manager.run_backtest(
            experiment_id=experiment_id,
            strategy_name=request.strategy_name,
            symbol=request.symbol,
            timeframe=request.timeframe,
            parameters=request.parameters,
            initial_capital=request.initial_capital
        )
        
        return {
            "status": "success",
            "run_id": run_id,
            "message": "Backtest completed"
        }
        
    except Exception as e:
        logger.error(f"Failed to run backtest: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
