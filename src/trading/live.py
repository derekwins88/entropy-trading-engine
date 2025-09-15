from __future__ import annotations

import asyncio

from entropy.analyzer import EntropyAnalyzer
from market.pipeline import MarketDataPipeline
from proof.db import ProofCapsuleDB
from risk.manager import EntropyRiskManager
from services.metrics import (
    broker_cash_gauge,
    capsules_total,
    last_price,
    open_position,
)
from utils.settings import load_settings

from trading.broker import MockBroker, Order


class EntropyTrader:
    def __init__(self, broker: MockBroker | None = None, db_url: str | None = None, symbols=None):
        settings = load_settings()
        self.broker = broker or MockBroker()
        self.analyzer = EntropyAnalyzer(
            window=settings.entropy_window,
            p_threshold=settings.p_threshold,
            np_threshold=settings.np_threshold,
        )
        self.risk = EntropyRiskManager(
            max_position_size=settings.max_position_size,
            entropy_confidence_threshold=settings.entropy_confidence_threshold,
        )
        self.db = ProofCapsuleDB(db_url or settings.database_url)
        self.pipeline = MarketDataPipeline(symbols=symbols or settings.symbols)
        self.price_buffers: dict[str, list[float]] = {}

    async def run_live_trading(self) -> None:
        async def run_symbol(symbol: str) -> None:
            self.price_buffers[symbol] = []
            async for tick in self.pipeline.stream_prices(symbol):
                buf = self.price_buffers[symbol]
                buf.append(tick.price)
                if len(buf) > self.analyzer.window:
                    buf.pop(0)
                last_price.labels(symbol=tick.symbol).set(tick.price)
                broker_cash_gauge.set(self.broker.cash)
                open_position.labels(symbol=tick.symbol).set(
                    self.broker.positions.get(tick.symbol, 0.0)
                )
                if len(buf) >= self.analyzer.window:
                    sig = self.analyzer.analyze_entropy_drift(buf)
                    cap = self.analyzer.generate_proof_capsule(
                        sig, inputs_fingerprint=f"{symbol}-last{len(buf)}"
                    )
                    self.db.store_capsule(symbol, cap)
                    capsules_total.labels(symbol=symbol).inc()
                    if self.risk.should_execute_trade(sig):
                        acct = self.broker.cash
                        size = self.risk.calculate_position_size(sig, acct).fraction
                        if size > 0:
                            notional = acct * size
                            qty = max(notional / tick.price, 0.0)
                            side = "buy" if sig.direction >= 0 else "sell"
                            self.broker.submit_order(
                                Order(symbol=symbol, qty=qty, side=side, price=tick.price)
                            )
                await asyncio.sleep(0)

        await asyncio.gather(*(run_symbol(s) for s in self.pipeline.symbols))
