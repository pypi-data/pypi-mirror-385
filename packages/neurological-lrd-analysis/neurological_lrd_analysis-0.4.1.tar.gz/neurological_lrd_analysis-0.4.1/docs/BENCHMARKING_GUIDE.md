# Enhanced Benchmarking Guide

## Overview

The Biomedical Hurst Factory now includes comprehensive benchmarking capabilities with detailed statistical reporting. This guide explains how to use the enhanced benchmarking system to evaluate estimator performance with bias, error, confidence intervals, and p-value analysis.

## Enhanced Statistical Metrics

The benchmarking system now reports comprehensive statistical metrics for each estimator:

### Core Metrics
- **Bias**: Systematic error (estimate - true_value)
- **Absolute Error**: |estimate - true_value|
- **Relative Error**: Absolute error / true_value
- **Root Mean Square Error (RMSE)**: √(mean(bias²))
- **Standard Error**: Standard deviation of estimates
- **Confidence Interval**: Statistical confidence bounds
- **P-value**: Statistical significance of regression fit

### Performance Metrics
- **Success Rate**: Percentage of successful estimations
- **Computation Time**: Average time per estimation
- **Convergence Flag**: Whether the method converged
- **Significance Rate**: Percentage of statistically significant estimates

## Usage Examples

### Basic Enhanced Benchmarking

#### Using the Command Line Script

```bash
# Run benchmark with default settings
python run_benchmark.py

# Customize benchmark parameters
python run_benchmark.py --hurst-values 0.3,0.5,0.7,0.8 --lengths 512,1024,2048 --output-dir ./my_results

# Quick test with fewer samples
python run_benchmark.py --hurst-values 0.5,0.7 --lengths 512 --bootstrap 50
```

#### Using the Python API

```python
from benchmark_core.generation import generate_grid
from benchmark_core.runner import BenchmarkConfig, run_benchmark_on_dataset, analyze_benchmark_results, create_leaderboard

# Generate test datasets
datasets = generate_grid(
    hurst_values=[0.3, 0.5, 0.7, 0.8],
    lengths=[512, 1024, 2048],
    contaminations=['none', 'noise'],
    contamination_level=0.1,
    seed=42
)

# Configure benchmark
config = BenchmarkConfig(
    output_dir='./benchmark_results',
    n_bootstrap=100,
    confidence_level=0.95,
    save_results=True,
    verbose=False
)

# Run benchmark
results = run_benchmark_on_dataset(datasets, config)

# Analyze results
analysis = analyze_benchmark_results(results)
leaderboard = create_leaderboard(results)

print("Enhanced Benchmarking Results:")
print(leaderboard.to_string(index=False))
```

### Comprehensive Statistical Analysis

```python
# Detailed analysis
for estimator, metrics in analysis.items():
    print(f"\n{estimator}:")
    print(f"  Success Rate: {metrics['success_rate']:.1%}")
    print(f"  Mean Bias: {metrics['mean_bias']:.4f}")
    print(f"  Std Bias: {metrics['std_bias']:.4f}")
    print(f"  Mean Absolute Error: {metrics['mean_absolute_error']:.4f}")
    print(f"  RMSE: {metrics['rmse']:.4f}")
    print(f"  Mean Relative Error: {metrics['mean_relative_error']:.1%}")
    print(f"  Significance Rate: {metrics['significance_rate']:.1%}")
    print(f"  Mean Computation Time: {metrics['mean_computation_time']:.4f}s")
```

### Bias Analysis by Hurst Value

```python
# Analyze bias patterns by true Hurst value
hurst_values = sorted(set(r.true_hurst for r in results if r.true_hurst is not None))

for hurst in hurst_values:
    print(f"\nHurst = {hurst}:")
    hurst_results = [r for r in results if r.true_hurst == hurst and r.convergence_flag and r.bias is not None]
    
    if hurst_results:
        biases = [r.bias for r in hurst_results]
        print(f"  Total estimates: {len(hurst_results)}")
        print(f"  Mean bias: {np.mean(biases):.4f}")
        print(f"  Std bias: {np.std(biases):.4f}")
        print(f"  Min bias: {np.min(biases):.4f}")
        print(f"  Max bias: {np.max(biases):.4f}")
```

## Benchmark Configuration Options

### BenchmarkConfig Parameters

```python
config = BenchmarkConfig(
    output_dir='./results',           # Output directory
    true_hurst=None,                  # Specific Hurst value (None for all)
    n_bootstrap=100,                  # Bootstrap samples for CI
    confidence_level=0.95,            # Confidence level
    random_state=42,                  # Random seed
    estimators=None,                  # Specific estimators (None for all)
    save_results=True,                # Save results to files
    verbose=False                     # Verbose output
)
```

### Data Generation Options

```python
datasets = generate_grid(
    hurst_values=[0.3, 0.5, 0.7],    # Hurst exponents to test
    lengths=[512, 1024, 2048],        # Data lengths
    contaminations=['none', 'noise'], # Contamination types
    contamination_level=0.1,          # Contamination level (0-1)
    seed=42                           # Random seed
)
```

## Statistical Interpretation

### Bias Analysis
- **Positive Bias**: Estimator tends to overestimate
- **Negative Bias**: Estimator tends to underestimate
- **Zero Bias**: Unbiased estimator (ideal)

### Error Analysis
- **Mean Absolute Error (MAE)**: Average absolute deviation
- **Root Mean Square Error (RMSE)**: Penalizes large errors more
- **Relative Error**: Error relative to true value

### Significance Analysis
- **P-value < 0.05**: Statistically significant regression
- **Significance Rate**: Percentage of significant estimates
- **High significance rate**: Consistent statistical reliability

