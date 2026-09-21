"""RFC SECURITIES - main entry point.

Turn Uncertainty Into Profitability.  Model. Predict. Optimize.

Login → robotic welcome → dashboard:
  - no data? cinematic 5-pillar carousel
  - data loaded? uploaded-product table view + metrics, then pages deep-dive
Always shows live FX ticker, footer, and the global sidebar.
"""
from __future__ import annotations

# --- path bootstrap: makes our modules importable (plain names) regardless of
# where the app is placed or run from (local, Streamlit Cloud, subfolder, ...).
# Both the app root and the `utils/` folder are put on sys.path, so the app
# works even if Python package resolution of `utils` is shadowed or the folder
# was extracted flat. ----------------------------------------------------------
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

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

import streamlit as st

st.set_page_config(page_title="RFC Securities", page_icon="📈",
                   layout="wide", initial_sidebar_state="expanded")

try:
    from translations import t
    from ui import (inject_css, page_guard, render_carousel, render_footer,
                    render_global_sidebar, render_login, render_report_view,
                    render_ticker, get_bundle, _load_macro, welcome_audio_html)
except ModuleNotFoundError as _e:
    st.error(
        "❌ Could not import the app's modules. The `utils/` folder (with files "
        f"like `ui.py`, `translations.py`) was not found next to app.py. Reason: {_e}")
    st.markdown(
        "**Fix on Streamlit Cloud / your deployment:** make sure the repository contains "
        "the three folders `pages/`, `utils/` and `.streamlit/` beside `app.py`, commit "
        "them (do **not** gitignore them), then redeploy. If you uploaded files one by one, "
        "upload the `utils/` folder contents as well.")
    st.stop()

inject_css()
lang = st.session_state.get("lang", "en")
if not st.session_state.get("authenticated"):
    render_login(lang)
    st.stop()
page_guard()

lang = st.session_state["lang"]
macro = _load_macro()

# ---------------- Robotic welcome (autoplay once right after login) ---------
WELCOME_TEXT = (
    "Welcome to RFC Securities. We turn business uncertainty into financial clarity. "
    "RFC Securities helps startups, SMEs and organisations understand profitability, cash flow, "
    "investment opportunities, risks and the best way to allocate their money. We analyse your "
    "business data together with current Zimbabwe market conditions, exchange rates, inflation, "
    "interest rates, government programmes, seasonal demand and market opportunities. We then "
    "explain the results in simple language, identify potential opportunities and risks, and "
    "provide practical financial insights to help you make informed business decisions. You can "
    "receive your complete report through WhatsApp or Gmail. Welcome to RFC Securities - Turn "
    "Uncertainty Into Profitability.")
if st.session_state.get("play_welcome"):
    html, _ = welcome_audio_html(lang)
    if html and not st.session_state.get("muted"):
        st.markdown(html, unsafe_allow_html=True)
    st.session_state["play_welcome"] = False

_wc, _ws = st.columns([6, 4])
with _ws:
    c1, c2, c3 = st.columns(3)
    if c1.button("🔊 Replay welcome", use_container_width=True, key="wa_replay"):
        html, _ = welcome_audio_html(lang)
        if html:
            st.markdown(html, unsafe_allow_html=True)
    if c2.button(t(lang, "btn_mute") if not st.session_state.get("muted")
                 else t(lang, "btn_unmute"), use_container_width=True, key="wa_mute"):
        st.session_state["muted"] = not st.session_state.get("muted")
        if not st.session_state["muted"]:
            html, _ = welcome_audio_html(lang)
            if html:
                st.markdown(html, unsafe_allow_html=True)
        st.rerun()
    sub_label = t(lang, "btn_subtitles") if not st.session_state.get("subtitles") \
        else t(lang, "btn_no_subtitles")
    if c3.button(sub_label, use_container_width=True, key="wa_sub"):
        st.session_state["subtitles"] = not st.session_state.get("subtitles")
        st.rerun()
    if st.session_state.get("subtitles"):
        st.caption("🔉 " + WELCOME_TEXT[:300] + "...")

# ---------------- Sidebar ----------------------------------------------------
render_global_sidebar()
render_ticker(macro)

lang = st.session_state["lang"]
bundle = get_bundle()

# ---------------- Main area ---------------------------------------------------
cols = st.columns([1, 4, 1])
with cols[1]:
    st.markdown(
        '<div class="brand" style="justify-content:center; margin:18px 0 4px 0;">'
        '<div class="logo-badge">RFC <span class="logo-arrow">▲</span></div>'
        '<span style="font-size:2rem; font-weight:900; letter-spacing:3px; color:var(--rfc-gold);">'
        'RFC&nbsp;SECURITIES</span></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center; color:var(--rfc-cream); font-weight:600;">'
        'Turn Uncertainty Into Profitability.</div>'
        '<div style="text-align:center; color:var(--rfc-gold); letter-spacing:5px; font-size:.85rem; '
        'margin-bottom:22px;">MODEL &nbsp;•&nbsp; PREDICT &nbsp;•&nbsp; OPTIMIZE</div>',
        unsafe_allow_html=True)

