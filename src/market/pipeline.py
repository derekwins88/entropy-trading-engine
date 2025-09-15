from __future__ import annotations

import asyncio
import random
from collections.abc import AsyncIterator
from datetime import UTC, datetime

import numpy as np
from entropy.metrics import delta_phi_from_window

from market.types import MarketTick


class MarketDataPipeline:
    def __init__(self, sources=None, symbols=None):
        self.sources = sources or ["simulated"]
        self.symbols = symbols or ["SPY", "QQQ", "VTI", "BTC-USD", "ETH-USD"]

    async def stream_prices(self, symbol: str) -> AsyncIterator[MarketTick]:
        assert "simulated" in self.sources, "Only simulated source implemented by default."
        price = 100.0 + random.random()
        while True:
            shock = np.random.normal(0, 0.05)
            price += shock - 0.01 * (price - 100.0)
            yield MarketTick(
                symbol=symbol,
                ts=datetime.now(UTC),
                price=float(max(price, 0.01)),
                source="simulated",
            )
            await asyncio.sleep(0.05)

    def calculate_entropy_series(self, price_window: list[float]) -> float:
        return (
            float(delta_phi_from_window(np.asarray(price_window, dtype=float)))
            if price_window
            else float("nan")
        )
