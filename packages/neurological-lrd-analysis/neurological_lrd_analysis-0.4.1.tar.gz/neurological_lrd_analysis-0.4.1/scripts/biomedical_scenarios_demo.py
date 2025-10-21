#!/usr/bin/env python3
"""
Biomedical Scenarios Demo for Neurological LRD Analysis

This script demonstrates the biomedical scenario-based time series generation
and enhanced contamination methods relevant to real biomedical data.

Developed as part of PhD research in Biomedical Engineering at the University of Reading, UK.
Author: Davian R. Chin (PhD Candidate in Biomedical Engineering)
Research Focus: Physics-Informed Fractional Operator Learning for Real-Time Neurological Biomarker Detection.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from neurological_lrd_analysis.benchmark_core.biomedical_scenarios import (
    generate_eeg_scenario, generate_ecg_scenario, generate_respiratory_scenario,
    BIOMEDICAL_SCENARIOS
)
from neurological_lrd_analysis.benchmark_core.generation import add_contamination, fbm_davies_harte


def plot_biomedical_scenarios():
    """Plot different biomedical scenarios."""
    print("Generating biomedical scenarios...")
    
    # Generate data for different scenarios
    n = 2000  # 8 seconds at 250 Hz
    hurst = 0.7
    
    scenarios = {
        'EEG Rest': generate_eeg_scenario(n, hurst, 'rest', contamination_level=0.0, seed=42),
        'EEG Eyes Closed': generate_eeg_scenario(n, hurst, 'eyes_closed', contamination_level=0.0, seed=42),
        'EEG Sleep': generate_eeg_scenario(n, hurst, 'sleep', contamination_level=0.0, seed=42),
        'ECG Normal': generate_ecg_scenario(n, hurst, heart_rate=70.0, contamination_level=0.0, seed=42),
        'ECG Tachycardia': generate_ecg_scenario(n, hurst, heart_rate=120.0, contamination_level=0.0, seed=42),
        'Respiratory': generate_respiratory_scenario(n, hurst, breathing_rate=15.0, contamination_level=0.0, seed=42)
    }
    
    # Create subplots
    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    axes = axes.flatten()
    
    for i, (scenario_name, data) in enumerate(scenarios.items()):
        ax = axes[i]
        time_axis = np.arange(len(data)) / 250.0  # Convert to seconds
        
        ax.plot(time_axis, data, linewidth=1, alpha=0.8)
        ax.set_title(f'{scenario_name} (H={hurst})', fontsize=12, fontweight='bold')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        ax.grid(True, alpha=0.3)
        
        # Add some statistics
        stats_text = f'Mean: {np.mean(data):.2f}\nStd: {np.std(data):.2f}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('biomedical_scenarios.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("Biomedical scenarios plot saved to 'biomedical_scenarios.png'")


def plot_contamination_effects():
    """Plot the effects of different contamination types on biomedical signals."""
    print("Demonstrating contamination effects...")
    
    # Generate base signals
    n = 1000
    hurst = 0.7
    
    base_signals = {
        'EEG': generate_eeg_scenario(n, hurst, 'rest', contamination_level=0.0, seed=42),
        'ECG': generate_ecg_scenario(n, hurst, heart_rate=70.0, contamination_level=0.0, seed=42),
        'Respiratory': generate_respiratory_scenario(n, hurst, breathing_rate=15.0, contamination_level=0.0, seed=42)
    }
    
    # Contamination types
    contamination_types = ['none', 'noise', 'baseline_drift', 'electrode_pop', 'motion', 'powerline']
    
    # Create plots
    fig, axes = plt.subplots(len(base_signals), len(contamination_types), figsize=(18, 9))
    
    for i, (signal_name, base_signal) in enumerate(base_signals.items()):
        for j, contam_type in enumerate(contamination_types):
            ax = axes[i, j]
            
            if contam_type == 'none':
                contaminated_signal = base_signal
            else:
                contaminated_signal = add_contamination(base_signal, contam_type, contamination_level=0.1, seed=42)
            
            time_axis = np.arange(len(contaminated_signal)) / 250.0
            
            ax.plot(time_axis, contaminated_signal, linewidth=1, alpha=0.8)
            ax.set_title(f'{signal_name}\n{contam_type.replace("_", " ").title()}', fontsize=10)
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Amplitude')
            ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('contamination_effects.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("Contamination effects plot saved to 'contamination_effects.png'")


def demonstrate_scenario_characteristics():
    """Demonstrate the characteristics of different biomedical scenarios."""
    print("Analyzing scenario characteristics...")
    
    scenarios = [
        ('eeg_rest', 'EEG Rest'),
        ('eeg_eyes_closed', 'EEG Eyes Closed'),
        ('eeg_sleep', 'EEG Sleep'),
        ('ecg_normal', 'ECG Normal'),
        ('ecg_tachycardia', 'ECG Tachycardia'),
        ('respiratory_rest', 'Respiratory Rest')
    ]
    
    print("\n" + "="*80)
    print("BIOMEDICAL SCENARIO CHARACTERISTICS")
    print("="*80)
    
    for scenario_key, scenario_name in scenarios:
        if scenario_key in BIOMEDICAL_SCENARIOS:
            config = BIOMEDICAL_SCENARIOS[scenario_key]
            
            print(f"\n{scenario_name}:")
            print(f"  Type: {config['scenario_type']}")
            print(f"  Expected Hurst Range: {config['hurst_range'][0]:.2f} - {config['hurst_range'][1]:.2f}")
            print(f"  Typical Amplitude: {config['typical_amplitude']}")
            print(f"  Typical Noise Level: {config['noise_level']}")
            
            # Generate sample data
            if config['scenario_type'] == 'eeg':
                data = generate_eeg_scenario(1000, 0.7, config.get('eeg_scenario', 'rest'), 0.0, 42)
            elif config['scenario_type'] == 'ecg':
                data = generate_ecg_scenario(1000, 0.7, config.get('heart_rate', 70.0), 0.0, 42)
            elif config['scenario_type'] == 'respiratory':
                data = generate_respiratory_scenario(1000, 0.7, config.get('breathing_rate', 15.0), 0.0, 42)
            
            print(f"  Sample Statistics:")
            print(f"    Mean: {np.mean(data):.4f}")
            print(f"    Std: {np.std(data):.4f}")
            print(f"    Min: {np.min(data):.4f}")
            print(f"    Max: {np.max(data):.4f}")


def run_biomedical_benchmark():
    """Run a benchmark specifically for biomedical scenarios."""
    print("\n" + "="*80)
    print("BIOMEDICAL SCENARIO BENCHMARK")
    print("="*80)
    
    from benchmark_core.generation import generate_grid
    from benchmark_core.runner import BenchmarkConfig, run_benchmark_on_dataset, create_leaderboard
    
    # Generate biomedical datasets
    datasets = generate_grid(
        hurst_values=[0.5, 0.7, 0.9],
        lengths=[512, 1024],
        contaminations=['none', 'noise', 'electrode_pop'],
        contamination_level=0.1,
        biomedical_scenarios=['eeg_rest', 'ecg_normal'],
        seed=42
    )
    
    print(f"Generated {len(datasets)} biomedical test datasets")
    
    # Configure benchmark
    config = BenchmarkConfig(
        output_dir='./biomedical_benchmark_results',
        n_bootstrap=50,  # Smaller for demo
        confidence_level=0.95,
        save_results=True,
        verbose=False
    )
    
    # Run benchmark
    print("Running biomedical benchmark...")
    results = run_benchmark_on_dataset(datasets, config)
    
    # Create leaderboard
    leaderboard = create_leaderboard(results)
    
    print("\n" + "="*80)
    print("BIOMEDICAL SCENARIO LEADERBOARD")
    print("="*80)
    print(leaderboard.to_string(index=False))
    
    print(f"\nResults saved to: {config.output_dir}")


def main():
    """Main demonstration function."""
    print("Biomedical Scenarios Demo")
    print("=" * 50)
    
    # Create output directory
    Path("biomedical_demo_output").mkdir(exist_ok=True)
    
    # Run demonstrations
    try:
        plot_biomedical_scenarios()
        plot_contamination_effects()
        demonstrate_scenario_characteristics()
        run_biomedical_benchmark()
        
        print("\n" + "="*80)
        print("DEMO COMPLETE")
        print("="*80)
        print("Generated files:")
        print("  - biomedical_scenarios.png: Different biomedical signal types")
        print("  - contamination_effects.png: Effects of various contaminations")
        print("  - biomedical_benchmark_results/: Benchmark results for biomedical scenarios")
        
        print("\nKey Features Demonstrated:")
        print("  1. Realistic EEG, ECG, and respiratory signal generation")
        print("  2. Biomedical-specific contamination methods")
        print("  3. Scenario-based benchmarking")
        print("  4. Enhanced contamination types relevant to biomedical data")
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
        raise


if __name__ == "__main__":
    main()
