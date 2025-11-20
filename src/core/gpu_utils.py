"""
GPU Utilities and Detection

Provides GPU acceleration utilities with automatic CPU fallback.
Supports CUDA via CuPy and Numba.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Try to import CuPy (CUDA arrays)
try:
    import cupy as cp
    import cupyx
    HAS_CUPY = True
    
    # Check if GPU is actually available
    try:
        GPU_AVAILABLE = cp.cuda.runtime.getDeviceCount() > 0
    except cp.cuda.runtime.CUDARuntimeError:
        GPU_AVAILABLE = False
        logger.warning("CuPy installed but no GPU detected")
except ImportError:
    HAS_CUPY = False
    GPU_AVAILABLE = False
    cp = None
    logger.info("CuPy not installed - GPU acceleration disabled")

# Try to import Numba (GPU kernels)
try:
    from numba import cuda, jit
    HAS_NUMBA = True
    
    # Check CUDA availability
    try:
        NUMBA_CUDA_AVAILABLE = cuda.is_available()
    except Exception:
        NUMBA_CUDA_AVAILABLE = False
except ImportError:
    HAS_NUMBA = False
    NUMBA_CUDA_AVAILABLE = False
    cuda = None
    jit = None
    logger.info("Numba not installed - CUDA kernels disabled")


def get_gpu_info() -> Dict[str, Any]:
    """
    Get GPU information and capabilities.
    
    Returns:
        Dictionary with GPU info:
        {
            "available": bool,
            "n_gpus": int,
            "current_device": int,
            "device_name": str,
            "memory_total_gb": float,
            "memory_free_gb": float,
            "compute_capability": tuple,
        }
    """
    if not GPU_AVAILABLE or not HAS_CUPY:
        return {
            "available": False,
            "message": "GPU not available - using CPU fallback"
        }
    
    try:
        device_id = cp.cuda.runtime.getDevice()
        props = cp.cuda.runtime.getDeviceProperties(device_id)
        mem_total, mem_free = cp.cuda.runtime.memGetInfo()
        
        return {
            "available": True,
            "n_gpus": cp.cuda.runtime.getDeviceCount(),
            "current_device": device_id,
            "device_name": props['name'].decode('utf-8'),
            "memory_total_gb": mem_total / 1e9,
            "memory_free_gb": mem_free / 1e9,
            "compute_capability": (props['major'], props['minor']),
            "has_cupy": HAS_CUPY,
            "has_numba": HAS_NUMBA,
            "numba_cuda": NUMBA_CUDA_AVAILABLE,
        }
    except Exception as e:
        logger.error(f"Error getting GPU info: {e}")
        return {
            "available": False,
            "error": str(e)
        }


def select_device(device_id: Optional[int] = None) -> bool:
    """
    Select GPU device to use.
    
    Args:
        device_id: GPU device ID (0, 1, 2, ...) or None for default
        
    Returns:
        True if device selected successfully
    """
    if not GPU_AVAILABLE or not HAS_CUPY:
        logger.warning("Cannot select GPU device - GPU not available")
        return False
    
    try:
        if device_id is None:
            device_id = 0
        
        cp.cuda.Device(device_id).use()
        logger.info(f"Selected GPU device {device_id}")
        return True
    except Exception as e:
        logger.error(f"Error selecting GPU device {device_id}: {e}")
        return False


def get_optimal_block_size(n: int, max_threads: int = 256) -> tuple:
    """
    Calculate optimal CUDA block size for n elements.
    
    Args:
        n: Number of elements to process
        max_threads: Maximum threads per block (default 256)
        
    Returns:
        Tuple of (threads_per_block, blocks_per_grid)
    """
    threads_per_block = min(max_threads, n)
    blocks_per_grid = (n + threads_per_block - 1) // threads_per_block
    return threads_per_block, blocks_per_grid


def to_gpu(arr, dtype=None):
    """
    Transfer array to GPU memory.
    
    Args:
        arr: NumPy array or list
        dtype: Optional dtype for GPU array
        
    Returns:
        CuPy array on GPU or original array if GPU not available
    """
    if not GPU_AVAILABLE or not HAS_CUPY:
        import numpy as np
        return np.array(arr, dtype=dtype)
    
    return cp.array(arr, dtype=dtype)


def to_cpu(arr):
    """
    Transfer array from GPU to CPU memory.
    
    Args:
        arr: CuPy array or NumPy array
        
    Returns:
        NumPy array on CPU
    """
    if HAS_CUPY and isinstance(arr, cp.ndarray):
        return arr.get()
    return arr


def synchronize():
    """Synchronize GPU operations (wait for completion)."""
    if GPU_AVAILABLE and HAS_CUPY:
        cp.cuda.Stream.null.synchronize()


def clear_memory():
    """Clear GPU memory cache."""
    if GPU_AVAILABLE and HAS_CUPY:
        cp.get_default_memory_pool().free_all_blocks()
        logger.debug("GPU memory cache cleared")


# Print GPU info on import
if GPU_AVAILABLE:
    info = get_gpu_info()
    logger.info(
        f"GPU Available: {info['device_name']} "
        f"({info['memory_free_gb']:.1f}GB free / {info['memory_total_gb']:.1f}GB total)"
    )
else:
    logger.info("GPU not available - using CPU for all operations")


__all__ = [
    'HAS_CUPY',
    'HAS_NUMBA',
    'GPU_AVAILABLE',
    'NUMBA_CUDA_AVAILABLE',
    'cp',
    'cuda',
    'jit',
    'get_gpu_info',
    'select_device',
    'get_optimal_block_size',
    'to_gpu',
    'to_cpu',
    'synchronize',
    'clear_memory',
]
