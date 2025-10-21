"""
Benchmark core module for Hurst exponent estimation benchmarking.

This module provides the core functionality for generating synthetic data,
running benchmarks, and collecting results for Hurst exponent estimation methods.

Developed as part of PhD research in Biomedical Engineering at the University of Reading, UK.
Author: Davian R. Chin (PhD Candidate in Biomedical Engineering)
Research Focus: Physics-Informed Fractional Operator Learning for Real-Time Neurological Biomarker Detection.
"""

from .generation import generate_grid, fbm_davies_harte
from .runner import BenchmarkConfig, run_benchmark_on_dataset

__all__ = [
    "generate_grid",
    "fbm_davies_harte", 
    "BenchmarkConfig",
    "run_benchmark_on_dataset",
]

