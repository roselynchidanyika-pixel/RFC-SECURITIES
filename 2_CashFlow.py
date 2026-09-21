"""RFC Securities - Pillar 2: Cash Flow. The financial lifeblood."""
from __future__ import annotations

import os
import sys as _sys

_APP_ROOT = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(_APP_ROOT) == "pages":
    _APP_ROOT = os.path.dirname(_APP_ROOT)
_APP_UTILS = os.path.join(_APP_ROOT, "utils")
for _cand in (_APP_UTILS, _APP_ROOT):
    if _cand not in _sys.path:
        _sys.path.insert(0, _cand)
del _APP_ROOT, _APP_UTILS, _cand

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analysis import forecast, liquidity, nice
from ui import (page_boot, render_footer, period_slice, render_chart_block,
                      get_bundle)
from translations import t

macro = page_boot("RFC Securities - Cash Flow", "💧")
lang = st.session_state["lang"]
bundle = get_bundle()
if bundle is None:
    st.info("Load or demo a business first from the sidebar.")
    render_footer()
    st.stop()

m = bundle["monthly"]

st.header("💧 Cash Flow - The Financial Lifeblood")
st.caption("Profit is a paper number. Cash pays the bills. Here is the real money story.")

liq = liquidity(m)
d1, d2, d3 = st.columns(3)
d1.metric("Cash balance now", nice(liq["closing"]), f"{liq['trend']}")
d2.metric("Months of cash cover", f"{liq['months_of_cash']}")
d3.metric("Cash brought in (12m)", nice(m["cash_in"].sum()))

period = st.radio("Period", ["3M", "6M", "12M"], horizontal=True, index=2)
sub = period_slice(m, int(period.replace("M", "")))

fig = go.Figure()
fig.add_bar(x=sub["month"], y=sub["cash_in"], name="Cash In",
            marker_color="#7BDCA6", hovertemplate="Cash in %{y:$,.0f}")
fig.add_bar(x=sub["month"], y=sub["cash_out"], name="Cash Out",
            marker_color="#B24C4C", hovertemplate="Cash out %{y:$,.0f}")
fig.add_scatter(x=sub["month"], y=sub["cash_balance"], name="Cash Balance",
                mode="lines+markers", line=dict(color="#C9A227", width=3.5),
                hovertemplate="Balance %{y:$,.0f}")
fig.update_layout(barmode="group",
                  title="Cash In vs Cash Out (bars) and Bank Balance (gold line)",
                  legend=dict(orientation="h", yanchor="bottom", y=1.02))
st.plotly_chart(fig, width="stretch", key="cf_river")

st.subheader("🔮 Future cash position (next 3 months, linear trend)")
fc_in = forecast(m, "cash_in", 3)
fc_out = forecast(m, "cash_out", 3)
if len(m):
    bal = m["cash_balance"].iloc[-1]
    fcs = []
    for i in range(3):
        bal += 0.96 * fc_in[i] - fc_out[i]
        fcs.append(bal)
future_months = ["Next 1", "Next 2", "Next 3"]
figf = go.Figure(go.Scatter(x=future_months, y=fcs, mode="lines+markers",
                            line=dict(color="#7BDCA6", width=4),
                            fill="tozeroy", fillcolor="rgba(123,220,166,.18)"))
figf.update_layout(title="Projected bank balance trajectory (trend model, not a promise)",
                   yaxis_title="USD")
st.plotly_chart(figf, width="stretch", key="cf_forecast")
st.caption("🔎 Forecast rule applied: cash in/out keep the same trend as the last 12 months. "
           "Real months can differ - this is a planning view, not a guarantee.")

st.markdown("---")
st.subheader("🤖 Read the graph in plain English")
from explanation_engine import build, render
expl = build(bundle, "cashflow", macro)
render(st, lang, expl, "cashflow")

render_footer()