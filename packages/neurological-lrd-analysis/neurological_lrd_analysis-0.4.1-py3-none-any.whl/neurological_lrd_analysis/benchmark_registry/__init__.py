"""
Registry for Hurst exponent estimation methods.

This module provides a registry of available estimation methods and their implementations.

Developed as part of PhD research in Biomedical Engineering at the University of Reading, UK.
Author: Davian R. Chin (PhD Candidate in Biomedical Engineering)
Research Focus: Physics-Informed Fractional Operator Learning for Real-Time Neurological Biomarker Detection.
"""

from .registry import get_registry, register_estimator, EstimatorResult, BaseEstimator

__all__ = [
    "get_registry",
    "register_estimator", 
    "EstimatorResult",
    "BaseEstimator",
]

