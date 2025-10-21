"""
Synthetic data generation for Hurst exponent estimation benchmarking.

This module provides functions to generate various types of synthetic time series
with known Hurst exponents for testing and validation purposes.
"""

import numpy as np
import math
import logging
from typing import List, Optional, Tuple, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TimeSeriesSample:
    """Container for a generated time series sample."""
    data: np.ndarray
    true_hurst: Optional[float]
    length: int
    contamination: str
    seed: Optional[int] = None


def fbm_davies_harte(n: int, hurst: float, seed: Optional[int] = None) -> np.ndarray:
    """
    Generate fractional Brownian motion using the Davies-Harte method.
    
    This implementation uses the fbm library which provides a fast and accurate
    implementation of the Davies-Harte method for generating fBm samples.
    
    Parameters:
    -----------
    n : int
        Length of the time series
    hurst : float
        Hurst exponent (0 < H < 1)
    seed : int, optional
        Random seed for reproducibility
        
    Returns:
    --------
    np.ndarray
        Fractional Brownian motion time series
    """
    if not (0 < hurst < 1):
        raise ValueError(f"Hurst exponent must be in (0, 1), got {hurst}")
    
    try:
        from fbm import FBM
        
        # Create FBM object
        fbm_obj = FBM(n=n, hurst=hurst, length=1, method='daviesharte')
        
        # Generate the fBm sample
        if seed is not None:
            # Set random seed if provided
            np.random.seed(seed)
        
        fbm_sample = fbm_obj.fbm()
        
        # Ensure we return exactly n points (fbm library sometimes returns n+1)
        if len(fbm_sample) > n:
            fbm_sample = fbm_sample[:n]
        elif len(fbm_sample) < n:
            # Pad with zeros if needed (shouldn't happen)
            fbm_sample = np.pad(fbm_sample, (0, n - len(fbm_sample)), mode='constant')
        
        return fbm_sample
        
    except ImportError:
        # Fallback to simplified implementation if fbm library not available
        logger.warning("fbm library not available, using simplified fBm approximation")
        
        if seed is not None:
            np.random.seed(seed)
        
        # Simple spectral approximation as fallback
        white_noise = np.random.randn(n)
        freqs = np.fft.fftfreq(n)
        freqs[0] = 1e-10  # Avoid division by zero
        
        # Power spectrum scales as 1/f^(2H+1) for fBm
        filter_coeffs = 1.0 / (np.abs(freqs)**(hurst + 0.5))
        filter_coeffs[0] = 0  # DC component
        
        fft_noise = np.fft.fft(white_noise)
        filtered_fft = fft_noise * filter_coeffs
        fbm_approx = np.real(np.fft.ifft(filtered_fft))
        
        # Integrate to get fBm
        fbm_approx = np.cumsum(fbm_approx - np.mean(fbm_approx))
        
        return fbm_approx


def generate_fgn(n: int, hurst: float, seed: Optional[int] = None) -> np.ndarray:
    """
    Generate fractional Gaussian noise.
    
    Parameters:
    -----------
    n : int
        Length of the time series
    hurst : float
        Hurst exponent (0 < H < 1)
    seed : int, optional
        Random seed for reproducibility
        
    Returns:
    --------
    np.ndarray
        Fractional Gaussian noise time series
    """
    fbm = fbm_davies_harte(n + 1, hurst, seed)
    return np.diff(fbm)


