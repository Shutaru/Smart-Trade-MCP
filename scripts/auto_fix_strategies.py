# -*- coding: utf-8 -*-
"""
AUTOMATED STRATEGY FIXER

Automatically fixes all 41 strategies to connect optimizable parameters.
Safe approach: Generates new __init__ methods and shows diffs for review.

Usage:
    python scripts/auto_fix_strategies.py --preview  # Show changes only
    python scripts/auto_fix_strategies.py --apply    # Apply changes
    python scripts/auto_fix_strategies.py --strategy bollinger_mean_reversion  # Fix single strategy
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.generate_strategies import STRATEGY_METADATA


class StrategyFixer:
    """Fixes strategy parameter connections"""
    
    def __init__(self):
        self.fixed_count = 0
        self.failed_count = 0
        self.changes = []
    
    def generate_init_method(self, strategy_name: str, metadata: Dict) -> str:
        """
        Generate correct __init__ method.
        
        Args:
            strategy_name: Strategy identifier
            metadata: Strategy metadata
            
        Returns:
            Python code for __init__ method
        """
        class_name = "".join(word.capitalize() for word in strategy_name.split("_"))
        
        default_params = metadata.get("default_params", {})
        
        if not default_params:
            return None  # No parameters to connect
        
        # Generate parameter initialization lines
        param_lines = []
        for param_name, default_value in default_params.items():
            param_lines.append(
                f'        self.{param_name} = self.config.get("{param_name}", {repr(default_value)})'
            )
        
        init_code = f'''    def __init__(self, config: StrategyConfig = None):
        """Initialize {class_name} strategy."""
        super().__init__(config)
        
        # ? OPTIMIZABLE PARAMETERS (auto-generated)
{chr(10).join(param_lines)}
'''
        
        return init_code
    
    def extract_current_init(self, content: str) -> Tuple[str, int, int]:
        """
        Extract current __init__ method from file.
        
        Returns:
            (init_code, start_pos, end_pos)
        """
        # Pattern to match __init__ method
        pattern = r'(    def __init__\(self.*?\):.*?)(?=\n    def |\nclass |\Z)'
        
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(1), match.start(), match.end()
        
        return None, None, None
    
    def show_diff(self, old_code: str, new_code: str, strategy_name: str):
        """Show colorized diff"""
        print(f"\n{'='*70}")
        print(f"STRATEGY: {strategy_name}")
        print(f"{'='*70}")
        
        print("\n?? OLD (CURRENT):")
        print("-" * 70)
        for line in old_code.split('\n'):
            print(f"  - {line}")
        
        print("\n?? NEW (PROPOSED):")
        print("-" * 70)
        for line in new_code.split('\n'):
            print(f"  + {line}")
        
        print("\n" + "="*70)
    
    def fix_strategy_file(
        self,
        file_path: Path,
        strategy_name: str,
        metadata: Dict,
        preview_only: bool = True
    ) -> bool:
        """
        Fix a single strategy file.
        
        Args:
            file_path: Path to strategy file
            strategy_name: Strategy identifier
            metadata: Strategy metadata
            preview_only: If True, only show diff without applying
            
        Returns:
            True if fixed successfully
        """
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate new __init__
            new_init = self.generate_init_method(strategy_name, metadata)
            
            if not new_init:
                print(f"??  {strategy_name}: No parameters to connect")
                return False
            
            # Extract current __init__
            old_init, start_pos, end_pos = self.extract_current_init(content)
            
            if not old_init:
                print(f"? {strategy_name}: Could not find __init__ method")
                self.failed_count += 1
                return False
            
            # Show diff
            self.show_diff(old_init, new_init, strategy_name)
            
            # Store change info
            self.changes.append({
                "strategy": strategy_name,
                "file": str(file_path),
                "old": old_init,
                "new": new_init,
            })
            
            # Apply if not preview
            if not preview_only:
                new_content = content[:start_pos] + new_init + content[end_pos:]
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"? {strategy_name}: APPLIED")
                self.fixed_count += 1
            else:
                print(f"???  {strategy_name}: PREVIEW ONLY (use --apply to save)")
            
            return True
            
        except Exception as e:
            print(f"? {strategy_name}: ERROR - {e}")
            self.failed_count += 1
            return False
    
    def fix_all_strategies(self, preview_only: bool = True, specific_strategy: str = None):
        """
        Fix all strategies or a specific one.
        
        Args:
            preview_only: If True, only show diffs
            specific_strategy: If provided, fix only this strategy
        """
        strategies_dir = Path("src/strategies/generated")
        
        if not strategies_dir.exists():
            print("? Generated strategies directory not found!")
            return
        
        print("=" * 70)
        if preview_only:
            print("PREVIEW MODE - No changes will be applied")
        else:
            print("APPLY MODE - Changes WILL be saved!")
        print("=" * 70)
        
        # Filter strategies
        if specific_strategy:
            strategies_to_fix = {specific_strategy: STRATEGY_METADATA.get(specific_strategy)}
            if strategies_to_fix[specific_strategy] is None:
                print(f"? Strategy not found: {specific_strategy}")
                return
        else:
            strategies_to_fix = STRATEGY_METADATA
        
        total = len(strategies_to_fix)
        print(f"\n?? Processing {total} strategies...\n")
        
        for strategy_name, metadata in strategies_to_fix.items():
            file_path = strategies_dir / f"{strategy_name}.py"
            
            if not file_path.exists():
                print(f"??  File not found: {strategy_name}.py")
                continue
            
            self.fix_strategy_file(file_path, strategy_name, metadata, preview_only)
        
        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Total strategies: {total}")
        print(f"Changes proposed: {len(self.changes)}")
        print(f"Applied: {self.fixed_count}")
        print(f"Failed: {self.failed_count}")
        
        if preview_only and self.changes:
            print("\n?? To apply changes, run:")
            print("   python scripts/auto_fix_strategies.py --apply")
        
        print("=" * 70)


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description="Automatically fix strategy parameter connections")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (default is preview only)"
    )
    parser.add_argument(
        "--strategy",
        type=str,
        help="Fix only specific strategy (e.g., 'bollinger_mean_reversion')"
    )
    
    args = parser.parse_args()
    
    fixer = StrategyFixer()
    fixer.fix_all_strategies(
        preview_only=not args.apply,
        specific_strategy=args.strategy
    )


if __name__ == "__main__":
    main()
