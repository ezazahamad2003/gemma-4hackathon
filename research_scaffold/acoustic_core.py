"""Core acoustic utilities and high-level interfaces for audio research."""

def framing(signal, frame_size=1024, hop=512):
    """Return simple frame indices for a 1-D signal placeholder."""
    n = len(signal)
    frames = []
    i = 0
    while i + frame_size <= n:
        frames.append((i, i + frame_size))
        i += hop
    return frames
