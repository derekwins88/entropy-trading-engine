from __future__ import annotations

import importlib


def xp():
    try:
        import cupy  # noqa: F401

        return importlib.import_module("cupy")
    except Exception:
        import numpy

        return numpy


def asarray(a):
    return xp().asarray(a)


def to_numpy(a):
    try:
        import cupy

        if isinstance(a, cupy.ndarray):
            return cupy.asnumpy(a)
    except Exception:
        pass
    import numpy as np

    return a if isinstance(a, np.ndarray) else np.asarray(a)
