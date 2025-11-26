# -*- coding: utf-8 -*-
"""
FastAPI Application - Smart-Trade API v3.0.0

Production-grade REST API for Smart-Trade MCP platform.
Provides HTTP/WebSocket access to all backtesting and optimization features.

**NEW in v3.0.0:**
- Complete rewrite with production-grade architecture
- Pydantic models for request/response validation
- Structured routers (strategies, backtest, optimization, portfolio, market)
- Reuses all MCP tools (no code duplication)
- Comprehensive error handling
- CORS, compression, logging middleware
- OpenAPI documentation at /api/docs

**Migration from v1.0.0:**
- All endpoints now under /api/v1/
- Request/response models enforced
- Better error messages
- Performance improvements
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time

from .config import settings
from .routers import strategies, backtest, optimization, portfolio, market, pairs, scanner
from .routers import paper
from ..core.logger import logger

# Track startup time
START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("=" * 80)
    logger.info("SMART-TRADE API v3.0.0 - STARTUP")
    logger.info("=" * 80)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Host: {settings.HOST}:{settings.PORT}")
    logger.info(f"Debug: {settings.DEBUG}")
    logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")
    logger.info(f"API Docs: http://{settings.HOST}:{settings.PORT}/api/docs")
    logger.info("=" * 80)
    
    yield
    
    # Shutdown
    logger.info("SMART-TRADE API - SHUTDOWN")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
**Smart-Trade API** - Professional algorithmic trading platform.

## Features

- ?? **Batch Processing** - Compare 41+ strategies in 15 seconds (20-30x faster!)
- ? **Optimized Responses** - 3KB vs 500KB (166x smaller)
- ?? **42+ Strategies** - Breakout, trend, mean reversion, momentum, hybrid, advanced
- ?? **Comprehensive Backtesting** - GPU-accelerated, 1-year auto-fetch
- ?? **Genetic Optimization** - Auto-find best parameters
- ?? **Portfolio Optimization** - Multi-strategy allocation
- ?? **Market Regime Detection** - Adaptive strategy selection

## Quick Start

1. **List Strategies:** `GET /api/v1/strategies/`
2. **Compare All:** `POST /api/v1/backtest/compare`
3. **Single Backtest:** `POST /api/v1/backtest/single`
4. **Detect Regime:** `POST /api/v1/market/regime`
5. **Optimize Portfolio:** `POST /api/v1/optimization/portfolio`

## Performance

- Single backtest: 1-2 sec
- Batch comparison (41 strategies): ~15 sec
- Parameter optimization: 2-5 min
- Portfolio optimization: 2-3 min

## Authentication

Currently no authentication required. API key support planned for production deployment.
    """,
    version=settings.API_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


# Middleware - CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware - Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred processing your request",
            "path": str(request.url),
        },
    )


# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns API status and uptime.
    """
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": round(time.time() - START_TIME, 2),
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    API root endpoint.
    
    Provides quick links to documentation and health check.
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.API_VERSION,
        "status": "operational",
        "docs": "/api/docs",
        "health": "/health",
        "endpoints": {
            "strategies": f"{settings.API_V1_PREFIX}/strategies/",
            "backtest": f"{settings.API_V1_PREFIX}/backtest/",
            "optimization": f"{settings.API_V1_PREFIX}/optimization/",
            "portfolio": f"{settings.API_V1_PREFIX}/portfolio/",
            "market": f"{settings.API_V1_PREFIX}/market/",
            "pairs": f"{settings.API_V1_PREFIX}/pairs/",
        },
    }


# Include routers
app.include_router(
    strategies.router,
    prefix=f"{settings.API_V1_PREFIX}/strategies",
    tags=["Strategies"],
)

app.include_router(
    backtest.router,
    prefix=f"{settings.API_V1_PREFIX}/backtest",
    tags=["Backtest"],
)

app.include_router(
    optimization.router,
    prefix=f"{settings.API_V1_PREFIX}/optimization",
    tags=["Optimization"],
)

app.include_router(
    portfolio.router,
    prefix=f"{settings.API_V1_PREFIX}/portfolio",
    tags=["Portfolio"],
)

app.include_router(
    market.router,
    prefix=f"{settings.API_V1_PREFIX}/market",
    tags=["Market"],
)

app.include_router(
    pairs.router,
    prefix=f"{settings.API_V1_PREFIX}/pairs",
    tags=["Pair Management"],
)

app.include_router(
    paper.router,
    prefix=f"{settings.API_V1_PREFIX}/paper",
    tags=["Paper Trading"],
)

app.include_router(
    scanner.router,
    prefix=f"{settings.API_V1_PREFIX}/scanner",
    tags=["Signal Scanner"],
)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
