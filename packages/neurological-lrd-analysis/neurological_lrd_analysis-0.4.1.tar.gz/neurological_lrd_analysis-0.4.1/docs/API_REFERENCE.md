# Biomedical Hurst Factory - API Reference

## Overview

The Biomedical Hurst Factory is a comprehensive Python library for estimating Hurst exponents in biomedical time series data. It provides multiple estimation methods, statistical confidence intervals, and performance monitoring capabilities.

## Quick Start

```python
from biomedical_hurst_factory import BiomedicalHurstEstimatorFactory, EstimatorType

# Create factory instance
factory = BiomedicalHurstEstimatorFactory()

# Estimate Hurst exponent using DFA
result = factory.estimate(data, EstimatorType.DFA)
print(f"Hurst exponent: {result.hurst_estimate:.3f}")
print(f"Confidence interval: {result.confidence_interval}")
```

## Core Classes

### BiomedicalHurstEstimatorFactory

Main factory class for Hurst exponent estimation.

#### Constructor
```python
BiomedicalHurstEstimatorFactory()
```

#### Methods

##### `estimate(data, method, **kwargs)`

Estimate Hurst exponent using specified method.

**Parameters:**
- `data` (Union[np.ndarray, List[float]]): Time series data
- `method` (Union[str, EstimatorType]): Estimation method
- `confidence_method` (ConfidenceMethod, optional): Confidence interval method. Default: `ConfidenceMethod.BOOTSTRAP`
- `confidence_level` (float, optional): Confidence level (0-1). Default: `0.95`
- `preprocess` (bool, optional): Whether to preprocess data. Default: `True`
- `assess_quality` (bool, optional): Whether to assess data quality. Default: `True`
- `**kwargs`: Additional method-specific parameters

**Returns:**
- `Union[HurstResult, GroupHurstResult]`: Estimation results

**Example:**
```python
# Single method estimation
result = factory.estimate(data, EstimatorType.DFA)

# Group estimation (multiple methods)
group_result = factory.estimate(data, EstimatorType.ALL)

# With custom parameters
result = factory.estimate(
    data, 
    EstimatorType.DFA,
    confidence_method=ConfidenceMethod.THEORETICAL,
    confidence_level=0.99,
    min_window=20,
    max_window=200
)
```

## Enumerations

### EstimatorType

Available estimation methods.

**Temporal Methods:**
- `DFA`: Detrended Fluctuation Analysis
- `RS_ANALYSIS`: Rescaled Range (R/S) Analysis
- `HIGUCHI`: Higuchi Fractal Dimension
- `GENERALIZED_HURST`: Generalized Hurst Exponent

**Spectral Methods:**
- `PERIODOGRAM`: Periodogram-based estimation
- `GPH`: Geweke-Porter-Hudak estimator
- `WHITTLE_MLE`: Local Whittle Maximum Likelihood

**Wavelet Methods:**
- `DWT`: Discrete Wavelet Transform Logscale
- `NDWT`: Non-decimated Wavelet Transform Logscale
- `ABRY_VEITCH`: Abry-Veitch wavelet estimator

**Multifractal Methods:**
- `MFDFA`: Multifractal Detrended Fluctuation Analysis
- `MF_DMA`: Multifractal Detrended Moving Average

**Group Methods:**
- `TEMPORAL`: All temporal methods
- `SPECTRAL`: All spectral methods
- `WAVELET`: All wavelet methods
- `ALL`: All available methods

### ConfidenceMethod

Confidence interval estimation methods.

- `BOOTSTRAP`: Bootstrap resampling
- `THEORETICAL`: Theoretical confidence intervals
- `CROSS_VALIDATION`: Cross-validation based
- `NONE`: No confidence intervals

## Result Classes

### HurstResult

Result from single method estimation.

