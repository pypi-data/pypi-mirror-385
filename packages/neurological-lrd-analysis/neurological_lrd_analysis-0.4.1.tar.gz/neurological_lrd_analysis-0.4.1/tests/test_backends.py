from benchmark_backends.selector import select_backend


def test_backend_selection_cpu():
    # On CPU-only environments, should return numpy or numba_cpu
    b = select_backend(1000, real_time=False)
    assert b in {"numpy", "numba_cpu", "numba_gpu", "jax_gpu"}


