# Biomedical Time Series Analytical Plotting System

## Overview

The **Biomedical Time Series Analytical Plotting System** is a comprehensive visualization and analysis toolkit designed specifically for biomedical signal processing. It provides a complete suite of plotting methods, analysis tools, and visualization capabilities that integrate seamlessly with the Biomedical Time Series Factory for end-to-end signal generation, analysis, and visualization.

## 🎯 Key Features

### **Individual Plot Methods**
- **Time Series Plots**: Basic signal visualization with customizable styling
- **Power Spectral Density (PSD)**: Frequency domain analysis with multiple estimation methods
- **Autocorrelation Function (ACF)**: Temporal correlation analysis with confidence bands
- **Histogram Plots**: Distribution analysis with normal distribution fitting
- **Q-Q Plots**: Quantile-quantile plots for distribution assessment
- **Hurst Analysis**: Long-range dependence estimation using R/S statistics
- **Stationarity Assessment**: Windowed statistics for non-stationarity detection
- **Spectrograms**: Time-frequency analysis for dynamic signal characteristics

### **Composite Analysis Suites**
- **Basic Analysis Suite**: Time series + PSD + ACF + histogram in one figure
- **Frequency Analysis Suite**: Comprehensive frequency domain analysis
- **Statistical Analysis Suite**: Distribution analysis, Q-Q plots, and Hurst estimation
- **Complete Analysis Dashboard**: 8-panel comprehensive analysis with all metrics

### **Comparison and Batch Analysis**
- **Signal Comparison**: Multi-signal overlay plots
- **Batch Analysis**: Statistical comparison across multiple signals
- **Contamination Effects**: Visual comparison of different signal contamination types
- **Factory Integration**: Direct analysis of biomedical factory outputs

### **Styling and Customization**
- **Multiple Themes**: Scientific, Clinical, Publication, Dark, Colorful
- **Style Presets**: Paper, Presentation, Poster, Web optimized settings
- **Export Capabilities**: High-quality output in PNG, PDF, SVG formats
- **Configurable Parameters**: Fonts, colors, sizes, DPI settings

## 📊 Architecture

```
BiomedicalTimeSeriesAnalyzer
│
├── Configuration System
│   ├── PlotConfig (themes, styling, export settings)
│   ├── PlotStyleManager (theme application, color palettes)
│   └── Parameter validation and defaults
│
├── Signal Analysis Engine
│   ├── SignalAnalyzer (core analysis methods)
│   ├── Power spectral density estimation
│   ├── Autocorrelation function computation
│   ├── Hurst exponent estimation (R/S method)
│   ├── Stationarity assessment
│   └── Time-frequency analysis
│
├── Individual Plot Methods
│   ├── time_series_plot()
│   ├── psd_plot() 
│   ├── acf_plot()
│   ├── histogram_plot()
│   ├── qq_plot()
│   ├── hurst_analysis_plot()
│   ├── stationarity_plot()
│   └── spectrogram_plot()
│
├── Composite Analysis Suites
│   ├── basic_analysis_suite()
│   ├── frequency_analysis_suite()
│   ├── statistical_analysis_suite()
│   └── complete_analysis_dashboard()
│
├── Comparison and Batch Tools
│   ├── contamination_comparison_plot()
│   ├── batch_compare_signals()
│   └── analyze_factory_output()
│
└── Utility Functions
    ├── get_analysis_summary()
    ├── save_figure()
    ├── set_style_preset()
    └── Factory integration methods
```

## 🚀 Quick Start Guide

### **Basic Usage**

```python
import numpy as np
from biomedical_plotting_system import BiomedicalTimeSeriesAnalyzer, PlotConfig, PlotTheme

# Generate sample signal
fs = 100.0  # Sampling frequency
N = 512     # Number of samples
time_axis = np.arange(N) / fs
signal = np.random.normal(0, 1, N) + 0.3 * np.sin(2 * np.pi * 10 * time_axis)

# Initialize analyzer
config = PlotConfig(theme=PlotTheme.SCIENTIFIC, figure_size=(12, 8))
analyzer = BiomedicalTimeSeriesAnalyzer(config)

# Create basic time series plot
fig, ax = analyzer.time_series_plot(signal, time_axis, 
                                   title="ECG Signal", 
                                   xlabel="Time (s)", 
                                   ylabel="Amplitude (mV)")

# Create comprehensive analysis
fig = analyzer.basic_analysis_suite(signal, time_axis, fs, "ECG Analysis")

# Get detailed analysis summary
summary = analyzer.get_analysis_summary(signal, fs)
print(f"Hurst exponent: {summary['hurst_exponent']:.3f}")
print(f"Peak frequency: {summary['frequency_analysis']['peak_frequency']:.2f} Hz")
```

