from __future__ import annotations

import argparse

import uvicorn
from utils.settings import load_settings


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=None)
    ap.add_argument("--port", type=int, default=None)
    args = ap.parse_args()
    settings = load_settings()
    host = args.host or settings.service_host
    port = args.port or settings.service_port
    uvicorn.run("services.api:app", host=host, port=port, reload=False)
