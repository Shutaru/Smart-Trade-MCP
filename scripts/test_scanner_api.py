
import sys
from pathlib import Path
import json

# Add src to python path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.logger import logger
logger.disabled = True

from src.api.main import app
from fastapi.testclient import TestClient

def test_scanner_endpoints(client):
    """Test scanner API endpoints."""
    print("Testing Scanner API...")
    
    # 1. Test /config
    print("\n1. Testing /config endpoint...")
    try:
        response = client.get("/api/v1/scanner/config")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Success!")
            print(f"Pairs configured: {len(data.get('pairs', []))}")
            print(f"Strategies configured: {len(data.get('strategies', []))}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

    # 2. Test /scan (Manual trigger)
    print("\n2. Testing /scan endpoint...")
    # We use a small subset to make it fast
    payload = {
        "pairs": ["BTC/USDT"],
        "strategies": ["rsi_band_reversion"] 
    }
    
    try:
        response = client.post("/api/v1/scanner/scan", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Success!")
            print(f"Signals found: {data.get('signals_found')}")
            summary = data.get('summary', {})
            print(f"Summary: {json.dumps(summary, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    try:
        # Initialize client here
        client = TestClient(app)
        test_scanner_endpoints(client)
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
