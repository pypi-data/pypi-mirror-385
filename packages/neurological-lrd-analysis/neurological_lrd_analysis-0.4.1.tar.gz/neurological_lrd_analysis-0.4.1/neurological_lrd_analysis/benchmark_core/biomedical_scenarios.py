"""
Biomedical scenario-based time series data generation.

This module provides realistic biomedical time series generators (EEG, ECG, etc.)
with appropriate contamination methods relevant to real biomedical data.
"""

import numpy as np
import math
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass

from .generation import TimeSeriesSample, fbm_davies_harte, generate_fgn


@dataclass
class BiomedicalScenario:
    """Configuration for biomedical time series scenarios."""
    scenario_type: str  # 'eeg', 'ecg', 'emg', 'respiratory', 'blood_pressure'
    sampling_rate: float  # Hz
    duration: float  # seconds
    hurst_range: Tuple[float, float]  # Expected Hurst range for this scenario
    typical_amplitude: float  # Typical signal amplitude
    noise_level: float  # Typical noise level (relative to signal)
    artifact_probability: float  # Probability of artifacts


def generate_eeg_scenario(n: int, hurst: float, scenario: str = 'rest', 
                         contamination_level: float = 0.1, 
                         seed: Optional[int] = None) -> np.ndarray:
    """
    Generate realistic EEG time series data.
    
    Parameters:
    -----------
    n : int
        Length of the time series
    hurst : float
        Hurst exponent (0 < H < 1)
    scenario : str
        EEG scenario ('rest', 'eyes_closed', 'eyes_open', 'sleep', 'seizure')
    contamination_level : float
        Level of contamination/artifacts
    seed : int, optional
        Random seed for reproducibility
        
    Returns:
    --------
    np.ndarray
        EEG-like time series data
    """
    if seed is not None:
        np.random.seed(seed)
    
    if not (0 < hurst < 1):
        raise ValueError(f"Hurst exponent must be in (0, 1), got {hurst}")
    
    # Generate base fBm signal
    base_signal = fbm_davies_harte(n, hurst, seed)
    
    # Add EEG-specific characteristics based on scenario
    if scenario == 'rest':
        # Resting state: alpha waves (8-12 Hz) with some theta
        alpha_freq = 10.0  # Hz
        theta_freq = 6.0   # Hz
        
    elif scenario == 'eyes_closed':
        # Eyes closed: stronger alpha waves
        alpha_freq = 9.5   # Hz
        theta_freq = 5.0   # Hz
        
    elif scenario == 'eyes_open':
        # Eyes open: reduced alpha, more beta
        alpha_freq = 8.0   # Hz
        theta_freq = 6.0   # Hz
        
    elif scenario == 'sleep':
        # Sleep: delta waves (0.5-4 Hz) and theta
        alpha_freq = 2.0   # Hz
        theta_freq = 1.5   # Hz
        
    elif scenario == 'seizure':
        # Seizure: high-frequency activity
        alpha_freq = 20.0  # Hz
        theta_freq = 15.0  # Hz
        
    elif scenario == 'parkinsonian':
        # Parkinson's disease: reduced alpha, increased beta (13-30 Hz), tremor
        alpha_freq = 6.0   # Reduced alpha
        theta_freq = 18.0  # Beta activity
        
    elif scenario == 'epileptic':
        # Epilepsy: irregular patterns, spikes, high-frequency bursts
        alpha_freq = 15.0  # Irregular
        theta_freq = 25.0  # High-frequency bursts
        
    else:
        raise ValueError(f"Unknown EEG scenario: {scenario}")
    
    # Generate time vector (assuming 250 Hz sampling rate)
    fs = 250.0
    t = np.arange(n) / fs
    
    # Add rhythmic components (simulating brain waves)
    alpha_component = 0.3 * np.sin(2 * np.pi * alpha_freq * t)
    theta_component = 0.2 * np.sin(2 * np.pi * theta_freq * t)
    
    # Combine base signal with rhythmic components
    eeg_signal = base_signal + alpha_component + theta_component
    
    # Add EEG-specific artifacts if contamination level > 0
    if contamination_level > 0:
        eeg_signal = add_eeg_artifacts(eeg_signal, contamination_level, seed)
    
    # Normalize to typical EEG amplitude (50-100 μV)
    eeg_signal = eeg_signal * 75.0  # Scale to ~75 μV
    
    return eeg_signal


