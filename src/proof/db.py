from __future__ import annotations

from typing import Any

from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    insert,
    select,
)

from proof.capsule import CapsuleModel


class ProofCapsuleDB:
    def __init__(self, url: str = "sqlite:///./entropy_capsules.db"):
        self.engine = create_engine(url, future=True)
        self.meta = MetaData()
        self.capsules = Table(
            "capsules",
            self.meta,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("symbol", String, nullable=False),
            Column("signal_hash", String, nullable=False),
            Column("schema_version", String, nullable=False),
            Column("timestamp_ns", BigInteger, nullable=False),
            Column("payload", JSON, nullable=False),
        )
        Index("ix_capsules_symbol_ts", self.capsules.c.symbol, self.capsules.c.timestamp_ns)
        Index("ux_capsules_signal_hash", self.capsules.c.signal_hash)
        self.meta.create_all(self.engine)

    def store_capsule(self, symbol: str, capsule: CapsuleModel) -> None:
        payload: dict[str, Any] = {
            "signal": capsule.signal.model_dump(),
            "statement": capsule.statement,
            "sat_provenance": capsule.sat_provenance,
            "inputs_fingerprint": capsule.inputs_fingerprint,
        }
        with self.engine.begin() as conn:
            conn.execute(
                insert(self.capsules).values(
                    symbol=symbol,
                    signal_hash=capsule.signal_hash,
                    schema_version=capsule.schema_version,
                    timestamp_ns=int(capsule.timestamp_ns),
                    payload=payload,
                )
            )

    def query_historical_proofs(
        self, symbol: str, entropy_range: tuple[float, float]
    ) -> list[dict]:
        lo, hi = entropy_range
        stmt = select(self.capsules).where(self.capsules.c.symbol == symbol)
        rows = []
        with self.engine.begin() as conn:
            for r in conn.execute(stmt):
                dphi = r.payload["signal"]["delta_phi"]
                if isinstance(dphi, (int | float)) and lo <= dphi <= hi:
                    rows.append(dict(r._mapping))
        return rows
