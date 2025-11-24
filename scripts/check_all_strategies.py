#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check All Strategies Status

Verifies if all 38 strategies have optimizable parameters connected.
"""

from pathlib import Path
import re


def check_strategy(file_path):
    """Check if strategy has optimizable parameters"""
    content = file_path.read_text(encoding='utf-8')
    
    # Check for optimizable parameters comment
    has_comment = (
        '# OPTIMIZABLE PARAMETERS' in content or
        '# ? OPTIMIZABLE PARAMETERS' in content
    )
    
    # Count self.param = self.config.get( occurrences
    init_match = re.search(r'def __init__.*?(?=\n    def |\Z)', content, re.DOTALL)
    
    if init_match:
        init_code = init_match.group(0)
        param_count = len(re.findall(r'self\.\w+ = self\.config\.get\(', init_code))
    else:
        param_count = 0
    
    return has_comment, param_count


def main():
    strategies_dir = Path('src/strategies/generated')
    
    print("=" * 80)
    print("STRATEGY OPTIMIZATION STATUS CHECK")
    print("=" * 80)
    print()
    
    results = []
    
    for file_path in sorted(strategies_dir.glob('*.py')):
        if file_path.stem in ['__init__', 'auto_register']:
            continue
        
        has_comment, param_count = check_strategy(file_path)
        results.append((file_path.stem, has_comment, param_count))
    
    print(f"Total strategies checked: {len(results)}")
    print()
    print("Status per strategy:")
    print("-" * 80)
    
    perfect_count = 0
    good_count = 0
    bad_count = 0
    
    for name, has_comment, param_count in results:
        if has_comment and param_count >= 4:
            status = "? PERFECT"
            perfect_count += 1
        elif param_count >= 4:
            status = "?? GOOD"
            good_count += 1
        else:
            status = "? BAD"
            bad_count += 1
        
        print(f"{status:<12} {name:<40} ({param_count:2d} params)")
    
    print()
    print("=" * 80)
    print(f"? PERFECT: {perfect_count} strategies (has comment + 4+ params)")
    print(f"?? GOOD:    {good_count} strategies (4+ params, no comment)")
    print(f"? BAD:     {bad_count} strategies (< 4 params)")
    print("=" * 80)
    
    if perfect_count + good_count == len(results):
        print()
        print("?? ALL STRATEGIES ARE OPTIMIZABLE!")
    elif perfect_count + good_count >= len(results) * 0.9:
        print()
        print(f"??  {bad_count} strategies need attention")
    else:
        print()
        print(f"? {bad_count} strategies are NOT optimizable")


if __name__ == "__main__":
    main()
