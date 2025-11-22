# -*- coding: utf-8 -*-
"""
Pydantic Request Models

All request schemas for API endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date


# ===== BACKTEST REQUESTS =====

class BacktestRequest(BaseModel):
    """Request model for single strategy backtest."""
    
    strategy_name: str = Field(..., description="Strategy identifier")
    symbol: str = Field(default="BTC/USDT", description="Trading pair")
    timeframe: str = Field(default="1h", description="Candle timeframe")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    initial_capital: float = Field(default=10000.0, description="Starting capital", gt=0)
    
    @validator('timeframe')
    def validate_timeframe(cls, v):
        valid = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']
        if v not in valid:
            raise ValueError(f"Timeframe must be one of {valid}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "strategy_name": "atr_expansion_breakout",
                "symbol": "BTC/USDT",
                "timeframe": "1h",
                "initial_capital": 10000
            }
        }


class CompareStrategiesRequest(BaseModel):
    """Request model for batch strategy comparison."""
    
    strategies: List[str] = Field(..., description="List of strategy names", min_length=1)
    symbol: str = Field(default="BTC/USDT", description="Trading pair")
    timeframe: str = Field(default="1h", description="Candle timeframe")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    initial_capital: float = Field(default=10000.0, description="Starting capital", gt=0)
    
    @validator('strategies')
    def validate_strategies_count(cls, v):
        if len(v) > 100:
            raise ValueError("Maximum 100 strategies per request")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "strategies": [
                    "atr_expansion_breakout",
                    "ema_stack_momentum",
                    "bollinger_mean_reversion"
                ],
                "symbol": "BTC/USDT",
                "timeframe": "1h"
            }
        }


# ===== OPTIMIZATION REQUESTS =====

class OptimizeParametersRequest(BaseModel):
    """Request model for parameter optimization."""
    
    strategy_name: str = Field(..., description="Strategy to optimize")
    symbol: str = Field(default="BTC/USDT", description="Trading pair")
    timeframe: str = Field(default="1h", description="Candle timeframe")
    population_size: int = Field(default=50, description="GA population size", ge=10, le=200)
    n_generations: int = Field(default=20, description="Number of generations", ge=5, le=100)
    use_ray: bool = Field(default=False, description="Use Ray for parallel processing")
    
    class Config:
        json_schema_extra = {
            "example": {
                "strategy_name": "rsi",
                "population_size": 30,
                "n_generations": 10
            }
        }


class OptimizePortfolioRequest(BaseModel):
    """Request model for portfolio optimization."""
    
    strategies: List[str] = Field(..., description="Strategies to include", min_length=2)
    symbol: str = Field(default="BTC/USDT", description="Trading pair")
    timeframe: str = Field(default="1h", description="Candle timeframe")
    method: str = Field(
        default="max_sharpe",
        description="Optimization method",
    )
    
    @validator('method')
    def validate_method(cls, v):
        valid = ['equal_weight', 'risk_parity', 'max_sharpe', 'min_variance']
        if v not in valid:
            raise ValueError(f"Method must be one of {valid}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "strategies": [
                    "atr_expansion_breakout",
                    "ema_stack_momentum",
                    "vwap_institutional_trend"
                ],
                "method": "max_sharpe"
            }
        }


# ===== VALIDATION REQUESTS =====

class WalkForwardRequest(BaseModel):
    """Request model for Walk-Forward Analysis."""
    
    strategy_name: str = Field(..., description="Strategy to validate")
    symbol: str = Field(default="BTC/USDT", description="Trading pair")
    timeframe: str = Field(default="1h", description="Candle timeframe")
    train_days: int = Field(default=180, description="Training window (days)", ge=30)
    test_days: int = Field(default=60, description="Testing window (days)", ge=10)
    step_days: int = Field(default=30, description="Step size (days)", ge=10)
    
    class Config:
        json_schema_extra = {
            "example": {
                "strategy_name": "atr_expansion_breakout",
                "train_days": 180,
                "test_days": 60
            }
        }


# ===== MARKET REQUESTS =====

class MarketRegimeRequest(BaseModel):
    """Request model for market regime detection."""
    
    symbol: str = Field(default="BTC/USDT", description="Trading pair")
    timeframe: str = Field(default="1h", description="Candle timeframe")
    lookback: int = Field(default=100, description="Candles to analyze", ge=20, le=1000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "BTC/USDT",
                "lookback": 100
            }
        }
