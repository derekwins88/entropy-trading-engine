from __future__ import annotations

import numpy as np


def delta_phi_from_window(prices: np.ndarray) -> float:
    if prices.size == 0:
        return float("nan")
    hi = float(np.max(prices))
    lo = float(np.min(prices))
    denom = max(abs(hi), 1e-9)
    return (hi - lo) / denom


def rolling_delta_phi(prices: np.ndarray, window: int) -> np.ndarray:
    n = prices.size
    out = np.full(n, np.nan, dtype=float)
    if n < window:
        return out
    for i in range(window - 1, n):
        w = prices[i - window + 1 : i + 1]
        hi = float(np.max(w))
        lo = float(np.min(w))
        out[i] = (hi - lo) / max(abs(hi), 1e-9)
    return out
