# Biomedical Hurst Factory - Documentation Index

## 📚 Complete Documentation Suite

This document provides an organized index of all documentation available for the Biomedical Hurst Factory project.

## 🚀 Getting Started

### Essential Reading
1. **[README.md](README.md)** - Project overview, quick start, and key features
2. **[ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)** - Detailed setup instructions and troubleshooting
3. **[TUTORIAL.md](TUTORIAL.md)** - Comprehensive tutorial with examples

### Quick Setup
```bash
# Automated setup (recommended)
python scripts/setup_venv.sh
source biomedical_hurst_env/bin/activate

# Verify installation
python -c "from biomedical_hurst_factory import BiomedicalHurstEstimatorFactory; print('Ready!')"
```

### Biomedical Scenarios Demo
```bash
# Run biomedical scenarios demonstration
python scripts/biomedical_scenarios_demo.py

# Run neurological conditions demonstration
python scripts/neurological_conditions_demo.py

# Run benchmark with custom parameters
python scripts/run_benchmark.py --hurst-values 0.5,0.7 --lengths 512,1024
```

## 📖 Reference Documentation

### Core API
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation with all classes, methods, and parameters
- **[BENCHMARKING_GUIDE.md](BENCHMARKING_GUIDE.md)** - Enhanced benchmarking with statistical reporting
- **[CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)** - Application-specific configuration and scoring customization

### Project Structure
- **[project_instructions.md](project_instructions.md)** - Original project requirements and specifications

## 🧪 Testing and Validation

### Test Documentation
- **[estimator_testing_validation/README_Tests.md](estimator_testing_validation/README_Tests.md)** - Test suite overview
- **[estimator_testing_validation/Summary_Comprehensive_Test_Plan.md](estimator_testing_validation/Summary_Comprehensive_Test_Plan.md)** - Test plan summary

### Running Tests
```bash
# All tests
python -m pytest estimator_testing_validation/ -v

# Specific test categories
python -m pytest estimator_testing_validation/ -m unit
python -m pytest estimator_testing_validation/ -m integration
python -m pytest estimator_testing_validation/ -m performance
```

## 🔬 Research and Implementation

### Research Documentation
- **[estimator_research/comprehensive-lrd-estimators-paper.md](estimator_research/comprehensive-lrd-estimators-paper.md)** - Comprehensive LRD estimators research
- **[estimator_research/Techniques_for_Estimating_the_Hurst_Exponent.md](estimator_research/Techniques_for_Estimating_the_Hurst_Exponent.md)** - Hurst estimation techniques
- **[estimator_research/wavelet-based-lrd-estimators.md](estimator_research/wavelet-based-lrd-estimators.md)** - Wavelet-based LRD estimators

### Implementation Documentation
- **[estimator_implementation/API_Reference_Guide.md](estimator_implementation/API_Reference_Guide.md)** - Implementation API guide
- **[estimator_implementation/comprehensive-hurst-library.md](estimator_implementation/comprehensive-hurst-library.md)** - Comprehensive Hurst library documentation
- **[estimator_implementation/GPU-Acceleration-Strategy.md](estimator_implementation/GPU-Acceleration-Strategy.md)** - GPU acceleration strategy

## 📊 Data Models and Analysis

### Data Models
- **[data_models_implementation/biomedical_data_models_generative_factory_architecture.md](data_models_implementation/biomedical_data_models_generative_factory_architecture.md)** - Data models architecture
- **[data_models_implementation/biomedical_time_series_data_analysis_plotting_utility.md](data_models_implementation/biomedical_time_series_data_analysis_plotting_utility.md)** - Plotting utilities
- **[data_models_implementation/biomedical-framework-api-documentation.md](data_models_implementation/biomedical-framework-api-documentation.md)** - Framework API documentation
- **[data_models_implementation/biomedical-framework-index.md](data_models_implementation/biomedical-framework-index.md)** - Framework index
- **[data_models_implementation/biomedical-framework-quick-reference.md](data_models_implementation/biomedical-framework-quick-reference.md)** - Quick reference guide
- **[data_models_implementation/biomedical-generative-model-documentation.md](data_models_implementation/biomedical-generative-model-documentation.md)** - Generative model documentation
- **[data_models_implementation/biomedical-plotting-system-documentation.md](data_models_implementation/biomedical-plotting-system-documentation.md)** - Plotting system documentation
- **[data_models_implementation/Complete_API_Documentation_Biomedical_Time_Series_Analysis.md](data_models_implementation/Complete_API_Documentation_Biomedical_Time_Series_Analysis.md)** - Complete API documentation
- **[data_models_implementation/design_algorithms_for_generating_synthetic_data.md](data_models_implementation/design_algorithms_for_generating_synthetic_data.md)** - Synthetic data generation algorithms

