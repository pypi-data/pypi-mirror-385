#!/usr/bin/env python3
"""
Application-Specific Scoring Demo for Neurological LRD Analysis

This script demonstrates how the parametrized scoring function can be customized
for different biomedical applications with varying priorities.

Developed as part of PhD research in Biomedical Engineering at the University of Reading, UK.
Author: Davian R. Chin (PhD Candidate in Biomedical Engineering)
Research Focus: Physics-Informed Fractional Operator Learning for Real-Time Neurological Biomarker Detection,
with particular emphasis on real-time biomarker detection optimization for clinical applications.
"""

import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from neurological_lrd_analysis.benchmark_core.runner import ScoringWeights, BenchmarkConfig, run_benchmark_on_dataset, create_leaderboard
from neurological_lrd_analysis.benchmark_core.generation import generate_grid
import pandas as pd


def create_application_scoring_configs():
    """
    Create scoring configurations for different biomedical applications.
    
    Returns:
    --------
    Dict[str, ScoringWeights]
        Dictionary of application-specific scoring weights
    """
    configs = {
        # BCI/Real-time applications: prioritize speed and reliability
        "BCI_Real_Time": ScoringWeights(
            success_rate=0.4,    # High: Need reliable results
            accuracy=0.2,        # Medium: Some accuracy trade-off acceptable
            speed=0.3,           # High: Real-time constraints
            robustness=0.1       # Low: Controlled environment
        ),
        
        # Research applications: prioritize accuracy and uncertainty quantification
        "Research": ScoringWeights(
            success_rate=0.2,    # Medium: Some failures acceptable
            accuracy=0.4,        # High: Need precise measurements
            speed=0.1,           # Low: Time not critical
            robustness=0.3       # High: Robust across conditions
        ),
        
        # Clinical applications: prioritize robustness and accuracy
        "Clinical": ScoringWeights(
            success_rate=0.3,    # High: Reliable results needed
            accuracy=0.3,        # High: Clinical decisions depend on accuracy
            speed=0.1,           # Low: Patient safety over speed
            robustness=0.3       # High: Must work across patients/conditions
        ),
        
        # Exploratory analysis: balanced approach
        "Exploratory": ScoringWeights(
            success_rate=0.25,   # Balanced
            accuracy=0.25,       # Balanced
            speed=0.25,          # Balanced
            robustness=0.25      # Balanced
        ),
        
        # High-throughput screening: prioritize speed and success rate
        "High_Throughput": ScoringWeights(
            success_rate=0.35,   # High: Need many successful estimates
            accuracy=0.15,       # Lower: Screening can be less precise
            speed=0.4,           # Very High: Process many samples
            robustness=0.1       # Lower: Controlled screening conditions
        ),
        
        # Quality control: prioritize robustness and success rate
        "Quality_Control": ScoringWeights(
            success_rate=0.35,   # High: Consistent results needed
            accuracy=0.2,        # Medium: Good accuracy required
            speed=0.15,          # Lower: Quality over speed
            robustness=0.3       # High: Must detect variations reliably
        )
    }
    
    return configs


def run_application_benchmarks():
    """
    Run benchmarks with different application-specific scoring configurations.
    """
    print("Application-Specific Scoring Demo")
    print("=" * 50)
    
    # Generate test datasets
    print("Generating test datasets...")
    datasets = generate_grid(
        hurst_values=[0.3, 0.5, 0.7],
        lengths=[512, 1024],
        contaminations=['none', 'noise', 'outliers'],
        contamination_level=0.1,
        seed=42
    )
    print(f"Generated {len(datasets)} test datasets")
    
    # Get application configurations
    app_configs = create_application_scoring_configs()
    
    # Run benchmarks for each application
    results = {}
    
    for app_name, scoring_weights in app_configs.items():
        print(f"\nRunning benchmark for {app_name} application...")
        print(f"  Scoring weights: Success={scoring_weights.success_rate:.2f}, "
              f"Accuracy={scoring_weights.accuracy:.2f}, "
              f"Speed={scoring_weights.speed:.2f}, "
              f"Robustness={scoring_weights.robustness:.2f}")
        
        # Configure benchmark
        config = BenchmarkConfig(
            output_dir=f"./benchmark_results_{app_name.lower()}",
            n_bootstrap=50,  # Reduced for demo
            confidence_level=0.95,
            save_results=False,  # Don't save individual results
            verbose=False,
            scoring_weights=scoring_weights
        )
        
        # Run benchmark
        benchmark_results = run_benchmark_on_dataset(datasets, config)
        
        # Create leaderboard with application-specific scoring
        leaderboard = create_leaderboard(benchmark_results, scoring_weights)
        
        # Store results
        results[app_name] = {
            'leaderboard': leaderboard,
            'scoring_weights': scoring_weights,
            'top_3': leaderboard.head(3)[['Estimator', 'Overall Score', 'Success Rate', 'Mean Absolute Error', 'Mean Time (s)']]
        }
    
    return results


