"""
Strategy Diagnostic and Improvement Test

Tests the new diagnostic tool and applies suggested fixes.
"""

import asyncio
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

from src.mcp_server.tools.strategy_diagnostics import (
    diagnose_strategy_failure,
    suggest_parameter_fixes,
)

print("=" * 80)
print("STRATEGY DIAGNOSTICS - Analyzing Failed Strategies")
print("=" * 80)
print()

# TOP 3 strategies that failed WFA
FAILED_STRATEGIES = [
    "multi_oscillator_confluence",
    "cci_extreme_snapback",
    "bollinger_mean_reversion",
]


async def diagnose_and_fix():
    """Diagnose failures and suggest fixes."""
    
    for i, strategy_name in enumerate(FAILED_STRATEGIES, 1):
        print(f"\n[{i}/{len(FAILED_STRATEGIES)}] Diagnosing: {strategy_name}")
        print("-" * 80)
        
        # Run diagnosis
        diagnosis = await diagnose_strategy_failure(
            strategy_name=strategy_name,
            limit=1000,
        )
        
        if 'error' in diagnosis:
            print(f"[ERROR] {diagnosis['error']}")
            continue
        
        # Print results
        print()
        print(f"Strategy: {diagnosis['strategy']}")
        print(f"Severity: {diagnosis['severity']}")
        print()
        
        print("Issues Found:")
        for issue in diagnosis['issues_found']:
            print(f"  - {issue}")
        print()
        
        print("Metrics:")
        metrics = diagnosis['metrics']
        print(f"  Total Trades:    {metrics['total_trades']}")
        print(f"  Total Return:    {metrics['total_return']:.2f}%")
        print(f"  Win Rate:        {metrics['win_rate']:.1f}%")
        print(f"  Max Drawdown:    {metrics['max_drawdown_pct']:.1f}%")
        print(f"  Sharpe Ratio:    {metrics['sharpe_ratio']:.2f}")
        print()
        
        print("Suggestions:")
        for suggestion in diagnosis['suggestions']:
            print(f"  {suggestion}")
        print()
        
        if diagnosis['parameter_adjustments']:
            print("Parameter Adjustments Recommended:")
            for param, details in diagnosis['parameter_adjustments'].items():
                print(f"\n  {param}:")
                if 'current' in details:
                    print(f"    Current:   {details['current']}")
                print(f"    Suggested: {details['suggested']}")
                print(f"    Reason:    {details['reason']}")
        print()
        
        print(f"Recommended Action: {diagnosis['recommended_action']}")
        print()
        
        # Get detailed fixes
        print("Getting detailed parameter fixes...")
        fixes = await suggest_parameter_fixes(
            strategy_name=strategy_name,
            diagnosis=diagnosis,
        )
        
        if 'error' in fixes:
            print(f"[ERROR] {fixes['error']}")
            continue
        
        print()
        print("Implementation Guide:")
        if fixes['implementation_code']:
            for i, code_change in enumerate(fixes['implementation_code'], 1):
                print(f"\n  Change {i}: {code_change['location']}")
                print(f"  Reason: {code_change['reason']}")
                print(f"  Code:")
                print(f"    {code_change['change']}")
        else:
            print("  No specific code changes generated")
        
        print()
        print("=" * 80)
        
        # Save diagnosis to file
        filename = f"diagnosis_{strategy_name}.json"
        with open(filename, 'w') as f:
            json.dump(diagnosis, f, indent=2)
        print(f"Diagnosis saved to: {filename}")
        print()
    
    print()
    print("=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)
    print()
    print("All diagnoses complete!")
    print()
    print("Next Steps:")
    print("  1. Review diagnosis files for each strategy")
    print("  2. Apply suggested parameter changes")
    print("  3. Re-run Walk-Forward Analysis with 2 years of data")
    print("  4. Validate improvements")
    print()


if __name__ == "__main__":
    asyncio.run(diagnose_and_fix())
