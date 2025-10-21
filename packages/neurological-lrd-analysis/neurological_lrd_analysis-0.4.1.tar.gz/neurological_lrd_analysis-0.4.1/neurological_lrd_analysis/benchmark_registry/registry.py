"""
Registry for Hurst exponent estimation methods.

This module provides a registry system for managing and accessing different
Hurst exponent estimation methods.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union
import numpy as np

from ..biomedical_hurst_factory import (
    BiomedicalHurstEstimatorFactory, 
    EstimatorType, 
    ConfidenceMethod,
    HurstResult
)


@dataclass
class EstimatorResult:
    """Result from an estimator run."""
    hurst_estimate: float
    convergence_flag: bool
    computation_time: float
    additional_metrics: Dict[str, Any]
    error_message: Optional[str] = None


class BaseEstimator(ABC):
    """Base class for all Hurst exponent estimators."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def estimate(self, data: np.ndarray, **kwargs) -> EstimatorResult:
        """Estimate Hurst exponent from data."""
        pass


class FactoryEstimator(BaseEstimator):
    """Wrapper for estimators from the biomedical factory."""
    
    def __init__(self, name: str, factory_method: EstimatorType):
        super().__init__(name)
        self.factory_method = factory_method
        self.factory = BiomedicalHurstEstimatorFactory()
    
    def estimate(self, data: np.ndarray, **kwargs) -> EstimatorResult:
        """Estimate using the biomedical factory."""
        try:
            start_time = time.time()
            
            # Extract confidence method from kwargs or use default
            confidence_method = kwargs.pop('confidence_method', ConfidenceMethod.BOOTSTRAP)
            if isinstance(confidence_method, str):
                confidence_method = ConfidenceMethod(confidence_method)
            
            result = self.factory.estimate(
                data, 
                method=self.factory_method,
                confidence_method=confidence_method,
                preprocess=False,  # Skip preprocessing for benchmarking
                assess_quality=False,  # Skip quality assessment for benchmarking
                **kwargs
            )
            
            computation_time = time.time() - start_time
            
            return EstimatorResult(
                hurst_estimate=result.hurst_estimate,
                convergence_flag=result.convergence_flag,
                computation_time=computation_time,
                additional_metrics={
                    'regression_r_squared': result.regression_r_squared,
                    'scaling_range': result.scaling_range,
                    'data_quality_score': result.data_quality_score,
                    'confidence_interval': result.confidence_interval,
                    'regression_p_value': result.regression_r_squared,  # Use R² as proxy for p-value
                    'regression_std_error': result.standard_error,
                    # Include all additional metrics from the result
                    **result.additional_metrics
                }
            )
            
        except Exception as e:
            return EstimatorResult(
                hurst_estimate=np.nan,
                convergence_flag=False,
                computation_time=0.0,
                additional_metrics={},
                error_message=str(e)
            )


class DFAEstimator(FactoryEstimator):
    """DFA estimator."""
    def __init__(self):
        super().__init__("DFA", EstimatorType.DFA)


class HiguchiEstimator(FactoryEstimator):
    """Higuchi estimator."""
    def __init__(self):
        super().__init__("Higuchi", EstimatorType.HIGUCHI)


class PeriodogramEstimator(FactoryEstimator):
    """Periodogram estimator."""
    def __init__(self):
        super().__init__("Periodogram", EstimatorType.PERIODOGRAM)


class RSAnalysisEstimator(FactoryEstimator):
    """R/S Analysis estimator."""
    def __init__(self):
        super().__init__("R/S", EstimatorType.RS_ANALYSIS)


class GPHEstimator(FactoryEstimator):
    """GPH estimator."""
    def __init__(self):
        super().__init__("GPH", EstimatorType.GPH)


class WhittleMLEEstimator(FactoryEstimator):
    """Local Whittle MLE estimator."""
    def __init__(self):
        super().__init__("Local-Whittle", EstimatorType.WHITTLE_MLE)


class GHEEstimator(FactoryEstimator):
    """Generalized Hurst Exponent estimator."""
    def __init__(self):
        super().__init__("GHE", EstimatorType.GENERALIZED_HURST)


