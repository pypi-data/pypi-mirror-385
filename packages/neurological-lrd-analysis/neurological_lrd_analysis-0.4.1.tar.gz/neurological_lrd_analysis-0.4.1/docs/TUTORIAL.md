# Biomedical Hurst Factory - Tutorial Guide

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Basic Usage](#basic-usage)
3. [Understanding Hurst Exponents](#understanding-hurst-exponents)
4. [Choosing the Right Estimator](#choosing-the-right-estimator)
5. [Data Preprocessing](#data-preprocessing)
6. [Advanced Features](#advanced-features)
7. [Performance Optimization](#performance-optimization)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

## Installation and Setup

### Prerequisites

- Python 3.11 or higher
- Basic understanding of time series analysis
- Familiarity with NumPy and pandas

### Quick Setup

```bash
# Clone the repository
git clone <repository-url>
cd long_range_dependence

# Set up virtual environment
./setup_venv.sh

# Activate environment
source biomedical_hurst_env/bin/activate

# Verify installation
python -c "from biomedical_hurst_factory import BiomedicalHurstEstimatorFactory; print('Installation successful!')"
```

### Manual Setup

```bash
# Create virtual environment
python3 -m venv biomedical_hurst_env
source biomedical_hurst_env/bin/activate

# Install dependencies
pip install -e .

# Install optional dependencies
pip install jax jaxlib numba pywavelets scikit-learn matplotlib seaborn
```

## Basic Usage

### Your First Hurst Estimation

```python
import numpy as np
from biomedical_hurst_factory import BiomedicalHurstEstimatorFactory, EstimatorType

# Generate sample data (fractional Brownian motion)
np.random.seed(42)
n = 1000
hurst_true = 0.7
data = np.cumsum(np.random.randn(n) * 0.1)  # Simplified fBm

# Create factory instance
factory = BiomedicalHurstEstimatorFactory()

# Estimate Hurst exponent using DFA
result = factory.estimate(data, EstimatorType.DFA)

# Display results
print(f"Estimated Hurst exponent: {result.hurst_estimate:.3f}")
print(f"Confidence interval: [{result.confidence_interval[0]:.3f}, {result.confidence_interval[1]:.3f}]")
print(f"Data quality score: {result.data_quality_score:.3f}")
print(f"Computation time: {result.computation_time:.3f} seconds")
```

### Comparing Multiple Methods

```python
# Compare all available methods
group_result = factory.estimate(data, EstimatorType.ALL)

print(f"Ensemble estimate: {group_result.ensemble_estimate:.3f}")
print(f"Best method: {group_result.best_method}")
print(f"Method agreement: {group_result.method_agreement:.3f}")

# Display individual results
for result in group_result.individual_results:
    print(f"{result.estimator_name:15s}: {result.hurst_estimate:.3f} ± {result.standard_error:.3f}")
```

## Understanding Hurst Exponents

### What is the Hurst Exponent?

The Hurst exponent (H) is a measure of long-range dependence in time series data:

- **H = 0.5**: Random walk (no long-range dependence)
- **H > 0.5**: Persistent behavior (trends tend to continue)
- **H < 0.5**: Anti-persistent behavior (trends tend to reverse)

### Interpretation in Biomedical Context

- **EEG signals**: H ≈ 0.5-0.8 (brain activity shows persistence)
- **Heart rate variability**: H ≈ 0.5-0.7 (healthy heart shows some persistence)
- **Blood pressure**: H ≈ 0.5-0.6 (regulatory mechanisms)
- **Respiratory signals**: H ≈ 0.5-0.8 (breathing patterns)

### Example: Different Hurst Values

```python
import matplotlib.pyplot as plt

# Generate data with different Hurst values
hurst_values = [0.3, 0.5, 0.7]
fig, axes = plt.subplots(3, 1, figsize=(12, 8))

for i, h in enumerate(hurst_values):
    # Generate fBm-like data
    np.random.seed(42)
    if h == 0.5:
        data = np.cumsum(np.random.randn(500))
    else:
        # Simplified fBm generation
        data = np.cumsum(np.random.randn(500) * (h - 0.5 + 0.1))
    
    axes[i].plot(data)
    axes[i].set_title(f'Hurst ≈ {h} - {"Anti-persistent" if h < 0.5 else "Random" if h == 0.5 else "Persistent"}')
    axes[i].set_ylabel('Value')

plt.xlabel('Time')
plt.tight_layout()
plt.show()
```

## Choosing the Right Estimator

### Estimator Categories

#### 1. Temporal Methods
- **DFA**: Robust, works well with trends
- **R/S Analysis**: Classic method, sensitive to trends
- **Higuchi**: Good for short time series
- **GHE**: Generalized approach, flexible

#### 2. Spectral Methods
- **Periodogram**: Fast, good for stationary data
- **GPH**: Robust to trends, good for long series
- **Whittle MLE**: Maximum likelihood, statistically optimal

#### 3. Wavelet Methods
- **DWT**: Good time-frequency localization
- **NDWT**: Better for non-stationary data
- **Abry-Veitch**: Robust wavelet method

#### 4. Multifractal Methods
- **MFDFA**: Captures multifractal properties
- **MF-DMA**: Alternative to MFDFA

### Selection Guide

```python
def choose_estimator(data_length, data_type, has_trends=False):
    """Guide for choosing the right estimator."""
    
    if data_length < 100:
        return EstimatorType.HIGUCHI
    elif data_length < 500:
        if has_trends:
            return EstimatorType.DFA
        else:
            return EstimatorType.PERIODOGRAM
    else:
        if has_trends:
            return EstimatorType.DFA
        elif data_type == 'stationary':
            return EstimatorType.WHITTLE_MLE
        else:
            return EstimatorType.ABRY_VEITCH

# Example usage
data_length = len(your_data)
estimator = choose_estimator(data_length, 'non-stationary', has_trends=True)
result = factory.estimate(your_data, estimator)
```

### Method Comparison Example

```python
# Compare methods for your specific data
methods_to_compare = [
    EstimatorType.DFA,
    EstimatorType.PERIODOGRAM,
    EstimatorType.WHITTLE_MLE,
    EstimatorType.ABRY_VEITCH
]

results = {}
for method in methods_to_compare:
    try:
        result = factory.estimate(data, method)
        results[method.value] = {
            'hurst': result.hurst_estimate,
            'ci': result.confidence_interval,
            'r_squared': result.regression_r_squared,
            'time': result.computation_time
        }
    except Exception as e:
        print(f"Method {method.value} failed: {e}")

# Display comparison
print("Method Comparison:")
print("-" * 50)
for method, metrics in results.items():
    print(f"{method:15s}: H={metrics['hurst']:.3f}, R²={metrics['r_squared']:.3f}, Time={metrics['time']:.3f}s")
```

## Data Preprocessing

### Quality Assessment

```python
from biomedical_hurst_factory import BiomedicalDataProcessor

processor = BiomedicalDataProcessor()

# Assess data quality
quality_metrics = processor.assess_data_quality(data)

print("Data Quality Assessment:")
print(f"Overall score: {quality_metrics['data_quality_score']:.3f}")
print(f"Missing data: {quality_metrics['missing_data_fraction']:.1%}")
print(f"Outliers: {quality_metrics['outlier_fraction']:.1%}")
print(f"SNR: {quality_metrics.get('signal_to_noise_ratio', 'N/A')} dB")
print(f"Stationarity p-value: {quality_metrics.get('stationarity_p_value', 'N/A')}")
```

### Preprocessing Options

```python
# Basic preprocessing
processed_data, log = processor.preprocess_biomedical_data(
    data,
    handle_missing='interpolate',  # or 'remove', 'forward_fill'
    remove_outliers=True,
    detrend=True,
    filter_artifacts=True
)

print("Preprocessing log:")
for key, value in log.items():
    print(f"  {key}: {value}")

# Advanced preprocessing with convergence trimming
processed_data, log = processor.preprocess_biomedical_data(
    data,
    trim_convergence=True,
    stability_threshold=0.05,
    min_stable_fraction=0.1
)
```

### Handling Missing Data

```python
# Example with missing data
data_with_missing = data.copy()
data_with_missing[100:110] = np.nan  # Add missing values

# Different handling strategies
strategies = ['interpolate', 'remove', 'forward_fill']
results = {}

for strategy in strategies:
    processed, _ = processor.preprocess_biomedical_data(
        data_with_missing,
        handle_missing=strategy
    )
    
    result = factory.estimate(processed, EstimatorType.DFA)
    results[strategy] = result.hurst_estimate

print("Missing data handling comparison:")
for strategy, hurst in results.items():
    print(f"  {strategy}: H = {hurst:.3f}")
```

## Advanced Features

### Custom Confidence Intervals

```python
from biomedical_hurst_factory import ConfidenceMethod

# Bootstrap confidence intervals
result = factory.estimate(
    data,
    EstimatorType.DFA,
    confidence_method=ConfidenceMethod.BOOTSTRAP,
    confidence_level=0.99,
    n_bootstrap=1000
)

# Theoretical confidence intervals
result = factory.estimate(
    data,
    EstimatorType.DFA,
    confidence_method=ConfidenceMethod.THEORETICAL,
    confidence_level=0.95
)
```

### Method-Specific Parameters

```python
# DFA with custom parameters
result = factory.estimate(
    data,
    EstimatorType.DFA,
    min_window=20,
    max_window=200,
    polynomial_order=2,
    overlap=0.3
)

# Wavelet methods with custom parameters
result = factory.estimate(
    data,
    EstimatorType.DWT,
    wavelet='db8',
    max_level=6
)

# Multifractal methods
result = factory.estimate(
    data,
    EstimatorType.MFDFA,
    q=2.0,
    min_window=50,
    max_window=500
)
```

### Batch Processing

```python
# Process multiple time series
time_series_list = [data1, data2, data3]
results = []

for i, ts in enumerate(time_series_list):
    result = factory.estimate(ts, EstimatorType.DFA)
    results.append({
        'series_id': i,
        'hurst': result.hurst_estimate,
        'ci': result.confidence_interval,
        'quality': result.data_quality_score
    })

# Convert to DataFrame for analysis
import pandas as pd
df = pd.DataFrame(results)
print(df)
```

## Performance Optimization

### Lazy Loading

The library uses lazy loading for heavy dependencies:

```python
# Heavy modules are loaded only when needed
# This reduces startup time and memory usage

# First use of wavelet methods loads PyWavelets
result = factory.estimate(data, EstimatorType.DWT)

# First use of optimization loads scipy.optimize
result = factory.estimate(data, EstimatorType.WHITTLE_MLE)
```

### Memory Management

```python
# For large datasets, consider chunking
def process_large_dataset(data, chunk_size=10000):
    results = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        result = factory.estimate(chunk, EstimatorType.DFA)
        results.append(result.hurst_estimate)
    return results

# Process in chunks
large_data = np.random.randn(100000)
chunk_results = process_large_dataset(large_data)
```

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp

def estimate_hurst_parallel(data, method):
    return factory.estimate(data, method)

# Parallel estimation of multiple methods
methods = [EstimatorType.DFA, EstimatorType.PERIODOGRAM, EstimatorType.WHITTLE_MLE]

with ThreadPoolExecutor(max_workers=mp.cpu_count()) as executor:
    futures = [executor.submit(estimate_hurst_parallel, data, method) for method in methods]
    results = [future.result() for future in futures]

for result in results:
    print(f"{result.estimator_name}: {result.hurst_estimate:.3f}")
```

## Troubleshooting

### Common Issues

#### 1. "Data too short" Error

```python
# Minimum data length requirements
min_lengths = {
    'DFA': 50,
    'Higuchi': 20,
    'Periodogram': 100,
    'R/S': 50,
    'GPH': 100,
    'Whittle MLE': 100,
    'GHE': 50,
    'DWT': 100,
    'Abry-Veitch': 100,
    'NDWT': 100,
    'MFDFA': 50,
    'MF-DMA': 50
}

# Check data length
if len(data) < min_lengths['DFA']:
    print(f"Data too short for DFA. Minimum: {min_lengths['DFA']}, Got: {len(data)}")
```

#### 2. "Insufficient valid windows" Error

```python
# Adjust window parameters for short data
if len(data) < 500:
    result = factory.estimate(
        data,
        EstimatorType.DFA,
        min_window=10,
        max_window=len(data)//4
    )
```

#### 3. "Too many missing values" Error

```python
# Check missing data fraction
missing_fraction = np.sum(np.isnan(data)) / len(data)
if missing_fraction > 0.2:
    print(f"Too many missing values: {missing_fraction:.1%}")
    # Consider different handling strategy
    processed, _ = processor.preprocess_biomedical_data(
        data,
        handle_missing='remove'  # or 'forward_fill'
    )
```

#### 4. Convergence Issues

```python
# Check convergence flags
result = factory.estimate(data, EstimatorType.DFA)
if not result.convergence_flag:
    print("Method did not converge. Try:")
    print("1. Different window parameters")
    print("2. Data preprocessing")
    print("3. Alternative method")
    
    # Try with different parameters
    result = factory.estimate(
        data,
        EstimatorType.DFA,
        min_window=20,
        max_window=100,
        polynomial_order=1
    )
```

### Debugging Tips

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check data quality
quality = processor.assess_data_quality(data)
if quality['data_quality_score'] < 0.5:
    print("Poor data quality detected")
    print(f"Missing: {quality['missing_data_fraction']:.1%}")
    print(f"Outliers: {quality['outlier_fraction']:.1%}")

# Test with synthetic data
synthetic_data = np.cumsum(np.random.randn(1000))
result = factory.estimate(synthetic_data, EstimatorType.DFA)
print(f"Synthetic test: H = {result.hurst_estimate:.3f}")
```

## Best Practices

### 1. Data Preparation

```python
# Always assess data quality first
quality = processor.assess_data_quality(data)
if quality['data_quality_score'] < 0.7:
    print("Warning: Poor data quality")

# Preprocess data appropriately
processed_data, log = processor.preprocess_biomedical_data(
    data,
    handle_missing='interpolate',
    remove_outliers=True,
    detrend=True,
    filter_artifacts=True
)
```

### 2. Method Selection

```python
# Use multiple methods for robust estimation
methods = [EstimatorType.DFA, EstimatorType.PERIODOGRAM, EstimatorType.WHITTLE_MLE]
results = []

for method in methods:
    try:
        result = factory.estimate(processed_data, method)
        if result.convergence_flag and result.regression_r_squared > 0.7:
            results.append(result)
    except Exception as e:
        print(f"Method {method.value} failed: {e}")

# Use ensemble estimate
if results:
    ensemble_hurst = np.mean([r.hurst_estimate for r in results])
    print(f"Ensemble estimate: {ensemble_hurst:.3f}")
```

### 3. Validation

```python
# Validate results
def validate_hurst_estimate(result):
    """Validate Hurst estimate results."""
    checks = []
    
    # Check convergence
    checks.append(("Convergence", result.convergence_flag))
    
    # Check R-squared
    if result.regression_r_squared:
        checks.append(("R-squared > 0.7", result.regression_r_squared > 0.7))
    
    # Check confidence interval width
    ci_width = result.confidence_interval[1] - result.confidence_interval[0]
    checks.append(("CI width < 0.3", ci_width < 0.3))
    
    # Check data quality
    checks.append(("Quality > 0.5", result.data_quality_score > 0.5))
    
    return checks

# Validate result
checks = validate_hurst_estimate(result)
for check_name, passed in checks:
    status = "✓" if passed else "✗"
    print(f"{status} {check_name}")
```

### 4. Reporting

```python
def generate_report(data, result):
    """Generate a comprehensive report."""
    report = f"""
Hurst Exponent Analysis Report
=============================

Data Information:
- Length: {len(data)}
- Mean: {np.mean(data):.3f}
- Std: {np.std(data):.3f}
- Quality Score: {result.data_quality_score:.3f}

Estimation Results:
- Method: {result.estimator_name}
- Hurst Exponent: {result.hurst_estimate:.3f}
- Confidence Interval: [{result.confidence_interval[0]:.3f}, {result.confidence_interval[1]:.3f}]
- Standard Error: {result.standard_error:.3f}
- Computation Time: {result.computation_time:.3f}s

Quality Metrics:
- Convergence: {'Yes' if result.convergence_flag else 'No'}
- R-squared: {result.regression_r_squared:.3f if result.regression_r_squared else 'N/A'}
- Missing Data: {result.missing_data_fraction:.1%}
- Outliers: {result.outlier_fraction:.1%}

Interpretation:
- H = {result.hurst_estimate:.3f} indicates {'persistent' if result.hurst_estimate > 0.5 else 'anti-persistent' if result.hurst_estimate < 0.5 else 'random'} behavior
- {'High' if result.data_quality_score > 0.8 else 'Moderate' if result.data_quality_score > 0.6 else 'Low'} data quality
"""
    return report

# Generate and print report
report = generate_report(data, result)
print(report)
```

### 5. Reproducibility

```python
# Set random seeds for reproducibility
np.random.seed(42)

# Use consistent parameters
default_params = {
    'confidence_method': ConfidenceMethod.BOOTSTRAP,
    'confidence_level': 0.95,
    'n_bootstrap': 100,
    'preprocess': True,
    'assess_quality': True
}

# Save results with metadata
import json
from datetime import datetime

result_data = {
    'timestamp': datetime.now().isoformat(),
    'data_length': len(data),
    'method': result.estimator_name,
    'hurst_estimate': result.hurst_estimate,
    'confidence_interval': result.confidence_interval,
    'parameters': default_params,
    'quality_score': result.data_quality_score
}

# Save to file
with open('hurst_analysis_results.json', 'w') as f:
    json.dump(result_data, f, indent=2)
```

This tutorial provides a comprehensive guide to using the Biomedical Hurst Factory. For more advanced topics and specific use cases, refer to the API Reference and the project documentation.

