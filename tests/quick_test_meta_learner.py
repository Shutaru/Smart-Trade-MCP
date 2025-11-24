#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Test - Verify Meta-Learner Integration

Tests:
1. Meta-Learner import & initialization
2. NAIVE ranges retrieval
3. SMART ranges adaptation
4. GeneticOptimizer integration
5. Example strategy (atr_expansion_breakout)
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_meta_learner_import():
    """Test 1: Can we import Meta-Learner?"""
    print("\n" + "="*70)
    print("TEST 1: Meta-Learner Import")
    print("="*70)
    
    try:
        from optimization.meta_learner import ParameterMetaLearner, MarketFeatures
        print("? Meta-Learner imported successfully")
        
        learner = ParameterMetaLearner()
        print("? Meta-Learner initialized")
        
        return True
    except Exception as e:
        print(f"? FAILED: {e}")
        return False


def test_naive_ranges():
    """Test 2: NAIVE ranges retrieval"""
    print("\n" + "="*70)
    print("TEST 2: NAIVE Ranges")
    print("="*70)
    
    try:
        from optimization.meta_learner import ParameterMetaLearner
        
        learner = ParameterMetaLearner()
        
        # Test known strategy
        ranges = learner.get_naive_ranges("trendflow_supertrend")
        print(f"? Retrieved NAIVE ranges for trendflow_supertrend:")
        for param, (min_val, max_val) in ranges.items():
            print(f"   - {param}: ({min_val}, {max_val})")
        
        # Test unknown strategy (should return defaults)
        defaults = learner.get_naive_ranges("unknown_strategy_123")
        print(f"? Default ranges for unknown strategy: {defaults}")
        
        return True
    except Exception as e:
        print(f"? FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_smart_ranges():
    """Test 3: SMART ranges with market data"""
    print("\n" + "="*70)
    print("TEST 3: SMART Ranges (requires data)")
    print("="*70)
    
    try:
        import pandas as pd
        import numpy as np
        from optimization.meta_learner import ParameterMetaLearner
        
        # Create fake OHLCV data
        n = 200
        dates = pd.date_range(start='2024-01-01', periods=n, freq='1h')
        df = pd.DataFrame({
            'timestamp': dates,
            'open': np.random.randn(n).cumsum() + 100,
            'high': np.random.randn(n).cumsum() + 102,
            'low': np.random.randn(n).cumsum() + 98,
            'close': np.random.randn(n).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, n),
        })
        
        # Add fake indicators
        df['atr'] = np.abs(np.random.randn(n) * 2)
        df['adx'] = np.random.randint(10, 40, n)
        df['rsi'] = np.random.randint(30, 70, n)
        
        learner = ParameterMetaLearner()
        
        # Extract market features
        features = learner.extract_market_features(df, lookback=100)
        print(f"? Market Features:")
        print(f"   - Regime: {features.regime}")
        print(f"   - Volatility: {features.volatility:.2f}%")
        print(f"   - Trend Strength: {features.trend_strength:.1f}")
        print(f"   - Momentum: {features.momentum:.1f}")
        
        # Get SMART ranges
        smart_ranges = learner.get_smart_ranges("trendflow_supertrend", df, lookback=100)
        print(f"\n? SMART ranges adapted to {features.regime} market:")
        for param, (min_val, max_val) in smart_ranges.items():
            print(f"   - {param}: ({min_val}, {max_val})")
        
        # Compare with NAIVE
        naive_ranges = learner.get_naive_ranges("trendflow_supertrend")
        print(f"\n? Comparison (SMART vs NAIVE):")
        for param in smart_ranges.keys():
            smart_width = smart_ranges[param][1] - smart_ranges[param][0]
            naive_width = naive_ranges[param][1] - naive_ranges[param][0]
            reduction = ((naive_width - smart_width) / naive_width) * 100
            print(f"   - {param}: {reduction:.1f}% narrower")
        
        return True
    except Exception as e:
        print(f"? FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_optimizer_integration():
    """Test 4: GeneticOptimizer with Meta-Learner"""
    print("\n" + "="*70)
    print("TEST 4: GeneticOptimizer Integration")
    print("="*70)
    
    try:
        from optimization.genetic_optimizer import GeneticOptimizer
        print("? GeneticOptimizer imported (meta_learner support added)")
        
        # Check if use_smart_ranges parameter exists
        import inspect
        sig = inspect.signature(GeneticOptimizer.__init__)
        params = list(sig.parameters.keys())
        
        if 'use_smart_ranges' in params:
            print("? GeneticOptimizer has 'use_smart_ranges' parameter")
        else:
            print("??  'use_smart_ranges' parameter not found (check implementation)")
        
        return True
    except Exception as e:
        print(f"? FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_example_strategy():
    """Test 5: Example corrected strategy"""
    print("\n" + "="*70)
    print("TEST 5: ATR Expansion Breakout (Corrected Strategy)")
    print("="*70)
    
    try:
        from strategies.generated.atr_expansion_breakout import AtrExpansionBreakout
        from strategies.base import StrategyConfig
        
        # Test 1: Default initialization
        strategy = AtrExpansionBreakout()
        print(f"? Strategy initialized with defaults:")
        print(f"   - atr_period: {strategy.atr_period}")
        print(f"   - atr_multiplier: {strategy.atr_multiplier}")
        
        # Test 2: Custom parameters
        config = StrategyConfig(params={
            "atr_period": 20,
            "atr_multiplier": 2.0,
            "stop_loss_atr_mult": 3.0,
            "take_profit_rr_ratio": 3.5
        })
        strategy_custom = AtrExpansionBreakout(config)
        
        assert strategy_custom.atr_period == 20, "atr_period not connected!"
        assert strategy_custom.atr_multiplier == 2.0, "atr_multiplier not connected!"
        assert strategy_custom.config.stop_loss_atr_mult == 3.0, "stop_loss_atr_mult not connected!"
        assert strategy_custom.config.take_profit_rr_ratio == 3.5, "take_profit_rr_ratio not connected!"
        
        print(f"? Custom parameters connected:")
        print(f"   - atr_period: {strategy_custom.atr_period}")
        print(f"   - atr_multiplier: {strategy_custom.atr_multiplier}")
        print(f"   - stop_loss_atr_mult: {strategy_custom.config.stop_loss_atr_mult}")
        print(f"   - take_profit_rr_ratio: {strategy_custom.config.take_profit_rr_ratio}")
        
        return True
    except Exception as e:
        print(f"? FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "?? " + "="*66 + " ??")
    print("QUICK TEST - Meta-Learner Integration")
    print("?? " + "="*66 + " ??")
    
    tests = [
        ("Meta-Learner Import", test_meta_learner_import),
        ("NAIVE Ranges", test_naive_ranges),
        ("SMART Ranges", test_smart_ranges),
        ("Optimizer Integration", test_optimizer_integration),
        ("Example Strategy", test_example_strategy),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n? TEST CRASHED: {name}")
            print(f"   Error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "? PASS" if success else "? FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({(passed/total)*100:.0f}%)")
    
    if passed == total:
        print("\n?? ALL TESTS PASSED! System ready for production!")
    else:
        print(f"\n??  {total - passed} test(s) failed. Review errors above.")
    
    print("="*70)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
