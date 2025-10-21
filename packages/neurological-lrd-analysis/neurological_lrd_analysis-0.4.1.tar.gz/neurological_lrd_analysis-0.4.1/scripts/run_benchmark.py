#!/usr/bin/env python3
"""
Biomedical Hurst Factory Benchmarking Script

This script demonstrates the enhanced benchmarking capabilities with comprehensive
statistical reporting including bias, error, confidence intervals, and p-values.

Usage:
    python run_benchmark.py [--hurst-values 0.3,0.5,0.7] [--lengths 512,1024] [--output-dir ./results]
"""

import argparse
import numpy as np
import pandas as pd
import time
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from neurological_lrd_analysis.benchmark_core.generation import generate_grid
from neurological_lrd_analysis.benchmark_core.runner import BenchmarkConfig, ScoringWeights, run_benchmark_on_dataset, analyze_benchmark_results, create_leaderboard


def main():
    """Main benchmarking function."""
    parser = argparse.ArgumentParser(description="Run enhanced benchmarking for Biomedical Hurst Factory")
    parser.add_argument("--hurst-values", type=str, default="0.3,0.5,0.7,0.8", 
                       help="Comma-separated Hurst values to test (default: 0.3,0.5,0.7,0.8)")
    parser.add_argument("--lengths", type=str, default="512,1024,2048", 
                       help="Comma-separated data lengths to test (default: 512,1024,2048)")
    parser.add_argument("--output-dir", type=str, default="./benchmark_results", 
                       help="Output directory for results (default: ./benchmark_results)")
    parser.add_argument("--bootstrap", type=int, default=100, 
                       help="Number of bootstrap samples (default: 100)")
    parser.add_argument("--contaminations", type=str, default="none,noise", 
                       help="Comma-separated contamination types (default: none,noise)")
    parser.add_argument("--verbose", action="store_true", 
                       help="Verbose output")
    parser.add_argument("--bayesian", action="store_true", 
                       help="Use Bayesian inference (NumPyro) instead of bootstrap")
    parser.add_argument("--num-samples", type=int, default=1000, 
                       help="Number of MCMC samples for Bayesian inference (default: 1000)")
    parser.add_argument("--num-warmup", type=int, default=500, 
                       help="Number of warmup samples for Bayesian inference (default: 500)")
    
    # Scoring weights
    parser.add_argument("--success-weight", type=float, default=0.3, 
                       help="Weight for success rate in scoring (default: 0.3)")
    parser.add_argument("--accuracy-weight", type=float, default=0.3, 
                       help="Weight for accuracy (MAE) in scoring (default: 0.3)")
    parser.add_argument("--speed-weight", type=float, default=0.2, 
                       help="Weight for speed in scoring (default: 0.2)")
    parser.add_argument("--robustness-weight", type=float, default=0.2, 
                       help="Weight for robustness in scoring (default: 0.2)")
    
    # Biomedical scenarios
    parser.add_argument("--biomedical-scenarios", type=str, default=None,
                       help="Comma-separated list of biomedical scenarios (eeg_rest,ecg_normal,etc.)")
    
    args = parser.parse_args()
    
    # Parse arguments
    hurst_values = [float(x.strip()) for x in args.hurst_values.split(',')]
    lengths = [int(x.strip()) for x in args.lengths.split(',')]
    contaminations = [x.strip() for x in args.contaminations.split(',')]
    
    # Parse biomedical scenarios
    biomedical_scenarios = None
    if args.biomedical_scenarios:
        biomedical_scenarios = [x.strip() for x in args.biomedical_scenarios.split(',')]
    
    print("Biomedical Hurst Factory Enhanced Benchmarking")
    print("=" * 60)
    print(f"Hurst values: {hurst_values}")
    print(f"Lengths: {lengths}")
    print(f"Contaminations: {contaminations}")
    if args.bayesian:
        print(f"Bayesian inference: {args.num_samples} samples, {args.num_warmup} warmup")
    else:
        print(f"Bootstrap samples: {args.bootstrap}")
    print(f"Output directory: {args.output_dir}")
    
    # Create scoring weights
    scoring_weights = ScoringWeights(
        success_rate=args.success_weight,
        accuracy=args.accuracy_weight,
        speed=args.speed_weight,
        robustness=args.robustness_weight
    )
    print(f"Scoring weights: Success={scoring_weights.success_rate:.1f}, "
          f"Accuracy={scoring_weights.accuracy:.1f}, "
          f"Speed={scoring_weights.speed:.1f}, "
          f"Robustness={scoring_weights.robustness:.1f}")
    
    # Generate test datasets
    print("\nGenerating test datasets...")
    datasets = generate_grid(
        hurst_values=hurst_values,
        lengths=lengths,
        contaminations=contaminations,
        contamination_level=0.1,
        biomedical_scenarios=biomedical_scenarios,
        seed=42
    )
    
    print(f"Generated {len(datasets)} test datasets")
    
    # Configure benchmark
    config = BenchmarkConfig(
        output_dir=args.output_dir,
        n_bootstrap=args.bootstrap,
        confidence_level=0.95,
        save_results=True,
        verbose=args.verbose,
        use_bayesian=args.bayesian,
        num_samples=args.num_samples,
        num_warmup=args.num_warmup,
        scoring_weights=scoring_weights
    )
    
    # Run benchmark
    if args.bayesian:
        print(f"\nRunning benchmark with Bayesian inference ({config.num_samples} samples)...")
    else:
        print(f"\nRunning benchmark with {config.n_bootstrap} bootstrap samples...")
    start_time = time.time()
    
    results = run_benchmark_on_dataset(datasets, config)
    
    benchmark_time = time.time() - start_time
    print(f"Benchmark completed in {benchmark_time:.2f} seconds")
    print(f"Total results: {len(results)}")
    
    # Analyze results
    print("\nAnalyzing results...")
    analysis = analyze_benchmark_results(results)
    leaderboard = create_leaderboard(results, config.scoring_weights)
    
    # Display summary
    print("\n" + "=" * 80)
    print("BENCHMARK SUMMARY")
    print("=" * 80)
    
    total_runs = len(results)
    successful_runs = sum(1 for r in results if r.convergence_flag)
    print(f"Total runs: {total_runs}")
    print(f"Successful runs: {successful_runs} ({successful_runs/total_runs:.1%})")
    print(f"Failed runs: {total_runs - successful_runs}")
    
    # Statistical metrics summary
    valid_results = [r for r in results if r.convergence_flag and r.bias is not None]
    if valid_results:
        biases = [r.bias for r in valid_results]
        errors = [r.absolute_error for r in valid_results]
        
        print(f"\nStatistical Metrics Summary:")
        print(f"  Mean bias: {np.mean(biases):.4f}")
        print(f"  Std bias: {np.std(biases):.4f}")
        print(f"  Mean absolute error: {np.mean(errors):.4f}")
        print(f"  RMSE: {np.sqrt(np.mean([b**2 for b in biases])):.4f}")
    
    # Display leaderboard
    print(f"\n" + "=" * 80)
    print("ESTIMATOR LEADERBOARD")
    print("=" * 80)
    print(leaderboard.to_string(index=False))
    
    # Save results
    results_dir = Path(args.output_dir)
    leaderboard_path = results_dir / 'leaderboard.csv'
    leaderboard.to_csv(leaderboard_path, index=False)
    print(f"\nResults saved to: {results_dir}")
    print(f"Leaderboard saved to: {leaderboard_path}")
    
    print("\nBenchmark completed successfully!")


if __name__ == "__main__":
    main()