### Research
- **[data_models_research/time-series-algorithms-comprehensive.md](data_models_research/time-series-algorithms-comprehensive.md)** - Time series algorithms research
- **[data_models_research/time-series-models-biomedicine-neuroscience.md](data_models_research/time-series-models-biomedicine-neuroscience.md)** - Biomedical time series models

## 🎯 Usage Examples

### Basic Usage
```python
from biomedical_hurst_factory import BiomedicalHurstEstimatorFactory, EstimatorType
import numpy as np

# Create factory
factory = BiomedicalHurstEstimatorFactory()

# Generate test data
data = np.cumsum(np.random.randn(1000))

# Single method estimation
result = factory.estimate(data, EstimatorType.DFA)
print(f"Hurst: {result.hurst_estimate:.3f}")

# Group estimation
group_result = factory.estimate(data, EstimatorType.ALL)
print(f"Ensemble: {group_result.ensemble_estimate:.3f}")
```

### Advanced Usage
```python
# Custom parameters
result = factory.estimate(
    data, 
    EstimatorType.DFA,
    min_window=20,
    max_window=200,
    confidence_method=ConfidenceMethod.BOOTSTRAP,
    n_bootstrap=1000
)

# Data quality assessment
from biomedical_hurst_factory import BiomedicalDataProcessor
processor = BiomedicalDataProcessor()
quality = processor.assess_data_quality(data)
print(f"Quality score: {quality['data_quality_score']:.3f}")
```

## 🔧 Development

### Project Structure
```
long_range_dependence/
├── biomedical_hurst_factory.py    # Main library
├── benchmark_core/                # Benchmarking infrastructure
├── benchmark_backends/            # Backend selection
├── benchmark_registry/            # Estimator registry
├── estimator_testing_validation/  # Test suite
├── estimator_implementation/      # Implementation docs
├── estimator_research/            # Research docs
├── data_models_implementation/    # Data models docs
├── data_models_research/          # Data models research
├── pyproject.toml                 # Project configuration
├── setup_venv.sh                  # Setup script
└── README.md                      # Project overview
```

### Development Workflow
1. **Setup**: Run `./setup_venv.sh` and activate environment
2. **Develop**: Make changes to code
3. **Test**: Run `python -m pytest estimator_testing_validation/ -v`
4. **Document**: Update relevant documentation
5. **Validate**: Run benchmarks and examples

## 📈 Performance Benchmarks

### Recent Benchmark Results
- **Total Estimators**: 12 implemented
- **Success Rate**: 100% across all methods
- **Best Performance**: GHE (MAE: 0.277), MF-DMA (MAE: 0.308)
- **Computation Time**: < 1 second for 1000-point time series

### Benchmarking
```bash
# Run quick benchmark
python -c "
from benchmark_core.generation import generate_grid
from benchmark_core.runner import BenchmarkConfig, run_benchmark_on_dataset
# ... benchmark code
"
```

## 🆘 Troubleshooting

### Common Issues
1. **Import Errors**: Ensure virtual environment is activated
2. **Data Too Short**: Check minimum length requirements
3. **Missing Dependencies**: Install optional packages as needed
4. **Performance Issues**: Consider using GPU acceleration

### Getting Help
- Check [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for setup issues
- Review [TUTORIAL.md](TUTORIAL.md) for usage examples
- Consult [API_REFERENCE.md](API_REFERENCE.md) for detailed API information

## 🔄 Version History

### Current Version: v0.3.0
- ✅ Convergence analysis in preprocessing
- ✅ Lazy imports for performance
- ✅ Comprehensive documentation suite
- ✅ Wavelet and multifractal estimators
- ✅ Virtual environment setup automation

### Previous Versions
- **v0.2.0**: Added wavelet and multifractal estimators
- **v0.1.0**: Initial release with classical estimators

## 📝 Contributing

### Documentation Updates
When adding new features or making changes:

1. **Update API Reference**: Modify [API_REFERENCE.md](API_REFERENCE.md)
2. **Update Tutorial**: Add examples to [TUTORIAL.md](TUTORIAL.md)
3. **Update README**: Keep [README.md](README.md) current
4. **Update Index**: Maintain this documentation index

### Documentation Standards
- Use clear, concise language
- Include code examples
- Provide troubleshooting information
- Keep documentation up-to-date with code changes

## 📞 Support and Contact

- **Documentation Issues**: Check this index for relevant docs
- **Setup Problems**: See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)
- **Usage Questions**: Review [TUTORIAL.md](TUTORIAL.md)
- **API Questions**: Consult [API_REFERENCE.md](API_REFERENCE.md)

---

**Last Updated**: December 2024  
**Documentation Version**: 1.0.0  
**Project Version**: 0.3.0

