# EntropyLab ⚡  
Turn market chaos into backtests in 13 seconds.  
Get Pro derekespinoza88@gmail.com

<!-- (Keep your existing README content below this line) -->

# Entropy Trading Engine

![CI](https://github.com/<YOUR_GH_USER_OR_ORG>/entropy-trading-engine/actions/workflows/ci.yml/badge.svg)

Production-ready skeleton for an entropy-driven trading assistant extending Derek's "Brain" proof system.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,test]"
pre-commit install
pre-commit run --all-files

Run a backtest from CSV (deterministic CPU)

entropy-backtest --csv data/SPY.csv --date-col date --price-col close --no-gpu --capital 100000

Run the API

entropy-service --host 0.0.0.0 --port 8000

Explore
•Health:        GET http://localhost:8000/health
•Start Live:    GET http://localhost:8000/run/live
•Price Stream:  WS  ws://localhost:8000/ws/prices/SPY
•Proof Query:   POST http://localhost:8000/proofs/query {"symbol":"SPY","entropy_range":[0.045,0.2]}
•Metrics:       GET http://localhost:8000/metrics (Prometheus exposition)

Config

Edit config/settings.yaml or use ENV (prefix ENTROPY_) to override thresholds, DB URL, symbols.

Disclaimer: Research software. Not investment advice.

## Commercial Use
See [LICENSE](LICENSE).  
Pro upgrade removes watermark & adds live-broker plugins.
