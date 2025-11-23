# -*- coding: utf-8 -*-
"""
MCP Tools for Async Optimization Jobs

Provides tools for starting, monitoring, and retrieving long-running optimizations.
Solves Claude Desktop's 4-minute timeout limitation.
"""

from typing import Dict, Any
import asyncio

from ...optimization.job_manager import get_job_manager, JobStatus
from ...optimization.genetic_optimizer import GeneticOptimizer
from ...optimization.config import OptimizationConfig
from ...optimization.meta_learner import ParameterMetaLearner
from ...optimization.parameter_space import ParameterSpace, ParameterDefinition, ParameterType
from ...strategies.registry import registry
from ...core.data_manager import DataManager
from ...core.indicators import calculate_all_indicators
from ...core.logger import logger
from datetime import datetime, timedelta


async def start_optimization_job(
    strategy_name: str,
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    population_size: int = 50,  # ? QUALIDADE MÁXIMA!
    n_generations: int = 20,
    use_ray: bool = False,
) -> Dict[str, Any]:
    """
    Start optimization job in background (NON-BLOCKING).
    
    ? **NO TIMEOUT:** Job runs in background, Claude can check status later!
    ? **FULL QUALITY:** Can use pop=50, gen=20 without timeout issues!
    
    Args:
        strategy_name: Strategy to optimize
        symbol: Trading pair
        timeframe: Timeframe
        population_size: Population size (50 recommended)
        n_generations: Generations (20 recommended)
        use_ray: Use Ray parallelization
        
    Returns:
        Job info with job_id for status checking
    """
    logger.info(
        f"?? Starting async optimization job: {strategy_name} on {symbol} {timeframe} "
        f"(pop={population_size}, gen={n_generations})"
    )
    
    # Create job
    job_manager = get_job_manager()
    job_id = job_manager.create_job(
        strategy_name=strategy_name,
        symbol=symbol,
        timeframe=timeframe,
        population_size=population_size,
        n_generations=n_generations,
    )
    
    # Define job execution function
    def _run_optimization(job_id: str) -> Dict[str, Any]:
        """Execute optimization (runs in background thread)"""
        
        # Get strategy
        strategy = registry.get(strategy_name)
        
        # Fetch data (async in sync context)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        dm = DataManager()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        
        df = loop.run_until_complete(dm.fetch_historical(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            max_candles=5000,
        ))
        
        loop.run_until_complete(dm.close())
        loop.close()
        
        # Calculate indicators
        required = strategy.get_required_indicators()
        df = calculate_all_indicators(df, required, use_gpu=False)
        
        # Meta-Learner
        meta_learner = ParameterMetaLearner()
        smart_ranges = meta_learner.get_smart_ranges(
            strategy_name=strategy_name,
            df=df,
            lookback=100
        )
        
        # Create parameter space
        param_definitions = {}
        for param_name, (min_val, max_val) in smart_ranges.items():
            param_type = ParameterType.INT if isinstance(min_val, int) else ParameterType.FLOAT
            
            param_definitions[param_name] = ParameterDefinition(
                name=param_name,
                type=param_type,
                low=min_val,
                high=max_val,
                description=f"Range for {param_name}"
            )
        
        param_space = ParameterSpace(
            parameters=param_definitions,
            strategy_name=strategy_name
        )
        
        # Progress callback
        def progress_callback(generation: int, stats: dict):
            """Update job progress"""
            job_manager.update_progress(
                job_id=job_id,
                current_generation=generation,
                best_sharpe=stats["best_fitness"]["sharpe_ratio"],
                avg_sharpe=stats["avg_fitness"]["sharpe_ratio"],
            )
        
        # Run optimization
        config = OptimizationConfig(
            population_size=population_size,
            n_generations=n_generations,
            use_ray=use_ray,
        )
        
        optimizer = GeneticOptimizer(
            df=df,
            strategy_class=strategy,
            param_space=param_space,
            config=config,
            use_smart_ranges=False,
            progress_callback=progress_callback,
        )
        
        results = optimizer.optimize()
        
        return {
            "strategy": strategy_name,
            "symbol": symbol,
            "timeframe": timeframe,
            "best_params": results["best_params"],
            "best_fitness": results["best_fitness"],
            "total_time": results["total_time"],
            "total_evaluations": results["total_evaluations"],
            "config": {
                "population_size": population_size,
                "n_generations": n_generations,
            },
        }
    
    # Start job in background
    job_manager.start_job(job_id, _run_optimization)
    
    # Get job info
    job = job_manager.get_job(job_id)
    
    return {
        "job_id": job_id,
        "status": job.status.value,
        "strategy": strategy_name,
        "symbol": symbol,
        "timeframe": timeframe,
        "population_size": population_size,
        "n_generations": n_generations,
        "estimated_time_minutes": job.estimated_time_seconds // 60,
        "created_at": job.created_at.isoformat(),
        "message": f"? Job started! Use get_optimization_job_status('{job_id}') to check progress.",
    }


