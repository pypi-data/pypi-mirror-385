# Neurological LRD Analysis

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/badge/PyPI-neurological--lrd--analysis-green.svg)](https://pypi.org/project/neurological-lrd-analysis/)
[![Documentation](https://img.shields.io/badge/docs-readthedocs-blue.svg)](https://neurological-lrd-analysis.readthedocs.io/)

A comprehensive library for estimating Hurst exponents in neurological time series data, featuring multiple estimation methods, realistic data generation, and advanced benchmarking capabilities.

**Developed as part of PhD research in Biomedical Engineering at the University of Reading, UK** by Davian R. Chin, focusing on **Physics-Informed Fractional Operator Learning for Real-Time Neurological Biomarker Detection: A Framework for Memory-Driven EEG Analysis**.

**Author:** Davian R. Chin (PhD Candidate in Biomedical Engineering, University of Reading, UK)  
**Email:** d.r.chin@pgr.reading.ac.uk  
**ORCiD:** [https://orcid.org/0009-0003-9434-3919](https://orcid.org/0009-0003-9434-3919)

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (recommended)
pip install neurological-lrd-analysis

# Install with GPU support
pip install neurological-lrd-analysis[gpu]

# Install with development dependencies
pip install neurological-lrd-analysis[dev]

# Or install from source
git clone https://github.com/dave2k77/neurological_lrd_analysis.git
cd neurological_lrd_analysis
pip install -e .
```

### Basic Usage

```python
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
print(f"Confidence interval: {result.confidence_interval}")
print(f"Data quality score: {result.data_quality_score:.3f}")
```

## ✨ Features

### 🧮 **Multiple Estimation Methods**
- **Temporal**: DFA, R/S Analysis, Higuchi, Generalized Hurst Exponent
- **Spectral**: Periodogram, GPH, Whittle MLE
- **Wavelet**: DWT, NDWT, Abry-Veitch
- **Multifractal**: MFDFA, MF-DMA

### 🏥 **Biomedical Scenarios**
- **EEG**: Rest, eyes closed/open, sleep, seizure patterns
- **ECG**: Normal heart rate, tachycardia, realistic QRS complexes
- **Respiratory**: Breathing patterns, irregular breathing
- **Neurological**: Memory-driven EEG analysis, neurological biomarker detection
- **Artifacts**: Electrode pops, motion, baseline drift, powerline interference
- **Physics-Informed Features**: Fractional operator learning, real-time biomarker detection

### 📊 **Statistical Analysis**
- Bootstrap confidence intervals
- Theoretical confidence intervals
- Uncertainty quantification
- Comprehensive error metrics (bias, MAE, RMSE)

### 🏆 **Enhanced Benchmarking**
- Parametrized scoring functions for different applications
- Application-specific rankings (BCI, research, clinical)
- Comprehensive statistical reporting
- Publication-ready visualizations

### ⚡ **Performance Optimization**
- JAX GPU acceleration
- Numba CPU optimization
- Intelligent backend selection
- Lazy imports for efficiency

## 📖 Documentation

- **[Complete Documentation](docs/)** - Comprehensive guides and API reference
- **[Tutorial](docs/TUTORIAL.md)** - Step-by-step tutorial with examples
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[Configuration Guide](docs/CONFIGURATION_GUIDE.md)** - Application-specific configuration
- **[Benchmarking Guide](docs/BENCHMARKING_GUIDE.md)** - Enhanced benchmarking system

## 🎯 Use Cases

### BCI/Real-time Applications
```bash
python scripts/run_benchmark.py --success-weight 0.4 --accuracy-weight 0.2 --speed-weight 0.3 --robustness-weight 0.1
```

### Research Applications
```bash
python scripts/run_benchmark.py --success-weight 0.2 --accuracy-weight 0.4 --speed-weight 0.1 --robustness-weight 0.3
```

### Biomedical Scenarios
```bash
python scripts/run_benchmark.py --biomedical-scenarios eeg_rest,ecg_normal --contaminations none,noise,electrode_pop
```

### Neurological Conditions
```bash
python scripts/run_benchmark.py --biomedical-scenarios eeg_parkinsonian,eeg_epileptic --contaminations heavy_tail,neural_avalanche
```

## 🧪 Examples and Demos

```bash
# Run biomedical scenarios demonstration
python scripts/biomedical_scenarios_demo.py

# Run neurological conditions demonstration
python scripts/neurological_conditions_demo.py

# Run NumPyro integration demonstration
python scripts/numpyro_integration_demo.py

# Run application scoring demonstration
python scripts/application_scoring_demo.py
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_accuracy.py -v
python -m pytest tests/test_backends.py -v
python -m pytest tests/test_registry.py -v
```

## 📊 Project Structure

```
neurological_lrd_analysis/
├── neurological_lrd_analysis/     # Main package directory
│   ├── biomedical_hurst_factory.py    # Main library file
│   ├── benchmark_core/                # Core benchmarking functionality
│   ├── benchmark_backends/            # Backend selection and optimization
│   └── benchmark_registry/            # Estimator registry system
├── docs/                         # Documentation
├── scripts/                      # Demo scripts and utilities
├── tests/                        # Test suite
├── examples/                     # Example notebooks and code
├── results/                      # Benchmark results and outputs
├── pyproject.toml               # Package configuration
├── setup.py                     # Setup script
└── requirements.txt             # Dependencies
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [JAX](https://github.com/google/jax) for GPU acceleration and physics-informed learning
- Uses [NumPyro](https://github.com/pyro-ppl/numpyro) for Bayesian inference in fractional operators
- Leverages [PyWavelets](https://github.com/PyWavelets/pywavelets) for wavelet-based fractional analysis
- Inspired by research in physics-informed machine learning and memory-driven neurological signal processing

## 📚 Citation

If you use this library in your research, please cite:

```bibtex
@software{neurological_lrd_analysis,
  title={Neurological LRD Analysis: A Comprehensive Library for Physics-Informed Fractional Operator Learning and Real-Time Neurological Biomarker Detection},
  author={Davian R. Chin},
  year={2025},
  institution={University of Reading, UK},
  email={d.r.chin@pgr.reading.ac.uk},
  orcid={https://orcid.org/0009-0003-9434-3919},
  note={PhD Research in Biomedical Engineering: A Framework for Memory-Driven EEG Analysis},
  url={https://github.com/dave2k77/neurological_lrd_analysis}
}
```

## 📦 Releases and Versioning

This project follows [Semantic Versioning](https://semver.org/) and uses GitHub Actions for automated releases to PyPI.

### Creating a New Release

1. **Bump version**: `python scripts/bump_version.py 0.4.1`
2. **Commit changes**: `git add . && git commit -m "Bump version to 0.4.1"`
3. **Create tag**: `git tag v0.4.1`
4. **Push to GitHub**: `git push origin main --tags`
5. **GitHub Actions** will automatically:
   - Run tests
   - Build the package
   - Publish to PyPI
   - Create a GitHub release

### Development Releases

For testing, you can publish to TestPyPI:

```bash
# Push to develop branch to trigger TestPyPI publishing
git checkout develop
git push origin develop
```

### Installation Options

- **Stable releases**: `pip install neurological-lrd-analysis`
- **Development versions**: `pip install git+https://github.com/dave2k77/neurological_lrd_analysis.git`
- **Test versions**: `pip install --index-url https://test.pypi.org/simple/ neurological-lrd-analysis`

## 🔗 Links

- [Documentation](https://neurological-lrd-analysis.readthedocs.io/)
- [Issue Tracker](https://github.com/dave2k77/neurological_lrd_analysis/issues)
- [PyPI Package](https://pypi.org/project/neurological-lrd-analysis/)
- [GitHub Releases](https://github.com/dave2k77/neurological_lrd_analysis/releases)
- [Research Paper](docs/comprehensive-lrd-estimators-paper.md)
