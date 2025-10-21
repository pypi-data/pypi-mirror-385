# Contributing to Neurological LRD Analysis

We welcome contributions to the Neurological LRD Analysis project! This document provides guidelines and information for contributors.

**Research Context**: This library is developed as part of PhD research in Biomedical Engineering at the University of Reading, UK by Davian R. Chin, focusing on **Physics-Informed Fractional Operator Learning for Real-Time Neurological Biomarker Detection: A Framework for Memory-Driven EEG Analysis**.

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Basic knowledge of biomedical signal processing and time series analysis

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/biomedical_hurst_factory.git
   cd biomedical_hurst_factory
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv biomedical_hurst_env
   source biomedical_hurst_env/bin/activate  # On Windows: biomedical_hurst_env\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt  # If available
   ```

4. **Run tests to ensure everything works**
   ```bash
   python -m pytest tests/ -v
   ```

## 📝 How to Contribute

### Reporting Issues

Before creating an issue, please:
1. Check if the issue already exists
2. Provide a clear description of the problem
3. Include steps to reproduce the issue
4. Specify your Python version and operating system

### Suggesting Enhancements

When suggesting new features:
1. Check if the feature is already planned or implemented
2. Provide a clear description of the proposed feature
3. Explain the use case and benefits
4. Consider implementation complexity

### Code Contributions

#### 1. Choose an Issue or Feature

- Look for issues labeled "good first issue" for beginners
- Check the project roadmap for planned features
- Propose new features by opening an issue first

#### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number
```

#### 3. Make Changes

- Follow the existing code style and conventions
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

#### 4. Test Your Changes

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific tests
python -m pytest tests/test_your_feature.py -v

# Run linting (if available)
flake8 biomedical_hurst_factory/
black biomedical_hurst_factory/
```

#### 5. Commit Your Changes

```bash
git add .
git commit -m "Add: brief description of your changes"
```

Use clear, descriptive commit messages:
- `Add:` for new features
- `Fix:` for bug fixes
- `Update:` for improvements
- `Docs:` for documentation changes
- `Test:` for test additions

#### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear description of changes
- Reference to related issues
- Screenshots or examples if applicable

## 🏗️ Code Style and Standards

### Python Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and reasonably sized

### Documentation

- Update relevant documentation files
- Add docstrings for new functions/classes
- Include examples in docstrings when helpful
- Update the main README if adding major features

### Testing

- Write tests for new functionality
- Aim for good test coverage
- Include both unit tests and integration tests
- Test edge cases and error conditions

## 🎯 Areas for Contribution

### High Priority

1. **Machine Learning Baselines**
   - Random Forest implementation
   - Support Vector Regression
   - Gradient Boosting Trees

2. **Neural Network Baselines**
   - Multi-Layer Perceptron
   - Convolutional Neural Networks
   - LSTM/GRU networks
   - Transformer architectures

3. **Advanced Wavelet Techniques**
   - Wavelet leaders implementation
   - Wavelet Whittle estimation

### Medium Priority

1. **Performance Optimization**
   - GPU acceleration improvements
   - Memory optimization
   - Parallel processing

2. **Additional Data Generators**
   - More realistic biomedical scenarios
   - Additional contamination types
   - Real data integration

3. **Visualization Enhancements**
   - Interactive plots
   - Real-time visualization
   - Advanced statistical plots

### Low Priority

1. **Documentation**
   - Tutorial improvements
   - API documentation enhancements
   - Example notebooks

2. **Testing**
   - Additional test cases
   - Performance benchmarks
   - Integration tests

## 🔍 Review Process

### Pull Request Review

1. **Automated Checks**
   - Tests must pass
   - Code style checks (if configured)
   - Documentation builds successfully

2. **Manual Review**
   - Code quality and style
   - Functionality correctness
   - Documentation completeness
   - Performance considerations

3. **Approval**
   - At least one maintainer approval required
   - All discussions resolved
   - Tests passing

### Response Time

- Initial review: Within 1 week
- Follow-up reviews: Within 3-5 days
- Final approval: Within 1-2 weeks

## 📚 Development Guidelines

### Adding New Estimators

1. **Implement the estimator class**
   ```python
   class YourEstimator(BaseEstimator):
       def estimate(self, data: np.ndarray, **kwargs) -> EstimatorResult:
           # Implementation here
           pass
   ```

2. **Register in the factory**
   ```python
   # In biomedical_hurst_factory.py
   self._estimators[EstimatorType.YOUR_METHOD] = YourEstimator()
   ```

3. **Add tests**
   ```python
   def test_your_estimator():
       # Test implementation
       pass
   ```

### Adding New Data Generators

1. **Implement generator function**
   ```python
   def generate_your_data(n: int, hurst: float, **kwargs) -> np.ndarray:
       # Implementation here
       pass
   ```

2. **Add to generation module**
   ```python
   # In benchmark_core/generation.py
   generator_functions['your_type'] = generate_your_data
   ```

3. **Update documentation**

### Adding New Contamination Types

1. **Implement contamination function**
   ```python
   elif contamination_type == 'your_contamination':
       # Implementation here
       pass
   ```

2. **Add to contamination types list**
3. **Update documentation and examples**

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Information**
   - Python version
   - Operating system
   - Package version
   - Dependencies

2. **Reproduction Steps**
   - Clear, minimal code example
   - Expected vs actual behavior
   - Error messages or stack traces

3. **Additional Context**
   - Workaround if available
   - Related issues or discussions

## 💡 Feature Requests

When requesting features:

1. **Use Case**
   - Describe the problem you're trying to solve
   - Explain why existing functionality doesn't meet your needs

2. **Proposed Solution**
   - Clear description of the proposed feature
   - Consider alternative approaches

3. **Implementation Notes**
   - Any technical considerations
   - Potential challenges or limitations

## 📦 Release Process

### For Maintainers

1. **Update version**:
   ```bash
   python scripts/bump_version.py 0.4.1
   ```

2. **Commit and tag**:
   ```bash
   git add .
   git commit -m "Bump version to 0.4.1"
   git tag v0.4.1
   git push origin main --tags
   ```

3. **GitHub Actions** will automatically:
   - Run all tests
   - Build the package
   - Publish to PyPI
   - Create a GitHub release

### For Contributors

- **Development releases**: Push to `develop` branch for TestPyPI publishing
- **Feature branches**: Create PRs to `main` branch
- **Testing**: Use TestPyPI for testing your changes

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check the docs/ folder for comprehensive guides

## 🙏 Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to Biomedical Hurst Factory! 🎉