class MFDFAEstimator(FactoryEstimator):
    """MFDFA estimator."""
    def __init__(self):
        super().__init__("MFDFA(q=2)", EstimatorType.MFDFA)


class MFDMAEstimator(FactoryEstimator):
    """MF-DMA estimator."""
    def __init__(self):
        super().__init__("MF-DMA(q=2)", EstimatorType.MF_DMA)


class DWTLogscaleEstimator(FactoryEstimator):
    """DWT Logscale estimator."""
    def __init__(self):
        super().__init__("DWT-Logscale", EstimatorType.DWT)


class AbryVeitchEstimator(FactoryEstimator):
    """Abry-Veitch estimator."""
    def __init__(self):
        super().__init__("Abry-Veitch", EstimatorType.ABRY_VEITCH)


class NDWTLogscaleEstimator(FactoryEstimator):
    """NDWT Logscale estimator."""
    def __init__(self):
        super().__init__("NDWT-Logscale", EstimatorType.NDWT)


# Registry of available estimators
_ESTIMATORS: List[BaseEstimator] = [
    DFAEstimator(),
    HiguchiEstimator(),
    PeriodogramEstimator(),
    RSAnalysisEstimator(),
    GPHEstimator(),
    WhittleMLEEstimator(),
    GHEEstimator(),
    MFDFAEstimator(),
    MFDMAEstimator(),
    DWTLogscaleEstimator(),
    AbryVeitchEstimator(),
    NDWTLogscaleEstimator(),
]


def get_registry() -> List[BaseEstimator]:
    """Get the list of available estimators."""
    return _ESTIMATORS.copy()


def register_estimator(estimator: BaseEstimator) -> None:
    """Register a new estimator."""
    _ESTIMATORS.append(estimator)


def get_estimator_by_name(name: str) -> Optional[BaseEstimator]:
    """Get an estimator by name."""
    for estimator in _ESTIMATORS:
        if estimator.name == name:
            return estimator
    return None


def list_estimator_names() -> List[str]:
    """List all available estimator names."""
    return [estimator.name for estimator in _ESTIMATORS]


def get_estimators_by_category(category: str) -> List[BaseEstimator]:
    """Get estimators by category."""
    # This is a simplified categorization
    # In a full implementation, estimators would have category attributes
    
    temporal_estimators = ["DFA", "Higuchi", "R/S", "GHE", "MFDFA(q=2)", "MF-DMA(q=2)"]
    spectral_estimators = ["Periodogram", "GPH", "Local-Whittle"]
    wavelet_estimators = ["DWT-Logscale", "Abry-Veitch", "NDWT-Logscale"]
    
    if category.lower() == "temporal":
        return [est for est in _ESTIMATORS if est.name in temporal_estimators]
    elif category.lower() == "spectral":
        return [est for est in _ESTIMATORS if est.name in spectral_estimators]
    elif category.lower() == "wavelet":
        return [est for est in _ESTIMATORS if est.name in wavelet_estimators]
    else:
        return _ESTIMATORS.copy()


def benchmark_estimator(estimator: BaseEstimator, 
                       data: np.ndarray,
                       n_runs: int = 5) -> Dict[str, Any]:
    """
    Benchmark an estimator on given data.
    
    Parameters:
    -----------
    estimator : BaseEstimator
        Estimator to benchmark
    data : np.ndarray
        Data to test on
    n_runs : int
        Number of runs for timing
        
    Returns:
    --------
    Dict[str, Any]
        Benchmark results
    """
    results = []
    
    for _ in range(n_runs):
        result = estimator.estimate(data)
        results.append(result)
    
    # Compute statistics
    estimates = [r.hurst_estimate for r in results if r.convergence_flag]
    times = [r.computation_time for r in results]
    
    benchmark_results = {
        'estimator_name': estimator.name,
        'n_runs': n_runs,
        'success_rate': sum(1 for r in results if r.convergence_flag) / n_runs,
        'mean_estimate': np.mean(estimates) if estimates else np.nan,
        'std_estimate': np.std(estimates) if estimates else np.nan,
        'mean_time': np.mean(times),
        'std_time': np.std(times),
        'min_time': np.min(times),
        'max_time': np.max(times)
    }
    
    return benchmark_results
