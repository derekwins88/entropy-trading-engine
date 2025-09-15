from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass

import numpy as np
from proof.capsule import CapsuleModel, EntropySignalModel

from .metrics import rolling_delta_phi


@dataclass(frozen=True)
class EntropySignal:
    np_wall: bool
    no_recovery: bool
    delta_phi: float
    p_threshold: float
    np_threshold: float
    window: int
    confidence: float
    direction: int


class EntropyAnalyzer:
    NP_THRESHOLD = 0.09
    P_THRESHOLD = 0.045
    WINDOW_SIZE = 21

    def __init__(
        self,
        window: int | None = None,
        p_threshold: float | None = None,
        np_threshold: float | None = None,
    ):
        self.window = window or self.WINDOW_SIZE
        self.p_thresh = p_threshold if p_threshold is not None else self.P_THRESHOLD
        self.np_thresh = np_threshold if np_threshold is not None else self.NP_THRESHOLD

    def analyze_entropy_drift(self, prices: np.ndarray) -> EntropySignal:
        prices = np.asarray(prices, dtype=float)
        if prices.size < self.window:
            return EntropySignal(
                False, False, float("nan"), self.p_thresh, self.np_thresh, self.window, 0.0, 0
            )
        dphi_series = rolling_delta_phi(prices, self.window)
        dphi = float(dphi_series[-1])
        trail = dphi_series[-self.window :]
        np_wall = bool(dphi > self.np_thresh)
        finite = trail[np.isfinite(trail)]
        no_recovery = bool(finite.size > 0 and np.min(finite) >= self.p_thresh)
        x = np.arange(self.window, dtype=float)
        y = prices[-self.window :]
        slope = float(np.cov(x, y, bias=True)[0, 1] / (np.var(x) + 1e-12))
        direction = 1 if slope > 0 else (-1 if slope < 0 else 0)
        if math.isnan(dphi):
            conf = 0.0
        else:
            span = max(self.np_thresh - self.p_thresh, 1e-9)
            conf = float(np.clip((dphi - self.p_thresh) / span, 0.0, 1.0))
        return EntropySignal(
            np_wall, no_recovery, dphi, self.p_thresh, self.np_thresh, self.window, conf, direction
        )

    def generate_proof_capsule(
        self, signal: EntropySignal, *, inputs_fingerprint: str
    ) -> CapsuleModel:
        payload = {
            "np_wall": signal.np_wall,
            "no_recovery": signal.no_recovery,
            "delta_phi": signal.delta_phi,
            "p_threshold": signal.p_threshold,
            "np_threshold": signal.np_threshold,
            "window": signal.window,
            "confidence": signal.confidence,
            "direction": signal.direction,
        }
        sig_json = json.dumps(payload, sort_keys=True).encode("utf-8")
        signal_hash = hashlib.sha256(sig_json).hexdigest()
        statement = (
            "Under entropy dynamics with ΔΦ over the trailing window, "
            f"market enters NP-wall={signal.np_wall} with no_recovery={signal.no_recovery}. "
            "This trading decision is backed by a structured entropy claim (P≠NP analogy)."
        )
        sat_prov = {
            "system": "Derek-SAT",
            "schema": "trade-capsule-1.1.0",
            "claim": {
                "delta_phi": signal.delta_phi,
                "p_threshold": signal.p_threshold,
                "np_threshold": signal.np_threshold,
            },
            "verdict": "SAT" if signal.np_wall and signal.no_recovery else "UNDECIDED",
        }
        from time import time_ns

        return CapsuleModel(
            signal_hash=signal_hash,
            timestamp_ns=time_ns(),
            statement=statement,
            sat_provenance=sat_prov,
            inputs_fingerprint=inputs_fingerprint,
            signal=EntropySignalModel(**payload),
        )