**Attributes:**
- `hurst_estimate` (float): Estimated Hurst exponent
- `estimator_name` (str): Name of the estimator used
- `confidence_interval` (Tuple[float, float]): Confidence interval
- `confidence_level` (float): Confidence level used
- `confidence_method` (str): Method used for confidence estimation
- `standard_error` (float): Standard error of the estimate
- `bias_estimate` (Optional[float]): Estimated bias
- `variance_estimate` (float): Estimated variance
- `bootstrap_samples` (Optional[np.ndarray]): Bootstrap samples (if applicable)
- `computation_time` (float): Computation time in seconds
- `memory_usage` (Optional[float]): Memory usage (if available)
- `convergence_flag` (bool): Whether the method converged
- `data_quality_score` (float): Data quality score (0-1)
- `missing_data_fraction` (float): Fraction of missing data
- `outlier_fraction` (float): Fraction of outliers detected
- `stationarity_p_value` (Optional[float]): Stationarity test p-value
- `regression_r_squared` (Optional[float]): R-squared of regression fit
- `scaling_range` (Optional[Tuple[int, int]]): Scaling range used
- `goodness_of_fit` (Optional[float]): Goodness of fit metric
- `signal_to_noise_ratio` (Optional[float]): Signal-to-noise ratio
- `artifact_detection` (Dict[str, Any]): Artifact detection results

**Methods:**
- `to_dict()`: Convert result to dictionary
- `__str__()`: String representation

### GroupHurstResult

Result from group estimation (multiple methods).

**Attributes:**
- `individual_results` (List[HurstResult]): Results from individual methods
- `ensemble_estimate` (float): Ensemble average estimate
- `ensemble_confidence_interval` (Tuple[float, float]): Ensemble confidence interval
- `method_agreement` (float): Agreement between methods (0-1)
- `best_method` (str): Best performing method name
- `consensus_estimate` (float): Median estimate across methods
- `weighted_estimate` (float): Quality-weighted estimate
- `total_computation_time` (float): Total computation time

**Methods:**
- `to_dict()`: Convert result to dictionary
- `__str__()`: String representation

## Data Processing

### BiomedicalDataProcessor

Specialized preprocessing for biomedical time series data.

#### Static Methods

##### `assess_data_quality(data)`

Comprehensive data quality assessment.

**Parameters:**
- `data` (np.ndarray): Time series data

**Returns:**
- `Dict[str, Any]`: Quality metrics including:
  - `data_quality_score`: Overall quality score (0-1)
  - `missing_data_fraction`: Fraction of missing data
  - `outlier_fraction`: Fraction of outliers
  - `signal_to_noise_ratio`: SNR in dB
  - `stationarity_p_value`: Stationarity test p-value
  - `artifact_detection`: Artifact detection results

##### `preprocess_biomedical_data(data, **kwargs)`

Preprocess biomedical time series data.

**Parameters:**
- `data` (np.ndarray): Input time series
- `handle_missing` (str, optional): Missing data handling method. Default: `'interpolate'`
  - `'interpolate'`: Linear interpolation
  - `'remove'`: Remove missing values
  - `'forward_fill'`: Forward fill
- `remove_outliers` (bool, optional): Whether to remove outliers. Default: `True`
- `detrend` (bool, optional): Whether to detrend data. Default: `True`
- `filter_artifacts` (bool, optional): Whether to filter artifacts. Default: `True`
- `trim_convergence` (bool, optional): Whether to trim for convergence. Default: `False`
- `stability_threshold` (float, optional): Stability threshold for trimming. Default: `0.05`
- `min_stable_fraction` (float, optional): Minimum stable fraction. Default: `0.1`

**Returns:**
- `Tuple[np.ndarray, Dict[str, Any]]`: Processed data and preprocessing log

## Individual Estimators

### DFAEstimator

Detrended Fluctuation Analysis optimized for biomedical signals.

**Parameters:**
- `min_window` (Optional[int]): Minimum window size
- `max_window` (Optional[int]): Maximum window size
- `polynomial_order` (int): Polynomial order for detrending. Default: `1`
- `overlap` (float): Window overlap fraction. Default: `0.5`

### HiguchiEstimator

Higuchi Fractal Dimension method.

**Parameters:**
- `kmax` (Optional[int]): Maximum k value

### PeriodogramEstimator

Periodogram-based Hurst estimation.

**Parameters:**
- `low_freq_fraction` (float): Fraction of low frequencies to use. Default: `0.1`
- `high_freq_cutoff` (float): High frequency cutoff. Default: `0.4`

### RSAnalysisEstimator

Rescaled Range (R/S) Analysis estimator.

**Parameters:**
- `min_window` (Optional[int]): Minimum window size
- `max_window` (Optional[int]): Maximum window size

