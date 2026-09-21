"""Shared financial analysis helpers used across all 5 pages."""
from __future__ import annotations

import numpy as np
import pandas as pd


def trend(series) -> str:
    """Human trend label: 'rising', 'falling', or 'volatile/flat'."""
    s = list(series)
    if len(s) < 2:
        return "flat"
    first = s[0]
    last = s[-1]
    diff_pct = (last - first) / abs(first) * 100 if first else 0
    if diff_pct > 5:
        return "rising"
    if diff_pct < -5:
        return "falling"
    if abs(np.std(s)) > abs(np.mean(s)) * 0.4:
        return "volatile"
    return "flat"


def consecutive_dir(series, lookback=5) -> str | None:
    """Count consecutive up/down months. Returns 'up', 'down' or None."""
    s = list(series)
    if len(s) < 2:
        return None
    tail = s[-lookback:]
    diffs = [1 if tail[i + 1] > tail[i] else (-1 if tail[i + 1] < tail[i] else 0)
             for i in range(len(tail) - 1)]
    d = 0
    for x in reversed(diffs):
        if x == 0:
            return "up" if d > 0 else ("down" if d < 0 else None)
        if x > 0 and d >= 0:
            d += 1
        elif x < 0 and d <= 0:
            d -= 1
        else:
            return "up" if d > 0 else ("down" if d < 0 else None)
    return "up" if d > 0 else ("down" if d < 0 else None)


def growth(monthly: pd.DataFrame, col: str = "revenue", months=12) -> float:
    s = monthly[col].tolist()
    if len(s) < 2:
        return 0.0
    a, b = s[0], s[-1]
    return ((b - a) / abs(a) * 100) if a else 0.0


def forecast(monthly: pd.DataFrame, col: str = "revenue", ahead: int = 3) -> list:
    """Simple linear-trend forecast. Returns [value, value, value] for next ahead months."""
    s = monthly[col].tolist()
    if len(s) < 3:
        return [float(s[-1])] * ahead if s else [0.0] * ahead
    x = np.arange(len(s))
    y = np.array(s)
    slope, intercept = np.polyfit(x, y, 1)
    return [float(max(0, intercept + slope * (len(s) + i))) for i in range(ahead)]


def liquidity(monthly: pd.DataFrame) -> dict:
    cash = monthly["cash_balance"].tolist()
    out = monthly["cash_out"].tolist()
    months_of_cash = (cash[-1] / (out[-1] / 30.4)) if out[-1] else 0
    return {
        "opening": cash[0] if cash else 0,
        "closing": cash[-1] if cash else 0,
        "months_of_cash": round(months_of_cash, 1),
        "trend": trend(cash),
    }


def nice(v) -> str:
    return f"${v:,.0f}"


def pct(v) -> str:
    return f"{v:+.1f}%"


def fmt_money(v) -> str:
    neg = v < 0
    return f"-${abs(v):,.2f}" if neg else f"${v:,.2f}"