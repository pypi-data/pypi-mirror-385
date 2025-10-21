from benchmark_registry.registry import get_registry


def test_registry_has_12():
    regs = get_registry()
    # exactly 12 built-ins (plugins may add more; allow >= 12)
    assert len(regs) >= 12
    names = {r.name for r in regs}
    required = {
        "DFA", "Higuchi", "R/S",
        "Periodogram", "GPH", "Local-Whittle",
        "GHE", "MF-DMA(q=2)", "MFDFA(q=2)",
        "DWT-Logscale", "Abry-Veitch", "NDWT-Logscale",
    }
    assert required.issubset(names)


