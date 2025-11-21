# -*- coding: utf-8 -*-
"""
Validate Champion Strategy - Multi Oscillator Confluence

Runs comprehensive Walk-Forward Analysis on the best performing strategy
from the end-to-end test to confirm it's not overfitted.

Results from E2E test:
- Total Return: 31.90% (2 years)
- Win Rate: 70.6%
- Trades: 466
- Sharpe: 0.27

Now we validate with WFA to ensure out-of-sample performance!
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from src.core.data_manager import DataManager
from src.core.backtest_engine import BacktestEngine
from src.core.indicators import calculate_all_indicators
from src.strategies import registry
from src.core.logger import logger

print("=" * 80)
print("CHAMPION VALIDATION - Multi Oscillator Confluence")
print("Walk-Forward Analysis on 2 Years of Data")
print("=" * 80)
print()


async def main():
    """Validate the champion strategy."""
    
    # Get the champion
    print("Loading champion strategy...")
    strategy = registry.get("multi_oscillator_confluence")
    print(f"[OK] Strategy: {strategy.name}")
    print()
    
    # Fetch 2 years of data (same as E2E test)
    print("Fetching 2 years of BTC/USDT data...")
    dm = DataManager()
    
    start_date = datetime.now() - timedelta(days=730)
    end_date = datetime.now()
    
    df = await dm.fetch_historical(
        symbol="BTC/USDT",
        timeframe="1h",
        start_date=start_date,
        end_date=end_date,
        max_candles=20000,
    )
    
    await dm.close()
    
    if df.empty:
        print("[ERROR] No data fetched!")
        return
    
    days = (df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).days
    print(f"[OK] Fetched {len(df)} candles")
    print(f"    Coverage: {days} days ({days/365:.2f} years)")
    print()
    
    # Calculate required indicators
    print("Calculating indicators...")
    required = strategy.get_required_indicators()
    df = calculate_all_indicators(df, required, use_gpu=False)
    print(f"[OK] Calculated {len(required)} indicators: {', '.join(required)}")
    print()
    
    # Run Walk-Forward Analysis
    print("=" * 80)
    print("RUNNING WALK-FORWARD ANALYSIS")
    print("=" * 80)
    print()
    print("Configuration:")
    print("  Train Window: 180 days (6 months)")
    print("  Test Window: 60 days (2 months)")
    print("  Step Size: 30 days (1 month)")
    print("  Parallel: Yes (all CPU cores)")
    print()
    
    engine = BacktestEngine(initial_capital=10000.0, use_gpu=False)
    
    results = engine.walk_forward_analysis(
        strategy=strategy,
        df=df,
        train_days=180,  # 6 months training
        test_days=60,    # 2 months testing
        step_days=30,    # 1 month rolling step
        parallel=True,
        n_jobs=-1,
    )
    
    # Print detailed results
    print()
    print("=" * 80)
    print("WALK-FORWARD ANALYSIS RESULTS")
    print("=" * 80)
    print()
    
    print(f"Windows Analyzed:     {results['n_windows']}")
    print(f"Stability Ratio:      {results['stability_ratio']:.3f} (target: >0.7)")
    print(f"Consistency:          {results['consistency']:.1f}% (target: >70%)")
    print()
    print(f"Avg In-Sample:        {results['avg_in_sample_return']:.2f}%")
    print(f"Avg Out-Sample:       {results['avg_out_sample_return']:.2f}%")
    print()
    print(f"Best In-Sample:       {results['best_in_sample_return']:.2f}%")
    print(f"Worst In-Sample:      {results['worst_in_sample_return']:.2f}%")
    print(f"Best Out-Sample:      {results['best_out_sample_return']:.2f}%")
    print(f"Worst Out-Sample:     {results['worst_out_sample_return']:.2f}%")
    print()
    
    # Recommendation
    print("=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    print()
    print(f"{results['recommendation']}")
    print()
    
    # Interpret
    if results['recommendation'].startswith("PASS"):
        print("? SUCCESS! Strategy VALIDATED!")
        print()
        print("The Multi Oscillator Confluence strategy:")
        print("  - Shows consistent out-of-sample performance")
        print("  - Has stable results across different market periods")
        print("  - Is READY for parameter optimization")
        print("  - Can be considered for production deployment")
        print()
        print("Next Steps:")
        print("  1. Run parameter optimization (Genetic Algorithm)")
        print("  2. Test on paper trading (Binance Testnet)")
        print("  3. Monitor performance for 1-2 weeks")
        print("  4. Deploy to live trading with small capital")
        
    elif results['recommendation'].startswith("MARGINAL"):
        print("??  MARGINAL - Strategy needs improvement")
        print()
        print("The strategy shows some promise but:")
        print("  - Out-of-sample performance is inconsistent")
        print("  - May benefit from parameter tuning")
        print("  - Should be optimized before deployment")
        print()
        print("Next Steps:")
        print("  1. Run parameter optimization")
        print("  2. Re-validate with WFA")
        print("  3. Consider adding filters or regime detection")
        
    else:
        print("? FAILED - Strategy is overfitted!")
        print()
        print("Unfortunately, the strategy:")
        print("  - Does NOT generalize to unseen data")
        print("  - Shows signs of curve-fitting")
        print("  - Should NOT be used in production")
        print()
        print("The high E2E return (31.90%) was likely due to:")
        print("  - Specific market conditions in the test period")
        print("  - Overfitting to historical data")
        print()
        print("Next Steps:")
        print("  1. Redesign strategy with more robust logic")
        print("  2. Add regime filters")
        print("  3. Test on different timeframes/symbols")
    
    print()
    print("=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    
    # Save results
    import json
    
    validation_results = {
        'strategy': 'multi_oscillator_confluence',
        'timestamp': datetime.now().isoformat(),
        'data_coverage_days': days,
        'total_candles': len(df),
        'wfa_results': {
            'n_windows': results['n_windows'],
            'stability_ratio': results['stability_ratio'],
            'consistency': results['consistency'],
            'avg_in_sample': results['avg_in_sample_return'],
            'avg_out_sample': results['avg_out_sample_return'],
            'recommendation': results['recommendation'],
        },
        'e2e_results': {
            'total_return': 31.90,
            'win_rate': 70.6,
            'trades': 466,
            'sharpe': 0.27,
        }
    }
    
    with open('champion_validation.json', 'w') as f:
        json.dump(validation_results, f, indent=2)
    
    print()
    print("Results saved to: champion_validation.json")
    print()


if __name__ == "__main__":
    asyncio.run(main())
