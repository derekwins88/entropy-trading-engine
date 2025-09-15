from __future__ import annotations

import argparse

import pandas as pd
from trading.backtest import EntropyBacktester


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--date-col", default="date")
    ap.add_argument("--price-col", default="close")
    ap.add_argument("--capital", type=float, default=100000)
    ap.add_argument("--no-gpu", action="store_true")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    if args.date_col in df.columns:
        df[args.date_col] = pd.to_datetime(df[args.date_col])
        df = df.set_index(args.date_col)
    df = df.rename(columns={args.price_col: "close"})[["close"]].dropna()

    bt = EntropyBacktester(use_gpu=not args.no_gpu)
    res = bt.backtest_entropy_strategy(df, start_capital=args.capital)
    print("Summary:", res.summary)
