# -*- coding: utf-8 -*-
"""
Async Job Manager for Long-Running Operations

Manages optimization jobs that exceed Claude Desktop's 4-minute timeout.
Jobs run in background threads and can be queried for status/results.
"""

import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

from ..core.logger import logger


class JobStatus(str, Enum):
    """Job status enum"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class OptimizationJob:
    """Optimization job data"""
    job_id: str
    strategy_name: str
    symbol: str
    timeframe: str
    population_size: int
    n_generations: int
    
    status: JobStatus = JobStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Progress tracking
    current_generation: int = 0
    best_sharpe: float = 0.0
    avg_sharpe: float = 0.0
    
    # Results
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    estimated_time_seconds: int = 0


class JobManager:
    """
    Manages async optimization jobs.
    
    Thread-safe job storage and execution.
    """
    
    def __init__(self):
        """Initialize job manager"""
        self._jobs: Dict[str, OptimizationJob] = {}
        self._lock = threading.Lock()
        self._threads: Dict[str, threading.Thread] = {}
        
        logger.info("JobManager initialized")
    
    def create_job(
        self,
        strategy_name: str,
        symbol: str,
        timeframe: str,
        population_size: int,
        n_generations: int,
    ) -> str:
        """
        Create a new optimization job.
        
        Args:
            strategy_name: Strategy to optimize
            symbol: Trading pair
            timeframe: Candle timeframe
            population_size: GA population
            n_generations: GA generations
            
        Returns:
            job_id: Unique job identifier
        """
        job_id = f"opt_{uuid.uuid4().hex[:8]}"
        
        # Estimate time (rough: 0.5s per individual * population * generations)
        estimated_time = int((population_size * n_generations * 0.5) / 60) * 60  # Round to minute
        
        job = OptimizationJob(
            job_id=job_id,
            strategy_name=strategy_name,
            symbol=symbol,
            timeframe=timeframe,
            population_size=population_size,
            n_generations=n_generations,
            estimated_time_seconds=estimated_time,
        )
        
        with self._lock:
            self._jobs[job_id] = job
        
        logger.info(
            f"Created job {job_id}: {strategy_name} on {symbol} {timeframe} "
            f"(pop={population_size}, gen={n_generations}, ~{estimated_time}s)"
        )
        
        return job_id
    
    def start_job(
        self,
        job_id: str,
        run_function: Callable[[str], Dict[str, Any]],
    ) -> None:
        """
        Start job execution in background thread.
        
        Args:
            job_id: Job to start
            run_function: Function to execute (receives job_id, returns results)
        """
        with self._lock:
            if job_id not in self._jobs:
                raise ValueError(f"Job {job_id} not found")
            
            job = self._jobs[job_id]
            
            if job.status != JobStatus.PENDING:
                raise ValueError(f"Job {job_id} already started (status: {job.status})")
        
        def _run_job():
            """Background job executor"""
            try:
                # Mark as running
                with self._lock:
                    self._jobs[job_id].status = JobStatus.RUNNING
                    self._jobs[job_id].started_at = datetime.now()
                
                logger.info(f"Job {job_id} started")
                
                # Execute
                results = run_function(job_id)
                
                # Mark as completed
                with self._lock:
                    self._jobs[job_id].status = JobStatus.COMPLETED
                    self._jobs[job_id].completed_at = datetime.now()
                    self._jobs[job_id].results = results
                
                logger.info(f"Job {job_id} completed successfully")
                
            except Exception as e:
                # Mark as failed
                with self._lock:
                    self._jobs[job_id].status = JobStatus.FAILED
                    self._jobs[job_id].completed_at = datetime.now()
                    self._jobs[job_id].error = str(e)
                
                logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        
        # Start thread
        thread = threading.Thread(target=_run_job, daemon=True)
        thread.start()
        
        with self._lock:
            self._threads[job_id] = thread
        
        logger.info(f"Job {job_id} thread started")
    
    def get_job(self, job_id: str) -> Optional[OptimizationJob]:
        """Get job by ID"""
        with self._lock:
            return self._jobs.get(job_id)
    
    def update_progress(
        self,
        job_id: str,
        current_generation: int,
        best_sharpe: float,
        avg_sharpe: float,
    ) -> None:
        """Update job progress (called by optimization callback)"""
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                job.current_generation = current_generation
                job.best_sharpe = best_sharpe
                job.avg_sharpe = avg_sharpe
    
    def cancel_job(self, job_id: str, reason: str = "User cancelled") -> bool:
        """
        Cancel a running job.
        
        Note: Python threads can't be forcibly stopped, so this just marks
        the job as cancelled. The job will continue running but results
        will be discarded.
        
        Args:
            job_id: Job to cancel
            reason: Cancellation reason
            
        Returns:
            True if cancelled, False if job not found or already finished
        """
        with self._lock:
            if job_id not in self._jobs:
                return False
            
            job = self._jobs[job_id]
            
            if job.status not in [JobStatus.PENDING, JobStatus.RUNNING]:
                return False
            
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.now()
            job.error = reason
        
        logger.info(f"Job {job_id} cancelled: {reason}")
        return True
    
    def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        limit: int = 50,
    ) -> list[OptimizationJob]:
        """
        List jobs.
        
        Args:
            status: Filter by status (None = all)
            limit: Maximum results
            
        Returns:
            List of jobs (newest first)
        """
        with self._lock:
            jobs = list(self._jobs.values())
        
        # Filter by status
        if status:
            jobs = [j for j in jobs if j.status == status]
        
        # Sort by created date (newest first)
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        
        return jobs[:limit]
    
    def cleanup_old_jobs(self, max_age_hours: int = 24) -> int:
        """
        Remove old completed/failed jobs.
        
        Args:
            max_age_hours: Remove jobs older than this
            
        Returns:
            Number of jobs removed
        """
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        with self._lock:
            old_jobs = [
                job_id
                for job_id, job in self._jobs.items()
                if job.completed_at and job.completed_at < cutoff
            ]
            
            for job_id in old_jobs:
                del self._jobs[job_id]
                if job_id in self._threads:
                    del self._threads[job_id]
        
        if old_jobs:
            logger.info(f"Cleaned up {len(old_jobs)} old jobs")
        
        return len(old_jobs)


# Global singleton
_job_manager: Optional[JobManager] = None


def get_job_manager() -> JobManager:
    """Get global job manager instance"""
    global _job_manager
    
    if _job_manager is None:
        _job_manager = JobManager()
    
    return _job_manager


__all__ = ["JobManager", "JobStatus", "OptimizationJob", "get_job_manager"]
