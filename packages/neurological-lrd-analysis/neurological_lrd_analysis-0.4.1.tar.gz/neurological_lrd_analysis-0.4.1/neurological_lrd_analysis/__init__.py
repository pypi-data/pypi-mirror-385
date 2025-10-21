"""
Neurological Long-Range Dependence Analysis

A comprehensive library for estimating Hurst exponents in neurological time series data,
featuring multiple estimation methods, realistic data generation, and advanced benchmarking capabilities.

This library is developed as part of PhD research in Biomedical Engineering at the University of Reading, UK,
focusing on physics-informed fractional operator learning for real-time neurological biomarker detection.

Author: Davian R. Chin (PhD Candidate in Biomedical Engineering, University of Reading, UK)
Research Focus: Physics-Informed Fractional Operator Learning for Real-Time Neurological Biomarker Detection: 
A Framework for Memory-Driven EEG Analysis
"""

__version__ = "0.4.1"
__author__ = "Davian R. Chin"
__author_title__ = "PhD Candidate in Biomedical Engineering"
__institution__ = "University of Reading, UK"
__email__ = "d.r.chin@pgr.reading.ac.uk"
__orcid__ = "https://orcid.org/0009-0003-9434-3919"
__license__ = "MIT"
__research_context__ = "PhD Research in Biomedical Engineering"

# Core imports
from .biomedical_hurst_factory import (
    BiomedicalHurstEstimatorFactory,
    EstimatorType,
    ConfidenceMethod,
    HurstResult,
    BiomedicalDataProcessor
)

# Benchmarking imports
from .benchmark_core.generation import (
    generate_grid,
    fbm_davies_harte,
    generate_fgn,
    generate_arfima,
    generate_mrw,
    generate_fou,
    add_contamination,
    TimeSeriesSample
)

from .benchmark_core.runner import (
    BenchmarkConfig,
    BenchmarkResult,
    ScoringWeights,
    run_benchmark_on_dataset,
    analyze_benchmark_results,
    create_leaderboard
)

from .benchmark_core.biomedical_scenarios import (
    generate_eeg_scenario,
    generate_ecg_scenario,
    generate_respiratory_scenario,
    BIOMEDICAL_SCENARIOS
)

# Registry imports
from .benchmark_registry.registry import (
    get_registry,
    register_estimator,
    BaseEstimator,
    EstimatorResult
)

# Backend imports
from .benchmark_backends.selector import select_backend

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    
    # Core factory
    "BiomedicalHurstEstimatorFactory",
    "EstimatorType",
    "ConfidenceMethod",
    "HurstResult",
    "BiomedicalDataProcessor",
    
    # Data generation
    "generate_grid",
    "fbm_davies_harte",
    "generate_fgn",
    "generate_arfima",
    "generate_mrw",
    "generate_fou",
    "add_contamination",
    "TimeSeriesSample",
    
    # Benchmarking
    "BenchmarkConfig",
    "BenchmarkResult",
    "ScoringWeights",
    "run_benchmark_on_dataset",
    "analyze_benchmark_results",
    "create_leaderboard",
    
    # Biomedical scenarios
    "generate_eeg_scenario",
    "generate_ecg_scenario",
    "generate_respiratory_scenario",
    "BIOMEDICAL_SCENARIOS",
    
    # Registry
    "get_registry",
    "register_estimator",
    "BaseEstimator",
    "EstimatorResult",
    
    # Backend
    "select_backend",
]
