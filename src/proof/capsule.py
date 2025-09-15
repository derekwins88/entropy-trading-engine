from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EntropySignalModel(BaseModel):
    np_wall: bool
    no_recovery: bool
    delta_phi: float
    p_threshold: float
    np_threshold: float
    window: int
    confidence: float
    direction: int


class CapsuleModel(BaseModel):
    schema_version: str = Field(default="trade-capsule-1.1.0")
    signal_hash: str
    timestamp_ns: int
    statement: str
    sat_provenance: dict[str, Any]
    inputs_fingerprint: str
    signal: EntropySignalModel
