# Biomedical Time Series Data Model and Analysis Framework - API Documentation

**Version:** 1.0.0  
**Date:** October 17, 2025  
**Authors:** AI Research Assistant  
**License:** Open Source

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Concepts](#core-concepts)
5. [API Reference](#api-reference)
6. [Examples and Tutorials](#examples-and-tutorials)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Contributing](#contributing)

---

## Overview

The **Biomedical Time Series Data Model and Analysis Framework** is a comprehensive Python library for generating, analyzing, and visualizing realistic biomedical time series data. The framework consists of two main components:

1. **Biomedical Time Series Factory**: A sophisticated generative model that creates realistic physiological signals with controllable contamination effects
2. **Analytical Plotting System**: A comprehensive visualization and analysis toolkit for biomedical signal processing

### Key Features

- **Realistic Signal Generation**: Fractional Gaussian models with biomedically validated parameters
- **Controllable Contamination**: Non-stationarity, periodicity, seasonality, and heavy-tail noise
- **Comprehensive Analysis**: Power spectral density, autocorrelation, Hurst analysis, stationarity assessment
- **Professional Visualization**: Publication-ready plots with multiple themes and export formats
- **Batch Processing**: Efficient analysis of multiple signals with comparative metrics
- **Clinical Integration**: Preset configurations for common biomedical signals (ECG, EEG, HRV, etc.)

### Applications

- **Research**: Algorithm development, validation, and benchmarking
- **Clinical**: Signal quality assessment and biomedical device testing
- **Education**: Interactive biomedical signal processing education
- **Industry**: Medical device validation and regulatory compliance

---

## Installation

### Prerequisites

```bash
# Required Python version
Python >= 3.8

# Core dependencies
numpy >= 1.20.0
scipy >= 1.7.0
matplotlib >= 3.5.0
pandas >= 1.3.0
seaborn >= 0.11.0
```

### Installation Methods

#### Method 1: Direct Installation (Recommended)

```bash
# Clone or download the framework files
# Place the following files in your working directory:
# - biomedical_timeseries_factory.py
# - biomedical_plotting_system.py

# Install dependencies
pip install numpy scipy matplotlib pandas seaborn
```

#### Method 2: Environment Setup

```bash
# Create virtual environment
python -m venv biomedical_env
source biomedical_env/bin/activate  # On Windows: biomedical_env\\Scripts\\activate

# Install dependencies
pip install numpy scipy matplotlib pandas seaborn

# Verify installation
python -c "import numpy, scipy, matplotlib; print('Dependencies installed successfully')"
```

#### Method 3: Conda Environment

```bash
# Create conda environment
conda create -n biomedical python=3.9
conda activate biomedical

# Install dependencies
conda install numpy scipy matplotlib pandas seaborn

# Place framework files in working directory
```

### Verification

```python
# Test installation
try:
    from biomedical_timeseries_factory import BiomedicalTimeSeriesFactory, GenerationConfig
    from biomedical_plotting_system import BiomedicalTimeSeriesAnalyzer, PlotConfig
    print("✅ Framework installed successfully!")
except ImportError as e:
    print(f"❌ Installation error: {e}")
```

---

## Quick Start

### Basic Signal Generation

```python
import numpy as np
from biomedical_timeseries_factory import BiomedicalTimeSeriesFactory, GenerationConfig, BiomedicalSignalType

# Create configuration for ECG-like signal
config = GenerationConfig(
    hurst_exponent=0.75,
    mean=0.0,
    std=1.0,
    length=1024,
    sampling_rate=250.0,
    signal_type=BiomedicalSignalType.ECG,
    non_stationarity=0.1,
    periodicity=0.2,
    heavy_tail_noise=0.05
)

# Generate signal
factory = BiomedicalTimeSeriesFactory(config)
signal, time_axis, metadata = factory.generate(seed=42)

print(f"Generated {metadata['signal_type']} signal")
print(f"Length: {len(signal)}, Duration: {time_axis[-1]:.2f}s")
```

### Basic Signal Analysis

```python
from biomedical_plotting_system import BiomedicalTimeSeriesAnalyzer, PlotConfig

# Initialize analyzer
analyzer = BiomedicalTimeSeriesAnalyzer()

# Create comprehensive analysis
fig = analyzer.complete_analysis_dashboard(
    signal=signal,
    time_axis=time_axis,
    fs=config.sampling_rate,
    signal_name="ECG Signal"
)

# Get analysis summary
summary = analyzer.get_analysis_summary(signal, config.sampling_rate)
print(f"Hurst exponent: {summary['hurst_exponent']:.3f}")
print(f"Peak frequency: {summary['frequency_analysis']['peak_frequency']:.2f} Hz")
```

### Integrated Workflow

```python
# Complete workflow: Generate → Analyze → Visualize
from biomedical_timeseries_factory import BiomedicalPresets

# Use preset configuration
config = BiomedicalPresets.create_ecg_config('moderate')
factory = BiomedicalTimeSeriesFactory(config)

# Generate signal
factory_output = factory.generate(seed=42)

# Analyze directly
analyzer = BiomedicalTimeSeriesAnalyzer()
fig = analyzer.analyze_factory_output(
    factory_output=factory_output,
    analysis_type='complete',
    show_quality_report=True
)

# Save results
analyzer.save_figure(fig, "ecg_analysis", format='pdf', dpi=300)
```

---

## Core Concepts

### Architecture Overview

```
Biomedical Time Series Framework
│
├── Generation Layer
│   ├── FractionalGaussianBase (Core signal generation)
│   ├── ContaminationModules (Non-stationarity, periodicity, etc.)
│   ├── BiomedicalTimeSeriesFactory (Main factory class)
│   └── ParameterValidation (Biomedical constraints)
│
├── Analysis Layer
│   ├── SignalAnalyzer (Core analysis methods)
│   ├── QualityAssessment (Signal validation)
│   └── BiomedicalTimeSeriesAnalyzer (Main analyzer class)
│
└── Visualization Layer
    ├── PlotStyleManager (Themes and styling)
    ├── Individual plot methods
    ├── Composite analysis suites
    └── Export capabilities
```

### Key Concepts

#### Fractional Gaussian Models
- **Fractional Gaussian Noise (fGn)**: Stationary process with long-range dependence
- **Fractional Brownian Motion (fBm)**: Non-stationary cumulative process
- **Hurst Parameter (H)**: Controls long-range dependence (0 < H < 1)
  - H < 0.5: Anti-persistent (mean-reverting)
  - H = 0.5: Standard Brownian motion
  - H > 0.5: Persistent (trending)

#### Contamination Types
1. **Non-stationarity**: Time-varying mean and variance
2. **Periodicity**: Sinusoidal components with amplitude modulation
3. **Seasonality**: Long-term cyclical patterns
4. **Heavy-tail Noise**: α-stable distributions and extreme events

#### Biomedical Signal Types
- **ECG**: Electrocardiogram (H: 0.5-0.9, 0.5-100 Hz)
- **EEG**: Electroencephalogram (H: 0.6-0.95, 0.5-50 Hz)
- **HRV**: Heart Rate Variability (H: 0.5-0.85, 0.001-0.5 Hz)
- **EMG**: Electromyogram (H: 0.4-0.7, 10-500 Hz)
- **PPG**: Photoplethysmogram (H: 0.55-0.8, 0.5-20 Hz)

---

## API Reference

### Biomedical Time Series Factory

#### Core Classes

##### `GenerationConfig`

Configuration dataclass for signal generation parameters.

```python
@dataclass
class GenerationConfig:
    """Configuration for biomedical time series generation"""
    
    # Core parameters
    hurst_exponent: float = 0.7
    mean: float = 0.0
    std: float = 1.0
    length: int = 1024
    sampling_rate: float = 1.0
    signal_type: Optional[BiomedicalSignalType] = None
    
    # Contamination intensities (0 = none, 1 = severe)
    non_stationarity: float = 0.0
    periodicity: float = 0.0
    seasonality: float = 0.0
    heavy_tail_noise: float = 0.0
    
    # Advanced parameters
    contamination_params: Dict = field(default_factory=dict)
    validate_parameters: bool = True
    compute_quality_metrics: bool = True
```

**Parameters:**
- `hurst_exponent` (float): Hurst parameter for long-range dependence (0.01-0.99)
- `mean` (float): Signal mean value
- `std` (float): Signal standard deviation
- `length` (int): Number of sample points
- `sampling_rate` (float): Sampling frequency in Hz
- `signal_type` (BiomedicalSignalType): Type of biomedical signal for validation
- `non_stationarity` (float): Non-stationarity contamination intensity (0-1)
- `periodicity` (float): Periodic contamination intensity (0-1)
- `seasonality` (float): Seasonal contamination intensity (0-1)
- `heavy_tail_noise` (float): Heavy-tail noise contamination intensity (0-1)
- `contamination_params` (Dict): Advanced contamination parameters
- `validate_parameters` (bool): Enable parameter validation
- `compute_quality_metrics` (bool): Compute quality metrics during generation

##### `BiomedicalTimeSeriesFactory`

Main factory class for generating biomedical time series.

```python
class BiomedicalTimeSeriesFactory:
    """Comprehensive factory for generating biomedical time series"""
    
    def __init__(self, config: GenerationConfig = None)
    def generate(self, seed: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray, Dict]
    def set_config(self, **kwargs)
    def get_last_quality_report(self) -> str
```

**Methods:**

###### `__init__(self, config: GenerationConfig = None)`

Initialize the factory with configuration.

**Parameters:**
- `config` (GenerationConfig): Configuration object for generation parameters

**Example:**
```python
config = GenerationConfig(hurst_exponent=0.8, length=512)
factory = BiomedicalTimeSeriesFactory(config)
```

###### `generate(self, seed: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray, Dict]`

Generate biomedical time series with specified contaminations.

**Parameters:**
- `seed` (int, optional): Random seed for reproducibility

**Returns:**
- `signal` (np.ndarray): Generated signal array
- `time_axis` (np.ndarray): Corresponding time axis
- `metadata` (Dict): Generation metadata including configuration and quality metrics

**Example:**
```python
signal, time_axis, metadata = factory.generate(seed=42)
print(f"Generated signal: {len(signal)} samples")
print(f"Quality metrics: {metadata['quality_metrics']}")
```

###### `set_config(self, **kwargs)`

Update configuration parameters.

**Parameters:**
- `**kwargs`: Configuration parameters to update

**Example:**
```python
factory.set_config(hurst_exponent=0.9, periodicity=0.3)
```

###### `get_last_quality_report(self) -> str`

Get formatted quality report for last generated signal.

**Returns:**
- `report` (str): Formatted quality report

**Example:**
```python
print(factory.get_last_quality_report())
```

#### Preset Configurations

##### `BiomedicalPresets`

Static class providing preset configurations for common biomedical signals.

```python
class BiomedicalPresets:
    """Preset configurations for common biomedical signal types"""
    
    @staticmethod
    def create_ecg_config(contamination_level: str = 'mild') -> GenerationConfig
    
    @staticmethod
    def create_eeg_config(contamination_level: str = 'mild') -> GenerationConfig
    
    @staticmethod
    def create_hrv_config(contamination_level: str = 'mild') -> GenerationConfig
```

**Methods:**

###### `create_ecg_config(contamination_level: str = 'mild') -> GenerationConfig`

Create ECG signal configuration.

**Parameters:**
- `contamination_level` (str): Contamination level ('clean', 'mild', 'moderate', 'severe')

**Returns:**
- `config` (GenerationConfig): ECG-specific configuration

**Example:**
```python
ecg_config = BiomedicalPresets.create_ecg_config('moderate')
factory = BiomedicalTimeSeriesFactory(ecg_config)
```

###### `create_eeg_config(contamination_level: str = 'mild') -> GenerationConfig`

Create EEG signal configuration.

**Parameters:**
- `contamination_level` (str): Contamination level ('clean', 'mild', 'moderate', 'severe')

**Returns:**
- `config` (GenerationConfig): EEG-specific configuration

**Example:**
```python
eeg_config = BiomedicalPresets.create_eeg_config('severe')
factory = BiomedicalTimeSeriesFactory(eeg_config)
```

###### `create_hrv_config(contamination_level: str = 'mild') -> GenerationConfig`

Create Heart Rate Variability signal configuration.

**Parameters:**
- `contamination_level` (str): Contamination level ('clean', 'mild', 'moderate', 'severe')

**Returns:**
- `config` (GenerationConfig): HRV-specific configuration

**Example:**
```python
hrv_config = BiomedicalPresets.create_hrv_config('clean')
factory = BiomedicalTimeSeriesFactory(hrv_config)
```

#### Enumerations

##### `BiomedicalSignalType`

Enumeration of supported biomedical signal types.

```python
class BiomedicalSignalType(Enum):
    ECG = "electrocardiogram"
    EEG = "electroencephalogram"
    EMG = "electromyogram"
    HRV = "heart_rate_variability"
    PPG = "photoplethysmogram"
    BP = "blood_pressure"
    RESP = "respiration"
    GSR = "galvanic_skin_response"
```

### Analytical Plotting System

#### Core Classes

##### `PlotConfig`

Configuration dataclass for plot styling and appearance.

```python
@dataclass
class PlotConfig:
    """Configuration for plot styling and appearance"""
    
    theme: PlotTheme = PlotTheme.SCIENTIFIC
    figure_size: Tuple[float, float] = (12, 8)
    dpi: int = 100
    font_size: int = 12
    title_size: int = 14
    label_size: int = 11
    tick_size: int = 10
    line_width: float = 1.5
    grid: bool = True
    grid_alpha: float = 0.3
    color_palette: Optional[List[str]] = None
    save_format: str = 'png'
    save_dpi: int = 300
```

**Parameters:**
- `theme` (PlotTheme): Visual theme for plots
- `figure_size` (Tuple[float, float]): Default figure size in inches
- `dpi` (int): Display resolution
- `font_size` (int): Base font size
- `title_size` (int): Title font size
- `label_size` (int): Axis label font size
- `tick_size` (int): Tick label font size
- `line_width` (float): Default line width
- `grid` (bool): Enable grid lines
- `grid_alpha` (float): Grid transparency
- `color_palette` (List[str], optional): Custom color palette
- `save_format` (str): Default save format ('png', 'pdf', 'svg')
- `save_dpi` (int): Save resolution

##### `BiomedicalTimeSeriesAnalyzer`

Main analyzer class for biomedical time series analysis and visualization.

```python
class BiomedicalTimeSeriesAnalyzer:
    """Comprehensive analyzer for biomedical time series"""
    
    def __init__(self, config: PlotConfig = None)
    def set_config(self, **kwargs)
    
    # Individual plot methods
    def time_series_plot(self, signal, time_axis=None, **kwargs) -> Tuple[plt.Figure, plt.Axes]
    def psd_plot(self, signal, fs=1.0, **kwargs) -> Tuple[plt.Figure, plt.Axes]
    def acf_plot(self, signal, max_lags=None, **kwargs) -> Tuple[plt.Figure, plt.Axes]
    def histogram_plot(self, signal, **kwargs) -> Tuple[plt.Figure, plt.Axes]
    def qq_plot(self, signal, distribution='norm', **kwargs) -> Tuple[plt.Figure, plt.Axes]
    def hurst_analysis_plot(self, signal, **kwargs) -> Tuple[plt.Figure, plt.Axes]
    def stationarity_plot(self, signal, **kwargs) -> Tuple[plt.Figure, plt.Axes]
    def spectrogram_plot(self, signal, fs=1.0, **kwargs) -> Tuple[plt.Figure, plt.Axes]
    
    # Composite analysis suites
    def basic_analysis_suite(self, signal, time_axis=None, fs=1.0, **kwargs) -> plt.Figure
    def frequency_analysis_suite(self, signal, fs=1.0, **kwargs) -> plt.Figure
    def statistical_analysis_suite(self, signal, **kwargs) -> plt.Figure
    def complete_analysis_dashboard(self, signal, time_axis=None, fs=1.0, **kwargs) -> plt.Figure
    
    # Comparison and batch analysis
    def contamination_comparison_plot(self, signals_dict, **kwargs) -> plt.Figure
    def batch_compare_signals(self, signals_dict, fs=1.0, **kwargs) -> plt.Figure
    def analyze_factory_output(self, factory_output, **kwargs) -> plt.Figure
    
    # Utility methods
    def get_analysis_summary(self, signal, fs=1.0) -> Dict
    def save_figure(self, fig, filename, **kwargs)
    def set_style_preset(self, preset: str)
```

#### Individual Plot Methods

##### `time_series_plot()`

Create time series plot with optional statistics overlay.

```python
def time_series_plot(self, signal: np.ndarray, time_axis: Optional[np.ndarray] = None,
                    title: str = "Time Series", xlabel: str = "Time", ylabel: str = "Amplitude",
                    color: Optional[str] = None, figsize: Optional[Tuple[float, float]] = None,
                    show_stats: bool = True, **kwargs) -> Tuple[plt.Figure, plt.Axes]
```

**Parameters:**
- `signal` (np.ndarray): Input signal array
- `time_axis` (np.ndarray, optional): Time axis values
- `title` (str): Plot title
- `xlabel`, `ylabel` (str): Axis labels
- `color` (str, optional): Line color
- `figsize` (Tuple[float, float], optional): Figure size override
- `show_stats` (bool): Show statistics text box
- `**kwargs`: Additional matplotlib plot parameters

**Returns:**
- `fig` (plt.Figure): Figure object
- `ax` (plt.Axes): Axes object

**Example:**
```python
fig, ax = analyzer.time_series_plot(
    signal=ecg_signal,
    time_axis=time_axis,
    title="ECG Lead II",
    xlabel="Time (s)",
    ylabel="Amplitude (mV)",
    color='blue',
    show_stats=True
)
```

##### `psd_plot()`

Create Power Spectral Density plot with logarithmic scaling options.

```python
def psd_plot(self, signal: np.ndarray, fs: float = 1.0, method: str = 'welch',
            title: str = "Power Spectral Density", log_scale: bool = True,
            color: Optional[str] = None, figsize: Optional[Tuple[float, float]] = None,
            freq_range: Optional[Tuple[float, float]] = None, **kwargs) -> Tuple[plt.Figure, plt.Axes]
```

**Parameters:**
- `signal` (np.ndarray): Input signal array
- `fs` (float): Sampling frequency in Hz
- `method` (str): PSD estimation method ('welch', 'periodogram', 'fft')
- `title` (str): Plot title
- `log_scale` (bool): Use logarithmic scaling for both axes
- `color` (str, optional): Line color
- `figsize` (Tuple[float, float], optional): Figure size override
- `freq_range` (Tuple[float, float], optional): Frequency range to display (min_freq, max_freq)
- `**kwargs`: Additional parameters for PSD computation

**Returns:**
- `fig` (plt.Figure): Figure object
- `ax` (plt.Axes): Axes object

**Example:**
```python
fig, ax = analyzer.psd_plot(
    signal=eeg_signal,
    fs=128.0,
    method='welch',
    freq_range=(0.5, 50),
    title="EEG Power Spectral Density"
)
```

##### `acf_plot()`

Create Autocorrelation Function plot with confidence bands.

```python
def acf_plot(self, signal: np.ndarray, max_lags: Optional[int] = None,
            title: str = "Autocorrelation Function", color: Optional[str] = None,
            figsize: Optional[Tuple[float, float]] = None, 
            confidence_bands: bool = True, **kwargs) -> Tuple[plt.Figure, plt.Axes]
```

**Parameters:**
- `signal` (np.ndarray): Input signal array
- `max_lags` (int, optional): Maximum number of lags to compute
- `title` (str): Plot title
- `color` (str, optional): Line color
- `figsize` (Tuple[float, float], optional): Figure size override
- `confidence_bands` (bool): Show 95% confidence bands
- `**kwargs`: Additional parameters for ACF computation

**Returns:**
- `fig` (plt.Figure): Figure object
- `ax` (plt.Axes): Axes object

**Example:**
```python
fig, ax = analyzer.acf_plot(
    signal=hrv_signal,
    max_lags=50,
    confidence_bands=True,
    title="HRV Autocorrelation"
)
```

##### `histogram_plot()`

Create histogram plot with optional normal distribution fitting.

```python
def histogram_plot(self, signal: np.ndarray, bins: Union[int, str] = 'auto',
                  title: str = "Signal Distribution", density: bool = True,
                  color: Optional[str] = None, figsize: Optional[Tuple[float, float]] = None,
                  fit_normal: bool = True, **kwargs) -> Tuple[plt.Figure, plt.Axes]
```

**Parameters:**
- `signal` (np.ndarray): Input signal array
- `bins` (int or str): Number of bins or binning strategy
- `title` (str): Plot title
- `density` (bool): Normalize histogram to density
- `color` (str, optional): Histogram color
- `figsize` (Tuple[float, float], optional): Figure size override
- `fit_normal` (bool): Overlay normal distribution fit
- `**kwargs`: Additional histogram parameters

**Returns:**
- `fig` (plt.Figure): Figure object
- `ax` (plt.Axes): Axes object

**Example:**
```python
fig, ax = analyzer.histogram_plot(
    signal=signal,
    bins=30,
    fit_normal=True,
    title="Signal Amplitude Distribution"
)
```

##### `hurst_analysis_plot()`

Create Hurst exponent analysis plot using R/S statistics.

```python
def hurst_analysis_plot(self, signal: np.ndarray, max_lag: Optional[int] = None,
                       title: str = "Hurst Exponent Analysis", color: Optional[str] = None,
                       figsize: Optional[Tuple[float, float]] = None) -> Tuple[plt.Figure, plt.Axes]
```

**Parameters:**
- `signal` (np.ndarray): Input signal array
- `max_lag` (int, optional): Maximum lag for R/S analysis
- `title` (str): Plot title
- `color` (str, optional): Line color
- `figsize` (Tuple[float, float], optional): Figure size override

**Returns:**
- `fig` (plt.Figure): Figure object
- `ax` (plt.Axes): Axes object

**Example:**
```python
fig, ax = analyzer.hurst_analysis_plot(
    signal=fbm_signal,
    max_lag=100,
    title="Long-Range Dependence Analysis"
)
```

##### `stationarity_plot()`

Create stationarity assessment plot showing windowed statistics.

```python
def stationarity_plot(self, signal: np.ndarray, window_size: Optional[int] = None,
                     title: str = "Stationarity Assessment", 
                     figsize: Optional[Tuple[float, float]] = None) -> Tuple[plt.Figure, plt.Axes]
```

**Parameters:**
- `signal` (np.ndarray): Input signal array
- `window_size` (int, optional): Window size for windowed statistics
- `title` (str): Plot title
- `figsize` (Tuple[float, float], optional): Figure size override

**Returns:**
- `fig` (plt.Figure): Figure object
- `axes` (Tuple[plt.Axes, plt.Axes]): Tuple of axes objects (mean, variance)

**Example:**
```python
fig, (ax1, ax2) = analyzer.stationarity_plot(
    signal=nonstationary_signal,
    window_size=64,
    title="Non-stationarity Assessment"
)
```

##### `spectrogram_plot()`

Create spectrogram plot for time-frequency analysis.

```python
def spectrogram_plot(self, signal: np.ndarray, fs: float = 1.0, 
                    title: str = "Spectrogram", figsize: Optional[Tuple[float, float]] = None,
                    **kwargs) -> Tuple[plt.Figure, plt.Axes]
```

**Parameters:**
- `signal` (np.ndarray): Input signal array
- `fs` (float): Sampling frequency in Hz
- `title` (str): Plot title
- `figsize` (Tuple[float, float], optional): Figure size override
- `**kwargs`: Additional spectrogram parameters (nperseg, noverlap)

**Returns:**
- `fig` (plt.Figure): Figure object
- `ax` (plt.Axes): Axes object

**Example:**
```python
fig, ax = analyzer.spectrogram_plot(
    signal=eeg_signal,
    fs=128.0,
    title="EEG Time-Frequency Analysis",
    nperseg=256,
    noverlap=128
)
```

#### Composite Analysis Suites

##### `basic_analysis_suite()`

Create basic analysis suite with time series, PSD, ACF, and histogram.

```python
def basic_analysis_suite(self, signal: np.ndarray, time_axis: Optional[np.ndarray] = None,
                       fs: float = 1.0, title_prefix: str = "Signal Analysis",
                       figsize: Optional[Tuple[float, float]] = None) -> plt.Figure
```

**Parameters:**
- `signal` (np.ndarray): Input signal array
- `time_axis` (np.ndarray, optional): Time axis values
- `fs` (float): Sampling frequency in Hz
- `title_prefix` (str): Prefix for subplot titles
- `figsize` (Tuple[float, float], optional): Figure size override

**Returns:**
- `fig` (plt.Figure): Figure object with 4 subplots

**Example:**
```python
fig = analyzer.basic_analysis_suite(
    signal=ecg_signal,
    time_axis=time_axis,
    fs=250.0,
    title_prefix="ECG Analysis"
)
```

##### `complete_analysis_dashboard()`

Create comprehensive analysis dashboard with 8 panels.

```python
def complete_analysis_dashboard(self, signal: np.ndarray, time_axis: Optional[np.ndarray] = None,
                              fs: float = 1.0, signal_name: str = "Signal",
                              figsize: Optional[Tuple[float, float]] = None) -> plt.Figure
```

**Parameters:**
- `signal` (np.ndarray): Input signal array
- `time_axis` (np.ndarray, optional): Time axis values
- `fs` (float): Sampling frequency in Hz
- `signal_name` (str): Name for the signal
- `figsize` (Tuple[float, float], optional): Figure size override

**Returns:**
- `fig` (plt.Figure): Figure object with 8 analysis panels

**Example:**
```python
fig = analyzer.complete_analysis_dashboard(
    signal=eeg_signal,
    time_axis=time_axis,
    fs=128.0,
    signal_name="EEG Channel 1"
)
```

#### Comparison and Batch Analysis

##### `contamination_comparison_plot()`

Create comparison plot for different contamination effects.

```python
def contamination_comparison_plot(self, signals_dict: Dict[str, np.ndarray], 
                                time_axis: Optional[np.ndarray] = None,
                                title: str = "Contamination Effects Comparison",
                                figsize: Optional[Tuple[float, float]] = None) -> plt.Figure
```

**Parameters:**
- `signals_dict` (Dict[str, np.ndarray]): Dictionary with signal names and arrays
- `time_axis` (np.ndarray, optional): Time axis values
- `title` (str): Overall plot title
- `figsize` (Tuple[float, float], optional): Figure size override

**Returns:**
- `fig` (plt.Figure): Figure object with stacked subplots

**Example:**
```python
signals = {
    'Clean Signal': clean_signal,
    'With Noise': noisy_signal,
    'Non-stationary': nonstat_signal
}

fig = analyzer.contamination_comparison_plot(
    signals_dict=signals,
    time_axis=time_axis,
    title="Signal Processing Effects"
)
```

##### `batch_compare_signals()`

Compare multiple signals with statistical metrics.

```python
def batch_compare_signals(self, signals_dict: Dict[str, Union[np.ndarray, Tuple]],
                        fs: float = 1.0, comparison_metrics: List[str] = None) -> plt.Figure
```

**Parameters:**
- `signals_dict` (Dict): Dictionary with signal names and arrays or factory outputs
- `fs` (float): Sampling frequency in Hz
- `comparison_metrics` (List[str], optional): Metrics to compare ('mean', 'std', 'skewness', 'kurtosis', 'hurst')

**Returns:**
- `fig` (plt.Figure): Figure object with comparison plots

**Example:**
```python
fig = analyzer.batch_compare_signals(
    signals_dict=signals,
    fs=100.0,
    comparison_metrics=['mean', 'std', 'hurst', 'skewness']
)
```

##### `analyze_factory_output()`

Analyze output directly from BiomedicalTimeSeriesFactory.

```python
def analyze_factory_output(self, factory_output: Tuple, 
                         analysis_type: str = 'complete',
                         show_quality_report: bool = True) -> plt.Figure
```

**Parameters:**
- `factory_output` (Tuple): Output from factory.generate() (signal, time_axis, metadata)
- `analysis_type` (str): Type of analysis ('basic', 'frequency', 'statistical', 'complete')
- `show_quality_report` (bool): Print quality report

**Returns:**
- `fig` (plt.Figure): Analysis figure

**Example:**
```python
# Generate signal
factory_output = factory.generate(seed=42)

# Analyze directly
fig = analyzer.analyze_factory_output(
    factory_output=factory_output,
    analysis_type='complete',
    show_quality_report=True
)
```

#### Utility Methods

##### `get_analysis_summary()`

Get comprehensive analysis summary as dictionary.

```python
def get_analysis_summary(self, signal: np.ndarray, fs: float = 1.0) -> Dict
```

**Parameters:**
- `signal` (np.ndarray): Input signal array
- `fs` (float): Sampling frequency in Hz

**Returns:**
- `summary` (Dict): Comprehensive analysis results

**Structure:**
```python
{
    'basic_statistics': {
        'length': int,
        'duration': float,
        'sampling_rate': float,
        'mean': float,
        'std': float,
        'var': float,
        'min': float,
        'max': float,
        'range': float,
        'skewness': float,
        'kurtosis': float
    },
    'frequency_analysis': {
        'peak_frequency': float,
        'mean_frequency': float,
        'total_power': float
    },
    'hurst_exponent': float,
    'stationarity': {
        'mean_stability': float,
        'variance_stability': float
    },
    'autocorrelation': {
        'lag_1': float,
        'lag_5': float,
        'lag_10': float
    }
}
```

**Example:**
```python
summary = analyzer.get_analysis_summary(signal, fs=250.0)
print(f"Signal duration: {summary['basic_statistics']['duration']:.2f} s")
print(f"Hurst exponent: {summary['hurst_exponent']:.3f}")
print(f"Peak frequency: {summary['frequency_analysis']['peak_frequency']:.2f} Hz")
```

##### `save_figure()`

Save figure with high-quality formatting.

```python
def save_figure(self, fig: plt.Figure, filename: str, 
               format: Optional[str] = None, dpi: Optional[int] = None,
               bbox_inches: str = 'tight', **kwargs)
```

**Parameters:**
- `fig` (plt.Figure): Figure to save
- `filename` (str): Output filename
- `format` (str, optional): File format ('png', 'pdf', 'svg', 'eps')
- `dpi` (int, optional): Resolution for raster formats
- `bbox_inches` (str): Bounding box specification
- `**kwargs`: Additional savefig parameters

**Example:**
```python
# Save high-quality PDF
analyzer.save_figure(fig, "analysis_results", format='pdf', dpi=300)

# Save PNG for web
analyzer.save_figure(fig, "web_figure", format='png', dpi=150)
```

##### `set_style_preset()`

Apply predefined style presets.

```python
def set_style_preset(self, preset: str)
```

**Parameters:**
- `preset` (str): Style preset name ('paper', 'presentation', 'poster', 'web')

**Presets:**
- `'paper'`: Publication-ready formatting (PDF, 300 DPI, serif fonts)
- `'presentation'`: Large fonts and high contrast for slides
- `'poster'`: Extra large elements for conference posters
- `'web'`: Web-optimized formatting (PNG, 96 DPI)

**Example:**
```python
# Configure for academic paper
analyzer.set_style_preset('paper')

# Configure for presentation
analyzer.set_style_preset('presentation')
```

#### Enumerations

##### `PlotTheme`

Available plot themes for visualization.

```python
class PlotTheme(Enum):
    SCIENTIFIC = "scientific"      # Clean, professional research style
    CLINICAL = "clinical"          # Medical-focused color scheme
    PUBLICATION = "publication"    # Black/white, serif fonts for papers
    DARK = "dark"                 # Dark background for presentations
    COLORFUL = "colorful"         # Vibrant colors for education
```

### Signal Analysis Methods

#### `SignalAnalyzer`

Static class providing core signal analysis methods.

```python
class SignalAnalyzer:
    """Core signal analysis methods for biomedical time series"""
    
    @staticmethod
    def compute_psd(signal, fs=1.0, method='welch', nperseg=None) -> Tuple[np.ndarray, np.ndarray]
    
    @staticmethod
    def compute_acf(signal, max_lags=None, normalized=True) -> Tuple[np.ndarray, np.ndarray]
    
    @staticmethod
    def compute_spectrogram(signal, fs=1.0, nperseg=None, noverlap=None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]
    
    @staticmethod
    def estimate_hurst_rs(signal, max_lag=None) -> Tuple[float, np.ndarray, np.ndarray]
    
    @staticmethod
    def windowed_statistics(signal, window_size=None) -> Dict
```

##### `compute_psd()`

Compute Power Spectral Density using various methods.

```python
@staticmethod
def compute_psd(signal: np.ndarray, fs: float = 1.0, method: str = 'welch', 
               nperseg: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]
```

**Parameters:**
- `signal` (np.ndarray): Input signal
- `fs` (float): Sampling frequency
- `method` (str): Estimation method ('welch', 'periodogram', 'fft')
- `nperseg` (int, optional): Length of each segment for Welch method

**Returns:**
- `freqs` (np.ndarray): Frequency array
- `psd` (np.ndarray): Power spectral density values

##### `estimate_hurst_rs()`

Estimate Hurst exponent using R/S statistic method.

```python
@staticmethod
def estimate_hurst_rs(signal: np.ndarray, max_lag: Optional[int] = None) -> Tuple[float, np.ndarray, np.ndarray]
```

**Parameters:**
- `signal` (np.ndarray): Input signal
- `max_lag` (int, optional): Maximum lag for analysis

**Returns:**
- `hurst_estimate` (float): Estimated Hurst exponent
- `lags` (np.ndarray): Lag values used
- `rs_values` (np.ndarray): R/S statistic values

---

## Examples and Tutorials

### Tutorial 1: Basic Signal Generation

This tutorial demonstrates basic signal generation with the biomedical factory.

```python
import numpy as np
from biomedical_timeseries_factory import (
    BiomedicalTimeSeriesFactory, 
    GenerationConfig, 
    BiomedicalSignalType
)

# Step 1: Create configuration
config = GenerationConfig(
    hurst_exponent=0.75,        # Long-range dependence
    mean=0.0,                   # Zero mean
    std=1.0,                    # Unit variance  
    length=1024,                # 1024 samples
    sampling_rate=100.0,        # 100 Hz sampling
    signal_type=BiomedicalSignalType.ECG
)

# Step 2: Initialize factory
factory = BiomedicalTimeSeriesFactory(config)

# Step 3: Generate signal
signal, time_axis, metadata = factory.generate(seed=42)

# Step 4: Examine results
print(f"Generated {metadata['signal_type']} signal")
print(f"Length: {len(signal)} samples")
print(f"Duration: {time_axis[-1]:.2f} seconds")
print(f"Sampling rate: {metadata['config'].sampling_rate} Hz")

# Step 5: Display quality metrics
print("\\nQuality Metrics:")
quality = metadata['quality_metrics']
for key, value in quality.items():
    if isinstance(value, float):
        print(f"  {key}: {value:.4f}")
```

### Tutorial 2: Adding Contamination Effects

This tutorial shows how to add various contamination effects to signals.

```python
# Create contaminated signal configuration
contaminated_config = GenerationConfig(
    hurst_exponent=0.7,
    length=512,
    sampling_rate=250.0,
    signal_type=BiomedicalSignalType.ECG,
    
    # Add contamination effects
    non_stationarity=0.3,       # 30% non-stationarity
    periodicity=0.2,            # 20% periodic contamination
    seasonality=0.1,            # 10% seasonal effects
    heavy_tail_noise=0.15,      # 15% heavy-tail noise
    
    # Advanced contamination parameters
    contamination_params={
        'periodicity': {
            'frequencies': [50.0, 60.0],  # Power line interference
            'amplitude_modulation': True
        },
        'non_stationarity': {
            'trend_type': 'polynomial',
            'variance_changes': True
        },
        'heavy_tail_noise': {
            'noise_type': 'student_t',
            'outlier_rate': 0.02
        }
    }
)

# Generate contaminated signal
factory = BiomedicalTimeSeriesFactory(contaminated_config)
contaminated_signal, time_axis, metadata = factory.generate(seed=123)

print("Contamination Effects Applied:")
for contamination in metadata['applied_contaminations']:
    print(f"  - {contamination['type']}: {contamination['parameters']['intensity']:.2f}")
```

### Tutorial 3: Using Preset Configurations

This tutorial demonstrates using preset configurations for common biomedical signals.

```python
from biomedical_timeseries_factory import BiomedicalPresets

# Generate different biomedical signals using presets
signal_types = {
    'ECG': BiomedicalPresets.create_ecg_config('moderate'),
    'EEG': BiomedicalPresets.create_eeg_config('mild'),
    'HRV': BiomedicalPresets.create_hrv_config('severe')
}

generated_signals = {}

for name, config in signal_types.items():
    factory = BiomedicalTimeSeriesFactory(config)
    signal, time_axis, metadata = factory.generate(seed=42)
    
    generated_signals[name] = {
        'signal': signal,
        'time_axis': time_axis,
        'metadata': metadata
    }
    
    print(f"{name} Signal Generated:")
    print(f"  Sampling Rate: {config.sampling_rate} Hz")
    print(f"  Duration: {len(signal) / config.sampling_rate:.2f} s")
    print(f"  Contamination Level: {len(metadata['applied_contaminations'])} types")
    print()
```

### Tutorial 4: Basic Signal Analysis

This tutorial shows basic signal analysis and visualization.

```python
from biomedical_plotting_system import BiomedicalTimeSeriesAnalyzer, PlotConfig

# Initialize analyzer with scientific theme
config = PlotConfig(theme=PlotTheme.SCIENTIFIC, figure_size=(12, 8))
analyzer = BiomedicalTimeSeriesAnalyzer(config)

# Generate test signal
from biomedical_timeseries_factory import BiomedicalPresets
ecg_config = BiomedicalPresets.create_ecg_config('mild')
factory = BiomedicalTimeSeriesFactory(ecg_config)
signal, time_axis, metadata = factory.generate(seed=42)

# Create individual plots
print("Creating individual analysis plots...")

# Time series plot
fig1, ax1 = analyzer.time_series_plot(
    signal=signal,
    time_axis=time_axis,
    title="ECG Signal",
    xlabel="Time (s)",
    ylabel="Amplitude (mV)",
    show_stats=True
)

# Power spectral density
fig2, ax2 = analyzer.psd_plot(
    signal=signal,
    fs=ecg_config.sampling_rate,
    title="ECG Power Spectral Density",
    freq_range=(0.5, 100)
)

# Autocorrelation function
fig3, ax3 = analyzer.acf_plot(
    signal=signal,
    max_lags=50,
    title="ECG Autocorrelation",
    confidence_bands=True
)

# Save plots
analyzer.save_figure(fig1, "ecg_timeseries", format='png', dpi=150)
analyzer.save_figure(fig2, "ecg_psd", format='png', dpi=150)
analyzer.save_figure(fig3, "ecg_acf", format='png', dpi=150)

print("Individual plots saved successfully!")
```

### Tutorial 5: Comprehensive Analysis Dashboard

This tutorial creates a complete analysis dashboard.

```python
# Create comprehensive analysis dashboard
fig = analyzer.complete_analysis_dashboard(
    signal=signal,
    time_axis=time_axis,
    fs=ecg_config.sampling_rate,
    signal_name="ECG Lead II"
)

# Save high-quality figure for publication
analyzer.save_figure(fig, "ecg_complete_analysis", format='pdf', dpi=300)

# Get detailed analysis summary
summary = analyzer.get_analysis_summary(signal, ecg_config.sampling_rate)

print("Analysis Summary:")
print(f"  Duration: {summary['basic_statistics']['duration']:.2f} seconds")
print(f"  Mean: {summary['basic_statistics']['mean']:.4f}")
print(f"  Standard Deviation: {summary['basic_statistics']['std']:.4f}")
print(f"  Skewness: {summary['basic_statistics']['skewness']:.4f}")
print(f"  Kurtosis: {summary['basic_statistics']['kurtosis']:.4f}")
print(f"  Hurst Exponent: {summary['hurst_exponent']:.4f}")
print(f"  Peak Frequency: {summary['frequency_analysis']['peak_frequency']:.2f} Hz")
print(f"  Mean Stability: {summary['stationarity']['mean_stability']:.4f}")
print(f"  Variance Stability: {summary['stationarity']['variance_stability']:.4f}")
```

### Tutorial 6: Batch Signal Comparison

This tutorial demonstrates comparing multiple signals with different characteristics.

```python
# Generate signals with different contamination levels
contamination_levels = ['clean', 'mild', 'moderate', 'severe']
signals_dict = {}

for level in contamination_levels:
    config = BiomedicalPresets.create_ecg_config(level)
    factory = BiomedicalTimeSeriesFactory(config)
    signal, time_axis, metadata = factory.generate(seed=42)
    
    signals_dict[f'ECG ({level})'] = signal

# Create comparison visualization
fig1 = analyzer.contamination_comparison_plot(
    signals_dict=signals_dict,
    time_axis=time_axis,
    title="ECG Contamination Effects Comparison"
)

# Create statistical comparison
fig2 = analyzer.batch_compare_signals(
    signals_dict=signals_dict,
    fs=250.0,
    comparison_metrics=['mean', 'std', 'skewness', 'kurtosis', 'hurst']
)

# Save comparison figures
analyzer.save_figure(fig1, "ecg_contamination_comparison", format='png', dpi=150)
analyzer.save_figure(fig2, "ecg_statistical_comparison", format='png', dpi=150)

print("Batch comparison completed and saved!")
```

### Tutorial 7: Custom Styling and Themes

This tutorial shows how to customize plot appearance for different purposes.

```python
# Academic paper styling
analyzer.set_style_preset('paper')
fig_paper = analyzer.basic_analysis_suite(
    signal=signal,
    time_axis=time_axis,
    fs=250.0,
    title_prefix="ECG Analysis"
)
analyzer.save_figure(fig_paper, "ecg_paper_style", format='pdf', dpi=300)

# Presentation styling
analyzer.set_style_preset('presentation')
fig_presentation = analyzer.basic_analysis_suite(
    signal=signal,
    time_axis=time_axis,
    fs=250.0,
    title_prefix="ECG Analysis"
)
analyzer.save_figure(fig_presentation, "ecg_presentation_style", format='png', dpi=150)

# Custom configuration
custom_config = PlotConfig(
    theme=PlotTheme.CLINICAL,
    figure_size=(14, 10),
    font_size=13,
    title_size=16,
    line_width=2.0,
    save_format='svg'
)

analyzer_custom = BiomedicalTimeSeriesAnalyzer(custom_config)
fig_custom = analyzer_custom.time_series_plot(
    signal=signal,
    time_axis=time_axis,
    title="Custom Styled ECG",
    color='darkblue'
)
analyzer_custom.save_figure(fig_custom, "ecg_custom_style", format='svg')

print("Custom styling examples completed!")
```

### Tutorial 8: Integration Workflow

This tutorial demonstrates a complete integrated workflow.

```python
# Complete integrated workflow
def biomedical_analysis_workflow(signal_type='ECG', contamination='moderate', seed=42):
    """Complete biomedical signal analysis workflow"""
    
    print(f"🔬 Starting {signal_type} Analysis Workflow")
    print(f"Contamination level: {contamination}")
    print(f"Random seed: {seed}")
    print("-" * 50)
    
    # Step 1: Generate signal
    if signal_type == 'ECG':
        config = BiomedicalPresets.create_ecg_config(contamination)
    elif signal_type == 'EEG':
        config = BiomedicalPresets.create_eeg_config(contamination)
    elif signal_type == 'HRV':
        config = BiomedicalPresets.create_hrv_config(contamination)
    else:
        raise ValueError(f"Unsupported signal type: {signal_type}")
    
    factory = BiomedicalTimeSeriesFactory(config)
    factory_output = factory.generate(seed=seed)
    signal, time_axis, metadata = factory_output
    
    print(f"✅ Generated {signal_type} signal:")
    print(f"   Length: {len(signal)} samples")
    print(f"   Duration: {len(signal) / config.sampling_rate:.2f} seconds")
    print(f"   Sampling rate: {config.sampling_rate} Hz")
    
    # Step 2: Analyze signal
    analyzer = BiomedicalTimeSeriesAnalyzer()
    
    # Direct factory output analysis
    fig = analyzer.analyze_factory_output(
        factory_output=factory_output,
        analysis_type='complete',
        show_quality_report=True
    )
    
    # Step 3: Get comprehensive summary
    summary = analyzer.get_analysis_summary(signal, config.sampling_rate)
    
    print(f"\\n📊 Analysis Summary:")
    print(f"   Hurst exponent: {summary['hurst_exponent']:.4f}")
    print(f"   Peak frequency: {summary['frequency_analysis']['peak_frequency']:.2f} Hz")
    print(f"   Signal-to-noise ratio: {summary['basic_statistics']['mean'] / summary['basic_statistics']['std']:.3f}")
    
    # Step 4: Save results
    filename = f"{signal_type.lower()}_{contamination}_analysis"
    analyzer.save_figure(fig, filename, format='pdf', dpi=300)
    
    print(f"\\n💾 Results saved as: {filename}.pdf")
    print("🎯 Workflow completed successfully!")
    
    return {
        'signal': signal,
        'time_axis': time_axis,
        'metadata': metadata,
        'summary': summary,
        'figure': fig
    }

# Run workflows for different signal types
results = {}
for signal_type in ['ECG', 'EEG', 'HRV']:
    results[signal_type] = biomedical_analysis_workflow(
        signal_type=signal_type,
        contamination='moderate',
        seed=42
    )
    print("\\n" + "="*60 + "\\n")

print("🏁 All workflows completed successfully!")
```

---

## Best Practices

### Signal Generation Guidelines

#### Parameter Selection

1. **Hurst Exponent Selection**
   ```python
   # Choose H based on physiological characteristics
   hurst_values = {
       'ECG': 0.7,      # Moderate persistence for cardiac signals
       'EEG': 0.85,     # High persistence for neural oscillations
       'HRV': 0.8,      # Strong persistence for autonomic control
       'EMG': 0.6       # Lower persistence for muscle activity
   }
   ```

2. **Sampling Rate Guidelines**
   ```python
   # Use appropriate sampling rates for different signals
   sampling_rates = {
       'ECG': 250.0,     # Standard ECG sampling
       'EEG': 128.0,     # Common EEG sampling
       'HRV': 4.0,       # RR interval sampling
       'EMG': 1000.0,    # High-frequency muscle signals
       'PPG': 100.0      # Pulse oximetry sampling
   }
   ```

3. **Contamination Level Guidelines**
   ```python
   # Realistic contamination levels
   contamination_guidelines = {
       'clean': {
           'research': 'Ideal conditions, algorithm development',
           'levels': {'all': 0.0}
       },
       'mild': {
           'research': 'Laboratory conditions, good signal quality',
           'levels': {
               'non_stationarity': 0.1,
               'periodicity': 0.15,
               'seasonality': 0.05,
               'heavy_tail_noise': 0.1
           }
       },
       'moderate': {
           'research': 'Clinical conditions, typical signal quality',
           'levels': {
               'non_stationarity': 0.25,
               'periodicity': 0.3,
               'seasonality': 0.15,
               'heavy_tail_noise': 0.2
           }
       },
       'severe': {
           'research': 'Challenging conditions, poor signal quality',
           'levels': {
               'non_stationarity': 0.4,
               'periodicity': 0.5,
               'seasonality': 0.3,
               'heavy_tail_noise': 0.35
           }
       }
   }
   ```

#### Code Organization

1. **Configuration Management**
   ```python
   # Use configuration objects for reproducibility
   def create_experiment_config(experiment_name: str) -> GenerationConfig:
       """Create standardized configuration for experiments"""
       base_config = GenerationConfig(
           length=1024,
           sampling_rate=100.0,
           validate_parameters=True,
           compute_quality_metrics=True
       )
       
       # Experiment-specific modifications
       if experiment_name == 'baseline':
           base_config.hurst_exponent = 0.7
           # No contamination
       elif experiment_name == 'noise_robustness':
           base_config.heavy_tail_noise = 0.3
       
       return base_config
   ```

2. **Batch Processing**
   ```python
   def batch_generate_signals(configurations: List[GenerationConfig], 
                            n_realizations: int = 10) -> Dict:
       """Generate multiple signal realizations for statistical analysis"""
       results = {}
       
       for i, config in enumerate(configurations):
           factory = BiomedicalTimeSeriesFactory(config)
           signals = []
           
           for realization in range(n_realizations):
               signal, time_axis, metadata = factory.generate(seed=realization)
               signals.append({
                   'signal': signal,
                   'time_axis': time_axis,
                   'metadata': metadata
               })
           
           results[f'config_{i}'] = signals
       
       return results
   ```

### Analysis and Visualization Guidelines

#### Plot Selection

1. **Choose Appropriate Analysis Methods**
   ```python
   # Signal-specific analysis recommendations
   analysis_recommendations = {
       'ECG': ['time_series', 'psd', 'acf', 'stationarity'],
       'EEG': ['time_series', 'psd', 'spectrogram', 'hurst_analysis'],
       'HRV': ['time_series', 'psd', 'acf', 'statistical_suite'],
       'EMG': ['time_series', 'psd', 'histogram', 'spectrogram']
   }
   
   def create_signal_specific_analysis(signal_type: str, signal: np.ndarray, 
                                     time_axis: np.ndarray, fs: float):
       analyzer = BiomedicalTimeSeriesAnalyzer()
       
       if signal_type in analysis_recommendations:
           methods = analysis_recommendations[signal_type]
           
           if 'statistical_suite' in methods:
               return analyzer.statistical_analysis_suite(signal)
           else:
               return analyzer.basic_analysis_suite(signal, time_axis, fs)
   ```

2. **Frequency Range Selection**
   ```python
   # Physiologically relevant frequency ranges
   frequency_ranges = {
       'ECG': (0.5, 100),      # Standard ECG bandwidth
       'EEG': (0.5, 50),       # Brain wave frequencies
       'HRV': (0.04, 0.4),     # HRV frequency bands
       'EMG': (10, 500),       # Muscle activity range
       'PPG': (0.5, 20)        # Pulse wave range
   }
   
   def plot_signal_psd(signal: np.ndarray, fs: float, signal_type: str):
       analyzer = BiomedicalTimeSeriesAnalyzer()
       freq_range = frequency_ranges.get(signal_type, None)
       
       return analyzer.psd_plot(
           signal=signal,
           fs=fs,
           freq_range=freq_range,
           title=f"{signal_type} Power Spectral Density"
       )
   ```

#### Performance Optimization

1. **Memory Management**
   ```python
   # For large signals or batch processing
   def memory_efficient_analysis(signal: np.ndarray, fs: float):
       analyzer = BiomedicalTimeSeriesAnalyzer()
       
       # Use appropriate parameters for large signals
       if len(signal) > 10000:
           # Limit ACF computation
           max_lags = min(len(signal) // 10, 200)
           # Use smaller PSD segments
           nperseg = min(len(signal) // 8, 1024)
       else:
           max_lags = None
           nperseg = None
       
       fig, ax = analyzer.acf_plot(signal, max_lags=max_lags)
       return fig
   ```

2. **Computational Efficiency**
   ```python
   # Efficient batch analysis
   def efficient_batch_analysis(signals_dict: Dict[str, np.ndarray], fs: float):
       analyzer = BiomedicalTimeSeriesAnalyzer()
       
       # Pre-compute common analyses
       summaries = {}
       for name, signal in signals_dict.items():
           summaries[name] = analyzer.get_analysis_summary(signal, fs)
       
       # Create comparison plot
       comparison_fig = analyzer.batch_compare_signals(signals_dict, fs)
       
       return summaries, comparison_fig
   ```

#### Publication Guidelines

1. **Academic Publications**
   ```python
   def create_publication_figures(signal: np.ndarray, time_axis: np.ndarray, 
                                fs: float, signal_name: str):
       """Create publication-ready figures"""
       
       # Configure for academic papers
       analyzer = BiomedicalTimeSeriesAnalyzer()
       analyzer.set_style_preset('paper')
       
       # Create main analysis figure
       main_fig = analyzer.complete_analysis_dashboard(
           signal=signal,
           time_axis=time_axis,
           fs=fs,
           signal_name=signal_name
       )
       
       # Save high-quality PDF
       analyzer.save_figure(
           fig=main_fig,
           filename=f"{signal_name.lower().replace(' ', '_')}_analysis",
           format='pdf',
           dpi=300,
           bbox_inches='tight'
       )
       
       return main_fig
   ```

2. **Presentation Materials**
   ```python
   def create_presentation_figures(signals_dict: Dict[str, np.ndarray]):
       """Create presentation-ready figures"""
       
       analyzer = BiomedicalTimeSeriesAnalyzer()
       analyzer.set_style_preset('presentation')
       
       # Create comparison figure
       comparison_fig = analyzer.contamination_comparison_plot(
           signals_dict=signals_dict,
           title="Signal Contamination Effects"
       )
       
       # Save high-contrast PNG
       analyzer.save_figure(
           fig=comparison_fig,
           filename="signal_comparison_presentation",
           format='png',
           dpi=150
       )
       
       return comparison_fig
   ```

### Data Management

#### Reproducibility

1. **Seed Management**
   ```python
   class ExperimentManager:
       """Manage reproducible experiments"""
       
       def __init__(self, base_seed: int = 42):
           self.base_seed = base_seed
           self.experiment_counter = 0
       
       def get_experiment_seed(self) -> int:
           """Get unique seed for each experiment"""
           seed = self.base_seed + self.experiment_counter
           self.experiment_counter += 1
           return seed
       
       def run_experiment(self, config: GenerationConfig, name: str):
           """Run reproducible experiment"""
           seed = self.get_experiment_seed()
           factory = BiomedicalTimeSeriesFactory(config)
           
           return {
               'name': name,
               'seed': seed,
               'config': config,
               'output': factory.generate(seed=seed)
           }
   ```

2. **Configuration Serialization**
   ```python
   import json
   from dataclasses import asdict
   
   def save_experiment_config(config: GenerationConfig, filename: str):
       """Save configuration for reproducibility"""
       config_dict = asdict(config)
       
       # Handle enum serialization
       if config.signal_type:
           config_dict['signal_type'] = config.signal_type.value
       
       with open(filename, 'w') as f:
           json.dump(config_dict, f, indent=2)
   
   def load_experiment_config(filename: str) -> GenerationConfig:
       """Load configuration from file"""
       with open(filename, 'r') as f:
           config_dict = json.load(f)
       
       # Handle enum deserialization
       if 'signal_type' in config_dict and config_dict['signal_type']:
           config_dict['signal_type'] = BiomedicalSignalType(config_dict['signal_type'])
       
       return GenerationConfig(**config_dict)
   ```

#### Quality Control

1. **Signal Validation**
   ```python
   def validate_generated_signal(signal: np.ndarray, time_axis: np.ndarray, 
                               metadata: Dict, expected_properties: Dict) -> bool:
       """Validate generated signal meets expected properties"""
       
       # Check basic properties
       if len(signal) != expected_properties.get('length'):
           return False
       
       # Check Hurst exponent estimation
       analyzer = BiomedicalTimeSeriesAnalyzer()
       summary = analyzer.get_analysis_summary(signal, 1.0)
       
       expected_hurst = expected_properties.get('hurst_exponent')
       estimated_hurst = summary['hurst_exponent']
       
       if abs(estimated_hurst - expected_hurst) > 0.1:  # 10% tolerance
           warnings.warn(f"Hurst exponent mismatch: expected {expected_hurst}, got {estimated_hurst}")
       
       return True
   ```

2. **Quality Metrics Monitoring**
   ```python
   def monitor_generation_quality(factory: BiomedicalTimeSeriesFactory, 
                                n_samples: int = 10) -> Dict:
       """Monitor quality across multiple generations"""
       
       quality_metrics = []
       
       for i in range(n_samples):
           signal, time_axis, metadata = factory.generate(seed=i)
           
           if 'quality_metrics' in metadata:
               quality_metrics.append(metadata['quality_metrics'])
       
       # Compute statistics across generations
       quality_stats = {}
       if quality_metrics:
           for key in quality_metrics[0].keys():
               values = [qm[key] for qm in quality_metrics if isinstance(qm[key], (int, float))]
               if values:
                   quality_stats[key] = {
                       'mean': np.mean(values),
                       'std': np.std(values),
                       'min': np.min(values),
                       'max': np.max(values)
                   }
       
       return quality_stats
   ```

---

## Troubleshooting

### Common Issues and Solutions

#### Installation Issues

**Issue 1: Import Errors**
```python
ImportError: No module named 'biomedical_timeseries_factory'
```

**Solution:**
```bash
# Ensure files are in the correct location
ls -la biomedical_timeseries_factory.py
ls -la biomedical_plotting_system.py

# Check Python path
python -c "import sys; print('\\n'.join(sys.path))"

# Verify dependencies
pip list | grep -E "(numpy|scipy|matplotlib)"
```

**Issue 2: Dependency Conflicts**
```
AttributeError: module 'scipy.signal' has no attribute 'welch'
```

**Solution:**
```bash
# Update scipy
pip install --upgrade scipy>=1.7.0

# Check versions
python -c "import scipy; print(scipy.__version__)"
```

#### Generation Issues

**Issue 3: Hurst Parameter Validation**
```
Warning: Hurst parameter 1.2 outside typical range [0.5, 0.9] for electrocardiogram
```

**Solution:**
```python
# Use valid Hurst parameter ranges
config = GenerationConfig(
    hurst_exponent=0.75,  # Valid range: 0.01-0.99
    signal_type=BiomedicalSignalType.ECG
)

# Disable validation if needed for research
config.validate_parameters = False
```

**Issue 4: Memory Issues with Large Signals**
```
MemoryError: Unable to allocate array
```

**Solution:**
```python
# Reduce signal length or use chunked processing
config = GenerationConfig(
    length=1024,  # Instead of 100000
    sampling_rate=100.0
)

# For very long signals, generate in chunks
def generate_long_signal(total_length: int, chunk_size: int = 1024):
    chunks = []
    n_chunks = total_length // chunk_size
    
    for i in range(n_chunks):
        config = GenerationConfig(length=chunk_size)
        factory = BiomedicalTimeSeriesFactory(config)
        signal, _, _ = factory.generate(seed=i)
        chunks.append(signal)
    
    return np.concatenate(chunks)
```

#### Plotting Issues

**Issue 5: Figure Display Problems**
```python
# Figures not displaying
```

**Solution:**
```python
import matplotlib
matplotlib.use('TkAgg')  # or 'Qt5Agg'

# Or use inline for Jupyter
%matplotlib inline

# Explicitly show figures
import matplotlib.pyplot as plt
plt.show()
```

**Issue 6: Font and Styling Issues**
```
UserWarning: Glyph missing from current font
```

**Solution:**
```python
# Reset matplotlib settings
import matplotlib.pyplot as plt
plt.style.use('default')

# Use basic fonts
config = PlotConfig(
    theme=PlotTheme.SCIENTIFIC,
    font_size=12
)

# Clear font cache if needed
import matplotlib.font_manager
matplotlib.font_manager._rebuild()
```

**Issue 7: Slow Performance**
```python
# Analysis taking too long
```

**Solution:**
```python
# Optimize analysis parameters
analyzer = BiomedicalTimeSeriesAnalyzer()

# For large signals, limit analysis scope
if len(signal) > 10000:
    # Reduce ACF lags
    fig, ax = analyzer.acf_plot(signal, max_lags=100)
    
    # Use smaller PSD segments
    fig, ax = analyzer.psd_plot(signal, fs, nperseg=512)
    
    # Skip time-intensive analyses
    summary = analyzer.get_analysis_summary(signal, fs)
    # summary contains pre-computed metrics
```

### Performance Optimization

#### Memory Optimization

```python
def memory_efficient_batch_analysis(signals_list: List[np.ndarray], fs: float):
    """Analyze large number of signals efficiently"""
    
    analyzer = BiomedicalTimeSeriesAnalyzer()
    results = []
    
    for i, signal in enumerate(signals_list):
        # Process one signal at a time
        summary = analyzer.get_analysis_summary(signal, fs)
        results.append(summary)
        
        # Clear intermediate variables
        del signal
        if i % 100 == 0:  # Periodic garbage collection
            import gc
            gc.collect()
    
    return results
```

#### Computational Optimization

```python
def optimized_analysis_suite(signal: np.ndarray, fs: float):
    """Create optimized analysis for better performance"""
    
    analyzer = BiomedicalTimeSeriesAnalyzer()
    
    # Pre-compute common analyses
    summary = analyzer.get_analysis_summary(signal, fs)
    
    # Use summary data instead of recomputing
    hurst_value = summary['hurst_exponent']
    peak_freq = summary['frequency_analysis']['peak_frequency']
    
    # Create simplified plots
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    # Time series (fast)
    axes[0, 0].plot(signal)
    axes[0, 0].set_title(f"Signal (H={hurst_value:.3f})")
    
    # Use pre-computed PSD
    freqs, psd = SignalAnalyzer.compute_psd(signal, fs, nperseg=256)
    axes[0, 1].loglog(freqs, psd)
    axes[0, 1].set_title(f"PSD (Peak: {peak_freq:.1f} Hz)")
    
    return fig
```

### Debugging Guidelines

#### Enable Debug Mode

```python
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

def debug_generation(config: GenerationConfig):
    """Generate signal with detailed debugging"""
    
    print("Configuration:")
    print(f"  Hurst: {config.hurst_exponent}")
    print(f"  Length: {config.length}")
    print(f"  Contamination: NS={config.non_stationarity}, P={config.periodicity}")
    
    factory = BiomedicalTimeSeriesFactory(config)
    
    try:
        signal, time_axis, metadata = factory.generate(seed=42)
        
        print("\\nGeneration successful:")
        print(f"  Signal shape: {signal.shape}")
        print(f"  Time axis shape: {time_axis.shape}")
        print(f"  Metadata keys: {list(metadata.keys())}")
        
        return signal, time_axis, metadata
        
    except Exception as e:
        print(f"\\nGeneration failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None
```

#### Validate Intermediate Results

```python
def validate_analysis_pipeline(signal: np.ndarray, fs: float):
    """Validate each step of analysis pipeline"""
    
    print("Signal validation:")
    print(f"  Shape: {signal.shape}")
    print(f"  Range: [{np.min(signal):.3f}, {np.max(signal):.3f}]")
    print(f"  NaN values: {np.sum(np.isnan(signal))}")
    print(f"  Inf values: {np.sum(np.isinf(signal))}")
    
    if np.any(np.isnan(signal)) or np.any(np.isinf(signal)):
        print("⚠️  Warning: Signal contains invalid values")
        return False
    
    # Test basic analysis methods
    try:
        freqs, psd = SignalAnalyzer.compute_psd(signal, fs)
        print(f"✅ PSD computation successful: {len(freqs)} frequency points")
    except Exception as e:
        print(f"❌ PSD computation failed: {e}")
        return False
    
    try:
        lags, acf = SignalAnalyzer.compute_acf(signal)
        print(f"✅ ACF computation successful: {len(lags)} lags")
    except Exception as e:
        print(f"❌ ACF computation failed: {e}")
        return False
    
    try:
        hurst_est, _, _ = SignalAnalyzer.estimate_hurst_rs(signal)
        print(f"✅ Hurst estimation successful: H = {hurst_est:.3f}")
    except Exception as e:
        print(f"❌ Hurst estimation failed: {e}")
        return False
    
    print("✅ All analysis methods validated successfully")
    return True
```

### Getting Help

#### Community Resources

1. **Documentation**: Refer to this API documentation for detailed method descriptions
2. **Examples**: Use the provided tutorials as starting points for your analysis
3. **Issues**: Check common issues in the troubleshooting section

#### Reporting Issues

When reporting issues, please include:

```python
def generate_debug_report():
    """Generate debug information for issue reporting"""
    
    import sys
    import numpy as np
    import scipy
    import matplotlib
    
    report = f"""
Debug Report
============
Python version: {sys.version}
NumPy version: {np.__version__}
SciPy version: {scipy.__version__}
Matplotlib version: {matplotlib.__version__}

System information:
Platform: {sys.platform}
Executable: {sys.executable}

Traceback (if any):
[Include full traceback here]

Minimal reproduction code:
[Include minimal code that reproduces the issue]

Expected behavior:
[Describe what should happen]

Actual behavior:
[Describe what actually happens]
    """
    
    return report

# Run this and include output in issue reports
print(generate_debug_report())
```

---

## Contributing

We welcome contributions to improve the Biomedical Time Series Framework! Here's how you can contribute:

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/biomedical-timeseries-framework.git
   cd biomedical-timeseries-framework
   ```

2. **Set Up Development Environment**
   ```bash
   python -m venv dev_env
   source dev_env/bin/activate  # On Windows: dev_env\\Scripts\\activate
   
   pip install -r requirements-dev.txt
   pip install -e .
   ```

3. **Run Tests**
   ```bash
   python -m pytest tests/
   ```

### Contributing Guidelines

#### Code Style

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Include docstrings for all public methods
- Write descriptive variable and function names

#### Testing

```python
def test_signal_generation():
    """Test basic signal generation functionality"""
    config = GenerationConfig(
        hurst_exponent=0.7,
        length=256,
        sampling_rate=100.0
    )
    
    factory = BiomedicalTimeSeriesFactory(config)
    signal, time_axis, metadata = factory.generate(seed=42)
    
    assert len(signal) == 256
    assert len(time_axis) == 256
    assert 'quality_metrics' in metadata
    assert np.isfinite(signal).all()
```

#### Documentation

- Update API documentation for new features
- Include examples in docstrings
- Add tutorials for significant new functionality

### Areas for Contribution

1. **New Contamination Models**
   - Implement additional contamination types
   - Add domain-specific contamination patterns

2. **Analysis Methods**
   - Add new signal analysis techniques
   - Implement advanced statistical tests

3. **Visualization Enhancements**
   - Create new plot types
   - Add interactive plotting capabilities

4. **Performance Improvements**
   - Optimize computational bottlenecks
   - Add parallel processing support

5. **Integration Features**
   - Add support for real-time processing
   - Create interfaces with other frameworks

### Submission Process

1. Create a feature branch: `git checkout -b feature-name`
2. Make your changes with appropriate tests
3. Update documentation as needed
4. Submit a pull request with clear description

### Code Review Process

All contributions go through code review to ensure:
- Code quality and style compliance
- Comprehensive testing
- Documentation completeness
- Compatibility with existing functionality

---

**End of API Documentation**

*This documentation is actively maintained and updated. For the latest version, please check the project repository.*