## Output Files

The enhanced benchmarking system generates several output files:

### CSV Files
- `benchmark_results.csv`: Raw results with all metrics
- `leaderboard.csv`: Ranked estimator performance
- `detailed_analysis.csv`: Comprehensive statistical analysis
- `bias_analysis.csv`: Bias patterns by Hurst value

### Text Files
- `benchmark_summary.txt`: Human-readable summary

### Example Output Structure
```
benchmark_results/
├── benchmark_results.csv      # Raw results
├── benchmark_summary.txt      # Summary report
├── leaderboard.csv           # Performance ranking
├── detailed_analysis.csv     # Statistical analysis
└── bias_analysis.csv         # Bias patterns
```

## Advanced Usage

### Custom Estimator Selection

```python
# Benchmark specific estimators only
config = BenchmarkConfig(
    output_dir='./custom_results',
    estimators=['DFA', 'R/S', 'GPH'],  # Only these estimators
    n_bootstrap=200,
    confidence_level=0.99
)
```

### Performance Comparison

```python
# Compare estimators across different conditions
conditions = {
    'clean_data': generate_grid([0.5, 0.7], [1024], ['none']),
    'noisy_data': generate_grid([0.5, 0.7], [1024], ['noise']),
    'short_data': generate_grid([0.5, 0.7], [512], ['none']),
    'long_data': generate_grid([0.5, 0.7], [2048], ['none'])
}

for condition_name, datasets in conditions.items():
    config = BenchmarkConfig(output_dir=f'./{condition_name}_results')
    results = run_benchmark_on_dataset(datasets, config)
    analysis = analyze_benchmark_results(results)
    
    print(f"\n{condition_name}:")
    for estimator, metrics in analysis.items():
        print(f"  {estimator}: MAE={metrics['mean_absolute_error']:.3f}")
```

### Statistical Testing

```python
# Compare estimator performance statistically
from scipy import stats

def compare_estimators(results, estimator1, estimator2):
    """Compare two estimators using paired t-test."""
    est1_results = [r for r in results if r.estimator == estimator1 and r.convergence_flag]
    est2_results = [r for r in results if r.estimator == estimator2 and r.convergence_flag]
    
    # Match by true Hurst value
    est1_errors = []
    est2_errors = []
    
    for r1 in est1_results:
        for r2 in est2_results:
            if r1.true_hurst == r2.true_hurst:
                est1_errors.append(r1.absolute_error)
                est2_errors.append(r2.absolute_error)
                break
    
    if len(est1_errors) > 1:
        t_stat, p_value = stats.ttest_rel(est1_errors, est2_errors)
        print(f"Comparison: {estimator1} vs {estimator2}")
        print(f"  T-statistic: {t_stat:.4f}")
        print(f"  P-value: {p_value:.4f}")
        print(f"  Significant difference: {'Yes' if p_value < 0.05 else 'No'}")

# Example usage
compare_estimators(results, 'DFA', 'R/S')
```

## Best Practices

### Benchmark Design
1. **Use multiple Hurst values**: Test across the range [0.1, 0.9]
2. **Vary data lengths**: Test with short (512), medium (1024), and long (2048) series
3. **Include contamination**: Test robustness with noise, missing data, outliers
4. **Adequate sample size**: Use at least 50 bootstrap samples for CI

### Statistical Interpretation
1. **Consider bias patterns**: Look for systematic over/under-estimation
2. **Evaluate consistency**: Check standard deviation of bias
3. **Assess significance**: High significance rate indicates reliability
4. **Compare across conditions**: Some estimators may be better for specific scenarios

### Performance Optimization
1. **Parallel processing**: Use multiple cores for large benchmarks
2. **Memory management**: Process datasets in batches for very large studies
3. **Result caching**: Save intermediate results for long-running benchmarks

## Troubleshooting

### Common Issues

#### Low Success Rates
```python
# Check for data quality issues
if metrics['success_rate'] < 0.8:
    print(f"Low success rate for {estimator}: {metrics['success_rate']:.1%}")
    print("Consider:")
    print("- Increasing data length")
    print("- Checking data quality")
    print("- Adjusting estimator parameters")
```

#### High Bias
```python
# Investigate bias patterns
if abs(metrics['mean_bias']) > 0.2:
    print(f"High bias for {estimator}: {metrics['mean_bias']:.3f}")
    print("Consider:")
    print("- Method may be inappropriate for data type")
    print("- Check preprocessing requirements")
    print("- Verify parameter settings")
```

#### Low Significance Rate
```python
# Check statistical reliability
if metrics['significance_rate'] < 0.5:
    print(f"Low significance rate for {estimator}: {metrics['significance_rate']:.1%}")
    print("Consider:")
    print("- Increasing bootstrap samples")
    print("- Checking data stationarity")
    print("- Verifying scaling range selection")
```

## Example Results Interpretation

### Sample Output
```
Estimator    Success Rate  Mean Bias  Std Bias  Mean Absolute Error  RMSE  Significance Rate
DFA          100.0%        -0.0662    0.1921    0.1751              0.2032  85.0%
R/S           100.0%        -0.0027    0.1939    0.1754              0.1940  92.0%
GPH           50.0%         0.0987    0.0993    0.1015              0.1400  75.0%
```

### Interpretation
- **DFA**: Consistent performance, slight negative bias, good significance
- **R/S**: Best overall performance, minimal bias, highest significance
- **GPH**: Lower success rate but good performance when successful

This enhanced benchmarking system provides comprehensive statistical analysis to help users select the most appropriate Hurst estimator for their specific biomedical time series data.
