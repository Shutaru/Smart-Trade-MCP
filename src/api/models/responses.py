# -*- coding: utf-8 -*-
"""
Pydantic Response Models

All response schemas for API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


# ===== COMMON MODELS =====

class MetricsModel(BaseModel):
    """Trading metrics model."""
    
    sharpe_ratio: float
    win_rate: float
    max_drawdown_pct: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float


class EquitySummaryModel(BaseModel):
    """Equity curve summary."""
    
    start: float
    end: float
    peak: float
    trough: float


# ===== BACKTEST RESPONSES =====

class BacktestResponse(BaseModel):
    """Response model for single strategy backtest."""
    
    strategy: str
    symbol: str
    timeframe: str
    start_date: str
    end_date: str
    days_tested: int
    candles_tested: int
    total_return: float
    total_trades: int
    tool_version: str
    
    metrics: MetricsModel
    equity_summary: EquitySummaryModel
    
    class Config:
        json_schema_extra = {
            "example": {
                "strategy": "atr_expansion_breakout",
                "symbol": "BTC/USDT",
                "timeframe": "1h",
                "days_tested": 364,
                "total_return": 2.39,
                "total_trades": 21,
                "metrics": {
                    "sharpe_ratio": 0.08,
                    "win_rate": 57.1,
                    "max_drawdown_pct": -10.73
                }
            }
        }


class StrategyComparisonItem(BaseModel):
    """Individual strategy result in comparison."""
    
    strategy: str
    sharpe_ratio: float
    total_return: float
    win_rate: float
    max_drawdown_pct: float
    profit_factor: float
    total_trades: int


class CompareStrategiesResponse(BaseModel):
    """Response model for batch comparison."""
    
    symbol: str
    timeframe: str
    start_date: str
    end_date: str
    days_tested: int
    candles_tested: int
    total_strategies: int
    successful: int
    failed: int
    
    top_3_by_sharpe: List[StrategyComparisonItem]
    top_3_by_return: List[StrategyComparisonItem]
    results: List[StrategyComparisonItem]
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "BTC/USDT",
                "days_tested": 364,
                "total_strategies": 10,
                "successful": 10,
                "top_3_by_sharpe": [
                    {
                        "strategy": "cci_extreme_snapback",
                        "sharpe_ratio": 0.22,
                        "total_return": 7.91
                    }
                ]
            }
        }


# ===== STRATEGY RESPONSES =====

class StrategyInfo(BaseModel):
    """Strategy metadata."""
    
    name: str
    category: str
    description: str
    required_indicators: List[str]


class ListStrategiesResponse(BaseModel):
    """Response model for strategy listing."""
    
    total: int
    strategies: List[StrategyInfo]


# ===== OPTIMIZATION RESPONSES =====

class OptimizationResult(BaseModel):
    """Parameter optimization result."""
    
    strategy: str
    best_params: Dict[str, Any]
    best_fitness: Dict[str, float]
    total_time: float
    total_evaluations: int
    config: Dict[str, int]


class PortfolioWeights(BaseModel):
    """Portfolio optimization weights."""
    
    weights: Dict[str, float]
    portfolio_sharpe: float
    portfolio_max_drawdown: float
    portfolio_total_return: float


# ===== MARKET RESPONSES =====

class MarketRegimeResponse(BaseModel):
    """Market regime detection result."""
    
    regime: str
    confidence: float
    volatility: str
    recommended_strategies: List[str]
    avoid_strategies: List[str]


# ===== ERROR RESPONSE =====

class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid strategy name",
                "detail": "Strategy 'invalid_strategy' not found in registry",
                "timestamp": "2025-11-21T20:00:00"
            }
        }


# ===== HEALTH RESPONSE =====

class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
    version: str
    environment: str
    uptime_seconds: Optional[float] = None
