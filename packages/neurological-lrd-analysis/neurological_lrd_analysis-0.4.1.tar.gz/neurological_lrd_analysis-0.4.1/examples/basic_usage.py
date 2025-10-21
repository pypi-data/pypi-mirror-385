#!/usr/bin/env python3
"""
Basic Usage Example for Neurological LRD Analysis

This example demonstrates the basic usage of the neurological LRD analysis library
for estimating Hurst exponents in neurological time series data.

Developed as part of PhD research in Biomedical Engineering at the University of Reading, UK.
Author: Davian R. Chin (PhD Candidate in Biomedical Engineering)
Research Focus: Physics-Informed Fractional Operator Learning for Real-Time Neurological Biomarker Detection.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from neurological_lrd_analysis.biomedical_hurst_factory import BiomedicalHurstEstimatorFactory, EstimatorType

def main():
    """Main example function."""
    print("Neurological LRD Analysis - Basic Usage Example")
    print("=" * 50)
    
    # Create factory instance
    factory = BiomedicalHurstEstimatorFactory()
    
    # Generate synthetic EEG-like data
    print("\n1. Generating synthetic EEG data...")
    from neurological_lrd_analysis.benchmark_core.biomedical_scenarios import generate_eeg_scenario
    
    # Generate EEG data with known Hurst exponent
    hurst_true = 0.7
    n_points = 1000
    eeg_data = generate_eeg_scenario(n_points, hurst_true, scenario='rest', seed=42)
    
    print(f"   Generated EEG data with {n_points} points")
    print(f"   True Hurst exponent: {hurst_true}")
    print(f"   Data range: [{np.min(eeg_data):.2f}, {np.max(eeg_data):.2f}]")
    
    # Estimate Hurst exponent using different methods
    print("\n2. Estimating Hurst exponent using different methods...")
    
    methods = [
        EstimatorType.DFA,
        EstimatorType.RS_ANALYSIS,
        EstimatorType.HIGUCHI,
        EstimatorType.GENERALIZED_HURST,
        EstimatorType.PERIODOGRAM,
        EstimatorType.GPH,
    ]
    
    results = {}
    
    for method in methods:
        try:
            result = factory.estimate(
                data=eeg_data,
                method=method,
                confidence_method="bootstrap",
                n_bootstrap=50  # Reduced for demo
            )
            
            results[method.value] = result
            print(f"   {method.value:20s}: {result.hurst_estimate:.4f} "
                  f"(CI: [{result.confidence_interval[0]:.4f}, {result.confidence_interval[1]:.4f}])")
            
        except Exception as e:
            print(f"   {method.value:20s}: Error - {str(e)}")
    
    # Compare results
    print(f"\n3. Results Summary:")
    print(f"   True Hurst exponent: {hurst_true:.4f}")
    print(f"   Best estimate: {min(results.items(), key=lambda x: abs(x[1].hurst_estimate - hurst_true))}")
    
    # Plot the data
    print(f"\n4. Creating visualization...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Plot time series
    time_axis = np.arange(len(eeg_data)) / 250.0  # Assuming 250 Hz sampling
    ax1.plot(time_axis, eeg_data, linewidth=1, alpha=0.8, color='blue')
    ax1.set_title('Synthetic EEG Data (H=0.7)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Amplitude (μV)')
    ax1.grid(True, alpha=0.3)
    
    # Plot estimates comparison
    method_names = list(results.keys())
    estimates = [results[method].hurst_estimate for method in method_names]
    errors = [abs(est - hurst_true) for est in estimates]
    
    bars = ax2.bar(range(len(method_names)), estimates, alpha=0.7, color='skyblue')
    ax2.axhline(y=hurst_true, color='red', linestyle='--', linewidth=2, label=f'True H={hurst_true}')
    ax2.set_title('Hurst Exponent Estimates Comparison', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Estimation Method')
    ax2.set_ylabel('Hurst Exponent')
    ax2.set_xticks(range(len(method_names)))
    ax2.set_xticklabels(method_names, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Add error values on bars
    for i, (bar, error) in enumerate(zip(bars, errors)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{error:.3f}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('basic_usage_example.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print("   Plot saved as 'basic_usage_example.png'")
    
    print(f"\n5. Example completed successfully!")
    print(f"   This example demonstrates:")
    print(f"   - Generating synthetic biomedical data")
    print(f"   - Estimating Hurst exponents with multiple methods")
    print(f"   - Comparing results and visualizing data")
    print(f"   - Basic usage of the biomedical Hurst factory library")

if __name__ == "__main__":
    main()
