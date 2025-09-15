from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from entropy.analyzer import EntropyAnalyzer, EntropySignal
from utils.arrays import to_numpy, xp


@dataclass
class BacktestResults:
    summary: dict[str, float]
    equity_curve: pd.Series
    signals: list[EntropySignal]


def _performance(equity: pd.Series) -> dict[str, float]:
    r = equity.pct_change().dropna()
    ann = float(r.mean() * 252)
    vol = float(r.std() * np.sqrt(252))
    sharpe = ann / vol if vol > 0 else float("nan")
    dd = float((equity / equity.cummax() - 1).min())
    return {"ann_return": ann, "ann_vol": vol, "sharpe": sharpe, "max_dd": dd}


class EntropyBacktester:
    def __init__(
        self,
        use_gpu: bool = True,
        window: int = 21,
        p_thresh: float = 0.045,
        np_thresh: float = 0.09,
    ):
        self.xp = xp() if use_gpu else np
        self.analyzer = EntropyAnalyzer(window=window, p_threshold=p_thresh, np_threshold=np_thresh)

    def backtest_entropy_strategy(
        self, historical_data: pd.DataFrame, start_capital: float = 100000
    ) -> BacktestResults:
        close = historical_data["close"].astype(float).to_numpy()
        n = close.size
        window = self.analyzer.window
        arr = self.xp.asarray(close)
        dphi = self.xp.full(n, self.xp.nan)
        for i in range(window - 1, n):
            w = arr[i - window + 1 : i + 1]
            hi = float(self.xp.max(w))
            lo = float(self.xp.min(w))
            dphi[i] = (hi - lo) / max(abs(hi), 1e-9)
        dphi_np = to_numpy(dphi)
        np_wall = dphi_np > self.analyzer.np_thresh
        no_rec = np.zeros(n, dtype=bool)
        for i in range(window - 1, n):
            trail = dphi_np[i - window + 1 : i + 1]
            finite = trail[np.isfinite(trail)]
            no_rec[i] = finite.size > 0 and np.min(finite) >= self.analyzer.p_thresh
        span = max(self.analyzer.np_thresh - self.analyzer.p_thresh, 1e-9)
        conf = np.clip((dphi_np - self.analyzer.p_thresh) / span, 0, 1)
        conf[~np.isfinite(conf)] = 0.0
        pos = np.zeros(n)
        hold = 5
        for i in range(window - 1, n):
            if conf[i] >= 0.85 and (np_wall[i] or no_rec[i]):
                x = np.arange(window, dtype=float)
                y = close[i - window + 1 : i + 1]
                slope = np.cov(x, y, bias=True)[0, 1] / (np.var(x) + 1e-12)
                direction = 1.0 if slope > 0 else -1.0
                pos[i : min(i + hold, n)] = direction
        ret = pd.Series(close, index=historical_data.index).pct_change().fillna(0.0).to_numpy()
        strat = pos[:-1] * ret[1:]
        equity = np.empty(ret.size, dtype=float)
        equity[0] = start_capital
        equity[1:] = start_capital * np.cumprod(1.0 + strat)
        equity_series = pd.Series(equity, index=historical_data.index)
        signals: list[EntropySignal] = []
        for i in range(window - 1, n):
            if conf[i] >= 0.85 and (np_wall[i] or no_rec[i]):
                sig = self.analyzer.analyze_entropy_drift(close[: i + 1])
                signals.append(sig)
        return BacktestResults(
            summary=_performance(equity_series), equity_curve=equity_series, signals=signals
        )
