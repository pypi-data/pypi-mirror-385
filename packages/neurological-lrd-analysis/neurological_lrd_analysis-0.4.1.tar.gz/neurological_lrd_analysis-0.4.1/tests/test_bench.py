import numpy as np

from benchmark_core.generation import fbm_davies_harte, generate_grid
from benchmark_core.runner import BenchmarkConfig, run_benchmark_on_dataset


def test_fbm_generator_basic():
    x = fbm_davies_harte(512, 0.7, seed=0)
    assert len(x) == 512
    assert np.isfinite(x).all()


def test_benchmark_runs_end_to_end(tmp_path):
    dataset = generate_grid([0.5], [512], ["none"], seed=1)
    cfg = BenchmarkConfig(output_dir=str(tmp_path), true_hurst=None)
    rows = run_benchmark_on_dataset(dataset, cfg)
    assert len(rows) >= 1
    # Ensure at least one estimator returns a finite value
    assert any(np.isfinite(r.hurst_estimate) for r in rows)


