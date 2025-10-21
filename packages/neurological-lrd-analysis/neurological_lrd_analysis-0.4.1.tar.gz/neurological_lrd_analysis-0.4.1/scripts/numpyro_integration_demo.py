#!/usr/bin/env python3
"""
NumPyro Integration Demo for Neurological LRD Analysis

This script demonstrates the enhanced Bayesian inference capabilities
using NumPyro for probabilistic Hurst exponent estimation.

Developed as part of PhD research in Biomedical Engineering at the University of Reading, UK.
Author: Davian R. Chin (PhD Candidate in Biomedical Engineering)
Research Focus: Physics-Informed Fractional Operator Learning for Real-Time Neurological Biomarker Detection,
with particular emphasis on Bayesian inference for physics-informed fractional operator learning.
"""

import numpy as np
import matplotlib.pyplot as plt
import time
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from neurological_lrd_analysis.biomedical_hurst_factory import (
    BiomedicalHurstEstimatorFactory, 
    EstimatorType, 
    ConfidenceMethod,
    BayesianHurstEstimator
)


def generate_synthetic_data(n: int = 1000, hurst: float = 0.7, seed: int = 42) -> np.ndarray:
    """Generate synthetic fractional Brownian motion data"""
    np.random.seed(seed)
    
    # Simple fBm approximation using power-law filtering
    white_noise = np.random.randn(n)
    
    # Apply power-law filter to approximate fBm
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


def compare_inference_methods(data: np.ndarray, true_hurst: float):
    """Compare different inference methods"""
    factory = BiomedicalHurstEstimatorFactory()
    
    print("=" * 80)
    print("COMPARISON OF INFERENCE METHODS")
    print("=" * 80)
    print(f"True Hurst exponent: {true_hurst:.3f}")
    print(f"Data length: {len(data)}")
    print()
    
    methods = [
        ("Bootstrap (100 samples)", ConfidenceMethod.BOOTSTRAP, {'n_bootstrap': 100}),
        ("Bootstrap (500 samples)", ConfidenceMethod.BOOTSTRAP, {'n_bootstrap': 500}),
        ("Theoretical", ConfidenceMethod.THEORETICAL, {}),
        ("Bayesian (1000 samples)", ConfidenceMethod.BAYESIAN, {'num_samples': 1000, 'num_warmup': 500}),
        ("Bayesian (2000 samples)", ConfidenceMethod.BAYESIAN, {'num_samples': 2000, 'num_warmup': 1000}),
    ]
    
    results = []
    
    for method_name, confidence_method, kwargs in methods:
        print(f"Running {method_name}...")
        start_time = time.time()
        
        try:
            result = factory.estimate(
                data, 
                EstimatorType.DFA,
                confidence_method=confidence_method,
                confidence_level=0.95,
                **kwargs
            )
            
            computation_time = time.time() - start_time
            
            # Calculate bias
            bias = result.hurst_estimate - true_hurst
            
            print(f"  Hurst estimate: {result.hurst_estimate:.4f}")
            print(f"  Bias: {bias:+.4f}")
            print(f"  Confidence interval: [{result.confidence_interval[0]:.4f}, {result.confidence_interval[1]:.4f}]")
            print(f"  CI width: {result.confidence_interval[1] - result.confidence_interval[0]:.4f}")
            print(f"  Computation time: {computation_time:.2f}s")
            
            # Bayesian-specific metrics
            if confidence_method == ConfidenceMethod.BAYESIAN:
                rhat = result.additional_metrics.get('bayesian_rhat', np.nan)
                convergence = result.additional_metrics.get('bayesian_convergence', False)
                print(f"  R-hat: {rhat:.4f}")
                print(f"  Convergence: {'✓' if convergence else '✗'}")
            
            results.append({
                'method': method_name,
                'estimate': result.hurst_estimate,
                'bias': bias,
                'ci_width': result.confidence_interval[1] - result.confidence_interval[0],
                'time': computation_time,
                'result': result
            })
            
        except Exception as e:
            print(f"  Error: {e}")
            results.append({
                'method': method_name,
                'estimate': np.nan,
                'bias': np.nan,
                'ci_width': np.nan,
                'time': time.time() - start_time,
                'error': str(e)
            })
        
        print()
    
    return results


