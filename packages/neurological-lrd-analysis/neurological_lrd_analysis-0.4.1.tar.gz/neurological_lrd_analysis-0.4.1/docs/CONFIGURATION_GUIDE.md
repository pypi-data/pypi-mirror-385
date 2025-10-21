# Configuration Guide for Biomedical Hurst Factory

This guide provides comprehensive information on configuring the biomedical Hurst factory library for different applications and use cases.

## Table of Contents

1. [Scoring Function Configuration](#scoring-function-configuration)
2. [Application-Specific Configurations](#application-specific-configurations)
3. [Benchmark Configuration](#benchmark-configuration)
4. [Backend Selection](#backend-selection)
5. [Data Generation Configuration](#data-generation-configuration)
6. [Visualization Configuration](#visualization-configuration)
7. [Best Practices](#best-practices)

## Scoring Function Configuration

The library uses a parametrized scoring function that combines multiple performance metrics with user-configurable weights. This allows you to prioritize different aspects of estimator performance based on your application needs.

### Scoring Components

The overall score is calculated as a weighted sum of four components:

```
Overall Score = w₁ × Success_Rate + w₂ × Accuracy_Score + w₃ × Speed_Score + w₄ × Robustness_Score
```

Where:
- **Success Rate** (w₁): Percentage of successful estimations (0-1, higher is better)
- **Accuracy Score** (w₂): Based on Mean Absolute Error (MAE), normalized and inverted (lower MAE = higher score)
- **Speed Score** (w₃): Based on computation time, normalized and inverted (lower time = higher score)
- **Robustness Score** (w₄): Based on consistency across conditions (lower variance = higher score)

### Default Configuration

```python
from benchmark_core.runner import ScoringWeights

# Default balanced configuration
default_weights = ScoringWeights(
    success_rate=0.3,    # 30% weight on success rate
    accuracy=0.3,        # 30% weight on accuracy
    speed=0.2,           # 20% weight on speed
    robustness=0.2       # 20% weight on robustness
)
```

### Command-Line Configuration

You can customize scoring weights directly from the command line:

```bash
# BCI/Real-time application (prioritize speed and success rate)
python run_benchmark.py \
    --success-weight 0.4 \
    --accuracy-weight 0.2 \
    --speed-weight 0.3 \
    --robustness-weight 0.1

# Research application (prioritize accuracy and robustness)
python run_benchmark.py \
    --success-weight 0.2 \
    --accuracy-weight 0.4 \
    --speed-weight 0.1 \
    --robustness-weight 0.3
```

## Application-Specific Configurations

### BCI/Real-time Applications

**Priority**: Speed and reliability for real-time processing

```python
bci_weights = ScoringWeights(
    success_rate=0.4,    # High: Need reliable results
    accuracy=0.2,        # Medium: Some accuracy trade-off acceptable
    speed=0.3,           # High: Real-time constraints
    robustness=0.1       # Low: Controlled environment
)
```

**Recommended estimators**: GPH, Periodogram, NDWT (fast and reliable)

### Research Applications

**Priority**: Accuracy and uncertainty quantification

```python
research_weights = ScoringWeights(
    success_rate=0.2,    # Medium: Some failures acceptable
    accuracy=0.4,        # High: Need precise measurements
    speed=0.1,           # Low: Time not critical
    robustness=0.3       # High: Robust across conditions
)
```

**Recommended estimators**: DFA, MFDFA, R/S Analysis (accurate and robust)

### Clinical Applications

**Priority**: Robustness and accuracy for patient safety

```python
clinical_weights = ScoringWeights(
    success_rate=0.3,    # High: Reliable results needed
    accuracy=0.3,        # High: Clinical decisions depend on accuracy
    speed=0.1,           # Low: Patient safety over speed
    robustness=0.3       # High: Must work across patients/conditions
)
```

**Recommended estimators**: DFA, MFDFA, R/S Analysis (robust and accurate)

### High-Throughput Screening

**Priority**: Speed and success rate for processing many samples

```python
screening_weights = ScoringWeights(
    success_rate=0.35,   # High: Need many successful estimates
    accuracy=0.15,       # Lower: Screening can be less precise
    speed=0.4,           # Very High: Process many samples
    robustness=0.1       # Lower: Controlled screening conditions
)
```

**Recommended estimators**: GPH, Periodogram, GHE (fast and reliable)

### Quality Control

**Priority**: Robustness and consistency

```python
qc_weights = ScoringWeights(
    success_rate=0.35,   # High: Consistent results needed
    accuracy=0.2,        # Medium: Good accuracy required
    speed=0.15,          # Lower: Quality over speed
    robustness=0.3       # High: Must detect variations reliably
)
```

**Recommended estimators**: DFA, MFDFA, R/S Analysis (robust and consistent)

## Benchmark Configuration

### Basic Configuration

```python
from benchmark_core.runner import BenchmarkConfig

config = BenchmarkConfig(
    output_dir="./results",
    n_bootstrap=100,           # Number of bootstrap samples
    confidence_level=0.95,     # Confidence level for intervals
    save_results=True,         # Save results to files
    verbose=False,             # Verbose output
    random_state=42,           # Random seed for reproducibility
    scoring_weights=my_weights # Custom scoring weights
)
```

### Bayesian Inference Configuration

```python
config = BenchmarkConfig(
    output_dir="./results",
    use_bayesian=True,         # Use Bayesian inference
    num_samples=2000,          # MCMC samples
    num_warmup=1000,           # Warmup samples
    confidence_level=0.95,     # Credible interval level
    scoring_weights=my_weights
)
```

### Advanced Configuration

```python
config = BenchmarkConfig(
    output_dir="./results",
    n_bootstrap=500,           # More bootstrap samples for better CI
    confidence_level=0.99,     # Higher confidence level
    estimators=["DFA", "GPH", "Periodogram"],  # Specific estimators only
    save_results=True,
    verbose=True,
    random_state=42,
    scoring_weights=my_weights
)
```

## Backend Selection

The library automatically selects the optimal backend based on available hardware:

### Automatic Selection

```python
from benchmark_backends.selector import select_backend

# Automatic selection based on data characteristics
backend = select_backend(
    data_length=1024,
    real_time=False,      # Not real-time critical
    prefer_jax=True       # Prefer JAX if GPU available
)
```

### Manual Backend Configuration

```python
# Force specific backend
backend = "jax_gpu"      # JAX with GPU acceleration
backend = "numba_cpu"    # Numba CPU optimization
backend = "numpy"        # Standard NumPy/SciPy
```

### Backend Recommendations

| Application Type | Recommended Backend | Reason |
|------------------|-------------------|---------|
| Real-time BCI | `numba_cpu` | Fast CPU execution |
| Research Analysis | `jax_gpu` | GPU acceleration for large datasets |
| Clinical Screening | `numpy` | Reliable, well-tested |
| High-throughput | `jax_gpu` | GPU parallelization |

## Data Generation Configuration

### Synthetic Data Types

```python
from benchmark_core.generation import generate_grid

# Different data generators for different scenarios
datasets = generate_grid(
    hurst_values=[0.3, 0.5, 0.7, 0.9],
    lengths=[512, 1024, 2048],
    contaminations=['none', 'noise', 'outliers', 'trend'],
    contamination_level=0.1,
    generators=['fbm', 'fgn', 'arfima', 'mrw', 'fou'],  # Multiple generators
    seed=42
)
```

### Generator Selection Guide

| Generator | Best For | Characteristics |
|-----------|----------|----------------|
| `fbm` | General testing | Standard fractional Brownian motion |
| `fgn` | Noise analysis | Fractional Gaussian noise |
| `arfima` | Time series analysis | AutoRegressive Fractionally Integrated |
| `mrw` | Multifractal analysis | Multifractal Random Walk |
| `fou` | Mean-reverting processes | Fractional Ornstein-Uhlenbeck |

### Contamination Types

```python
contaminations = [
    'none',      # Clean data
    'noise',     # Additive Gaussian noise
    'outliers',  # Random outliers
    'trend',     # Linear trend
    'missing'    # Missing data points
]
```

## Visualization Configuration

### Focused Analysis Reports

The library generates application-focused visualizations:

```python
from benchmark_core.visualization import create_focused_analysis_report

# Generate focused visualizations
create_focused_analysis_report(
    results=benchmark_results,
    output_dir="./plots"
)
```

### Visualization Types

1. **Estimation Accuracy**: Bias and error analysis
2. **Uncertainty Quantification**: Confidence intervals and coverage
3. **Efficiency Analysis**: Time vs accuracy trade-offs

### Custom Visualization

```python
from benchmark_core.visualization import create_accuracy_comparison_plot

# Create custom accuracy plot
fig = create_accuracy_comparison_plot(results, save_path="./accuracy.png")
```

## Best Practices

### 1. Choose Appropriate Scoring Weights

- **For real-time applications**: High speed and success rate weights
- **For research**: High accuracy and robustness weights
- **For clinical use**: High accuracy and robustness weights
- **For screening**: High speed and success rate weights

### 2. Select Suitable Data Generators

- **General benchmarking**: Use `fbm` and `fgn`
- **Multifractal analysis**: Include `mrw`
- **Time series analysis**: Include `arfima`
- **Mean-reverting processes**: Include `fou`

### 3. Configure Bootstrap Parameters

- **Quick testing**: 50-100 bootstrap samples
- **Production use**: 500-1000 bootstrap samples
- **High precision**: 1000+ bootstrap samples

### 4. Backend Selection

- **GPU available**: Use `jax_gpu` for large datasets
- **CPU only**: Use `numba_cpu` for optimization
- **Reliability**: Use `numpy` for critical applications

### 5. Validation Strategy

```python
# Multi-generator validation
generators = ['fbm', 'fgn', 'arfima', 'mrw', 'fou']
contaminations = ['none', 'noise', 'outliers']

# Cross-validation with different scoring weights
weight_configs = [
    ScoringWeights(0.4, 0.2, 0.3, 0.1),  # BCI
    ScoringWeights(0.2, 0.4, 0.1, 0.3),  # Research
    ScoringWeights(0.3, 0.3, 0.1, 0.3),  # Clinical
]
```

### 6. Performance Monitoring

```python
# Monitor key metrics
config = BenchmarkConfig(
    output_dir="./results",
    verbose=True,           # Enable detailed output
    save_results=True,      # Save for analysis
    scoring_weights=weights
)
```

## Example Configurations

### Complete BCI Application Setup

```python
from benchmark_core.runner import BenchmarkConfig, ScoringWeights
from benchmark_core.generation import generate_grid

# BCI-specific scoring weights
bci_weights = ScoringWeights(
    success_rate=0.4,
    accuracy=0.2,
    speed=0.3,
    robustness=0.1
)

# Generate test data
datasets = generate_grid(
    hurst_values=[0.5, 0.7],
    lengths=[512, 1024],
    contaminations=['none', 'noise'],
    generators=['fbm', 'fgn'],
    seed=42
)

# Configure benchmark
config = BenchmarkConfig(
    output_dir="./bci_results",
    n_bootstrap=100,
    confidence_level=0.95,
    save_results=True,
    verbose=True,
    scoring_weights=bci_weights
)
```

### Complete Research Application Setup

```python
# Research-specific scoring weights
research_weights = ScoringWeights(
    success_rate=0.2,
    accuracy=0.4,
    speed=0.1,
    robustness=0.3
)

# Generate comprehensive test data
datasets = generate_grid(
    hurst_values=[0.3, 0.5, 0.7, 0.9],
    lengths=[512, 1024, 2048, 4096],
    contaminations=['none', 'noise', 'outliers', 'trend'],
    generators=['fbm', 'fgn', 'arfima', 'mrw'],
    contamination_level=0.15,
    seed=42
)

# Configure benchmark
config = BenchmarkConfig(
    output_dir="./research_results",
    n_bootstrap=500,
    confidence_level=0.99,
    save_results=True,
    verbose=True,
    scoring_weights=research_weights
)
```

## Troubleshooting

### Common Issues

1. **Low success rates**: Reduce contamination level or use more robust estimators
2. **Poor accuracy**: Increase bootstrap samples or use more accurate estimators
3. **Slow performance**: Use faster estimators or enable GPU acceleration
4. **Inconsistent results**: Increase robustness weight or use more stable estimators

### Performance Optimization

1. **Use appropriate data lengths**: 512-2048 for most applications
2. **Select relevant estimators**: Don't test all estimators if not needed
3. **Optimize bootstrap samples**: Balance between accuracy and speed
4. **Use hardware acceleration**: Enable JAX GPU when available

This configuration guide provides the foundation for optimizing the biomedical Hurst factory library for your specific application needs.
