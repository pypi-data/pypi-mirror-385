# Changelog

All notable changes to the Neurological LRD Analysis project will be documented in this file.

**Research Context**: This library is developed as part of PhD research in Biomedical Engineering at the University of Reading, UK by Davian R. Chin, focusing on **Physics-Informed Fractional Operator Learning for Real-Time Neurological Biomarker Detection: A Framework for Memory-Driven EEG Analysis**.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Neural network baseline implementations (MLP, CNN, LSTM, GRU, Transformer)
- Machine learning baseline implementations (Random Forest, SVR, GBT)
- Advanced wavelet techniques (Wavelet Leaders, Wavelet Whittle)

### Changed
- Project structure reorganized for GitHub repository
- Documentation moved to `docs/` folder
- Scripts moved to `scripts/` folder
- Tests moved to `tests/` folder

## [0.4.0] - 2025-10-XX

### Added
- **Neurological Contamination Methods**
  - Heavy-tail amplitude distributions for Parkinson's disease and epilepsy
  - Neural avalanche patterns with critical dynamics
  - Parkinsonian tremor (4-6 Hz oscillations with amplitude modulation)
  - Epileptic spike patterns (sharp onset, exponential decay)
  - Burst-suppression patterns (anesthesia, coma conditions)

- **Neurological Scenarios**
  - `eeg_parkinsonian`: Base Parkinson's EEG with reduced alpha, increased beta
  - `eeg_parkinsonian_avalanche`: Combined with neural avalanche patterns
  - `eeg_epileptic`: Base epileptic EEG with irregular patterns
  - `eeg_epileptic_heavy_tail`: Combined with heavy-tail distributions
  - `eeg_burst_suppression`: Burst-suppression patterns

- **Enhanced Contamination Methods**
  - Baseline drift (slow sinusoidal drift)
  - Electrode pop artifacts (sudden jumps)
  - Motion artifacts (sudden amplitude changes)
  - Powerline interference (50/60 Hz noise)

- **Demo Scripts**
  - `neurological_conditions_demo.py`: Comprehensive neurological scenarios demonstration
  - `application_scoring_demo.py`: Application-specific scoring demonstration

### Changed
- Enhanced contamination methods with biomedical-specific artifacts
- Improved statistical analysis with kurtosis and skewness calculations
- Updated documentation with neurological condition examples

## [0.3.0] - 2025-10-XX

### Added
- **Biomedical Scenarios**
  - EEG scenarios: rest, eyes closed/open, sleep, seizure patterns
  - ECG scenarios: normal heart rate, tachycardia with realistic QRS complexes
  - Respiratory scenarios: breathing patterns with irregular breathing

- **Biomedical-Specific Artifacts**
  - Eye movement artifacts (EOG)
  - Muscle artifacts (EMG)
  - Cough artifacts for respiratory signals
  - Speaking artifacts (irregular breathing)

- **Enhanced Data Generation**
  - Realistic frequency characteristics for different EEG states
  - Appropriate amplitude scaling for different signal types
  - Integration with existing contamination methods

- **Demo Scripts**
  - `biomedical_scenarios_demo.py`: Comprehensive biomedical scenarios demonstration

### Changed
- Updated data generation to support biomedical scenarios
- Enhanced benchmarking system to handle scenario-specific data

## [0.2.0] - 2025-10-XX

### Added
- **Advanced Synthetic Data Generators**
  - ARFIMA (AutoRegressive Fractionally Integrated Moving Average)
  - Multifractal Random Walk (MRW)
  - Fractional Ornstein-Uhlenbeck (fOU) process
  - Enhanced fBm generation using Davies-Harte method via `fbm` library

- **Advanced Estimation Methods**
  - MFDFA (Multifractal Detrended Fluctuation Analysis)
  - MF-DMA (Multifractal Detrended Moving Average)
  - NDWT (Non-decimated Wavelet Transform)
  - Abry-Veitch wavelet estimation

- **Enhanced Benchmarking System**
  - Comprehensive statistical metrics (bias, MAE, RMSE, confidence intervals, p-values)
  - Parametrized scoring functions for different applications
  - Application-specific rankings (BCI, research, clinical, etc.)
  - Advanced visualizations for accuracy, uncertainty, and efficiency analysis

- **NumPyro Integration**
  - Bayesian Hurst exponent estimation
  - MCMC sampling with convergence diagnostics
  - Hierarchical modeling capabilities
  - Enhanced uncertainty quantification

### Changed
- Improved estimator accuracy with corrected formulas
- Enhanced confidence interval reporting
- Better error handling and validation

## [0.1.0] - 2025-10-XX

### Added
- **Core Estimation Methods**
  - Temporal: R/S Analysis, DFA, Higuchi, Generalized Hurst Exponent
  - Spectral: Periodogram, GPH, Whittle MLE
  - Wavelet: DWT, CWT

- **Basic Synthetic Data Generation**
  - Fractional Brownian Motion (fBm)
  - Fractional Gaussian Noise (fGn)

- **Backend Infrastructure**
  - JAX GPU acceleration
  - Numba CPU optimization
  - Intelligent backend selection
  - Lazy imports for efficiency

- **Basic Benchmarking**
  - Simple performance comparison
  - Basic statistical metrics

- **Documentation**
  - API reference
  - Tutorial
  - Configuration guide

## [0.0.1] - 2025-10-XX

### Added
- Initial project structure
- Basic package configuration
- Core library framework
