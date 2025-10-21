Welcome to Neurological LRD Analysis's documentation!
=====================================================

.. image:: https://img.shields.io/badge/python-3.11+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python 3.11+

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

.. image:: https://img.shields.io/badge/PyPI-neurological--lrd--analysis-green.svg
   :target: https://pypi.org/project/neurological-lrd-analysis/
   :alt: PyPI

A comprehensive library for estimating Hurst exponents in neurological time series data, featuring multiple estimation methods, realistic data generation, and advanced benchmarking capabilities.

**Research Context**: This library is developed as part of PhD research in Biomedical Engineering at the University of Reading, UK by Davian R. Chin, focusing on **Physics-Informed Fractional Operator Learning for Real-Time Neurological Biomarker Detection: A Framework for Memory-Driven EEG Analysis**.

Features
--------

* **Multiple Estimation Methods**: Temporal, spectral, wavelet, and multifractal estimators
* **Neurological Scenarios**: EEG, ECG, respiratory signals with realistic artifacts
* **Advanced Benchmarking**: Parametrized scoring and comprehensive statistical analysis
* **GPU Acceleration**: JAX and NumPyro integration for Bayesian inference
* **Clinical Relevance**: Specialized for Parkinson's disease, epilepsy, and neurological conditions

Quick Start
-----------

Install the package:

.. code-block:: bash

   pip install neurological-lrd-analysis

Basic usage:

.. code-block:: python

   from neurological_lrd_analysis import BiomedicalHurstEstimatorFactory, EstimatorType

   # Create factory instance
   factory = BiomedicalHurstEstimatorFactory()

   # Estimate Hurst exponent using DFA
   result = factory.estimate(
       data=your_time_series,
       method=EstimatorType.DFA,
       confidence_method="bootstrap",
       n_bootstrap=100
   )

   print(f"Hurst exponent: {result.hurst_estimate:.3f}")

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   tutorial

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   api_reference
   benchmarking
   configuration
   biomedical_scenarios
   neurological_conditions

.. toctree::
   :maxdepth: 2
   :caption: Advanced Topics

   bayesian_inference
   gpu_acceleration
   custom_estimators
   performance_optimization

.. toctree::
   :maxdepth: 2
   :caption: Development

   contributing
   changelog
   api

.. toctree::
   :maxdepth: 2
   :caption: Research

   research_paper
   benchmarks
   validation_studies

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
