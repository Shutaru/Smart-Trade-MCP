"""Portfolio resource for MCP."""

import json


async def get_current_portfolio() -> str:
    """Get current portfolio as JSON string."""
    # TODO: Implement in Phase 2
    return json.dumps({
        "holdings": [],
        "total_value": 0.0,
        "cash": 10000.0,
    })


__all__ = ["get_current_portfolio"]
