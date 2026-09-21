"""RFC Securities - Pillar 5: Optimization. Find the best allocation."""
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

from utils.analysis import liquidity, nice
from utils.ui import page_boot, render_footer, get_bundle
from utils.sector_advisor import can_do
from utils.translations import t

macro = page_boot("RFC Securities - Optimization", "⚙")
lang = st.session_state["lang"]
bundle = get_bundle()
if bundle is None:
    st.info("Load or demo a business first from the sidebar.")
    render_footer()
    st.stop()

m = bundle["monthly"]
products = bundle["products"]
liq = liquidity(m)

st.header("⚙ Optimization - Find The Best Allocation")
st.caption("Your money can go many places. This page shows where it earns the most - and what you "
           "are constrained by.")

if not products.empty:
    margin = products[["Product", "Profit Margin %", "Stock Qty"]].copy()
    margin["Margin-$"] = (margin["Profit Margin %"] / 100).clip(lower=0)
    total_stock = margin["Stock Qty"].sum() or 1
    fig_sun = go.Figure(go.Sunburst(
        labels=margin["Product"].tolist(),
        parents=[""] * len(margin),
        values=margin["Stock Qty"].tolist(),
        branchvalues="total",
        hovertemplate="%{label}<br>Stock: %{value}<br>Margin: %{customdata:.1f}%<extra></extra>",
        customdata=margin["Profit Margin %"].tolist()))
    fig_sun.update_layout(title="Where your stock sits vs its margin - look for high stock with low margin")
    st.plotly_chart(fig_sun, width="stretch", key="opt_sunburst")
else:
    st.info("Upload a product list to unlock the stock/margin sunburst.")

cash_now = liq["closing"]
inventory_now = float(m["inventory"].iloc[-1])
profit_pool = float(m["profit"].sum())
reserve = cash_now * 0.45
allocate_stock = min(inventory_now * 0.35, cash_now * 0.6)
allocate_growth = cash_now * 0.2
allocate_debt = cash_now * 0.1
allocate_margin = max(cash_now * 0.1, profit_pool * 0.05)

sankey = go.Figure(go.Sankey(
    arrangement="snap",
    node=dict(
        pad=20, thickness=24,
        label=["Cash reserve", "Turn slow stock", "Best-margin products",
               "Reduce debt", "Marketing & growth", "Buffer against inflation",
               "Higher sales & margin", "Cleaner interest bill", "Stronger cash"],
        color=["#0E4A37", "#7BDCA6", "#C9A227", "#B24C4C", "#4da6ff", "#7BDCA6",
               "#C9A227", "#B24C4C", "#7BDCA6"],
    ),
    link=dict(
        source=[0, 0, 0, 0, 1, 0],
        target=[5, 2, 3, 4, 5, 8],
        value=[reserve, allocate_margin, allocate_debt, allocate_growth, allocate_stock, reserve * 0.2],
        color=["rgba(201,162,39,.5)", "rgba(123,220,166,.55)", "rgba(178,76,76,.55)",
               "rgba(77,166,255,.55)", "rgba(123,220,166,.45)", "rgba(123,220,166,.35)"],
    )))
sankey.update_layout(title="Suggested allocation of your current cash (modelled, decisions stay with you)",
                     font=dict(color="#F2EDE4"))
st.plotly_chart(sankey, width="stretch", key="opt_sankey")

st.markdown("---")
st.markdown("### 🧠 How to read the allocation")
st.markdown(f"""
- You currently hold **{nice(cash_now)}** cash and about **{nice(inventory_now)}** in stock.
- Recommended split (modelled today): keep **${reserve:,.0f}** as a buffer against inflation & supplier shocks,
  move **{nice(allocate_stock)}** out of slow-moving stock into fast, high-margin lines,
  cut **{nice(allocate_debt)}** of costly debt, and put **{nice(allocate_growth)}** into proven growth.
- The rule: *allocate by profit per dollar*, not by habit. Every dollar earns somewhere - make sure it earns in your best place.
""")
sector = bundle["business"].sector
st.markdown("### 🎯 Ideas to act on this week")
for item in can_do(sector, "diversify")[:2]:
    st.markdown(f"- {item}")

st.markdown("---")
st.subheader("🤖 Read the graph in plain English")
from utils.explanation_engine import build, render
expl = build(bundle, "optimization", macro)
render(st, lang, expl, "optimization")

render_footer()