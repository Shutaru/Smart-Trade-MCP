# -*- coding: utf-8 -*-
"""
Walk-Forward Analyzer

Main engine for walk-forward analysis validation.
"""

from typing import Dict, Any, List, Tuple
import pandas as pd
from datetime import datetime, timedelta
import time
from pathlib import Path

from .walk_forward_config import WalkForwardConfig
from .walk_forward_results import WindowResult, WalkForwardResults, FoldResult
from .genetic_optimizer import GeneticOptimizer
from .parameter_space import ParameterSpace
from .config import OptimizationConfig
from ..core.backtest_engine import BacktestEngine
from ..core.logger import logger


class WalkForwardAnalyzer:
    """
    Walk-Forward Analysis Engine
    
    Performs rolling window optimization and out-of-sample validation
    to detect overfitting and validate strategy robustness.
    """
    
    def __init__(
        self,
        df: pd.DataFrame,
        strategy_class: Any,
        param_space: ParameterSpace,
        config: WalkForwardConfig,
    ):
        """
        Initialize walk-forward analyzer.
        
        Args:
            df: Full OHLCV DataFrame with indicators
            strategy_class: Strategy class to validate
            param_space: Parameter space for optimization
            config: Walk-forward configuration
        """
        self.df = df
        self.strategy_class = strategy_class
        self.param_space = param_space
        self.config = config
        
        # Validate config
        self.config.validate_config()
        
        # Calculate windows
        self.windows = self._calculate_windows()
        
        logger.info(
            "WalkForwardAnalyzer initialized",
            strategy=strategy_class.name if hasattr(strategy_class, 'name') else strategy_class.__class__.__name__,
            total_windows=len(self.windows),
            train_days=config.train_days,
            test_days=config.test_days,
            step_days=config.step_days
        )
    
    def _calculate_windows(self) -> List[Dict[str, Any]]:
        """
        Calculate all walk-forward windows with N-fold support.
        
        Each window has:
        - 1 training period
        - N test folds (with optional purging between train and each fold)
        
        Returns:
            List of window definitions with start/end dates and fold splits
        """
        windows = []
        
        # Get date range
        start_date = self.df['timestamp'].min()
        end_date = self.df['timestamp'].max()
        
        # Calculate window boundaries
        current_train_start = start_date
        window_id = 0
        
        while True:
            # Training period
            train_end = current_train_start + timedelta(days=self.config.train_days)
            
            # Calculate total test period needed (including purges)
            total_test_days = (
                self.config.test_days * self.config.n_folds +
                self.config.purge_days * self.config.n_folds  # Purge before each fold
            )
            
            test_end = train_end + timedelta(days=total_test_days)
            
            # Check if we have enough data
            if test_end > end_date:
                break
            
            # Get training data
            train_df = self.df[
                (self.df['timestamp'] >= current_train_start) &
                (self.df['timestamp'] < train_end)
            ]
            
            # Validate minimum training candles
            if len(train_df) < self.config.min_train_candles:
                logger.warning(f"Window {window_id}: Insufficient training data ({len(train_df)} candles)")
                break
            
            # Calculate N test folds with purging
            folds = []
            fold_start = train_end
            
            for fold_id in range(self.config.n_folds):
                # Purge period (avoid data leakage)
                purge_end = fold_start + timedelta(days=self.config.purge_days)
                
                # Test fold period
                fold_test_start = purge_end
                fold_test_end = fold_test_start + timedelta(days=self.config.test_days)
                
                # Get fold data
                fold_df = self.df[
                    (self.df['timestamp'] >= fold_test_start) &
                    (self.df['timestamp'] < fold_test_end)
                ]
                
                # Validate minimum test candles
                if len(fold_df) < self.config.min_test_candles:
                    logger.warning(
                        f"Window {window_id}, Fold {fold_id}: Insufficient test data ({len(fold_df)} candles)"
                    )
                    break
                
                folds.append({
                    'fold_id': fold_id,
                    'start': fold_test_start,
                    'end': fold_test_end,
                    'df': fold_df,
                })
                
                # Move to next fold
                fold_start = fold_test_end
            
            # Skip window if we don't have all folds
            if len(folds) < self.config.n_folds:
                break
            
            # Add window with all folds
            windows.append({
                'id': window_id,
                'train_start': current_train_start,
                'train_end': train_end,
                'train_df': train_df,
                'folds': folds,
                'test_start': folds[0]['start'],
                'test_end': folds[-1]['end'],
            })
            
            window_id += 1
            
            # Move to next window
            current_train_start += timedelta(days=self.config.step_days)
        
        return windows
    
    def _optimize_window(self, window: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize parameters for a single window.
        
        Args:
            window: Window definition
            
        Returns:
            Optimized parameters and training metrics
        """
        # Create optimization config
        opt_config = OptimizationConfig(
            population_size=self.config.population_size,
            n_generations=self.config.n_generations,
            use_gpu=False,  # CPU for now (GPU in Phase 6B)
        )
        
        # Initialize optimizer on training data
        optimizer = GeneticOptimizer(
            df=window['train_df'],
            strategy_class=self.strategy_class,
            param_space=self.param_space,
            config=opt_config,
        )
        
        # Run optimization (silently - no dashboard for each window)
        results = optimizer.optimize()
        
        return {
            'best_params': results['best_params'],
            'train_fitness': results['best_fitness'],
            'optimization_time': results['total_time'],
        }
    
    def _test_window(
        self,
        window: Dict[str, Any],
        optimized_params: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Test optimized parameters on out-of-sample data.
        
        Args:
            window: Window definition
            optimized_params: Parameters from training optimization
            
        Returns:
            Test performance metrics
        """
        # Create strategy instance with optimized params
        strategy = self.strategy_class(params=optimized_params)
        
        # Run backtest on test data
        engine = BacktestEngine(
            df=window['test_df'],
            strategy=strategy,
            initial_capital=10000.0,
            commission=0.001,
            slippage=0.0005,
        )
        
        results = engine.run()
        
        return {
            'sharpe_ratio': results.get('sharpe_ratio', 0.0),
            'win_rate': results.get('win_rate', 0.0),
            'max_drawdown': results.get('max_drawdown_pct', 0.0),
            'total_return': results.get('total_return_pct', 0.0),
            'total_trades': results.get('total_trades', 0),
        }
    
    def _test_folds(
        self,
        window: Dict[str, Any],
        optimized_params: Dict[str, Any]
    ) -> List[FoldResult]:
        """
        Test optimized parameters on all out-of-sample folds.
        
        Args:
            window: Window definition with multiple folds
            optimized_params: Parameters from training optimization
            
        Returns:
            List of FoldResult for each test fold
        """
        # Import StrategyConfig
        from ..strategies import StrategyConfig
        
        fold_results = []
        
        for fold in window['folds']:
            # Create strategy instance with optimized params
            # Get strategy class (handle both class and instance)
            if isinstance(self.strategy_class, type):
                # It's a class
                strategy_cls = self.strategy_class
            else:
                # It's an instance - get its class
                strategy_cls = self.strategy_class.__class__
            
            # Create StrategyConfig with optimized parameters
            config = StrategyConfig(params=optimized_params)
            
            # Create strategy instance with config
            strategy = strategy_cls(config)
            
            # Create backtest engine
            engine = BacktestEngine(
                initial_capital=10000.0,
                commission_rate=0.001,
                slippage_rate=0.0005,
            )
            
            # Run backtest on this fold (df is passed to run(), not __init__)
            results = engine.run(strategy, fold['df'])
            
            # Validate against thresholds
            is_valid = (
                results.get('metrics', {}).get('sharpe_ratio', 0.0) >= self.config.min_sharpe_ratio and
                results.get('metrics', {}).get('win_rate', 0.0) >= self.config.min_win_rate and
                results.get('metrics', {}).get('max_drawdown_pct', 0.0) >= self.config.max_drawdown_pct
            )
            
            # Create fold result
            fold_result = FoldResult(
                fold_id=fold['fold_id'],
                start=fold['start'],
                end=fold['end'],
                candles=len(fold['df']),
                sharpe=results.get('metrics', {}).get('sharpe_ratio', 0.0),
                win_rate=results.get('metrics', {}).get('win_rate', 0.0),
                max_dd=results.get('metrics', {}).get('max_drawdown_pct', 0.0),
                total_return=results.get('total_return', 0.0),
                trades=results.get('total_trades', 0),
                is_valid=is_valid,
            )
            
            fold_results.append(fold_result)
        
        return fold_results
    
    def _process_window(self, window: Dict[str, Any]) -> WindowResult:
        """
        Process a single window (optimize + test on N folds).
        
        Args:
            window: Window definition with multiple folds
            
        Returns:
            WindowResult with complete metrics from all folds
        """
        window_start = time.time()
        
        # Optimize on training data
        opt_results = self._optimize_window(window)
        
        # Test on all out-of-sample folds
        fold_results = self._test_folds(window, opt_results['best_params'])
        
        # Create window result
        result = WindowResult(
            window_id=window['id'],
            train_start=window['train_start'],
            train_end=window['train_end'],
            test_start=window['test_start'],
            test_end=window['test_end'],
            train_candles=len(window['train_df']),
            train_sharpe=opt_results['train_fitness']['sharpe_ratio'],
            train_win_rate=opt_results['train_fitness']['win_rate'],
            train_max_dd=opt_results['train_fitness']['max_drawdown_pct'],
            folds=fold_results,
            test_candles=0,  # Will be calculated in calculate_aggregates
            test_sharpe=0.0,
            test_win_rate=0.0,
            test_max_dd=0.0,
            test_total_return=0.0,
            test_trades=0,
            best_params=opt_results['best_params'],
            sharpe_degradation=0.0,
            win_rate_degradation=0.0,
            valid_folds=0,
            fold_consistency=0.0,
            is_valid=False,
            optimization_time=time.time() - window_start,
        )
        
        # Calculate aggregates across folds
        result.calculate_aggregates()
        
        # Calculate degradation
        result.calculate_degradation()
        
        # Validate window (must have min_valid_folds passing)
        result.is_valid = result.valid_folds >= self.config.min_valid_folds
        
        return result
    
    def analyze(self) -> WalkForwardResults:
        """
        Run complete walk-forward analysis.
        
        Returns:
            WalkForwardResults with all windows and aggregate metrics
        """
        start_time = time.time()
        
        logger.info(f"Starting walk-forward analysis with {len(self.windows)} windows")
        
        # Process each window
        window_results = []
        
        if self.config.use_parallel:
            # PARALLEL PROCESSING WITH RAY
            try:
                from .ray_batch_evaluator import (
                    RayBatchEvaluator,
                    BatchEvaluationConfig,
                    evaluate_window_remote,
                    RAY_AVAILABLE,
                )
                
                if RAY_AVAILABLE:
                    logger.info("Using Ray for parallel window processing")
                    
                    # Create batch evaluator
                    batch_config = BatchEvaluationConfig(
                        use_ray=True,
                        n_workers=self.config.n_jobs,
                        batch_size=min(len(self.windows), 4),  # Process up to 4 windows at once
                    )
                    
                    with RayBatchEvaluator(batch_config) as evaluator:
                        # Convert windows to serializable format
                        window_data_list = []
                        for window in self.windows:
                            window_data_list.append({
                                'id': window['id'],
                                'train_start': window['train_start'],
                                'train_end': window['train_end'],
                                'test_start': window['test_start'],
                                'test_end': window['test_end'],
                                'train_df': window['train_df'],
                                'folds': window['folds'],
                            })
                        
                        # Create optimization config
                        opt_config = OptimizationConfig(
                            population_size=self.config.population_size,
                            n_generations=self.config.n_generations,
                            use_gpu=False,
                        )
                        
                        # Evaluate all windows in parallel
                        import ray
                        futures = [
                            evaluate_window_remote.remote(
                                window_data,
                                self.strategy_class,
                                self.param_space,
                                opt_config,
                                self.config,
                            )
                            for window_data in window_data_list
                        ]
                        
                        # Get results
                        raw_results = ray.get(futures)
                        
                        # Convert to WindowResult objects
                        for raw in raw_results:
                            from .walk_forward_results import FoldResult
                            
                            fold_objs = [
                                FoldResult(
                                    fold_id=f['fold_id'],
                                    start=f['start'],
                                    end=f['end'],
                                    candles=f['candles'],
                                    sharpe=f['sharpe'],
                                    win_rate=f['win_rate'],
                                    max_dd=f['max_dd'],
                                    total_return=f['total_return'],
                                    trades=f['trades'],
                                    is_valid=f['is_valid'],
                                )
                                for f in raw['folds']
                            ]
                            
                            result = WindowResult(
                                window_id=raw['window_id'],
                                train_start=raw['train_start'],
                                train_end=raw['train_end'],
                                test_start=raw['test_start'],
                                test_end=raw['test_end'],
                                train_candles=raw['train_candles'],
                                train_sharpe=raw['train_fitness']['sharpe_ratio'],
                                train_win_rate=raw['train_fitness']['win_rate'],
                                train_max_dd=raw['train_fitness']['max_drawdown_pct'],
                                folds=fold_objs,
                                test_candles=0,
                                test_sharpe=0.0,
                                test_win_rate=0.0,
                                test_max_dd=0.0,
                                test_total_return=0.0,
                                test_trades=0,
                                best_params=raw['best_params'],
                                sharpe_degradation=0.0,
                                win_rate_degradation=0.0,
                                valid_folds=0,
                                fold_consistency=0.0,
                                is_valid=False,
                                optimization_time=raw['optimization_time'],
                            )
                            
                            # Calculate aggregates
                            result.calculate_aggregates()
                            result.calculate_degradation()
                            result.is_valid = result.valid_folds >= self.config.min_valid_folds
                            
                            window_results.append(result)
                    
                    logger.info(f"Ray parallel processing complete: {len(window_results)} windows")
                else:
                    raise ImportError("Ray not available")
                    
            except (ImportError, Exception) as e:
                logger.warning(f"Ray parallel processing failed: {e}, falling back to sequential")
                # Fall back to sequential
                for window in self.windows:
                    result = self._process_window(window)
                    window_results.append(result)
        else:
            # Sequential processing
            for window in self.windows:
                result = self._process_window(window)
                window_results.append(result)
        
        # Create final results
        valid_count = sum(1 for r in window_results if r.is_valid)
        
        results = WalkForwardResults(
            strategy_name=self.strategy_class.name if hasattr(self.strategy_class, 'name') else self.strategy_class.__class__.__name__,
            start_date=self.df['timestamp'].min(),
            end_date=self.df['timestamp'].max(),
            total_windows=len(window_results),
            valid_windows=valid_count,
            windows=window_results,
            avg_test_sharpe=0.0,  # Will calculate in calculate_aggregates
            avg_test_win_rate=0.0,
            avg_test_max_dd=0.0,
            avg_test_return=0.0,
            sharpe_std=0.0,
            win_rate_std=0.0,
            avg_sharpe_degradation=0.0,
            avg_win_rate_degradation=0.0,
            consistency_score=0.0,
            is_robust=False,
            robustness_score=0.0,
            total_time=time.time() - start_time,
            avg_window_time=(time.time() - start_time) / len(window_results) if window_results else 0.0,
        )
        
        # Calculate aggregates
        results.calculate_aggregates()
        
        logger.info(
            "Walk-forward analysis complete",
            total_windows=results.total_windows,
            valid_windows=results.valid_windows,
            robustness_score=f"{results.robustness_score:.1f}",
            is_robust=results.is_robust,
        )
        
        return results
