"""RFC Securities - Pillar 3: Investment. Building the future. NPV / IRR /
MIRR / Payback / PI / DCF explained simply and shown as graphs."""
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
import plotly.graph_objects as go
import streamlit as st

from analysis import nice
from ui import page_boot, render_footer, get_bundle
from translations import t


def pv(cf, r, t):
    return cf / (1 + r) ** t


def npv(cfs, r):
    return -cfs[0] + sum(pv(cf, r, i) for i, cf in enumerate(cfs[1:], start=1))


def irr(cfs, lo=-0.95, hi=5.0):
    f = lambda r: npv(cfs, r)
    for _ in range(200):
        mid = (lo + hi) / 2
        fm = f(mid)
        if abs(fm) < 1e-6:
            return mid
        if f(lo) * fm < 0:
            hi = mid
        else:
            lo = mid
        if hi - lo < 1e-8:
            return mid
    return None


def mirr(cfs, finance_rate, reinvest_rate):
    pos = [cf for cf in cfs[1:] if cf > 0]
    neg = [cf for cf in cfs]  # including initial outflow
    tv = sum(pv(cf, reinvest_rate, len(cfs) - 1 - i) for i, cf in enumerate(cfs[1:]) if cf > 0) * (1 + reinvest_rate) ** (len(cfs) - 1)
    order = len(cfs) - 1
    pv_neg = sum(abs(cf) / (1 + finance_rate) ** i for i, cf in enumerate(cfs) if cf < 0)
    if pv_neg <= 0:
        return None
    return (tv / pv_neg) ** (1 / order) - 1


def payback(cfs):
    cum = 0.0
    initial = abs(cfs[0])
    for i, cf in enumerate(cfs[1:], start=1):
        cum += cf
        if cum >= initial:
            return i
    return None


macro = page_boot("RFC Securities - Investment", "🏗")
lang = st.session_state["lang"]
bundle = get_bundle()
if bundle is None:
    st.info("Load or demo a business first from the sidebar.")
    render_footer()
    st.stop()

m = bundle["monthly"]
avg_profit = float(m["profit"].mean())
avg_rev = float(m["revenue"].mean())

st.header("🏗 Investment - Building The Future")
st.caption("Before spending money, answer one question: will this money come back bigger than it left?")

c1, c2, c3 = st.columns(3)
with c1:
    capital = st.slider("Money you want to invest (USD)", 500, 20000,
                        int(min(max(avg_profit * 6, 1000), 20000)), step=500)
with c2:
    disc = st.slider("Discount rate % (your cost of money incl. inflation & bank rate)", 5, 45,
                     int(min(max((macro.get("interest") or 20), 5), 45)))
    fr = disc / 100
with c3:
    growth_pct = st.slider("Expected annual growth % of the project", -10, 60, 12)

years = 5
initial = float(capital)
monthly_flow = max(avg_profit * growth_pct / 100 * 0.5, avg_profit * 0.3)
base = max(monthly_flow, 10.0) * 12
cfs = [initial]
r_g = growth_pct / 100
for y in range(1, years + 1):
    cfs.append(base * (1 + r_g) ** (y - 1))
cfs = [-cfs[0]] + [max(0.0, v) for v in cfs[1:]]

r_disc = disc / 100
npv_val = npv(cfs, r_disc)
irr_val = irr(cfs)
mirr_val = mirr(cfs, finance_rate=max(fr, 0.05), reinvest_rate=max(fr, 0.1))
pb = payback(cfs)
pv_in = sum(pv(cf, r_disc, i) for i, cf in enumerate(cfs[1:], start=1))
pi = pv_in / (initial + 1e-9) if initial else 0

d1, d2, d3, d4 = st.columns(4)
d1.metric("Net Present Value (NPV)", nice(npv_val).replace("−", "-"),
          "Positive = project creates value over the bank")
d2.metric("IRR", f"{irr_val*100:.1f}%" if irr_val is not None else "n/a",
          f"Bank pays ~{disc}%")
d3.metric("Payback", f"{pb} years" if pb else "Not within 5y", f"Years to recover {nice(initial)}")
d4.metric("Profitability Index (PI)", f"{pi:.2f}", ">1 means it earns more than it costs")

st.markdown("---")
st.subheader("📈 Investment graphs")

rs = np.linspace(0.02, 0.9, 100)
npv_curve = [npv(cfs, r) for r in rs]
fig1 = go.Figure(go.Scatter(x=rs * 100, y=npv_curve, mode="lines",
                            line=dict(color="#C9A227", width=3)))
fig1.add_hline(y=0, line_dash="dot", line_color="#fff")
fig1.update_layout(title="NPV vs discount rate - where the line crosses zero the IRR sits",
                   xaxis_title="Discount rate %", yaxis_title="NPV (USD)")
st.plotly_chart(fig1, width="stretch", key="inv_npv")

labels = ["Now"] + [f"Y{i}" for i in range(1, years + 1)]
cum = []
run = 0.0
for cf in cfs:
    run += cf
    cum.append(run)
fig2 = go.Figure()
fig2.add_bar(x=labels, y=cfs, name="Cash flow", marker_color="#7BDCA6")
fig2.add_scatter(x=labels, y=cum, name="Cumulative (payback when it crosses 0)",
                 mode="lines+markers", line=dict(color="#C9A227", width=3))
fig2.add_hline(y=0, line_dash="dot", line_color="#fff")
fig2.update_layout(title="Project cash flows and cumulative recovery (DCF / Payback view)",
                   yaxis_title="USD")
st.plotly_chart(fig2, width="stretch", key="inv_payback")

dcf_in = pv_in
fig3 = go.Figure(go.Bar(x=["Present value of inflows", "Investment"],
                        y=[dcf_in, initial], marker_color=["#7BDCA6", "#B24C4C"]))
fig3.update_layout(title=f"Discounted inflows vs what you put in (PI = {pi:.2f})",
                   yaxis_title="USD")
st.plotly_chart(fig3, width="stretch", key="inv_dcf")

st.markdown("---")
st.markdown("### 🧠 What these numbers mean (plain professional English)")
st.markdown("""
- **NPV** - *If you invest now, will you get back more than you put in, after time and inflation are removed?* A positive NPV means yes. A negative NPV means the bank would beat the project.
- **IRR** - *How fast your money grows each year inside this project.* If the bank pays 10% and the project returns 25%, the project grows your money faster. The project is worth it while IRR is above your cost of money (here ~**{0}%**).
- **Payback** - *How many months/years it takes to recover your initial capital from profit.* Shorter payback = less time your money is at risk.
- **MIRR** - A more careful version of IRR that assumes your project's earnings are reinvested at a realistic rate. Good check against a too-optimistic IRR.
- **PI (Profitability Index)** - *Profit created per $1 invested.* Above 1.0 means value is being created. Compare projects on PI when choosing where to put money.
""".format(disc))

st.markdown("---")
st.subheader("🤖 Read the graph in plain English")
from explanation_engine import build, render
expl = build(bundle, "investment", macro)
render(st, lang, expl, "investment")

render_footer()