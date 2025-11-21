# -*- coding: utf-8 -*-
"""
Ray Batch Evaluator

Distributed batch evaluation using Ray for massive speedup.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from dataclasses import dataclass

try:
    import ray
    from ray.util.multiprocessing import Pool
    RAY_AVAILABLE = True
except ImportError:
    RAY_AVAILABLE = False
    ray = None

from ..core.logger import logger


@dataclass
class BatchEvaluationConfig:
    """Configuration for batch evaluation"""
    use_ray: bool = True
    n_workers: int = -1  # -1 = all CPUs
    batch_size: int = 10
    ray_address: Optional[str] = None  # None = local, 'auto' = cluster


class RayBatchEvaluator:
    """
    Ray-based distributed batch evaluator.
    
    Enables massive parallelization for:
    - Population evaluation in GA
    - Window evaluation in WFA
    - Multi-strategy backtesting
    """
    
    def __init__(self, config: BatchEvaluationConfig):
        """
        Initialize Ray batch evaluator.
        
        Args:
            config: Batch evaluation configuration
        """
        if not RAY_AVAILABLE:
            raise ImportError("Ray not available. Install with: pip install ray")
        
        self.config = config
        self.initialized = False
        
        logger.info(
            "RayBatchEvaluator created",
            n_workers=config.n_workers,
            batch_size=config.batch_size
        )
    
    def initialize(self):
        """Initialize Ray runtime"""
        if self.initialized:
            return
        
        if not ray.is_initialized():
            # Initialize Ray
            if self.config.ray_address:
                # Connect to existing cluster
                ray.init(address=self.config.ray_address)
                logger.info(f"Connected to Ray cluster: {self.config.ray_address}")
            else:
                # Start local Ray
                num_cpus = self.config.n_workers if self.config.n_workers > 0 else None
                ray.init(num_cpus=num_cpus, ignore_reinit_error=True)
                logger.info(f"Ray initialized locally with {num_cpus or 'all'} CPUs")
        
        self.initialized = True
    
    def shutdown(self):
        """Shutdown Ray runtime"""
        if self.initialized and ray.is_initialized():
            ray.shutdown()
            self.initialized = False
            logger.info("Ray shutdown")
    
    def evaluate_batch(
        self,
        evaluate_fn: Any,
        items: List[Any],
        batch_size: Optional[int] = None
    ) -> List[Any]:
        """
        Evaluate a batch of items in parallel using Ray.
        
        Args:
            evaluate_fn: Function to evaluate each item (must be Ray remote)
            items: List of items to evaluate
            batch_size: Batch size (None = use config default)
            
        Returns:
            List of evaluation results
        """
        self.initialize()
        
        batch_size = batch_size or self.config.batch_size
        
        logger.info(f"Evaluating {len(items)} items in batches of {batch_size}")
        
        # Submit all tasks
        futures = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            for item in batch:
                futures.append(evaluate_fn.remote(item))
        
        # Gather results
        results = ray.get(futures)
        
        logger.info(f"Batch evaluation complete: {len(results)} results")
        
        return results
    
    def __enter__(self):
        """Context manager entry"""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.shutdown()


# Ray remote function decorator for fitness evaluation
if RAY_AVAILABLE:
    @ray.remote
    def evaluate_individual_remote(
        individual: List,
        param_names: List[str],
        df: pd.DataFrame,
        strategy_class: Any,
        initial_capital: float,
        commission: float,
        slippage: float
    ) -> tuple:
        """
        Ray remote function to evaluate a single individual.
        
        This runs in a separate Ray worker process.
        """
        # Import here to avoid serialization issues
        from ..strategies import StrategyConfig
        from ..core.backtest_engine import BacktestEngine
        
        # Convert individual to params dict
        params = {name: value for name, value in zip(param_names, individual)}
        
        # Create strategy
        if isinstance(strategy_class, type):
            strategy_cls = strategy_class
        else:
            strategy_cls = strategy_class.__class__
        
        config = StrategyConfig(params=params)
        strategy = strategy_cls(config)
        
        # Run backtest
        engine = BacktestEngine(
            initial_capital=initial_capital,
            commission_rate=commission,
            slippage_rate=slippage,
        )
        
        results = engine.run(strategy, df)
        
        # Return fitness tuple
        return (
            results['metrics']['sharpe_ratio'],
            results['metrics']['win_rate'],
            results['metrics']['max_drawdown_pct'],
        )
    
    @ray.remote
    def evaluate_window_remote(
        window_data: Dict[str, Any],
        strategy_class: Any,
        param_space: Any,
        opt_config: Any,
        wfa_config: Any
    ) -> Dict[str, Any]:
        """
        Ray remote function to evaluate a single WFA window.
        
        Runs full optimization + testing for one window.
        """
        # Import here
        from .genetic_optimizer import GeneticOptimizer
        from ..strategies import StrategyConfig
        from ..core.backtest_engine import BacktestEngine
        from .walk_forward_results import FoldResult
        
        import time
        
        window_start = time.time()
        
        # Optimize on training data
        optimizer = GeneticOptimizer(
            df=window_data['train_df'],
            strategy_class=strategy_class,
            param_space=param_space,
            config=opt_config,
        )
        
        opt_results = optimizer.optimize()
        
        # Test on folds
        fold_results = []
        
        for fold in window_data['folds']:
            # Create strategy
            if isinstance(strategy_class, type):
                strategy_cls = strategy_class
            else:
                strategy_cls = strategy_class.__class__
            
            config = StrategyConfig(params=opt_results['best_params'])
            strategy = strategy_cls(config)
            
            # Backtest
            engine = BacktestEngine(
                initial_capital=10000.0,
                commission_rate=0.001,
                slippage_rate=0.0005,
            )
            
            results = engine.run(strategy, fold['df'])
            
            # Validate
            is_valid = (
                results['metrics']['sharpe_ratio'] >= wfa_config.min_sharpe_ratio and
                results['metrics']['win_rate'] >= wfa_config.min_win_rate and
                results['metrics']['max_drawdown_pct'] >= wfa_config.max_drawdown_pct
            )
            
            fold_result = {
                'fold_id': fold['fold_id'],
                'start': fold['start'],
                'end': fold['end'],
                'candles': len(fold['df']),
                'sharpe': results['metrics']['sharpe_ratio'],
                'win_rate': results['metrics']['win_rate'],
                'max_dd': results['metrics']['max_drawdown_pct'],
                'total_return': results['total_return'],
                'trades': results['total_trades'],
                'is_valid': is_valid,
            }
            
            fold_results.append(fold_result)
        
        return {
            'window_id': window_data['id'],
            'train_start': window_data['train_start'],
            'train_end': window_data['train_end'],
            'test_start': window_data['test_start'],
            'test_end': window_data['test_end'],
            'train_candles': len(window_data['train_df']),
            'train_fitness': opt_results['best_fitness'],
            'best_params': opt_results['best_params'],
            'folds': fold_results,
            'optimization_time': time.time() - window_start,
        }


__all__ = [
    'RayBatchEvaluator',
    'BatchEvaluationConfig',
]
