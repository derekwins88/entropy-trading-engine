import numpy as np
from entropy.metrics import delta_phi_from_window, rolling_delta_phi


def test_delta_phi_basic():
    w = np.array([1, 2, 3, 4, 5], dtype=float)
    d = delta_phi_from_window(w)
    assert 0 < d <= 1.0


def test_rolling_has_nans_then_values():
    x = np.linspace(100, 101, 50)
    r = rolling_delta_phi(x, 21)
    assert np.isnan(r[:20]).all()
    assert np.isfinite(r[20:]).all()
