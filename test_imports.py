"""
Test imports and GPU availability
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("TESTING IMPORTS")
print("=" * 60)
print()

# Test GPU utils
print("1. Testing GPU utils...")
try:
    from src.core.gpu_utils import get_gpu_info, GPU_AVAILABLE
    print("   [OK] gpu_utils imported")
    
    info = get_gpu_info()
    if info.get('available'):
        print(f"   [OK] GPU: {info['device_name']}")
        print(f"        Memory: {info['memory_free_gb']:.1f}GB free")
    else:
        print("   [INFO] No GPU - will use CPU")
except Exception as e:
    print(f"   [ERROR] {e}")

print()

# Test indicators
print("2. Testing indicators...")
try:
    from src.core.indicators import calculate_all_indicators
    print("   [OK] indicators imported")
except Exception as e:
    print(f"   [ERROR] {e}")

print()

# Test backtest engine
print("3. Testing backtest engine...")
try:
    from src.core.backtest_engine import BacktestEngine
    print("   [OK] BacktestEngine imported")
except Exception as e:
    print(f"   [ERROR] {e}")

print()

# Test strategies
print("4. Testing strategies...")
try:
    from src.strategies import registry
    strategies = registry.list_strategies()
    print(f"   [OK] {len(strategies)} strategies loaded")
except Exception as e:
    print(f"   [ERROR] {e}")

print()

# Test data manager
print("5. Testing data manager...")
try:
    from src.core.data_manager import DataManager
    print("   [OK] DataManager imported")
except Exception as e:
    print(f"   [ERROR] {e}")

print()

print("=" * 60)
print("IMPORT TEST COMPLETE")
print("=" * 60)
print()

if all([
    'get_gpu_info' in dir(),
    'calculate_all_indicators' in dir(),
    'BacktestEngine' in dir(),
    'registry' in dir(),
    'DataManager' in dir(),
]):
    print("[OK] All imports successful!")
    print()
    print("System is ready for validation!")
    print()
    print("Next step: Run Walk-Forward Analysis on TOP strategies")
else:
    print("[ERROR] Some imports failed - check errors above")