### GPHEstimator

Geweke-Porter-Hudak (GPH) estimator.

**Parameters:**
- `m_fraction` (float): Fraction of frequencies to use. Default: `0.5`

### WhittleMLEEstimator

Local Whittle Maximum Likelihood Estimator.

**Parameters:**
- `m_fraction` (float): Fraction of frequencies to use. Default: `0.5`

### GHEEstimator

Generalized Hurst Exponent estimator.

**Parameters:**
- `q_values` (Optional[List[float]]): q-values for estimation. Default: `[2.0]`
- `max_tau` (int): Maximum tau value. Default: `100`

### DWTEstimator

Discrete Wavelet Transform Logscale estimator.

**Parameters:**
- `wavelet` (str): Wavelet type. Default: `'db4'`
- `max_level` (Optional[int]): Maximum decomposition level

### AbryVeitchEstimator

Abry-Veitch wavelet-based estimator.

**Parameters:**
- `wavelet` (str): Wavelet type. Default: `'db4'`
- `max_level` (Optional[int]): Maximum decomposition level

### NDWTEstimator

Non-decimated Wavelet Transform Logscale estimator.

**Parameters:**
- `wavelet` (str): Wavelet type. Default: `'db4'`
- `max_level` (Optional[int]): Maximum decomposition level

### MFDFAEstimator

Multifractal Detrended Fluctuation Analysis estimator.

**Parameters:**
- `q` (float): q-value for estimation. Default: `2.0`
- `min_window` (Optional[int]): Minimum window size
- `max_window` (Optional[int]): Maximum window size
- `polynomial_order` (int): Polynomial order for detrending. Default: `1`
- `overlap` (float): Window overlap fraction. Default: `0.5`

### MFDMAEstimator

Multifractal Detrended Moving Average estimator.

**Parameters:**
- `q` (float): q-value for estimation. Default: `2.0`
- `min_window` (Optional[int]): Minimum window size
- `max_window` (Optional[int]): Maximum window size
- `overlap` (float): Window overlap fraction. Default: `0.5`

## Convenience Functions

### `estimate_hurst(data, method="dfa", **kwargs)`

Convenience function for quick Hurst estimation.

**Parameters:**
- `data` (Union[np.ndarray, List[float]]): Time series data
- `method` (str): Estimation method name. Default: `"dfa"`
- `**kwargs`: Additional parameters

**Returns:**
- `HurstResult`: Estimation result

### `compare_methods(data, methods=None, **kwargs)`

Convenience function for method comparison.

**Parameters:**
- `data` (Union[np.ndarray, List[float]]): Time series data
- `methods` (List[str], optional): Methods to compare. Default: `None` (all methods)
- `**kwargs`: Additional parameters

**Returns:**
- `GroupHurstResult`: Comparison results

## Error Handling

The library provides comprehensive error handling:

- **Data validation**: Automatic validation of input data
- **Method-specific errors**: Detailed error messages for each estimator
- **Graceful degradation**: Fallback implementations when optional dependencies unavailable
- **Logging**: Comprehensive logging for debugging

## Performance Considerations

- **Lazy imports**: Heavy modules loaded only when needed
- **Memory efficient**: Optimized algorithms for large datasets
- **Parallel processing**: Support for parallel computation (when available)
- **Caching**: Results cached for repeated computations

## Dependencies

**Required:**
- numpy >= 1.22
- scipy >= 1.8
- pandas >= 1.4

**Optional:**
- jax >= 0.4.0 (for GPU acceleration)
- jaxlib >= 0.4.0 (for GPU acceleration)
- numba >= 0.55 (for CPU acceleration)
- pywavelets (for wavelet methods)
- scikit-learn >= 1.0 (for ML methods)
- matplotlib >= 3.5 (for plotting)
- seaborn >= 0.11 (for plotting)

## Examples

### Basic Usage

```python
import numpy as np
from biomedical_hurst_factory import BiomedicalHurstEstimatorFactory, EstimatorType

# Generate test data
np.random.seed(42)
data = np.cumsum(np.random.randn(1000))

# Create factory
factory = BiomedicalHurstEstimatorFactory()

# Single method estimation
result = factory.estimate(data, EstimatorType.DFA)
print(f"DFA estimate: {result.hurst_estimate:.3f}")
print(f"Confidence interval: {result.confidence_interval}")
print(f"Data quality score: {result.data_quality_score:.3f}")
```