def generate_arfima(n: int, hurst: float, ar_coeffs: Optional[List[float]] = None, 
                   ma_coeffs: Optional[List[float]] = None, seed: Optional[int] = None) -> np.ndarray:
    """
    Generate ARFIMA (AutoRegressive Fractionally Integrated Moving Average) time series.
    
    Parameters:
    -----------
    n : int
        Length of the time series
    hurst : float
        Hurst exponent (0 < H < 1), related to fractional differencing parameter d = H - 0.5
    ar_coeffs : List[float], optional
        AR coefficients (default: [0.3, -0.1] for AR(2))
    ma_coeffs : List[float], optional
        MA coefficients (default: [0.2] for MA(1))
    seed : int, optional
        Random seed for reproducibility
        
    Returns:
    --------
    np.ndarray
        ARFIMA time series
    """
    if seed is not None:
        np.random.seed(seed)
    
    if not (0 < hurst < 1):
        raise ValueError(f"Hurst exponent must be in (0, 1), got {hurst}")
    
    # Default AR and MA coefficients
    if ar_coeffs is None:
        ar_coeffs = [0.3, -0.1]  # AR(2)
    if ma_coeffs is None:
        ma_coeffs = [0.2]  # MA(1)
    
    # Fractional differencing parameter
    d = hurst - 0.5
    
    # Generate white noise
    white_noise = np.random.randn(n + 100)  # Extra points for initialization
    
    # Apply fractional differencing
    frac_diff_series = np.zeros_like(white_noise)
    frac_diff_series[0] = white_noise[0]
    
    # Fractional differencing: (1-L)^d where L is lag operator
    for t in range(1, len(white_noise)):
        frac_diff_series[t] = white_noise[t]
        for k in range(1, min(t + 1, 50)):  # Truncate infinite series
            coeff = (-1)**k * np.prod([d - j for j in range(k)]) / math.factorial(k)
            if t - k >= 0:
                frac_diff_series[t] += coeff * frac_diff_series[t - k]
    
    # Apply AR and MA components
    ar_order = len(ar_coeffs)
    ma_order = len(ma_coeffs)
    
    # Initialize with zeros
    arfima_series = np.zeros(len(frac_diff_series))
    
    # ARMA process
    for t in range(max(ar_order, ma_order), len(frac_diff_series)):
        # AR component
        ar_component = 0
        for i, coeff in enumerate(ar_coeffs):
            ar_component += coeff * arfima_series[t - i - 1]
        
        # MA component
        ma_component = 0
        for i, coeff in enumerate(ma_coeffs):
            if t - i - 1 >= 0:
                ma_component += coeff * frac_diff_series[t - i - 1]
        
        arfima_series[t] = ar_component + frac_diff_series[t] + ma_component
    
    # Return the last n points and normalize
    result = arfima_series[-n:]
    result = result - np.mean(result)
    result = result / np.std(result) * np.sqrt(n)
    
    return result


def generate_mrw(n: int, hurst: float, lambda_param: float = 0.12, 
                sigma: float = 1.0, seed: Optional[int] = None) -> np.ndarray:
    """
    Generate Multifractal Random Walk (MRW) time series.
    
    Parameters:
    -----------
    n : int
        Length of the time series
    hurst : float
        Hurst exponent (0 < H < 1)
    lambda_param : float, optional
        Intermittency parameter (default: 0.12)
    sigma : float, optional
        Volatility parameter (default: 1.0)
    seed : int, optional
        Random seed for reproducibility
        
    Returns:
    --------
    np.ndarray
        MRW time series
    """
    if seed is not None:
        np.random.seed(seed)
    
    if not (0 < hurst < 1):
        raise ValueError(f"Hurst exponent must be in (0, 1), got {hurst}")
    
    # Generate log-normal multifractal process
    # MRW: X(t) = ∫_0^t exp(ω(s)) dW(s)
    # where ω(s) is a Gaussian process with long-range correlations
    
    # Time grid
    dt = 1.0 / n
    t = np.arange(n) * dt
    
    # Generate correlated Gaussian process ω(s)
    # Covariance: C(s,t) = λ² log(T/|t-s|) for |t-s| < T
    T = n * dt  # Total time
    
    # Generate covariance matrix
    cov_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            time_diff = abs(t[i] - t[j])
            if time_diff < T and time_diff > 0:
                cov_matrix[i, j] = lambda_param**2 * np.log(T / time_diff)
            elif time_diff == 0:
                cov_matrix[i, j] = lambda_param**2 * np.log(T / dt)  # Diagonal
    
    # Generate multivariate Gaussian with this covariance
    try:
        L = np.linalg.cholesky(cov_matrix)
        z = np.random.randn(n)
        omega = L @ z
    except np.linalg.LinAlgError:
        # Fallback to eigenvalue decomposition
        eigenvals, eigenvecs = np.linalg.eigh(cov_matrix)
        eigenvals = np.maximum(eigenvals, 1e-12)  # Ensure positive
        sqrt_eigenvals = np.sqrt(eigenvals)
        z = np.random.randn(n)
        omega = eigenvecs @ (sqrt_eigenvals * z)
    
    # Generate MRW increments
    # dX(t) = exp(ω(t)) * dW(t) where dW(t) ~ N(0, dt)
    dW = np.sqrt(dt) * np.random.randn(n)
    dX = np.exp(omega) * dW * sigma
    
    # Integrate to get MRW process
    mrw_series = np.cumsum(dX)
    
    # Normalize to have reasonable scale
    mrw_series = mrw_series - np.mean(mrw_series)
    mrw_series = mrw_series / np.std(mrw_series) * np.sqrt(n)
    
    return mrw_series


