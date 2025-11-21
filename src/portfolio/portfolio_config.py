# -*- coding: utf-8 -*-
"""
Portfolio Optimization Configuration

Type-safe configuration for portfolio optimization.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional
from datetime import datetime


class PortfolioConfig(BaseModel):
    """Configuration for portfolio optimization"""
    
    # Portfolio composition
    strategies: List[str] = Field(
        description="List of strategy names to include in portfolio"
    )
    
    # Optimization method
    optimization_method: Literal["equal_weight", "risk_parity", "max_sharpe", "min_variance"] = Field(
        default="max_sharpe",
        description="Portfolio optimization method"
    )
    
    # Constraints
    min_weight: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum weight per strategy"
    )
    
    max_weight: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Maximum weight per strategy"
    )
    
    allow_shorts: bool = Field(
        default=False,
        description="Allow negative weights (short positions)"
    )
    
    # Rebalancing
    rebalance_frequency: Literal["daily", "weekly", "monthly", "quarterly"] = Field(
        default="monthly",
        description="How often to rebalance portfolio"
    )
    
    rebalance_threshold: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
        description="Rebalance if weight drifts by more than this (5% = 0.05)"
    )
    
    # Risk management
    target_volatility: Optional[float] = Field(
        default=None,
        description="Target portfolio volatility (annualized)"
    )
    
    max_correlation: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Maximum allowed correlation between strategies"
    )
    
    # Backtesting
    initial_capital: float = Field(
        default=10000.0,
        gt=0,
        description="Initial capital for portfolio backtest"
    )
    
    commission: float = Field(
        default=0.001,
        ge=0.0,
        description="Commission rate per trade"
    )
    
    slippage: float = Field(
        default=0.0005,
        ge=0.0,
        description="Slippage rate"
    )
    
    def validate_config(self) -> None:
        """Validate configuration"""
        if self.min_weight > self.max_weight:
            raise ValueError("min_weight cannot be greater than max_weight")
        
        if len(self.strategies) < 2:
            raise ValueError("Portfolio must have at least 2 strategies")


class PortfolioPresets:
    """Common portfolio optimization presets"""
    
    @staticmethod
    def diversified_momentum() -> PortfolioConfig:
        """Diversified momentum portfolio (3 strategies, max Sharpe)"""
        return PortfolioConfig(
            strategies=["ema_stack_momentum", "macd_zero_trend", "adx_trend_filter_plus"],
            optimization_method="max_sharpe",
            min_weight=0.2,
            max_weight=0.5,
            rebalance_frequency="monthly",
        )
    
    @staticmethod
    def mean_reversion_blend() -> PortfolioConfig:
        """Mean reversion blend (risk parity)"""
        return PortfolioConfig(
            strategies=["rsi_band_reversion", "bollinger_mean_reversion", "vwap_mean_reversion"],
            optimization_method="risk_parity",
            min_weight=0.2,
            max_weight=0.5,
            rebalance_frequency="weekly",
        )
    
    @staticmethod
    def balanced_portfolio() -> PortfolioConfig:
        """Balanced portfolio (trend + mean reversion + breakout)"""
        return PortfolioConfig(
            strategies=[
                "trendflow_supertrend",
                "rsi_band_reversion",
                "bollinger_squeeze_breakout",
                "multi_oscillator_confluence",
            ],
            optimization_method="max_sharpe",
            min_weight=0.1,
            max_weight=0.4,
            rebalance_frequency="monthly",
            max_correlation=0.6,
        )
    
    @staticmethod
    def equal_weight() -> PortfolioConfig:
        """Simple equal weight portfolio"""
        return PortfolioConfig(
            strategies=["rsi", "macd", "ema_stack_momentum"],
            optimization_method="equal_weight",
            rebalance_frequency="monthly",
        )