### **Advanced Analysis Dashboard**

```python
# Create complete analysis dashboard
fig = analyzer.complete_analysis_dashboard(signal, time_axis, fs, "ECG Signal")

# Save high-quality figure
analyzer.save_figure(fig, "ecg_analysis", format='pdf', dpi=300)
```

### **Style Customization**

```python
# Apply different style presets
analyzer.set_style_preset('paper')        # For academic papers
analyzer.set_style_preset('presentation') # For presentations
analyzer.set_style_preset('poster')       # For conference posters
analyzer.set_style_preset('web')          # For web display

# Custom theme configuration
analyzer.set_config(
    theme=PlotTheme.CLINICAL,
    figure_size=(14, 10),
    font_size=12,
    line_width=2.0
)
```

## 📈 Individual Plot Methods

### **Time Series Plot**
```python
fig, ax = analyzer.time_series_plot(
    signal=signal,
    time_axis=time_axis,
    title="Biomedical Signal",
    xlabel="Time (s)",
    ylabel="Amplitude",
    color='blue',
    show_stats=True  # Show mean, std, range
)
```

### **Power Spectral Density**
```python
fig, ax = analyzer.psd_plot(
    signal=signal,
    fs=100.0,
    method='welch',    # 'welch', 'periodogram', 'fft'
    log_scale=True,
    freq_range=(0.1, 50)  # Frequency range to display
)
```

### **Autocorrelation Function**
```python
fig, ax = analyzer.acf_plot(
    signal=signal,
    max_lags=50,
    confidence_bands=True  # Show 95% confidence bands
)
```

### **Histogram with Distribution Analysis**
```python
fig, ax = analyzer.histogram_plot(
    signal=signal,
    bins='auto',
    density=True,
    fit_normal=True  # Overlay normal distribution fit
)
```

### **Hurst Exponent Analysis**
```python
fig, ax = analyzer.hurst_analysis_plot(
    signal=signal,
    max_lag=100,
    title="Long-Range Dependence Analysis"
)
```

### **Stationarity Assessment**
```python
fig, axes = analyzer.stationarity_plot(
    signal=signal,
    window_size=64,  # Window size for analysis
    title="Signal Stationarity Assessment"
)
```

## 🔬 Composite Analysis Suites

### **Basic Analysis Suite**
Four-panel analysis including time series, PSD, ACF, and histogram:

```python
fig = analyzer.basic_analysis_suite(
    signal=signal,
    time_axis=time_axis,
    fs=fs,
    title_prefix="Heart Rate Variability"
)
```

### **Frequency Analysis Suite**
Comprehensive frequency domain analysis:

```python
fig = analyzer.frequency_analysis_suite(
    signal=signal,
    fs=fs,
    title_prefix="EEG Frequency Analysis"
)
```

### **Statistical Analysis Suite**
Distribution analysis, Q-Q plots, Hurst estimation, and stationarity:

```python
fig = analyzer.statistical_analysis_suite(
    signal=signal,
    title_prefix="Statistical Characterization"
)
```

### **Complete Analysis Dashboard**
Comprehensive 8-panel analysis dashboard:

```python
fig = analyzer.complete_analysis_dashboard(
    signal=signal,
    time_axis=time_axis,
    fs=fs,
    signal_name="ECG Lead II"
)
```

## 🔍 Signal Comparison and Batch Analysis

### **Signal Comparison**
```python
signals_dict = {
    'Clean Signal': clean_signal,
    'Noisy Signal': noisy_signal,
    'Filtered Signal': filtered_signal
}

fig = analyzer.contamination_comparison_plot(
    signals_dict=signals_dict,
    time_axis=time_axis,
    title="Signal Processing Comparison"
)
```

### **Batch Statistical Comparison**
```python
fig = analyzer.batch_compare_signals(
    signals_dict=signals_dict,
    fs=fs,
    comparison_metrics=['mean', 'std', 'skewness', 'hurst']
)
```

