"""
GPU vs CPU Simple Benchmark

Tests GPU acceleration for indicators without full dependencies.
"""

import numpy as np
import pandas as pd
import time
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 80)
print("GPU vs CPU BENCHMARK - INDICATORS")
print("=" * 80)
print()

# Check GPU availability
try:
    from src.core.gpu_utils import get_gpu_info, GPU_AVAILABLE
    
    gpu_info = get_gpu_info()
    if gpu_info['available']:
        print(f"? GPU Detected: {gpu_info['device_name']}")
        print(f"   Memory: {gpu_info['memory_free_gb']:.1f}GB free / {gpu_info['memory_total_gb']:.1f}GB total")
        print(f"   Compute: {gpu_info['compute_capability']}")
    else:
        print("? GPU Not Available")
        print("   Install CuPy: pip install cupy-cuda12x")
except Exception as e:
    print(f"? GPU Not Available: {e}")
    GPU_AVAILABLE = False

print()

# Create test data
print("?? Creating test data...")
n_candles = 5000  # 5000 candles for testing

np.random.seed(42)
df = pd.DataFrame({
    'timestamp': pd.date_range('2024-01-01', periods=n_candles, freq='1H'),
    'open': 50000 + np.random.randn(n_candles) * 1000,
    'high': 50000 + np.random.randn(n_candles) * 1000 + 500,
    'low': 50000 + np.random.randn(n_candles) * 1000 - 500,
    'close': 50000 + np.random.randn(n_candles) * 1000,
    'volume': np.random.rand(n_candles) * 1000000,
})

print(f"? Created {n_candles} candles")
print()

# Test indicators
indicators_to_test = ["rsi", "macd", "ema", "bollinger", "atr", "adx", "cci"]

try:
    from src.core.indicators import calculate_all_indicators, enable_gpu, disable_gpu
    
    print("=" * 80)
    print("BENCHMARK: INDICATORS")
    print("=" * 80)
    print()
    
    # CPU Benchmark
    print("?? CPU Mode...")
    disable_gpu()
    
    start = time.time()
    df_cpu = calculate_all_indicators(df.copy(), indicators_to_test, use_gpu=False)
    cpu_time = time.time() - start
    
    print(f"   Time: {cpu_time:.3f}s")
    print(f"   Indicators: {indicators_to_test}")
    print()
    
    # GPU Benchmark
    if GPU_AVAILABLE:
        print("?? GPU Mode...")
        enable_gpu()
        
        start = time.time()
        df_gpu = calculate_all_indicators(df.copy(), indicators_to_test, use_gpu=True)
        gpu_time = time.time() - start
        
        print(f"   Time: {gpu_time:.3f}s")
        print(f"   Speedup: {cpu_time / gpu_time:.1f}x ??")
        print()
        
        # Verify results match
        print("?? Verifying results match...")
        for col in df_cpu.columns:
            if col in df_gpu.columns and col not in ['timestamp', 'open', 'high', 'low', 'close', 'volume']:
                cpu_vals = df_cpu[col].values
                gpu_vals = df_gpu[col].values
                
                # Check if close (allowing for floating point errors)
                diff = np.abs(cpu_vals - gpu_vals)
                max_diff = np.nanmax(diff[~np.isnan(diff)])
                
                if max_diff < 0.01:  # Allow 0.01 difference
                    print(f"   ? {col}: Match (max diff: {max_diff:.6f})")
                else:
                    print(f"   ??  {col}: Difference detected (max diff: {max_diff:.6f})")
        
        print()
        
        # Summary
        print("=" * 80)
        print("BENCHMARK SUMMARY")
        print("=" * 80)
        print()
        print(f"Dataset: {n_candles} candles")
        print(f"Indicators: {len(indicators_to_test)}")
        print()
        print(f"CPU Time:    {cpu_time:.3f}s")
        print(f"GPU Time:    {gpu_time:.3f}s")
        print(f"Speedup:     {cpu_time / gpu_time:.1f}x ??")
        print()
        
        if cpu_time / gpu_time > 5:
            print("?? EXCELLENT SPEEDUP! GPU is significantly faster!")
        elif cpu_time / gpu_time > 2:
            print("? GOOD SPEEDUP! GPU acceleration is working!")
        else:
            print("??  Speedup is modest. GPU may have overhead for small datasets.")
        
    else:
        print("??  GPU not available - skipping GPU benchmark")
        print()
        print("To enable GPU acceleration:")
        print("  1. Install CUDA toolkit")
        print("  2. pip install cupy-cuda12x  # For CUDA 12.x")
        print("  3. pip install cupy-cuda11x  # For CUDA 11.x")
    
except Exception as e:
    print(f"? Benchmark failed: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("BENCHMARK COMPLETE")
print("=" * 80)
