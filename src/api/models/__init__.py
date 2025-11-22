# -*- coding: utf-8 -*-
"""API Models Package."""

from .requests import (
    BacktestRequest,
    CompareStrategiesRequest,
    OptimizeParametersRequest,
    OptimizePortfolioRequest,
    WalkForwardRequest,
    MarketRegimeRequest,
)

from .responses import (
    BacktestResponse,
    CompareStrategiesResponse,
    ListStrategiesResponse,
    StrategyInfo,
    ErrorResponse,
    HealthResponse,
)

__all__ = [
    # Requests
    "BacktestRequest",
    "CompareStrategiesRequest",
    "OptimizeParametersRequest",
    "OptimizePortfolioRequest",
    "WalkForwardRequest",
    "MarketRegimeRequest",
    # Responses
    "BacktestResponse",
    "CompareStrategiesResponse",
    "ListStrategiesResponse",
    "StrategyInfo",
    "ErrorResponse",
    "HealthResponse",
]