### **Factory Integration**
Direct analysis of biomedical factory outputs:

```python
from biomedical_timeseries_factory import BiomedicalTimeSeriesFactory, GenerationConfig

# Generate signal using factory
config = GenerationConfig(
    hurst_exponent=0.7,
    non_stationarity=0.2,
    periodicity=0.3
)
factory = BiomedicalTimeSeriesFactory(config)
factory_output = factory.generate(seed=42)

# Analyze factory output directly
fig = analyzer.analyze_factory_output(
    factory_output=factory_output,
    analysis_type='complete',  # 'basic', 'frequency', 'statistical', 'complete'
    show_quality_report=True
)
```

## 🎨 Styling and Themes

### **Available Themes**
- **SCIENTIFIC**: Clean, professional appearance for research
- **CLINICAL**: Medical-focused styling with appropriate colors
- **PUBLICATION**: Black and white, serif fonts for academic papers
- **DARK**: Dark background theme for presentations
- **COLORFUL**: Vibrant colors for educational and outreach materials

### **Style Presets**
- **Paper**: Optimized for academic publications (PDF, 300 DPI)
- **Presentation**: Large fonts and high contrast for slides
- **Poster**: Extra large elements for conference posters
- **Web**: Optimized for web display (96 DPI, PNG)

### **Custom Styling**
```python
# Configure specific parameters
config = PlotConfig(
    theme=PlotTheme.SCIENTIFIC,
    figure_size=(12, 8),
    dpi=150,
    font_size=11,
    title_size=14,
    line_width=1.5,
    grid=True,
    save_format='pdf',
    save_dpi=300
)

analyzer = BiomedicalTimeSeriesAnalyzer(config)
```

## 📊 Analysis Summary and Quality Metrics

### **Get Comprehensive Analysis Summary**
```python
summary = analyzer.get_analysis_summary(signal, fs)

# Access different analysis components
basic_stats = summary['basic_statistics']
freq_analysis = summary['frequency_analysis'] 
hurst_value = summary['hurst_exponent']
stationarity = summary['stationarity']
autocorr = summary['autocorrelation']

print(f"Signal duration: {basic_stats['duration']:.2f} seconds")
print(f"Mean amplitude: {basic_stats['mean']:.3f}")
print(f"Standard deviation: {basic_stats['std']:.3f}")
print(f"Hurst exponent: {hurst_value:.3f}")
print(f"Peak frequency: {freq_analysis['peak_frequency']:.2f} Hz")
print(f"Mean stability: {stationarity['mean_stability']:.3f}")
```

## 💾 Export and Save Options

### **High-Quality Figure Export**
```python
# Save with different formats and settings
analyzer.save_figure(fig, "analysis_results", format='pdf', dpi=300)
analyzer.save_figure(fig, "analysis_results", format='png', dpi=150)
analyzer.save_figure(fig, "analysis_results", format='svg')  # Vector format

# Custom save parameters
analyzer.save_figure(
    fig=fig,
    filename="ecg_analysis_final",
    format='pdf',
    dpi=300,
    bbox_inches='tight',
    facecolor='white',
    edgecolor='none'
)
```

## 🔧 Advanced Usage Examples

### **ECG Analysis Example**
```python
# ECG-specific analysis
analyzer.set_style_preset('clinical')

# Comprehensive ECG analysis
fig = analyzer.complete_analysis_dashboard(
    signal=ecg_signal,
    time_axis=time_axis,
    fs=250.0,  # Typical ECG sampling rate
    signal_name="ECG Lead II"
)

# Focus on clinically relevant frequency range
fig, ax = analyzer.psd_plot(
    signal=ecg_signal,
    fs=250.0,
    freq_range=(0.5, 100),  # ECG frequency range
    title="ECG Power Spectral Density"
)
```

### **EEG Analysis Example**
```python
# EEG-specific analysis with brain wave bands
analyzer.set_config(theme=PlotTheme.SCIENTIFIC)

# Create frequency analysis focusing on EEG bands
fig = analyzer.frequency_analysis_suite(
    signal=eeg_signal,
    fs=128.0,  # Typical EEG sampling rate
    title_prefix="EEG Alpha Rhythm"
)

# Detailed spectral analysis
fig, ax = analyzer.psd_plot(
    signal=eeg_signal,
    fs=128.0,
    freq_range=(0.5, 50),  # EEG frequency range
    log_scale=True
)

# Add brain wave band annotations (manual)
ax.axvspan(0.5, 4, alpha=0.2, color='purple', label='Delta')
ax.axvspan(4, 8, alpha=0.2, color='blue', label='Theta') 
ax.axvspan(8, 13, alpha=0.2, color='green', label='Alpha')
ax.axvspan(13, 30, alpha=0.2, color='orange', label='Beta')
ax.legend()
```

