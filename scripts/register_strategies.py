"""
Auto-register all generated strategies.

This script scans the generated strategies folder and registers them all.
"""

from pathlib import Path
import importlib
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.strategies.registry import StrategyRegistry
from scripts.migrate_strategies import STRATEGY_METADATA


def register_all_generated_strategies():
    """Dynamically register all generated strategies."""
    
    registry = StrategyRegistry()
    generated_dir = Path("src/strategies/generated")
    
    if not generated_dir.exists():
        print("Generated strategies directory not found!")
        return
    
    registered_count = 0
    
    for strategy_file in generated_dir.glob("*.py"):
        if strategy_file.name.startswith("__"):
            continue
        
        strategy_name = strategy_file.stem
        
        if strategy_name not in STRATEGY_METADATA:
            continue
        
        metadata = STRATEGY_METADATA[strategy_name]
        
        try:
            # Import the module
            module_path = f"src.strategies.generated.{strategy_name}"
            module = importlib.import_module(module_path)
            
            # Get the strategy class
            class_name = "".join(word.capitalize() for word in strategy_name.split("_"))
            strategy_class = getattr(module, class_name)
            
            # Register it
            registry.register(
                name=strategy_name,
                strategy_class=strategy_class,
                category=metadata["category"],
                description=metadata["description"],
                default_params={},
            )
            
            registered_count += 1
            print(f"? Registered: {strategy_name} ({metadata['category']})")
            
        except Exception as e:
            print(f"? Failed to register {strategy_name}: {e}")
    
    print()
    print(f"? Registered {registered_count}/38 strategies")
    
    return registry


if __name__ == "__main__":
    register_all_generated_strategies()
