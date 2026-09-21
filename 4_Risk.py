"""RFC Securities - Pillar 4: Risk & Stress Testing. Prepare before the storm."""
from __future__ import annotations

import os
import sys as _sys

_APP_ROOT = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(_APP_ROOT) == "pages":
    _APP_ROOT = os.path.dirname(_APP_ROOT)
for _cand in (_APP_ROOT, os.path.dirname(_APP_ROOT)):
    if _cand not in _sys.path:
        _sys.path.insert(0, _cand)
del _APP_ROOT, _cand

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.analysis import nice
from utils.ui import page_boot, render_footer, get_bundle
from utils.translations import t

macro = page_boot("RFC Securities - Risk & Stress Testing", "⛈")
lang = st.session_state["lang"]
bundle = get_bundle()
if bundle is None:
    st.info("Load or demo a business first from the sidebar.")
    render_footer()
    st.stop()

m = bundle["monthly"]
sector = bundle["business"].sector

st.header("⛈ Risk & Stress Testing - Prepare Before The Storm")
st.caption("Inflation, FX, interest rates, fuel, revenue dips, cost spikes. What happens to your "
           "profit if the world moves against you?")

inf = macro.get("inflation") or 20.0
d1, d2, d3 = st.columns(3)
with d1:
    episodes = st.slider("Stress level: what shocks to test", 10, 40, 20, 5)
with d2:
    b_inf = st.slider("Inflation/Input cost shock %", 5, 60, int(inf))
with d3:
    b_rev = st.slider("Revenue/sales shock %", -40, -5, -20)

months = m.index.tolist()
rev = m["revenue"].astype(float).tolist()
cost = m["costs"].astype(float).tolist()
base_profit = [r - c for r, c in zip(rev, cost)]

inf_up = [r - c * (1 + b_inf / 100) for r, c in zip(rev, cost)]
rev_down = [r * (1 + b_rev / 100) - c for r, c in zip(rev, cost)]
double_hit = [r * (1 + b_rev / 100) - c * (1 + b_inf / 100) for r, c in zip(rev, cost)]

stress = pd.DataFrame({
    "month": m["month"],
    "Base profit": base_profit,
    f"Cost shock +{b_inf}%": inf_up,
    f"Revenue shock {b_rev}%": rev_down,
    f"Double hit (+{b_inf}% cost, {b_rev}% revenue)": double_hit,
})

fig = go.Figure()
colors = {"Base profit": "#7BDCA6", f"Cost shock +{b_inf}%": "#ffb54d",
          f"Revenue shock {b_rev}%": "#e07b6b", f"Double hit (+{b_inf}% cost, {b_rev}% revenue)": "#C0392B"}
for col in stress.columns[1:]:
    fig.add_scatter(x=stress["month"], y=stress[col], mode="lines",
                    name=col, line=dict(color=colors[col], width=3 if col == "Base profit" else 2.2))
fig.add_hline(y=0, line_dash="dot", line_color="#fff")
fig.update_layout(title="Stress scenarios: how many months would your profit stay positive?",
                  yaxis_title="Monthly profit (USD)", legend=dict(orientation="h", yanchor="bottom", y=1.02))
st.plotly_chart(fig, width="stretch", key="risk_scen")

last_prof = base_profit[-1]
final_double = double_hit[-1]
st.metric("Latest month profit (base)", nice(last_prof))
st.metric("Latest month profit under double hit", nice(final_double),
          f"{(final_double - last_prof) / abs(last_prof) * 100 if last_prof else 0:+.0f}% vs base")

st.markdown("---")
st.markdown("### 🧠 Why this matters in Zimbabwe")
from utils.sector_advisor import macro_context_line
st.markdown(macro_context_line(sector, macro))
st.markdown("""
**What to watch each week:** exchange rate, fuel price, RBZ interest rate and policy announcements,
harvest/market news for your sector, and how your suppliers behave. Each of these lands directly in
your cost line or your customer's wallet.
""")

st.markdown("---")
st.subheader("🤖 Read the graph in plain English")
from utils.explanation_engine import build, render
expl = build(bundle, "risk", macro)
render(st, lang, expl, "risk")

render_footer()