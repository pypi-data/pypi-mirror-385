#!/usr/bin/env python3
"""
Neurological Conditions Demo for Neurological LRD Analysis

This script demonstrates the neurological condition-specific time series generation
with heavy-tail amplitudes and neural avalanches relevant to Parkinson's disease,
epilepsy, and other neurological conditions.

Developed as part of PhD research in Biomedical Engineering at the University of Reading, UK.
Author: Davian R. Chin (PhD Candidate in Biomedical Engineering)
Research Focus: Physics-Informed Fractional Operator Learning for Real-Time Neurological Biomarker Detection,
with particular emphasis on memory-driven EEG analysis for neurological condition detection.
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
    generate_eeg_scenario, BIOMEDICAL_SCENARIOS
)
from neurological_lrd_analysis.benchmark_core.generation import add_contamination, fbm_davies_harte


def plot_neurological_contaminations():
    """Plot different neurological contamination types."""
    print("Generating neurological contamination examples...")
    
    # Generate base signal
    n = 2000  # 8 seconds at 250 Hz
    hurst = 0.7
    base_signal = fbm_davies_harte(n, hurst, seed=42)
    
    # Neurological contamination types
    contamination_types = [
        'heavy_tail',
        'neural_avalanche', 
        'parkinsonian_tremor',
        'epileptic_spike',
        'burst_suppression'
    ]
    
    # Create subplots
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    # Plot original signal
    time_axis = np.arange(n) / 250.0
    axes[0].plot(time_axis, base_signal, linewidth=1, alpha=0.8, color='blue')
    axes[0].set_title('Original Signal (fBm, H=0.7)', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Time (s)')
    axes[0].set_ylabel('Amplitude')
    axes[0].grid(True, alpha=0.3)
    
    # Plot contaminated signals
    for i, contam_type in enumerate(contamination_types):
        ax = axes[i + 1]
        
        contaminated_signal = add_contamination(base_signal, contam_type, contamination_level=0.15, seed=42)
        
        ax.plot(time_axis, contaminated_signal, linewidth=1, alpha=0.8, color='red')
        ax.set_title(f'{contam_type.replace("_", " ").title()}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        ax.grid(True, alpha=0.3)
        
        # Add statistics
        stats_text = f'Mean: {np.mean(contaminated_signal):.2f}\nStd: {np.std(contaminated_signal):.2f}\nMax: {np.max(contaminated_signal):.2f}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('neurological_contaminations.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("Neurological contaminations plot saved to 'neurological_contaminations.png'")


def plot_parkinsonian_scenarios():
    """Plot Parkinson's disease scenarios with different contamination types."""
    print("Generating Parkinson's disease scenarios...")
    
    n = 2000
    hurst = 0.5
    
    scenarios = {
        'Parkinsonian EEG': generate_eeg_scenario(n, hurst, 'parkinsonian', contamination_level=0.0, seed=42),
        'Parkinsonian + Tremor': add_contamination(
            generate_eeg_scenario(n, hurst, 'parkinsonian', contamination_level=0.0, seed=42),
            'parkinsonian_tremor', contamination_level=0.15, seed=42
        ),
        'Parkinsonian + Avalanche': add_contamination(
            generate_eeg_scenario(n, hurst, 'parkinsonian', contamination_level=0.0, seed=42),
            'neural_avalanche', contamination_level=0.15, seed=42
        ),
        'Parkinsonian + Heavy Tail': add_contamination(
            generate_eeg_scenario(n, hurst, 'parkinsonian', contamination_level=0.0, seed=42),
            'heavy_tail', contamination_level=0.15, seed=42
        )
    }
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, (scenario_name, data) in enumerate(scenarios.items()):
        ax = axes[i]
        time_axis = np.arange(len(data)) / 250.0
        
        ax.plot(time_axis, data, linewidth=1, alpha=0.8)
        ax.set_title(f'{scenario_name}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude (μV)')
        ax.grid(True, alpha=0.3)
        
        # Add statistics
        stats_text = f'Mean: {np.mean(data):.1f}\nStd: {np.std(data):.1f}\nMax: {np.max(data):.1f}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('parkinsonian_scenarios.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("Parkinson's disease scenarios plot saved to 'parkinsonian_scenarios.png'")


def plot_epileptic_scenarios():
    """Plot epilepsy scenarios with different contamination types."""
    print("Generating epilepsy scenarios...")
    
    n = 2000
    hurst = 0.4
    
    scenarios = {
        'Epileptic EEG': generate_eeg_scenario(n, hurst, 'epileptic', contamination_level=0.0, seed=42),
        'Epileptic + Spikes': add_contamination(
            generate_eeg_scenario(n, hurst, 'epileptic', contamination_level=0.0, seed=42),
            'epileptic_spike', contamination_level=0.15, seed=42
        ),
        'Epileptic + Heavy Tail': add_contamination(
            generate_eeg_scenario(n, hurst, 'epileptic', contamination_level=0.0, seed=42),
            'heavy_tail', contamination_level=0.15, seed=42
        ),
        'Epileptic + Avalanche': add_contamination(
            generate_eeg_scenario(n, hurst, 'epileptic', contamination_level=0.0, seed=42),
            'neural_avalanche', contamination_level=0.15, seed=42
        )
    }
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, (scenario_name, data) in enumerate(scenarios.items()):
        ax = axes[i]
        time_axis = np.arange(len(data)) / 250.0
        
        ax.plot(time_axis, data, linewidth=1, alpha=0.8)
        ax.set_title(f'{scenario_name}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude (μV)')
        ax.grid(True, alpha=0.3)
        
        # Add statistics
        stats_text = f'Mean: {np.mean(data):.1f}\nStd: {np.std(data):.1f}\nMax: {np.max(data):.1f}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('epileptic_scenarios.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("Epilepsy scenarios plot saved to 'epileptic_scenarios.png'")


