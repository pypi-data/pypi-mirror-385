"""
Backend selection logic for Hurst exponent estimation.

This module provides functionality to automatically select the best available
backend based on hardware capabilities, data size, and performance requirements.
"""

import os
import platform
from enum import Enum
from typing import List, Optional, Dict, Any
import numpy as np


class BackendType(Enum):
    """Available backend types."""
    NUMPY = "numpy"
    NUMBA_CPU = "numba_cpu"
    NUMBA_GPU = "numba_gpu"
    JAX_CPU = "jax_cpu"
    JAX_GPU = "jax_gpu"


def check_jax_availability() -> Dict[str, bool]:
    """Check JAX availability and GPU support."""
    jax_info = {
        'available': False,
        'gpu_available': False,
        'tpu_available': False
    }
    
    try:
        import jax
        jax_info['available'] = True
        
        # Check for GPU
        try:
            jax.devices('gpu')
            jax_info['gpu_available'] = True
        except:
            pass
        
        # Check for TPU
        try:
            jax.devices('tpu')
            jax_info['tpu_available'] = True
        except:
            pass
            
    except ImportError:
        pass
    
    return jax_info


def check_numba_availability() -> Dict[str, bool]:
    """Check Numba availability and GPU support."""
    numba_info = {
        'available': False,
        'cuda_available': False
    }
    
    try:
        import numba
        numba_info['available'] = True
        
        # Check for CUDA
        try:
            from numba import cuda
            numba_info['cuda_available'] = cuda.is_available()
        except:
            pass
            
    except ImportError:
        pass
    
    return numba_info


def get_system_info() -> Dict[str, Any]:
    """Get system information for backend selection."""
    info = {
        'platform': platform.system(),
        'architecture': platform.machine(),
        'cpu_count': os.cpu_count(),
        'memory_gb': None
    }
    
    # Try to get memory information
    try:
        import psutil
        info['memory_gb'] = psutil.virtual_memory().total / (1024**3)
    except ImportError:
        pass
    
    return info


def get_available_backends() -> List[BackendType]:
    """Get list of available backends."""
    available = [BackendType.NUMPY]  # NumPy is always available
    
    # Check Numba
    numba_info = check_numba_availability()
    if numba_info['available']:
        available.append(BackendType.NUMBA_CPU)
        if numba_info['cuda_available']:
            available.append(BackendType.NUMBA_GPU)
    
    # Check JAX
    jax_info = check_jax_availability()
    if jax_info['available']:
        available.append(BackendType.JAX_CPU)
        if jax_info['gpu_available']:
            available.append(BackendType.JAX_GPU)
    
    return available


def select_backend(data_size: int, 
                  real_time: bool = False,
                  prefer_gpu: bool = True,
                  prefer_jax: bool = True) -> str:
    """
    Select the best available backend for the given requirements.
    
    Parameters:
    -----------
    data_size : int
        Size of the data to process
    real_time : bool
        Whether real-time processing is required
    prefer_gpu : bool
        Whether to prefer GPU backends
    prefer_jax : bool
        Whether to prefer JAX backends
        
    Returns:
    --------
    str
        Selected backend name
    """
    available = get_available_backends()
    
    # For very small data or real-time requirements, prefer CPU
    if data_size < 1000 or real_time:
        if BackendType.NUMBA_CPU in available:
            return "numba_cpu"
        else:
            return "numpy"
    
    # For large data, prefer GPU if available
    if data_size > 10000 and prefer_gpu:
        if prefer_jax and BackendType.JAX_GPU in available:
            return "jax_gpu"
        elif BackendType.NUMBA_GPU in available:
            return "numba_gpu"
    
    # For medium data or when GPU is not preferred
    if prefer_jax and BackendType.JAX_CPU in available:
        return "jax_cpu"
    elif BackendType.NUMBA_CPU in available:
        return "numba_cpu"
    else:
        return "numpy"


def get_backend_info() -> Dict[str, Any]:
    """Get information about available backends."""
    info = {
        'system': get_system_info(),
        'available_backends': [b.value for b in get_available_backends()],
        'jax': check_jax_availability(),
        'numba': check_numba_availability()
    }
    
    return info


def recommend_backend(data_size: int, 
                     use_case: str = "general",
                     **kwargs) -> Dict[str, Any]:
    """
    Recommend backend with detailed reasoning.
    
    Parameters:
    -----------
    data_size : int
        Size of the data to process
    use_case : str
        Use case description ("general", "real_time", "batch", "research")
    **kwargs
        Additional parameters
        
    Returns:
    --------
    Dict[str, Any]
        Recommendation with reasoning
    """
    available = get_available_backends()
    system_info = get_system_info()
    
    recommendation = {
        'recommended_backend': None,
        'reasoning': [],
        'alternatives': [],
        'performance_estimate': {}
    }
    
    # Determine requirements based on use case
    real_time = use_case == "real_time"
    prefer_gpu = use_case in ["batch", "research"] and data_size > 5000
    prefer_jax = use_case == "research" or kwargs.get('prefer_jax', True)
    
    # Select backend
    selected = select_backend(data_size, real_time, prefer_gpu, prefer_jax)
    recommendation['recommended_backend'] = selected
    
    # Add reasoning
    if real_time:
        recommendation['reasoning'].append("Real-time processing requires low latency")
    
    if data_size < 1000:
        recommendation['reasoning'].append("Small data size favors CPU backends")
    elif data_size > 10000:
        recommendation['reasoning'].append("Large data size benefits from GPU acceleration")
    
    if prefer_gpu and "gpu" in selected:
        recommendation['reasoning'].append("GPU acceleration available and beneficial")
    elif prefer_gpu and "gpu" not in selected:
        recommendation['reasoning'].append("GPU preferred but not available")
    
    if prefer_jax and "jax" in selected:
        recommendation['reasoning'].append("JAX backend selected for advanced features")
    
    # Add alternatives
    for backend in available:
        if backend.value != selected:
            recommendation['alternatives'].append(backend.value)
    
    # Performance estimates (rough)
    if selected == "numpy":
        recommendation['performance_estimate'] = {
            'speed': "baseline",
            'memory': "low",
            'scalability': "limited"
        }
    elif selected == "numba_cpu":
        recommendation['performance_estimate'] = {
            'speed': "2-5x faster",
            'memory': "low",
            'scalability': "good"
        }
    elif selected == "numba_gpu":
        recommendation['performance_estimate'] = {
            'speed': "10-50x faster",
            'memory': "medium",
            'scalability': "excellent"
        }
    elif selected == "jax_cpu":
        recommendation['performance_estimate'] = {
            'speed': "3-10x faster",
            'memory': "medium",
            'scalability': "excellent"
        }
    elif selected == "jax_gpu":
        recommendation['performance_estimate'] = {
            'speed': "20-100x faster",
            'memory': "high",
            'scalability': "excellent"
        }
    
    return recommendation

