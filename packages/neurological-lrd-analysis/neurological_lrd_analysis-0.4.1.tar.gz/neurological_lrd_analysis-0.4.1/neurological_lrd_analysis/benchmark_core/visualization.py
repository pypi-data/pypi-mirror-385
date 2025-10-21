"""
Focused visualization module for LRD estimator analysis.

This module provides targeted visualizations for the core goals of the library:
1. Estimation accuracy (bias, error, precision)
2. Uncertainty quantification (confidence intervals, coverage)
3. Efficiency analysis (computation time, memory usage)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from .runner import BenchmarkResult, analyze_benchmark_results


def create_accuracy_comparison_plot(results: List[BenchmarkResult], 
                                   save_path: Optional[str] = None) -> plt.Figure:
    """
    Create a focused plot comparing estimation accuracy across estimators.
    
    Parameters:
    -----------
    results : List[BenchmarkResult]
        Benchmark results
    save_path : str, optional
        Path to save the plot
        
    Returns:
    --------
    plt.Figure
        The created figure
    """
    # Analyze results
    analysis = analyze_benchmark_results(results)
    
    # Extract key accuracy metrics
    estimators = list(analysis.keys())
    biases = [analysis[est]['mean_bias'] for est in estimators]
    mae_values = [analysis[est]['mean_absolute_error'] for est in estimators]
    rmse_values = [analysis[est]['rmse'] for est in estimators]
    
    # Create subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Plot 1: Bias comparison
    bars1 = ax1.bar(range(len(estimators)), biases, color='skyblue', alpha=0.7)
    ax1.set_title('Estimation Bias by Estimator')
    ax1.set_xlabel('Estimator')
    ax1.set_ylabel('Mean Bias (Estimated - True Hurst)')
    ax1.set_xticks(range(len(estimators)))
    ax1.set_xticklabels(estimators, rotation=45, ha='right')
    ax1.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='Perfect Estimation')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, bias) in enumerate(zip(bars1, biases)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + (0.01 if height >= 0 else -0.03),
                f'{bias:.3f}', ha='center', va='bottom' if height >= 0 else 'top', fontsize=9)
    
    # Plot 2: Error comparison (MAE and RMSE)
    x = np.arange(len(estimators))
    width = 0.35
    
    bars2a = ax2.bar(x - width/2, mae_values, width, label='Mean Absolute Error', color='lightcoral', alpha=0.7)
    bars2b = ax2.bar(x + width/2, rmse_values, width, label='Root Mean Square Error', color='lightgreen', alpha=0.7)
    
    ax2.set_title('Estimation Error Comparison')
    ax2.set_xlabel('Estimator')
    ax2.set_ylabel('Error Magnitude')
    ax2.set_xticks(x)
    ax2.set_xticklabels(estimators, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars2a, bars2b]:
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def create_bias_distribution_plot(results: List[BenchmarkResult], 
                                save_path: Optional[str] = None) -> plt.Figure:
    """
    Create a violin plot showing the distribution of bias across estimators.
    
    Parameters:
    -----------
    results : List[BenchmarkResult]
        Benchmark results
    save_path : str, optional
        Path to save the plot
        
    Returns:
    --------
    plt.Figure
        The created figure
    """
    # Extract bias data by estimator
    bias_data = {}
    
    for result in results:
        estimator = result.estimator
        if result.bias is not None and not np.isnan(result.bias):
            if estimator not in bias_data:
                bias_data[estimator] = []
            bias_data[estimator].append(result.bias)
    
    # Create DataFrame for seaborn
    bias_list = []
    estimator_list = []
    
    for estimator, biases in bias_data.items():
        bias_list.extend(biases)
        estimator_list.extend([estimator] * len(biases))
    
    df = pd.DataFrame({'Estimator': estimator_list, 'Bias': bias_list})
    
    # Create violin plot
    fig, ax = plt.subplots(figsize=(14, 8))
    
    sns.violinplot(data=df, x='Estimator', y='Bias', ax=ax)
    ax.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='Perfect Estimation')
    ax.set_title('Bias Distribution Across Estimators')
    ax.set_xlabel('Estimator')
    ax.set_ylabel('Bias (Estimated - True Hurst)')
    ax.tick_params(axis='x', rotation=45)
    ax.legend()
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def create_error_vs_hurst_plot(results: List[BenchmarkResult], 
                              save_path: Optional[str] = None) -> plt.Figure:
    """
    Create a scatter plot showing error vs true Hurst exponent.
    
    Parameters:
    -----------
    results : List[BenchmarkResult]
        Benchmark results
    save_path : str, optional
        Path to save the plot
        
    Returns:
    --------
    plt.Figure
        The created figure
    """
    # Extract data
    estimators = set(result.estimator_name for result in results)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(estimators)))
    
    for i, estimator in enumerate(estimators):
        estimator_results = [r for r in results if r.estimator_name == estimator]
        
        hurst_values = []
        errors = []
        
        for result in estimator_results:
            if (result.true_hurst is not None and 
                result.absolute_error is not None and 
                not np.isnan(result.absolute_error)):
                hurst_values.append(result.true_hurst)
                errors.append(result.absolute_error)
        
        if hurst_values and errors:
            ax.scatter(hurst_values, errors, 
                      label=estimator, alpha=0.6, color=colors[i], s=50)
    
    ax.set_xlabel('True Hurst Exponent')
    ax.set_ylabel('Absolute Error')
    ax.set_title('Estimation Error vs True Hurst Exponent')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def create_efficiency_analysis_plot(results: List[BenchmarkResult], 
                                   save_path: Optional[str] = None) -> plt.Figure:
    """
    Create a focused plot for efficiency analysis (time vs accuracy trade-offs).
    
    Parameters:
    -----------
    results : List[BenchmarkResult]
        Benchmark results
    save_path : str, optional
        Path to save the plot
        
    Returns:
    --------
    plt.Figure
        The created figure
    """
    # Analyze results
    analysis = analyze_benchmark_results(results)
    
    # Extract efficiency metrics
    estimators = list(analysis.keys())
    mean_times = [analysis[est]['mean_computation_time'] for est in estimators]
    mae_values = [analysis[est]['mean_absolute_error'] for est in estimators]
    rmse_values = [analysis[est]['rmse'] for est in estimators]
    
    # Create subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Plot 1: Computation time comparison
    bars1 = ax1.bar(range(len(estimators)), mean_times, color='orange', alpha=0.7)
    ax1.set_title('Average Computation Time by Estimator')
    ax1.set_xlabel('Estimator')
    ax1.set_ylabel('Computation Time (seconds)')
    ax1.set_xticks(range(len(estimators)))
    ax1.set_xticklabels(estimators, rotation=45, ha='right')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, time in zip(bars1, mean_times):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height * 1.1,
                f'{time:.3f}s', ha='center', va='bottom', fontsize=9)
    
    # Plot 2: Time vs Accuracy scatter (MAE)
    ax2.scatter(mean_times, mae_values, s=100, alpha=0.7, c='red')
    ax2.set_xlabel('Computation Time (seconds)')
    ax2.set_ylabel('Mean Absolute Error')
    ax2.set_title('Efficiency Trade-off: Time vs MAE')
    ax2.set_xscale('log')
    ax2.grid(True, alpha=0.3)
    
    # Add estimator labels
    for i, est in enumerate(estimators):
        ax2.annotate(est, (mean_times[i], mae_values[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    # Plot 3: Time vs Accuracy scatter (RMSE)
    ax3.scatter(mean_times, rmse_values, s=100, alpha=0.7, c='blue')
    ax3.set_xlabel('Computation Time (seconds)')
    ax3.set_ylabel('Root Mean Square Error')
    ax3.set_title('Efficiency Trade-off: Time vs RMSE')
    ax3.set_xscale('log')
    ax3.grid(True, alpha=0.3)
    
    # Add estimator labels
    for i, est in enumerate(estimators):
        ax3.annotate(est, (mean_times[i], rmse_values[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    # Plot 4: Efficiency score (accuracy per unit time)
    efficiency_scores = [1/(mae * time) for mae, time in zip(mae_values, mean_times)]
    bars4 = ax4.bar(range(len(estimators)), efficiency_scores, color='green', alpha=0.7)
    ax4.set_title('Efficiency Score (1/(MAE × Time))')
    ax4.set_xlabel('Estimator')
    ax4.set_ylabel('Efficiency Score')
    ax4.set_xticks(range(len(estimators)))
    ax4.set_xticklabels(estimators, rotation=45, ha='right')
    ax4.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, score in zip(bars4, efficiency_scores):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{score:.1f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def create_uncertainty_quantification_plot(results: List[BenchmarkResult], 
                                          save_path: Optional[str] = None) -> plt.Figure:
    """
    Create a focused plot for uncertainty quantification analysis.
    
    Parameters:
    -----------
    results : List[BenchmarkResult]
        Benchmark results
    save_path : str, optional
        Path to save the plot
        
    Returns:
    --------
    plt.Figure
        The created figure
    """
    # Extract confidence interval data
    ci_data = {}
    
    for result in results:
        estimator = result.estimator
        if (result.confidence_interval is not None and 
            result.true_hurst is not None):
            
            if estimator not in ci_data:
                ci_data[estimator] = {'widths': [], 'coverage': [], 'standard_errors': []}
            
            ci_lower, ci_upper = result.confidence_interval
            ci_width = ci_upper - ci_lower
            coverage = 1 if ci_lower <= result.true_hurst <= ci_upper else 0
            
            ci_data[estimator]['widths'].append(ci_width)
            ci_data[estimator]['coverage'].append(coverage)
            
            if result.standard_error is not None and not np.isnan(result.standard_error):
                ci_data[estimator]['standard_errors'].append(result.standard_error)
    
    # Create subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    estimators = list(ci_data.keys())
    
    # Plot 1: Confidence interval widths
    widths = [np.mean(ci_data[est]['widths']) for est in estimators]
    bars1 = ax1.bar(range(len(estimators)), widths, color='lightblue', alpha=0.7)
    ax1.set_title('Average Confidence Interval Width')
    ax1.set_xlabel('Estimator')
    ax1.set_ylabel('Average CI Width')
    ax1.set_xticks(range(len(estimators)))
    ax1.set_xticklabels(estimators, rotation=45, ha='right')
    ax1.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, width in zip(bars1, widths):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{width:.3f}', ha='center', va='bottom', fontsize=9)
    
    # Plot 2: Coverage rates
    coverage_rates = [np.mean(ci_data[est]['coverage']) for est in estimators]
    bars2 = ax2.bar(range(len(estimators)), coverage_rates, color='lightgreen', alpha=0.7)
    ax2.set_title('Confidence Interval Coverage Rate')
    ax2.set_xlabel('Estimator')
    ax2.set_ylabel('Coverage Rate')
    ax2.set_xticks(range(len(estimators)))
    ax2.set_xticklabels(estimators, rotation=45, ha='right')
    ax2.axhline(y=0.95, color='red', linestyle='--', alpha=0.7, label='Target (95%)')
    ax2.set_ylim(0, 1)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, rate in zip(bars2, coverage_rates):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{rate:.2f}', ha='center', va='bottom', fontsize=9)
    
    # Plot 3: Standard errors
    std_errors = [np.mean(ci_data[est]['standard_errors']) if ci_data[est]['standard_errors'] else 0 
                  for est in estimators]
    bars3 = ax3.bar(range(len(estimators)), std_errors, color='lightcoral', alpha=0.7)
    ax3.set_title('Average Standard Error')
    ax3.set_xlabel('Estimator')
    ax3.set_ylabel('Average Standard Error')
    ax3.set_xticks(range(len(estimators)))
    ax3.set_xticklabels(estimators, rotation=45, ha='right')
    ax3.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, se in zip(bars3, std_errors):
        height = bar.get_height()
        if height > 0:
            ax3.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{se:.3f}', ha='center', va='bottom', fontsize=9)
    
    # Plot 4: CI Width vs Coverage scatter
    ax4.scatter(widths, coverage_rates, s=100, alpha=0.7, c='purple')
    ax4.set_xlabel('Average CI Width')
    ax4.set_ylabel('Coverage Rate')
    ax4.set_title('CI Width vs Coverage Trade-off')
    ax4.axhline(y=0.95, color='red', linestyle='--', alpha=0.7, label='Target Coverage')
    ax4.axvline(x=np.mean(widths), color='blue', linestyle='--', alpha=0.7, label='Mean Width')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Add estimator labels to scatter points
    for i, est in enumerate(estimators):
        ax4.annotate(est, (widths[i], coverage_rates[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def create_focused_analysis_report(results: List[BenchmarkResult], 
                                  output_dir: str = "./benchmark_plots") -> None:
    """
    Create a focused visualization report for LRD estimator analysis.
    
    Focuses on the core library goals:
    1. Estimation accuracy (bias, error, precision)
    2. Uncertainty quantification (confidence intervals, coverage)
    3. Efficiency analysis (time vs accuracy trade-offs)
    
    Parameters:
    -----------
    results : List[BenchmarkResult]
        Benchmark results
    output_dir : str
        Directory to save all plots
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating focused LRD analysis report in {output_dir}...")
    
    # Create focused plots aligned with library goals
    plots = [
        ("01_estimation_accuracy.png", create_accuracy_comparison_plot),
        ("02_uncertainty_quantification.png", create_uncertainty_quantification_plot),
        ("03_efficiency_analysis.png", create_efficiency_analysis_plot),
    ]
    
    for filename, plot_func in plots:
        print(f"Creating {filename}...")
        try:
            fig = plot_func(results, save_path=str(output_path / filename))
            plt.close(fig)
        except Exception as e:
            print(f"Warning: Could not create {filename}: {e}")
    
    print(f"Focused analysis report complete! Check {output_dir} for plots.")
    print("Report includes:")
    print("  - 01_estimation_accuracy.png: Bias and error analysis")
    print("  - 02_uncertainty_quantification.png: Confidence intervals and coverage")
    print("  - 03_efficiency_analysis.png: Time vs accuracy trade-offs")