def generate_fou(n: int, hurst: float, theta: float = 1.0, 
                sigma: float = 1.0, seed: Optional[int] = None) -> np.ndarray:
    """
    Generate Fractional Ornstein-Uhlenbeck (fOU) process.
    
    Parameters:
    -----------
    n : int
        Length of the matrix
    hurst : float
        Hurst exponent (0 < H < 1)
    theta : float, optional
        Mean reversion parameter (default: 1.0)
    sigma : float, optional
        Volatility parameter (default: 1.0)
    seed : int, optional
        Random seed for reproducibility
        
    Returns:
    --------
    np.ndarray
        fOU process
    """
    if seed is not None:
        np.random.seed(seed)
    
    if not (0 < hurst < 1):
        raise ValueError(f"Hurst exponent must be in (0, 1), got {hurst}")
    
    # fOU process: dX(t) = -θX(t)dt + σdB_H(t)
    # where B_H(t) is fractional Brownian motion
    
    # Time grid
    dt = 1.0 / n
    t = np.arange(n) * dt
    
    # Generate fractional Brownian motion increments
    fbm = fbm_davies_harte(n, hurst, seed)
    dB_H = np.diff(fbm)
    
    # Initialize fOU process
    fou_series = np.zeros(n)
    fou_series[0] = 0  # Initial condition
    
    # Euler-Maruyama discretization
    for i in range(1, n):
        # dX = -θX*dt + σ*dB_H
        fou_series[i] = fou_series[i-1] - theta * fou_series[i-1] * dt + sigma * dB_H[i-1]
    
    # Normalize
    fou_series = fou_series - np.mean(fou_series)
    fou_series = fou_series / np.std(fou_series) * np.sqrt(n)
    
    return fou_series


