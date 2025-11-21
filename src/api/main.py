"""
FastAPI Backend for Smart Trade MCP Dashboard

Provides REST API endpoints for frontend to consume backtest results,
regime data, and strategy performance metrics.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import json
from typing import List, Dict, Any

app = FastAPI(
    title="Smart Trade MCP API",
    description="REST API for autonomous trading system dashboard",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data file path
DATA_FILE = Path(__file__).parent.parent.parent / "end_to_end_results.json"


def load_results() -> Dict[str, Any]:
    """Load results from JSON file."""
    if not DATA_FILE.exists():
        raise HTTPException(status_code=404, detail="Results file not found")
    
    with open(DATA_FILE) as f:
        return json.load(f)


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "Smart Trade MCP API",
        "version": "1.0.0",
        "endpoints": {
            "/api/strategies": "List all strategies with performance",
            "/api/strategies/top/{n}": "Get top N strategies",
            "/api/regime/distribution": "Get regime distribution",
            "/api/comparison": "Compare best single vs regime-aware",
            "/api/stats": "Get overall statistics",
        }
    }


@app.get("/api/strategies")
async def get_strategies() -> List[Dict[str, Any]]:
    """Get all strategy backtest results."""
    data = load_results()
    return data["backtest_results"]


@app.get("/api/strategies/top/{n}")
async def get_top_strategies(n: int = 10) -> List[Dict[str, Any]]:
    """Get top N performing strategies."""
    data = load_results()
    return data["backtest_results"][:n]


@app.get("/api/regime/distribution")
async def get_regime_distribution() -> Dict[str, float]:
    """Get market regime distribution."""
    data = load_results()
    return data["regime_distribution"]


@app.get("/api/comparison")
async def get_comparison() -> Dict[str, Any]:
    """Get comparison between best single and regime-aware strategies."""
    data = load_results()
    
    best_single = data["backtest_results"][0]
    
    return {
        "best_single": {
            "strategy": best_single["strategy"],
            "total_return": best_single["total_return"],
            "total_trades": best_single["total_trades"],
            "win_rate": best_single["win_rate"],
            "sharpe_ratio": best_single["sharpe_ratio"],
            "max_drawdown_pct": best_single["max_drawdown_pct"],
        },
        "regime_aware": {
            "total_return": data["regime_aware_result"]["total_return"],
            "total_trades": data["regime_aware_result"]["total_trades"],
        },
        "improvement": data["improvement"],
    }


@app.get("/api/stats")
async def get_stats() -> Dict[str, Any]:
    """Get overall statistics."""
    data = load_results()
    
    return {
        "total_strategies": len(data["backtest_results"]),
        "regime_periods": len(data.get("regime_distribution", {})),
        "total_candles": 17420,  # From E2E test
        "data_coverage_days": 726,  # ~2 years
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