### **HRV Analysis Example**
```python
# Heart rate variability analysis
fig = analyzer.statistical_analysis_suite(
    signal=rr_intervals,
    title_prefix="Heart Rate Variability"
)

# Focus on HRV-specific frequency bands
fig, ax = analyzer.psd_plot(
    signal=rr_intervals,
    fs=4.0,  # Typical HRV sampling rate
    freq_range=(0.04, 0.4),  # HRV frequency bands
    title="HRV Frequency Domain Analysis"
)

# Add HRV band annotations
ax.axvspan(0.04, 0.15, alpha=0.2, color='blue', label='LF Band')
ax.axvspan(0.15, 0.4, alpha=0.2, color='red', label='HF Band')
ax.legend()
```

## 🔍 Troubleshooting and Best Practices

### **Common Issues and Solutions**

1. **Memory Issues with Large Signals**
   ```python
   # For very long signals, use appropriate max_lags
   fig, ax = analyzer.acf_plot(signal, max_lags=min(len(signal)//10, 200))
   
   # Use appropriate PSD parameters
   fig, ax = analyzer.psd_plot(signal, fs, nperseg=min(len(signal)//8, 1024))
   ```

2. **Styling Issues**
   ```python
   # Reset to default theme if styling problems occur
   analyzer.set_config(theme=PlotTheme.SCIENTIFIC)
   
   # Clear matplotlib cache
   plt.style.use('default')
   ```

3. **Export Quality Issues**
   ```python
   # Use appropriate DPI for different outputs
   analyzer.set_config(save_dpi=300)  # High quality
   analyzer.set_config(save_dpi=150)  # Medium quality
   analyzer.set_config(save_dpi=96)   # Web quality
   ```

### **Best Practices**

1. **Signal Preprocessing**
   - Remove DC offset before analysis
   - Apply appropriate filtering if needed
   - Handle missing values and outliers

2. **Analysis Parameter Selection**
   - Choose appropriate frequency ranges for PSD analysis
   - Select suitable window sizes for stationarity assessment
   - Use appropriate lag ranges for autocorrelation analysis

3. **Visualization**
   - Use appropriate themes for target audience
   - Include proper axis labels and units
   - Add legends and annotations where helpful
   - Choose appropriate figure sizes for intended use

4. **Performance Optimization**
   - Use appropriate signal lengths for analysis methods
   - Consider downsampling very high-frequency signals
   - Use batch processing for multiple signals

## 📚 Integration with Biomedical Factory

The plotting system integrates seamlessly with the Biomedical Time Series Factory:

```python
from biomedical_timeseries_factory import BiomedicalTimeSeriesFactory, GenerationConfig
from biomedical_plotting_system import BiomedicalTimeSeriesAnalyzer

# Generate contaminated signal
config = GenerationConfig(
    hurst_exponent=0.75,
    non_stationarity=0.2,
    periodicity=0.3,
    heavy_tail_noise=0.15
)

factory = BiomedicalTimeSeriesFactory(config)
signal, time_axis, metadata = factory.generate(seed=42)

# Analyze generated signal
analyzer = BiomedicalTimeSeriesAnalyzer()
fig = analyzer.analyze_factory_output(
    factory_output=(signal, time_axis, metadata),
    analysis_type='complete'
)

# Compare different contamination levels
contamination_levels = ['clean', 'mild', 'moderate', 'severe']
signals_dict = {}

for level in contamination_levels:
    # Generate signal with different contamination
    config.non_stationarity = {'clean': 0, 'mild': 0.1, 'moderate': 0.3, 'severe': 0.5}[level]
    factory = BiomedicalTimeSeriesFactory(config)
    signal, _, _ = factory.generate()
    signals_dict[level] = signal

# Compare contamination effects
fig = analyzer.batch_compare_signals(signals_dict, fs=100.0)
```

## 📖 API Reference Summary

### **Main Class**
- `BiomedicalTimeSeriesAnalyzer(config=None)`: Main analyzer class

