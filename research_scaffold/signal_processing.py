"""Signal processing primitives for experiments."""

def normalize(samples):
    """Normalize int16 samples to float32 in [-1, 1]."""
    if not samples:
        return []
    mx = max(abs(x) for x in samples)
    if mx == 0:
        return [0.0 for _ in samples]
    return [float(x) / mx for x in samples]
