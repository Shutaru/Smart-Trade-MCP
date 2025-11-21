# -*- coding: utf-8 -*-
"""
Portfolio Optimizer

Optimizes allocation across multiple trading strategies.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime
from dataclasses import dataclass

from .portfolio_config import PortfolioConfig
from ..strategies import registry
from ..core.backtest_engine import BacktestEngine
from ..core.logger import logger


@dataclass
class StrategyPerformance:
    """Performance metrics for a single strategy"""
    name: str
    returns: np.ndarray
    sharpe: float
    volatility: float
    max_drawdown: float
    win_rate: float
    total_return: float


class PortfolioOptimizer:
    """
    Multi-strategy portfolio optimizer.
    
    Optimizes allocation across strategies using:
    - Equal Weight
    - Risk Parity
    - Maximum Sharpe Ratio
    - Minimum Variance
    """
    
    def __init__(
        self,
        df: pd.DataFrame,
        config: PortfolioConfig,
    ):
        """
        Initialize portfolio optimizer.
        
        Args:
            df: OHLCV DataFrame with indicators
            config: Portfolio configuration
        """
        self.df = df
        self.config = config
        
        # Validate config
        self.config.validate_config()
        
        # Strategy performances
        self.strategy_performances: Dict[str, StrategyPerformance] = {}
        
        # Optimized weights
        self.weights: Optional[Dict[str, float]] = None
        
        logger.info(
            "PortfolioOptimizer initialized",
            n_strategies=len(config.strategies),
            method=config.optimization_method
        )
    
    def _backtest_strategy(self, strategy_name: str) -> StrategyPerformance:
        """
        Backtest a single strategy and extract performance.
        
        Args:
            strategy_name: Name of strategy to backtest
            
        Returns:
            StrategyPerformance object
        """
        # Get strategy from registry
        strategy = registry.get(strategy_name)
        
        # Run backtest
        engine = BacktestEngine(
            initial_capital=self.config.initial_capital,
            commission_rate=self.config.commission,
            slippage_rate=self.config.slippage,
        )
        
        results = engine.run(strategy, self.df)
        
        # Extract equity curve
        equity_curve = pd.DataFrame(results['equity_curve'])
        equity_curve['timestamp'] = pd.to_datetime(equity_curve['timestamp'])
        equity_curve = equity_curve.set_index('timestamp')
        
        # Calculate returns
        returns = equity_curve['equity'].pct_change().fillna(0).values
        
        return StrategyPerformance(
            name=strategy_name,
            returns=returns,
            sharpe=results['metrics']['sharpe_ratio'],
            volatility=np.std(returns) * np.sqrt(252),  # Annualized
            max_drawdown=results['metrics']['max_drawdown_pct'],
            win_rate=results['metrics']['win_rate'],
            total_return=results['total_return'],
        )
    
    def _calculate_correlation_matrix(self) -> np.ndarray:
        """Calculate correlation matrix of strategy returns"""
        returns_matrix = np.column_stack([
            perf.returns for perf in self.strategy_performances.values()
        ])
        
        return np.corrcoef(returns_matrix, rowvar=False)
    
    def _optimize_equal_weight(self) -> Dict[str, float]:
        """Equal weight allocation"""
        n = len(self.config.strategies)
        weight = 1.0 / n
        
        return {name: weight for name in self.config.strategies}
    
    def _optimize_risk_parity(self) -> Dict[str, float]:
        """
        Risk parity allocation.
        
        Allocates inversely proportional to volatility.
        """
        # Get volatilities
        vols = np.array([
            self.strategy_performances[name].volatility
            for name in self.config.strategies
        ])
        
        # Inverse volatility weights
        inv_vols = 1.0 / vols
        weights = inv_vols / inv_vols.sum()
        
        return {
            name: weight
            for name, weight in zip(self.config.strategies, weights)
        }
    
    def _optimize_max_sharpe(self) -> Dict[str, float]:
        """
        Maximum Sharpe Ratio allocation.
        
        Uses Mean-Variance Optimization to find portfolio
        with highest risk-adjusted return.
        """
        # Get returns matrix
        returns_matrix = np.column_stack([
            self.strategy_performances[name].returns
            for name in self.config.strategies
        ])
        
        # Calculate mean returns and covariance
        mean_returns = np.mean(returns_matrix, axis=0)
        cov_matrix = np.cov(returns_matrix, rowvar=False)
        
        # Optimize using scipy
        from scipy.optimize import minimize
        
        n_assets = len(self.config.strategies)
        
        def neg_sharpe(weights):
            """Negative Sharpe ratio (to minimize)"""
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            # Avoid division by zero
            if portfolio_vol < 1e-10:
                return 1e10
            
            return -portfolio_return / portfolio_vol
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}  # Sum to 1
        ]
        
        # Bounds
        bounds = [(self.config.min_weight, self.config.max_weight)] * n_assets
        
        # Initial guess (equal weight)
        x0 = np.array([1.0 / n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            neg_sharpe,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
        )
        
        if not result.success:
            logger.warning(f"Max Sharpe optimization failed: {result.message}")
            # Fall back to equal weight
            return self._optimize_equal_weight()
        
        return {
            name: weight
            for name, weight in zip(self.config.strategies, result.x)
        }
    
    def _optimize_min_variance(self) -> Dict[str, float]:
        """
        Minimum Variance allocation.
        
        Finds portfolio with lowest volatility.
        """
        # Get returns matrix
        returns_matrix = np.column_stack([
            self.strategy_performances[name].returns
            for name in self.config.strategies
        ])
        
        cov_matrix = np.cov(returns_matrix, rowvar=False)
        
        from scipy.optimize import minimize
        
        n_assets = len(self.config.strategies)
        
        def portfolio_variance(weights):
            """Portfolio variance"""
            return np.dot(weights.T, np.dot(cov_matrix, weights))
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}
        ]
        
        # Bounds
        bounds = [(self.config.min_weight, self.config.max_weight)] * n_assets
        
        # Initial guess
        x0 = np.array([1.0 / n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            portfolio_variance,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
        )
        
        if not result.success:
            logger.warning(f"Min Variance optimization failed: {result.message}")
            return self._optimize_equal_weight()
        
        return {
            name: weight
            for name, weight in zip(self.config.strategies, result.x)
        }
    
    def optimize(self) -> Dict[str, float]:
        """
        Run portfolio optimization.
        
        Returns:
            Dictionary of strategy weights
        """
        logger.info("Starting portfolio optimization")
        
        # Backtest all strategies
        for strategy_name in self.config.strategies:
            logger.info(f"Backtesting strategy: {strategy_name}")
            perf = self._backtest_strategy(strategy_name)
            self.strategy_performances[strategy_name] = perf
        
        # Check correlation
        corr_matrix = self._calculate_correlation_matrix()
        max_corr = np.max(corr_matrix[np.triu_indices_from(corr_matrix, k=1)])
        
        if max_corr > self.config.max_correlation:
            logger.warning(
                f"High correlation detected: {max_corr:.2f} "
                f"(max allowed: {self.config.max_correlation})"
            )
        
        # Optimize weights
        logger.info(f"Optimizing weights using: {self.config.optimization_method}")
        
        if self.config.optimization_method == "equal_weight":
            self.weights = self._optimize_equal_weight()
        elif self.config.optimization_method == "risk_parity":
            self.weights = self._optimize_risk_parity()
        elif self.config.optimization_method == "max_sharpe":
            self.weights = self._optimize_max_sharpe()
        elif self.config.optimization_method == "min_variance":
            self.weights = self._optimize_min_variance()
        else:
            raise ValueError(f"Unknown optimization method: {self.config.optimization_method}")
        
        logger.info(f"Optimization complete: {self.weights}")
        
        return self.weights
    
    def get_portfolio_metrics(self) -> Dict[str, Any]:
        """
        Calculate portfolio-level metrics.
        
        Returns:
            Dictionary with portfolio metrics
        """
        if not self.weights:
            raise ValueError("Must run optimize() first")
        
        # Calculate portfolio returns
        returns_matrix = np.column_stack([
            self.strategy_performances[name].returns
            for name in self.config.strategies
        ])
        
        weights_array = np.array([
            self.weights[name] for name in self.config.strategies
        ])
        
        portfolio_returns = np.dot(returns_matrix, weights_array)
        
        # Calculate metrics
        portfolio_sharpe = (
            np.mean(portfolio_returns) / np.std(portfolio_returns) * np.sqrt(252)
            if np.std(portfolio_returns) > 0 else 0
        )
        
        portfolio_vol = np.std(portfolio_returns) * np.sqrt(252)
        
        cumulative_returns = (1 + portfolio_returns).cumprod()
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        max_dd = np.min(drawdowns) * 100
        
        total_return = (cumulative_returns[-1] - 1) * 100
        
        return {
            'weights': self.weights,
            'portfolio_sharpe': portfolio_sharpe,
            'portfolio_volatility': portfolio_vol,
            'portfolio_max_drawdown': max_dd,
            'portfolio_total_return': total_return,
            'correlation_matrix': self._calculate_correlation_matrix().tolist(),
            'strategy_performances': {
                name: {
                    'sharpe': perf.sharpe,
                    'volatility': perf.volatility,
                    'max_drawdown': perf.max_drawdown,
                    'total_return': perf.total_return,
                }
                for name, perf in self.strategy_performances.items()
            },
        }
