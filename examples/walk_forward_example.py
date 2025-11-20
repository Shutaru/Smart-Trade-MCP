"""
Walk-Forward Analysis Example

Demonstrates how to use the Walk-Forward Analysis tool to validate
trading strategies and detect overfitting.

This is the CRITICAL step before deploying any strategy to production.
"""

import asyncio
import json
from datetime import datetime

from src.core.backtest_engine import BacktestEngine
from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators
from src.strategies import registry
from src.core.logger import logger


async def main():
    """Run Walk-Forward Analysis on TOP 3 strategies."""
    
    print("=" * 80)
    print("WALK-FORWARD ANALYSIS - VALIDATION OF TOP 3 STRATEGIES")
    print("=" * 80)
    print()
    
    # TOP 3 strategies to validate
    strategies_to_test = [
        "multi_oscillator_confluence",  # +15.27% in backtest
        "cci_extreme_snapback",         # +8.75% in backtest
        "bollinger_mean_reversion",     # +2.91% in backtest
    ]
    
    symbol = "BTC/USDT"
    timeframe = "1h"
    initial_capital = 10000.0
    
    # WFA parameters
    train_days = 180  # 6 months training
    test_days = 60    # 2 months testing
    step_days = 30    # 1 month step (50% overlap)
    
    results_summary = []
    
    for strategy_name in strategies_to_test:
        print(f"\n{'='*80}")
        print(f"VALIDATING: {strategy_name.upper()}")
        print(f"{'='*80}\n")
        
        try:
            # Get strategy
            strategy = registry.get(strategy_name)
            
            # Fetch data
            print(f"?? Fetching market data for {symbol}...")
            dm = DataManager()
            
            # Need ~1 year of data for meaningful WFA
            df = await dm.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=365 * 24,  # ~1 year of hourly data
            )
            
            await dm.close()
            
            print(f"? Fetched {len(df)} candles")
            print(f"   Period: {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
            print(f"   Days: {(df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).days}")
            
            # Calculate indicators
            print(f"\n?? Calculating indicators: {strategy.get_required_indicators()}")
            df = calculate_all_indicators(df, strategy.get_required_indicators())
            print("? Indicators calculated")
            
            # Run Walk-Forward Analysis
            print(f"\n?? Running Walk-Forward Analysis...")
            print(f"   Train window: {train_days} days")
            print(f"   Test window: {test_days} days")
            print(f"   Step size: {step_days} days")
            print(f"   Parallel: True (using all CPU cores)\n")
            
            engine = BacktestEngine(initial_capital=initial_capital)
            
            wfa_results = engine.walk_forward_analysis(
                strategy=strategy,
                df=df,
                train_days=train_days,
                test_days=test_days,
                step_days=step_days,
                optimize_func=None,  # No optimization yet
                parallel=True,
                n_jobs=-1,  # Use all CPUs
            )
            
            # Display results
            print("\n" + "="*80)
            print("WALK-FORWARD ANALYSIS RESULTS")
            print("="*80)
            print(f"\n?? Strategy: {strategy_name}")
            print(f"?? Windows Analyzed: {wfa_results['n_windows']}")
            print(f"\n?? KEY METRICS:")
            print(f"   Stability Ratio:      {wfa_results['stability_ratio']:.3f}  {'? PASS' if wfa_results['stability_ratio'] >= 0.7 else '??  MARGINAL' if wfa_results['stability_ratio'] >= 0.5 else '? FAIL'}")
            print(f"   Consistency:          {wfa_results['consistency']:.1f}%  {'? PASS' if wfa_results['consistency'] >= 70 else '??  MARGINAL' if wfa_results['consistency'] >= 50 else '? FAIL'}")
            print(f"\n?? RETURNS:")
            print(f"   Avg In-Sample:        {wfa_results['avg_in_sample_return']:+.2f}%")
            print(f"   Avg Out-of-Sample:    {wfa_results['avg_out_sample_return']:+.2f}%  {'? PROFITABLE' if wfa_results['avg_out_sample_return'] > 0 else '? LOSING'}")
            print(f"   Std In-Sample:        {wfa_results['std_in_sample_return']:.2f}%")
            print(f"   Std Out-of-Sample:    {wfa_results['std_out_sample_return']:.2f}%")
            print(f"\n?? BEST WINDOW:")
            best = wfa_results['best_window']
            print(f"   Window #{best['window_id']}")
            print(f"   Out-Sample Return:    {best['out_sample_return']:+.2f}%")
            print(f"   Sharpe Ratio:         {best['out_sample_sharpe']:.2f}")
            print(f"\n?? WORST WINDOW:")
            worst = wfa_results['worst_window']
            print(f"   Window #{worst['window_id']}")
            print(f"   Out-Sample Return:    {worst['out_sample_return']:+.2f}%")
            print(f"   Sharpe Ratio:         {worst['out_sample_sharpe']:.2f}")
            print(f"\n?? RECOMMENDATION:")
            print(f"   {wfa_results['recommendation']}")
            print("="*80)
            
            # Store summary
            results_summary.append({
                'strategy': strategy_name,
                'stability_ratio': wfa_results['stability_ratio'],
                'consistency': wfa_results['consistency'],
                'avg_out_sample_return': wfa_results['avg_out_sample_return'],
                'recommendation': wfa_results['recommendation'],
            })
            
            # Save detailed results to file
            filename = f"wfa_{strategy_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(wfa_results, f, indent=2, default=str)
            print(f"\n?? Detailed results saved to: {filename}\n")
            
        except Exception as e:
            logger.error(f"Error validating {strategy_name}: {e}", exc_info=True)
            print(f"\n? ERROR: {e}\n")
            results_summary.append({
                'strategy': strategy_name,
                'error': str(e),
            })
    
    # Final summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY - ALL STRATEGIES")
    print("="*80)
    print()
    
    for result in results_summary:
        if 'error' in result:
            print(f"? {result['strategy']}: ERROR - {result['error']}")
        else:
            status = "? PASS" if "PASS" in result['recommendation'] else "??  MARGINAL" if "MARGINAL" in result['recommendation'] else "? FAIL"
            print(f"{status} {result['strategy']}")
            print(f"   Stability: {result['stability_ratio']:.3f} | Consistency: {result['consistency']:.1f}% | Avg Return: {result['avg_out_sample_return']:+.2f}%")
            print(f"   {result['recommendation']}")
            print()
    
    print("="*80)
    print("NEXT STEPS:")
    print("="*80)
    print()
    print("? Strategies that PASSED:")
    print("   ? Ready for parameter optimization (Genetic Algorithm)")
    print("   ? Consider portfolio construction")
    print()
    print("??  Strategies that are MARGINAL:")
    print("   ? Try different parameter ranges")
    print("   ? Consider different timeframes")
    print("   ? May need additional filters")
    print()
    print("? Strategies that FAILED:")
    print("   ? Likely overfitted - DO NOT USE IN PRODUCTION")
    print("   ? Revisit strategy logic")
    print("   ? May work better on different symbols/timeframes")
    print()
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
