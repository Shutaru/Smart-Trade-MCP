
import sys
import os
import inspect
import importlib
from pathlib import Path

# Add src to python path
sys.path.append(str(Path(__file__).parent.parent))

from src.strategies.base import BaseStrategy
from src.core.logger import logger
logger.disabled = True


def verify_strategies():
    strategies_dir = Path("src/strategies/generated")
    sys.path.append(str(Path.cwd()))
    
    print(f"Scanning {strategies_dir}...")
    
    strategy_files = [f for f in os.listdir(strategies_dir) if f.endswith(".py") and not f.startswith("__")]
    
    success_count = 0
    error_count = 0
    
    with open("errors.txt", "w") as f:
        for strategy_file in strategy_files:
            if strategy_file == "auto_register.py":
                continue
            module_name = f"src.strategies.generated.{strategy_file[:-3]}"
            try:
                module = importlib.import_module(module_name)
                
                # Find strategy classes in the module
                strategies = []
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, BaseStrategy) and obj is not BaseStrategy:
                        strategies.append(obj)
                
                if not strategies:
                    f.write(f"WARNING: No strategy class found in {strategy_file}\n")
                    error_count += 1
                    continue
                    
                for StrategyClass in strategies:
                    try:
                        # Try to instantiate
                        strategy = StrategyClass()
                        
                        # Check required methods
                        if not hasattr(strategy, "generate_signals"):
                            f.write(f"ERROR: {StrategyClass.__name__} missing generate_signals\n")
                            error_count += 1
                        elif not hasattr(strategy, "get_required_indicators"):
                            f.write(f"ERROR: {StrategyClass.__name__} missing get_required_indicators\n")
                            error_count += 1
                        else:
                            success_count += 1
                            
                    except Exception as e:
                        f.write(f"ERROR: Failed to instantiate {StrategyClass.__name__}: {e}\n")
                        error_count += 1
                        
            except Exception as e:
                f.write(f"ERROR: Failed to import {module_name}: {e}\n")
                error_count += 1

    print(f"\nVerification Complete.")
    print(f"Success: {success_count}")
    print(f"Errors: {error_count}")
    
    if error_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    verify_strategies()
