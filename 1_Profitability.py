"""RFC Securities - Pillar 1: Profitability. The engine of the business."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.analysis import growth, nice, pct
from utils.ui import (page_boot, render_footer, period_slice, render_chart_block,
                      dash_metric, get_bundle)
from utils.translations import t

macro = page_boot("RFC Securities - Profitability", "📊")
lang = st.session_state["lang"]
bundle = get_bundle()
if bundle is None:
    st.info("Load or demo a business first from the sidebar.")
    render_footer()
    st.stop()

m = bundle["monthly"]
products = bundle["products"]
sector = bundle["business"].sector

st.header("📊 Profitability - The Engine of the Business")
st.caption("Revenue, costs and profit - and what every cent is telling you.")

d1, d2, d3, d4 = st.columns(4)
last, prev = m.iloc[-1], m.iloc[-2] if len(m) > 1 else m.iloc[-1]
d1.metric(t(lang, "metric_revenue"), nice(last["revenue"]), f"{growth(m,'revenue'):+.1f}% 12m")
d2.metric(t(lang, "metric_costs"), nice(last["costs"]), f"{growth(m,'costs'):+.1f}% 12m")
d3.metric(t(lang, "metric_profit"), nice(last["profit"]), f"{growth(m,'profit'):+.1f}% 12m")
g = growth(m, "revenue")
d4.metric(t(lang, "metric_growth"), f"{g:+.1f}%",
          "Cost growth vs revenue" if growth(m, "costs") > g else "Revenue outrunning cost growth")

period = st.radio("Period", ["3M", "6M", "12M"], horizontal=True, index=2)
sub = period_slice(m, int(period.replace("M", "")))

fig = go.Figure()
fig.add_bar(x=sub["month"], y=sub["revenue"], name="Revenue",
            marker_color="#C9A227", hovertemplate="Revenue %{y:$,.0f}")
fig.add_bar(x=sub["month"], y=sub["costs"], name="Costs",
            marker_color="#9b8a4e", hovertemplate="Costs %{y:$,.0f}")
fig.add_scatter(x=sub["month"], y=sub["profit"], name="Profit",
                mode="lines+markers", line=dict(color="#7BDCA6", width=3),
                hovertemplate="Profit %{y:$,.0f}")
fig.update_layout(barmode="group", title="Revenue vs Costs vs Profit",
                  xaxis_title=None, yaxis_title="USD",
                  legend=dict(orientation="h", yanchor="bottom", y=1.02))
st.plotly_chart(fig, width="stretch", key="prof_main")
st.caption("Click legend to isolate. Hover any bar for exact USD values.")

c1, c2 = st.columns([2, 1])
with c1:
    m0 = (m["revenue"] - m["costs"]) / m["revenue"].replace(0, np.nan)
    donut_data = pd.DataFrame({
        "slice": ["Cost of sales + expenses", "Profit kept"],
        "value": [float(m["costs"].iloc[-1]), float(max(m["profit"].iloc[-1], 0))]})
    fig2 = go.Figure(go.Pie(labels=donut_data["slice"], values=donut_data["value"],
                            hole=0.55, marker=dict(colors=["#9b8a4e", "#7BDCA6"]),
                            hovertemplate="%{label}: %{value:$,.0f}"))
    fig2.update_layout(title="Where a dollar lands today (latest month)",
                       showlegend=True, legend=dict(orientation="h"))
    st.plotly_chart(fig2, width="stretch", key="prof_donut")
with c2:
    st.markdown("#### Product margins")
    if not products.empty:
        keep = products[["Product", "Profit Margin %", "Fast/Slow Moving"]]
        st.dataframe(keep, hide_index=True, width="stretch", height=300)
        best = keep.loc[keep["Profit Margin %"].idxmax()]
        st.markdown(f"Best margin line: **{best['Product']}** ({best['Profit Margin %']:.1f}%)")

st.markdown("---")
st.subheader("🤖 Read the graph in plain English")
from utils.explanation_engine import build, render
expl = build(bundle, "profitability", macro)
render(st, lang, expl, "profitability")

render_footer()