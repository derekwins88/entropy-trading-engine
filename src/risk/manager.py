from __future__ import annotations

from dataclasses import dataclass

from entropy.analyzer import EntropySignal


@dataclass(frozen=True)
class PositionSize:
    fraction: float
    hedge: bool


class EntropyRiskManager:
    def __init__(self, max_position_size: float = 0.25, entropy_confidence_threshold: float = 0.85):
        self.max_position_size = float(max_position_size)
        self.entropy_confidence_threshold = float(entropy_confidence_threshold)

    def calculate_position_size(self, signal: EntropySignal, account_value: float) -> PositionSize:
        if signal.confidence < self.entropy_confidence_threshold:
            return PositionSize(0.0, hedge=False)
        frac = min(self.max_position_size, signal.confidence * self.max_position_size)
        hedge = bool(signal.np_wall)
        return PositionSize(frac, hedge)

    def should_execute_trade(self, signal: EntropySignal) -> bool:
        return signal.confidence >= self.entropy_confidence_threshold and (
            signal.np_wall or signal.no_recovery
        )
