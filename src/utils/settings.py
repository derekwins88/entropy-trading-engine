from __future__ import annotations

import os

import yaml  # type: ignore[import-untyped]
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    symbols: list[str] = ["SPY", "QQQ", "VTI", "BTC-USD", "ETH-USD"]
    sources: list[str] = ["simulated"]
    entropy_window: int = 21
    p_threshold: float = 0.045
    np_threshold: float = 0.09
    max_position_size: float = 0.25
    entropy_confidence_threshold: float = 0.85
    start_capital: int = 100_000
    database_url: str = "sqlite:///./entropy_capsules.db"
    service_host: str = "0.0.0.0"
    service_port: int = 8000

    model_config = SettingsConfigDict(env_prefix="ENTROPY_", env_file=".env", extra="ignore")


def load_settings() -> AppSettings:
    s = AppSettings()
    yml = "config/settings.yaml"
    if os.path.exists(yml):
        with open(yml) as f:
            data = yaml.safe_load(f) or {}
        s = AppSettings(
            symbols=data.get("symbols", s.symbols),
            sources=data.get("sources", s.sources),
            entropy_window=data.get("entropy", {}).get("window", s.entropy_window),
            p_threshold=data.get("entropy", {}).get("p_threshold", s.p_threshold),
            np_threshold=data.get("entropy", {}).get("np_threshold", s.np_threshold),
            max_position_size=data.get("risk", {}).get("max_position_size", s.max_position_size),
            entropy_confidence_threshold=data.get("risk", {}).get(
                "entropy_confidence_threshold", s.entropy_confidence_threshold
            ),
            start_capital=data.get("backtest", {}).get("start_capital", s.start_capital),
            database_url=data.get("database", {}).get("url", s.database_url),
            service_host=data.get("service", {}).get("host", s.service_host),
            service_port=data.get("service", {}).get("port", s.service_port),
        )
    return s
