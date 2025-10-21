"""
Backend selection and optimization for Hurst exponent estimation.

This module provides backend selection and optimization functionality for
different computational environments (CPU, GPU, TPU) and acceleration libraries.

Developed as part of PhD research in Biomedical Engineering at the University of Reading, UK.
Author: Davian R. Chin (PhD Candidate in Biomedical Engineering)
Research Focus: Physics-Informed Fractional Operator Learning for Real-Time Neurological Biomarker Detection.
"""

from .selector import select_backend

__all__ = [
    "select_backend",
]
