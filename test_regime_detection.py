"""
Test Regime Detection

Quick test of regime detection engine.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.mcp_server.tools.regime import detect_market_regime, detect_historical_regimes

print("=" * 80)
print("REGIME DETECTION TEST")
print("=" * 80)
print()


async def test_current_regime():
    """Test current regime detection."""
    print("1. Detecting current market regime...")
    print("-" * 80)
    
    result = await detect_market_regime(
        symbol="BTC/USDT",
        timeframe="1h",
        lookback=100,
    )
    
    if 'error' in result:
        print(f"[ERROR] {result['error']}")
        return
    
    print(f"Regime: {result['regime']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print()
    print("Metrics:")
    for key, value in result['metrics'].items():
        print(f"  {key}: {value:.3f}")
    print()
    print("Recommended Strategies:")
    for strategy in result['recommended_strategies']:
        print(f"  + {strategy}")
    print()
    print("Avoid Strategies:")
    for strategy in result['avoid_strategies']:
        print(f"  - {strategy}")
    print()


async def test_historical_regimes():
    """Test historical regime detection."""
    print()
    print("2. Detecting historical regimes (5000 candles)...")
    print("-" * 80)
    
    result = await detect_historical_regimes(
        symbol="BTC/USDT",
        timeframe="1h",
        limit=5000,
        window_size=100,
    )
    
    if 'error' in result:
        print(f"[ERROR] {result['error']}")
        return
    
    print(f"Total Periods: {result['total_periods']}")
    print()
    print("Regime Distribution:")
    for regime, pct in result['regime_distribution'].items():
        print(f"  {regime}: {pct}%")
    print()
    
    print("Recent Periods (last 10):")
    for period in result['periods'][-10:]:
        print(f"  {period['start']} to {period['end']}")
        print(f"    Regime: {period['regime']}, Duration: {period['duration_hours']}h")
    print()


async def main():
    await test_current_regime()
    await test_historical_regimes()
    
    print("=" * 80)
    print("REGIME DETECTION TEST COMPLETE")
    print("=" * 80)
    print()
    print("Next: Add to MCP server and use in regime-aware backtesting!")


if __name__ == "__main__":
    asyncio.run(main())
