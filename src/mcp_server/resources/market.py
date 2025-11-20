"""Market status resource for MCP."""

import json


async def get_market_status() -> str:
    """Get current market status as JSON string."""
    # TODO: Implement in Phase 2
    return json.dumps({
        "regime": "unknown",
        "volatility": "normal",
        "trend": "neutral",
    })


__all__ = ["get_market_status"]