def demonstrate_contamination_statistics():
    """Demonstrate statistical properties of different contamination types."""
    print("Analyzing contamination statistics...")
    
    n = 5000
    hurst = 0.7
    base_signal = fbm_davies_harte(n, hurst, seed=42)
    
    contamination_types = [
        'heavy_tail',
        'neural_avalanche',
        'parkinsonian_tremor',
        'epileptic_spike',
        'burst_suppression'
    ]
    
    print("\n" + "="*80)
    print("NEUROLOGICAL CONTAMINATION STATISTICS")
    print("="*80)
    
    for contam_type in contamination_types:
        contaminated = add_contamination(base_signal, contam_type, contamination_level=0.15, seed=42)
        
        # Calculate statistics
        mean_val = np.mean(contaminated)
        std_val = np.std(contaminated)
        max_val = np.max(contaminated)
        min_val = np.min(contaminated)
        skewness = np.mean(((contaminated - mean_val) / std_val)**3)
        kurtosis = np.mean(((contaminated - mean_val) / std_val)**4) - 3
        
        print(f"\n{contam_type.replace('_', ' ').title()}:")
        print(f"  Mean: {mean_val:.4f}")
        print(f"  Std: {std_val:.4f}")
        print(f"  Min: {min_val:.4f}")
        print(f"  Max: {max_val:.4f}")
        print(f"  Skewness: {skewness:.4f}")
        print(f"  Kurtosis: {kurtosis:.4f}")
        
        # Check for heavy tails (kurtosis > 3 indicates heavy tails)
        if kurtosis > 3:
            print(f"  *** Heavy-tailed distribution detected (kurtosis > 3)")


def run_neurological_benchmark():
    """Run a benchmark specifically for neurological conditions."""
    print("\n" + "="*80)
    print("NEUROLOGICAL CONDITIONS BENCHMARK")
    print("="*80)
    
    from benchmark_core.generation import generate_grid
    from benchmark_core.runner import BenchmarkConfig, run_benchmark_on_dataset, create_leaderboard
    
    # Generate neurological datasets
    datasets = generate_grid(
        hurst_values=[0.3, 0.5, 0.7],
        lengths=[512, 1024],
        contaminations=['none', 'heavy_tail', 'neural_avalanche'],
        contamination_level=0.15,
        biomedical_scenarios=['eeg_parkinsonian', 'eeg_epileptic', 'eeg_parkinsonian_avalanche'],
        seed=42
    )
    
    print(f"Generated {len(datasets)} neurological test datasets")
    
    # Configure benchmark
    config = BenchmarkConfig(
        output_dir='./neurological_benchmark_results',
        n_bootstrap=50,  # Smaller for demo
        confidence_level=0.95,
        save_results=True,
        verbose=False
    )
    
    # Run benchmark
    print("Running neurological conditions benchmark...")
    results = run_benchmark_on_dataset(datasets, config)
    
    # Create leaderboard
    leaderboard = create_leaderboard(results)
    
    print("\n" + "="*80)
    print("NEUROLOGICAL CONDITIONS LEADERBOARD")
    print("="*80)
    print(leaderboard.to_string(index=False))
    
    print(f"\nResults saved to: {config.output_dir}")


def main():
    """Main demonstration function."""
    print("Neurological Conditions Demo")
    print("=" * 50)
    
    # Create output directory
    Path("neurological_demo_output").mkdir(exist_ok=True)
    
    # Run demonstrations
    try:
        plot_neurological_contaminations()
        plot_parkinsonian_scenarios()
        plot_epileptic_scenarios()
        demonstrate_contamination_statistics()
        run_neurological_benchmark()
        
        print("\n" + "="*80)
        print("DEMO COMPLETE")
        print("="*80)
        print("Generated files:")
        print("  - neurological_contaminations.png: Different neurological contamination types")
        print("  - parkinsonian_scenarios.png: Parkinson's disease scenarios")
        print("  - epileptic_scenarios.png: Epilepsy scenarios")
        print("  - neurological_benchmark_results/: Benchmark results for neurological conditions")
        
        print("\nKey Features Demonstrated:")
        print("  1. Heavy-tail amplitude distributions")
        print("  2. Neural avalanche patterns")
        print("  3. Parkinsonian tremor characteristics")
        print("  4. Epileptic spike patterns")
        print("  5. Burst-suppression patterns")
        print("  6. Statistical analysis of neurological contaminants")
        
        print("\nClinical Relevance:")
        print("  - Parkinson's disease: Tremor, neural avalanches, reduced Hurst exponent")
        print("  - Epilepsy: Spikes, heavy-tail distributions, irregular patterns")
        print("  - Anesthesia/Coma: Burst-suppression patterns")
        print("  - General neurological conditions: Heavy-tail amplitude distributions")
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
        raise


if __name__ == "__main__":
    main()
