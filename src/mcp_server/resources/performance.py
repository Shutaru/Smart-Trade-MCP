"""Performance metrics resource for MCP."""

import json


async def get_performance_metrics() -> str:
    """Get performance metrics as JSON string."""
    # TODO: Implement in Phase 2
    return json.dumps({
        "sharpe_ratio": 0.0,
        "win_rate": 0.0,
        "total_trades": 0,
        "pnl": 0.0,
    })


__all__ = ["get_performance_metrics"]
