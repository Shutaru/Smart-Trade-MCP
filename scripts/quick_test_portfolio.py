"""
Quick Portfolio API Test - Just verify endpoints are registered
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.core.logger import logger
logger.disabled = True

from src.api.main import app

def test_routes():
    """Check if portfolio routes are registered."""
    print("Checking Portfolio API routes...")
    
    routes = [route.path for route in app.routes]
    
    portfolio_routes = [
        "/api/v1/portfolio/status",
        "/api/v1/portfolio/optimize",
        "/api/v1/portfolio/analyze", 
        "/api/v1/portfolio/rebalance"
    ]
    
    print(f"\nTotal routes: {len(routes)}")
    print("\nPortfolio API endpoints:")
    
    for route in portfolio_routes:
        if route in routes:
            print(f"✓ {route} - FOUND")
        else:
            print(f"✗ {route} - MISSING")
    
    # Check what portfolio routes actually exist
    actual_portfolio_routes = [r for r in routes if '/portfolio' in r]
    print(f"\nActual portfolio routes found: {actual_portfolio_routes}")
    
    return all(route in routes for route in portfolio_routes)

if __name__ == "__main__":
    success = test_routes()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