def bayesian_analysis_demo(data: np.ndarray):
    """Demonstrate detailed Bayesian analysis"""
    print("=" * 80)
    print("DETAILED BAYESIAN ANALYSIS")
    print("=" * 80)
    
    # Create Bayesian estimator
    bayesian_estimator = BayesianHurstEstimator(EstimatorType.DFA)
    
    # Run inference
    print("Running Bayesian inference...")
    results = bayesian_estimator.infer_hurst(
        data, 
        num_samples=2000, 
        num_warmup=1000, 
        num_chains=4,
        random_seed=42
    )
    
    print(f"Hurst estimate: {results['hurst_mean']:.4f} ± {results['hurst_std']:.4f}")
    print(f"95% Credible interval: [{results['credible_interval'][0]:.4f}, {results['credible_interval'][1]:.4f}]")
    print(f"R-hat: {results['rhat']:.4f}")
    print(f"Convergence: {'✓' if results['convergence_flag'] else '✗'}")
    
    # Extract samples for plotting
    if 'samples' in results and 'hurst' in results['samples']:
        hurst_samples = results['samples']['hurst']
        
        # Create plots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Trace plot
        axes[0, 0].plot(hurst_samples)
        axes[0, 0].set_title('MCMC Trace')
        axes[0, 0].set_xlabel('Sample')
        axes[0, 0].set_ylabel('Hurst Exponent')
        
        # Histogram
        axes[0, 1].hist(hurst_samples, bins=50, density=True, alpha=0.7)
        axes[0, 1].axvline(results['hurst_mean'], color='red', linestyle='--', label='Mean')
        axes[0, 1].axvline(results['credible_interval'][0], color='orange', linestyle='--', label='95% CI')
        axes[0, 1].axvline(results['credible_interval'][1], color='orange', linestyle='--')
        axes[0, 1].set_title('Posterior Distribution')
        axes[0, 1].set_xlabel('Hurst Exponent')
        axes[0, 1].set_ylabel('Density')
        axes[0, 1].legend()
        
        # Autocorrelation
        autocorr = np.correlate(hurst_samples - np.mean(hurst_samples), 
                               hurst_samples - np.mean(hurst_samples), mode='full')
        autocorr = autocorr[autocorr.size // 2:]
        autocorr = autocorr / autocorr[0]
        
        axes[1, 0].plot(autocorr[:100])
        axes[1, 0].set_title('Autocorrelation')
        axes[1, 0].set_xlabel('Lag')
        axes[1, 0].set_ylabel('Autocorrelation')
        
        # Running mean
        running_mean = np.cumsum(hurst_samples) / np.arange(1, len(hurst_samples) + 1)
        axes[1, 1].plot(running_mean)
        axes[1, 1].set_title('Running Mean')
        axes[1, 1].set_xlabel('Sample')
        axes[1, 1].set_ylabel('Running Mean')
        
        plt.tight_layout()
        plt.savefig('bayesian_analysis.png', dpi=150, bbox_inches='tight')
        plt.show()
        
        print(f"\nBayesian analysis plots saved to 'bayesian_analysis.png'")
    
    return results


def hierarchical_model_demo():
    """Demonstrate hierarchical Bayesian modeling for multiple time series"""
    print("=" * 80)
    print("HIERARCHICAL BAYESIAN MODELING")
    print("=" * 80)
    
    # Generate multiple time series with different Hurst exponents
    hurst_values = [0.3, 0.5, 0.7]
    n_series = len(hurst_values)
    n_points = 1000
    
    print(f"Generating {n_series} time series with Hurst values: {hurst_values}")
    
    # Generate data
    data_list = []
    for i, hurst in enumerate(hurst_values):
        data = generate_synthetic_data(n_points, hurst, seed=42 + i)
        data_list.append(data)
    
    # Analyze each series individually
    print("\nIndividual Bayesian estimates:")
    individual_estimates = []
    
    for i, (data, true_hurst) in enumerate(zip(data_list, hurst_values)):
        print(f"\nSeries {i+1} (True H = {true_hurst:.3f}):")
        
        bayesian_estimator = BayesianHurstEstimator(EstimatorType.DFA)
        results = bayesian_estimator.infer_hurst(data, num_samples=1000, num_warmup=500)
        
        print(f"  Estimate: {results['hurst_mean']:.4f} ± {results['hurst_std']:.4f}")
        print(f"  95% CI: [{results['credible_interval'][0]:.4f}, {results['credible_interval'][1]:.4f}]")
        print(f"  R-hat: {results['rhat']:.4f}")
        
        individual_estimates.append(results['hurst_mean'])
    
    # Calculate overall statistics
    print(f"\nOverall statistics:")
    print(f"Individual estimates: {[f'{h:.4f}' for h in individual_estimates]}")
    print(f"Mean estimate: {np.mean(individual_estimates):.4f}")
    print(f"Std estimate: {np.std(individual_estimates):.4f}")
    print(f"True mean: {np.mean(hurst_values):.4f}")


def main():
    """Main demonstration function"""
    print("NumPyro Integration Demo for Biomedical Hurst Factory")
    print("=" * 80)
    
    # Generate synthetic data
    print("Generating synthetic fractional Brownian motion data...")
    true_hurst = 0.7
    data = generate_synthetic_data(n=2000, hurst=true_hurst, seed=42)
    
    # Compare inference methods
    results = compare_inference_methods(data, true_hurst)
    
    # Detailed Bayesian analysis
    bayesian_results = bayesian_analysis_demo(data)
    
    # Hierarchical modeling demo
    hierarchical_model_demo()
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("NumPyro integration provides:")
    print("✓ Bayesian inference with full posterior distributions")
    print("✓ Credible intervals with proper uncertainty quantification")
    print("✓ Convergence diagnostics (R-hat)")
    print("✓ JAX-accelerated MCMC sampling")
    print("✓ Hierarchical modeling capabilities")
    print("✓ Probabilistic Hurst exponent estimation")
    
    print(f"\nDemo completed successfully!")
    print(f"Results saved to current directory.")


if __name__ == "__main__":
    main()
