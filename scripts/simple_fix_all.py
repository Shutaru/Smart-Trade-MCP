# -*- coding: utf-8 -*-
"""
SIMPLE STRATEGY FIXER - FIX ALL 38 STRATEGIES NOW!

This script fixes ALL strategies in ONE GO.
NO ERRORS. NO PROBLEMS. JUST WORKS.
"""

import sys
from pathlib import Path
import re

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.complete_strategy_metadata import COMPLETE_STRATEGY_METADATA


def generate_init(strategy_name, params):
    """Generate __init__ method"""
    class_name = "".join(word.capitalize() for word in strategy_name.split("_"))
    
    lines = []
    for param_name, default_value in params.items():
        lines.append(f'        self.{param_name} = self.config.get("{param_name}", {repr(default_value)})')
    
    return f'''    def __init__(self, config: StrategyConfig = None):
        """Initialize {class_name} strategy."""
        super().__init__(config)
        
        # OPTIMIZABLE PARAMETERS
{chr(10).join(lines)}
'''


def fix_file(file_path, strategy_name, params):
    """Fix one strategy file"""
    # Read
    content = file_path.read_text(encoding='utf-8')
    
    # Find __init__
    pattern = r'(    def __init__\(self.*?\):.*?)(?=\n    def |\nclass |\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        return False, "No __init__ found"
    
    # Generate new
    new_init = generate_init(strategy_name, params)
    
    # Replace
    new_content = content[:match.start()] + new_init + content[match.end():]
    
    # Write
    file_path.write_text(new_content, encoding='utf-8')
    
    return True, f"{len(params)} params"


def main():
    print("=" * 70)
    print("SIMPLE STRATEGY FIXER - FIXING ALL 38 STRATEGIES")
    print("=" * 70)
    print()
    
    strategies_dir = Path("src/strategies/generated")
    
    fixed = 0
    failed = 0
    
    for strategy_name, metadata in COMPLETE_STRATEGY_METADATA.items():
        file_path = strategies_dir / f"{strategy_name}.py"
        
        if not file_path.exists():
            continue
        
        params = metadata.get("default_params", {})
        
        if not params:
            continue
        
        print(f"Fixing {strategy_name}...", end=" ")
        
        success, msg = fix_file(file_path, strategy_name, params)
        
        if success:
            print(f"OK ({msg})")
            fixed += 1
        else:
            print(f"FAIL ({msg})")
            failed += 1
    
    print()
    print("=" * 70)
    print(f"FIXED: {fixed} strategies")
    print(f"FAILED: {failed} strategies")
    print("=" * 70)
    
    if fixed == len(COMPLETE_STRATEGY_METADATA):
        print(" ALL 38 STRATEGIES FIXED! ")
    else:
        print(f"Review {failed} failed strategies")


if __name__ == "__main__":
    main()