async def get_optimization_job_status(job_id: str) -> Dict[str, Any]:
    """
    Get status of running optimization job.
    
    ? FAST: Returns immediately with current status
    
    Args:
        job_id: Job ID from start_optimization_job()
        
    Returns:
        Current job status and progress
    """
    job_manager = get_job_manager()
    job = job_manager.get_job(job_id)
    
    if not job:
        return {"error": f"Job {job_id} not found"}
    
    # Calculate progress
    progress_pct = 0
    if job.n_generations > 0:
        progress_pct = (job.current_generation / job.n_generations) * 100
    
    # Estimate remaining time
    eta_seconds = None
    if job.status == JobStatus.RUNNING and job.started_at:
        elapsed = (datetime.now() - job.started_at).total_seconds()
        if job.current_generation > 0:
            time_per_gen = elapsed / job.current_generation
            remaining_gens = job.n_generations - job.current_generation
            eta_seconds = int(time_per_gen * remaining_gens)
    
    result = {
        "job_id": job_id,
        "status": job.status.value,
        "strategy": job.strategy_name,
        "symbol": job.symbol,
        "timeframe": job.timeframe,
        "progress": {
            "current_generation": job.current_generation,
            "total_generations": job.n_generations,
            "progress_pct": round(progress_pct, 1),
            "best_sharpe": round(job.best_sharpe, 2),
            "avg_sharpe": round(job.avg_sharpe, 2),
        },
        "created_at": job.created_at.isoformat(),
    }
    
    if job.started_at:
        result["started_at"] = job.started_at.isoformat()
        result["elapsed_seconds"] = int((datetime.now() - job.started_at).total_seconds())
    
    if eta_seconds:
        result["eta_seconds"] = eta_seconds
        result["eta_minutes"] = eta_seconds // 60
    
    if job.completed_at:
        result["completed_at"] = job.completed_at.isoformat()
        result["total_seconds"] = int((job.completed_at - job.started_at).total_seconds())
    
    if job.error:
        result["error"] = job.error
    
    # Status-specific messages
    if job.status == JobStatus.PENDING:
        result["message"] = "? Job pending..."
    elif job.status == JobStatus.RUNNING:
        result["message"] = f"?? Gen {job.current_generation}/{job.n_generations} - Best Sharpe: {job.best_sharpe:.2f}"
    elif job.status == JobStatus.COMPLETED:
        result["message"] = f"? Complete! Best Sharpe: {job.best_sharpe:.2f} - Use get_optimization_job_results('{job_id}') to get full results"
    elif job.status == JobStatus.FAILED:
        result["message"] = f"? Failed: {job.error}"
    elif job.status == JobStatus.CANCELLED:
        result["message"] = f"?? Cancelled: {job.error}"
    
    return result


async def get_optimization_job_results(job_id: str) -> Dict[str, Any]:
    """
    Get full results of completed optimization job.
    
    ? FAST: Returns immediately if job is complete
    
    Args:
        job_id: Job ID from start_optimization_job()
        
    Returns:
        Full optimization results
    """
    job_manager = get_job_manager()
    job = job_manager.get_job(job_id)
    
    if not job:
        return {"error": f"Job {job_id} not found"}
    
    if job.status == JobStatus.COMPLETED:
        if job.results:
            return {
                "job_id": job_id,
                "status": "completed",
                **job.results,
            }
        else:
            return {"error": "Job completed but results are missing (internal error)"}
    
    elif job.status == JobStatus.RUNNING:
        return {
            "error": f"Job still running (Gen {job.current_generation}/{job.n_generations})",
            "current_best_sharpe": job.best_sharpe,
            "message": "Use get_optimization_job_status() to monitor progress",
        }
    
    elif job.status == JobStatus.FAILED:
        return {
            "error": f"Job failed: {job.error}",
            "status": "failed",
        }
    
    elif job.status == JobStatus.CANCELLED:
        return {
            "error": f"Job was cancelled: {job.error}",
            "status": "cancelled",
        }
    
    else:
        return {
            "error": f"Job is {job.status.value}",
            "message": "Wait for job to complete",
        }


async def list_optimization_jobs(
    status: str = "all",  # "all", "running", "completed", "failed"
    limit: int = 20,
) -> Dict[str, Any]:
    """
    List optimization jobs.
    
    Args:
        status: Filter by status
        limit: Max results
        
    Returns:
        List of jobs
    """
    job_manager = get_job_manager()
    
    # Map status string to enum
    status_filter = None
    if status != "all":
        try:
            status_filter = JobStatus(status.upper())
        except ValueError:
            return {"error": f"Invalid status '{status}'. Use: all, running, completed, failed"}
    
    jobs = job_manager.list_jobs(status=status_filter, limit=limit)
    
    return {
        "total": len(jobs),
        "jobs": [
            {
                "job_id": job.job_id,
                "strategy": job.strategy_name,
                "symbol": job.symbol,
                "status": job.status.value,
                "progress": f"{job.current_generation}/{job.n_generations}",
                "best_sharpe": round(job.best_sharpe, 2),
                "created_at": job.created_at.isoformat(),
            }
            for job in jobs
        ],
    }


async def cancel_optimization_job(job_id: str, reason: str = "User requested") -> Dict[str, Any]:
    """
    Cancel a running optimization job.
    
    Args:
        job_id: Job to cancel
        reason: Cancellation reason
        
    Returns:
        Cancellation result
    """
    job_manager = get_job_manager()
    
    success = job_manager.cancel_job(job_id, reason)
    
    if success:
        return {
            "job_id": job_id,
            "status": "cancelled",
            "message": f"? Job cancelled: {reason}",
        }
    else:
        job = job_manager.get_job(job_id)
        if not job:
            return {"error": f"Job {job_id} not found"}
        else:
            return {"error": f"Cannot cancel job (status: {job.status.value})"}


__all__ = [
    "start_optimization_job",
    "get_optimization_job_status",
    "get_optimization_job_results",
    "list_optimization_jobs",
    "cancel_optimization_job",
]
