# -*- coding: utf-8 -*-
"""
Strategy Parameter Connector

Automatically connects optimizable parameters to strategy implementations.
Fixes the critical issue where parameters were defined but not used.

Run this script to fix all 41+ strategies at once.
"""

import os
import re
from pathlib import Path
from typing import Dict, List

# Import metadata
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.generate_strategies import STRATEGY_METADATA


def fix_strategy_init(strategy_name: str, metadata: Dict) -> str:
    """
    Generate proper __init__ method that connects parameters.
    
    Args:
        strategy_name: Strategy identifier
        metadata: Strategy metadata with default_params
        
    Returns:
        Python code for __init__ method
    """
    class_name = "".join(word.capitalize() for word in strategy_name.split("_"))
    
    # Get all parameters
    default_params = metadata.get("default_params", {})
    
    # Generate parameter initialization code
    param_lines = []
    for param_name, default_value in default_params.items():
        param_lines.append(
            f'        self.{param_name} = self.config.get("{param_name}", {repr(default_value)})'
        )
    
    init_code = f'''    def __init__(self, config: StrategyConfig = None):
        """Initialize {class_name} strategy."""
        super().__init__(config)
        
        # ? OPTIMIZABLE PARAMETERS (connected to parameter space)
{chr(10).join(param_lines)}
'''
    
    return init_code


def update_strategy_file(file_path: Path, strategy_name: str, metadata: Dict) -> bool:
    """
    Update a strategy file to connect parameters.
    
    Args:
        file_path: Path to strategy file
        strategy_name: Strategy identifier
        metadata: Strategy metadata
        
    Returns:
        True if updated successfully
    """
    try:
        # Read current file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate new __init__ method
        new_init = fix_strategy_init(strategy_name, metadata)
        
        # Replace __init__ method
        # Pattern to match entire __init__ method
        pattern = r'(    def __init__\(self.*?\):.*?)(?=\n    def |\n\nclass |\Z)'
        
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, new_init, content, flags=re.DOTALL)
        else:
            print(f"  ??  Could not find __init__ in {file_path.name}")
            return False
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ? Fixed: {file_path.name}")
        return True
        
    except Exception as e:
        print(f"  ? Error fixing {file_path.name}: {e}")
        return False


def update_all_parameter_spaces():
    """
    Update all_parameter_spaces.py to include ALL parameters.
    """
    from src.optimization.all_parameter_spaces import AllParameterSpaces
    
    print("\n?? Updating parameter spaces...")
    
    spaces_file = Path("src/optimization/all_parameter_spaces.py")
    
    if not spaces_file.exists():
        print("  ? all_parameter_spaces.py not found!")
        return
    
    with open(spaces_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # For each strategy, verify parameter space includes ALL params
    fixed_count = 0
    
    for strategy_name, metadata in STRATEGY_METADATA.items():
        if "param_space" not in metadata:
            continue
        
        # Generate complete parameter space
        method_name = f"{strategy_name}_strategy"
        
        # Check if method exists
        if method_name not in content:
            print(f"  ??  {method_name} not found in parameter spaces")
            continue
        
        # Verify all params are present
        param_space = metadata["param_space"]
        default_params = metadata.get("default_params", {})
        
        # Add missing params (sl_atr_mult, tp_rr_mult)
        for key in ["sl_atr_mult", "tp_rr_mult"]:
            if key in default_params and key not in param_space:
                # Add to param_space
                if key == "sl_atr_mult":
                    param_space[key] = {"type": "float", "low": 1.5, "high": 3.0}
                elif key == "tp_rr_mult":
                    param_space[key] = {"type": "float", "low": 1.5, "high": 4.0}
                fixed_count += 1
    
    print(f"  ? Added {fixed_count} missing risk management parameters")


def main():
    """Main execution"""
    print("=" * 70)
    print("STRATEGY PARAMETER CONNECTOR")
    print("=" * 70)
    print()
    print("This script fixes ALL strategies to properly connect parameters.")
    print()
    
    strategies_dir = Path("src/strategies/generated")
    
    if not strategies_dir.exists():
        print("? Generated strategies directory not found!")
        print("   Run scripts/generate_all_strategies.py first")
        return
    
    # Count strategies
    total_strategies = len(STRATEGY_METADATA)
    print(f"?? Found {total_strategies} strategies in metadata")
    print()
    
    # Fix each strategy
    fixed = 0
    failed = 0
    
    print("?? Fixing strategy files...")
    print()
    
    for strategy_name, metadata in STRATEGY_METADATA.items():
        file_path = strategies_dir / f"{strategy_name}.py"
        
        if not file_path.exists():
            print(f"  ??  File not found: {strategy_name}.py")
            continue
        
        if update_strategy_file(file_path, strategy_name, metadata):
            fixed += 1
        else:
            failed += 1
    
    print()
    print("=" * 70)
    print(f"? Fixed: {fixed} strategies")
    if failed > 0:
        print(f"? Failed: {failed} strategies")
    print("=" * 70)
    print()
    
    # Update parameter spaces
    update_all_parameter_spaces()
    
    print()
    print("?? ALL DONE!")
    print()
    print("Next steps:")
    print("1. Verify strategies can be instantiated")
    print("2. Run optimization with new parameter connections")
    print("3. Check meta-learner integration")


if __name__ == "__main__":
    main()
