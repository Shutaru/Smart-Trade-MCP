
import sys
from pathlib import Path
import json

# Add src to python path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.logger import logger
logger.disabled = True

from src.api.main import app
from fastapi.testclient import TestClient

def test_portfolio_endpoints(client):
    """Test portfolio API endpoints."""
    print("Testing Portfolio API...")
    
    # 1. Test /optimize
    print("\n1. Testing /optimize endpoint...")
    payload = {
        "strategies": ["TrendFollowing", "MeanReversion"],
        "optimization_method": "max_sharpe",
        "min_weight": 0.1,
        "max_weight": 0.9,
        "max_correlation": 0.7
    }
    
    try:
        response = client.post("/api/v1/portfolio/optimize", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Success!")
            # Print summary of weights
            weights = data.get('weights', {})
            print(f"Weights: {json.dumps(weights, indent=2)}")
            # Print summary of metrics
            metrics = data.get('metrics', {})
            print(f"Metrics: Sharpe={metrics.get('portfolio_sharpe', 'N/A'):.2f}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

    # 2. Test /analyze
    print("\n2. Testing /analyze endpoint...")
    analyze_payload = {
        "strategies": ["TrendFollowing", "MeanReversion"],
        "lookback_days": 90
    }
    
    try:
        response = client.post("/api/v1/portfolio/analyze", json=analyze_payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Success!")
            corr_matrix = data.get('correlation_matrix', {})
            print(f"Correlation Matrix keys: {list(corr_matrix.keys())}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

    # 3. Test /rebalance
    print("\n3. Testing /rebalance endpoint...")
    rebalance_payload = {
        "current_weights": {"TrendFollowing": 0.6, "MeanReversion": 0.4},
        "target_weights": {"TrendFollowing": 0.5, "MeanReversion": 0.5},
        "total_capital": 10000.0,
        "min_trade_size": 100.0
    }
    
    try:
        response = client.post("/api/v1/portfolio/rebalance", json=rebalance_payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Success!")
            trades = data.get('trades', [])
            print(f"Trades generated: {len(trades)}")
            if trades:
                print(f"First trade: {trades[0]}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    try:
        # Initialize client here to avoid multiprocessing issues
        client = TestClient(app)
        test_portfolio_endpoints(client)
    except Exception as e:
        with open("test_error.txt", "w") as f:
            f.write(str(e))
        print(f"CRITICAL ERROR: {e}")
