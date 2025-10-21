#!/usr/bin/env python3
"""
Biomedical Hurst Exponent Estimation Factory

A comprehensive Python library for estimating Hurst exponents in biomedical 
time series data with statistical confidence, uncertainty quantification, 
and performance monitoring.

Developed as part of PhD research in Biomedical Engineering at the University of Reading, UK.
Author: Davian R. Chin (PhD Candidate in Biomedical Engineering, University of Reading, UK)
Email: d.r.chin@pgr.reading.ac.uk
ORCiD: https://orcid.org/0009-0003-9434-3919
Research Focus: Physics-Informed Fractional Operator Learning for Real-Time Neurological Biomarker Detection: 
A Framework for Memory-Driven EEG Analysis

This library represents a significant contribution to the field of physics-informed machine learning
for neurological signal processing, providing researchers and practitioners with a comprehensive toolkit
for fractional operator learning and real-time biomarker detection in EEG and other neurological time series data.

Date: October 2025
License: MIT

Example Usage:
    from neurological_lrd_analysis import BiomedicalHurstEstimatorFactory, EstimatorType
    
    factory = BiomedicalHurstEstimatorFactory()
    result = factory.estimate(data, EstimatorType.DFA)
    print(f"Hurst exponent: {result.hurst_estimate:.3f}")
"""

import numpy as np
import pandas as pd
import time
import warnings
from dataclasses import dataclass
from typing import Union, List, Dict, Optional, Tuple, Any
from enum import Enum
import logging

# Lazy imports for heavy modules
def _lazy_import_scipy():
    """Lazy import of scipy modules"""
    try:
        from scipy import stats, signal
        from scipy.fft import fft, fftfreq
        return stats, signal, fft, fftfreq
    except ImportError:
        raise ImportError("scipy is required but not installed")

def _lazy_import_optimize():
    """Lazy import of scipy.optimize"""
    try:
        from scipy import optimize
        return optimize
    except ImportError:
        raise ImportError("scipy.optimize is required but not installed")

def _lazy_import_numpyro():
    """Lazy import of NumPyro for Bayesian inference"""
    try:
        import numpyro
        import numpyro.distributions as dist
        from numpyro.infer import MCMC, NUTS, Predictive
        import jax.numpy as jnp
        import jax
        return numpyro, dist, MCMC, NUTS, Predictive, jnp, jax
    except ImportError:
        raise ImportError("numpyro and jax are required for Bayesian inference but not installed")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class EstimatorType(Enum):
    """Types of Hurst estimators available"""
    # Temporal domain methods
    DFA = "dfa"
    RS_ANALYSIS = "rs" 
    HIGUCHI = "higuchi"
    DETRENDED_MA = "dma"
    GENERALIZED_HURST = "ghe"
    
    # Spectral domain methods
    PERIODOGRAM = "periodogram"
    WHITTLE_MLE = "whittle"
    GPH = "gph"
    
    # Wavelet domain methods
    DWT = "dwt"
    CWT = "cwt"
    NDWT = "ndwt"
    WAVELET_LEADERS = "leaders"
    ABRY_VEITCH = "abry_veitch"
    
    # Multifractal methods
    MFDFA = "mfdfa"
    MF_DMA = "mf_dma"
    
    # Machine learning methods (future implementation)
    RANDOM_FOREST = "rf"
    SVR = "svr"
    
    # Group estimators
    TEMPORAL = "temporal"
    SPECTRAL = "spectral" 
    WAVELET = "wavelet"
    ALL = "all"

class ConfidenceMethod(Enum):
    """Methods for confidence interval estimation"""
    BOOTSTRAP = "bootstrap"
    THEORETICAL = "theoretical"
    CROSS_VALIDATION = "cross_validation"
    BAYESIAN = "bayesian"  # NumPyro-based Bayesian inference
    NONE = "none"

# ============================================================================
# RESULT CONTAINERS
# ============================================================================

@dataclass
class HurstResult:
    """Comprehensive result container for Hurst exponent estimation"""
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
    
    # Additional metrics (Bayesian, method-specific, etc.)
    additional_metrics: Dict[str, Any]
    
    def __str__(self):
        return f"""
Hurst Exponent Analysis Results
===============================
Method: {self.estimator_name}
Estimate: {self.hurst_estimate:.4f}
Confidence Interval ({self.confidence_level*100:.0f}%): [{self.confidence_interval[0]:.4f}, {self.confidence_interval[1]:.4f}]
Standard Error: {self.standard_error:.4f}
Data Quality Score: {self.data_quality_score:.3f}
Computation Time: {self.computation_time:.3f}s
Convergence: {'Success' if self.convergence_flag else 'Failed'}
"""

    def to_dict(self):
        """Convert result to dictionary for serialization"""
        return {
            'hurst_estimate': self.hurst_estimate,
            'estimator_name': self.estimator_name,
            'confidence_interval': self.confidence_interval,
            'confidence_level': self.confidence_level,
            'standard_error': self.standard_error,
            'computation_time': self.computation_time,
            'convergence_flag': self.convergence_flag,
            'data_quality_score': self.data_quality_score,
            'regression_r_squared': self.regression_r_squared,
            'scaling_range': self.scaling_range,
            'signal_to_noise_ratio': self.signal_to_noise_ratio
        }

@dataclass
class GroupHurstResult:
    """Results for group estimation (multiple methods)"""
    individual_results: List[HurstResult]
    ensemble_estimate: float
    ensemble_confidence_interval: Tuple[float, float]
    method_agreement: float
    best_method: str
    consensus_estimate: float
    weighted_estimate: float
    total_computation_time: float
    
    def __str__(self):
        methods = [r.estimator_name for r in self.individual_results]
        estimates = [r.hurst_estimate for r in self.individual_results]
        
        return f"""
Group Hurst Exponent Analysis
=============================
Methods Used: {', '.join(methods)}
Individual Estimates: {[f'{e:.3f}' for e in estimates]}
Ensemble Estimate: {self.ensemble_estimate:.4f}
Consensus Estimate: {self.consensus_estimate:.4f}
Best Method: {self.best_method}
Method Agreement: {self.method_agreement:.3f}
Total Time: {self.total_computation_time:.3f}s
"""

    def to_dict(self):
        """Convert group result to dictionary"""
        return {
            'individual_results': [r.to_dict() for r in self.individual_results],
            'ensemble_estimate': self.ensemble_estimate,
            'ensemble_confidence_interval': self.ensemble_confidence_interval,
            'method_agreement': self.method_agreement,
            'best_method': self.best_method,
            'consensus_estimate': self.consensus_estimate,
            'weighted_estimate': self.weighted_estimate,
            'total_computation_time': self.total_computation_time
        }

# ============================================================================
# BIOMEDICAL DATA PROCESSING
# ============================================================================

