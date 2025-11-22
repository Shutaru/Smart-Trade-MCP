# -*- coding: utf-8 -*-
"""
Portfolio Router

REST API endpoints for portfolio management.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/status", summary="Get portfolio status")
async def get_portfolio_status():
    """Get current portfolio status (placeholder)."""
    return {"status": "not_implemented"}