def generate_ecg_scenario(n: int, hurst: float, heart_rate: float = 70.0,
                         contamination_level: float = 0.1,
                         seed: Optional[int] = None) -> np.ndarray:
    """
    Generate realistic ECG time series data.
    
    Parameters:
    -----------
    n : int
        Length of the time series
    hurst : float
        Hurst exponent (0 < H < 1)
    heart_rate : float
        Heart rate in BPM
    contamination_level : float
        Level of contamination/artifacts
    seed : int, optional
        Random seed for reproducibility
        
    Returns:
    --------
    np.ndarray
        ECG-like time series data
    """
    if seed is not None:
        np.random.seed(seed)
    
    if not (0 < hurst < 1):
        raise ValueError(f"Hurst exponent must be in (0, 1), got {hurst}")
    
    # Generate base fBm signal
    base_signal = fbm_davies_harte(n, hurst, seed)
    
    # Generate time vector (assuming 250 Hz sampling rate)
    fs = 250.0
    t = np.arange(n) / fs
    
    # Generate ECG-like waveform
    ecg_signal = np.zeros(n)
    
    # Calculate RR interval
    rr_interval = 60.0 / heart_rate  # seconds
    
    # Generate QRS complexes
    for i in range(int(t[-1] / rr_interval) + 1):
        # QRS complex timing
        qrs_time = i * rr_interval
        
        if 0 <= qrs_time <= t[-1]:
            # Find closest time index
            qrs_idx = int(qrs_time * fs)
            
            if 0 <= qrs_idx < n:
                # Add QRS complex (simplified)
                qrs_width = int(0.08 * fs)  # 80ms QRS width
                start_idx = max(0, qrs_idx - qrs_width//2)
                end_idx = min(n, qrs_idx + qrs_width//2)
                
                # QRS complex shape (simplified)
                qrs_shape = np.exp(-((np.arange(end_idx - start_idx) - qrs_width//2) / (qrs_width//4))**2)
                ecg_signal[start_idx:end_idx] += 2.0 * qrs_shape
    
    # Add P and T waves (simplified)
    for i in range(int(t[-1] / rr_interval) + 1):
        rr_time = i * rr_interval
        
        if 0 <= rr_time <= t[-1]:
            rr_idx = int(rr_time * fs)
            
            # P wave (before QRS)
            p_time = rr_time - 0.15  # 150ms before QRS
            if p_time >= 0:
                p_idx = int(p_time * fs)
                if 0 <= p_idx < n:
                    p_width = int(0.08 * fs)
                    start_idx = max(0, p_idx - p_width//2)
                    end_idx = min(n, p_idx + p_width//2)
                    p_shape = np.exp(-((np.arange(end_idx - start_idx) - p_width//2) / (p_width//3))**2)
                    ecg_signal[start_idx:end_idx] += 0.3 * p_shape
            
            # T wave (after QRS)
            t_time = rr_time + 0.25  # 250ms after QRS
            if t_time <= t[-1]:
                t_idx = int(t_time * fs)
                if 0 <= t_idx < n:
                    t_width = int(0.12 * fs)
                    start_idx = max(0, t_idx - t_width//2)
                    end_idx = min(n, t_idx + t_width//2)
                    t_shape = np.exp(-((np.arange(end_idx - start_idx) - t_width//2) / (t_width//3))**2)
                    ecg_signal[start_idx:end_idx] += 0.4 * t_shape
    
    # Combine with base signal
    ecg_signal = ecg_signal + 0.1 * base_signal
    
    # Add ECG-specific artifacts if contamination level > 0
    if contamination_level > 0:
        ecg_signal = add_ecg_artifacts(ecg_signal, contamination_level, seed)
    
    # Normalize to typical ECG amplitude (1-5 mV)
    ecg_signal = ecg_signal * 2.0  # Scale to ~2 mV
    
    return ecg_signal


def generate_respiratory_scenario(n: int, hurst: float, breathing_rate: float = 15.0,
                                 contamination_level: float = 0.1,
                                 seed: Optional[int] = None) -> np.ndarray:
    """
    Generate realistic respiratory time series data.
    
    Parameters:
    -----------
    n : int
        Length of the time series
    hurst : float
        Hurst exponent (0 < H < 1)
    breathing_rate : float
        Breathing rate in breaths per minute
    contamination_level : float
        Level of contamination/artifacts
    seed : int, optional
        Random seed for reproducibility
        
    Returns:
    --------
    np.ndarray
        Respiratory-like time series data
    """
    if seed is not None:
        np.random.seed(seed)
    
    if not (0 < hurst < 1):
        raise ValueError(f"Hurst exponent must be in (0, 1), got {hurst}")
    
    # Generate base fBm signal
    base_signal = fbm_davies_harte(n, hurst, seed)
    
    # Generate time vector (assuming 10 Hz sampling rate for respiratory)
    fs = 10.0
    t = np.arange(n) / fs
    
    # Generate breathing pattern
    breathing_period = 60.0 / breathing_rate  # seconds per breath
    breathing_signal = np.sin(2 * np.pi * t / breathing_period)
    
    # Add some irregularity to breathing
    irregularity = 0.1 * np.sin(2 * np.pi * 0.1 * t)  # Slow variation in breathing rate
    breathing_signal = np.sin(2 * np.pi * t / breathing_period + irregularity)
    
    # Combine with base signal
    respiratory_signal = breathing_signal + 0.2 * base_signal
    
    # Add respiratory-specific artifacts if contamination level > 0
    if contamination_level > 0:
        respiratory_signal = add_respiratory_artifacts(respiratory_signal, contamination_level, seed)
    
    # Normalize to typical respiratory amplitude
    respiratory_signal = respiratory_signal * 0.5  # Scale to reasonable amplitude
    
    return respiratory_signal


def add_eeg_artifacts(data: np.ndarray, contamination_level: float, 
                     seed: Optional[int] = None) -> np.ndarray:
    """
    Add EEG-specific artifacts to the signal.
    
    Parameters:
    -----------
    data : np.ndarray
        Original EEG signal
    contamination_level : float
        Level of contamination
    seed : int, optional
        Random seed for reproducibility
        
    Returns:
    --------
    np.ndarray
        EEG signal with artifacts
    """
    if seed is not None:
        np.random.seed(seed)
    
    contaminated = data.copy()
    n = len(data)
    
    # Eye movement artifacts (EOG)
    if np.random.random() < contamination_level:
        n_eye_movements = int(contamination_level * 10)  # Few eye movements
        for _ in range(n_eye_movements):
            start_idx = np.random.randint(0, n - 100)
            duration = np.random.randint(50, 200)
            end_idx = min(n, start_idx + duration)
            
            # Eye movement artifact (slow, large amplitude)
            eye_artifact = np.linspace(0, np.random.choice([-1, 1]) * 200, end_idx - start_idx)
            contaminated[start_idx:end_idx] += eye_artifact
    
    # Muscle artifacts (EMG)
    if np.random.random() < contamination_level * 0.5:
        n_muscle_artifacts = int(contamination_level * 20)
        for _ in range(n_muscle_artifacts):
            start_idx = np.random.randint(0, n - 50)
            duration = np.random.randint(10, 100)
            end_idx = min(n, start_idx + duration)
            
            # Muscle artifact (high frequency, random amplitude)
            muscle_artifact = np.random.randn(end_idx - start_idx) * 50
            contaminated[start_idx:end_idx] += muscle_artifact
    
    # Electrode artifacts (sudden jumps)
    if np.random.random() < contamination_level * 0.3:
        n_electrode_artifacts = int(contamination_level * 5)
        for _ in range(n_electrode_artifacts):
            idx = np.random.randint(0, n)
            jump_amplitude = np.random.choice([-1, 1]) * 100
            contaminated[idx:] += jump_amplitude  # Persistent offset
    
    return contaminated


def add_ecg_artifacts(data: np.ndarray, contamination_level: float,
                     seed: Optional[int] = None) -> np.ndarray:
    """
    Add ECG-specific artifacts to the signal.
    
    Parameters:
    -----------
    data : np.ndarray
        Original ECG signal
    contamination_level : float
        Level of contamination
    seed : int, optional
        Random seed for reproducibility
        
    Returns:
    --------
    np.ndarray
        ECG signal with artifacts
    """
    if seed is not None:
        np.random.seed(seed)
    
    contaminated = data.copy()
    n = len(data)
    
    # Baseline wander (slow drift)
    if np.random.random() < contamination_level:
        # Generate slow sinusoidal drift
        t = np.arange(n)
        drift_freq = 0.5  # Very low frequency
        baseline_wander = 0.5 * np.sin(2 * np.pi * drift_freq * t / 250.0)
        contaminated += baseline_wander
    
    # Muscle noise (high frequency)
    if np.random.random() < contamination_level * 0.7:
        # Add high-frequency noise
        muscle_noise = np.random.randn(n) * 0.1
        contaminated += muscle_noise
    
    # Motion artifacts (sudden changes)
    if np.random.random() < contamination_level * 0.4:
        n_motion_artifacts = int(contamination_level * 10)
        for _ in range(n_motion_artifacts):
            start_idx = np.random.randint(0, n - 100)
            duration = np.random.randint(20, 200)
            end_idx = min(n, start_idx + duration)
            
            # Motion artifact (sudden change in amplitude)
            motion_artifact = np.random.choice([-0.5, 0.5]) * np.ones(end_idx - start_idx)
            contaminated[start_idx:end_idx] += motion_artifact
    
    return contaminated


def add_respiratory_artifacts(data: np.ndarray, contamination_level: float,
                             seed: Optional[int] = None) -> np.ndarray:
    """
    Add respiratory-specific artifacts to the signal.
    
    Parameters:
    -----------
    data : np.ndarray
        Original respiratory signal
    contamination_level : float
        Level of contamination
    seed : int, optional
        Random seed for reproducibility
        
    Returns:
    --------
    np.ndarray
        Respiratory signal with artifacts
    """
    if seed is not None:
        np.random.seed(seed)
    
    contaminated = data.copy()
    n = len(data)
    
    # Cough artifacts (sudden spikes)
    if np.random.random() < contamination_level * 0.3:
        n_coughs = int(contamination_level * 5)
        for _ in range(n_coughs):
            idx = np.random.randint(0, n - 50)
            duration = np.random.randint(5, 20)
            end_idx = min(n, idx + duration)
            
            # Cough artifact (sudden spike)
            cough_artifact = np.exp(-np.arange(end_idx - idx) / 5) * np.random.choice([-1, 1]) * 2
            contaminated[idx:end_idx] += cough_artifact
    
    # Speaking artifacts (irregular breathing)
    if np.random.random() < contamination_level * 0.5:
        # Add irregular breathing patterns
        irregular_component = 0.3 * np.random.randn(n)
        contaminated += irregular_component
    
    # Movement artifacts (baseline shifts)
    if np.random.random() < contamination_level * 0.4:
        n_movements = int(contamination_level * 3)
        for _ in range(n_movements):
            idx = np.random.randint(0, n - 100)
            shift_amplitude = np.random.choice([-0.5, 0.5])
            contaminated[idx:] += shift_amplitude
    
    return contaminated


def generate_biomedical_scenario(scenario_type: str, n: int, hurst: float,
                                contamination_level: float = 0.1,
                                auto_contamination: str = None,
                                **kwargs) -> np.ndarray:
    """
    Generate biomedical time series data for a specific scenario.
    
    Parameters:
    -----------
    scenario_type : str
        Type of biomedical scenario ('eeg', 'ecg', 'respiratory')
    n : int
        Length of the time series
    hurst : float
        Hurst exponent
    contamination_level : float
        Level of contamination/artifacts
    auto_contamination : str, optional
        Automatic contamination type to apply (e.g., 'parkinsonian_tremor', 'epileptic_spike')
    **kwargs
        Additional parameters for specific scenarios
        
    Returns:
    --------
    np.ndarray
        Biomedical time series data
    """
    if scenario_type == 'eeg':
        eeg_scenario = kwargs.get('eeg_scenario', 'rest')
        data = generate_eeg_scenario(n, hurst, eeg_scenario, contamination_level)
        
        # Apply automatic contamination if specified
        if auto_contamination:
            from .generation import add_contamination
            data = add_contamination(data, auto_contamination, contamination_level)
        
        return data
    
    elif scenario_type == 'ecg':
        heart_rate = kwargs.get('heart_rate', 70.0)
        data = generate_ecg_scenario(n, hurst, heart_rate, contamination_level)
        
        # Apply automatic contamination if specified
        if auto_contamination:
            from .generation import add_contamination
            data = add_contamination(data, auto_contamination, contamination_level)
        
        return data
    
    elif scenario_type == 'respiratory':
        breathing_rate = kwargs.get('breathing_rate', 15.0)
        data = generate_respiratory_scenario(n, hurst, breathing_rate, contamination_level)
        
        # Apply automatic contamination if specified
        if auto_contamination:
            from .generation import add_contamination
            data = add_contamination(data, auto_contamination, contamination_level)
        
        return data
    
    else:
        raise ValueError(f"Unknown biomedical scenario: {scenario_type}")


def generate_biomedical_grid(scenario_type: str, hurst_values: List[float],
                           lengths: List[int], contamination_levels: List[float],
                           **kwargs) -> List[TimeSeriesSample]:
    """
    Generate a grid of biomedical time series samples.
    
    Parameters:
    -----------
    scenario_type : str
        Type of biomedical scenario
    hurst_values : List[float]
        List of Hurst exponents
    lengths : List[int]
        List of time series lengths
    contamination_levels : List[float]
        List of contamination levels
    **kwargs
        Additional parameters for specific scenarios
        
    Returns:
    --------
    List[TimeSeriesSample]
        List of biomedical time series samples
    """
    samples = []
    sample_id = 0
    
    for hurst in hurst_values:
        for length in lengths:
            for contamination_level in contamination_levels:
                # Generate biomedical time series
                data = generate_biomedical_scenario(
                    scenario_type, length, hurst, contamination_level, **kwargs
                )
                
                # Create sample
                sample = TimeSeriesSample(
                    data=data,
                    true_hurst=hurst,
                    length=length,
                    contamination=f"{scenario_type}_contamination_{contamination_level}",
                    seed=sample_id
                )
                samples.append(sample)
                sample_id += 1
    
    return samples


# Predefined biomedical scenarios
BIOMEDICAL_SCENARIOS = {
    'eeg_rest': {
        'scenario_type': 'eeg',
        'eeg_scenario': 'rest',
        'hurst_range': (0.5, 0.8),
        'typical_amplitude': 75.0,
        'noise_level': 0.1
    },
    'eeg_eyes_closed': {
        'scenario_type': 'eeg',
        'eeg_scenario': 'eyes_closed',
        'hurst_range': (0.6, 0.9),
        'typical_amplitude': 80.0,
        'noise_level': 0.08
    },
    'eeg_sleep': {
        'scenario_type': 'eeg',
        'eeg_scenario': 'sleep',
        'hurst_range': (0.7, 0.95),
        'typical_amplitude': 100.0,
        'noise_level': 0.05
    },
    'eeg_parkinsonian': {
        'scenario_type': 'eeg',
        'eeg_scenario': 'parkinsonian',
        'hurst_range': (0.3, 0.6),
        'typical_amplitude': 120.0,
        'noise_level': 0.2,
        'auto_contamination': 'parkinsonian_tremor'
    },
    'eeg_epileptic': {
        'scenario_type': 'eeg',
        'eeg_scenario': 'epileptic',
        'hurst_range': (0.2, 0.5),
        'typical_amplitude': 150.0,
        'noise_level': 0.25,
        'auto_contamination': 'epileptic_spike'
    },
    'eeg_parkinsonian_avalanche': {
        'scenario_type': 'eeg',
        'eeg_scenario': 'parkinsonian',
        'hurst_range': (0.2, 0.4),
        'typical_amplitude': 140.0,
        'noise_level': 0.3,
        'auto_contamination': 'neural_avalanche'
    },
    'eeg_epileptic_heavy_tail': {
        'scenario_type': 'eeg',
        'eeg_scenario': 'epileptic',
        'hurst_range': (0.1, 0.4),
        'typical_amplitude': 180.0,
        'noise_level': 0.35,
        'auto_contamination': 'heavy_tail'
    },
    'eeg_burst_suppression': {
        'scenario_type': 'eeg',
        'eeg_scenario': 'sleep',
        'hurst_range': (0.4, 0.7),
        'typical_amplitude': 90.0,
        'noise_level': 0.15,
        'auto_contamination': 'burst_suppression'
    },
    'ecg_normal': {
        'scenario_type': 'ecg',
        'heart_rate': 70.0,
        'hurst_range': (0.3, 0.6),
        'typical_amplitude': 2.0,
        'noise_level': 0.1
    },
    'ecg_tachycardia': {
        'scenario_type': 'ecg',
        'heart_rate': 120.0,
        'hurst_range': (0.2, 0.5),
        'typical_amplitude': 2.5,
        'noise_level': 0.15
    },
    'respiratory_rest': {
        'scenario_type': 'respiratory',
        'breathing_rate': 15.0,
        'hurst_range': (0.4, 0.7),
        'typical_amplitude': 0.5,
        'noise_level': 0.1
    }
}