def add_contamination(data: np.ndarray, contamination_type: str, 
                     contamination_level: float = 0.1, 
                     seed: Optional[int] = None) -> np.ndarray:
    """
    Add contamination to time series data.
    
    Parameters:
    -----------
    data : np.ndarray
        Original time series
    contamination_type : str
        Type of contamination ('none', 'noise', 'missing', 'outliers', 'trend', 
                              'baseline_drift', 'electrode_pop', 'motion', 'powerline',
                              'heavy_tail', 'neural_avalanche', 'parkinsonian_tremor', 
                              'epileptic_spike', 'burst_suppression')
    contamination_level : float
        Level of contamination (0-1)
    seed : int, optional
        Random seed for reproducibility
        
    Returns:
    --------
    np.ndarray
        Contaminated time series
    """
    if seed is not None:
        np.random.seed(seed)
    
    contaminated = data.copy()
    n = len(data)
    
    if contamination_type == 'none':
        return contaminated
    
    elif contamination_type == 'noise':
        # Add Gaussian noise
        noise_level = contamination_level * np.std(data)
        noise = np.random.randn(n) * noise_level
        contaminated += noise
    
    elif contamination_type == 'missing':
        # Add missing values
        n_missing = int(contamination_level * n)
        missing_indices = np.random.choice(n, size=n_missing, replace=False)
        contaminated[missing_indices] = np.nan
    
    elif contamination_type == 'outliers':
        # Add outliers
        n_outliers = int(contamination_level * n)
        outlier_indices = np.random.choice(n, size=n_outliers, replace=False)
        outlier_values = np.random.randn(n_outliers) * 5 * np.std(data)
        contaminated[outlier_indices] = outlier_values
    
    elif contamination_type == 'trend':
        # Add linear trend
        trend_slope = contamination_level * np.std(data) / n
        trend = np.linspace(0, trend_slope * n, n)
        contaminated += trend
    
    elif contamination_type == 'baseline_drift':
        # Add slow baseline drift (common in biomedical signals)
        t = np.arange(n)
        drift_freq = 0.1  # Very low frequency drift
        drift_amplitude = contamination_level * np.std(data)
        drift = drift_amplitude * np.sin(2 * np.pi * drift_freq * t / 250.0)
        contaminated += drift
    
    elif contamination_type == 'electrode_pop':
        # Add electrode pop artifacts (sudden jumps)
        n_pops = int(contamination_level * 5)  # Few electrode pops
        for _ in range(n_pops):
            pop_idx = np.random.randint(0, n)
            pop_amplitude = np.random.choice([-1, 1]) * contamination_level * 10 * np.std(data)
            contaminated[pop_idx:] += pop_amplitude  # Persistent offset
    
    elif contamination_type == 'motion':
        # Add motion artifacts (common in wearable devices)
        n_motion_events = int(contamination_level * 10)
        for _ in range(n_motion_events):
            start_idx = np.random.randint(0, n - 100)
            duration = np.random.randint(20, 200)
            end_idx = min(n, start_idx + duration)
            
            # Motion artifact (sudden change in amplitude)
            motion_amplitude = np.random.choice([-1, 1]) * contamination_level * 3 * np.std(data)
            motion_artifact = motion_amplitude * np.ones(end_idx - start_idx)
            contaminated[start_idx:end_idx] += motion_artifact
    
    elif contamination_type == 'powerline':
        # Add powerline interference (50/60 Hz)
        t = np.arange(n)
        powerline_freq = 50.0  # Hz (or 60 Hz in some regions)
        powerline_amplitude = contamination_level * 0.5 * np.std(data)
        powerline_noise = powerline_amplitude * np.sin(2 * np.pi * powerline_freq * t / 250.0)
        contaminated += powerline_noise
    
    elif contamination_type == 'heavy_tail':
        # Add heavy-tail amplitude variations (relevant for Parkinson's, epilepsy)
        n_heavy_events = int(contamination_level * 20)  # Number of heavy-tail events
        for _ in range(n_heavy_events):
            start_idx = np.random.randint(0, n - 50)
            duration = np.random.randint(10, 100)
            end_idx = min(n, start_idx + duration)
            
            # Generate heavy-tail amplitude using power-law distribution
            # Heavy-tail: P(x) ~ x^(-α) where α is the tail exponent
            alpha = 1.5  # Typical value for neural avalanches
            heavy_amplitude = np.random.power(alpha, end_idx - start_idx) * contamination_level * 5 * np.std(data)
            heavy_amplitude *= np.random.choice([-1, 1])  # Random sign
            
            contaminated[start_idx:end_idx] += heavy_amplitude
    
    elif contamination_type == 'neural_avalanche':
        # Add neural avalanche patterns (characteristic of Parkinson's, epilepsy)
        n_avalanches = int(contamination_level * 5)  # Few but significant avalanches
        for _ in range(n_avalanches):
            # Avalanche start time
            start_idx = np.random.randint(0, n - 200)
            
            # Avalanche duration (exponentially distributed)
            duration = int(np.random.exponential(50))  # Mean duration of 50 samples
            end_idx = min(n, start_idx + duration)
            
            # Generate avalanche pattern with critical dynamics
            # Neural avalanches follow power-law size distribution
            avalanche_size = np.random.power(2.0) * contamination_level * 10 * np.std(data)
            
            # Create avalanche waveform (sudden onset, exponential decay)
            t_avalanche = np.arange(end_idx - start_idx)
            avalanche_pattern = avalanche_size * np.exp(-t_avalanche / (duration / 3))
            
            # Add some randomness to the pattern
            noise_component = np.random.randn(end_idx - start_idx) * 0.1 * avalanche_size
            avalanche_pattern += noise_component
            
            contaminated[start_idx:end_idx] += avalanche_pattern
    
    elif contamination_type == 'parkinsonian_tremor':
        # Add Parkinsonian tremor patterns (4-6 Hz oscillations with amplitude modulation)
        tremor_freq = 5.0  # Hz (typical Parkinsonian tremor frequency)
        tremor_amplitude = contamination_level * 3 * np.std(data)
        
        t = np.arange(n) / 250.0  # Time in seconds
        
        # Base tremor oscillation
        tremor_signal = tremor_amplitude * np.sin(2 * np.pi * tremor_freq * t)
        
        # Amplitude modulation (tremor severity varies over time)
        modulation_freq = 0.1  # Slow modulation
        modulation = 0.5 + 0.5 * np.sin(2 * np.pi * modulation_freq * t)
        tremor_signal *= modulation
        
        # Add some phase jitter (tremor is not perfectly periodic)
        phase_jitter = 0.2 * np.random.randn(n)
        tremor_signal *= np.cos(phase_jitter)
        
        contaminated += tremor_signal
    
    elif contamination_type == 'epileptic_spike':
        # Add epileptic spike patterns (sudden high-amplitude events)
        n_spikes = int(contamination_level * 10)
        for _ in range(n_spikes):
            spike_idx = np.random.randint(0, n - 20)
            spike_duration = np.random.randint(5, 20)
            end_idx = min(n, spike_idx + spike_duration)
            
            # Generate spike waveform (sharp onset, exponential decay)
            t_spike = np.arange(end_idx - spike_idx)
            spike_amplitude = contamination_level * 8 * np.std(data)
            
            # Sharp spike with exponential decay
            spike_pattern = spike_amplitude * np.exp(-t_spike / 3) * np.random.choice([-1, 1])
            
            contaminated[spike_idx:end_idx] += spike_pattern
    
    elif contamination_type == 'burst_suppression':
        # Add burst-suppression pattern (common in anesthesia, coma, some neurological conditions)
        # Alternating periods of high activity (bursts) and low activity (suppression)
        burst_duration = int(contamination_level * 100)  # Duration of each phase
        suppression_duration = int(contamination_level * 150)
        
        i = 0
        while i < n:
            # Burst phase
            burst_end = min(n, i + burst_duration)
            burst_amplitude = contamination_level * 4 * np.std(data)
            contaminated[i:burst_end] += burst_amplitude * np.random.randn(burst_end - i)
            
            i = burst_end
            
            # Suppression phase
            supp_end = min(n, i + suppression_duration)
            supp_amplitude = contamination_level * 0.2 * np.std(data)
            contaminated[i:supp_end] += supp_amplitude * np.random.randn(supp_end - i)
            
            i = supp_end
    
    else:
        # Default to noise if unknown contamination type
        noise_level = contamination_level * np.std(data)
        noise = np.random.randn(n) * noise_level
        contaminated += noise
    
    return contaminated


