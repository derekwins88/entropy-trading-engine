from __future__ import annotations

import asyncio

from entropy.analyzer import EntropyAnalyzer
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from market.pipeline import MarketDataPipeline
from pydantic import BaseModel
from trading.live import EntropyTrader
from utils.settings import load_settings

from services.metrics import engine_up, metrics_response

settings = load_settings()
app = FastAPI(title="Entropy Trading Engine")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

trader = EntropyTrader(db_url=settings.database_url, symbols=settings.symbols)
db = trader.db
analyzer = EntropyAnalyzer(
    window=settings.entropy_window,
    p_threshold=settings.p_threshold,
    np_threshold=settings.np_threshold,
)
pipeline = MarketDataPipeline(symbols=[settings.symbols[0] if settings.symbols else "SPY"])
_live_task: asyncio.Task | None = None


class QueryRange(BaseModel):
    symbol: str
    entropy_range: tuple[float, float]


@app.on_event("startup")
async def startup_event() -> None:
    engine_up.set(1)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    global _live_task
    if _live_task and not _live_task.done():
        _live_task.cancel()
    engine_up.set(0)


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.post("/proofs/query")
def proofs_query(body: QueryRange):
    return db.query_historical_proofs(body.symbol, body.entropy_range)


@app.websocket("/ws/prices/{symbol}")
async def ws_prices(ws: WebSocket, symbol: str) -> None:
    await ws.accept()
    async for tick in pipeline.stream_prices(symbol):
        await ws.send_json({"symbol": tick.symbol, "ts": tick.ts.isoformat(), "price": tick.price})


@app.get("/metrics")
def metrics():
    return metrics_response()


@app.get("/run/live")
async def run_live():
    global _live_task
    if _live_task and not _live_task.done():
        return {"status": "already_running"}
    _live_task = asyncio.create_task(trader.run_live_trading())
    return {"status": "started"}
