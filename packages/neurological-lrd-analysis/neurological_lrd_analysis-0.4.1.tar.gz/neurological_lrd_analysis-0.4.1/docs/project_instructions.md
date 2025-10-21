# Long-Range Dependence Estimation in Biomedical Time Series Data

### AIM

- To develop a efficient and flexible LRD estimation framework for supporting biomedical engineering research into more robust, efficient, and accurate LRD estimators.

- To establish reproducible performance benchmarks against which researchers can compare more innovative LRD estimators.

- To create a publicly available library (PyPI installation) that can be installed and run on any machine, and make use of available hardware such as GPUs, TPUs etc.


### Features

- Should implement the most commonly used classical (statistical estimators): 
    - temporal: R/S, DFA, Higuhi, GHE, 
    - spectral: Whittle MLE, GPH, Periodogram, spectral-variance analysis
    - multifractal: mdfa

- Should implement modern wavelet techniques:
    - wavelet leaders
    - wavelet coefficients
    - wavelet variance/log variance
    - wavelet whittle

- Should implement machine learning base lines:
    - Randon Forest
    - SVR
    - GBT

- Should implement neural network baselines:
    - MLP
    - CNN
    - LSTM
    - GRU
    - Transformer

- Should include multiple synthetic time series data generators:
    - fBm and fGn
    - ARFIMA
    - Multifractal Random Walk (MRW)
    - Fractional Ornstein-Uhlenbek (fOU)

- Should implement adaptive backend selection and memory management:
    - JAX - GPU acceleration
    - NUMBA - CPU/GPU acceleration/parallelisation
    - NUMPY/SCIPY fallback
    - hardware detection with intelligent backend selection.
    - intelligent memory management

- Efficient and intuitive performance benchmarking process with leaderboard generation
    - flexible benchmarking process allowing users to:
        - add/register their own estimators and have them participate in the benchmarking process
        - select which estimators participate in the benchmarking process
        - select which data models are used in the benchmarking process
        - provide bias and uncertainty quantification with estimation processes.

    - implement a smart and flexible estimator scoring process that is used to rank estimators on the leaderboard
    - provide guidance on estimator and data generator selection and reproducibility guidance
    - provide useful visualisations of results.

- Should implement contamination types and scenarios
    - nonstationarity, heavy-tail statistics, outliers, missing data, etc
    - biomedical scenarios: EEG, ECG, etc with configuration guidance

### Plan proposal (phased, high signal)

#### Phase 0 — Foundations and packaging
Scaffold packaging, module layout, Python 3.11, env biomedical_hurst_env 1.
Set up backend abstraction and hardware detection (NumPy/JAX/Numba) with automatic selection.
Establish test harness wiring so current tests can run; stub missing modules referenced by tests.

#### Phase 1 — Classical estimators and registry
Extend BiomedicalHurstEstimatorFactory with R/S, GPH, Local Whittle.
Create a registry with at least the 12 built-ins that tests expect.
Solidify confidence intervals (bootstrap and theoretical) and data-quality pipeline.

#### Phase 2 — Wavelet and multifractal estimators
Implement DWT/NDWT logscale, Abry–Veitch, Wavelet Leaders.
Add MFDFA (q=2), MF-DMA (q=2), and GHE.
Validate scaling ranges and regression robustness.

#### Phase 3 — Synthetic data generators and contamination
Implement fBm/fGn (Davies–Harte), ARFIMA, MRW, fOU; add contamination (noise, missingness, nonstationarity).
Provide unified generator API and grid builder for benchmarks.

#### Phase 4 — Benchmarking, backends, and leaderboard
Implement benchmark_core.generation and benchmark_core.runner used by tests.
Implement benchmark_backends.selector and a backend layer with JAX-first acceleration respecting your preference for JAX/NumPyro going forward 2.
Produce reproducible benchmark outputs and plots.

#### Phase 5 — ML and NN baselines
ML: RF, SVR, GBT with robust feature extractor.
NN: JAX/Flax baselines (MLP, CNN, LSTM/GRU, Transformer); keep them optional, with clear API.
Provide training scripts and pre-trained configs where feasible.

#### Phase 6 — Docs, tutorials, and release
Markdown-based tutorials/examples (no notebooks) 3, API reference sync, quickstart, and method selection guide.
CI, versioning, and PyPI publish workflow; note hpfracc compatibility and Python 3.11 

### Technical Notes:

- create a python virtual env for this project, and activate everytime the project starts up and becomes active.
- implement effective import management from early to avoid more complex issues later (lazy imports for efficiency)
- use estimator factory for modularising and unifying estimator creation 
- use a unified data generator for creating time series generators
- create a unified plotting module to manage time series visualisation, error quantification visualisations, bias analysis, etc
- use a standardised metadata format together with a data preprocessing pipeline to ensure data standardisation. 
    This should include convergence analysis to find/estimate delayed starting point for time series to ensure that we capture the time
    series after it has settled down into its correct behaviour since it would have been sampled from previously realised time series processes.
- when implementing data models and estimators, always make reference to the research and implementation guidance provided in the root directory. they are placed there to help and guide you with technical implementation and theoretical foundations.
- we will take a test-driven approach to development. testing should be comprehensive and functional. so test coverage should be an on-going process and the development should be done in phases - e.g. data generators: testing and validation, visualsation, then estimators: testing and validation
- full and complete API documentation should be an on-going process.
- For ML and NN modules, we in development and then save these pre-trained models. These pre-trained models are used when the models are deployed to production.
