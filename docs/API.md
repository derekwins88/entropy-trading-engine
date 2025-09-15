API
•GET /health → {ok: true}
•GET /run/live → starts simulated live loop (idempotent guard)
•WS /ws/prices/{symbol} → price ticks (sim)
•POST /proofs/query body: {"symbol": "...", "entropy_range": [low, high]}
•GET /metrics → Prometheus text exposition
