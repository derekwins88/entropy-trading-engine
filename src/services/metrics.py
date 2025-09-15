from __future__ import annotations

from fastapi.responses import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    generate_latest,
)

registry = CollectorRegistry()
engine_up = Gauge("entropy_engine_up", "Service up flag", registry=registry)
capsules_total = Counter(
    "entropy_capsules_total", "Total proof capsules stored", ["symbol"], registry=registry
)
last_price = Gauge("entropy_last_price", "Last observed price", ["symbol"], registry=registry)
broker_cash_gauge = Gauge("entropy_broker_cash", "Broker cash balance", registry=registry)
open_position = Gauge(
    "entropy_open_position", "Open position quantity (mock broker)", ["symbol"], registry=registry
)


def metrics_response() -> Response:
    data = generate_latest(registry)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
