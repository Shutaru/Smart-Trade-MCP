"""
Auto-generate all 38 strategies from metadata.

This script creates placeholder strategy files that can then be
filled in with actual logic from the old repo.
"""

import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.migrate_strategies import STRATEGY_METADATA, generate_strategy_template


def create_strategy_files():
    """Create all strategy files."""
    
    strategies_dir = Path("src/strategies/generated")
    strategies_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating {len(STRATEGY_METADATA)} strategy files...")
    print()
    
    created = []
    
    for name, metadata in STRATEGY_METADATA.items():
        # Generate file content
        content = generate_strategy_template(name, metadata)
        
        # Write to file
        file_path = strategies_dir / f"{name}.py"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        created.append(name)
        print(f"? Created: {name}.py")
    
    # Create __init__.py for the generated module
    init_content = '"""Auto-generated strategies."""\n\n'
    init_content += "# This module contains auto-generated strategy templates\n"
    init_content += "# Fill in the generate_signals() method for each strategy\n\n"
    
    init_path = strategies_dir / "__init__.py"
    with open(init_path, "w", encoding="utf-8") as f:
        f.write(init_content)
    
    print()
    print(f"? Created {len(created)} strategy files in {strategies_dir}")
    print()
    print("Next steps:")
    print("1. Review generated files in src/strategies/generated/")
    print("2. Implement generate_signals() for each strategy")
    print("3. Register strategies in the main registry")
    
    return created


if __name__ == "__main__":
    create_strategy_files()