def compare_application_rankings(results):
    """
    Compare how different applications rank estimators differently.
    """
    print("\n" + "=" * 80)
    print("APPLICATION-SPECIFIC RANKING COMPARISON")
    print("=" * 80)
    
    # Create comparison table
    comparison_data = []
    
    for app_name, app_results in results.items():
        top_3 = app_results['top_3']
        for i, (_, row) in enumerate(top_3.iterrows()):
            comparison_data.append({
                'Application': app_name,
                'Rank': i + 1,
                'Estimator': row['Estimator'],
                'Overall Score': row['Overall Score'],
                'Success Rate': row['Success Rate'],
                'MAE': row['Mean Absolute Error'],
                'Time (s)': row['Mean Time (s)']
            })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Display top 3 for each application
    for app_name in results.keys():
        print(f"\n{app_name} Application - Top 3 Estimators:")
        print("-" * 60)
        app_data = comparison_df[comparison_df['Application'] == app_name]
        
        for _, row in app_data.iterrows():
            print(f"  {row['Rank']}. {row['Estimator']}")
            print(f"     Score: {row['Overall Score']:.4f}")
            print(f"     Success Rate: {row['Success Rate']}, MAE: {row['MAE']}, Time: {row['Time (s)']}s")
    
    # Show how rankings differ
    print(f"\n{'='*80}")
    print("RANKING VARIABILITY ANALYSIS")
    print("=" * 80)
    
    # Count how many times each estimator appears in top 3
    estimator_counts = comparison_df['Estimator'].value_counts()
    
    print("\nEstimator frequency in top 3 across applications:")
    for estimator, count in estimator_counts.items():
        percentage = (count / len(results)) * 100
        print(f"  {estimator}: {count}/{len(results)} applications ({percentage:.1f}%)")
    
    # Find most consistent top performer
    most_consistent = estimator_counts.index[0]
    print(f"\nMost consistent top performer: {most_consistent}")
    print(f"Appears in top 3 for {(estimator_counts.iloc[0] / len(results)) * 100:.1f}% of applications")


def demonstrate_scoring_sensitivity():
    """
    Demonstrate how sensitive the rankings are to scoring weight changes.
    """
    print(f"\n{'='*80}")
    print("SCORING SENSITIVITY ANALYSIS")
    print("=" * 80)
    
    # Generate test data
    datasets = generate_grid(
        hurst_values=[0.7],
        lengths=[1024],
        contaminations=['none', 'noise'],
        contamination_level=0.1,
        seed=42
    )
    
    # Test different weight configurations
    weight_variations = [
        ("Default", ScoringWeights()),
        ("Accuracy_Focused", ScoringWeights(success_rate=0.1, accuracy=0.7, speed=0.1, robustness=0.1)),
        ("Speed_Focused", ScoringWeights(success_rate=0.1, accuracy=0.1, speed=0.7, robustness=0.1)),
        ("Robustness_Focused", ScoringWeights(success_rate=0.1, accuracy=0.1, speed=0.1, robustness=0.7)),
        ("Success_Focused", ScoringWeights(success_rate=0.7, accuracy=0.1, speed=0.1, robustness=0.1)),
    ]
    
    print("\nTesting weight sensitivity...")
    
    for name, weights in weight_variations:
        config = BenchmarkConfig(
            output_dir="./temp",
            n_bootstrap=50,
            save_results=False,
            verbose=False,
            scoring_weights=weights
        )
        
        benchmark_results = run_benchmark_on_dataset(datasets, config)
        leaderboard = create_leaderboard(benchmark_results, weights)
        
        print(f"\n{name} Scoring:")
        print(f"  Weights: S={weights.success_rate:.1f}, A={weights.accuracy:.1f}, "
              f"Sp={weights.speed:.1f}, R={weights.robustness:.1f}")
        print(f"  Top 3: {', '.join(leaderboard.head(3)['Estimator'].tolist())}")


def main():
    """Main demonstration function."""
    try:
        # Run application-specific benchmarks
        results = run_application_benchmarks()
        
        # Compare rankings across applications
        compare_application_rankings(results)
        
        # Demonstrate scoring sensitivity
        demonstrate_scoring_sensitivity()
        
        print(f"\n{'='*80}")
        print("DEMO COMPLETE")
        print("=" * 80)
        print("\nKey Insights:")
        print("1. Different applications prioritize different metrics")
        print("2. Ranking changes significantly based on scoring weights")
        print("3. Some estimators are more versatile across applications")
        print("4. The parametrized scoring allows fine-tuning for specific needs")
        
        print("\nExample usage for BCI application:")
        print("  python run_benchmark.py --success-weight 0.4 --accuracy-weight 0.2 --speed-weight 0.3 --robustness-weight 0.1")
        
        print("\nExample usage for research application:")
        print("  python run_benchmark.py --success-weight 0.2 --accuracy-weight 0.4 --speed-weight 0.1 --robustness-weight 0.3")
        
    except Exception as e:
        print(f"Error running demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
