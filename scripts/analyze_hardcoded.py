#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EMERGENCY FIX - Find Hardcoded Values in generate_signals()

Identifies strategies with parameters in __init__ but not used in generate_signals().
"""

from pathlib import Path
import re


def analyze_strategy(file_path):
    """Analyze a strategy for hardcoded values"""
    content = file_path.read_text(encoding='utf-8')
    
    # Extract parameters from __init__
    init_match = re.search(r'def __init__.*?(?=\n    def )', content, re.DOTALL)
    if not init_match:
        return None, None, None
    
    init_code = init_match.group(0)
    
    # Find all self.param = self.config.get("param", default)
    params = re.findall(r'self\.(\w+) = self\.config\.get\("(\w+)"', init_code)
    
    if not params:
        return [], [], []
    
    # Extract generate_signals method
    gen_match = re.search(r'def generate_signals.*?(?=\n    def |\Z)', content, re.DOTALL)
    if not gen_match:
        return params, [], []
    
    gen_code = gen_match.group(0)
    
    # Check which params are actually used in generate_signals
    used_params = []
    unused_params = []
    
    for param_name, config_name in params:
        # Look for self.param_name usage
        if f'self.{param_name}' in gen_code:
            used_params.append(param_name)
        else:
            unused_params.append(param_name)
    
    # Find hardcoded numbers in generate_signals
    hardcoded = []
    
    # Common patterns for hardcoded values
    patterns = [
        r'ema_(\d+)',           # ema_200, ema_50, etc
        r'sma_(\d+)',           # sma_200
        r'> (\d+\.?\d*)',       # comparisons: > 30
        r'< (\d+\.?\d*)',       # comparisons: < 70
        r'== (\d+\.?\d*)',      # equality: == 50
        r'atr_multiplier.*?(\d+\.?\d*)',  # atr multiplier
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, gen_code)
        hardcoded.extend(matches)
    
    return [p[0] for p in params], unused_params, hardcoded


def main():
    strategies_dir = Path('src/strategies/generated')
    
    print("=" * 80)
    print("EMERGENCY ANALYSIS - HARDCODED VALUES IN STRATEGIES")
    print("=" * 80)
    print()
    
    problem_strategies = []
    
    for file_path in sorted(strategies_dir.glob('*.py')):
        if file_path.stem in ['__init__', 'auto_register']:
            continue
        
        all_params, unused_params, hardcoded = analyze_strategy(file_path)
        
        if not all_params:
            continue
        
        has_problem = len(unused_params) > 0 or len(hardcoded) > 3
        
        if has_problem:
            problem_strategies.append({
                'name': file_path.stem,
                'all_params': all_params,
                'unused': unused_params,
                'hardcoded': hardcoded
            })
    
    print(f"Found {len(problem_strategies)} strategies with potential issues:\n")
    
    for strategy in problem_strategies:
        print(f"? {strategy['name']}")
        print(f"   Total params: {len(strategy['all_params'])}")
        print(f"   Unused params: {strategy['unused']}")
        print(f"   Hardcoded values: {set(strategy['hardcoded'])}")
        print()
    
    print("=" * 80)
    print(f"SUMMARY: {len(problem_strategies)} strategies need manual review")
    print("=" * 80)
    
    # Save to file for reference
    with open('HARDCODED_ISSUES.txt', 'w') as f:
        f.write("STRATEGIES WITH HARDCODED VALUES\n")
        f.write("=" * 80 + "\n\n")
        
        for strategy in problem_strategies:
            f.write(f"{strategy['name']}\n")
            f.write(f"  Unused params: {', '.join(strategy['unused'])}\n")
            f.write(f"  Hardcoded: {', '.join(set(strategy['hardcoded']))}\n")
            f.write("\n")
    
    print("\n?? Detailed report saved to: HARDCODED_ISSUES.txt")


if __name__ == "__main__":
    main()