render_report_view()

if bundle is None:
    # ---------------- Clean empty state: cinematic carousel
    st.markdown(
        f'<div style="text-align:center; margin:6px 0 14px 0; color:var(--rfc-cream);">'
        f'<span style="background:#0E4A37; border:1px solid #C9A227; padding:6px 16px; border-radius:999px;">'
        f'📂 Upload your data on the left, or pick a demo business — then the 5 pillars unlock '
        f'in the pages menu.</span></div>', unsafe_allow_html=True)
    render_carousel()
else:
    # ---------------- Data loaded: product view + quick dashboard
    src = st.session_state.get("source")
    name = bundle["business"].name
    sector = bundle["business"].sector
    if src == "upload":
        label = t(lang, "data_status_real")
    else:
        label = t(lang, "data_status_demo")
    st.markdown(
        f'<div style="display:flex; gap:12px; align-items:center; flex-wrap:wrap; margin-bottom:8px;">'
        f'<span style="background:#0E4A37;border:1px solid #C9A227;padding:6px 14px;border-radius:999px;">'
        f'🏢 {name} &nbsp;|&nbsp; {sector}</span>'
        f'<span style="background:#0E4A37;border:1px solid #3f7a63;padding:6px 14px;border-radius:999px;">{label}</span>'
        f'</div>', unsafe_allow_html=True)

    m = bundle["monthly"]
    last, prev = m.iloc[-1], (m.iloc[-2] if len(m) > 1 else m.iloc[-1])
    from analysis import growth, nice

    d1, d2, d3 = st.columns(3)
    d1.metric(t(lang, "metric_revenue"), nice(last["revenue"]),
              f"{growth(m,'revenue',2):+.1f}% vs last month")
    d2.metric(t(lang, "metric_profit"), nice(last["profit"]),
              f"{growth(m,'profit',2):+.1f}% vs last month")
    d3.metric(t(lang, "metric_cash"), nice(last["cash_balance"]),
              f"{growth(m,'cash_balance',2):+.1f}% vs last month")
    d4, d5 = st.columns(2)
    d4.metric(t(lang, "metric_stock"), nice(last["inventory"]),
              f"{growth(m,'inventory',2):+.1f}% vs last month")
    d5.metric("Products", f"{len(bundle['products'])}",
              f"Sector: {sector}")

    st.markdown("---")
    st.subheader("🧾 Your data - products, prices, margins")
    if not bundle["products"].empty:
        st.dataframe(bundle["products"], width="stretch", hide_index=True)
    else:
        st.caption("No product-level file; monthly aggregates shown in pages.")
    if st.button(t(lang, "back_to_cinematic"), width="content"):
        st.session_state["cinematic"] = True
        st.rerun()
    if st.session_state.get("cinematic"):
        st.session_state["cinematic"] = False
        st.markdown("You can return to the 5-pillar view anytime from this button.")

    st.markdown("---")
    st.markdown(
        "**Next step:** open the pages in the left-hand menu — **📊 Profitability**, **💧 Cash Flow**, "
        "**🏗 Investment**, **⛈ Risk**, **⚙ Optimization** — every graph comes with a plain-English "
        "🤖 EXPLAIN THIS section that connects your numbers to the Zimbabwe economy.")

# ---------------- Live news section -----------------------------------------
st.markdown("---")
st.subheader("📰 LIVE ZIMBABWE BUSINESS & POLICY NEWS")
sector_filter = st.session_state.get("sector_filter", "All sectors")
from ui import _load_news
news = _load_news(sector_filter)
if news.get("live"):
    st.caption(f"LIVE • Last checked: {news['last_checked']} • Sources checked: "
               f"{news['sources_checked']} verified • Filter: {sector_filter}")
else:
    st.caption("DATA UNAVAILABLE/STALE - attempting reconnect next refresh (every 10 min).")
if news.get("items"):
    for it in news["items"][:10]:
        badge = {"High": "🔴 High", "Medium": "🟠 Medium", "Low": "🟢 Low"}.get(it.get("sector-score-tag") or
                 ("High" if it.get("score", 0) >= 2 else ("Medium" if it.get("score", 0) == 1 else "Low")), "🟢 Low")
        with st.expander(f"{it['headline']}", expanded=False):
            st.markdown(f"**{it.get('date') or '(date not listed)'}** • {it.get('author','')} • "
                        f"{badge} impact for SMEs")
            if it.get("summary"):
                st.markdown(it["summary"])
            if it.get("content"):
                st.markdown(f"> {it['content'][:600]}")
            st.markdown(f"[Open original article ↗]({it['link']})")
            st.markdown("**Business Impact Analysis:**")
            st.markdown(f"- **What happened?** {it['headline']}")
            st.markdown("- **Why it matters:** Your business operates adjacent to this news; it can move costs, demand or policy.")
            st.markdown("- **What you can consider:** Review prices, stock timing, and diversify sales channels this week.")
else:
    st.info("No feed items available right now (sources may be unreachable). Refreshing automatically every 10 minutes.")

# ---------------- Footer -------------------------------------------------------
render_footer()