def create_summary_dashboard(results: List[BenchmarkResult], 
                           save_path: Optional[str] = None) -> plt.Figure:
    """
    Create a summary dashboard with multiple subplots.
    
    Parameters:
    -----------
    results : List[BenchmarkResult]
        Benchmark results
    save_path : str, optional
        Path to save the plot
        
    Returns:
    --------
    plt.Figure
        The created figure
    """
    fig = plt.figure(figsize=(20, 12))
    
    # Create a 2x3 grid of subplots
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
    
    # Subplot 1: Performance heatmap (simplified)
    ax1 = fig.add_subplot(gs[0, 0])
    analysis = analyze_benchmark_results(results)
    estimators = list(analysis.keys())
    success_rates = [analysis[est]['success_rate'] for est in estimators]
    
    bars = ax1.bar(range(len(estimators)), success_rates)
    ax1.set_title('Success Rates')
    ax1.set_xticks(range(len(estimators)))
    ax1.set_xticklabels(estimators, rotation=45)
    ax1.set_ylabel('Success Rate')
    
    # Subplot 2: Mean bias
    ax2 = fig.add_subplot(gs[0, 1])
    mean_biases = [analysis[est]['mean_bias'] for est in estimators]
    bars = ax2.bar(range(len(estimators)), mean_biases)
    ax2.set_title('Mean Bias')
    ax2.set_xticks(range(len(estimators)))
    ax2.set_xticklabels(estimators, rotation=45)
    ax2.set_ylabel('Mean Bias')
    ax2.axhline(y=0, color='red', linestyle='--', alpha=0.7)
    
    # Subplot 3: Mean absolute error
    ax3 = fig.add_subplot(gs[0, 2])
    mean_errors = [analysis[est]['mean_absolute_error'] for est in estimators]
    bars = ax3.bar(range(len(estimators)), mean_errors)
    ax3.set_title('Mean Absolute Error')
    ax3.set_xticks(range(len(estimators)))
    ax3.set_xticklabels(estimators, rotation=45)
    ax3.set_ylabel('MAE')
    
    # Subplot 4: Computation time
    ax4 = fig.add_subplot(gs[1, 0])
    mean_times = [analysis[est]['mean_computation_time'] for est in estimators]
    bars = ax4.bar(range(len(estimators)), mean_times)
    ax4.set_title('Mean Computation Time')
    ax4.set_xticks(range(len(estimators)))
    ax4.set_xticklabels(estimators, rotation=45)
    ax4.set_ylabel('Time (seconds)')
    ax4.set_yscale('log')
    
    # Subplot 5: RMSE
    ax5 = fig.add_subplot(gs[1, 1])
    rmse_values = [analysis[est]['rmse'] for est in estimators]
    bars = ax5.bar(range(len(estimators)), rmse_values)
    ax5.set_title('Root Mean Square Error')
    ax5.set_xticks(range(len(estimators)))
    ax5.set_xticklabels(estimators, rotation=45)
    ax5.set_ylabel('RMSE')
    
    # Subplot 6: Significance rate
    ax6 = fig.add_subplot(gs[1, 2])
    sig_rates = [analysis[est]['significance_rate'] for est in estimators]
    bars = ax6.bar(range(len(estimators)), sig_rates)
    ax6.set_title('Significance Rate')
    ax6.set_xticks(range(len(estimators)))
    ax6.set_xticklabels(estimators, rotation=45)
    ax6.set_ylabel('Significance Rate')
    
    plt.suptitle('Hurst Exponent Estimation Performance Dashboard', fontsize=16)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig
