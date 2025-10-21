# Biomedical Time Series Framework - Quick Reference

## 🚀 Quick Start Commands

### Basic Signal Generation
```python
from biomedical_timeseries_factory import BiomedicalTimeSeriesFactory, GenerationConfig

config = GenerationConfig(hurst_exponent=0.7, length=1024, sampling_rate=100.0)
factory = BiomedicalTimeSeriesFactory(config)
signal, time_axis, metadata = factory.generate(seed=42)
```

### Basic Analysis
```python
from biomedical_plotting_system import BiomedicalTimeSeriesAnalyzer

analyzer = BiomedicalTimeSeriesAnalyzer()
fig = analyzer.complete_analysis_dashboard(signal, time_axis, 100.0, "Signal")
```

## 📊 Core Classes Quick Reference

### BiomedicalTimeSeriesFactory
| Method | Description | Returns |
|--------|-------------|---------|
| `__init__(config)` | Initialize factory | Factory instance |
| `generate(seed=None)` | Generate signal | (signal, time_axis, metadata) |
| `set_config(**kwargs)` | Update configuration | None |
| `get_last_quality_report()` | Get quality report | str |

### BiomedicalTimeSeriesAnalyzer  
| Method | Description | Returns |
|--------|-------------|---------|
| `time_series_plot(signal, ...)` | Basic time series plot | (fig, ax) |
| `psd_plot(signal, fs, ...)` | Power spectral density | (fig, ax) |
| `acf_plot(signal, ...)` | Autocorrelation function | (fig, ax) |
| `basic_analysis_suite(signal, ...)` | 4-panel basic analysis | fig |
| `complete_analysis_dashboard(...)` | 8-panel comprehensive | fig |
| `get_analysis_summary(signal, fs)` | Analysis summary | Dict |

## ⚙️ Configuration Parameters

### GenerationConfig Key Parameters
```python
GenerationConfig(
    hurst_exponent=0.7,      # Long-range dependence (0.01-0.99)
    mean=0.0,                # Signal mean
    std=1.0,                 # Signal standard deviation  
    length=1024,             # Number of samples
    sampling_rate=100.0,     # Sampling frequency (Hz)
    signal_type=BiomedicalSignalType.ECG,  # Signal type for validation
    
    # Contamination levels (0.0-1.0)
    non_stationarity=0.1,    # Time-varying statistics
    periodicity=0.2,         # Sinusoidal components
    seasonality=0.1,         # Long-term cycles
    heavy_tail_noise=0.05    # Outliers and extreme events
)
```

### PlotConfig Key Parameters
```python
PlotConfig(
    theme=PlotTheme.SCIENTIFIC,        # Visual theme
    figure_size=(12, 8),               # Figure size in inches
    font_size=12,                      # Base font size
    save_format='png',                 # Export format
    save_dpi=300                       # Export resolution
)
```

## 🔬 Biomedical Signal Types

| Type | H Range | Freq Range (Hz) | Typical Use |
|------|---------|-----------------|-------------|
| ECG | 0.5-0.9 | 0.5-100 | Cardiac monitoring |
| EEG | 0.6-0.95 | 0.5-50 | Brain activity |
| EMG | 0.4-0.7 | 10-500 | Muscle activity |
| HRV | 0.5-0.85 | 0.001-0.5 | Autonomic function |
| PPG | 0.55-0.8 | 0.5-20 | Pulse monitoring |

## 🎨 Plot Themes and Presets

### Available Themes
- `PlotTheme.SCIENTIFIC` - Clean research style
- `PlotTheme.CLINICAL` - Medical-focused colors  
- `PlotTheme.PUBLICATION` - Black/white for papers
- `PlotTheme.DARK` - Dark background
- `PlotTheme.COLORFUL` - Vibrant educational

### Style Presets
```python
analyzer.set_style_preset('paper')        # Academic papers
analyzer.set_style_preset('presentation') # Slides
analyzer.set_style_preset('poster')       # Conference posters
analyzer.set_style_preset('web')          # Web display
```

## 📈 Common Analysis Methods

### Individual Plots
```python
# Time series with statistics
fig, ax = analyzer.time_series_plot(signal, time_axis, show_stats=True)

# Power spectral density  
fig, ax = analyzer.psd_plot(signal, fs=100.0, method='welch')

# Autocorrelation with confidence bands
fig, ax = analyzer.acf_plot(signal, confidence_bands=True)

# Distribution with normal fit
fig, ax = analyzer.histogram_plot(signal, fit_normal=True)

# Hurst exponent analysis
fig, ax = analyzer.hurst_analysis_plot(signal)

# Stationarity assessment
fig, axes = analyzer.stationarity_plot(signal)
```

### Analysis Suites
```python
# Basic 4-panel analysis
fig = analyzer.basic_analysis_suite(signal, time_axis, fs)

# Frequency domain focus
fig = analyzer.frequency_analysis_suite(signal, fs)

# Statistical characterization
fig = analyzer.statistical_analysis_suite(signal)

# Complete 8-panel dashboard
fig = analyzer.complete_analysis_dashboard(signal, time_axis, fs, "Signal Name")
```

## 🔄 Preset Configurations

### Quick Signal Generation
```python
from biomedical_timeseries_factory import BiomedicalPresets

# ECG signal with different contamination levels
ecg_clean = BiomedicalPresets.create_ecg_config('clean')
ecg_mild = BiomedicalPresets.create_ecg_config('mild') 
ecg_moderate = BiomedicalPresets.create_ecg_config('moderate')
ecg_severe = BiomedicalPresets.create_ecg_config('severe')

# EEG signal
eeg_config = BiomedicalPresets.create_eeg_config('mild')

# Heart rate variability
hrv_config = BiomedicalPresets.create_hrv_config('moderate')
```

## 🔍 Analysis Summary Structure

```python
summary = analyzer.get_analysis_summary(signal, fs)

# Access different components
basic_stats = summary['basic_statistics']      # mean, std, skewness, etc.
freq_analysis = summary['frequency_analysis']  # peak_frequency, total_power
hurst_value = summary['hurst_exponent']        # long-range dependence
stationarity = summary['stationarity']         # mean/variance stability
autocorr = summary['autocorrelation']          # lag correlations
```

## 🔧 Common Usage Patterns

### Complete Workflow
```python
# 1. Generate signal
config = BiomedicalPresets.create_ecg_config('moderate')
factory = BiomedicalTimeSeriesFactory(config)
factory_output = factory.generate(seed=42)

# 2. Analyze directly
analyzer = BiomedicalTimeSeriesAnalyzer()
fig = analyzer.analyze_factory_output(factory_output, analysis_type='complete')

# 3. Save results
analyzer.save_figure(fig, "results", format='pdf', dpi=300)
```

### Batch Comparison
```python
# Generate multiple signals
signals = {}
for level in ['clean', 'mild', 'moderate', 'severe']:
    config = BiomedicalPresets.create_ecg_config(level)
    factory = BiomedicalTimeSeriesFactory(config)
    signal, _, _ = factory.generate(seed=42)
    signals[f'ECG ({level})'] = signal

# Compare statistically
fig = analyzer.batch_compare_signals(signals, fs=250.0)
```

### Custom Analysis
```python
# Create custom analysis for specific needs
def analyze_ecg_signal(signal, fs=250.0):
    analyzer = BiomedicalTimeSeriesAnalyzer()
    
    # ECG-specific frequency range
    psd_fig, _ = analyzer.psd_plot(signal, fs, freq_range=(0.5, 100))
    
    # Focus on cardiac-relevant lags
    acf_fig, _ = analyzer.acf_plot(signal, max_lags=int(2*fs))  # 2 second window
    
    # Get comprehensive summary
    summary = analyzer.get_analysis_summary(signal, fs)
    
    return psd_fig, acf_fig, summary
```

## ⚠️ Common Pitfalls to Avoid

### Parameter Validation
```python
# ❌ Avoid invalid Hurst parameters
config = GenerationConfig(hurst_exponent=1.5)  # Too high!

# ✅ Use valid range
config = GenerationConfig(hurst_exponent=0.75)  # Good
```

### Memory Management  
```python
# ❌ Avoid generating very long signals without chunking
config = GenerationConfig(length=1000000)  # May cause memory issues

# ✅ Use reasonable lengths or chunk processing
config = GenerationConfig(length=8192)  # More manageable
```

### Analysis Parameter Selection
```python
# ❌ Don't use default parameters for all signals
analyzer.acf_plot(signal)  # May be too many lags for long signals

# ✅ Adjust parameters based on signal characteristics
max_lags = min(len(signal)//4, 100)
analyzer.acf_plot(signal, max_lags=max_lags)
```

## 🎯 Performance Tips

### Efficient Analysis
```python
# Pre-compute summary for multiple uses
summary = analyzer.get_analysis_summary(signal, fs)
hurst = summary['hurst_exponent']  # Use cached result

# Batch process multiple signals
summaries = [analyzer.get_analysis_summary(sig, fs) for sig in signals]
```

### Memory Optimization
```python
# For large signals, limit analysis scope
if len(signal) > 10000:
    # Reduce parameters for better performance
    fig, ax = analyzer.psd_plot(signal, fs, nperseg=512)
    fig, ax = analyzer.acf_plot(signal, max_lags=200)
```

## 📁 File Export Options

### High-Quality Exports
```python
# Academic publication
analyzer.save_figure(fig, "paper_figure", format='pdf', dpi=300)

# Web display  
analyzer.save_figure(fig, "web_figure", format='png', dpi=96)

# Vector graphics
analyzer.save_figure(fig, "vector_figure", format='svg')

# Presentation
analyzer.save_figure(fig, "presentation", format='png', dpi=150)
```

## 🔗 Integration Examples

### With NumPy/SciPy
```python
import numpy as np
from scipy import signal as sp_signal

# Apply additional processing
filtered_signal = sp_signal.butter(4, 0.1, 'low', fs=fs, output='sos')
processed_signal = sp_signal.sosfilt(filtered_signal, signal)

# Analyze processed signal
fig = analyzer.basic_analysis_suite(processed_signal, time_axis, fs)
```

### With Pandas
```python
import pandas as pd

# Create DataFrame
df = pd.DataFrame({
    'time': time_axis,
    'signal': signal,
    'processed': processed_signal
})

# Export for further analysis
df.to_csv('signal_data.csv', index=False)
```

---

## 📖 Essential Documentation Links

- **Full API Reference**: See `biomedical-framework-api-documentation.md`
- **Installation Guide**: API documentation → Installation section
- **Tutorials**: API documentation → Examples and Tutorials section
- **Troubleshooting**: API documentation → Troubleshooting section

## 🆘 Getting Help

1. **Check Common Issues**: Review troubleshooting section
2. **Validate Parameters**: Use built-in validation
3. **Start Simple**: Begin with preset configurations
4. **Debug Step-by-Step**: Validate each analysis step

---

*Quick Reference v1.0.0 - October 17, 2025*