### Method Comparison

```python
# Compare multiple methods
group_result = factory.estimate(data, EstimatorType.ALL)
print(f"Ensemble estimate: {group_result.ensemble_estimate:.3f}")
print(f"Best method: {group_result.best_method}")
print(f"Method agreement: {group_result.method_agreement:.3f}")
```

### Custom Parameters

```python
# DFA with custom parameters
result = factory.estimate(
    data, 
    EstimatorType.DFA,
    min_window=20,
    max_window=200,
    polynomial_order=2,
    confidence_method=ConfidenceMethod.THEORETICAL
)
```

### Data Preprocessing

```python
from biomedical_hurst_factory import BiomedicalDataProcessor

processor = BiomedicalDataProcessor()

# Assess data quality
quality = processor.assess_data_quality(data)
print(f"Data quality score: {quality['data_quality_score']:.3f}")

# Preprocess data
processed_data, log = processor.preprocess_biomedical_data(
    data,
    handle_missing='interpolate',
    remove_outliers=True,
    detrend=True,
    trim_convergence=True
)
```

## Enhanced Benchmarking

### Benchmarking Infrastructure

The library includes comprehensive benchmarking capabilities with detailed statistical reporting and parametrized scoring functions for application-specific optimization.

#### Scoring Weights Configuration

```python
from benchmark_core.runner import ScoringWeights

# Application-specific scoring weights
bci_weights = ScoringWeights(
    success_rate=0.4,    # High: Need reliable results
    accuracy=0.2,        # Medium: Some accuracy trade-off acceptable
    speed=0.3,           # High: Real-time constraints
    robustness=0.1       # Low: Controlled environment
)

research_weights = ScoringWeights(
    success_rate=0.2,    # Medium: Some failures acceptable
    accuracy=0.4,        # High: Need precise measurements
    speed=0.1,           # Low: Time not critical
    robustness=0.3       # High: Robust across conditions
)
```

#### Benchmark Configuration

```python
from benchmark_core.runner import BenchmarkConfig

config = BenchmarkConfig(
    output_dir='./benchmark_results',
    n_bootstrap=100,
    confidence_level=0.95,
    save_results=True,
    verbose=False,
    scoring_weights=bci_weights  # Application-specific scoring
)
```

#### Statistical Metrics

The benchmarking system reports comprehensive statistical metrics:

- **Bias**: Systematic error (estimate - true_value)
- **Absolute Error**: |estimate - true_value|
- **Relative Error**: Absolute error / true_value
- **RMSE**: Root Mean Square Error
- **Standard Error**: Standard deviation of estimates
- **Confidence Interval**: Statistical confidence bounds
- **P-value**: Statistical significance of regression fit
- **Significance Rate**: Percentage of statistically significant estimates

#### Benchmark Execution

```python
from benchmark_core.generation import generate_grid
from benchmark_core.runner import run_benchmark_on_dataset, analyze_benchmark_results, create_leaderboard

# Generate test datasets
datasets = generate_grid(
    hurst_values=[0.3, 0.5, 0.7, 0.8],
    lengths=[512, 1024, 2048],
    contaminations=['none', 'noise']
)

# Run benchmark
results = run_benchmark_on_dataset(datasets, config)

# Analyze results
analysis = analyze_benchmark_results(results)
leaderboard = create_leaderboard(results)
```

#### Output Files

The benchmarking system generates:
- `benchmark_results.csv`: Raw results with all metrics
- `leaderboard.csv`: Ranked estimator performance
- `detailed_analysis.csv`: Comprehensive statistical analysis
- `benchmark_summary.txt`: Human-readable summary

For detailed benchmarking documentation, see [BENCHMARKING_GUIDE.md](BENCHMARKING_GUIDE.md).

## Command Line Interface

### Benchmark Script

The main benchmarking script is located at `scripts/run_benchmark.py`:

```bash
# Basic usage
python scripts/run_benchmark.py

# Custom parameters
python scripts/run_benchmark.py --hurst-values 0.3,0.5,0.7,0.8 --lengths 512,1024,2048 --output-dir ./my_results

# Biomedical scenarios
python scripts/run_benchmark.py --biomedical-scenarios eeg_rest,ecg_normal --contaminations none,noise,electrode_pop

# Neurological conditions
python scripts/run_benchmark.py --biomedical-scenarios eeg_parkinsonian,eeg_epileptic --contaminations heavy_tail,neural_avalanche

# Application-specific scoring
python scripts/run_benchmark.py --success-weight 0.4 --accuracy-weight 0.2 --speed-weight 0.3 --robustness-weight 0.1
```

### Demo Scripts

```bash
# Biomedical scenarios demonstration
python scripts/biomedical_scenarios_demo.py

# Neurological conditions demonstration  
python scripts/neurological_conditions_demo.py

# NumPyro integration demonstration
python scripts/numpyro_integration_demo.py

# Application scoring demonstration
python scripts/application_scoring_demo.py
```

## Biomedical Scenarios

### Scenario-Based Data Generation

The library includes realistic biomedical time series generators for EEG, ECG, and respiratory signals:

```python
from benchmark_core.biomedical_scenarios import (
    generate_eeg_scenario, generate_ecg_scenario, generate_respiratory_scenario
)

# Generate EEG data
eeg_data = generate_eeg_scenario(
    n=1000, 
    hurst=0.7, 
    scenario='rest',  # 'rest', 'eyes_closed', 'eyes_open', 'sleep', 'seizure'
    contamination_level=0.1
)

# Generate ECG data
ecg_data = generate_ecg_scenario(
    n=1000,
    hurst=0.5,
    heart_rate=70.0,  # BPM
    contamination_level=0.1
)

# Generate respiratory data
resp_data = generate_respiratory_scenario(
    n=1000,
    hurst=0.6,
    breathing_rate=15.0,  # breaths per minute
    contamination_level=0.1
)
```

### Enhanced Contamination Methods

Biomedical-specific contamination methods:

```python
from benchmark_core.generation import add_contamination

# Biomedical contamination types
contamination_types = [
    'baseline_drift',        # Slow baseline drift
    'electrode_pop',         # Electrode pop artifacts
    'motion',                # Motion artifacts
    'powerline',             # Powerline interference (50/60 Hz)
    'heavy_tail',            # Heavy-tail amplitude distributions (Parkinson's, epilepsy)
    'neural_avalanche',      # Neural avalanche patterns (critical dynamics)
    'parkinsonian_tremor',   # Parkinsonian tremor (4-6 Hz oscillations)
    'epileptic_spike',       # Epileptic spike patterns
    'burst_suppression',     # Burst-suppression patterns (anesthesia, coma)
    'noise',                 # Gaussian noise
    'missing',               # Missing data points
    'outliers',              # Outlier values
    'trend'                  # Linear trend
]

# Apply contamination
contaminated_data = add_contamination(
    data, 
    contamination_type='electrode_pop',
    contamination_level=0.1
)
```

### Predefined Biomedical Scenarios

```python
from benchmark_core.biomedical_scenarios import BIOMEDICAL_SCENARIOS

# Available scenarios
available_scenarios = list(BIOMEDICAL_SCENARIOS.keys())
# ['eeg_rest', 'eeg_eyes_closed', 'eeg_sleep', 'eeg_parkinsonian', 'eeg_epileptic', 
#  'eeg_parkinsonian_avalanche', 'eeg_epileptic_heavy_tail', 'eeg_burst_suppression',
#  'ecg_normal', 'ecg_tachycardia', 'respiratory_rest']

# Generate grid with biomedical scenarios
from benchmark_core.generation import generate_grid

datasets = generate_grid(
    hurst_values=[0.5, 0.7],
    lengths=[512, 1024],
    contaminations=['none', 'noise', 'electrode_pop'],
    biomedical_scenarios=['eeg_rest', 'ecg_normal']
)
```

For detailed biomedical scenario documentation, see [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md).

## Version History

- **v0.1.0**: Initial release with classical estimators
- **v0.2.0**: Added wavelet and multifractal estimators
- **v0.3.0**: Added convergence analysis and lazy imports
- **v0.4.0**: Enhanced benchmarking with comprehensive statistical reporting