### **Individual Plot Methods**
- `time_series_plot(signal, time_axis, ...)`: Basic time series visualization
- `psd_plot(signal, fs, method, ...)`: Power spectral density analysis
- `acf_plot(signal, max_lags, ...)`: Autocorrelation function
- `histogram_plot(signal, bins, ...)`: Distribution analysis
- `qq_plot(signal, distribution, ...)`: Quantile-quantile plots
- `hurst_analysis_plot(signal, ...)`: Long-range dependence analysis
- `stationarity_plot(signal, ...)`: Non-stationarity assessment
- `spectrogram_plot(signal, fs, ...)`: Time-frequency analysis

### **Composite Analysis Suites**
- `basic_analysis_suite(signal, time_axis, fs, ...)`: 4-panel basic analysis
- `frequency_analysis_suite(signal, fs, ...)`: Frequency domain analysis
- `statistical_analysis_suite(signal, ...)`: Statistical characterization
- `complete_analysis_dashboard(signal, time_axis, fs, ...)`: Comprehensive 8-panel analysis

### **Comparison and Batch Methods**
- `contamination_comparison_plot(signals_dict, ...)`: Multi-signal comparison
- `batch_compare_signals(signals_dict, fs, ...)`: Batch statistical analysis
- `analyze_factory_output(factory_output, ...)`: Direct factory integration

### **Utility Methods**
- `get_analysis_summary(signal, fs)`: Comprehensive analysis summary
- `save_figure(fig, filename, ...)`: High-quality figure export
- `set_config(**kwargs)`: Update configuration parameters
- `set_style_preset(preset)`: Apply predefined style presets

## 🎓 Educational Applications

The plotting system is designed for educational use in biomedical signal processing:

### **Interactive Learning**
```python
# Create educational comparison
signals = {
    'Original Signal': original_signal,
    'After Filtering': filtered_signal,
    'With Noise': noisy_signal
}

# Show processing effects
fig = analyzer.contamination_comparison_plot(signals, time_axis, 
                                           "Signal Processing Effects")

# Detailed analysis for each step
for name, signal in signals.items():
    fig = analyzer.basic_analysis_suite(signal, time_axis, fs, name)
    analyzer.save_figure(fig, f"educational_{name.lower().replace(' ', '_')}")
```

### **Algorithm Validation**
```python
# Compare algorithm performance
algorithms = {
    'Algorithm A': processed_signal_a,
    'Algorithm B': processed_signal_b,
    'Ground Truth': reference_signal
}

fig = analyzer.batch_compare_signals(algorithms, fs, 
                                   ['mean', 'std', 'hurst', 'stationarity'])
```

## 🔮 Future Extensions

The system is designed for extensibility:

### **Custom Plot Methods**
```python
# Example of adding custom analysis method
def custom_analysis_plot(self, signal, **kwargs):
    # Custom analysis implementation
    fig, ax = self._setup_figure()
    # ... custom plotting code ...
    return fig, ax

# Add to analyzer class
BiomedicalTimeSeriesAnalyzer.custom_analysis_plot = custom_analysis_plot
```

### **New Themes**
```python
# Add custom color palette
PlotStyleManager.PALETTES[PlotTheme.CUSTOM] = ['#ff0000', '#00ff00', '#0000ff']
```

### **Integration Extensions**
- Real-time signal analysis
- Interactive plotting with widgets
- Advanced statistical tests
- Machine learning integration
- Multi-channel signal analysis

## 📝 Summary

The Biomedical Time Series Analytical Plotting System provides a comprehensive, professional-grade toolkit for biomedical signal analysis and visualization. With its modular architecture, extensive customization options, and seamless integration capabilities, it serves as a complete solution for research, clinical, and educational applications in biomedical signal processing.

**Key Benefits:**
- **Complete Analysis Pipeline**: From basic visualization to comprehensive analysis dashboards
- **Publication Ready**: High-quality output suitable for academic and clinical publications  
- **Easy Integration**: Seamless compatibility with existing biomedical analysis workflows
- **Extensible Design**: Easy to customize and extend for specific research needs
- **Educational Value**: Excellent for teaching biomedical signal processing concepts

The system is ready for immediate use in biomedical research, clinical applications, and educational settings, providing researchers and practitioners with powerful tools for understanding and communicating complex biomedical signal characteristics.