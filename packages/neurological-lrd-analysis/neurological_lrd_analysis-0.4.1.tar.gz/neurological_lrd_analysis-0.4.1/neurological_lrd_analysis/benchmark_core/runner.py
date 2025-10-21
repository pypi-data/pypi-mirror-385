"""
Benchmark runner for Hurst exponent estimation methods.

This module provides functionality to run benchmarks on generated datasets
and collect results for performance evaluation.
"""

import time
import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import numpy as np
import pandas as pd

from .generation import TimeSeriesSample
from ..benchmark_registry.registry import get_registry, EstimatorResult


@dataclass
class ScoringWeights:
    """Weights for different performance metrics in the scoring function."""
    success_rate: float = 0.3
    accuracy: float = 0.3  # Based on MAE (lower is better)
    speed: float = 0.2     # Based on computation time (lower is better)
    robustness: float = 0.2  # Based on consistency across conditions
    
    def __post_init__(self):
        """Ensure weights sum to 1.0."""
        total = self.success_rate + self.accuracy + self.speed + self.robustness
        if abs(total - 1.0) > 1e-6:
            # Normalize weights
            self.success_rate /= total
            self.accuracy /= total
            self.speed /= total
            self.robustness /= total


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark runs."""
    output_dir: str
    true_hurst: Optional[float] = None
    n_bootstrap: int = 100
    confidence_level: float = 0.95
    random_state: Optional[int] = None
    estimators: Optional[List[str]] = None
    save_results: bool = True
    verbose: bool = False
    
    # Bayesian inference parameters
    use_bayesian: bool = False
    num_samples: int = 1000
    num_warmup: int = 500
    
    # Scoring weights for leaderboard ranking
    scoring_weights: Optional[ScoringWeights] = None
    
    def __post_init__(self):
        """Initialize default scoring weights if not provided."""
        if self.scoring_weights is None:
            self.scoring_weights = ScoringWeights()


@dataclass
class BenchmarkResult:
    """Result from a single estimator run."""
    estimator: str
    hurst_estimate: float
    true_hurst: Optional[float] = None
    computation_time: float = 0.0
    convergence_flag: bool = True
    additional_metrics: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    # Statistical metrics
    bias: Optional[float] = None
    absolute_error: Optional[float] = None
    relative_error: Optional[float] = None
    confidence_interval: Optional[tuple] = None
    p_value: Optional[float] = None
    standard_error: Optional[float] = None


def run_benchmark_on_dataset(samples: List[TimeSeriesSample], 
                           config: BenchmarkConfig) -> List[BenchmarkResult]:
    """
    Run benchmark on a dataset of time series samples.
    
    Parameters:
    -----------
    samples : List[TimeSeriesSample]
        List of time series samples to benchmark
    config : BenchmarkConfig
        Benchmark configuration
        
    Returns:
    --------
    List[BenchmarkResult]
        List of benchmark results
    """
    # Get available estimators
    registry = get_registry()
    
    # Filter estimators if specified
    if config.estimators is not None:
        available_estimators = [est for est in registry if est.name in config.estimators]
    else:
        available_estimators = registry
    
    if not available_estimators:
        raise ValueError("No estimators available for benchmarking")
    
    results = []
    
    for sample in samples:
        if config.verbose:
            print(f"Processing sample: H={sample.true_hurst}, "
                  f"length={sample.length}, contamination={sample.contamination}")
        
        for estimator in available_estimators:
            try:
                start_time = time.time()
                
                # Run estimation
                if config.use_bayesian:
                    # Use Bayesian inference
                    estimator_result = estimator.estimate(
                        sample.data,
                        confidence_method="bayesian",
                        num_samples=config.num_samples,
                        num_warmup=config.num_warmup,
                        confidence_level=config.confidence_level,
                        random_state=config.random_state
                    )
                else:
                    # Use bootstrap inference
                    estimator_result = estimator.estimate(
                        sample.data,
                        n_bootstrap=config.n_bootstrap,
                        confidence_level=config.confidence_level,
                        random_state=config.random_state
                    )
                
                computation_time = time.time() - start_time
                
                # Compute statistical metrics
                bias = None
                absolute_error = None
                relative_error = None
                p_value = None
                standard_error = None
                confidence_interval = None
                
                if sample.true_hurst is not None and not np.isnan(estimator_result.hurst_estimate):
                    bias = estimator_result.hurst_estimate - sample.true_hurst
                    absolute_error = abs(bias)
                    relative_error = absolute_error / sample.true_hurst if sample.true_hurst != 0 else None
                    
                    # Get confidence interval and p-value from additional metrics
                    if 'confidence_interval' in estimator_result.additional_metrics:
                        confidence_interval = estimator_result.additional_metrics['confidence_interval']
                    if 'regression_p_value' in estimator_result.additional_metrics:
                        p_value = estimator_result.additional_metrics['regression_p_value']
                    if 'regression_std_error' in estimator_result.additional_metrics:
                        standard_error = estimator_result.additional_metrics['regression_std_error']
                
                # Create benchmark result
                result = BenchmarkResult(
                    estimator=estimator.name,
                    hurst_estimate=estimator_result.hurst_estimate,
                    true_hurst=sample.true_hurst,
                    computation_time=computation_time,
                    convergence_flag=estimator_result.convergence_flag,
                    additional_metrics=estimator_result.additional_metrics,
                    bias=bias,
                    absolute_error=absolute_error,
                    relative_error=relative_error,
                    confidence_interval=confidence_interval,
                    p_value=p_value,
                    standard_error=standard_error
                )
                
                results.append(result)
                
            except Exception as e:
                # Record failed estimation
                result = BenchmarkResult(
                    estimator=estimator.name,
                    hurst_estimate=np.nan,
                    true_hurst=sample.true_hurst,
                    computation_time=0.0,
                    convergence_flag=False,
                    error_message=str(e)
                )
                results.append(result)
                
                if config.verbose:
                    print(f"  {estimator.name} failed: {e}")
    
    # Save results if requested
    if config.save_results:
        save_benchmark_results(results, config)
    
    return results


def save_benchmark_results(results: List[BenchmarkResult], 
                          config: BenchmarkConfig,
                          create_visualizations: bool = True) -> None:
    """
    Save benchmark results to files.
    
    Parameters:
    -----------
    results : List[BenchmarkResult]
        Benchmark results to save
    config : BenchmarkConfig
        Benchmark configuration
    create_visualizations : bool
        Whether to create visualization plots
    """
    os.makedirs(config.output_dir, exist_ok=True)
    
    # Convert to DataFrame
    data = []
    for result in results:
        row = {
            'estimator': result.estimator,
            'hurst_estimate': result.hurst_estimate,
            'true_hurst': result.true_hurst,
            'computation_time': result.computation_time,
            'convergence_flag': result.convergence_flag,
            'error_message': result.error_message,
            # Statistical metrics
            'bias': result.bias,
            'absolute_error': result.absolute_error,
            'relative_error': result.relative_error,
            'confidence_interval_lower': result.confidence_interval[0] if result.confidence_interval else None,
            'confidence_interval_upper': result.confidence_interval[1] if result.confidence_interval else None,
            'p_value': result.p_value,
            'standard_error': result.standard_error
        }
        
        # Add additional metrics
        for key, value in result.additional_metrics.items():
            row[f'metric_{key}'] = value
        
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # Save as CSV
    csv_path = os.path.join(config.output_dir, 'benchmark_results.csv')
    df.to_csv(csv_path, index=False)
    
    # Save summary statistics
    summary_path = os.path.join(config.output_dir, 'benchmark_summary.txt')
    with open(summary_path, 'w') as f:
        f.write("Benchmark Summary\n")
        f.write("================\n\n")
        
        # Overall statistics
        f.write(f"Total runs: {len(results)}\n")
        f.write(f"Successful runs: {sum(1 for r in results if r.convergence_flag)}\n")
        f.write(f"Failed runs: {sum(1 for r in results if not r.convergence_flag)}\n\n")
        
        # Per-estimator statistics
        estimators = set(r.estimator for r in results)
        for estimator in sorted(estimators):
            estimator_results = [r for r in results if r.estimator == estimator]
            successful = [r for r in estimator_results if r.convergence_flag]
            
            f.write(f"{estimator}:\n")
            f.write(f"  Total runs: {len(estimator_results)}\n")
            f.write(f"  Successful: {len(successful)}\n")
            f.write(f"  Success rate: {len(successful)/len(estimator_results):.2%}\n")
            
            if successful:
                estimates = [r.hurst_estimate for r in successful if not np.isnan(r.hurst_estimate)]
                biases = [r.bias for r in successful if r.bias is not None and not np.isnan(r.bias)]
                errors = [r.absolute_error for r in successful if r.absolute_error is not None and not np.isnan(r.absolute_error)]
                p_values = [r.p_value for r in successful if r.p_value is not None and not np.isnan(r.p_value)]
                
                if estimates:
                    f.write(f"  Mean estimate: {np.mean(estimates):.4f}\n")
                    f.write(f"  Std estimate: {np.std(estimates):.4f}\n")
                    f.write(f"  Mean computation time: {np.mean([r.computation_time for r in successful]):.4f}s\n")
                    
                    if biases:
                        f.write(f"  Mean bias: {np.mean(biases):.4f}\n")
                        f.write(f"  Std bias: {np.std(biases):.4f}\n")
                        f.write(f"  Mean absolute error: {np.mean(errors):.4f}\n")
                        f.write(f"  RMSE: {np.sqrt(np.mean([b**2 for b in biases])):.4f}\n")
                    
                    if p_values:
                        significant = sum(1 for p in p_values if p < 0.05)
                        f.write(f"  Significant estimates (p<0.05): {significant}/{len(p_values)} ({significant/len(p_values):.1%})\n")
                    
                    # Add confidence interval information
                    confidence_intervals = [r.confidence_interval for r in successful if r.confidence_interval is not None]
                    if confidence_intervals:
                        ci_lowers = [ci[0] for ci in confidence_intervals]
                        ci_uppers = [ci[1] for ci in confidence_intervals]
                        ci_widths = [ci[1] - ci[0] for ci in confidence_intervals]
                        f.write(f"  Mean confidence interval: [{np.mean(ci_lowers):.4f}, {np.mean(ci_uppers):.4f}]\n")
                        f.write(f"  Mean CI width: {np.mean(ci_widths):.4f}\n")
                        f.write(f"  Std CI width: {np.std(ci_widths):.4f}\n")
            f.write("\n")
    
    # Create visualizations if requested
    if create_visualizations:
        try:
            from .visualization import create_focused_analysis_report
            print("Creating focused LRD analysis visualizations...")
            create_focused_analysis_report(results, config.output_dir)
        except ImportError as e:
            print(f"Warning: Could not create visualizations: {e}")
        except Exception as e:
            print(f"Warning: Error creating visualizations: {e}")


def calculate_estimator_score(analysis: Dict[str, Any], 
                             estimator: str, 
                             weights: ScoringWeights) -> float:
    """
    Calculate a parametrized score for an estimator based on performance metrics.
    
    Parameters:
    -----------
    analysis : Dict[str, Any]
        Analysis results from analyze_benchmark_results
    estimator : str
        Name of the estimator
    weights : ScoringWeights
        Weights for different metrics
        
    Returns:
    --------
    float
        Overall score (higher is better)
    """
    if estimator not in analysis:
        return 0.0
    
    est_data = analysis[estimator]
    
    # Success rate component (0-1, higher is better)
    success_rate_score = est_data.get('success_rate', 0.0)
    
    # Accuracy component (based on MAE, lower is better, so invert)
    mae = est_data.get('mean_absolute_error', np.inf)
    if mae == 0:
        accuracy_score = 1.0
    else:
        # Normalize MAE to 0-1 range, then invert (lower MAE = higher score)
        # Use exponential decay: score = exp(-mae/0.5) for reasonable scaling
        accuracy_score = np.exp(-mae / 0.5)
    
    # Speed component (based on computation time, lower is better, so invert)
    mean_time = est_data.get('mean_computation_time', np.inf)
    if mean_time == 0:
        speed_score = 1.0
    else:
        # Normalize time to 0-1 range, then invert (lower time = higher score)
        # Use exponential decay: score = exp(-time/1.0) for reasonable scaling
        speed_score = np.exp(-mean_time / 1.0)
    
    # Robustness component (based on consistency across conditions)
    # Use coefficient of variation of bias as robustness measure
    std_bias = est_data.get('std_bias', 0.0)
    mean_bias = abs(est_data.get('mean_bias', 0.0))
    
    if mean_bias == 0:
        robustness_score = 1.0
    else:
        cv = std_bias / mean_bias  # Coefficient of variation
        # Lower CV = higher robustness score
        robustness_score = np.exp(-cv / 2.0)  # Reasonable scaling
    
    # Calculate weighted score
    total_score = (weights.success_rate * success_rate_score +
                   weights.accuracy * accuracy_score +
                   weights.speed * speed_score +
                   weights.robustness * robustness_score)
    
    return total_score


def analyze_benchmark_results(results: List[BenchmarkResult]) -> Dict[str, Any]:
    """
    Analyze benchmark results and compute performance metrics.
    
    Parameters:
    -----------
    results : List[BenchmarkResult]
        Benchmark results to analyze
        
    Returns:
    --------
    Dict[str, Any]
        Analysis results
    """
    analysis = {}
    
    # Group by estimator
    estimators = set(r.estimator for r in results)
    
    for estimator in estimators:
        estimator_results = [r for r in results if r.estimator == estimator]
        successful = [r for r in estimator_results if r.convergence_flag and not np.isnan(r.hurst_estimate)]
        
        if not successful:
            analysis[estimator] = {
                'success_rate': 0.0,
                'mean_bias': np.nan,
                'std_bias': np.nan,
                'mean_absolute_error': np.nan,
                'rmse': np.nan,
                'mean_relative_error': np.nan,
                'mean_standard_error': np.nan,
                'significance_rate': np.nan,
                'mean_computation_time': np.nan,
                'mean_ci_lower': np.nan,
                'mean_ci_upper': np.nan,
                'mean_ci_width': np.nan,
                'std_ci_width': np.nan,
                'n_successful': 0,
                'n_total': len(estimator_results),
                'n_with_p_values': 0,
                'n_significant': 0
            }
            continue
        
        # Compute metrics
        estimates = [r.hurst_estimate for r in successful]
        biases = [r.bias for r in successful if r.bias is not None and not np.isnan(r.bias)]
        errors = [r.absolute_error for r in successful if r.absolute_error is not None and not np.isnan(r.absolute_error)]
        relative_errors = [r.relative_error for r in successful if r.relative_error is not None and not np.isnan(r.relative_error)]
        p_values = [r.p_value for r in successful if r.p_value is not None and not np.isnan(r.p_value)]
        standard_errors = [r.standard_error for r in successful if r.standard_error is not None and not np.isnan(r.standard_error)]
        
        # Confidence interval metrics
        confidence_intervals = [r.confidence_interval for r in successful if r.confidence_interval is not None]
        ci_lowers = [ci[0] for ci in confidence_intervals]
        ci_uppers = [ci[1] for ci in confidence_intervals]
        ci_widths = [ci[1] - ci[0] for ci in confidence_intervals]
        
        success_rate = len(successful) / len(estimator_results)
        mean_computation_time = np.mean([r.computation_time for r in successful])
        
        # Statistical metrics
        mean_bias = np.mean(biases) if biases else np.nan
        std_bias = np.std(biases) if biases else np.nan
        mean_absolute_error = np.mean(errors) if errors else np.nan
        rmse = np.sqrt(np.mean([b**2 for b in biases])) if biases else np.nan
        mean_relative_error = np.mean(relative_errors) if relative_errors else np.nan
        mean_standard_error = np.mean(standard_errors) if standard_errors else np.nan
        
        # Significance analysis
        significant_count = sum(1 for p in p_values if p < 0.05) if p_values else 0
        significance_rate = significant_count / len(p_values) if p_values else np.nan
        
        # Confidence interval analysis
        mean_ci_lower = np.mean(ci_lowers) if ci_lowers else np.nan
        mean_ci_upper = np.mean(ci_uppers) if ci_uppers else np.nan
        mean_ci_width = np.mean(ci_widths) if ci_widths else np.nan
        std_ci_width = np.std(ci_widths) if ci_widths else np.nan
        
        analysis[estimator] = {
            'success_rate': success_rate,
            'mean_bias': mean_bias,
            'std_bias': std_bias,
            'mean_absolute_error': mean_absolute_error,
            'rmse': rmse,
            'mean_relative_error': mean_relative_error,
            'mean_standard_error': mean_standard_error,
            'significance_rate': significance_rate,
            'mean_computation_time': mean_computation_time,
            'mean_ci_lower': mean_ci_lower,
            'mean_ci_upper': mean_ci_upper,
            'mean_ci_width': mean_ci_width,
            'std_ci_width': std_ci_width,
            'n_successful': len(successful),
            'n_total': len(estimator_results),
            'n_with_p_values': len(p_values),
            'n_significant': significant_count
        }
    
    return analysis


def create_leaderboard(results: List[BenchmarkResult], 
                       weights: Optional[ScoringWeights] = None) -> pd.DataFrame:
    """
    Create a leaderboard from benchmark results using parametrized scoring.
    
    Parameters:
    -----------
    results : List[BenchmarkResult]
        Benchmark results
    weights : ScoringWeights, optional
        Weights for scoring function. If None, uses default weights.
        
    Returns:
    --------
    pd.DataFrame
        Leaderboard DataFrame sorted by overall score
    """
    analysis = analyze_benchmark_results(results)
    
    if weights is None:
        weights = ScoringWeights()
    
    leaderboard_data = []
    for estimator, metrics in analysis.items():
        # Calculate overall score
        overall_score = calculate_estimator_score(analysis, estimator, weights)
        
        # Format confidence interval
        ci_str = "N/A"
        if not np.isnan(metrics['mean_ci_lower']) and not np.isnan(metrics['mean_ci_upper']):
            ci_str = f"[{metrics['mean_ci_lower']:.4f}, {metrics['mean_ci_upper']:.4f}]"
        
        leaderboard_data.append({
            'Overall Score': overall_score,
            'Estimator': estimator,
            'Success Rate': f"{metrics['success_rate']:.2%}",
            'Mean Bias': f"{metrics['mean_bias']:.4f}" if not np.isnan(metrics['mean_bias']) else "N/A",
            'Std Bias': f"{metrics['std_bias']:.4f}" if not np.isnan(metrics['std_bias']) else "N/A",
            'Mean Absolute Error': f"{metrics['mean_absolute_error']:.4f}" if not np.isnan(metrics['mean_absolute_error']) else "N/A",
            'RMSE': f"{metrics['rmse']:.4f}" if not np.isnan(metrics['rmse']) else "N/A",
            'Mean Relative Error': f"{metrics['mean_relative_error']:.2%}" if not np.isnan(metrics['mean_relative_error']) else "N/A",
            'Mean Standard Error': f"{metrics['mean_standard_error']:.4f}" if not np.isnan(metrics['mean_standard_error']) else "N/A",
            '95% CI': ci_str,
            'Mean CI Width': f"{metrics['mean_ci_width']:.4f}" if not np.isnan(metrics['mean_ci_width']) else "N/A",
            'Significance Rate': f"{metrics['significance_rate']:.2%}" if not np.isnan(metrics['significance_rate']) else "N/A",
            'Mean Time (s)': f"{metrics['mean_computation_time']:.4f}",
            'Successful Runs': metrics['n_successful'],
            'Total Runs': metrics['n_total'],
            'Significant': metrics['n_significant']
        })
    
    df = pd.DataFrame(leaderboard_data)
    
    # Sort by overall score (higher is better)
    df = df.sort_values('Overall Score', ascending=False)
    
    return df

