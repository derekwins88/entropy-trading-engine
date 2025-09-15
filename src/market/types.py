from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass(frozen=True)
class MarketTick:
    symbol: str
    ts: datetime
    price: float
    source: Literal["simulated", "yahoo_finance", "alpha_vantage", "polygon_io"]
