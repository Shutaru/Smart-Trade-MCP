# -*- coding: utf-8 -*-
"""
Walk-Forward Analysis Configuration

Type-safe configuration for walk-forward validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WalkForwardConfig(BaseModel):
    """Configuration for walk-forward analysis"""
    
    # Window sizes
    train_days: int = Field(
        default=180,
        description="Training window size in days",
        ge=30,
        le=730
    )
    
    test_days: int = Field(
        default=60,
        description="Testing window size in days (per fold)",
        ge=7,
        le=365
    )
    
    step_days: int = Field(
        default=30,
        description="Step size for rolling window in days",
        ge=1,
        le=365
    )
    
    # N-Fold Cross-Validation
    n_folds: int = Field(
        default=1,
        description="Number of out-of-sample test folds (1 = simple rolling, 3+ = k-fold)",
        ge=1,
        le=10
    )
    
    purge_days: int = Field(
        default=0,
        description="Days to purge between train and test to avoid data leakage",
        ge=0,
        le=30
    )
    
    # Optimization settings
    min_train_candles: int = Field(
        default=500,
        description="Minimum candles required in training window"
    )
    
    min_test_candles: int = Field(
        default=100,
        description="Minimum candles required in testing window (per fold)"
    )
    
    # Validation thresholds
    min_sharpe_ratio: float = Field(
        default=0.2,  # Lowered from 0.5 - crypto has lower Sharpe ratios
        description="Minimum Sharpe ratio to consider window valid"
    )
    
    min_win_rate: float = Field(
        default=40.0,
        description="Minimum win rate % to consider window valid"
    )
    
    max_drawdown_pct: float = Field(
        default=-30.0,
        description="Maximum drawdown % allowed (negative value)"
    )
    
    # Fold aggregation
    min_valid_folds: int = Field(
        default=1,
        description="Minimum folds that must pass validation for window to be valid",
        ge=1
    )
    
    # Performance
    use_parallel: bool = Field(
        default=True,
        description="Use parallel processing for windows"
    )
    
    n_jobs: int = Field(
        default=-1,
        description="Number of parallel jobs (-1 = all cores)"
    )
    
    # Optimization config (reuse from genetic optimizer)
    population_size: int = Field(default=20, ge=10, le=200)
    n_generations: int = Field(default=5, ge=3, le=50)
    
    def validate_config(self) -> None:
        """Validate configuration consistency"""
        if self.step_days > self.test_days:
            raise ValueError("step_days should not be larger than test_days")
        
        if self.train_days < self.min_train_candles // 24:  # Rough estimate
            raise ValueError("train_days might be too small for min_train_candles")
        
        if self.min_valid_folds > self.n_folds:
            raise ValueError("min_valid_folds cannot be greater than n_folds")
        
        if self.purge_days > self.test_days:
            raise ValueError("purge_days should not exceed test_days")


class WalkForwardPresets:
    """Preset configurations for common use cases"""
    
    @staticmethod
    def quick_validation() -> WalkForwardConfig:
        """Quick validation (3 months train, 1 month test, 2 weeks step, 1 fold)"""
        return WalkForwardConfig(
            train_days=90,
            test_days=30,
            step_days=14,
            n_folds=1,
            purge_days=0,
            population_size=10,
            n_generations=3,
        )
    
    @staticmethod
    def standard() -> WalkForwardConfig:
        """Standard validation (6 months train, 2 months test, 1 month step, 3 folds)"""
        return WalkForwardConfig(
            train_days=180,
            test_days=60,
            step_days=30,
            n_folds=3,
            purge_days=7,
            min_valid_folds=2,
            population_size=20,
            n_generations=5,
        )
    
    @staticmethod
    def thorough() -> WalkForwardConfig:
        """Thorough validation (1 year train, 3 months test, 1 month step, 5 folds)"""
        return WalkForwardConfig(
            train_days=365,
            test_days=90,
            step_days=30,
            n_folds=5,
            purge_days=14,
            min_valid_folds=3,
            population_size=50,
            n_generations=10,
        )
    
    @staticmethod
    def conservative() -> WalkForwardConfig:
        """Conservative validation (strict thresholds, 3 folds)"""
        return WalkForwardConfig(
            train_days=180,
            test_days=60,
            step_days=30,
            n_folds=3,
            purge_days=7,
            min_valid_folds=3,  # ALL folds must pass!
            min_sharpe_ratio=1.0,
            min_win_rate=50.0,
            max_drawdown_pct=-20.0,
            population_size=30,
            n_generations=8,
        )
