"""
EntropyLab ⚡ — minimal backtest stub

Usage
-----
>>> import pandas as pd
>>> from entropylab import backtest
>>> # prices = pd.Series([...])  # daily close prices
>>> result = backtest(prices)
>>> print(result["sharpe"])
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Optional

import numpy as np
import pandas as pd

__all__ = ["backtest", "BacktestResult", "__version__"]
__version__ = "1.0.0"


@dataclass
class BacktestResult:
    sharpe: float
    cagr: float
    total_return: float
    max_drawdown: float
    trades: int

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


def _annualization_factor(prices: pd.Series) -> float:
    """Infer periods per year from the index frequency; default to 252 (daily)."""
    if isinstance(prices.index, pd.DatetimeIndex):
        try:
            # If a proper freq exists, map common ones
            freq = prices.index.inferred_freq or prices.index.freqstr
            if freq:
                f = freq.upper()
                if "B" in f or "D" in f:  # business/daily
                    return 252.0
                if "W" in f:
                    return 52.0
                if "M" in f:
                    return 12.0
                if "Q" in f:
                    return 4.0
                if "A" in f or "Y" in f:
                    return 1.0
        except Exception:
            pass
    # Fallback: assume daily
    return 252.0


def backtest(
    prices: pd.Series,
    risk_free_annual: float = 0.0,
    plot: bool = False,
) -> Dict[str, float]:
    """
    Minimal, opinionated backtest:
    - Strategy: long-and-hold the input price series
    - Outputs: Sharpe (excess), CAGR, Total Return, Max Drawdown, Trades (0)

    Parameters
    ----------
    prices : pd.Series
        Close prices indexed by datetime (preferred) or ordinal index.
    risk_free_annual : float
        Annualized risk-free rate (e.g., 0.02 for 2%). Default 0.
    plot : bool
        If True, show NAV chart (requires matplotlib; it’s in install_requires).

    Returns
    -------
    dict
        {"sharpe", "cagr", "total_return", "max_drawdown", "trades"}
    """
    if not isinstance(prices, pd.Series):
        raise TypeError("prices must be a pandas Series of close prices")

    prices = prices.dropna().astype(float)
    if prices.size < 3:
        return BacktestResult(sharpe=0.0, cagr=0.0, total_return=0.0, max_drawdown=0.0, trades=0).to_dict()

    rets = prices.pct_change().dropna()
    periods_per_year = _annualization_factor(prices)
    rf_per_period = (1 + risk_free_annual) ** (1 / periods_per_year) - 1

    excess = rets - rf_per_period
    vol = excess.std()
    sharpe = float((excess.mean() / vol) * np.sqrt(periods_per_year)) if vol > 0 else 0.0

    nav = (1 + rets).cumprod()
    total_return = float(nav.iloc[-1] - 1)

    # Max drawdown
    roll_max = nav.cummax()
    drawdown = nav / roll_max - 1.0
    max_dd = float(drawdown.min())

    # CAGR (robust to irregular spacing by using time delta if datetime)
    if isinstance(prices.index, pd.DatetimeIndex) and prices.index.size > 1:
        days = (prices.index[-1] - prices.index[0]).days or 1
        years = days / 365.25
        cagr = float((prices.iloc[-1] / prices.iloc[0]) ** (1 / years) - 1) if years > 0 else 0.0
    else:
        years = max(len(prices) / periods_per_year, 1e-9)
        cagr = float((prices.iloc[-1] / prices.iloc[0]) ** (1 / years) - 1)

    if plot:
        # Lazy import to keep import time snappy
        import matplotlib.pyplot as plt  # noqa: WPS433 (runtime import)

        ax = nav.rename("NAV").plot(title="EntropyLab Backtest — Buy & Hold")
        ax.set_xlabel("Date")
        ax.set_ylabel("NAV (normalized)")
        plt.show()

    result = BacktestResult(
        sharpe=round(sharpe, 4),
        cagr=round(cagr, 6),
        total_return=round(total_return, 6),
        max_drawdown=round(max_dd, 6),
        trades=0,
    )
    # Print a nice one-liner for the Quickstart notebook UX
    print(f"Sharpe (entropylab): {result.sharpe:.2f} | CAGR: {result.cagr:.2%} | MaxDD: {result.max_drawdown:.2%}")
    return result.to_dict()
