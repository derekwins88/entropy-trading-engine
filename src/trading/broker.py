from __future__ import annotations

from dataclasses import dataclass

FEE_PER_TRADE = 0.0005  # 5 bps demo fee


@dataclass
class Order:
    symbol: str
    qty: float
    side: str  # "buy" | "sell"
    price: float


class MockBroker:
    def __init__(self) -> None:
        self.positions: dict[str, float] = {}
        self.cash = 100_000.0
        self.trades: list[Order] = []

    def submit_order(self, order: Order) -> dict[str, object]:
        notional = order.qty * order.price
        fee = notional * FEE_PER_TRADE
        if order.side == "buy":
            self.cash -= notional + fee
            self.positions[order.symbol] = self.positions.get(order.symbol, 0.0) + order.qty
        else:
            cur = self.positions.get(order.symbol, 0.0)
            qty_to_sell = min(order.qty, max(cur, 0.0))
            self.cash += qty_to_sell * order.price - fee
            self.positions[order.symbol] = cur - qty_to_sell
        self.trades.append(order)
        return {"status": "filled", "order": order}