def generate_grid(hurst_values: List[float], 
                 lengths: List[int], 
                 contaminations: List[str],
                 contamination_level: float = 0.1,
                 generators: List[str] = None,
                 biomedical_scenarios: List[str] = None,
                 seed: Optional[int] = None) -> List[TimeSeriesSample]:
    """
    Generate a grid of time series samples for benchmarking.
    
    Parameters:
    -----------
    hurst_values : List[float]
        List of Hurst exponents to generate
    lengths : List[int]
        List of time series lengths to generate
    contaminations : List[str]
        List of contamination types to apply
    contamination_level : float
        Level of contamination to apply
    generators : List[str], optional
        List of generator types to use ('fbm', 'fgn', 'arfima', 'mrw', 'fou')
        Default: ['fbm']
    biomedical_scenarios : List[str], optional
        List of biomedical scenarios to generate ('eeg_rest', 'ecg_normal', etc.)
    seed : int, optional
        Random seed for reproducibility
        
    Returns:
    --------
    List[TimeSeriesSample]
        List of generated time series samples
    """
    if generators is None:
        generators = ['fbm']
    
    # Available generators
    generator_functions = {
        'fbm': fbm_davies_harte,
        'fgn': generate_fgn,
        'arfima': generate_arfima,
        'mrw': generate_mrw,
        'fou': generate_fou
    }
    
    samples = []
    sample_id = 0
    
    # Generate biomedical scenarios if specified
    if biomedical_scenarios:
        try:
            from .biomedical_scenarios import generate_biomedical_scenario, BIOMEDICAL_SCENARIOS
            
            for hurst in hurst_values:
                for length in lengths:
                    for contamination in contaminations:
                        for scenario in biomedical_scenarios:
                            current_seed = seed + sample_id if seed is not None else sample_id
                            
                            if scenario in BIOMEDICAL_SCENARIOS:
                                scenario_config = BIOMEDICAL_SCENARIOS[scenario]
                                data = generate_biomedical_scenario(
                                    scenario_config['scenario_type'],
                                    length, hurst, contamination_level,
                                    **{k: v for k, v in scenario_config.items() 
                                       if k not in ['scenario_type', 'hurst_range', 'typical_amplitude', 'noise_level', 'auto_contamination']}
                                )
                                
                                # Apply additional contamination if specified
                                if contamination != 'none':
                                    data = add_contamination(data, contamination, contamination_level, current_seed)
                                
                                samples.append(TimeSeriesSample(
                                    data=data,
                                    true_hurst=hurst,
                                    length=length,
                                    contamination=f"{scenario}_{contamination}",
                                    seed=current_seed
                                ))
                                sample_id += 1
        except ImportError:
            print("Warning: Biomedical scenarios module not available, skipping biomedical data generation")
    
    # Generate standard synthetic data
    for hurst in hurst_values:
        for length in lengths:
            for contamination in contaminations:
                for generator_type in generators:
                    # Generate base time series
                    current_seed = seed + sample_id if seed is not None else sample_id
                    
                    if generator_type in generator_functions:
                        data = generator_functions[generator_type](length, hurst, seed=current_seed)
                    else:
                        # Fallback to fBm
                        data = fbm_davies_harte(length, hurst, seed=current_seed)
                    
                    # Apply contamination if specified
                    if contamination != 'none':
                        data = add_contamination(data, contamination, contamination_level, current_seed)
                    
                    samples.append(TimeSeriesSample(
                        data=data,
                        true_hurst=hurst,
                        length=length,
                        contamination=contamination,
                        seed=current_seed
                    ))
                    sample_id += 1
    
    return samples



