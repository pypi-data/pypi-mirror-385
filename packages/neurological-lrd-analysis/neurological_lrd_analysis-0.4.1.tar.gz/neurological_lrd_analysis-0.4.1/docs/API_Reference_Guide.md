# Biomedical Hurst Exponent Estimation Factory - API Reference

**Version:** 1.0.0  
**Date:** October 2025  
**License:** MIT

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Core Classes](#core-classes)
4. [Data Types](#data-types)
5. [Estimator Methods](#estimator-methods)
6. [Configuration](#configuration)
7. [Examples](#examples)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Quick Reference](#quick-reference)

---

## Overview

The Biomedical Hurst Exponent Estimation Factory provides a comprehensive, production-ready library for estimating Hurst exponents in biomedical time series data. The library features multiple estimation methods, statistical confidence intervals, biomedical-specific preprocessing, and comprehensive quality assessment.

### Key Features

- **Multiple Estimation Methods**: DFA, Higuchi, Periodogram, and group estimation
- **Statistical Confidence**: Bootstrap and theoretical confidence intervals
- **Biomedical Preprocessing**: Missing data handling, artifact detection, quality assessment
- **Performance Monitoring**: Computation time tracking and convergence monitoring
- **Production Ready**: Comprehensive error handling and logging

### Installation

```python
# Import the main factory class
from biomedical_hurst_factory import BiomedicalHurstEstimatorFactory, EstimatorType, ConfidenceMethod

# Or import specific components
from biomedical_hurst_factory import (
    DFAEstimator,
    HiguchiEstimator, 
    PeriodogramEstimator,
    HurstResult,
    GroupHurstResult
)
```

---

## Quick Start

```python
import numpy as np
from biomedical_hurst_factory import BiomedicalHurstEstimatorFactory, EstimatorType

# Create factory instance
factory = BiomedicalHurstEstimatorFactory()

# Load your biomedical time series data
data = np.random.randn(1000).cumsum()  # Example: random walk

# Single method estimation
result = factory.estimate(data, EstimatorType.DFA)
print(f"Hurst exponent: {result.hurst_estimate:.3f}")
print(f"95% CI: [{result.confidence_interval[0]:.3f}, {result.confidence_interval[1]:.3f}]")

# Group estimation with all methods
group_result = factory.estimate(data, EstimatorType.ALL)
print(f"Ensemble estimate: {group_result.ensemble_estimate:.3f}")
print(f"Best method: {group_result.best_method}")
```

---

## Core Classes

### BiomedicalHurstEstimatorFactory

**Main factory class for biomedical time series Hurst exponent estimation.**

#### Constructor

```python
BiomedicalHurstEstimatorFactory()
```

Creates a new factory instance with all estimators initialized and ready to use.

**Returns:**
- `BiomedicalHurstEstimatorFactory`: Factory instance

#### Methods

##### estimate()

**Primary method for Hurst exponent estimation.**

```python
estimate(
    data: Union[np.ndarray, List[float]], 
    method: Union[str, EstimatorType],
    confidence_method: ConfidenceMethod = ConfidenceMethod.BOOTSTRAP,
    confidence_level: float = 0.95,
    preprocess: bool = True,
    assess_quality: bool = True,
    **kwargs
) -> Union[HurstResult, GroupHurstResult]
```

**Parameters:**
- **`data`** (array-like): Time series data to analyze
- **`method`** (str or EstimatorType): Estimation method or group
  - Single methods: `'dfa'`, `'higuchi'`, `'periodogram'`
  - Groups: `'temporal'`, `'spectral'`, `'all'`
- **`confidence_method`** (ConfidenceMethod): Method for confidence intervals
  - `ConfidenceMethod.BOOTSTRAP`: Non-parametric bootstrap
  - `ConfidenceMethod.THEORETICAL`: Based on regression standard errors
  - `ConfidenceMethod.NONE`: No confidence interval
- **`confidence_level`** (float): Confidence level (0-1), default 0.95
- **`preprocess`** (bool): Enable biomedical preprocessing, default True
- **`assess_quality`** (bool): Enable data quality assessment, default True
- **`**kwargs`**: Method-specific parameters (see individual estimators)

**Returns:**
- `HurstResult`: For single method estimation
- `GroupHurstResult`: For group method estimation

**Raises:**
- `ValueError`: Invalid method name or parameters
- `TypeError`: Invalid data type

**Example:**
```python
# Basic usage
result = factory.estimate(data, 'dfa')

# Advanced configuration
result = factory.estimate(
    data=eeg_signal,
    method=EstimatorType.DFA,
    confidence_method=ConfidenceMethod.BOOTSTRAP,
    confidence_level=0.99,
    preprocess=True,
    # DFA-specific parameters
    min_window=20,
    polynomial_order=2,
    n_bootstrap=500
)
```

---

### Individual Estimators

#### DFAEstimator

**Detrended Fluctuation Analysis estimator optimized for biomedical signals.**

##### Constructor

```python
DFAEstimator()
```

##### estimate()

```python
estimate(
    data: np.ndarray,
    min_window: Optional[int] = None,
    max_window: Optional[int] = None,
    polynomial_order: int = 1,
    overlap: float = 0.5
) -> Tuple[float, Dict[str, Any]]
```

**Parameters:**
- **`data`** (np.ndarray): Input time series
- **`min_window`** (int, optional): Minimum window size for scaling analysis
  - Default: `max(10, len(data) // 100)`
- **`max_window`** (int, optional): Maximum window size
  - Default: `min(len(data) // 4, 500)`
- **`polynomial_order`** (int): Order of polynomial detrending
  - `1`: Linear detrending (default)
  - `2`: Quadratic detrending
  - `3`: Cubic detrending
- **`overlap`** (float): Overlap fraction between windows (0-1)
  - Default: 0.5 (50% overlap)

**Returns:**
- `tuple`: (hurst_estimate, additional_metrics)
  - `hurst_estimate` (float): Estimated Hurst exponent
  - `additional_metrics` (dict): Regression statistics and quality metrics

**Mathematical Foundation:**
- Scaling law: F(s) ∼ s^H
- Where F(s) is the detrended fluctuation function
- Linear regression in log-log space: log(F(s)) = H·log(s) + const

**Example:**
```python
dfa = DFAEstimator()
h_est, metrics = dfa.estimate(
    data,
    min_window=15,
    max_window=200,
    polynomial_order=2,
    overlap=0.75
)
print(f"Hurst: {h_est:.3f}, R²: {metrics['regression_r_squared']:.3f}")
```

#### HiguchiEstimator

**Higuchi Fractal Dimension method for fast Hurst estimation.**

##### Constructor

```python
HiguchiEstimator()
```

##### estimate()

```python
estimate(
    data: np.ndarray,
    kmax: Optional[int] = None
) -> Tuple[float, Dict[str, Any]]
```

**Parameters:**
- **`data`** (np.ndarray): Input time series
- **`kmax`** (int, optional): Maximum k value for curve length calculation
  - Default: `min(20, len(data) // 10)`

**Returns:**
- `tuple`: (hurst_estimate, additional_metrics)

**Mathematical Foundation:**
- Fractal dimension relationship: H = 2 - D
- Curve length scaling: L(k) ∼ k^(-D)
- Where k is the step size parameter

**Example:**
```python
higuchi = HiguchiEstimator()
h_est, metrics = higuchi.estimate(data, kmax=15)
print(f"Hurst: {h_est:.3f}, Fractal Dimension: {metrics['fractal_dimension']:.3f}")
```

#### PeriodogramEstimator

**Periodogram-based Hurst estimation using spectral analysis.**

##### Constructor

```python
PeriodogramEstimator()
```

##### estimate()

```python
estimate(
    data: np.ndarray,
    low_freq_fraction: float = 0.1,
    high_freq_cutoff: float = 0.4
) -> Tuple[float, Dict[str, Any]]
```

**Parameters:**
- **`data`** (np.ndarray): Input time series
- **`low_freq_fraction`** (float): Fraction of low frequencies to use
  - Default: 0.1 (10% of frequency range)
- **`high_freq_cutoff`** (float): High frequency cutoff (0-0.5)
  - Default: 0.4 (exclude very high frequencies)

**Returns:**
- `tuple`: (hurst_estimate, additional_metrics)

**Mathematical Foundation:**
- Power spectral density scaling: S(f) ∼ f^(1-2H)
- Linear regression: log(S(f)) = (1-2H)·log(f) + const
- Therefore: H = (1 - slope) / 2

**Example:**
```python
periodogram = PeriodogramEstimator()
h_est, metrics = periodogram.estimate(
    data,
    low_freq_fraction=0.05,
    high_freq_cutoff=0.3
)
```

---

### Data Processing Components

#### BiomedicalDataProcessor

**Specialized preprocessing for biomedical time series data.**

##### Static Methods

##### assess_data_quality()

```python
@staticmethod
assess_data_quality(data: np.ndarray) -> Dict[str, Any]
```

**Parameters:**
- **`data`** (np.ndarray): Input time series data

**Returns:**
- `dict`: Comprehensive quality metrics
  - `data_quality_score` (float): Overall quality score (0-1)
  - `missing_data_fraction` (float): Fraction of missing values
  - `outlier_fraction` (float): Fraction of statistical outliers
  - `signal_to_noise_ratio` (float): SNR estimate in dB
  - `stationarity_p_value` (float): Stationarity test p-value
  - `artifact_detection` (dict): Detected artifacts

**Example:**
```python
from biomedical_hurst_factory import BiomedicalDataProcessor

quality = BiomedicalDataProcessor.assess_data_quality(data)
print(f"Quality Score: {quality['data_quality_score']:.3f}")
print(f"SNR: {quality['signal_to_noise_ratio']:.1f} dB")
```

##### preprocess_biomedical_data()

```python
@staticmethod
preprocess_biomedical_data(
    data: np.ndarray,
    handle_missing: str = 'interpolate',
    remove_outliers: bool = True,
    detrend: bool = True,
    filter_artifacts: bool = True
) -> Tuple[np.ndarray, Dict[str, Any]]
```

**Parameters:**
- **`data`** (np.ndarray): Input time series
- **`handle_missing`** (str): Missing data strategy
  - `'interpolate'`: Linear interpolation
  - `'remove'`: Remove missing points
  - `'forward_fill'`: Forward fill missing values
  - `'none'`: No handling
- **`remove_outliers`** (bool): Remove statistical outliers
- **`detrend`** (bool): Remove linear trend
- **`filter_artifacts`** (bool): Apply artifact filtering

**Returns:**
- `tuple`: (processed_data, preprocessing_log)

**Example:**
```python
processed_data, log = BiomedicalDataProcessor.preprocess_biomedical_data(
    raw_data,
    handle_missing='interpolate',
    remove_outliers=True,
    detrend=False,  # Preserve signal characteristics
    filter_artifacts=True
)
print(f"Processed {log['original_length']} -> {log['final_length']} points")
```

#### ConfidenceEstimator

**Statistical confidence interval estimation.**

##### Static Methods

##### bootstrap_confidence()

```python
@staticmethod
bootstrap_confidence(
    estimator: BaseHurstEstimator,
    data: np.ndarray,
    n_bootstrap: int = 100,
    confidence_level: float = 0.95,
    random_state: Optional[int] = None
) -> Tuple[float, Tuple[float, float], np.ndarray]
```

**Parameters:**
- **`estimator`** (BaseHurstEstimator): Estimator instance
- **`data`** (np.ndarray): Input data
- **`n_bootstrap`** (int): Number of bootstrap samples
- **`confidence_level`** (float): Confidence level (0-1)
- **`random_state`** (int, optional): Random seed for reproducibility

**Returns:**
- `tuple`: (mean_estimate, confidence_interval, bootstrap_samples)

**Example:**
```python
from biomedical_hurst_factory import ConfidenceEstimator, DFAEstimator

estimator = DFAEstimator()
mean_h, (ci_lower, ci_upper), samples = ConfidenceEstimator.bootstrap_confidence(
    estimator, data, n_bootstrap=200, confidence_level=0.99, random_state=42
)
```

##### theoretical_confidence()

```python
@staticmethod
theoretical_confidence(
    hurst_estimate: float,
    standard_error: float,
    n_samples: int,
    confidence_level: float = 0.95
) -> Tuple[float, float]
```

**Parameters:**
- **`hurst_estimate`** (float): Point estimate
- **`standard_error`** (float): Standard error from regression
- **`n_samples`** (int): Sample size
- **`confidence_level`** (float): Confidence level

**Returns:**
- `tuple`: (ci_lower, ci_upper)

---

## Data Types

### Enumerations

#### EstimatorType

**Enumeration of available estimator types.**

```python
class EstimatorType(Enum):
    # Individual methods
    DFA = "dfa"
    HIGUCHI = "higuchi"
    PERIODOGRAM = "periodogram"
    
    # Group methods  
    TEMPORAL = "temporal"
    SPECTRAL = "spectral"
    ALL = "all"
```

#### ConfidenceMethod

**Enumeration of confidence interval methods.**

```python
class ConfidenceMethod(Enum):
    BOOTSTRAP = "bootstrap"
    THEORETICAL = "theoretical"
    NONE = "none"
```

### Result Classes

#### HurstResult

**Comprehensive result container for single method estimation.**

```python
@dataclass
class HurstResult:
    # Core results
    hurst_estimate: float
    estimator_name: str
    
    # Statistical confidence
    confidence_interval: Tuple[float, float]
    confidence_level: float
    confidence_method: str
    
    # Error and uncertainty
    standard_error: float
    bias_estimate: Optional[float]
    variance_estimate: float
    bootstrap_samples: Optional[np.ndarray]
    
    # Performance metrics
    computation_time: float
    memory_usage: Optional[float]
    convergence_flag: bool
    
    # Data quality metrics
    data_quality_score: float
    missing_data_fraction: float
    outlier_fraction: float
    stationarity_p_value: Optional[float]
    
    # Method-specific metrics
    regression_r_squared: Optional[float]
    scaling_range: Optional[Tuple[int, int]]
    goodness_of_fit: Optional[float]
    
    # Biomedical-specific
    signal_to_noise_ratio: Optional[float]
    artifact_detection: Dict[str, Any]
```

**Methods:**

##### to_dict()

```python
def to_dict(self) -> Dict[str, Any]
```

**Returns:**
- `dict`: Serializable dictionary representation

**Example:**
```python
result = factory.estimate(data, 'dfa')
result_dict = result.to_dict()

# Access key metrics
print(f"Hurst: {result.hurst_estimate:.3f}")
print(f"Quality: {result.data_quality_score:.3f}")
print(f"Computation time: {result.computation_time:.3f}s")
print(f"95% CI: {result.confidence_interval}")
```

#### GroupHurstResult

**Results container for group estimation with multiple methods.**

```python
@dataclass
class GroupHurstResult:
    individual_results: List[HurstResult]
    ensemble_estimate: float
    ensemble_confidence_interval: Tuple[float, float]
    method_agreement: float
    best_method: str
    consensus_estimate: float
    weighted_estimate: float
    total_computation_time: float
```

**Methods:**

##### to_dict()

```python
def to_dict(self) -> Dict[str, Any]
```

**Example:**
```python
group_result = factory.estimate(data, EstimatorType.ALL)

print(f"Ensemble: {group_result.ensemble_estimate:.3f}")
print(f"Consensus: {group_result.consensus_estimate:.3f}")
print(f"Best method: {group_result.best_method}")
print(f"Agreement: {group_result.method_agreement:.3f}")

# Access individual results
for result in group_result.individual_results:
    print(f"{result.estimator_name}: {result.hurst_estimate:.3f}")
```

---

## Configuration

### Method-Specific Parameters

#### DFA Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_window` | int | `max(10, n//100)` | Minimum window size |
| `max_window` | int | `min(n//4, 500)` | Maximum window size |
| `polynomial_order` | int | 1 | Polynomial detrending order |
| `overlap` | float | 0.5 | Window overlap fraction |

#### Higuchi Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `kmax` | int | `min(20, n//10)` | Maximum k parameter |

#### Periodogram Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `low_freq_fraction` | float | 0.1 | Low frequency fraction |
| `high_freq_cutoff` | float | 0.4 | High frequency cutoff |

### Bootstrap Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `n_bootstrap` | int | 100 | Number of bootstrap samples |
| `confidence_level` | float | 0.95 | Confidence level |
| `random_state` | int | None | Random seed |

### Preprocessing Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `handle_missing` | str | 'interpolate' | Missing data strategy |
| `remove_outliers` | bool | True | Remove outliers |
| `detrend` | bool | True | Remove linear trend |
| `filter_artifacts` | bool | True | Filter artifacts |

---

## Examples

### Basic Usage

```python
import numpy as np
from biomedical_hurst_factory import BiomedicalHurstEstimatorFactory, EstimatorType

# Create factory
factory = BiomedicalHurstEstimatorFactory()

# Generate sample data (random walk)
data = np.cumsum(np.random.randn(1000))

# Single method estimation
result = factory.estimate(data, EstimatorType.DFA)
print(f"Hurst exponent: {result.hurst_estimate:.3f}")
```

### EEG Signal Analysis

```python
# EEG-specific configuration
eeg_result = factory.estimate(
    eeg_signal,
    method=EstimatorType.DFA,
    confidence_method=ConfidenceMethod.BOOTSTRAP,
    
    # Preprocessing for EEG
    handle_missing='interpolate',
    remove_outliers=True,
    detrend=False,  # Preserve EEG dynamics
    filter_artifacts=True,
    
    # DFA parameters for EEG
    min_window=20,      # Suitable for EEG sampling rates
    max_window=500,
    polynomial_order=2, # Quadratic detrending for EEG
    overlap=0.75,       # High overlap for better statistics
    
    # Bootstrap parameters
    n_bootstrap=500,
    confidence_level=0.99,
    random_state=42
)

print(f"EEG Hurst exponent: {eeg_result.hurst_estimate:.3f}")
print(f"99% CI: [{eeg_result.confidence_interval[0]:.3f}, {eeg_result.confidence_interval[1]:.3f}]")
print(f"Data quality: {eeg_result.data_quality_score:.3f}")
print(f"SNR: {eeg_result.signal_to_noise_ratio:.1f} dB")
```

### ECG Heart Rate Variability

```python
# ECG R-R interval analysis
ecg_result = factory.estimate(
    rr_intervals,
    method=EstimatorType.DFA,
    
    # ECG-specific preprocessing
    handle_missing='forward_fill',  # Appropriate for R-R intervals
    remove_outliers=True,
    detrend=False,  # Preserve cardiac dynamics
    
    # DFA parameters for HRV
    min_window=10,
    max_window=200,
    polynomial_order=1,  # Linear detrending for HRV
    
    # Statistical confidence
    confidence_method=ConfidenceMethod.BOOTSTRAP,
    n_bootstrap=200
)

print(f"HRV Hurst exponent: {ecg_result.hurst_estimate:.3f}")
```

### Group Estimation with Method Comparison

```python
# Compare all available methods
group_result = factory.estimate(
    physiological_signal,
    method=EstimatorType.ALL,
    confidence_method=ConfidenceMethod.BOOTSTRAP,
    n_bootstrap=100
)

print("Method Comparison Results:")
print(f"Ensemble estimate: {group_result.ensemble_estimate:.3f}")
print(f"Consensus estimate: {group_result.consensus_estimate:.3f}")
print(f"Best method: {group_result.best_method}")
print(f"Method agreement: {group_result.method_agreement:.3f}")

# Individual method results
for result in group_result.individual_results:
    print(f"{result.estimator_name:12}: {result.hurst_estimate:.3f} "
          f"(R² = {result.regression_r_squared:.3f})")
```

### Real-time Monitoring

```python
class RealTimeHurstMonitor:
    def __init__(self, window_size=1000, update_interval=100):
        self.factory = BiomedicalHurstEstimatorFactory()
        self.window_size = window_size
        self.update_interval = update_interval
        self.buffer = []
        self.estimates = []
        
    def add_sample(self, value):
        self.buffer.append(value)
        
        # Maintain sliding window
        if len(self.buffer) > self.window_size:
            self.buffer.pop(0)
        
        # Update estimate periodically
        if (len(self.buffer) >= self.window_size and 
            len(self.buffer) % self.update_interval == 0):
            
            result = self.factory.estimate(
                np.array(self.buffer),
                method=EstimatorType.HIGUCHI,  # Fast method
                confidence_method=ConfidenceMethod.NONE,
                preprocess=True
            )
            
            self.estimates.append({
                'timestamp': len(self.estimates),
                'hurst': result.hurst_estimate,
                'quality': result.data_quality_score,
                'computation_time': result.computation_time
            })
            
            return result
        
        return None

# Usage
monitor = RealTimeHurstMonitor()
for sample in streaming_data:
    result = monitor.add_sample(sample)
    if result:
        print(f"Real-time H: {result.hurst_estimate:.3f}, "
              f"Quality: {result.data_quality_score:.3f}")
```

### Batch Processing

```python
def batch_hurst_analysis(data_files, output_file):
    """Process multiple data files and save results"""
    factory = BiomedicalHurstEstimatorFactory()
    results = []
    
    for file_path in data_files:
        # Load data
        data = np.loadtxt(file_path)
        
        # Analyze with multiple methods
        group_result = factory.estimate(
            data, 
            EstimatorType.ALL,
            assess_quality=True
        )
        
        # Store results
        results.append({
            'file': file_path,
            'ensemble_hurst': group_result.ensemble_estimate,
            'best_method': group_result.best_method,
            'method_agreement': group_result.method_agreement,
            'data_quality': group_result.individual_results[0].data_quality_score,
            'computation_time': group_result.total_computation_time
        })
    
    # Save results
    import pandas as pd
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    
    return df

# Usage
results_df = batch_hurst_analysis(
    ['eeg_patient1.txt', 'eeg_patient2.txt', 'eeg_patient3.txt'],
    'hurst_analysis_results.csv'
)
```

---

## Error Handling

### Exception Types

#### ValueError
- Invalid method name
- Invalid parameter values
- Insufficient data length
- Invalid confidence level

#### TypeError
- Wrong data type for input parameters
- Non-numeric data

#### RuntimeError
- Estimation convergence failure
- Numerical instability

### Error Handling Patterns

```python
from biomedical_hurst_factory import BiomedicalHurstEstimatorFactory, EstimatorType

factory = BiomedicalHurstEstimatorFactory()

try:
    result = factory.estimate(data, EstimatorType.DFA)
    
    # Check convergence
    if not result.convergence_flag:
        print("Warning: Estimation may not have converged properly")
        print(f"R-squared: {result.regression_r_squared:.3f}")
    
    # Check data quality
    if result.data_quality_score < 0.5:
        print("Warning: Poor data quality detected")
        print(f"Quality score: {result.data_quality_score:.3f}")
    
    # Use results
    print(f"Hurst exponent: {result.hurst_estimate:.3f}")
    
except ValueError as e:
    print(f"Parameter error: {e}")
    
except RuntimeError as e:
    print(f"Computation error: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Robust Error Handling

```python
def robust_hurst_estimation(data, methods=None):
    """Robust estimation with fallback methods"""
    
    if methods is None:
        methods = [EstimatorType.DFA, EstimatorType.HIGUCHI, EstimatorType.PERIODOGRAM]
    
    factory = BiomedicalHurstEstimatorFactory()
    results = []
    
    for method in methods:
        try:
            result = factory.estimate(data, method)
            
            if (result.convergence_flag and 
                0.01 <= result.hurst_estimate <= 0.99 and
                result.data_quality_score > 0.3):
                results.append(result)
                
        except Exception as e:
            print(f"Method {method} failed: {e}")
            continue
    
    if not results:
        raise RuntimeError("All estimation methods failed")
    
    # Return best result based on quality metrics
    best_result = max(results, key=lambda r: (
        r.convergence_flag,
        r.regression_r_squared or 0,
        r.data_quality_score
    ))
    
    return best_result, results

# Usage
try:
    best_result, all_results = robust_hurst_estimation(noisy_data)
    print(f"Best estimate: {best_result.hurst_estimate:.3f}")
    print(f"Method: {best_result.estimator_name}")
    print(f"Successful methods: {len(all_results)}")
    
except RuntimeError as e:
    print(f"All methods failed: {e}")
```

---

## Best Practices

### Data Preparation

```python
# 1. Check data quality before estimation
quality = BiomedicalDataProcessor.assess_data_quality(raw_data)
if quality['data_quality_score'] < 0.5:
    print("Consider data cleaning or different acquisition")

# 2. Appropriate preprocessing for signal type
if signal_type == 'EEG':
    # EEG-specific preprocessing
    result = factory.estimate(
        data,
        method=EstimatorType.DFA,
        handle_missing='interpolate',
        remove_outliers=True,
        detrend=False,  # Preserve neural dynamics
        filter_artifacts=True
    )
elif signal_type == 'ECG':
    # ECG-specific preprocessing
    result = factory.estimate(
        data,
        method=EstimatorType.DFA,
        handle_missing='forward_fill',
        remove_outliers=True,
        detrend=False   # Preserve cardiac dynamics
    )
```

### Method Selection

```python
# 1. Choose method based on data characteristics
def select_optimal_method(data):
    n = len(data)
    quality = BiomedicalDataProcessor.assess_data_quality(data)
    
    if n < 200:
        return EstimatorType.HIGUCHI  # Works with shorter data
    elif quality['data_quality_score'] < 0.6:
        return EstimatorType.DFA      # More robust to noise
    elif n > 5000:
        return EstimatorType.HIGUCHI  # Computationally efficient
    else:
        return EstimatorType.DFA      # Generally most accurate

# 2. Use group estimation for critical applications
critical_result = factory.estimate(data, EstimatorType.ALL)
if critical_result.method_agreement < 0.7:
    print("Warning: Methods disagree - investigate data quality")
```

### Parameter Optimization

```python
# 1. Optimize DFA parameters for your data
def optimize_dfa_parameters(data):
    factory = BiomedicalHurstEstimatorFactory()
    best_r_squared = 0
    best_params = {}
    
    # Test different parameter combinations
    for poly_order in [1, 2]:
        for min_win_frac in [0.02, 0.05, 0.1]:
            for max_win_frac in [0.2, 0.25, 0.3]:
                try:
                    result = factory.estimate(
                        data,
                        EstimatorType.DFA,
                        min_window=int(len(data) * min_win_frac),
                        max_window=int(len(data) * max_win_frac),
                        polynomial_order=poly_order
                    )
                    
                    if (result.convergence_flag and 
                        result.regression_r_squared > best_r_squared):
                        best_r_squared = result.regression_r_squared
                        best_params = {
                            'polynomial_order': poly_order,
                            'min_window': int(len(data) * min_win_frac),
                            'max_window': int(len(data) * max_win_frac)
                        }
                except:
                    continue
    
    return best_params

# Usage
optimal_params = optimize_dfa_parameters(data)
result = factory.estimate(data, EstimatorType.DFA, **optimal_params)
```

### Statistical Validation

```python
# 1. Always check confidence intervals
result = factory.estimate(
    data, 
    EstimatorType.DFA,
    confidence_method=ConfidenceMethod.BOOTSTRAP,
    n_bootstrap=200
)

ci_width = result.confidence_interval[1] - result.confidence_interval[0]
if ci_width > 0.3:
    print("Warning: Large confidence interval - consider more data")

# 2. Validate with multiple methods
def validate_hurst_estimate(data):
    group_result = factory.estimate(data, EstimatorType.ALL)
    
    estimates = [r.hurst_estimate for r in group_result.individual_results 
                if r.convergence_flag]
    
    if len(estimates) >= 2:
        std_estimates = np.std(estimates)
        if std_estimates > 0.2:
            print(f"Warning: Methods disagree (std = {std_estimates:.3f})")
            return False
    
    return True

# Usage
if validate_hurst_estimate(data):
    print("Hurst estimate validated across methods")
else:
    print("Consider data quality or method-specific issues")
```

### Performance Optimization

```python
# 1. For real-time applications
def real_time_estimation(data):
    # Use fastest method with minimal bootstrap
    return factory.estimate(
        data,
        method=EstimatorType.HIGUCHI,
        confidence_method=ConfidenceMethod.THEORETICAL,  # Faster than bootstrap
        preprocess=True,
        assess_quality=False  # Skip if performance critical
    )

# 2. For batch processing
def batch_estimation(data_list):
    # Use group estimation for thorough analysis
    results = []
    for data in data_list:
        result = factory.estimate(
            data,
            method=EstimatorType.ALL,
            confidence_method=ConfidenceMethod.BOOTSTRAP,
            n_bootstrap=100  # Balance accuracy vs speed
        )
        results.append(result)
    return results
```

---

## Quick Reference

### Import Statements

```python
# Main factory class
from biomedical_hurst_factory import BiomedicalHurstEstimatorFactory

# Enums and types
from biomedical_hurst_factory import EstimatorType, ConfidenceMethod

# Result classes
from biomedical_hurst_factory import HurstResult, GroupHurstResult

# Individual estimators
from biomedical_hurst_factory import DFAEstimator, HiguchiEstimator, PeriodogramEstimator

# Utility classes
from biomedical_hurst_factory import BiomedicalDataProcessor, ConfidenceEstimator
```

### Common Usage Patterns

```python
# Basic estimation
factory = BiomedicalHurstEstimatorFactory()
result = factory.estimate(data, 'dfa')
print(f"H = {result.hurst_estimate:.3f}")

# With confidence intervals
result = factory.estimate(data, 'dfa', confidence_method='bootstrap')
print(f"H = {result.hurst_estimate:.3f} [{result.confidence_interval[0]:.3f}, {result.confidence_interval[1]:.3f}]")

# Group estimation
group_result = factory.estimate(data, 'all')
print(f"Ensemble H = {group_result.ensemble_estimate:.3f}")

# Custom parameters
result = factory.estimate(data, 'dfa', min_window=20, polynomial_order=2)
```

### Method Selection Guide

| Data Type | Recommended Method | Parameters |
|-----------|-------------------|------------|
| **EEG** | DFA | `polynomial_order=2`, `min_window=20` |
| **ECG/HRV** | DFA | `polynomial_order=1`, detrend=False |
| **Short series (<200)** | Higuchi | `kmax=10` |
| **Real-time** | Higuchi | Default parameters |
| **Noisy data** | DFA | `polynomial_order=2`, high bootstrap |
| **Research/Critical** | ALL | Group estimation |

### Performance Guidelines

| Data Length | Method | Expected Time | Memory Usage |
|-------------|--------|---------------|--------------|
| 100-500 | Higuchi | <0.1s | <10MB |
| 500-2000 | DFA | <1s | <50MB |
| 2000-5000 | DFA | <5s | <100MB |
| >5000 | Higuchi (fast) | <2s | <100MB |

### Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| `ValueError: Data too short` | Insufficient data | Use longer time series or Higuchi method |
| `H estimate > 0.9 or < 0.1` | Data issues or method failure | Check data quality, try different method |
| Poor `regression_r_squared` | Wrong parameters or noisy data | Optimize parameters, preprocess data |
| `convergence_flag = False` | Numerical issues | Try different method or parameters |
| Large confidence intervals | High uncertainty | Collect more data or improve preprocessing |

---

## Changelog

### Version 1.0.0 (October 2025)
- Initial release
- Complete factory implementation with DFA, Higuchi, and Periodogram methods
- Bootstrap and theoretical confidence intervals
- Biomedical-specific preprocessing and quality assessment
- Comprehensive test suite and validation
- Full API documentation

---

## License

MIT License - see LICENSE file for details.

## Citation

If you use this library in your research, please cite:

```bibtex
@software{biomedical_hurst_factory,
  title={Biomedical Hurst Exponent Estimation Factory},
  author={AI Assistant},
  year={2025},
  version={1.0.0},
  url={https://github.com/example/biomedical-hurst-factory}
}
```

---

**For additional support, examples, and updates, visit the project documentation and repository.**