"""Shared financial analysis and Bloomberg-style chart builders."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

GOLD = "#C9A227"
TEAL = "#2F9E8F"
RED = "#D64545"
AMBER = "#E0A73C"
BLUE = "#4A90D9"
GREEN = "#3FA66B"

_TPL = dict(
    layout=dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E8E4D8", size=12),
        margin=dict(l=48, r=16, t=40, b=32),
        hovermode="x unified",
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.10)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.10)"),
    )
)


def trend(series) -> str:
    s = list(series)
    if len(s) < 2:
        return "flat"
    first, last = s[0], s[-1]
    diff_pct = (last - first) / abs(first) * 100 if first else 0
    if diff_pct > 5:
        return "rising"
    if diff_pct < -5:
        return "falling"
    if abs(np.std(s)) > abs(np.mean(s)) * 0.4:
        return "volatile"
    return "flat"


def consecutive_dir(series, lookback=5):
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


def growth(monthly: pd.DataFrame, col: str = "revenue", months: int = 12) -> float:
    s = monthly[col].tolist()
    if len(s) < 2:
        return 0.0
    a, b = s[0], s[-1]
    return ((b - a) / abs(a) * 100) if a else 0.0


def pct(v) -> str:
    return f"{v:+.1f}%"


def forecast(monthly: pd.DataFrame, col: str = "revenue", ahead: int = 3) -> list:
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


def npv(discount_rate: float, cashflows: list) -> float:
    return sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(cashflows))


def irr(cashflows: list) -> float | None:
    lo, hi, eps = -0.99, 5.0, 1e-5
    f = lambda r: npv(r, cashflows)
    if f(lo) * f(hi) > 0 and abs(f(lo)) > abs(f(hi)):
        return 0.0
    for _ in range(120):
        mid = (lo + hi) / 2
        if f(mid) * f(lo) <= 0:
            hi = mid
        else:
            lo = mid
        if abs(f((lo + hi) / 2)) < eps:
            break
    return round((lo + hi) / 2, 4)


def payback(cashflows: list) -> float | None:
    cum, prior = 0.0, 0.0
    for i, cf in enumerate(cashflows):
        cum += cf
        if cum >= 0 and i > 0 and cashflows[i - 1] < 0:
            step = abs(cashflows[i - 1]) / abs(cum - cashflows[i - 1] + cashflows[i - 1])
            return round((i - 1) + step, 2)
        prior = cf
    return None


def _fig(df, months):
    f = go.Figure(layout=_TPL["layout"])
    start = max(0, len(df) - months)
    d = df.iloc[start:]
    return f, d


def build_chart(graph_type: str, df: pd.DataFrame, months: int = 12):
    f, d = _fig(df, months)
    labels = d["month"].tolist()
    if graph_type == "profitability":
        f.add_bar(x=labels, y=d["revenue"], name="Revenue", marker_color=GOLD, opacity=0.85)
        f.add_scatter(x=labels, y=d["profit"], name="Net Profit", mode="lines+markers",
                      line=dict(color=TEAL, width=3))
        f.update_layout(title="Profitability Drivers - Revenue vs Net Profit",
                        barmode="group")
    elif graph_type == "cashflow":
        f.add_bar(x=labels, y=d["cash_in"], name="Cash In", marker_color=TEAL, opacity=0.7)
        f.add_bar(x=labels, y=d["cash_out"], name="Cash Out", marker_color=AMBER, opacity=0.7)
        f.add_scatter(x=labels, y=d["cash_balance"], name="Cash Balance", mode="lines+markers",
                      line=dict(color=GOLD, width=3), yaxis="y2")
        f.update_layout(title="Cash Flow - In, Out and Balance",
                        yaxis2=dict(overlaying="y", side="right", showgrid=False),
                        barmode="group")
    elif graph_type == "investment":
        capex = -abs(float(d["revenue"].iloc[0]) * 0.6)
        flows = [capex] + [float(v) for v in d["profit"]]
        cum = np.cumsum(flows)
        f.add_bar(x=["Investment"] + labels, y=flows, name="Net Cash Flow",
                  marker_color=[RED if v < 0 else TEAL for v in flows])
        f.add_scatter(x=["Investment"] + labels, y=cum, name="Cumulative", mode="lines+markers",
                      line=dict(color=GOLD, width=3))
        rate = 0.15
        npv_v = npv(rate, flows)
        irr_v = irr([capex] + [float(v) for v in d["profit"]])
        f.add_annotation(x=0.98, y=0.95, xref="paper", yref="paper", align="right",
                         text=f"NPV @15% = ${npv_v:,.0f}<br>IRR = {irr_v*100:.1f}%",
                         showarrow=False, font=dict(color=GOLD, size=13))
        f.update_layout(title="Investment - Cumulative Net Cash Flow (NPV / IRR)")
    elif graph_type == "risk":
        scenarios = ["Revenue -20%", "Fuel / Transport +15%",
                     "Inflation 12%", "Supplier costs +10%"]
        profit = d["profit"].mean()
        impact = [profit * -0.30, profit * -0.22, profit * -0.16, profit * -0.18]
        f.add_bar(y=scenarios, x=impact, orientation="h", marker_color=[RED, AMBER, BLUE, TEAL])
        f.add_vline(x=0, line_color="rgba(255,255,255,0.35)")
        f.update_layout(title="Risk & Stress Test - Impact on Monthly Profit",
                        xaxis_title="USD impact on average monthly profit")
    elif graph_type == "optimization":
        opts = ["Restock fast movers", "Expand online sales", "Reduce slow stock",
                "Add high-margin service", "Renegotiate supplier terms"]
        roi = [22, 16, 12, 28, 9]
        f.add_bar(x=opts, y=roi, marker_color=[GOLD, TEAL, AMBER, BLUE, GREEN])
        f.update_layout(title="Optimization - Best Allocation of Capital (modelled ROI %)",
                        yaxis_title="Modelled potential return %")
    f.update_layout(xaxis_title="", template=None)
    return f


def sparkline(values: list, width: int = 220, height: int = 30, color: str = GOLD) -> str:
    """Return an inline SVG sparkline (mini trend line)."""
    if not values or len(values) < 2:
        return ""
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1
    pts = []
    n = len(values)
    for i, v in enumerate(values):
        x = 4 + i * (width - 8) / (n - 1)
        y = height - 6 - (v - lo) / span * (height - 12)
        pts.append(f"{x:.1f},{y:.1f}")
    last = values[-1]
    up = last >= values[0]
    col = TEAL if up else RED
    poly = " ".join(pts)
    return (f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
            f'<polyline points="{poly}" fill="none" stroke="{col}" stroke-width="2"/>'
            f'<circle cx="{width-8:.1f}" cy="{height-6-(last-lo)/span*(height-12):.1f}" '
            f'r="2.6" fill="{col}"/></svg>')