class BiomedicalDataProcessor:
    """Specialized preprocessing for biomedical time series data"""
    
    @staticmethod
    def assess_data_quality(data: np.ndarray) -> Dict[str, Any]:
        """Comprehensive data quality assessment for biomedical signals"""
        data = np.asarray(data)
        n = len(data)
        quality_metrics = {}
        
        # Missing data assessment
        missing_mask = np.isnan(data) | np.isinf(data)
        missing_fraction = np.sum(missing_mask) / n
        quality_metrics['missing_data_fraction'] = missing_fraction
        quality_metrics['has_missing_data'] = missing_fraction > 0
        
        # Clean data for analysis
        clean_data = data[~missing_mask] if np.any(missing_mask) else data
        
        if len(clean_data) == 0:
            return {'error': 'No valid data points', 'data_quality_score': 0.0}
        
        # Outlier detection using modified Z-score
        median_val = np.median(clean_data)
        mad = np.median(np.abs(clean_data - median_val))
        if mad > 0:
            modified_z_scores = 0.6745 * (clean_data - median_val) / mad
            outlier_mask = np.abs(modified_z_scores) > 3.5
            outlier_fraction = np.sum(outlier_mask) / len(clean_data)
        else:
            outlier_fraction = 0.0
        quality_metrics['outlier_fraction'] = outlier_fraction
        
        # Signal-to-noise ratio estimation
        if len(clean_data) > 10:
            signal_power = np.var(clean_data)
            noise_power = np.var(np.diff(clean_data)) if len(clean_data) > 1 else signal_power
            snr = signal_power / (noise_power + 1e-10)
            quality_metrics['signal_to_noise_ratio'] = 10 * np.log10(snr) if snr > 0 else None
        else:
            quality_metrics['signal_to_noise_ratio'] = None
        
        # Simple stationarity test
        if len(clean_data) > 20:
            first_half = clean_data[:len(clean_data)//2]
            second_half = clean_data[len(clean_data)//2:]
            var1, var2 = np.var(first_half), np.var(second_half)
            if min(var1, var2) > 0:
                f_stat = max(var1, var2) / min(var1, var2)
                stationarity_p = 1 / (1 + f_stat) if f_stat > 1 else 0.8
            else:
                stationarity_p = 0.5
            quality_metrics['stationarity_p_value'] = stationarity_p
        else:
            quality_metrics['stationarity_p_value'] = None
        
        # Artifact detection
        artifacts = {}
        if len(clean_data) > 10:
            diff_data = np.diff(clean_data)
            flat_threshold = np.std(clean_data) * 0.01
            flat_segments = np.sum(np.abs(diff_data) < flat_threshold) / len(diff_data)
            artifacts['flat_segments_fraction'] = flat_segments
            
            jump_threshold = 5 * np.std(diff_data)
            jumps = np.sum(np.abs(diff_data) > jump_threshold)
            artifacts['sudden_jumps'] = jumps
            artifacts['jump_fraction'] = jumps / len(diff_data)
        
        quality_metrics['artifact_detection'] = artifacts
        
        # Overall quality score
        quality_score = 1.0
        quality_score -= missing_fraction * 0.5
        quality_score -= min(outlier_fraction * 2, 0.3)
        quality_score -= artifacts.get('flat_segments_fraction', 0) * 0.2
        quality_score -= min(artifacts.get('jump_fraction', 0) * 10, 0.3)
        
        quality_metrics['data_quality_score'] = max(0.0, min(1.0, quality_score))
        
        return quality_metrics
    
    @staticmethod
    def preprocess_biomedical_data(data: np.ndarray, 
                                 handle_missing: str = 'interpolate',
                                 remove_outliers: bool = True,
                                 detrend: bool = True,
                                 filter_artifacts: bool = True,
                                 trim_convergence: bool = False,
                                 stability_threshold: float = 0.05,
                                 min_stable_fraction: float = 0.1) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Preprocess biomedical time series data"""
        
        data = np.asarray(data, dtype=float)
        preprocessing_log = {'original_length': len(data)}
        
        # Handle missing data
        missing_mask = np.isnan(data) | np.isinf(data)
        if np.any(missing_mask):
            if handle_missing == 'interpolate':
                valid_indices = np.where(~missing_mask)[0]
                if len(valid_indices) > 1:
                    data = np.interp(np.arange(len(data)), valid_indices, data[valid_indices])
                    preprocessing_log['interpolated_points'] = np.sum(missing_mask)
                else:
                    raise ValueError("Insufficient valid data for interpolation")
            elif handle_missing == 'remove':
                data = data[~missing_mask]
                preprocessing_log['removed_points'] = np.sum(missing_mask)
            elif handle_missing == 'forward_fill':
                last_valid = data[~missing_mask][0] if np.any(~missing_mask) else 0
                for i in range(len(data)):
                    if missing_mask[i]:
                        data[i] = last_valid
                    else:
                        last_valid = data[i]
                preprocessing_log['forward_filled_points'] = np.sum(missing_mask)
        
        # Remove outliers
        if remove_outliers and len(data) > 10:
            median_val = np.median(data)
            mad = np.median(np.abs(data - median_val))
            if mad > 0:
                modified_z_scores = 0.6745 * (data - median_val) / mad
                outlier_mask = np.abs(modified_z_scores) > 3.5
                if np.any(outlier_mask):
                    data[outlier_mask] = median_val
                    preprocessing_log['outliers_replaced'] = np.sum(outlier_mask)
        
        # Detrend data
        if detrend and len(data) > 2:
            t = np.arange(len(data))
            coeffs = np.polyfit(t, data, 1)
            trend = np.polyval(coeffs, t)
            data = data - trend
            preprocessing_log['detrended'] = True
            preprocessing_log['trend_slope'] = coeffs[0]
        
        # Basic artifact filtering
        if filter_artifacts and len(data) > 20:
            diff_data = np.diff(data)
            jump_threshold = 5 * np.std(diff_data)
            jump_indices = np.where(np.abs(diff_data) > jump_threshold)[0]
            
            for idx in jump_indices:
                if 0 < idx < len(data) - 1:
                    data[idx + 1] = (data[idx] + data[idx + 2]) / 2
            
            preprocessing_log['jumps_smoothed'] = len(jump_indices)
        
        # Optional convergence trimming: find delayed start where statistics stabilize
        if trim_convergence and len(data) > 100:
            try:
                window_length = max(50, len(data) // 20)
                # Rolling std as stability proxy
                diffs = np.abs(np.diff(data))
                if len(diffs) < window_length + 2:
                    window_length = max(20, len(diffs) // 2)
                if window_length > 5 and len(diffs) > window_length + 2:
                    rolling_std = np.array([
                        np.std(diffs[i:i+window_length])
                        for i in range(0, len(diffs) - window_length)
                    ])
                    # Normalize to first window to get relative change
                    eps = 1e-12
                    normalized = rolling_std / (rolling_std[0] + eps)
                    # Compute relative change over a step of window_length
                    rel_change = np.abs(np.diff(normalized)) / (normalized[:-1] + eps)
                    # Require stability over a contiguous stable span
                    stable_span = max(10, int(min_stable_fraction * len(rel_change)))
                    start_idx = 0
                    found = False
                    for i in range(0, len(rel_change) - stable_span):
                        if np.all(rel_change[i:i+stable_span] < stability_threshold):
                            start_idx = i
                            found = True
                            break
                    if found:
                        # Map back to data index; add margin of one window
                        trim_index = min(len(data) - 1, start_idx + window_length)
                        if trim_index > 0 and trim_index < len(data) - 10:
                            data = data[trim_index:]
                            preprocessing_log['trimmed_for_convergence'] = True
                            preprocessing_log['trim_start_index'] = int(trim_index)
                            preprocessing_log['stability_threshold'] = float(stability_threshold)
                            preprocessing_log['stable_span'] = int(stable_span)
                        else:
                            preprocessing_log['trimmed_for_convergence'] = False
                    else:
                        preprocessing_log['trimmed_for_convergence'] = False
                else:
                    preprocessing_log['trimmed_for_convergence'] = False
            except Exception:
                # Fail-safe: do not trim on any error
                preprocessing_log['trimmed_for_convergence'] = False
        
        preprocessing_log['final_length'] = len(data)
        return data, preprocessing_log

# ============================================================================
# BASE ESTIMATOR CLASS
# ============================================================================

class BaseHurstEstimator:
    """Base class for all Hurst estimators"""
    
    def __init__(self, name: str):
        self.name = name
        self.last_computation_time = 0.0
        self.last_memory_usage = None
        
    def estimate(self, data: np.ndarray, **kwargs) -> Tuple[float, Dict[str, Any]]:
        """Estimate Hurst exponent with additional metrics"""
        raise NotImplementedError("Subclasses must implement estimate method")
    
    def validate_data(self, data: np.ndarray, min_length: int = 50) -> None:
        """Validate input data"""
        if len(data) < min_length:
            raise ValueError(f"Data too short: {len(data)} < {min_length}")
        
        valid_data = data[~np.isnan(data)]
        if len(valid_data) == 0:
            raise ValueError("All data points are NaN")
        
        if np.var(valid_data) == 0:
            raise ValueError("Data has zero variance")

# ============================================================================
# SPECIFIC ESTIMATORS
# ============================================================================

class DFAEstimator(BaseHurstEstimator):
    """Detrended Fluctuation Analysis optimized for biomedical signals"""
    
    def __init__(self):
        super().__init__("DFA")
    
    def estimate(self, data: np.ndarray, 
                 min_window: Optional[int] = None,
                 max_window: Optional[int] = None,
                 polynomial_order: int = 1,
                 overlap: float = 0.5,
                 **kwargs) -> Tuple[float, Dict[str, Any]]:
        
        start_time = time.time()
        self.validate_data(data)
        data = np.asarray(data)
        n = len(data)
        
        if min_window is None:
            min_window = max(10, n // 100)
        if max_window is None:
            max_window = min(n // 4, 500)
        
        # Remove mean and integrate (profile)
        mean_val = np.nanmean(data)
        profile = np.nancumsum(data - mean_val)
        
        # Handle NaN values
        if np.any(np.isnan(profile)):
            valid_mask = ~np.isnan(profile)
            profile = np.interp(np.arange(len(profile)), 
                              np.where(valid_mask)[0], 
                              profile[valid_mask])
        
        # Window sizes
        window_sizes = np.unique(np.logspace(np.log10(min_window), 
                                           np.log10(max_window), 20).astype(int))
        
        fluctuations = []
        valid_windows = []
        
        for window_size in window_sizes:
            if window_size >= n:
                continue
            
            step_size = max(1, int(window_size * (1 - overlap)))
            segment_fluctuations = []
            
            for start in range(0, n - window_size + 1, step_size):
                segment = profile[start:start + window_size]
                t = np.arange(len(segment))
                
                try:
                    coeffs = np.polyfit(t, segment, polynomial_order)
                    trend = np.polyval(coeffs, t)
                    detrended = segment - trend
                    fluctuation = np.sqrt(np.mean(detrended**2))
                    if fluctuation > 0:
                        segment_fluctuations.append(fluctuation)
                except np.linalg.LinAlgError:
                    continue
            
            if segment_fluctuations:
                avg_fluctuation = np.exp(np.mean(np.log(segment_fluctuations)))
                fluctuations.append(avg_fluctuation)
                valid_windows.append(window_size)
        
        if len(valid_windows) < 3:
            raise ValueError("Insufficient valid windows for regression")
        
        # Linear regression
        log_windows = np.log(valid_windows)
        log_fluctuations = np.log(fluctuations)
        
        stats, _, _, _ = _lazy_import_scipy()
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_windows, log_fluctuations)
        
        hurst_estimate = slope
        
        additional_metrics = {
            'regression_r_squared': r_value**2,
            'regression_p_value': p_value,
            'regression_std_error': std_err,
            'scaling_range': (int(valid_windows[0]), int(valid_windows[-1])),
            'num_windows_used': len(valid_windows),
            'polynomial_order': polynomial_order,
            'convergence_flag': r_value**2 > 0.8
        }
        
        self.last_computation_time = time.time() - start_time
        return hurst_estimate, additional_metrics

class HiguchiEstimator(BaseHurstEstimator):
    """Higuchi Fractal Dimension method"""
    
    def __init__(self):
        super().__init__("Higuchi")
    
    def estimate(self, data: np.ndarray, kmax: Optional[int] = None, **kwargs) -> Tuple[float, Dict[str, Any]]:
        start_time = time.time()
        self.validate_data(data, min_length=20)
        data = np.asarray(data)
        n = len(data)
        
        if kmax is None:
            kmax = min(20, n // 10)
        
        k_values = np.arange(1, kmax + 1)
        curve_lengths = []
        
        for k in k_values:
            lengths_for_k = []
            
            for m in range(k):
                indices = np.arange(m, n, k)
                if len(indices) < 2:
                    continue
                
                subsequence = data[indices]
                
                if np.any(np.isnan(subsequence)):
                    valid_mask = ~np.isnan(subsequence)
                    if np.sum(valid_mask) < 2:
                        continue
                    subsequence = subsequence[valid_mask]
                    indices = indices[valid_mask]
                
                length = 0
                for i in range(1, len(subsequence)):
                    time_diff = indices[i] - indices[i-1]
                    length += abs(subsequence[i] - subsequence[i-1]) * time_diff / k
                
                if len(subsequence) > 1:
                    N_m = (n - 1) / (len(subsequence) - 1) / k
                    normalized_length = length * N_m
                    lengths_for_k.append(normalized_length)
            
            if lengths_for_k:
                curve_lengths.append(np.median(lengths_for_k))
            else:
                curve_lengths.append(np.nan)
        
        valid_indices = ~np.isnan(curve_lengths)
        if np.sum(valid_indices) < 3:
            raise ValueError("Insufficient valid curve lengths")
        
        valid_k = k_values[valid_indices]
        valid_lengths = np.array(curve_lengths)[valid_indices]
        
        log_k = np.log(valid_k)
        log_lengths = np.log(valid_lengths)
        
        stats, _, _, _ = _lazy_import_scipy()
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_k, log_lengths)
        
        fractal_dimension = -slope
        hurst_estimate = 2 - fractal_dimension
        
        additional_metrics = {
            'fractal_dimension': fractal_dimension,
            'regression_r_squared': r_value**2,
            'regression_p_value': p_value,
            'regression_std_error': std_err,
            'scaling_range': (int(valid_k[0]), int(valid_k[-1])),
            'kmax_used': int(valid_k[-1]),
            'convergence_flag': r_value**2 > 0.7
        }
        
        self.last_computation_time = time.time() - start_time
        return hurst_estimate, additional_metrics

class PeriodogramEstimator(BaseHurstEstimator):
    """Periodogram-based Hurst estimation"""
    
    def __init__(self):
        super().__init__("Periodogram")
    
    def estimate(self, data: np.ndarray, 
                 low_freq_fraction: float = 0.1,
                 high_freq_cutoff: float = 0.4,
                 **kwargs) -> Tuple[float, Dict[str, Any]]:
        
        start_time = time.time()
        self.validate_data(data, min_length=100)
        data = np.asarray(data)
        
        if np.any(np.isnan(data)):
            valid_mask = ~np.isnan(data)
            if np.sum(valid_mask) < len(data) * 0.8:
                raise ValueError("Too many missing values for spectral analysis")
            data = np.interp(np.arange(len(data)), 
                           np.where(valid_mask)[0], 
                           data[valid_mask])
        
        data = data - np.mean(data)
        _, signal, _, _ = _lazy_import_scipy()
        window = signal.windows.hann(len(data))
        windowed_data = data * window
        
        freqs, psd = signal.periodogram(windowed_data, fs=1.0, scaling='density')
        
        start_idx = max(1, int(len(freqs) * 0.01))
        end_idx = min(len(freqs), int(len(freqs) * high_freq_cutoff))
        
        num_low_freqs = max(5, int((end_idx - start_idx) * low_freq_fraction))
        selected_freqs = freqs[start_idx:start_idx + num_low_freqs]
        selected_psd = psd[start_idx:start_idx + num_low_freqs]
        
        positive_mask = selected_psd > 0
        if np.sum(positive_mask) < 3:
            raise ValueError("Insufficient positive power spectral density values")
        
        selected_freqs = selected_freqs[positive_mask]
        selected_psd = selected_psd[positive_mask]
        
        log_freqs = np.log(selected_freqs)
        log_psd = np.log(selected_psd)
        
        stats, _, _, _ = _lazy_import_scipy()
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_freqs, log_psd)
        hurst_estimate = (1 - slope) / 2
        
        additional_metrics = {
            'spectral_slope': slope,
            'regression_r_squared': r_value**2,
            'regression_p_value': p_value,
            'regression_std_error': std_err,
            'frequency_range': (float(selected_freqs[0]), float(selected_freqs[-1])),
            'num_frequencies_used': len(selected_freqs),
            'convergence_flag': r_value**2 > 0.1  # More lenient convergence criteria
        }
        
        self.last_computation_time = time.time() - start_time
        return hurst_estimate, additional_metrics

class RSAnalysisEstimator(BaseHurstEstimator):
    """Rescaled Range (R/S) Analysis estimator"""
    
    def __init__(self):
        super().__init__("R/S Analysis")
    
    def estimate(self, data: np.ndarray, 
                 min_window: Optional[int] = None,
                 max_window: Optional[int] = None,
                 **kwargs) -> Tuple[float, Dict[str, Any]]:
        
        start_time = time.time()
        self.validate_data(data)
        data = np.asarray(data)
        n = len(data)
        
        if min_window is None:
            min_window = max(10, n // 100)
        if max_window is None:
            max_window = min(n // 4, 500)
        
        # Window sizes
        window_sizes = np.unique(np.logspace(np.log10(min_window), 
                                           np.log10(max_window), 20).astype(int))
        
        rs_values = []
        valid_windows = []
        
        for window_size in window_sizes:
            if window_size >= n:
                continue
            
            num_windows = n // window_size
            if num_windows < 2:
                continue
            
            rs_window = []
            for i in range(num_windows):
                start_idx = i * window_size
                end_idx = (i + 1) * window_size
                window_data = data[start_idx:end_idx]
                
                mean_val = np.mean(window_data)
                deviations = window_data - mean_val
                cum_deviations = np.cumsum(deviations)
                
                R = np.max(cum_deviations) - np.min(cum_deviations)
                S = np.std(window_data, ddof=1)
                
                if S > 1e-10:
                    rs_window.append(R / S)
            
            if rs_window:
                rs_values.append(np.mean(rs_window))
                valid_windows.append(window_size)
        
        if len(valid_windows) < 3:
            raise ValueError("Insufficient valid windows for regression")
        
        # Linear regression in log-log space
        log_windows = np.log(valid_windows)
        log_rs = np.log(rs_values)
        
        stats, _, _, _ = _lazy_import_scipy()
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_windows, log_rs)
        hurst_estimate = slope
        
        additional_metrics = {
            'regression_r_squared': r_value**2,
            'regression_p_value': p_value,
            'regression_std_error': std_err,
            'scaling_range': (int(valid_windows[0]), int(valid_windows[-1])),
            'num_windows_used': len(valid_windows),
            'convergence_flag': r_value**2 > 0.7
        }
        
        self.last_computation_time = time.time() - start_time
        return hurst_estimate, additional_metrics

class GPHEstimator(BaseHurstEstimator):
    """Geweke-Porter-Hudak (GPH) estimator"""
    
    def __init__(self):
        super().__init__("GPH")
    
    def estimate(self, data: np.ndarray, 
                 m_fraction: float = 0.5,
                 **kwargs) -> Tuple[float, Dict[str, Any]]:
        
        start_time = time.time()
        self.validate_data(data, min_length=100)
        data = np.asarray(data)
        
        if np.any(np.isnan(data)):
            valid_mask = ~np.isnan(data)
            if np.sum(valid_mask) < len(data) * 0.8:
                raise ValueError("Too many missing values for spectral analysis")
            data = np.interp(np.arange(len(data)), 
                           np.where(valid_mask)[0], 
                           data[valid_mask])
        
        data = data - np.mean(data)
        n = len(data)
        
        # Calculate periodogram
        _, _, fft, fftfreq = _lazy_import_scipy()
        freqs = fftfreq(n, d=1.0)
        fft_data = fft(data)
        periodogram = np.abs(fft_data)**2 / n
        
        positive_freqs = freqs[1:n//2]
        positive_periodogram = periodogram[1:n//2]
        
        m = max(3, int(len(positive_freqs) * m_fraction))
        low_freqs = positive_freqs[:m]
        low_periodogram = positive_periodogram[:m]
        
        # GPH regression
        sin_term = np.sin(low_freqs * np.pi)
        sin_squared = np.maximum(sin_term**2, 1e-10)
        regressor = -np.log(4 * sin_squared)
        log_periodogram = np.log(low_periodogram)
        
        finite_mask = np.isfinite(regressor) & np.isfinite(log_periodogram)
        if np.sum(finite_mask) < 3:
            raise ValueError("Insufficient valid frequencies for GPH regression")
        
        stats, _, _, _ = _lazy_import_scipy()
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            regressor[finite_mask], log_periodogram[finite_mask]
        )
        hurst_estimate = slope + 0.5
        
        additional_metrics = {
            'gph_slope': slope,
            'regression_r_squared': r_value**2,
            'regression_p_value': p_value,
            'regression_std_error': std_err,
            'frequency_range': (float(low_freqs[0]), float(low_freqs[-1])),
            'num_frequencies_used': len(low_freqs),
            'convergence_flag': r_value**2 > 0.1  # More lenient convergence criteria
        }
        
        self.last_computation_time = time.time() - start_time
        return hurst_estimate, additional_metrics

class WhittleMLEEstimator(BaseHurstEstimator):
    """Local Whittle Maximum Likelihood Estimator"""
    
    def __init__(self):
        super().__init__("Local Whittle MLE")
    
    def estimate(self, data: np.ndarray, 
                 m_fraction: float = 0.5,
                 **kwargs) -> Tuple[float, Dict[str, Any]]:
        
        start_time = time.time()
        self.validate_data(data, min_length=100)
        data = np.asarray(data)
        
        if np.any(np.isnan(data)):
            valid_mask = ~np.isnan(data)
            if np.sum(valid_mask) < len(data) * 0.8:
                raise ValueError("Too many missing values for spectral analysis")
            data = np.interp(np.arange(len(data)), 
                           np.where(valid_mask)[0], 
                           data[valid_mask])
        
        data = data - np.mean(data)
        n = len(data)
        
        # Calculate periodogram
        _, _, fft, fftfreq = _lazy_import_scipy()
        freqs = fftfreq(n, d=1.0)
        fft_data = fft(data)
        periodogram = np.abs(fft_data)**2 / n
        
        positive_freqs = freqs[1:n//2]
        positive_periodogram = periodogram[1:n//2]
        
        m = max(3, int(len(positive_freqs) * m_fraction))
        selected_freqs = positive_freqs[:m]
        selected_periodogram = positive_periodogram[:m]
        
        def negative_log_likelihood(theta):
            d = theta[0]  # d = H - 0.5
            spectral_density = selected_freqs**(-2*d)
            spectral_density = np.maximum(spectral_density, 1e-10)
            return np.sum(np.log(spectral_density) + selected_periodogram / spectral_density)
        
        try:
            optimize = _lazy_import_optimize()
            result = optimize.minimize(negative_log_likelihood, [0.0], 
                                     bounds=[(-0.49, 0.49)], method='L-BFGS-B')
            
            if result.success:
                d_estimate = result.x[0]
                hurst_estimate = d_estimate + 0.5
                convergence_flag = True
            else:
                hurst_estimate = np.nan
                convergence_flag = False
        except:
            hurst_estimate = np.nan
            convergence_flag = False
        
        additional_metrics = {
            'd_estimate': d_estimate if 'd_estimate' in locals() else np.nan,
            'frequency_range': (float(selected_freqs[0]), float(selected_freqs[-1])),
            'num_frequencies_used': len(selected_freqs),
            'convergence_flag': convergence_flag
        }
        
        self.last_computation_time = time.time() - start_time
        return hurst_estimate, additional_metrics

class GHEEstimator(BaseHurstEstimator):
    """Generalized Hurst Exponent estimator"""
    
    def __init__(self):
        super().__init__("GHE")
    
    def estimate(self, data: np.ndarray, 
                 q_values: Optional[List[float]] = None,
                 max_tau: int = 100,
                 **kwargs) -> Tuple[float, Dict[str, Any]]:
        
        start_time = time.time()
        self.validate_data(data)
        data = np.asarray(data)
        n = len(data)
        
        if q_values is None:
            q_values = [2.0]
        
        tau_values = np.unique(np.logspace(0, np.log10(min(max_tau, n//10)), 15).astype(int))
        hurst_estimates = []
        
        for q in q_values:
            moments = []
            
            for tau in tau_values:
                if tau >= n:
                    continue
                
                increments = []
                for i in range(n - tau):
                    increment = abs(data[i + tau] - data[i])
                    increments.append(increment)
                
                if len(increments) == 0:
                    continue
                
                if q == 0:
                    log_increments = np.log(np.array(increments) + 1e-10)
                    moment = np.exp(np.mean(log_increments))
                else:
                    moment = np.mean(np.array(increments)**q)**(1/q)
                
                moments.append(moment)
            
            # Linear regression in log-log space
            valid_indices = ~np.isnan(moments)
            if np.sum(valid_indices) < 3:
                hurst_estimates.append(np.nan)
                continue
            
            valid_tau = tau_values[:len(moments)][valid_indices]
            valid_moments = np.array(moments)[valid_indices]
            
            log_tau = np.log(valid_tau)
            log_moments = np.log(valid_moments)
            
            stats, _, _, _ = _lazy_import_scipy()
            slope, intercept, r_value, p_value, std_err = stats.linregress(log_tau, log_moments)
            
            # For GHE: log(M_q(τ)) = H(q) * log(τ) + constant
            # The slope directly gives us H(q), no bias correction needed
            hurst_estimates.append(slope)
        
        hurst_estimate = hurst_estimates[0] if len(q_values) == 1 else hurst_estimates
        
        additional_metrics = {
            'q_values': q_values,
            'hurst_estimates': hurst_estimates,
            'tau_range': (int(tau_values[0]), int(tau_values[-1])),
            'convergence_flag': not np.isnan(hurst_estimate)
        }
        
        self.last_computation_time = time.time() - start_time
        return hurst_estimate, additional_metrics

# Wavelet-based estimators
class DWTEstimator(BaseHurstEstimator):
    """Discrete Wavelet Transform Logscale estimator"""
    
    def __init__(self):
        super().__init__("DWT Logscale")
    
    def estimate(self, data: np.ndarray, 
                 wavelet: str = 'db4',
                 max_level: Optional[int] = None,
                 **kwargs) -> Tuple[float, Dict[str, Any]]:
        
        start_time = time.time()
        self.validate_data(data, min_length=100)
        data = np.asarray(data)
        
        if np.any(np.isnan(data)):
            valid_mask = ~np.isnan(data)
            if np.sum(valid_mask) < len(data) * 0.8:
                raise ValueError("Too many missing values for wavelet analysis")
            data = np.interp(np.arange(len(data)), 
                           np.where(valid_mask)[0], 
                           data[valid_mask])
        
        data = data - np.mean(data)
        n = len(data)
        
        if max_level is None:
            max_level = min(int(np.log2(n)) - 2, 8)
        
        try:
            # Lazy import of PyWavelets
            import pywt
            
            # Check maximum possible level for DWT
            max_possible_level = pywt.dwt_max_level(n, wavelet)
            max_level = min(max_level, max_possible_level)
            
            # Perform DWT decomposition
            coeffs = pywt.wavedec(data, wavelet, level=max_level)
            detail_coeffs = coeffs[1:]  # Skip approximation coefficients
            
            # Calculate wavelet variance for each level
            # Note: PyWavelets returns coefficients from finest to coarsest scale
            # We need to reverse the order to get increasing variances with scale
            scales = []
            variances = []
            
            for i, detail in enumerate(reversed(detail_coeffs)):
                if len(detail) > 0:
                    scale = 2**(i + 1)
                    variance = np.var(detail)
                    if variance > 0:
                        scales.append(scale)
                        variances.append(variance)
            
            if len(scales) < 3:
                raise ValueError("Insufficient wavelet levels for regression")
            
            # Linear regression in log2-log2 space (as per research)
            # log_2(μ_j²) ~ (2H+1)j + constant, so H = (slope - 1) / 2
            log2_scales = np.log2(scales)
            log2_variances = np.log2(variances)
            
            stats, _, _, _ = _lazy_import_scipy()
            slope, intercept, r_value, p_value, std_err = stats.linregress(log2_scales, log2_variances)
            
            # Hurst exponent from wavelet variance slope
            # Correct formula: H = (slope - 1) / 2
            hurst_estimate = (slope - 1) / 2
            
            additional_metrics = {
                'wavelet_variance_slope': slope,
                'regression_r_squared': r_value**2,
                'regression_p_value': p_value,
                'regression_std_error': std_err,
                'scales_used': scales,
                'wavelet': wavelet,
                'max_level': max_level,
                'convergence_flag': r_value**2 > 0.7,
                'debug_log2_scales': log2_scales.tolist(),
                'debug_log2_variances': log2_variances.tolist()
            }
            
        except ImportError:
            # Fallback to simple approximation if PyWavelets not available
            logger.warning("PyWavelets not available, using simplified DWT approximation")
            
            # Simple approximation using differences at different scales
            scales = [2, 4, 8, 16, 32]
            variances = []
            
            for scale in scales:
                if scale < n:
                    # Downsample and calculate variance
                    downsampled = data[::scale]
                    if len(downsampled) > 10:
                        variances.append(np.var(downsampled))
                    else:
                        break
            
            if len(variances) < 3:
                raise ValueError("Insufficient scales for DWT approximation")
            
            # Use log2-log2 space for consistency with research
            log2_scales = np.log2(scales[:len(variances)])
            log2_variances = np.log2(variances)
            
            stats, _, _, _ = _lazy_import_scipy()
            slope, intercept, r_value, p_value, std_err = stats.linregress(log2_scales, log2_variances)
            
            # Correct formula for wavelet variance scaling: H = (slope - 1) / 2
            hurst_estimate = (slope - 1) / 2
            
            additional_metrics = {
                'wavelet_variance_slope': slope,
                'regression_r_squared': r_value**2,
                'regression_p_value': p_value,
                'regression_std_error': std_err,
                'scales_used': scales[:len(variances)],
                'wavelet': 'approximation',
                'max_level': len(variances),
                'convergence_flag': r_value**2 > 0.5,
                'note': 'Simplified approximation (PyWavelets not available)'
            }
        
        self.last_computation_time = time.time() - start_time
        return hurst_estimate, additional_metrics

class AbryVeitchEstimator(BaseHurstEstimator):
    """Abry-Veitch wavelet-based estimator"""
    
    def __init__(self):
        super().__init__("Abry-Veitch")
    
    def estimate(self, data: np.ndarray, 
                 wavelet: str = 'db4',
                 max_level: Optional[int] = None,
                 **kwargs) -> Tuple[float, Dict[str, Any]]:
        
        start_time = time.time()
        self.validate_data(data, min_length=100)
        data = np.asarray(data)
        
        if np.any(np.isnan(data)):
            valid_mask = ~np.isnan(data)
            if np.sum(valid_mask) < len(data) * 0.8:
                raise ValueError("Too many missing values for wavelet analysis")
            data = np.interp(np.arange(len(data)), 
                           np.where(valid_mask)[0], 
                           data[valid_mask])
        
        data = data - np.mean(data)
        n = len(data)
        
        if max_level is None:
            max_level = min(int(np.log2(n)) - 2, 8)
        
        try:
            # Lazy import of PyWavelets
            import pywt
            
            # Check maximum possible level for DWT
            max_possible_level = pywt.dwt_max_level(n, wavelet)
            max_level = min(max_level, max_possible_level)
            
            # Perform DWT decomposition
            coeffs = pywt.wavedec(data, wavelet, level=max_level)
            detail_coeffs = coeffs[1:]  # Skip approximation coefficients
            
            # Abry-Veitch method: use log2 of wavelet coefficients
            # Note: PyWavelets returns coefficients from finest to coarsest scale
            # We need to reverse the order to get increasing energies with scale
            scales = []
            log2_energies = []
            
            for i, detail in enumerate(reversed(detail_coeffs)):
                if len(detail) > 0:
                    scale = 2**(i + 1)
                    # Calculate log2 of the mean squared coefficients
                    mean_squared = np.mean(detail**2)
                    if mean_squared > 0:
                        log2_energy = np.log2(mean_squared)
                        scales.append(scale)
                        log2_energies.append(log2_energy)
            
            if len(scales) < 3:
                raise ValueError("Insufficient wavelet levels for Abry-Veitch regression")
            
            # Linear regression: log2(energy) vs log2(scale)
            log2_scales = np.log2(scales)
            
            stats, _, _, _ = _lazy_import_scipy()
            slope, intercept, r_value, p_value, std_err = stats.linregress(log2_scales, log2_energies)
            
            # Hurst exponent from Abry-Veitch relationship
            # Correct formula: H = (slope - 1) / 2
            hurst_estimate = (slope - 1) / 2
            
            additional_metrics = {
                'abry_veitch_slope': slope,
                'regression_r_squared': r_value**2,
                'regression_p_value': p_value,
                'regression_std_error': std_err,
                'scales_used': scales,
                'log2_energies': log2_energies,
                'wavelet': wavelet,
                'max_level': max_level,
                'convergence_flag': r_value**2 > 0.7
            }
            
        except ImportError:
            # Fallback to simplified approximation
            logger.warning("PyWavelets not available, using simplified Abry-Veitch approximation")
            
            # Simple approximation using differences at different scales
            scales = [2, 4, 8, 16, 32]
            log2_energies = []
            
            for scale in scales:
                if scale < n:
                    # Downsample and calculate mean squared differences
                    downsampled = data[::scale]
                    if len(downsampled) > 10:
                        mean_squared = np.mean(downsampled**2)
                        if mean_squared > 0:
                            log2_energies.append(np.log2(mean_squared))
                        else:
                            break
                    else:
                        break
            
            if len(log2_energies) < 3:
                raise ValueError("Insufficient scales for Abry-Veitch approximation")
            
            log2_scales = np.log2(scales[:len(log2_energies)])
            
            stats, _, _, _ = _lazy_import_scipy()
            slope, intercept, r_value, p_value, std_err = stats.linregress(log2_scales, log2_energies)
            
            # Correct formula for wavelet variance scaling: H = (slope - 1) / 2
            hurst_estimate = (slope - 1) / 2
            
            additional_metrics = {
                'abry_veitch_slope': slope,
                'regression_r_squared': r_value**2,
                'regression_p_value': p_value,
                'regression_std_error': std_err,
                'scales_used': scales[:len(log2_energies)],
                'log2_energies': log2_energies,
                'wavelet': 'approximation',
                'max_level': len(log2_energies),
                'convergence_flag': r_value**2 > 0.5,
                'note': 'Simplified approximation (PyWavelets not available)'
            }
        
        self.last_computation_time = time.time() - start_time
        return hurst_estimate, additional_metrics

class NDWTEstimator(BaseHurstEstimator):
    """Non-decimated Wavelet Transform Logscale estimator"""
    
    def __init__(self):
        super().__init__("NDWT Logscale")
    
    def estimate(self, data: np.ndarray, 
                 wavelet: str = 'db4',
                 max_level: Optional[int] = None,
                 **kwargs) -> Tuple[float, Dict[str, Any]]:
        
        start_time = time.time()
        self.validate_data(data, min_length=100)
        data = np.asarray(data)
        
        if np.any(np.isnan(data)):
            valid_mask = ~np.isnan(data)
            if np.sum(valid_mask) < len(data) * 0.8:
                raise ValueError("Too many missing values for wavelet analysis")
            data = np.interp(np.arange(len(data)), 
                           np.where(valid_mask)[0], 
                           data[valid_mask])
        
        data = data - np.mean(data)
        n = len(data)
        
        if max_level is None:
            max_level = min(int(np.log2(n)) - 2, 8)
        
        try:
            # Lazy import of PyWavelets
            import pywt
            
            # Check maximum possible level for SWT
            max_possible_level = pywt.swt_max_level(n)
            max_level = min(max_level, max_possible_level)
            
            # Perform NDWT (Stationary Wavelet Transform) decomposition
            coeffs = pywt.swt(data, wavelet, level=max_level)
            detail_coeffs = [coeff[1] for coeff in coeffs]  # Extract detail coefficients
            
            # Calculate wavelet variance for each level
            # Note: PyWavelets returns coefficients from finest to coarsest scale
            # We need to reverse the order to get increasing variances with scale
            scales = []
            variances = []
            
            for i, detail in enumerate(reversed(detail_coeffs)):
                if len(detail) > 0:
                    scale = 2**(i + 1)
                    variance = np.var(detail)
                    if variance > 0:
                        scales.append(scale)
                        variances.append(variance)
            
            if len(scales) < 3:
                raise ValueError("Insufficient NDWT levels for regression")
            
            # Linear regression in log-log space
            log_scales = np.log(scales)
            log_variances = np.log(variances)
            
            stats, _, _, _ = _lazy_import_scipy()
            slope, intercept, r_value, p_value, std_err = stats.linregress(log_scales, log_variances)
            
            # Hurst exponent from NDWT variance slope
            # Correct formula for wavelet variance scaling: H = (slope - 1) / 2
            hurst_estimate = (slope - 1) / 2
            
            additional_metrics = {
                'ndwt_variance_slope': slope,
                'regression_r_squared': r_value**2,
                'regression_p_value': p_value,
                'regression_std_error': std_err,
                'scales_used': scales,
                'wavelet': wavelet,
                'max_level': max_level,
                'convergence_flag': r_value**2 > 0.7
            }
            
        except ImportError:
            # Fallback to simplified approximation if PyWavelets not available
            logger.warning("PyWavelets not available, using simplified NDWT approximation")
            
            # Simple approximation using differences at different scales
            # NDWT is similar to DWT but without decimation
            scales = [2, 4, 8, 16, 32]
            variances = []
            
            for scale in scales:
                if scale < n:
                    # Calculate differences at different scales (approximating NDWT)
                    if scale == 1:
                        diff_data = np.diff(data)
                    else:
                        # Simple approximation: take differences at scale intervals
                        diff_data = data[scale:] - data[:-scale]
                    
                    if len(diff_data) > 10:
                        variances.append(np.var(diff_data))
                    else:
                        break
            
            if len(variances) < 3:
                raise ValueError("Insufficient scales for NDWT approximation")
            
            log_scales = np.log(scales[:len(variances)])
            log_variances = np.log(variances)
            
            stats, _, _, _ = _lazy_import_scipy()
            slope, intercept, r_value, p_value, std_err = stats.linregress(log_scales, log_variances)
            
            # Correct formula for wavelet variance scaling: H = (slope - 1) / 2
            hurst_estimate = (slope - 1) / 2
            
            additional_metrics = {
                'ndwt_variance_slope': slope,
                'regression_r_squared': r_value**2,
                'regression_p_value': p_value,
                'regression_std_error': std_err,
                'scales_used': scales[:len(variances)],
                'wavelet': 'approximation',
                'max_level': len(variances),
                'convergence_flag': r_value**2 > 0.5,
                'note': 'Simplified approximation (PyWavelets not available)'
            }
        
        self.last_computation_time = time.time() - start_time
        return hurst_estimate, additional_metrics

class MFDFAEstimator(BaseHurstEstimator):
    """Multifractal Detrended Fluctuation Analysis estimator (q=2)"""
    
    def __init__(self):
        super().__init__("MFDFA(q=2)")
    
    def estimate(self, data: np.ndarray, 
                 q: float = 2.0,
                 min_window: Optional[int] = None,
                 max_window: Optional[int] = None,
                 polynomial_order: int = 1,
                 overlap: float = 0.5,
                 **kwargs) -> Tuple[float, Dict[str, Any]]:
        
        start_time = time.time()
        self.validate_data(data)
        data = np.asarray(data)
        n = len(data)
        
        if min_window is None:
            min_window = max(10, n // 100)
        if max_window is None:
            max_window = min(n // 4, 500)
        
        # Remove mean and integrate (profile)
        mean_val = np.nanmean(data)
        profile = np.nancumsum(data - mean_val)
        
        # Handle NaN values
        if np.any(np.isnan(profile)):
            valid_mask = ~np.isnan(profile)
            profile = np.interp(np.arange(len(profile)), 
                              np.where(valid_mask)[0], 
                              profile[valid_mask])
        
        # Window sizes
        window_sizes = np.unique(np.logspace(np.log10(min_window), 
                                           np.log10(max_window), 20).astype(int))
        
        fluctuations = []
        valid_windows = []
        
        for window_size in window_sizes:
            if window_size >= n:
                continue
            
            step_size = max(1, int(window_size * (1 - overlap)))
            segment_fluctuations = []
            
            for start in range(0, n - window_size + 1, step_size):
                segment = profile[start:start + window_size]
                t = np.arange(len(segment))
                
                try:
                    coeffs = np.polyfit(t, segment, polynomial_order)
                    trend = np.polyval(coeffs, t)
                    detrended = segment - trend
                    
                    # Calculate q-th order fluctuation
                    if q == 0:
                        # Special case for q=0: use log of mean squared
                        fluctuation = np.exp(np.mean(np.log(detrended**2 + 1e-10)))
                    else:
                        fluctuation = np.mean(np.abs(detrended)**q)**(1/q)
                    
                    if fluctuation > 0:
                        segment_fluctuations.append(fluctuation)
                        
                except np.linalg.LinAlgError:
                    continue
            
            if segment_fluctuations:
                # Average fluctuation for this window size
                if q == 0:
                    avg_fluctuation = np.exp(np.mean(np.log(segment_fluctuations)))
                else:
                    avg_fluctuation = np.mean(segment_fluctuations)
                
                fluctuations.append(avg_fluctuation)
                valid_windows.append(window_size)
        
        if len(valid_windows) < 3:
            raise ValueError("Insufficient valid windows for MFDFA regression")
        
        # Linear regression
        log_windows = np.log(valid_windows)
        log_fluctuations = np.log(fluctuations)
        
        stats, _, _, _ = _lazy_import_scipy()
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_windows, log_fluctuations)
        
        # For q=2, the slope gives the Hurst exponent directly
        # For other q values, this would be the generalized Hurst exponent h(q)
        hurst_estimate = slope
        
        additional_metrics = {
            'mfdfa_slope': slope,
            'q_value': q,
            'regression_r_squared': r_value**2,
            'regression_p_value': p_value,
            'regression_std_error': std_err,
            'scaling_range': (int(valid_windows[0]), int(valid_windows[-1])),
            'num_windows_used': len(valid_windows),
            'polynomial_order': polynomial_order,
            'convergence_flag': r_value**2 > 0.8
        }
        
        self.last_computation_time = time.time() - start_time
        return hurst_estimate, additional_metrics

class MFDMAEstimator(BaseHurstEstimator):
    """Multifractal Detrended Moving Average estimator (q=2)"""
    
    def __init__(self):
        super().__init__("MF-DMA(q=2)")
    
    def estimate(self, data: np.ndarray, 
                 q: float = 2.0,
                 min_window: Optional[int] = None,
                 max_window: Optional[int] = None,
                 overlap: float = 0.5,
                 **kwargs) -> Tuple[float, Dict[str, Any]]:
        
        start_time = time.time()
        self.validate_data(data)
        data = np.asarray(data)
        n = len(data)
        
        if min_window is None:
            min_window = max(10, n // 100)
        if max_window is None:
            max_window = min(n // 4, 500)
        
        # Window sizes
        window_sizes = np.unique(np.logspace(np.log10(min_window), 
                                           np.log10(max_window), 20).astype(int))
        
        fluctuations = []
        valid_windows = []
        
        for window_size in window_sizes:
            if window_size >= n:
                continue
            
            step_size = max(1, int(window_size * (1 - overlap)))
            segment_fluctuations = []
            
            for start in range(0, n - window_size + 1, step_size):
                segment = data[start:start + window_size]
                
                # Calculate moving average (DMA detrending)
                # Simple moving average as detrending method
                window_half = window_size // 2
                if window_half > 0:
                    # Calculate moving average
                    ma = np.convolve(segment, np.ones(window_half)/window_half, mode='same')
                    detrended = segment - ma
                else:
                    detrended = segment - np.mean(segment)
                
                # Calculate q-th order fluctuation
                if q == 0:
                    # Special case for q=0: use log of mean squared
                    fluctuation = np.exp(np.mean(np.log(detrended**2 + 1e-10)))
                else:
                    fluctuation = np.mean(np.abs(detrended)**q)**(1/q)
                
                if fluctuation > 0:
                    segment_fluctuations.append(fluctuation)
            
            if segment_fluctuations:
                # Average fluctuation for this window size
                if q == 0:
                    avg_fluctuation = np.exp(np.mean(np.log(segment_fluctuations)))
                else:
                    avg_fluctuation = np.mean(segment_fluctuations)
                
                fluctuations.append(avg_fluctuation)
                valid_windows.append(window_size)
        
        if len(valid_windows) < 3:
            raise ValueError("Insufficient valid windows for MF-DMA regression")
        
        # Linear regression
        log_windows = np.log(valid_windows)
        log_fluctuations = np.log(fluctuations)
        
        stats, _, _, _ = _lazy_import_scipy()
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_windows, log_fluctuations)
        
        # For q=2, the slope gives the Hurst exponent directly
        # For other q values, this would be the generalized Hurst exponent h(q)
        hurst_estimate = slope
        
        additional_metrics = {
            'mfdma_slope': slope,
            'q_value': q,
            'regression_r_squared': r_value**2,
            'regression_p_value': p_value,
            'regression_std_error': std_err,
            'scaling_range': (int(valid_windows[0]), int(valid_windows[-1])),
            'num_windows_used': len(valid_windows),
            'convergence_flag': r_value**2 > 0.8
        }
        
        self.last_computation_time = time.time() - start_time
        return hurst_estimate, additional_metrics

# ============================================================================
# CONFIDENCE ESTIMATION
# ============================================================================

class ConfidenceEstimator:
    """Statistical confidence estimation for Hurst exponents"""
    
    @staticmethod
    def bootstrap_confidence(estimator: BaseHurstEstimator, 
                           data: np.ndarray,
                           n_bootstrap: int = 100,
                           confidence_level: float = 0.95,
                           random_state: Optional[int] = None) -> Tuple[float, Tuple[float, float], np.ndarray]:
        
        if random_state is not None:
            np.random.seed(random_state)
        
        n = len(data)
        bootstrap_estimates = []
        
        for _ in range(n_bootstrap):
            bootstrap_indices = np.random.choice(n, size=n, replace=True)
            bootstrap_data = data[bootstrap_indices]
            
            try:
                h_est, _ = estimator.estimate(bootstrap_data)
                if not np.isnan(h_est) and 0.01 <= h_est <= 0.99:
                    bootstrap_estimates.append(h_est)
            except:
                continue
        
        if len(bootstrap_estimates) < 10:
            return np.nan, (np.nan, np.nan), np.array([])
        
        bootstrap_estimates = np.array(bootstrap_estimates)
        mean_estimate = np.mean(bootstrap_estimates)
        
        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        ci_lower = np.percentile(bootstrap_estimates, lower_percentile)
        ci_upper = np.percentile(bootstrap_estimates, upper_percentile)
        
        return mean_estimate, (ci_lower, ci_upper), bootstrap_estimates
    
    @staticmethod
    def theoretical_confidence(hurst_estimate: float,
                             standard_error: float,
                             n_samples: int,
                             confidence_level: float = 0.95) -> Tuple[float, float]:
        
        alpha = 1 - confidence_level
        stats, _, _, _ = _lazy_import_scipy()
        z_score = stats.norm.ppf(1 - alpha / 2)
        
        margin = z_score * standard_error
        ci_lower = max(0.01, hurst_estimate - margin)
        ci_upper = min(0.99, hurst_estimate + margin)
        
        return ci_lower, ci_upper


class BayesianHurstEstimator:
    """Bayesian inference for Hurst exponent estimation using NumPyro"""
    
    def __init__(self, estimator_type: EstimatorType = EstimatorType.DFA):
        self.estimator_type = estimator_type
        self.numpyro, self.dist, self.MCMC, self.NUTS, self.Predictive, self.jnp, self.jax = _lazy_import_numpyro()
    
    def dfa_model(self, data, min_window: int = 10, max_window: int = None):
        """
        Bayesian model for DFA-based Hurst estimation
        
        Model: log(F(n)) = log(C) + H * log(n) + ε
        where ε ~ Normal(0, σ²)
        """
        n = len(data)
        if max_window is None:
            max_window = n // 4
        
        # Generate window sizes
        window_sizes = np.unique(np.logspace(np.log10(min_window), 
                                           np.log10(max_window), 20).astype(int))
        window_sizes = window_sizes[window_sizes < n]
        
        # Calculate fluctuations for each window size
        fluctuations = []
        for window_size in window_sizes:
            # Simple DFA calculation
            profile = np.cumsum(data - np.mean(data))
            segments = len(profile) // window_size
            if segments < 1:
                continue
                
            segment_fluctuations = []
            for i in range(segments):
                segment = profile[i * window_size:(i + 1) * window_size]
                # Detrend (linear)
                x = np.arange(len(segment))
                coeffs = np.polyfit(x, segment, 1)
                trend = np.polyval(coeffs, x)
                detrended = segment - trend
                fluctuation = np.sqrt(np.mean(detrended**2))
                segment_fluctuations.append(fluctuation)
            
            if segment_fluctuations:
                fluctuations.append(np.mean(segment_fluctuations))
            else:
                break
        
        if len(fluctuations) < 3:
            raise ValueError("Insufficient data for DFA analysis")
        
        # Convert to JAX arrays
        window_sizes_jax = self.jnp.array(window_sizes[:len(fluctuations)], dtype=self.jnp.float32)
        fluctuations_jax = self.jnp.array(fluctuations, dtype=self.jnp.float32)
        log_windows = self.jnp.log(window_sizes_jax)
        log_fluctuations = self.jnp.log(fluctuations_jax)
        
        # Bayesian model
        # Prior for Hurst exponent: Beta distribution centered around 0.5
        hurst = self.numpyro.sample("hurst", self.dist.Beta(2.0, 2.0))
        
        # Prior for log constant
        log_c = self.numpyro.sample("log_c", self.dist.Normal(0.0, 2.0))
        
        # Prior for noise variance
        sigma = self.numpyro.sample("sigma", self.dist.HalfNormal(1.0))
        
        # Likelihood: log(F) = log(C) + H * log(n) + ε
        mean = log_c + hurst * log_windows
        self.numpyro.sample("obs", self.dist.Normal(mean, sigma), obs=log_fluctuations)
        
        return hurst, log_c, sigma
    
    def periodogram_model(self, data, low_freq_fraction: float = 0.4):
        """
        Bayesian model for periodogram-based Hurst estimation
        
        Model: log(S(f)) = log(C) - (2H-1) * log(f) + ε
        """
        # Calculate periodogram
        fft_data = np.fft.fft(data - np.mean(data))
        freqs = np.fft.fftfreq(len(data))
        
        # Use only positive frequencies up to low_freq_fraction
        n_freqs = int(len(data) * low_freq_fraction)
        freqs = freqs[1:n_freqs]  # Exclude DC component
        power = np.abs(fft_data[1:n_freqs])**2
        
        # Convert to JAX arrays
        freqs_pos = freqs[freqs > 0]
        power_pos = power[freqs > 0]
        freqs_jax = self.jnp.array(freqs_pos, dtype=self.jnp.float32)
        power_jax = self.jnp.array(power_pos, dtype=self.jnp.float32)
        log_freqs = self.jnp.log(freqs_jax)
        log_power = self.jnp.log(power_jax)
        
        # Bayesian model
        hurst = self.numpyro.sample("hurst", self.dist.Beta(2.0, 2.0))
        log_c = self.numpyro.sample("log_c", self.dist.Normal(0.0, 2.0))
        sigma = self.numpyro.sample("sigma", self.dist.HalfNormal(1.0))
        
        # Likelihood: log(S) = log(C) - (2H-1) * log(f) + ε
        mean = log_c - (2 * hurst - 1) * log_freqs
        self.numpyro.sample("obs", self.dist.Normal(mean, sigma), obs=log_power)
        
        return hurst, log_c, sigma
    
    def infer_hurst(self, 
                   data: np.ndarray,
                   num_samples: int = 1000,
                   num_warmup: int = 500,
                   num_chains: int = 4,
                   random_seed: int = 42) -> Dict[str, Any]:
        """
        Perform Bayesian inference for Hurst exponent
        
        Parameters:
        -----------
        data : np.ndarray
            Time series data
        num_samples : int
            Number of MCMC samples
        num_warmup : int
            Number of warmup samples
        num_chains : int
            Number of MCMC chains
        random_seed : int
            Random seed for reproducibility
            
        Returns:
        --------
        Dict containing posterior samples and statistics
        """
        try:
            # Select model based on estimator type
            if self.estimator_type == EstimatorType.DFA:
                model = self.dfa_model
            elif self.estimator_type == EstimatorType.PERIODOGRAM:
                model = self.periodogram_model
            else:
                # Default to DFA for other estimators
                model = self.dfa_model
            
            # Set up MCMC
            nuts_kernel = self.NUTS(model)
            
            # Adjust number of chains based on available devices
            available_devices = self.jax.local_device_count()
            actual_chains = min(num_chains, available_devices)
            
            mcmc = self.MCMC(nuts_kernel, num_samples=num_samples, num_warmup=num_warmup, num_chains=actual_chains)
            
            # Run MCMC
            rng_key = self.jax.random.PRNGKey(random_seed)
            mcmc.run(rng_key, data)
            
            # Get samples
            samples = mcmc.get_samples()
            
            # Calculate statistics
            hurst_samples = samples['hurst']
            hurst_mean = float(np.mean(hurst_samples))
            hurst_std = float(np.std(hurst_samples))
            
            # Credible intervals
            ci_lower = float(np.percentile(hurst_samples, 2.5))
            ci_upper = float(np.percentile(hurst_samples, 97.5))
            
            # Diagnostic metrics
            rhat = self._calculate_rhat(hurst_samples.reshape(actual_chains, -1))
            
            return {
                'hurst_mean': hurst_mean,
                'hurst_std': hurst_std,
                'credible_interval': (ci_lower, ci_upper),
                'rhat': rhat,
                'samples': samples,
                'mcmc': mcmc,
                'convergence_flag': rhat < 1.1
            }
            
        except Exception as e:
            logger.error(f"Bayesian inference failed: {e}")
            return {
                'hurst_mean': np.nan,
                'hurst_std': np.nan,
                'credible_interval': (np.nan, np.nan),
                'rhat': np.nan,
                'samples': {},
                'mcmc': None,
                'convergence_flag': False,
                'error': str(e)
            }
    
    def _calculate_rhat(self, samples: np.ndarray) -> float:
        """Calculate R-hat diagnostic for convergence checking"""
        # samples shape: (num_chains, num_samples)
        chain_means = np.mean(samples, axis=1)
        chain_vars = np.var(samples, axis=1)
        
        # Between-chain variance
        B = len(samples[0]) * np.var(chain_means)
        
        # Within-chain variance
        W = np.mean(chain_vars)
        
        # Pooled variance
        var_plus = (len(samples[0]) - 1) / len(samples[0]) * W + B / len(samples[0])
        
        # R-hat
        rhat = np.sqrt(var_plus / W)
        return float(rhat)
    
    @staticmethod
    def bayesian_confidence(estimator: BaseHurstEstimator,
                          data: np.ndarray,
                          estimator_type: EstimatorType = EstimatorType.DFA,
                          num_samples: int = 1000,
                          num_warmup: int = 500,
                          random_seed: Optional[int] = None) -> Tuple[float, Tuple[float, float], Dict[str, Any]]:
        """
        Static method for Bayesian confidence estimation
        
        Parameters:
        -----------
        estimator : BaseHurstEstimator
            Estimator instance (not used in Bayesian approach, but kept for interface consistency)
        data : np.ndarray
            Time series data
        estimator_type : EstimatorType
            Type of estimator to use for Bayesian model
        num_samples : int
            Number of MCMC samples
        num_warmup : int
            Number of warmup samples
        random_seed : int
            Random seed
            
        Returns:
        --------
        Tuple of (mean_estimate, credible_interval, inference_results)
        """
        if random_seed is None:
            random_seed = 42
            
        bayesian_estimator = BayesianHurstEstimator(estimator_type)
        results = bayesian_estimator.infer_hurst(data, num_samples, num_warmup, random_seed=random_seed)
        
        return results['hurst_mean'], results['credible_interval'], results

# ============================================================================
# MAIN FACTORY CLASS
# ============================================================================

class BiomedicalHurstEstimatorFactory:
    """Main factory for biomedical time series Hurst exponent estimation"""
    
    def __init__(self):
        self.estimators = {
            EstimatorType.DFA: DFAEstimator(),
            EstimatorType.HIGUCHI: HiguchiEstimator(),
            EstimatorType.PERIODOGRAM: PeriodogramEstimator(),
            EstimatorType.RS_ANALYSIS: RSAnalysisEstimator(),
            EstimatorType.GPH: GPHEstimator(),
            EstimatorType.WHITTLE_MLE: WhittleMLEEstimator(),
            EstimatorType.GENERALIZED_HURST: GHEEstimator(),
            EstimatorType.DWT: DWTEstimator(),
            EstimatorType.ABRY_VEITCH: AbryVeitchEstimator(),
            EstimatorType.NDWT: NDWTEstimator(),
            EstimatorType.MFDFA: MFDFAEstimator(),
            EstimatorType.MF_DMA: MFDMAEstimator(),
        }
        
        self.groups = {
            EstimatorType.TEMPORAL: [EstimatorType.DFA, EstimatorType.HIGUCHI, EstimatorType.RS_ANALYSIS, EstimatorType.GENERALIZED_HURST],
            EstimatorType.SPECTRAL: [EstimatorType.PERIODOGRAM, EstimatorType.GPH, EstimatorType.WHITTLE_MLE],
            EstimatorType.WAVELET: [EstimatorType.DWT, EstimatorType.ABRY_VEITCH, EstimatorType.NDWT],
            EstimatorType.ALL: [
                EstimatorType.DFA, EstimatorType.HIGUCHI, EstimatorType.PERIODOGRAM,
                EstimatorType.RS_ANALYSIS, EstimatorType.GPH, EstimatorType.WHITTLE_MLE,
                EstimatorType.GENERALIZED_HURST, EstimatorType.DWT, EstimatorType.ABRY_VEITCH,
                EstimatorType.NDWT, EstimatorType.MFDFA, EstimatorType.MF_DMA
            ]
        }
        
        self.data_processor = BiomedicalDataProcessor()
        self.confidence_estimator = ConfidenceEstimator()
    
    def estimate(self, 
                 data: Union[np.ndarray, List[float]], 
                 method: Union[str, EstimatorType],
                 confidence_method: Union[str, ConfidenceMethod] = ConfidenceMethod.BOOTSTRAP,
                 confidence_level: float = 0.95,
                 preprocess: bool = True,
                 assess_quality: bool = True,
                 **kwargs) -> Union[HurstResult, GroupHurstResult]:
        """
        Main estimation method
        
        Parameters:
        - data: Time series data
        - method: Estimator type or group type
        - confidence_method: Method for confidence interval estimation
        - confidence_level: Confidence level (0-1)
        - preprocess: Whether to preprocess data
        - assess_quality: Whether to assess data quality
        - **kwargs: Additional parameters for specific methods
        """
        
        data = np.asarray(data, dtype=float)
        
        if isinstance(method, str):
            try:
                method = EstimatorType(method.lower())
            except ValueError:
                raise ValueError(f"Unknown method: {method}")
        
        # Convert confidence_method string to enum if needed
        if isinstance(confidence_method, str):
            try:
                confidence_method = ConfidenceMethod(confidence_method.lower())
            except ValueError:
                raise ValueError(f"Unknown confidence method: {confidence_method}")
        
        # Data quality assessment
        quality_metrics = {}
        if assess_quality:
            quality_metrics = self.data_processor.assess_data_quality(data)
            if quality_metrics['data_quality_score'] < 0.5:
                logger.warning(f"Poor data quality detected (score: {quality_metrics['data_quality_score']:.3f})")
        
        # Preprocessing
        original_data = data.copy()
        preprocessing_log = {}
        
        if preprocess:
            try:
                data, preprocessing_log = self.data_processor.preprocess_biomedical_data(
                    data, 
                    handle_missing=kwargs.get('handle_missing', 'interpolate'),
                    remove_outliers=kwargs.get('remove_outliers', True),
                    detrend=kwargs.get('detrend', False),
                    filter_artifacts=kwargs.get('filter_artifacts', True)
                )
            except Exception as e:
                logger.warning(f"Preprocessing failed: {e}")
                data = original_data
        
        # Check if group estimation
        if method in self.groups:
            return self._estimate_group(
                data, method, confidence_method, confidence_level, 
                quality_metrics, preprocessing_log, **kwargs
            )
        else:
            return self._estimate_single(
                data, method, confidence_method, confidence_level,
                quality_metrics, preprocessing_log, **kwargs
            )
    
    def _estimate_single(self, 
                        data: np.ndarray,
                        method: EstimatorType,
                        confidence_method: ConfidenceMethod,
                        confidence_level: float,
                        quality_metrics: Dict[str, Any],
                        preprocessing_log: Dict[str, Any],
                        **kwargs) -> HurstResult:
        """Estimate using single method"""
        
        if method not in self.estimators:
            raise ValueError(f"Method {method} not implemented")
        
        estimator = self.estimators[method]
        
        try:
            start_time = time.time()
            hurst_estimate, method_metrics = estimator.estimate(data, **kwargs)
            computation_time = time.time() - start_time
            
            # Confidence interval estimation
            confidence_interval = (np.nan, np.nan)
            standard_error = np.nan
            bootstrap_samples = None
            
            if confidence_method == ConfidenceMethod.BOOTSTRAP:
                try:
                    bootstrap_mean, ci, bootstrap_samples = self.confidence_estimator.bootstrap_confidence(
                        estimator, data, 
                        n_bootstrap=kwargs.get('n_bootstrap', 100),
                        confidence_level=confidence_level,
                        random_state=kwargs.get('random_state', None)
                    )
                    confidence_interval = ci
                    standard_error = np.std(bootstrap_samples) if len(bootstrap_samples) > 0 else np.nan
                    
                    if not np.isnan(bootstrap_mean) and len(bootstrap_samples) > 50:
                        hurst_estimate = bootstrap_mean
                        
                except Exception as e:
                    logger.warning(f"Bootstrap confidence estimation failed: {e}")
            
            elif confidence_method == ConfidenceMethod.THEORETICAL:
                if 'regression_std_error' in method_metrics:
                    standard_error = method_metrics['regression_std_error']
                    confidence_interval = self.confidence_estimator.theoretical_confidence(
                        hurst_estimate, standard_error, len(data), confidence_level
                    )
            
            elif confidence_method == ConfidenceMethod.BAYESIAN:
                try:
                    # Use Bayesian inference for uncertainty quantification only
                    # Keep the original estimator's point estimate
                    bayesian_mean, credible_interval, bayesian_results = BayesianHurstEstimator.bayesian_confidence(
                        estimator, data,
                        estimator_type=method,
                        num_samples=kwargs.get('num_samples', 1000),
                        num_warmup=kwargs.get('num_warmup', 500),
                        random_seed=kwargs.get('random_state', 42)
                    )
                    
                    # Use Bayesian results for confidence intervals and diagnostics only
                    # Keep the original estimator's hurst_estimate
                    if not np.isnan(bayesian_mean):
                        # Only update confidence interval and standard error from Bayesian inference
                        confidence_interval = credible_interval
                        standard_error = bayesian_results.get('hurst_std', np.nan)
                        
                        # Add Bayesian-specific metrics
                        method_metrics.update({
                            'bayesian_rhat': bayesian_results.get('rhat', np.nan),
                            'bayesian_convergence': bayesian_results.get('convergence_flag', False),
                            'bayesian_samples': bayesian_results.get('samples', {}),
                            'bayesian_method': 'numpyro_mcmc'
                        })
                        
                        logger.info(f"Bayesian inference completed: H={hurst_estimate:.3f}, R-hat={bayesian_results.get('rhat', np.nan):.3f}")
                        
                except Exception as e:
                    logger.warning(f"Bayesian confidence estimation failed: {e}")
                    # Fall back to point estimate without confidence interval
            
            # Create result
            result = HurstResult(
                hurst_estimate=float(hurst_estimate),
                estimator_name=estimator.name,
                confidence_interval=confidence_interval,
                confidence_level=confidence_level,
                confidence_method=confidence_method.value,
                standard_error=float(standard_error),
                bias_estimate=None,
                variance_estimate=float(standard_error**2) if not np.isnan(standard_error) else np.nan,
                bootstrap_samples=bootstrap_samples,
                computation_time=computation_time,
                memory_usage=None,
                convergence_flag=method_metrics.get('convergence_flag', True),
                data_quality_score=quality_metrics.get('data_quality_score', 1.0),
                missing_data_fraction=quality_metrics.get('missing_data_fraction', 0.0),
                outlier_fraction=quality_metrics.get('outlier_fraction', 0.0),
                stationarity_p_value=quality_metrics.get('stationarity_p_value'),
                regression_r_squared=method_metrics.get('regression_r_squared'),
                scaling_range=method_metrics.get('scaling_range'),
                goodness_of_fit=method_metrics.get('regression_r_squared'),
                signal_to_noise_ratio=quality_metrics.get('signal_to_noise_ratio'),
                artifact_detection=quality_metrics.get('artifact_detection', {}),
                additional_metrics=method_metrics
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Estimation failed for method {method}: {e}")
            return HurstResult(
                hurst_estimate=np.nan,
                estimator_name=estimator.name,
                confidence_interval=(np.nan, np.nan),
                confidence_level=confidence_level,
                confidence_method=confidence_method.value,
                standard_error=np.nan,
                bias_estimate=None,
                variance_estimate=np.nan,
                bootstrap_samples=None,
                computation_time=0.0,
                memory_usage=None,
                convergence_flag=False,
                data_quality_score=quality_metrics.get('data_quality_score', 0.0),
                missing_data_fraction=quality_metrics.get('missing_data_fraction', 0.0),
                outlier_fraction=quality_metrics.get('outlier_fraction', 0.0),
                stationarity_p_value=quality_metrics.get('stationarity_p_value'),
                regression_r_squared=None,
                scaling_range=None,
                goodness_of_fit=None,
                signal_to_noise_ratio=quality_metrics.get('signal_to_noise_ratio'),
                artifact_detection=quality_metrics.get('artifact_detection', {})
            )
    
    def _estimate_group(self,
                       data: np.ndarray,
                       group: EstimatorType,
                       confidence_method: ConfidenceMethod,
                       confidence_level: float,
                       quality_metrics: Dict[str, Any],
                       preprocessing_log: Dict[str, Any],
                       **kwargs) -> GroupHurstResult:
        """Estimate using group of methods"""
        
        methods = self.groups[group]
        individual_results = []
        total_start_time = time.time()
        
        for method in methods:
            try:
                result = self._estimate_single(
                    data, method, confidence_method, confidence_level,
                    quality_metrics, preprocessing_log, **kwargs
                )
                individual_results.append(result)
            except Exception as e:
                logger.warning(f"Method {method} failed in group estimation: {e}")
                continue
        
        total_computation_time = time.time() - total_start_time
        
        if not individual_results:
            raise ValueError("All methods in group failed")
        
        valid_results = [r for r in individual_results if not np.isnan(r.hurst_estimate)]
        
        if not valid_results:
            raise ValueError("No valid estimates from group methods")
        
        estimates = np.array([r.hurst_estimate for r in valid_results])
        
        # Ensemble estimation
        ensemble_estimate = np.mean(estimates)
        
        # Weighted estimation
        weights = []
        for result in valid_results:
            weight = 1.0
            if result.regression_r_squared is not None:
                weight *= result.regression_r_squared
            if not result.convergence_flag:
                weight *= 0.5
            weight *= result.data_quality_score
            weights.append(weight)
        
        weights = np.array(weights)
        weights = weights / np.sum(weights) if np.sum(weights) > 0 else np.ones_like(weights) / len(weights)
        weighted_estimate = np.sum(estimates * weights)
        
        # Method agreement
        method_agreement = 1.0 / (1.0 + np.std(estimates) / np.mean(estimates)) if np.mean(estimates) > 0 else 0.0
        
        # Best method
        best_method_idx = 0
        best_score = -1
        for i, result in enumerate(valid_results):
            score = 0
            if result.regression_r_squared is not None:
                score += result.regression_r_squared
            if result.convergence_flag:
                score += 0.5
            score += result.data_quality_score * 0.3
            
            if score > best_score:
                best_score = score
                best_method_idx = i
        
        best_method = valid_results[best_method_idx].estimator_name
        consensus_estimate = np.median(estimates)
        
        # Ensemble confidence interval
        all_cis = [r.confidence_interval for r in valid_results if not np.isnan(r.confidence_interval[0])]
        if all_cis:
            ensemble_ci_lower = np.mean([ci[0] for ci in all_cis])
            ensemble_ci_upper = np.mean([ci[1] for ci in all_cis])
            ensemble_confidence_interval = (ensemble_ci_lower, ensemble_ci_upper)
        else:
            ensemble_confidence_interval = (np.nan, np.nan)
        
        return GroupHurstResult(
            individual_results=individual_results,
            ensemble_estimate=float(ensemble_estimate),
            ensemble_confidence_interval=ensemble_confidence_interval,
            method_agreement=float(method_agreement),
            best_method=best_method,
            consensus_estimate=float(consensus_estimate),
            weighted_estimate=float(weighted_estimate),
            total_computation_time=total_computation_time
        )

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def estimate_hurst(data: Union[np.ndarray, List[float]], 
                  method: str = "dfa",
                  **kwargs) -> HurstResult:
    """Convenience function for quick Hurst estimation"""
    factory = BiomedicalHurstEstimatorFactory()
    return factory.estimate(data, method, **kwargs)

def compare_methods(data: Union[np.ndarray, List[float]], 
                   methods: List[str] = None,
                   **kwargs) -> GroupHurstResult:
    """Convenience function for method comparison"""
    if methods is None:
        methods = ["all"]
    
    factory = BiomedicalHurstEstimatorFactory()
    return factory.estimate(data, methods[0] if len(methods) == 1 else "all", **kwargs)

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example usage
    np.random.seed(42)
    
    # Generate test biomedical data
    n = 1000
    test_data = np.cumsum(np.random.randn(n) * 0.1)  # Random walk
    test_data += 0.1 * np.sin(2 * np.pi * np.arange(n) / 50)  # Periodic component
    test_data += 0.05 * np.random.randn(n)  # Noise
    
    # Add some missing values
    missing_indices = np.random.choice(n, size=20, replace=False)
    test_data[missing_indices] = np.nan
    
    print("Biomedical Hurst Estimator Factory Demo")
    print("=" * 50)
    
    # Single method estimation
    print("\n1. Single Method Estimation (DFA):")
    result = estimate_hurst(test_data, method="dfa")
    print(result)
    
    # Group estimation
    print("\n2. Group Estimation (All Methods):")
    group_result = compare_methods(test_data)
    print(group_result)
    
    print("\nDemo completed successfully!")